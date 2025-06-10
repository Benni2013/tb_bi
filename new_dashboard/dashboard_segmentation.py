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
            
            # Debug: Show data info
            st.write(f"Debug: Filtered data shape: {filtered_data.shape}")
            st.write(f"Debug: Rating range: {filtered_data['avg_rating'].min():.2f} to {filtered_data['avg_rating'].max():.2f}")
            
            # Create segmentation based on rating - with better handling
            filtered_data_clean = filtered_data.dropna(subset=['avg_rating']).copy()
            
            if not filtered_data_clean.empty and len(filtered_data_clean) > 0:
                # Use simpler binning approach
                def categorize_rating(rating):
                    if rating <= 2.0:
                        return 'Low (0-2)'
                    elif rating <= 3.0:
                        return 'Medium (2-3)'
                    elif rating <= 4.0:
                        return 'Good (3-4)'
                    else:
                        return 'Excellent (4-5)'
                
                # Apply categorization
                filtered_data_clean['rating_segment'] = filtered_data_clean['avg_rating'].apply(categorize_rating)
                
                # Count segments
                segment_counts = filtered_data_clean['rating_segment'].value_counts()
                
                st.write(f"Debug: Segment counts: {segment_counts}")
                
                if len(segment_counts) > 0:
                    # Create DataFrame for treemap
                    treemap_data = pd.DataFrame({
                        'segment': segment_counts.index,
                        'count': segment_counts.values,
                        'percentage': (segment_counts.values / segment_counts.sum() * 100).round(1)
                    })
                    
                    # Try different treemap approaches
                    try:
                        # Method 1: Using px.treemap with DataFrame
                        fig = px.treemap(
                            treemap_data,
                            path=['segment'],
                            values='count',
                            title="Rating Segmentation Distribution",
                            color='count',
                            color_continuous_scale='RdYlGn',
                            hover_data={'percentage': True}
                        )
                        fig.update_layout(height=400, font_size=12)
                        fig.update_traces(textinfo="label+value+percent parent")
                        st.plotly_chart(fig, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Treemap error: {e}")
                        
                        # Fallback: Use bar chart instead
                        fig = px.bar(
                            treemap_data,
                            x='segment',
                            y='count',
                            title="Rating Segmentation Distribution (Bar Chart)",
                            color='count',
                            color_continuous_scale='RdYlGn',
                            text='count'
                        )
                        fig.update_layout(height=400)
                        fig.update_traces(texttemplate='%{text}', textposition='outside')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Show segment breakdown as table
                    st.markdown("**Segment Breakdown:**")
                    for _, row in treemap_data.iterrows():
                        st.markdown(f"- **{row['segment']}**: {row['count']} locations ({row['percentage']:.1f}%)")
                        
                else:
                    st.info("No rating segments available - all ratings may be in same range")
                    
                    # Show alternative visualization - histogram
                    fig = px.histogram(
                        filtered_data_clean,
                        x='avg_rating',
                        nbins=10,
                        title="Rating Distribution Histogram",
                        labels={'avg_rating': 'Average Rating', 'count': 'Number of Locations'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
            else:
                st.info("No rating data available for segmentation")
                
                # Show sample data if available
                if not filtered_data.empty:
                    st.write("Sample data:")
                    st.dataframe(filtered_data[['city', 'avg_rating']].head())
                
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