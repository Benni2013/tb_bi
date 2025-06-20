import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from shared_utils import load_data, load_css
from datetime import datetime, date
import folium
from streamlit_folium import folium_static
import json
import requests

def render_location_dashboard():
    load_css()
    st.markdown('<h1 class="main-header">📍 Performa Lokasi & Tren Rating</h1>', unsafe_allow_html=True)
    
    # Mapping kode state ke nama state
    state_mapping = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
        'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
        'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
        'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
        'DC': 'District of Columbia', 'AS': 'American Samoa', 'GU': 'Guam', 'MP': 'Northern Mariana Islands',
        'PR': 'Puerto Rico', 'VI': 'U.S. Virgin Islands', 'AB': 'Alberta', 'BC': 'British Columbia',
        'MB': 'Manitoba', 'NB': 'New Brunswick', 'NL': 'Newfoundland and Labrador', 'NS': 'Nova Scotia',
        'ON': 'Ontario', 'PE': 'Prince Edward Island', 'QC': 'Quebec', 'SK': 'Saskatchewan',
        'NT': 'Northwest Territories', 'NU': 'Nunavut', 'YT': 'Yukon'
    }
    
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
        # Buat mapping untuk dropdown states
        unique_states = sorted(location_data['state'].unique())
        state_options = []
        reverse_mapping = {}
        
        for state_code in unique_states:
            state_name = state_mapping.get(state_code, state_code)
            display_name = f"{state_name} ({state_code})"
            state_options.append(display_name)
            reverse_mapping[display_name] = state_code
        
        # Get date range from data for time filter
        location_data['date'] = pd.to_datetime(location_data['date_actual'])
        min_date = location_data['date'].min().date()
        max_date = location_data['date'].max().date()
        
        # Sidebar Filters
        st.sidebar.subheader("🔍 Filter Data")
        
        # MULTI-SELECT ORGANIZATION FILTER WITH MAX HEIGHT
        st.sidebar.markdown("**Pilih Organisasi (Multi-Select):**")
        available_orgs = sorted(location_data['organization_name'].unique())
        
        # Add custom CSS for max height
        st.sidebar.markdown("""
        <style>
        .stMultiSelect > div > div > div {
            max-height: 200px;
            overflow-y: auto;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Option to select all organizations
        select_all_orgs = st.sidebar.checkbox("Pilih Semua Organisasi", value=True, key="select_all_orgs")
        
        if select_all_orgs:
            selected_orgs = st.sidebar.multiselect(
                "Pilih organisasi:",
                options=available_orgs,
                default=available_orgs,
                key="selected_orgs",
                help="Scroll untuk melihat lebih banyak pilihan"
            )
        else:
            selected_orgs = st.sidebar.multiselect(
                "Pilih organisasi:",
                options=available_orgs,
                default=[],
                key="selected_orgs_custom",
                help="Scroll untuk melihat lebih banyak pilihan"
            )
        
        # Show selected count with color coding
        if selected_orgs:
            if len(selected_orgs) == len(available_orgs):
                st.sidebar.success(f"✅ Semua organisasi dipilih ({len(selected_orgs)})")
            else:
                st.sidebar.info(f"📊 {len(selected_orgs)} dari {len(available_orgs)} organisasi dipilih")
        else:
            st.sidebar.warning("⚠️ Tidak ada organisasi dipilih")
        
        # TIME INTERVAL FILTER
        st.sidebar.markdown("**Pilih Periode Waktu:**")
        
        # Quick time range options
        time_range_option = st.sidebar.selectbox(
            "Pilih Range Cepat:",
            ["Custom Range", "Last 3 Months", "Last 6 Months", "Last 1 Year", "All Time"],
            key="time_range_option"
        )
        
        # Calculate date range based on selection
        if time_range_option == "Last 3 Months":
            start_date = max_date - pd.DateOffset(months=3)
            end_date = max_date
            st.sidebar.info(f"📅 {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")
        elif time_range_option == "Last 6 Months":
            start_date = max_date - pd.DateOffset(months=6)
            end_date = max_date
            st.sidebar.info(f"📅 {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")
        elif time_range_option == "Last 1 Year":
            start_date = max_date - pd.DateOffset(years=1)
            end_date = max_date
            st.sidebar.info(f"📅 {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")
        elif time_range_option == "All Time":
            start_date = min_date
            end_date = max_date
            st.sidebar.info(f"📅 {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}")
        else:  # Custom Range
            st.sidebar.markdown("**Pilih Tanggal:**")
            col1, col2 = st.sidebar.columns(2)
            with col1:
                start_date = st.date_input(
                    "Dari:",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="start_date"
                )
            with col2:
                end_date = st.date_input(
                    "Sampai:",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="end_date"
                )
            
            # Validate date range
            if start_date > end_date:
                st.sidebar.error("❌ Tanggal mulai tidak boleh lebih dari tanggal akhir!")
                start_date, end_date = end_date, start_date
            
            # Show selected period duration
            duration_days = (end_date - start_date).days
            st.sidebar.success(f"📊 Durasi: {duration_days} hari")
        
        # STATE FILTER (unchanged)
        selected_state_display = st.sidebar.selectbox(
            "Pilih State",
            ["Semua"] + state_options,
            key="loc_state"
        )
        
        # Convert display name back to state code
        if selected_state_display != "Semua":
            selected_state_code = reverse_mapping[selected_state_display]
        else:
            selected_state_code = "Semua"
        
        # APPLY FILTERS
        filtered_data = location_data.copy()
        
        # Filter by organizations (multi-select)
        if selected_orgs:
            filtered_data = filtered_data[filtered_data['organization_name'].isin(selected_orgs)]
        else:
            # If no orgs selected, show empty result
            filtered_data = pd.DataFrame()
        
        # Filter by date range
        if not filtered_data.empty:
            filtered_data = filtered_data[
                (filtered_data['date'].dt.date >= start_date) & 
                (filtered_data['date'].dt.date <= end_date)
            ]
        
        # Filter by state
        if selected_state_code != "Semua" and not filtered_data.empty:
            filtered_data = filtered_data[filtered_data['state'] == selected_state_code]
        
        # Check if we have data after filtering
        if filtered_data.empty:
            st.warning("⚠️ Tidak ada data yang cocok dengan filter yang dipilih. Silakan ubah filter.")
            
            # Show current filter summary in an expander
            with st.expander("📋 Filter Aktif Saat Ini", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🏢 Organisasi:**")
                    if selected_orgs:
                        for i, org in enumerate(selected_orgs[:3]):
                            st.markdown(f"• {org}")
                        if len(selected_orgs) > 3:
                            st.markdown(f"• ... dan {len(selected_orgs) - 3} lainnya")
                    else:
                        st.markdown("*Tidak ada yang dipilih*")
                
                with col2:
                    st.markdown("**📅 Periode:**")
                    st.markdown(f"• {start_date.strftime('%d %b %Y')}")
                    st.markdown(f"• {end_date.strftime('%d %b %Y')}")
                    st.markdown(f"• Durasi: {(end_date - start_date).days} hari")
                
                with col3:
                    st.markdown("**🗺️ Lokasi:**")
                    st.markdown(f"• State: {selected_state_display}")
            
            return
        
        # Enhanced Performance Metrics (rest of the code remains unchanged)
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate additional metrics
        avg_rating_overall = filtered_data['avg_rating'].mean() if len(filtered_data) > 0 else 0
        total_reviews_overall = filtered_data['total_reviews'].sum()
        growth_rate = calculate_growth_rate(filtered_data)
        
        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>🏙️ Total Cities</h4>
                    <h2>{filtered_data['city'].nunique()}</h2>
                    <p>Active Locations</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>🏪 Total Brands</h4>
                    <h2>{filtered_data['organization_name'].nunique()}</h2>
                    <p>Brands Analyzed</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col3:
            rating_trend = "📈" if growth_rate > 0 else "📉" if growth_rate < 0 else "➡️"
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>⭐ Avg Rating</h4>
                    <h2>{avg_rating_overall:.2f}</h2>
                    <p>{rating_trend} {abs(growth_rate):.1f}% trend</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h4>📊 Total Reviews</h4>
                    <h2>{total_reviews_overall:,}</h2>
                    <p>Customer Feedback</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # KEY INSIGHT ALERTS
        st.markdown("### 🚨 Key Insights & Alerts")
        
        # Identify problem areas
        city_performance = filtered_data.groupby('city').agg({
            'avg_rating': 'mean',
            'total_reviews': 'sum'
        }).reset_index()
        
        # Top and bottom performers
        top_cities = city_performance.nlargest(3, 'avg_rating')
        bottom_cities = city_performance.nsmallest(3, 'avg_rating')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("🏆 **Top Performers**")
            for _, city in top_cities.iterrows():
                st.write(f"• **{city['city']}**: ⭐ {city['avg_rating']:.2f}")
        
        with col2:
            st.error("⚠️ **Needs Attention**")
            for _, city in bottom_cities.iterrows():
                st.write(f"• **{city['city']}**: ⭐ {city['avg_rating']:.2f}")
        
        with col3:
            # Review volume analysis
            high_volume = city_performance.nlargest(3, 'total_reviews')
            st.info("📢 **High Activity Locations**")
            for _, city in high_volume.iterrows():
                st.write(f"• **{city['city']}**: {city['total_reviews']:,} reviews")
                
        # SEASONAL ANALYSIS - untuk Tim Pemasaran
        st.markdown("### 📅 Analisis Seasonal untuk Strategi Pemasaran")
        seasonal_data = filtered_data.copy()
        seasonal_data['quarter'] = seasonal_data['date'].dt.quarter
        seasonal_data['season'] = seasonal_data['quarter'].map({
            1: 'Winter (Q1)', 2: 'Spring (Q2)', 
            3: 'Summer (Q3)', 4: 'Fall (Q4)'
        })

        seasonal_performance = seasonal_data.groupby('season').agg({
            'avg_rating': 'mean',
            'total_reviews': 'sum'
        }).reset_index()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🌱 Best Season for Marketing")
            best_season = seasonal_performance.loc[seasonal_performance['avg_rating'].idxmax()]
            st.success(f"**{best_season['season']}** - ⭐ {best_season['avg_rating']:.2f}")

        with col2:
            st.subheader("📈 Most Active Season")
            active_season = seasonal_performance.loc[seasonal_performance['total_reviews'].idxmax()]
            st.info(f"**{active_season['season']}** - 📝 {active_season['total_reviews']:,} reviews")
        
        # ENHANCED VISUALIZATIONS
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
            st.subheader("📊 Performance Matrix: Rating vs Volume")
            
            location_perf = filtered_data.groupby('city').agg({
                'avg_rating': 'mean',
                'total_reviews': 'sum'
            }).reset_index()
            
            if not location_perf.empty:
                # Create performance quadrants
                avg_rating_median = location_perf['avg_rating'].median()
                avg_reviews_median = location_perf['total_reviews'].median()
                
                # Add quadrant labels
                def get_quadrant(row):
                    if row['avg_rating'] >= avg_rating_median and row['total_reviews'] >= avg_reviews_median:
                        return "⭐ High Rating, High Volume"
                    elif row['avg_rating'] >= avg_rating_median and row['total_reviews'] < avg_reviews_median:
                        return "🎯 High Rating, Low Volume"
                    elif row['avg_rating'] < avg_rating_median and row['total_reviews'] >= avg_reviews_median:
                        return "⚠️ Low Rating, High Volume"
                    else:
                        return "🔍 Low Rating, Low Volume"
                
                location_perf['quadrant'] = location_perf.apply(get_quadrant, axis=1)
                
                fig = px.scatter(
                    location_perf,
                    x='total_reviews',
                    y='avg_rating',
                    size=[20] * len(location_perf),  # Fixed size for better visibility
                    hover_data=['city'],
                    color='quadrant',
                    title="Performance Matrix by City",
                    labels={'total_reviews': 'Total Reviews', 'avg_rating': 'Average Rating'},
                    color_discrete_map={
                        "⭐ High Rating, High Volume": "#2E8B57",
                        "🎯 High Rating, Low Volume": "#4682B4", 
                        "⚠️ Low Rating, High Volume": "#FF6347",
                        "🔍 Low Rating, Low Volume": "#778899"
                    }
                )
                
                # Add quadrant lines
                fig.add_hline(y=avg_rating_median, line_dash="dash", line_color="gray", opacity=0.5)
                fig.add_vline(x=avg_reviews_median, line_dash="dash", line_color="gray", opacity=0.5)
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # REPLACED: Review Volume Trend with Rating Map per State
            st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
            st.subheader("🗺️ Rating Peta Per State")
            
            # Prepare data for the map
            state_performance = filtered_data.groupby('state').agg({
                'avg_rating': 'mean',
                'total_reviews': 'sum'
            }).reset_index()
            
            if not state_performance.empty:
                try:
                    # Load GeoJSON untuk state di USA
                    @st.cache_data(ttl=3600)  # Cache for 1 hour
                    def load_geojson():
                        url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json'
                        response = requests.get(url)
                        return response.json()
                    
                    geojson_data = load_geojson()
                    
                    # Create the map
                    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
                    
                    # Add choropleth layer
                    folium.Choropleth(
                        geo_data=geojson_data,
                        name='choropleth',
                        data=state_performance,
                        columns=['state', 'avg_rating'],
                        key_on='feature.id',  # 'id' pada geojson = kode state (CA, NY, dll)
                        fill_color='YlOrRd',
                        fill_opacity=0.7,
                        line_opacity=0.2,
                        legend_name='Average Rating per State',
                        nan_fill_color='lightgray'
                    ).add_to(m)
                    
                    # Add markers for better interactivity
                    for _, row in state_performance.iterrows():
                        # Get state center coordinates (simplified mapping)
                        state_coords = get_state_coordinates(row['state'])
                        if state_coords:
                            folium.CircleMarker(
                                location=state_coords,
                                radius=min(max(row['avg_rating'] * 2, 3), 15),
                                popup=f"""
                                <b>{state_mapping.get(row['state'], row['state'])}</b><br>
                                Rating: {row['avg_rating']:.2f}<br>
                                Reviews: {row['total_reviews']:,}
                                """,
                                color='darkred',
                                fill=True,
                                fillColor='red',
                                fillOpacity=0.6
                            ).add_to(m)
                    
                    # Display the map
                    folium_static(m, width=600, height=400)
                    
                    
                except Exception as e:
                    st.error(f"❌ Error loading map: {str(e)}")
                    # Fallback to bar chart
                    fig = px.bar(
                        state_performance.sort_values('avg_rating', ascending=True).tail(10),
                        x='avg_rating',
                        y='state',
                        orientation='h',
                        title="Top 10 States by Average Rating",
                        labels={'avg_rating': 'Average Rating', 'state': 'State'},
                        color='avg_rating',
                        color_continuous_scale='YlOrRd'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📍 No state-level data available for mapping")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Rating Trend Analysis
        st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
        st.subheader("📈 Rating Trend Analysis with Benchmarks")
        
        monthly_trend = filtered_data.groupby(['year', 'month']).agg({
            'avg_rating': 'mean',
            'total_reviews': 'sum'
        }).reset_index()
        
        if not monthly_trend.empty:
            monthly_trend['date'] = pd.to_datetime(monthly_trend[['year', 'month']].assign(day=1))
            
            # Create subplot with dual axis
            fig = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=["Rating Trend with Volume Context"]
            )
            
            # Add rating line
            fig.add_trace(
                go.Scatter(
                    x=monthly_trend['date'],
                    y=monthly_trend['avg_rating'],
                    mode='lines+markers',
                    name='Average Rating',
                    line=dict(color='#2E8B57', width=3),
                    marker=dict(size=8)
                ),
                secondary_y=False
            )
            
            # Add review volume bars
            fig.add_trace(
                go.Bar(
                    x=monthly_trend['date'],
                    y=monthly_trend['total_reviews'],
                    name='Review Volume',
                    opacity=0.3,
                    marker_color='#4682B4'
                ),
                secondary_y=True
            )
            
            # Add benchmark lines
            overall_avg = monthly_trend['avg_rating'].mean()
            fig.add_hline(y=overall_avg, line_dash="dash", line_color="red", 
                         annotation_text=f"Overall Average: {overall_avg:.2f}")
            
            # Set axis labels
            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Average Rating", secondary_y=False)
            fig.update_yaxes(title_text="Review Volume", secondary_y=True)
            
            fig.update_layout(height=500, title="📊 Rating Performance vs Review Activity")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Competitive Analysis (only show if multiple orgs selected)
        if len(selected_orgs) > 1:
            st.markdown('<hr style="border: 1px solid white; margin: 20px 0;">', unsafe_allow_html=True)
            st.subheader("🏆 Competitive Landscape Analysis")
                    
            org_performance = filtered_data.groupby('organization_name').agg({
                'avg_rating': 'mean',
                'total_reviews': 'sum',
                'city': 'nunique'
            }).reset_index().rename(columns={'city': 'locations_count'})
            
            # Sort by total reviews untuk menampilkan yang paling aktif di atas
            org_performance = org_performance.sort_values('total_reviews', ascending=True)
            
            # Create the horizontal bar chart with total_reviews on x-axis and colored by avg_rating
            fig = px.bar(
                org_performance.tail(15),  # Show top 15 organizations by review volume
                x='total_reviews',  # X-axis: Total Reviews
                y='organization_name',
                orientation='h',
                title="Top Organizations by Review Volume (Colored by Average Rating)",
                labels={
                    'total_reviews': 'Total Reviews', 
                    'organization_name': 'Organization',
                    'avg_rating': 'Average Rating'
                },
                color='avg_rating',  # Color by average rating
                color_continuous_scale='RdYlGn',  # Red (low) to Yellow to Green (high)
                hover_data={
                    'avg_rating': ':.2f',
                    'total_reviews': ':,',
                    'locations_count': True
                },
                text='total_reviews'  # Show review numbers on bars
            )
            
            # Customize the chart
            fig.update_traces(
                texttemplate='%{text:,}',  # Format numbers with commas
                textposition='outside'     # Place text outside bars
            )
            
            # Update layout for better readability
            fig.update_layout(
                height=500,
                xaxis_title="Total Number of Reviews",
                yaxis_title="Organization",
                coloraxis_colorbar=dict(
                    title="Average Rating",
                    title_side="right"
                ),
                margin=dict(l=200),  # More left margin for org names
                font=dict(size=12)
            )
            
            # Add range indicator for colorbar
            fig.update_coloraxes(
                colorbar_title_text="Average Rating ⭐",
                cmin=org_performance['avg_rating'].min(),
                cmax=org_performance['avg_rating'].max()
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add summary insights below the chart
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Most active organization
                most_active = org_performance.loc[org_performance['total_reviews'].idxmax()]
                st.success(f"""
                **📊 Most Active:**
                - **{most_active['organization_name']}**
                - {most_active['total_reviews']:,} reviews
                - ⭐ {most_active['avg_rating']:.2f} avg rating
                """)
            
            with col2:
                # Highest rated organization (among those with significant reviews)
                # Filter to orgs with at least 10% of max reviews to avoid outliers
                min_reviews_threshold = org_performance['total_reviews'].max() * 0.1
                qualified_orgs = org_performance[org_performance['total_reviews'] >= min_reviews_threshold]
                
                if not qualified_orgs.empty:
                    highest_rated = qualified_orgs.loc[qualified_orgs['avg_rating'].idxmax()]
                    st.info(f"""
                    **⭐ Highest Quality:**
                    - **{highest_rated['organization_name']}**
                    - ⭐ {highest_rated['avg_rating']:.2f} avg rating
                    - {highest_rated['total_reviews']:,} reviews
                    """)
            
            with col3:
                # Best overall performance (balanced rating and volume)
                org_performance['balanced_score'] = (
                    org_performance['avg_rating'] * 0.6 + 
                    (org_performance['total_reviews'] / org_performance['total_reviews'].max()) * 5 * 0.4
                )
                best_overall = org_performance.loc[org_performance['balanced_score'].idxmax()]
                st.warning(f"""
                **🏆 Best Overall:**
                - **{best_overall['organization_name']}**
                - ⭐ {best_overall['avg_rating']:.2f} rating
                - {best_overall['total_reviews']:,} reviews
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        
        
        # Action Items Section
        # st.markdown("### 🎯 Recommended Actions")
        
        # col1, col2 = st.columns(2)
        
        # with col1:
        #     st.markdown("""
        #     **🔴 Diperlukan Tindakan Segera:**
        #     - Meninjau operasi di lokasi yang berkinerja buruk
        #     - Menerapkan program pelatihan layanan pelanggan
        #     - Menangani keluhan khusus di area dengan peringkat rendah
        #     - Mempertimbangkan audit operasional untuk lokasi-lokasi yang bermasalah
        #     """)
        
        # with col2:
        #     st.markdown("""
        #     **🟢 Peluang Pertumbuhan:**
        #     - Meniru praktik terbaik dari para pemain terbaik
        #     - Meningkatkan pemasaran di area dengan peringkat tinggi dan volume rendah
        #     - Memperluas model lokasi yang berhasil
        #     - Memantau strategi pesaing di pasar-pasar utama
        #     """)
        
    else:
        st.warning("⚠️ No data available for location performance analysis")

def get_state_coordinates(state_code):
    """Get approximate center coordinates for US states"""
    # Simplified state coordinates mapping
    coordinates = {
        'AL': [32.806671, -86.791130], 'AK': [61.370716, -152.404419], 'AZ': [33.729759, -111.431221],
        'AR': [34.969704, -92.373123], 'CA': [36.116203, -119.681564], 'CO': [39.059811, -105.311104],
        'CT': [41.767, -72.677], 'DE': [39.161921, -75.526755], 'FL': [27.766279, -81.686783],
        'GA': [33.76, -84.39], 'HI': [21.30895, -157.826182], 'ID': [44.240459, -114.478828],
        'IL': [40.349457, -88.986137], 'IN': [39.790942, -86.147685], 'IA': [42.011539, -93.210526],
        'KS': [38.526600, -96.726486], 'KY': [37.66814, -84.86311], 'LA': [31.169546, -91.867805],
        'ME': [44.323535, -69.765261], 'MD': [39.063946, -76.802101], 'MA': [42.230171, -71.530106],
        'MI': [43.326618, -84.536095], 'MN': [45.694454, -93.900192], 'MS': [32.320, -90.207],
        'MO': [38.572954, -92.189283], 'MT': [47.052952, -109.633040], 'NE': [41.12537, -98.268082],
        'NV': [37.839333, -116.46048], 'NH': [43.452492, -71.563896], 'NJ': [40.221741, -74.756138],
        'NM': [34.97273, -105.032363], 'NY': [42.659829, -75.615], 'NC': [35.771, -78.638],
        'ND': [47.555049, -101.002012], 'OH': [40.269789, -82.799043], 'OK': [35.482309, -97.534994],
        'OR': [44.931109, -123.029159], 'PA': [40.269789, -76.875613], 'RI': [41.82355, -71.422132],
        'SC': [33.836082, -81.163727], 'SD': [44.299782, -99.438828], 'TN': [35.771, -86.25],
        'TX': [31.106, -97.6475], 'UT': [39.32098, -111.094], 'VT': [44.26639, -72.580536],
        'VA': [37.54, -78.86], 'WA': [47.042418, -122.893077], 'WV': [38.349497, -81.633294],
        'WI': [44.268543, -89.616508], 'WY': [42.906847, -107.556081], 'DC': [38.904722, -77.016389]
    }
    return coordinates.get(state_code, None)

def calculate_growth_rate(data):
    """Calculate rating growth rate over time"""
    try:
        if len(data) < 2:
            return 0
        
        # Sort by date and calculate trend
        data_sorted = data.sort_values(['year', 'month'])
        monthly_avg = data_sorted.groupby(['year', 'month'])['avg_rating'].mean()
        
        if len(monthly_avg) < 2:
            return 0
        
        # Simple growth rate calculation
        first_half = monthly_avg.iloc[:len(monthly_avg)//2].mean()
        second_half = monthly_avg.iloc[len(monthly_avg)//2:].mean()
        
        if first_half > 0:
            growth_rate = ((second_half - first_half) / first_half) * 100
            return growth_rate
        
        return 0
    except:
        return 0