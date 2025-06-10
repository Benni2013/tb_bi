import streamlit as st
from dashboard_segmentation import render_segmentation_dashboard
from dashboard_location import render_location_dashboard
from dashboard_sentiment import render_sentiment_dashboard
from shared_utils import render_footer

# Page configuration
st.set_page_config(
    page_title="🍽️ Restaurant Analytics Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Render selected dashboard
if dashboard_selection == "Segmentasi Pelanggan & Analisis Performa Gabungan":
    render_segmentation_dashboard()
elif dashboard_selection == "Performa Lokasi & Tren Rating":
    render_location_dashboard()
elif dashboard_selection == "Sentimen & Suara Pelanggan":
    render_sentiment_dashboard()

# Footer
render_footer()