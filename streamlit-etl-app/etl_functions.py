import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import re
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt_tab')
except:
    pass

from database_config import DB_CONFIG

def create_engine_connection():
    engine = create_engine(f"postgresql://postgres.cwbeoriyhbsamwvhkuna:dw_dashboard_bi@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres")
    return engine

def clear_all_tables(engine, retain_data=False):
    """
    Clear all tables in correct order to avoid foreign key constraint violations
    """
    if not retain_data:
        try:
            with engine.connect() as conn:
                print("🗑️ Clearing all tables in correct order...")
                # Delete in correct order: child tables first, then parent tables
                conn.execute(text("DELETE FROM fact_restaurant_reviews"))
                conn.execute(text("DELETE FROM bridge_sentiment_keywords"))
                conn.execute(text("DELETE FROM dim_sentiment"))
                conn.execute(text("DELETE FROM dim_keywords"))
                conn.execute(text("DELETE FROM dim_category"))
                conn.execute(text("DELETE FROM dim_restaurant"))
                conn.execute(text("DELETE FROM dim_location"))
                conn.execute(text("DELETE FROM dim_time"))
                conn.commit()
                print("✅ All tables cleared successfully")
        except Exception as e:
            print(f"⚠️ Warning during table clearing: {e}")

def etl_dim_time(df, engine, retain_data=False):
    print("Starting ETL for dim_time...")
    
    # Convert Time_GMT to datetime with error handling
    try:
        df['Time_GMT'] = pd.to_datetime(df['Time_GMT'], format='%m/%d/%Y %H:%M', errors='coerce')
        # Remove rows with invalid dates
        df = df.dropna(subset=['Time_GMT'])
    except Exception as e:
        print(f"Error parsing dates: {e}")
        return pd.DataFrame()
    
    unique_times = df['Time_GMT'].dropna().unique()
    
    time_data = []
    time_key = 1
    
    for timestamp in unique_times:
        dt = pd.to_datetime(timestamp)
        time_data.append({
            'time_key': time_key,
            'full_timestamp': dt,
            'date_actual': dt.date(),
            'year': dt.year,
            'month': dt.month,
            'week_of_year': dt.isocalendar()[1],
            'day_of_month': dt.day,
            'day_of_week': dt.weekday() + 1,
            'day_name': dt.strftime('%A')
        })
        time_key += 1
    
    dim_time_df = pd.DataFrame(time_data)
    
    # Insert data without clearing (clearing is done in clear_all_tables)
    if not dim_time_df.empty:
        dim_time_df.to_sql('dim_time', engine, if_exists='append', index=False)
        print(f"✓ Successfully loaded {len(dim_time_df)} time records to dim_time")
    
    return dim_time_df

def etl_dim_location(df, engine, retain_data=False):
    print("Starting ETL for dim_location...")
    location_cols = ['Country', 'CountryCode', 'State', 'City', 'Street', 'Building']
    
    # Check if all required columns exist
    missing_cols = [col for col in location_cols if col not in df.columns]
    if missing_cols:
        print(f"⚠️ Missing columns: {missing_cols}")
        return pd.DataFrame()
    
    # Make a copy and fill missing values with "-"
    df_copy = df.copy()
    
    # Fill missing/empty values with "-" for Street and Building
    df_copy['Street'] = df_copy['Street'].fillna('-').astype(str).replace('', '-')
    df_copy['Building'] = df_copy['Building'].fillna('-').astype(str).replace('', '-')
    
    # Also handle other location columns to ensure no empty values
    df_copy['Country'] = df_copy['Country'].fillna('-').astype(str).replace('', '-')
    df_copy['CountryCode'] = df_copy['CountryCode'].fillna('-').astype(str).replace('', '-')
    df_copy['State'] = df_copy['State'].fillna('-').astype(str).replace('', '-')
    df_copy['City'] = df_copy['City'].fillna('-').astype(str).replace('', '-')
    
    location_data = df_copy[location_cols].drop_duplicates().reset_index(drop=True)
    
    locations = []
    location_key = 1
    
    for _, row in location_data.iterrows():
        locations.append({
            'location_key': location_key,
            'country': str(row['Country']) if pd.notna(row['Country']) and str(row['Country']) != 'nan' else '-',
            'country_code': str(row['CountryCode']) if pd.notna(row['CountryCode']) and str(row['CountryCode']) != 'nan' else '-',
            'state': str(row['State']) if pd.notna(row['State']) and str(row['State']) != 'nan' else '-',
            'city': str(row['City']) if pd.notna(row['City']) and str(row['City']) != 'nan' else '-',
            'street': str(row['Street']) if pd.notna(row['Street']) and str(row['Street']) != 'nan' else '-',
            'building': str(row['Building']) if pd.notna(row['Building']) and str(row['Building']) != 'nan' else '-'
        })
        location_key += 1
    
    dim_location_df = pd.DataFrame(locations)
    
    if not dim_location_df.empty:
        dim_location_df.to_sql('dim_location', engine, if_exists='append', index=False)
        print(f"✓ Successfully loaded {len(dim_location_df)} location records to dim_location")
    
    return dim_location_df

def etl_dim_restaurant(df, engine, retain_data=False):
    print("Starting ETL for dim_restaurant...")
    restaurant_cols = ['Organization', 'Phone', 'OLF']
    
    # Check if all required columns exist
    missing_cols = [col for col in restaurant_cols if col not in df.columns]
    if missing_cols:
        print(f"⚠️ Missing columns: {missing_cols}")
        return pd.DataFrame()
    
    # Make a copy and handle missing values
    df_copy = df.copy()
    df_copy['Organization'] = df_copy['Organization'].fillna('Unknown').astype(str)
    df_copy['Phone'] = df_copy['Phone'].fillna('-').astype(str)
    df_copy['OLF'] = df_copy['OLF'].fillna('-').astype(str)
    
    restaurant_data = df_copy[restaurant_cols].drop_duplicates().reset_index(drop=True)
    
    restaurants = []
    restaurant_key = 1
    
    for _, row in restaurant_data.iterrows():
        restaurants.append({
            'restaurant_key': restaurant_key,
            'organization_name': str(row['Organization']) if pd.notna(row['Organization']) and str(row['Organization']) != 'nan' else 'Unknown',
            'phone_number': str(row['Phone']) if pd.notna(row['Phone']) and str(row['Phone']) != 'nan' else '-',
            'oil_info': str(row['OLF']) if pd.notna(row['OLF']) and str(row['OLF']) != 'nan' else '-'
        })
        restaurant_key += 1
    
    dim_restaurant_df = pd.DataFrame(restaurants)
    
    if not dim_restaurant_df.empty:
        dim_restaurant_df.to_sql('dim_restaurant', engine, if_exists='append', index=False)
        print(f"✓ Successfully loaded {len(dim_restaurant_df)} restaurant records to dim_restaurant")
    
    return dim_restaurant_df

def etl_dim_category(df, engine, retain_data=False):
    print("Starting ETL for dim_category...")
    
    if 'Category' not in df.columns:
        print("⚠️ Category column not found")
        return pd.DataFrame()
    
    # Handle missing categories
    df_copy = df.copy()
    df_copy['Category'] = df_copy['Category'].fillna('Unknown').astype(str)
    
    unique_categories = df_copy['Category'].dropna().unique()
    
    categories = []
    category_key = 1
    
    for category in unique_categories:
        categories.append({
            'category_key': category_key,
            'category_name': str(category) if str(category) != 'nan' else 'Unknown'
        })
        category_key += 1
    
    dim_category_df = pd.DataFrame(categories)
    
    if not dim_category_df.empty:
        dim_category_df.to_sql('dim_category', engine, if_exists='append', index=False)
        print(f"✓ Successfully loaded {len(dim_category_df)} category records to dim_category")
    
    return dim_category_df

def etl_dim_keywords(df, engine, retain_data=False):
    print("Starting ETL for dim_keywords...")
    
    if 'ReviewText' not in df.columns:
        print("⚠️ ReviewText column not found")
        return pd.DataFrame()
    
    review_texts = df['ReviewText'].dropna().tolist()
    all_keywords = []
    
    try:
        stop_words = set(stopwords.words('english'))
    except:
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    
    stop_words.update(['restaurant', 'place', 'food', 'service', 'experience', 'was', 'were', 'is', 'are'])
    
    food_keywords = {
        'delicious', 'tasty', 'fresh', 'hot', 'cold', 'spicy', 'sweet', 'sour', 'salty', 'bitter',
        'juicy', 'crispy', 'tender', 'overcooked', 'undercooked', 'bland', 'flavorful', 'seasoned',
        'burnt', 'raw', 'frozen', 'stale', 'greasy', 'dry', 'moist', 'creamy'
    }
    
    service_keywords = {
        'friendly', 'rude', 'slow', 'fast', 'quick', 'attentive', 'helpful', 'polite', 'professional',
        'unprofessional', 'courteous', 'patient', 'impatient', 'efficient', 'inefficient', 'responsive',
        'unresponsive', 'knowledgeable', 'clueless', 'accommodating'
    }
    
    location_keywords = {
        'clean', 'dirty', 'comfortable', 'uncomfortable', 'spacious', 'cramped', 'noisy', 'quiet',
        'bright', 'dark', 'cozy', 'cold', 'warm', 'modern', 'outdated', 'beautiful', 'ugly',
        'convenient', 'inconvenient', 'accessible', 'parking'
    }
    
    for review in review_texts:
        if isinstance(review, str) and len(review.strip()) > 0:
            try:
                review_clean = re.sub(r'[^\w\s]', '', review.lower())
                words = word_tokenize(review_clean)
                keywords = [word for word in words 
                           if len(word) > 2 and word not in stop_words and word.isalpha()]
                all_keywords.extend(keywords)
            except:
                continue
    
    if not all_keywords:
        print("⚠️ No keywords found")
        return pd.DataFrame()
    
    keyword_counts = Counter(all_keywords)
    top_keywords = keyword_counts.most_common(200)
    
    keywords_data = []
    keyword_key = 1
    
    for keyword, frequency in top_keywords:
        if keyword in food_keywords:
            category = 'food'
        elif keyword in service_keywords:
            category = 'service'
        elif keyword in location_keywords:
            category = 'location'
        else:
            category = 'general'
        
        keywords_data.append({
            'keyword_key': keyword_key,
            'keyword': keyword,
            'keyword_category': category
        })
        keyword_key += 1
    
    dim_keywords_df = pd.DataFrame(keywords_data)
    
    if not dim_keywords_df.empty:
        dim_keywords_df.to_sql('dim_keywords', engine, if_exists='append', index=False)
        print(f"✓ Successfully loaded {len(dim_keywords_df)} keywords to dim_keywords")
    
    return dim_keywords_df

def etl_dim_sentiment(df, engine, retain_data=False):
    print("Starting ETL for dim_sentiment...")
    
    if 'ReviewText' not in df.columns:
        print("⚠️ ReviewText column not found")
        return pd.DataFrame()
    
    sia = SentimentIntensityAnalyzer()
    review_data = df[['ReviewText', 'Rating']].dropna().copy()
    
    sentiment_data = []
    sentiment_key = 1
    
    for idx, row in review_data.iterrows():
        review_text = row['ReviewText']
        rating = row['Rating']
        
        if isinstance(review_text, str) and len(review_text.strip()) > 0:
            try:
                sentiment_scores = sia.polarity_scores(review_text)
                compound_score = sentiment_scores['compound']
                
                if compound_score >= 0.05:
                    sentiment_label = 'positive'
                elif compound_score <= -0.05:
                    sentiment_label = 'negative'
                else:
                    sentiment_label = 'neutral'
                
                review_clean = re.sub(r'[^\w\s]', '', review_text.lower())
                words = word_tokenize(review_clean)
                
                try:
                    stop_words = set(stopwords.words('english'))
                except:
                    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
                
                keywords = [word for word in words 
                           if len(word) > 2 and word not in stop_words and word.isalpha()]
                
                keyword_counts = Counter(keywords)
                top_keywords = [kw[0] for kw in keyword_counts.most_common(5)]
                
                word_count = len(review_text.split())
                character_count = len(review_text)
                
                sentiment_data.append({
                    'sentiment_key': sentiment_key,
                    'review_text': review_text[:1000],  # Limit text length
                    'sentiment_label': sentiment_label,
                    'sentiment_score': round(compound_score, 4),
                    'top_keywords': top_keywords,
                    'word_count': word_count,
                    'character_count': character_count
                })
                
                sentiment_key += 1
            except Exception as e:
                print(f"Error processing sentiment for row {idx}: {e}")
                continue
    
    dim_sentiment_df = pd.DataFrame(sentiment_data)
    
    if not dim_sentiment_df.empty:
        dim_sentiment_df.to_sql('dim_sentiment', engine, if_exists='append', index=False)
        print(f"✓ Successfully loaded {len(dim_sentiment_df)} sentiment records to dim_sentiment")
    
    return dim_sentiment_df

def etl_bridge_sentiment_keywords(dim_sentiment_df, dim_keywords_df, engine, retain_data=False):
    print("Starting ETL for bridge_sentiment_keywords...")
    
    if dim_sentiment_df.empty or dim_keywords_df.empty:
        print("⚠️ No sentiment or keywords data to process")
        return pd.DataFrame()
    
    bridge_data = []
    keyword_lookup = {row['keyword']: row['keyword_key'] 
                     for _, row in dim_keywords_df.iterrows()}
    
    for _, sentiment_row in dim_sentiment_df.iterrows():
        sentiment_key = sentiment_row['sentiment_key']
        top_keywords = sentiment_row['top_keywords']
        
        if isinstance(top_keywords, list):
            for keyword in top_keywords:
                if keyword in keyword_lookup:
                    keyword_key = keyword_lookup[keyword]
                    review_text = sentiment_row['review_text'].lower()
                    keyword_frequency = review_text.count(keyword)
                    
                    if keyword_frequency > 0:
                        bridge_data.append({
                            'sentiment_key': sentiment_key,
                            'keyword_key': keyword_key,
                            'keyword_frequency': keyword_frequency
                        })
    
    bridge_df = pd.DataFrame(bridge_data)
    if not bridge_df.empty:
        bridge_df = bridge_df.groupby(['sentiment_key', 'keyword_key'])['keyword_frequency'].sum().reset_index()
        bridge_df.to_sql('bridge_sentiment_keywords', engine, if_exists='append', index=False)
        print(f"✓ Successfully loaded {len(bridge_df)} bridge records to bridge_sentiment_keywords")
    else:
        print("⚠️ No bridge data to load")
    
    return bridge_df

def etl_fact_restaurant_reviews(df, engine, dim_time_df, dim_location_df, dim_restaurant_df, dim_category_df, dim_sentiment_df, retain_data=False):
    print("Starting ETL for fact_restaurant_reviews...")
    
    # Check if dimension dataframes are not empty
    if any(df_dim.empty for df_dim in [dim_time_df, dim_location_df, dim_restaurant_df, dim_category_df]):
        print("⚠️ One or more dimension tables are empty")
        return pd.DataFrame()
    
    # Make a copy of the original dataframe and handle missing values
    df_fact = df.copy()
    
    # Fill missing values with default values
    df_fact['Street'] = df_fact['Street'].fillna('-').astype(str).replace('', '-')
    df_fact['Building'] = df_fact['Building'].fillna('-').astype(str).replace('', '-')
    df_fact['Country'] = df_fact['Country'].fillna('-').astype(str).replace('', '-')
    df_fact['State'] = df_fact['State'].fillna('-').astype(str).replace('', '-')
    df_fact['City'] = df_fact['City'].fillna('-').astype(str).replace('', '-')
    df_fact['Organization'] = df_fact['Organization'].fillna('Unknown').astype(str)
    df_fact['Category'] = df_fact['Category'].fillna('Unknown').astype(str)
    
    time_lookup = {}
    for _, row in dim_time_df.iterrows():
        try:
            timestamp_str = row['full_timestamp'].strftime('%m/%d/%Y %H:%M')
            time_lookup[timestamp_str] = row['time_key']
        except:
            continue
    
    location_lookup = {}
    for _, row in dim_location_df.iterrows():
        # Handle the case where values might be '-'
        country = str(row['country']) if row['country'] not in [None, 'None', 'nan'] else '-'
        state = str(row['state']) if row['state'] not in [None, 'None', 'nan'] else '-'
        city = str(row['city']) if row['city'] not in [None, 'None', 'nan'] else '-'
        street = str(row['street']) if row['street'] not in [None, 'None', 'nan'] else '-'
        building = str(row['building']) if row['building'] not in [None, 'None', 'nan'] else '-'
        
        key = f"{country}_{state}_{city}_{street}_{building}"
        location_lookup[key] = row['location_key']
    
    restaurant_lookup = {str(row['organization_name']): row['restaurant_key'] 
                        for _, row in dim_restaurant_df.iterrows()}
    
    category_lookup = {str(row['category_name']): row['category_key'] 
                      for _, row in dim_category_df.iterrows()}
    
    fact_data = []
    review_id = 1
    
    # Debug: Print some lookup info
    print(f"Created {len(time_lookup)} time lookups")
    print(f"Created {len(location_lookup)} location lookups")
    print(f"Created {len(restaurant_lookup)} restaurant lookups")
    print(f"Created {len(category_lookup)} category lookups")
    
    for idx, row in df_fact.iterrows():
        try:
            # Parse time
            time_str = pd.to_datetime(row['Time_GMT'], format='%m/%d/%Y %H:%M', errors='coerce')
            if pd.isna(time_str):
                print(f"⚠️ Invalid time for row {idx}: {row['Time_GMT']}")
                continue
                
            time_str = time_str.strftime('%m/%d/%Y %H:%M')
            time_key = time_lookup.get(time_str)
            
            # Get location key - ensure all values are strings and handle empty values
            country = str(row.get('Country', '-')) if pd.notna(row.get('Country')) and str(row.get('Country')) != 'nan' else '-'
            state = str(row.get('State', '-')) if pd.notna(row.get('State')) and str(row.get('State')) != 'nan' else '-'
            city = str(row.get('City', '-')) if pd.notna(row.get('City')) and str(row.get('City')) != 'nan' else '-'
            street = str(row.get('Street', '-')) if pd.notna(row.get('Street')) and str(row.get('Street')) != 'nan' else '-'
            building = str(row.get('Building', '-')) if pd.notna(row.get('Building')) and str(row.get('Building')) != 'nan' else '-'
            
            location_key_str = f"{country}_{state}_{city}_{street}_{building}"
            location_key = location_lookup.get(location_key_str)
            
            # Get restaurant and category keys
            organization = str(row.get('Organization', 'Unknown')) if pd.notna(row.get('Organization')) else 'Unknown'
            category = str(row.get('Category', 'Unknown')) if pd.notna(row.get('Category')) else 'Unknown'
            
            restaurant_key = restaurant_lookup.get(organization)
            category_key = category_lookup.get(category)
            
            # Get sentiment key (use index as fallback)
            sentiment_key = min(idx + 1, len(dim_sentiment_df)) if not dim_sentiment_df.empty else 1
            
            review_length = len(str(row.get('ReviewText', ''))) if pd.notna(row.get('ReviewText')) else 0
            
            # Debug missing keys
            if not time_key:
                print(f"⚠️ Missing time_key for row {idx}: {time_str}")
            if not location_key:
                print(f"⚠️ Missing location_key for row {idx}: {location_key_str}")
            if not restaurant_key:
                print(f"⚠️ Missing restaurant_key for row {idx}: {organization}")
            if not category_key:
                print(f"⚠️ Missing category_key for row {idx}: {category}")
            
            # Only require time_key and location_key to be valid
            if time_key and location_key:
                # Use default keys if restaurant or category keys are missing
                if not restaurant_key:
                    restaurant_key = 1  # Use first restaurant as default
                if not category_key:
                    category_key = 1  # Use first category as default
                
                fact_data.append({
                    'review_id': review_id,
                    'restaurant_key': restaurant_key,
                    'location_key': location_key,
                    'time_key': time_key,
                    'category_key': category_key,
                    'sentiment_key': sentiment_key,
                    'rating': float(row.get('Rating', 0)) if pd.notna(row.get('Rating')) else 0.0,
                    'number_of_reviews': int(row.get('NumberReview', 1)) if pd.notna(row.get('NumberReview')) else 1,
                    'review_length': review_length
                })
                review_id += 1
            else:
                print(f"⚠️ Skipping row {idx} due to missing required keys")
                
        except Exception as e:
            print(f"Error processing fact row {idx}: {e}")
            continue
    
    fact_reviews_df = pd.DataFrame(fact_data)
    
    if not fact_reviews_df.empty:
        fact_reviews_df.to_sql('fact_restaurant_reviews', engine, if_exists='append', index=False)
        print(f"✓ Successfully loaded {len(fact_reviews_df)} fact records to fact_restaurant_reviews")
    else:
        print("⚠️ No fact data to load")
    
    return fact_reviews_df

def run_complete_etl(df, engine, retain_data=False):
    """
    Main function untuk menjalankan seluruh ETL process untuk semua tabel
    """
    try:
        print(f"Loaded {len(df)} records from dataset")
        
        print("\n" + "="*60)
        print("STARTING COMPLETE ETL PROCESS")
        print("="*60)
        
        # Clear all tables first if not retaining data
        clear_all_tables(engine, retain_data)
        
        # 1. ETL Dimension Tables
        print("\n--- ETL DIMENSION TABLES ---")
        dim_time_df = etl_dim_time(df, engine, retain_data)
        dim_location_df = etl_dim_location(df, engine, retain_data)
        dim_restaurant_df = etl_dim_restaurant(df, engine, retain_data)
        dim_category_df = etl_dim_category(df, engine, retain_data)
        
        # 2. ETL Sentiment-related tables
        print("\n--- ETL SENTIMENT TABLES ---")
        dim_keywords_df = etl_dim_keywords(df, engine, retain_data)
        dim_sentiment_df = etl_dim_sentiment(df, engine, retain_data)
        bridge_df = etl_bridge_sentiment_keywords(dim_sentiment_df, dim_keywords_df, engine, retain_data)
        
        # 3. ETL Fact Table
        print("\n--- ETL FACT TABLE ---")
        fact_df = etl_fact_restaurant_reviews(df, engine, dim_time_df, dim_location_df, 
                                            dim_restaurant_df, dim_category_df, dim_sentiment_df, retain_data)
        
        print("\n" + "="*60)
        print("COMPLETE ETL PROCESS FINISHED SUCCESSFULLY!")
        print("="*60)
        
        return {
            'dim_time': len(dim_time_df),
            'dim_location': len(dim_location_df),
            'dim_restaurant': len(dim_restaurant_df),
            'dim_category': len(dim_category_df),
            'dim_keywords': len(dim_keywords_df),
            'dim_sentiment': len(dim_sentiment_df),
            'bridge_sentiment_keywords': len(bridge_df),
            'fact_restaurant_reviews': len(fact_df)
        }
        
    except Exception as e:
        print(f"Error in complete ETL process: {e}")
        return None