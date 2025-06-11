import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sqlalchemy import create_engine, text
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Import WordCloud with error handling
try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

# Database configuration
# DB_CONFIG = {
#     'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
#     'database': 'postgres?pgbouncer=true',
#     'user': 'postgres.cwbeoriyhbsamwvhkuna',
#     'password': 'dw_bi',
#     'port': '6543'
# }

# def create_engine_connection():
#     return create_engine(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

def create_engine_connection():
    return create_engine(f"postgresql://postgres.cwbeoriyhbsamwvhkuna:dw_dashboard_bi@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres")

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

# Custom CSS
def load_css():
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
            padding: 0.5rem;
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

def render_footer():
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