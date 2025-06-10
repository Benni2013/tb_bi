import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from shared_utils import load_data, load_css, check_table_exists, create_safe_wordcloud, WORDCLOUD_AVAILABLE

def render_sentiment_dashboard():
    load_css()
    st.markdown('<h1 class="main-header">💬 Sentimen & Suara Pelanggan</h1>', unsafe_allow_html=True)
    
    # Check if sentiment tables exist first
    sentiment_table_exists = check_table_exists('dim_sentiment')
    keywords_table_exists = check_table_exists('dim_keywords')
    
    if not sentiment_table_exists:
        st.warning("⚠️ Tabel dim_sentiment tidak ditemukan di database.")
        st.info("💡 Pastikan proses ETL telah dijalankan untuk membuat tabel sentiment.")
        
        # Create mock data for demonstration
        st.subheader("📊 Demo Sentiment Analysis")
        
        # Mock sentiment data
        mock_sentiment_data = pd.DataFrame({
            'sentiment_label': ['positive', 'negative', 'neutral', 'positive', 'negative', 'positive', 'neutral'] * 10,
            'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio'] * 10,
            'organization_name': ['Restaurant A', 'Restaurant B', 'Restaurant C', 'Restaurant D', 'Restaurant E'] * 14,
            'rating': [4.5, 2.1, 3.2, 4.8, 1.9, 4.2, 3.5] * 10
        })
        
        # Sidebar Filters for mock data
        st.sidebar.subheader("🔍 Filter Data (Demo)")
        
        selected_location = st.sidebar.selectbox(
            "Pilih Lokasi",
            ["Semua"] + list(mock_sentiment_data['city'].unique()),
            key="demo_sent_location"
        )
        
        selected_org = st.sidebar.selectbox(
            "Pilih Organisasi", 
            ["Semua"] + list(mock_sentiment_data['organization_name'].unique()),
            key="demo_sent_org"
        )
        
        # Filter mock data
        filtered_mock_data = mock_sentiment_data.copy()
        if selected_location != "Semua":
            filtered_mock_data = filtered_mock_data[filtered_mock_data['city'] == selected_location]
        if selected_org != "Semua":
            filtered_mock_data = filtered_mock_data[filtered_mock_data['organization_name'] == selected_org]
        
        # Mock sentiment metrics
        sentiment_counts = filtered_mock_data['sentiment_label'].value_counts()
        total_reviews = len(filtered_mock_data)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            positive_count = sentiment_counts.get('positive', 0)
            positive_pct = (positive_count / total_reviews * 100) if total_reviews > 0 else 0
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>😊 Positive</h4>
                    <h2>{positive_count}</h2>
                    <p>{positive_pct:.1f}%</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            negative_count = sentiment_counts.get('negative', 0)
            negative_pct = (negative_count / total_reviews * 100) if total_reviews > 0 else 0
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>😞 Negative</h4>
                    <h2>{negative_count}</h2>
                    <p>{negative_pct:.1f}%</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col3:
            neutral_count = sentiment_counts.get('neutral', 0)
            neutral_pct = (neutral_count / total_reviews * 100) if total_reviews > 0 else 0
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>😐 Neutral</h4>
                    <h2>{neutral_count}</h2>
                    <p>{neutral_pct:.1f}%</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>📝 Total Reviews</h4>
                    <h2>{total_reviews:,}</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # Mock Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
            st.subheader("📊 Distribusi Sentimen (Demo)")
            
            if len(sentiment_counts) > 0:
                fig = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    title="Sentiment Distribution",
                    color_discrete_map={
                        'positive': '#2E8B57',
                        'negative': "#200B0F",
                        'neutral': '#4682B4'
                    }
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
            st.subheader("📈 Sentimen per Lokasi (Demo)")
            
            location_sentiment = filtered_mock_data.groupby(['city', 'sentiment_label']).size().reset_index(name='count')
            
            if not location_sentiment.empty:
                fig = px.bar(
                    location_sentiment,
                    x='city',
                    y='count',
                    color='sentiment_label',
                    title="Sentiment by Location",
                    color_discrete_map={
                        'positive': '#2E8B57',
                        'negative': '#DC143C',
                        'neutral': '#4682B4'
                    }
                )
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Mock keywords
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🔤 Top Keywords (Demo)")
        
        mock_keywords = [
            "delicious", "great", "excellent", "amazing", "wonderful", "fantastic", "perfect", "love",
            "terrible", "awful", "bad", "horrible", "disgusting", "worst", "hate", "poor",
            "good", "nice", "okay", "decent", "average", "fine", "normal", "standard"
        ]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Positive Keywords:**")
            for i, keyword in enumerate(mock_keywords[:8], 1):
                st.markdown(f"{i}. **{keyword}** - {np.random.randint(10, 50)} mentions")
        
        with col2:
            st.markdown("**Negative Keywords:**")
            for i, keyword in enumerate(mock_keywords[8:16], 1):
                st.markdown(f"{i}. **{keyword}** - {np.random.randint(5, 30)} mentions")
        
        with col3:
            st.markdown("**Neutral Keywords:**")
            for i, keyword in enumerate(mock_keywords[16:24], 1):
                st.markdown(f"{i}. **{keyword}** - {np.random.randint(15, 40)} mentions")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mock reviews
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📝 Sample Reviews (Demo)")
        
        mock_reviews = {
            'positive': [
                "The food was absolutely delicious! Great service and amazing atmosphere.",
                "Best restaurant in town! Highly recommend the pasta dishes.",
                "Wonderful experience, will definitely come back again."
            ],
            'negative': [
                "Terrible service, food was cold and tasteless.",
                "Worst dining experience ever. Would not recommend to anyone.",
                "Poor quality food and very expensive for what you get."
            ],
            'neutral': [
                "Food was okay, nothing special but decent enough.",
                "Average restaurant, service was fine but not outstanding.",
                "Standard quality, met expectations but didn't exceed them."
            ]
        }
        
        col1, col2, col3 = st.columns(3)
        
        sentiments = ['positive', 'negative', 'neutral']
        columns = [col1, col2, col3]
        
        for sentiment, col in zip(sentiments, columns):
            with col:
                st.markdown(f"**{sentiment.title()} Reviews:**")
                review = np.random.choice(mock_reviews[sentiment])
                st.markdown(f"*{review}*")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Real sentiment data loading
        @st.cache_data(ttl=300)
        def load_sentiment_data_safe():
            try:
                # Simple query to test first
                query = """
                SELECT COUNT(*) as total_count FROM dim_sentiment
                """
                test_result = load_data(query)
                
                if test_result.empty or test_result['total_count'].iloc[0] == 0:
                    st.warning("⚠️ Tabel dim_sentiment kosong.")
                    return pd.DataFrame()
                
                # Load actual data with LIMIT to prevent crashes
                query = """
                SELECT 
                    ds.sentiment_label,
                    ds.sentiment_score,
                    SUBSTRING(ds.review_text, 1, 200) as review_text,
                    dr.organization_name,
                    dl.city,
                    dl.state,
                    frr.rating,
                    dt.year,
                    dt.month
                FROM dim_sentiment ds
                JOIN fact_restaurant_reviews frr ON ds.sentiment_key = frr.sentiment_key
                JOIN dim_restaurant dr ON frr.restaurant_key = dr.restaurant_key
                JOIN dim_location dl ON frr.location_key = dl.location_key
                JOIN dim_time dt ON frr.time_key = dt.time_key
                WHERE ds.sentiment_label IS NOT NULL
                LIMIT 500
                """
                return load_data(query)
            except Exception as e:
                st.error(f"Error loading sentiment data: {e}")
                return pd.DataFrame()
        
        @st.cache_data(ttl=300)
        def load_keywords_data_safe():
            if not keywords_table_exists:
                return pd.DataFrame()
            
            try:
                # Test if keywords table has data
                query = """
                SELECT COUNT(*) as total_count FROM dim_keywords
                """
                test_result = load_data(query)
                
                if test_result.empty or test_result['total_count'].iloc[0] == 0:
                    return pd.DataFrame()
                
                # Load keywords data with joins to enable filtering
                query = """
                SELECT 
                    dk.keyword,
                    dk.keyword_category,
                    dl.city,
                    dr.organization_name,
                    ds.sentiment_label,
                    COALESCE(COUNT(bsk.sentiment_key), 1) as frequency
                FROM dim_keywords dk
                LEFT JOIN bridge_sentiment_keywords bsk ON dk.keyword_key = bsk.keyword_key
                LEFT JOIN dim_sentiment ds ON bsk.sentiment_key = ds.sentiment_key
                LEFT JOIN fact_restaurant_reviews frr ON ds.sentiment_key = frr.sentiment_key
                LEFT JOIN dim_restaurant dr ON frr.restaurant_key = dr.restaurant_key
                LEFT JOIN dim_location dl ON frr.location_key = dl.location_key
                WHERE dk.keyword IS NOT NULL AND dk.keyword != ''
                GROUP BY dk.keyword, dk.keyword_category, dl.city, dr.organization_name, ds.sentiment_label
                ORDER BY frequency DESC
                LIMIT 1000
                """
                return load_data(query)
            except Exception as e:
                st.error(f"Error loading keywords data: {e}")
                return pd.DataFrame()
        
        # Load data safely
        with st.spinner("📊 Loading sentiment data..."):
            sentiment_data = load_sentiment_data_safe()
            keywords_data = load_keywords_data_safe()
        
        if not sentiment_data.empty:
            # Sidebar Filters
            st.sidebar.subheader("🔍 Filter Data")
            
            selected_location = st.sidebar.selectbox(
                "Pilih Lokasi",
                ["Semua"] + sorted(list(sentiment_data['city'].unique())),
                key="real_sent_location"
            )
            
            selected_org = st.sidebar.selectbox(
                "Pilih Organisasi",
                ["Semua"] + sorted(list(sentiment_data['organization_name'].unique())),
                key="real_sent_org"
            )
            
            # Filter data
            filtered_data = sentiment_data.copy()
            if selected_location != "Semua":
                filtered_data = filtered_data[filtered_data['city'] == selected_location]
            if selected_org != "Semua":
                filtered_data = filtered_data[filtered_data['organization_name'] == selected_org]
            
            # Filter keywords data based on selected filters
            filtered_keywords_data = keywords_data.copy()
            if not keywords_data.empty:
                if selected_location != "Semua":
                    filtered_keywords_data = filtered_keywords_data[
                        (filtered_keywords_data['city'] == selected_location) | 
                        (filtered_keywords_data['city'].isna())
                    ]
                if selected_org != "Semua":
                    filtered_keywords_data = filtered_keywords_data[
                        (filtered_keywords_data['organization_name'] == selected_org) | 
                        (filtered_keywords_data['organization_name'].isna())
                    ]
                
                # Re-aggregate keywords after filtering
                filtered_keywords_data = filtered_keywords_data.groupby(['keyword', 'keyword_category']).agg({
                    'frequency': 'sum'
                }).reset_index().sort_values('frequency', ascending=False)

            # Sentiment metrics
            sentiment_counts = filtered_data['sentiment_label'].value_counts()
            total_reviews = len(filtered_data)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                positive_count = sentiment_counts.get('positive', 0)
                positive_pct = (positive_count / total_reviews * 100) if total_reviews > 0 else 0
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h4>😊 Positive</h4>
                        <h2>{positive_count}</h2>
                        <p>{positive_pct:.1f}%</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            with col2:
                negative_count = sentiment_counts.get('negative', 0)
                negative_pct = (negative_count / total_reviews * 100) if total_reviews > 0 else 0
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h4>😞 Negative</h4>
                        <h2>{negative_count}</h2>
                        <p>{negative_pct:.1f}%</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            with col3:
                neutral_count = sentiment_counts.get('neutral', 0)
                neutral_pct = (neutral_count / total_reviews * 100) if total_reviews > 0 else 0
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h4>😐 Neutral</h4>
                        <h2>{neutral_count}</h2>
                        <p>{neutral_pct:.1f}%</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            with col4:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h4>📝 Total Reviews</h4>
                        <h2>{total_reviews:,}</h2>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.subheader("📊 Distribusi Sentimen")
                
                if len(sentiment_counts) > 0:
                    fig = px.pie(
                        values=sentiment_counts.values,
                        names=sentiment_counts.index,
                        title="Sentiment Distribution",
                        color_discrete_map={
                            'positive': '#2E8B57',
                            'negative': '#DC143C',
                            'neutral': '#4682B4'
                        }
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No sentiment data available")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.subheader("📈 Sentimen per Lokasi")
                
                location_sentiment = filtered_data.groupby(['city', 'sentiment_label']).size().reset_index(name='count')
                location_sentiment = location_sentiment.sort_values(by='count', ascending=False).head(30)
                
                if not location_sentiment.empty:
                    fig = px.bar(
                        location_sentiment,
                        x='city',
                        y='count',
                        color='sentiment_label',
                        title="Sentiment by Location (Top Locations)",
                        color_discrete_map={
                            'positive': '#2E8B57',
                            'negative': '#DC143C',
                            'neutral': '#4682B4'
                        }
                    )
                    fig.update_layout(height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No location sentiment data available")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Keywords analysis
            st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
            st.subheader("☁️ Keyword Analysis from Review Text")
            
            # Extract keywords directly from review text
            def extract_keywords_from_reviews(reviews_data, sentiment_filter="Semua"):
                """Extract keywords directly from review text"""
                import re
                from collections import Counter
                
                # Filter by sentiment if specified
                if sentiment_filter != "Semua":
                    reviews_data = reviews_data[reviews_data['sentiment_label'] == sentiment_filter]
                
                # Combine all review texts
                all_text = ' '.join(reviews_data['review_text'].fillna('').astype(str))
                
                # Clean and tokenize text
                # Remove special characters and convert to lowercase
                cleaned_text = re.sub(r'[^a-zA-Z\s]', '', all_text.lower())
                
                # Split into words
                words = cleaned_text.split()
                
                # Common stopwords to filter out
                stopwords = {
                    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that',
                    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                    'would', 'could', 'should', 'can', 'may', 'might', 'must', 'shall', 'i', 'you', 'he', 'she', 'it',
                    'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
                    'am', 'very', 'so', 'just', 'all', 'any', 'some', 'no', 'not', 'only', 'own', 'same', 'such',
                    'than', 'too', 'now', 'here', 'there', 'when', 'where', 'why', 'how', 'what', 'which', 'who',
                    'restaurant', 'food', 'place', 'time', 'get', 'got', 'go', 'went', 'come', 'came', 'one', 'two',
                    'also', 'back', 'really', 'much', 'well', 'good', 'great', 'nice', 'like', 'love', 'dont', 'didnt',
                    'wouldnt', 'couldnt', 'shouldnt', 'wasnt', 'werent', 'havent', 'hasnt', 'hadnt', 'wont', 'cant'
                }
                
                # Filter words (remove stopwords, short words, and empty strings)
                filtered_words = [
                    word for word in words 
                    if len(word) > 2 and word not in stopwords and word.isalpha()
                ]
                
                # Count word frequency
                word_counts = Counter(filtered_words)
                
                return word_counts.most_common(100)  # Return top 100 words
            
            # Extract keywords from filtered review data
            if not filtered_data.empty and 'review_text' in filtered_data.columns:
                col_filter, col_info = st.columns([1, 1])
                
                with col_filter:
                    sentiment_filter = st.selectbox(
                        "Filter Keywords by Sentiment",
                        ["Semua", "positive", "negative", "neutral"],
                        key="review_keyword_sentiment_filter"
                    )
                
                try:
                    # Extract keywords from reviews
                    review_keywords = extract_keywords_from_reviews(filtered_data, sentiment_filter)
                    
                    if review_keywords:
                        with col_info:
                            st.metric("Keywords Found", len(review_keywords))
                            total_word_count = sum([count for _, count in review_keywords])
                            st.metric("Total Word Mentions", total_word_count)
                        
                        # Display top keywords in columns
                        st.subheader("🔤 Top Keywords from Reviews")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        # Split keywords into three columns
                        keywords_per_col = len(review_keywords) // 3
                        
                        with col1:
                            st.markdown("**Most Frequent (1-15):**")
                            for i, (word, count) in enumerate(review_keywords[:15], 1):
                                st.markdown(f"{i}. **{word}** - {count} mentions")
                        
                        with col2:
                            st.markdown("**Frequent (16-30):**")
                            for i, (word, count) in enumerate(review_keywords[15:30], 16):
                                st.markdown(f"{i}. **{word}** - {count} mentions")
                        
                        with col3:
                            st.markdown("**Common (31-45):**")
                            for i, (word, count) in enumerate(review_keywords[30:45], 31):
                                st.markdown(f"{i}. **{word}** - {count} mentions")
                        
                        # Create word cloud from review keywords
                        if WORDCLOUD_AVAILABLE and len(review_keywords) > 0:
                            try:
                                # Create weighted text for word cloud
                                wordcloud_text = ' '.join([
                                    f"{word} " * min(count, 20)  # Limit repetition to prevent one word dominating
                                    for word, count in review_keywords[:50]  # Top 50 words
                                ])
                                
                                if wordcloud_text.strip():
                                    st.subheader("☁️ Word Cloud from Reviews")
                                    st.info(f"📝 Showing top keywords from {len(filtered_data)} reviews")
                                    create_safe_wordcloud(wordcloud_text, f"Keywords from {sentiment_filter.title()} Reviews" if sentiment_filter != "Semua" else "Keywords from All Reviews")
                                    
                            except Exception as e:
                                st.warning(f"Word cloud generation failed: {str(e)}")
                                
                                # Fallback: Show as bar chart
                                st.subheader("📊 Top Keywords (Bar Chart)")
                                top_words_df = pd.DataFrame(review_keywords[:20], columns=['word', 'count'])
                                fig = px.bar(
                                    top_words_df,
                                    x='word',
                                    y='count',
                                    title="Top 20 Keywords from Reviews",
                                    labels={'word': 'Keywords', 'count': 'Frequency'}
                                )
                                fig.update_layout(height=400, xaxis_tickangle=-45)
                                st.plotly_chart(fig, use_container_width=True)
                        
                        else:
                            # If wordcloud not available, show bar chart
                            st.subheader("📊 Top Keywords Visualization")
                            top_words_df = pd.DataFrame(review_keywords[:20], columns=['word', 'count'])
                            fig = px.bar(
                                top_words_df,
                                x='word',
                                y='count',
                                title="Top 20 Keywords from Reviews",
                                labels={'word': 'Keywords', 'count': 'Frequency'},
                                color='count',
                                color_continuous_scale='viridis'
                            )
                            fig.update_layout(height=400, xaxis_tickangle=-45)
                            st.plotly_chart(fig, use_container_width=True)
                    
                    else:
                        st.info("📝 No keywords found in review text.")
                        
                except Exception as e:
                    st.error(f"Error extracting keywords from reviews: {str(e)}")
                    
                    # Fallback to database keywords if available
                    if not filtered_keywords_data.empty:
                        st.info("🔄 Falling back to database keywords...")
                        # ... existing database keywords code ...
            
            else:
                st.warning("📝 No review text available for keyword extraction.")
                
                # Show database keywords as fallback
                if not filtered_keywords_data.empty:
                    st.info("📊 Showing keywords from database instead...")
                    # Show database keywords code here
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        for i, (_, row) in enumerate(filtered_keywords_data.head(15).iterrows(), 1):
                            if pd.notna(row['keyword']) and row['keyword'] != '':
                                category = row.get('keyword_category', 'general')
                                st.markdown(f"{i}. **{row['keyword']}** ({category}) - {row['frequency']} mentions")
                    
                    with col2:
                        remaining_keywords = filtered_keywords_data.iloc[15:30]
                        for i, (_, row) in enumerate(remaining_keywords.iterrows(), 16):
                            if pd.notna(row['keyword']) and row['keyword'] != '':
                                category = row.get('keyword_category', 'general')
                                st.markdown(f"{i}. **{row['keyword']}** ({category}) - {row['frequency']} mentions")
        
            # Sample reviews by sentiment
            st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
            st.subheader("📝 Sample Reviews by Sentiment")
            
            col1, col2, col3 = st.columns(3)
            
            sentiments = ['positive', 'negative', 'neutral']
            columns = [col1, col2, col3]
            
            for sentiment, col in zip(sentiments, columns):
                with col:
                    sentiment_reviews = filtered_data[
                        filtered_data['sentiment_label'] == sentiment
                    ]['review_text'].dropna()
                    
                    st.markdown(f"**{sentiment.title()} Reviews:**")
                    if not sentiment_reviews.empty:
                        # Show up to 3 sample reviews
                        for i, review in enumerate(sentiment_reviews.head(3)):
                            sample_review = str(review)
                            if len(sample_review) > 100:
                                sample_review = sample_review[:100] + "..."
                            st.markdown(f"{i+1}. *{sample_review}*")
                            st.markdown("---")
                    else:
                        st.info("No reviews available")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sentiment trends over time
            st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
            st.subheader("📅 Tren Sentimen dari Waktu ke Waktu")
            
            monthly_sentiment = filtered_data.groupby(['year', 'month', 'sentiment_label']).size().reset_index(name='count')
            
            if not monthly_sentiment.empty and len(monthly_sentiment) > 3:
                monthly_sentiment['date'] = pd.to_datetime(monthly_sentiment[['year', 'month']].assign(day=1))
                
                fig = px.line(
                    monthly_sentiment,
                    x='date',
                    y='count',
                    color='sentiment_label',
                    title="Monthly Sentiment Trends",
                    labels={'date': 'Date', 'count': 'Number of Reviews'},
                    color_discrete_map={
                        'positive': '#2E8B57',
                        'negative': '#DC143C',
                        'neutral': '#4682B4'
                    },
                    markers=True
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient data for trend analysis")
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.warning("⚠️ No sentiment data available")
            st.info("Pastikan proses ETL telah dijalankan dan tabel dim_sentiment berisi data.")