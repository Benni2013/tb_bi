import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from shared_utils import load_data, load_css

def render_segmentation_dashboard():
    load_css()
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