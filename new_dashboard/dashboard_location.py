import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from shared_utils import load_data, load_css
from datetime import datetime, date

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
                    <h4>🏪 Total Restaurants</h4>
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
        
        # ENHANCED VISUALIZATIONS
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
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
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("📈 Review Volume Trend")
            
            monthly_reviews = filtered_data.groupby(['year', 'month']).agg({
                'total_reviews': 'sum'
            }).reset_index()
            
            if not monthly_reviews.empty:
                monthly_reviews['date'] = pd.to_datetime(monthly_reviews[['year', 'month']].assign(day=1))
                
                fig = px.bar(
                    monthly_reviews,
                    x='date',
                    y='total_reviews',
                    title="Monthly Review Volume",
                    labels={'date': 'Date', 'total_reviews': 'Number of Reviews'},
                    color='total_reviews',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Rating Trend Analysis
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
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
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("🏆 Competitive Landscape Analysis")
            
            org_performance = filtered_data.groupby('organization_name').agg({
                'avg_rating': 'mean',
                'total_reviews': 'sum',
                'city': 'nunique'
            }).reset_index().rename(columns={'city': 'locations_count'})
            
            # Sort by performance score (weighted rating and volume)
            org_performance['performance_score'] = (
                org_performance['avg_rating'] * 0.7 + 
                (org_performance['total_reviews'] / org_performance['total_reviews'].max()) * 0.3
            )
            org_performance = org_performance.sort_values('performance_score', ascending=True)
            
            fig = px.bar(
                org_performance.tail(10),
                x='performance_score',
                y='organization_name',
                orientation='h',
                title="Top 10 Organizations by Performance Score",
                labels={'performance_score': 'Performance Score (Rating + Volume)', 'organization_name': 'Brand'},
                color='avg_rating',
                color_continuous_scale='RdYlGn',
                hover_data=['avg_rating', 'total_reviews', 'locations_count']
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Top Organizations Trend
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 Top Organizations Rating Evolution")
        
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
            title="Rating Evolution for Market Leaders",
            labels={'date': 'Date', 'avg_rating': 'Average Rating'},
            markers=True
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action Items Section
        st.markdown("### 🎯 Recommended Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔴 Diperlukan Tindakan Segera:**
            - Meninjau operasi di lokasi yang berkinerja buruk
            - Menerapkan program pelatihan layanan pelanggan
            - Menangani keluhan khusus di area dengan peringkat rendah
            - Mempertimbangkan audit operasional untuk lokasi-lokasi yang bermasalah
            """)
        
        with col2:
            st.markdown("""
            **🟢 Peluang Pertumbuhan:**
            - Meniru praktik terbaik dari para pemain terbaik
            - Meningkatkan pemasaran di area dengan peringkat tinggi dan volume rendah
            - Memperluas model lokasi yang berhasil
            - Memantau strategi pesaing di pasar-pasar utama
            """)
        
    else:
        st.warning("⚠️ No data available for location performance analysis")

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