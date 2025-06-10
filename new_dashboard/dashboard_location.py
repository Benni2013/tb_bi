import streamlit as st
import pandas as pd
import plotly.express as px
from shared_utils import load_data, load_css

def render_location_dashboard():
    load_css()
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
            st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
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
            st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
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
        st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
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