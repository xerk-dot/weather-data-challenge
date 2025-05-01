import duckdb
from pathlib import Path

def init_database():
    """Initialize the DuckDB database with required schema."""
    conn = duckdb.connect('data.db')
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS hrrr_forecasts (
        valid_time_utc TIMESTAMP,
        run_time_utc TIMESTAMP,
        latitude FLOAT,
        longitude FLOAT,
        variable VARCHAR,
        value FLOAT,
        source_s3 VARCHAR,
        PRIMARY KEY (valid_time_utc, run_time_utc, latitude, longitude, variable)
    )
    """)
    conn.close()

def insert_forecast_data(data_df):
    """Insert forecast data into database, handling duplicates."""
    conn = duckdb.connect('data.db')
    # Use INSERT OR IGNORE to handle duplicates
    conn.execute("""
        INSERT OR IGNORE INTO hrrr_forecasts 
        SELECT * FROM data_df
    """)
    conn.close()