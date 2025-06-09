# Streamlit ETL Application

This project is a Streamlit web application designed to facilitate the ETL (Extract, Transform, Load) process for restaurant review data. Users can upload a CSV file containing restaurant reviews, and the application will process the data, load it into a PostgreSQL database, and provide a summary of the ETL process.

## Project Structure

```
streamlit-etl-app
├── web_ETL.py            # Streamlit web application for the ETL process
├── etl_functions.py      # ETL functions for processing the data
├── database_config.py    # Database connection configuration
├── requirements.txt      # List of dependencies required for the project
└── README.md             # Documentation for the project
```

## Requirements

To run this application, you need to have the following Python packages installed:

- Streamlit
- pandas
- SQLAlchemy
- psycopg2
- nltk
- textblob

You can install the required packages using pip:

```
pip install -r requirements.txt
```

## Setup Instructions

1. **Clone the Repository**: 
   Clone this repository to your local machine.

   ```
   git clone <repository-url>
   cd streamlit-etl-app
   ```

2. **Install Dependencies**: 
   Install the required Python packages using the command mentioned above.

3. **Database Configuration**: 
   Update the `database_config.py` file with your PostgreSQL database connection details.

4. **Run the Application**: 
   Start the Streamlit application by running the following command in your terminal:

   ```
   streamlit run web_ETL.py
   ```

5. **Upload CSV File**: 
   Once the application is running, open it in your web browser. You can upload a CSV file containing restaurant reviews.

6. **Execute ETL Process**: 
   After uploading the file, you can execute the ETL process. You have the option to retain existing data in the Data Warehouse.

7. **View Results**: 
   The application will display the top 5 rows of the dataset and provide a step-by-step summary of the ETL process for each table, concluding with a success message.

## Dataset

The application is designed to work with a CSV file containing restaurant reviews. The expected columns in the dataset include:

- Time_GMT
- Phone
- Organization
- OLF
- Rating
- NumberReview
- Category
- Country
- CountryCode
- State
- City
- Street
- Building
- ReviewText

## Conclusion

This Streamlit ETL application provides a user-friendly interface for processing restaurant review data and loading it into a PostgreSQL database. It simplifies the ETL process and allows users to visualize the data transformation steps.