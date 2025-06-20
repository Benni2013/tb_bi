import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from etl_functions import run_complete_etl, create_engine_connection
import time

def main():
    st.set_page_config(
        page_title="🍽️ Restaurant ETL Dashboard",
        page_icon="🍽️",
        layout="wide"
    )
    
    st.title("🍽️ Web ETL Application - Restaurant Reviews")
    st.markdown("---")
    
    # File uploader
    st.subheader("📁 Upload Dataset")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Display basic info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Total Columns", len(df.columns))
            with col3:
                st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
            
            st.subheader("📊 Dataset Preview (Top 5 rows)")
            st.dataframe(df.head(), use_container_width=True)
            
            # Show column info
            with st.expander("📋 Column Information"):
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Data Type': df.dtypes,
                    'Non-Null Count': df.count(),
                    'Sample Value': [str(df[col].iloc[0]) if len(df) > 0 else 'N/A' for col in df.columns]
                })
                st.dataframe(col_info)
            
            st.markdown("---")
            
            # ETL Configuration
            st.subheader("⚙️ ETL Configuration")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                retain_data = st.checkbox(
                    "🔄 Pertahankan data yang ada di Data Warehouse?", 
                    value=False,
                    help="Jika dicentang, data lama tidak akan dihapus. Jika tidak, semua data lama akan dihapus terlebih dahulu."
                )
            
            with col2:
                if retain_data:
                    st.info("📝 Mode: Append Data")
                else:
                    st.warning("🔄 Mode: Replace All Data")
            
            # ETL Execution
            st.markdown("---")
            if st.button("🚀 Lakukan ETL", type="primary", use_container_width=True):
                try:
                    # Create database engine
                    engine = create_engine_connection()
                    
                    # Test connection first
                    with st.spinner("🔌 Testing database connection..."):
                        with engine.connect() as conn:
                            conn.execute(text("SELECT 1"))
                        st.success("✅ Database connection successful!")
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # ETL Steps
                    steps = [
                        ("📅 ETL dim_time", 12.5),
                        ("🌍 ETL dim_location", 25.0),
                        ("🏪 ETL dim_restaurant", 37.5),
                        ("📂 ETL dim_category", 50.0),
                        ("🔤 ETL dim_keywords", 62.5),
                        ("😊 ETL dim_sentiment", 75.0),
                        ("🔗 ETL bridge_sentiment_keywords", 87.5),
                        ("📊 ETL fact_restaurant_reviews", 100.0)
                    ]
                    
                    # Show step-by-step progress
                    step_container = st.container()
                    with step_container:
                        st.subheader("📋 ETL Progress")
                        step_placeholders = []
                        for i, (step_name, _) in enumerate(steps):
                            step_placeholders.append(st.empty())
                    
                    # Run ETL with progress updates
                    with st.spinner("🔄 Running ETL process..."):
                        # Simulate step updates
                        for i, (step_name, progress) in enumerate(steps):
                            status_text.text(f"Processing: {step_name}")
                            step_placeholders[i].info(f"⏳ {step_name}")
                            progress_bar.progress(int(progress))
                            time.sleep(0.5)  # Simulate processing time
                            
                        # Run actual ETL
                        etl_summary = run_complete_etl(df, engine, retain_data)
                        
                        # Update step status to completed
                        for i, (step_name, _) in enumerate(steps):
                            step_placeholders[i].success(f"✅ {step_name}")
                    
                    # Show results
                    if etl_summary:
                        st.success("🎉 ETL Process Completed Successfully!")
                        
                        # Summary metrics
                        st.subheader("📈 ETL Summary")
                        
                        # Create metrics in columns
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("⏰ Time Records", etl_summary.get('dim_time', 0))
                            st.metric("🌍 Location Records", etl_summary.get('dim_location', 0))
                        with col2:
                            st.metric("🏪 Restaurant Records", etl_summary.get('dim_restaurant', 0))
                            st.metric("📂 Category Records", etl_summary.get('dim_category', 0))
                        with col3:
                            st.metric("🔤 Keywords", etl_summary.get('dim_keywords', 0))
                            st.metric("😊 Sentiments", etl_summary.get('dim_sentiment', 0))
                        with col4:
                            st.metric("🔗 Bridge Records", etl_summary.get('bridge_sentiment_keywords', 0))
                            st.metric("📊 Fact Records", etl_summary.get('fact_restaurant_reviews', 0))
                        
                        # Detailed summary table
                        with st.expander("📋 Detailed Summary"):
                            summary_df = pd.DataFrame([
                                {"Table": "dim_time", "Records Loaded": etl_summary.get('dim_time', 0), "Description": "Time dimension data"},
                                {"Table": "dim_location", "Records Loaded": etl_summary.get('dim_location', 0), "Description": "Location dimension data"},
                                {"Table": "dim_restaurant", "Records Loaded": etl_summary.get('dim_restaurant', 0), "Description": "Restaurant dimension data"},
                                {"Table": "dim_category", "Records Loaded": etl_summary.get('dim_category', 0), "Description": "Category dimension data"},
                                {"Table": "dim_keywords", "Records Loaded": etl_summary.get('dim_keywords', 0), "Description": "Keywords dimension data"},
                                {"Table": "dim_sentiment", "Records Loaded": etl_summary.get('dim_sentiment', 0), "Description": "Sentiment analysis data"},
                                {"Table": "bridge_sentiment_keywords", "Records Loaded": etl_summary.get('bridge_sentiment_keywords', 0), "Description": "Sentiment-Keywords relationship"},
                                {"Table": "fact_restaurant_reviews", "Records Loaded": etl_summary.get('fact_restaurant_reviews', 0), "Description": "Main fact table"}
                            ])
                            st.dataframe(summary_df, use_container_width=True)
                        
                        # Success message with balloons
                        st.balloons()
                        
                    else:
                        st.error("❌ ETL Process Failed!")
                        
                except Exception as e:
                    st.error(f"❌ Error during ETL process: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
    else:
        st.info("👆 Please upload a CSV file to begin the ETL process")
        
        # Show example of expected CSV format
        with st.expander("📋 Expected CSV Format"):
            st.write("The CSV file should contain the following columns:")
            expected_columns = [
                "ID", "Time_GMT", "Phone", "Organization", "OLF", "Rating", 
                "NumberReview", "Category", "Country", "CountryCode", "State", 
                "City", "Street", "Building", "ReviewText"
            ]
            st.code(", ".join(expected_columns))

if __name__ == "__main__":
    main()