import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Import WordCloud with error handling
try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

from sqlalchemy import create_engine, text
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# NLTK imports with error handling - DISABLE FOR NOW
NLTK_AVAILABLE = False

# Add the parent directory to the path to import from streamlit-etl-app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'streamlit-etl-app'))

# Fallback configuration if import fails
DB_CONFIG = {
    'host': 'localhost',
    'database': 'dw_bi',
    'user': 'postgres',
    'password': 'postgres',
    'port': '5432'
}

def create_engine_connection():
    return create_engine(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

# Page configuration
st.set_page_config(
    page_title="🍽️ Restaurant Analytics Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stSelectbox > div > div > select {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_engine():
    try:
        return create_engine_connection()
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Data loading functions
@st.cache_data(ttl=300)
def load_data(query):
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()
    
    try:
        with engine.connect() as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Check if tables exist
@st.cache_data(ttl=300) 
def check_table_exists(table_name):
    engine = get_engine()
    if engine is None:
        return False
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table_name}'
                );
            """))
            return result.scalar()
    except:
        return False

# Safe WordCloud function
def create_safe_wordcloud(text_data, title="Word Cloud"):
    if not WORDCLOUD_AVAILABLE:
        st.info("📝 WordCloud visualization tidak tersedia.")
        return
    
    if not text_data or not isinstance(text_data, str) or len(text_data.strip()) == 0:
        st.info("📝 Tidak ada data keyword yang tersedia untuk word cloud.")
        return
    
    try:
        wordcloud = WordCloud(
            width=600, 
            height=300, 
            background_color='white',
            colormap='viridis',
            max_words=50,
            relative_scaling=0.5,
            min_font_size=8
        ).generate(text_data)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(title, fontsize=14, pad=15)
        st.pyplot(fig)
        plt.close(fig)
    except Exception as e:
        st.info("📝 Menggunakan tampilan alternatif untuk keywords")

# Sidebar
st.sidebar.title("🍽️ Restaurant Analytics Dashboard")
st.sidebar.markdown("---")

# Dashboard selection as dropdown
dashboard_options = [
    "Segmentasi Pelanggan & Analisis Performa Gabungan",
    "Performa Lokasi & Tren Rating", 
    "Sentimen & Suara Pelanggan"
]

dashboard_selection = st.sidebar.selectbox(
    "📊 Pilih Dashboard",
    dashboard_options,
    key="dashboard_nav"
)

st.sidebar.markdown("---")

# Initialize filters in sidebar
if 'filters_initialized' not in st.session_state:
    st.session_state.filters_initialized = True

# Dashboard 1: Segmentasi Pelanggan & Analisis Performa Gabungan
if dashboard_selection == "Segmentasi Pelanggan & Analisis Performa Gabungan":
    st.markdown('<h1 class="main-header">🎯 Segmentasi Pelanggan & Analisis Performa Gabungan</h1>', unsafe_allow_html=True)
    
    # Load data
    @st.cache_data(ttl=300)
    def load_segmentation_data():
        query = """
        SELECT 
            dr.organization_name,
            dl.country,
            dl.state,
            dl.city,
            dc.category_name,
            AVG(frr.rating) as avg_rating,
            COUNT(frr.review_id) as total_reviews,
            SUM(frr.number_of_reviews) as total_customer_reviews,
            AVG(frr.review_length) as avg_review_length,
            dt.year,
            dt.month
        FROM fact_restaurant_reviews frr
        JOIN dim_restaurant dr ON frr.restaurant_key = dr.restaurant_key
        JOIN dim_location dl ON frr.location_key = dl.location_key
        JOIN dim_category dc ON frr.category_key = dc.category_key
        JOIN dim_time dt ON frr.time_key = dt.time_key
        GROUP BY dr.organization_name, dl.country, dl.state, dl.city, dc.category_name, dt.year, dt.month
        """
        return load_data(query)
    
    segmentation_data = load_segmentation_data()
    
    if not segmentation_data.empty:
        # Sidebar Filters
        st.sidebar.subheader("🔍 Filter Data")
        
        selected_org = st.sidebar.selectbox(
            "Pilih Organisasi",
            ["Semua"] + list(segmentation_data['organization_name'].unique()),
            key="seg_org"
        )
        
        selected_location = st.sidebar.selectbox(
            "Pilih Lokasi",
            ["Semua"] + list(segmentation_data['city'].unique()),
            key="seg_location"
        )
        
        # Filter data
        filtered_data = segmentation_data.copy()
        if selected_org != "Semua":
            filtered_data = filtered_data[filtered_data['organization_name'] == selected_org]
        if selected_location != "Semua":
            filtered_data = filtered_data[filtered_data['city'] == selected_location]
        
        # Performance metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>📊 Total Reviews</h3>
                    <h2>{filtered_data['total_reviews'].sum():,}</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            avg_rating = filtered_data['avg_rating'].mean() if len(filtered_data) > 0 else 0
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>⭐ Average Rating</h3>
                    <h2>{avg_rating:.2f}</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col3:
            total_restaurants = filtered_data['organization_name'].nunique()
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>🏪 Total Restaurants</h3>
                    <h2>{total_restaurants}</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📈 Performa Lokasi Berdasarkan Rating")
            
            location_perf = filtered_data.groupby(['city', 'state']).agg({
                'avg_rating': 'mean',
                'total_reviews': 'sum'
            }).reset_index()
            
            if not location_perf.empty:
                fig = px.scatter(
                    location_perf, 
                    x='total_reviews', 
                    y='avg_rating',
                    size='total_reviews',
                    hover_data=['city', 'state'],
                    title="Location Performance Analysis",
                    labels={'total_reviews': 'Total Reviews', 'avg_rating': 'Average Rating'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available for chart")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("🗺️ Segmentasi Lokasi Berdasarkan Rating")
            
            # Create segmentation based on rating
            filtered_data['rating_segment'] = pd.cut(
                filtered_data['avg_rating'], 
                bins=[0, 2, 3, 4, 5], 
                labels=['Low (1-2)', 'Medium (2-3)', 'Good (3-4)', 'Excellent (4-5)']
            )
            
            segment_counts = filtered_data['rating_segment'].value_counts()
            
            fig = px.treemap(
                values=segment_counts.values,
                names=segment_counts.index,
                title="Rating Segmentation",
                color=segment_counts.values,
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Restaurant performance clustering
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🎯 Pengelompokan Kinerja Restoran")
        
        restaurant_perf = filtered_data.groupby('organization_name').agg({
            'avg_rating': 'mean',
            'total_reviews': 'sum',
            'total_customer_reviews': 'sum'
        }).reset_index()
        
        # Create performance segments
        restaurant_perf['performance_score'] = (
            restaurant_perf['avg_rating'] * 0.5 + 
            np.log1p(restaurant_perf['total_reviews']) * 0.3 +
            np.log1p(restaurant_perf['total_customer_reviews']) * 0.2
        )
        
        fig = px.scatter(
            restaurant_perf,
            x='total_reviews',
            y='avg_rating',
            size='total_customer_reviews',
            color='performance_score',
            hover_data=['organization_name'],
            title="Restaurant Performance Clustering",
            labels={
                'total_reviews': 'Total Reviews',
                'avg_rating': 'Average Rating',
                'performance_score': 'Performance Score'
            },
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Performance insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("🔝 Lokasi dengan Rating Tertinggi")
            if not filtered_data.empty:
                top_locations = filtered_data.nlargest(5, 'avg_rating')[['city', 'state', 'avg_rating', 'total_reviews']]
                for _, row in top_locations.iterrows():
                    st.markdown(f"**{row['city']}, {row['state']}** - ⭐ {row['avg_rating']:.2f} ({row['total_reviews']} reviews)")
            else:
                st.info("No data available")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📉 Lokasi dengan Rating Terendah")
            if not filtered_data.empty:
                bottom_locations = filtered_data.nsmallest(5, 'avg_rating')[['city', 'state', 'avg_rating', 'total_reviews']]
                for _, row in bottom_locations.iterrows():
                    st.markdown(f"**{row['city']}, {row['state']}** - ⭐ {row['avg_rating']:.2f} ({row['total_reviews']} reviews)")
            else:
                st.info("No data available")
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ No data available for segmentation analysis")

# Dashboard 2: Performa Lokasi & Tren Rating
elif dashboard_selection == "Performa Lokasi & Tren Rating":
    st.markdown('<h1 class="main-header">📍 Performa Lokasi & Tren Rating</h1>', unsafe_allow_html=True)
    
    # Load data
    @st.cache_data(ttl=300)
    def load_location_data():
        query = """
        SELECT 
            dr.organization_name,
            dl.country,
            dl.state,
            dl.city,
            dc.category_name,
            AVG(frr.rating) as avg_rating,
            COUNT(frr.review_id) as total_reviews,
            dt.year,
            dt.month,
            dt.date_actual
        FROM fact_restaurant_reviews frr
        JOIN dim_restaurant dr ON frr.restaurant_key = dr.restaurant_key
        JOIN dim_location dl ON frr.location_key = dl.location_key
        JOIN dim_category dc ON frr.category_key = dc.category_key
        JOIN dim_time dt ON frr.time_key = dt.time_key
        GROUP BY dr.organization_name, dl.country, dl.state, dl.city, dc.category_name, 
                 dt.year, dt.month, dt.date_actual
        ORDER BY dt.date_actual
        """
        return load_data(query)
    
    location_data = load_location_data()
    
    if not location_data.empty:
        # Sidebar Filters
        st.sidebar.subheader("🔍 Filter Data")
        
        selected_org = st.sidebar.selectbox(
            "Pilih Organisasi",
            ["Semua"] + list(location_data['organization_name'].unique()),
            key="loc_org"
        )
        
        selected_time = st.sidebar.selectbox(
            "Pilih Waktu",
            ["Semua"] + [f"{year}" for year in sorted(location_data['year'].unique())],
            key="loc_time"
        )
        
        selected_location = st.sidebar.selectbox(
            "Pilih Lokasi",
            ["Semua"] + list(location_data['city'].unique()),
            key="loc_location"
        )
        
        # Filter data
        filtered_data = location_data.copy()
        if selected_org != "Semua":
            filtered_data = filtered_data[filtered_data['organization_name'] == selected_org]
        if selected_time != "Semua":
            filtered_data = filtered_data[filtered_data['year'] == int(selected_time)]
        if selected_location != "Semua":
            filtered_data = filtered_data[filtered_data['city'] == selected_location]
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>🏙️ Total Cities</h4>
                    <h2>{filtered_data['city'].nunique()}</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>🏪 Total Restaurants</h4>
                    <h2>{filtered_data['organization_name'].nunique()}</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col3:
            avg_rating = filtered_data['avg_rating'].mean() if len(filtered_data) > 0 else 0
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>⭐ Avg Rating</h4>
                    <h2>{avg_rating:.2f}</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>📊 Total Reviews</h4>
                    <h2>{filtered_data['total_reviews'].sum():,}</h2>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📊 Performa Lokasi & Tren Rating")
            
            location_perf = filtered_data.groupby('city').agg({
                'avg_rating': 'mean',
                'total_reviews': 'sum'
            }).reset_index().sort_values('avg_rating', ascending=True)
            
            if not location_perf.empty:
                fig = px.bar(
                    location_perf.tail(10),
                    x='avg_rating',
                    y='city',
                    orientation='h',
                    title="Top 10 Cities by Rating",
                    labels={'avg_rating': 'Average Rating', 'city': 'City'},
                    color='avg_rating',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No location data available")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📈 Tren Rating Bulanan")
            
            monthly_trend = filtered_data.groupby(['year', 'month']).agg({
                'avg_rating': 'mean',
                'total_reviews': 'sum'
            }).reset_index()
            
            if not monthly_trend.empty:
                monthly_trend['date'] = pd.to_datetime(monthly_trend[['year', 'month']].assign(day=1))
                
                fig = px.line(
                    monthly_trend,
                    x='date',
                    y='avg_rating',
                    title="Monthly Rating Trend",
                    labels={'date': 'Date', 'avg_rating': 'Average Rating'},
                    markers=True
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No trend data available")
            st.markdown('</div>', unsafe_allow_html=True)
    
        # Multi-line trend for top organizations
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 Tren Rating untuk Organisasi Teratas")
        
        # Get top organizations by review count
        top_orgs = filtered_data.groupby('organization_name')['total_reviews'].sum().nlargest(5).index
        trend_data = filtered_data[filtered_data['organization_name'].isin(top_orgs)]
        
        monthly_org_trend = trend_data.groupby(['organization_name', 'year', 'month']).agg({
            'avg_rating': 'mean'
        }).reset_index()
        monthly_org_trend['date'] = pd.to_datetime(monthly_org_trend[['year', 'month']].assign(day=1))
        
        fig = px.line(
            monthly_org_trend,
            x='date',
            y='avg_rating',
            color='organization_name',
            title="Rating Trends for Top Organizations",
            labels={'date': 'Date', 'avg_rating': 'Average Rating'},
            markers=True
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ No data available for location performance analysis")

# Dashboard 3: Sentimen & Suara Pelanggan
elif dashboard_selection == "Sentimen & Suara Pelanggan":
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
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📊 Distribusi Sentimen (Demo)")
            
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
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
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
                
                # Load keywords data
                query = """
                SELECT 
                    dk.keyword,
                    dk.keyword_category,
                    COALESCE(COUNT(bsk.sentiment_key), 1) as frequency
                FROM dim_keywords dk
                LEFT JOIN bridge_sentiment_keywords bsk ON dk.keyword_key = bsk.keyword_key
                WHERE dk.keyword IS NOT NULL AND dk.keyword != ''
                GROUP BY dk.keyword, dk.keyword_category
                ORDER BY frequency DESC
                LIMIT 50
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
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("☁️ Keyword Analysis")
            
            if not keywords_data.empty:
                # Show keywords as list
                st.subheader("🔤 Top Keywords")
                col1, col2 = st.columns(2)
                
                with col1:
                    for i, (_, row) in enumerate(keywords_data.head(15).iterrows(), 1):
                        if pd.notna(row['keyword']) and row['keyword'] != '':
                            category = row.get('keyword_category', 'general')
                            st.markdown(f"{i}. **{row['keyword']}** ({category}) - {row['frequency']} mentions")
                
                with col2:
                    remaining_keywords = keywords_data.iloc[15:30]
                    for i, (_, row) in enumerate(remaining_keywords.iterrows(), 16):
                        if pd.notna(row['keyword']) and row['keyword'] != '':
                            category = row.get('keyword_category', 'general')
                            st.markdown(f"{i}. **{row['keyword']}** ({category}) - {row['frequency']} mentions")
                
                # Try to create word cloud if available
                if WORDCLOUD_AVAILABLE:
                    try:
                        wordcloud_text = ' '.join([
                            f"{row['keyword']} " * max(1, min(5, int(row['frequency'])))
                            for _, row in keywords_data.iterrows() 
                            if pd.notna(row['keyword']) and isinstance(row['keyword'], str) and row['keyword'] != ''
                        ])
                        
                        if wordcloud_text.strip():
                            st.subheader("☁️ Word Cloud")
                            create_safe_wordcloud(wordcloud_text, "Most Mentioned Keywords")
                    except Exception as e:
                        st.info("Word cloud generation skipped")
                
            else:
                st.info("📝 No keywords data available. Keywords will be generated during ETL process.")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sample reviews by sentiment
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
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
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
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

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🍽️ Restaurant Analytics Dashboard | Built with Streamlit</p>
        <p>💡 Tip: Jalankan proses ETL terlebih dahulu untuk mendapatkan data sentiment yang lengkap</p>
    </div>
    """, 
    unsafe_allow_html=True
)