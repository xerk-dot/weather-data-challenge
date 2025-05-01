"""Database operations for HRRR data storage."""

import duckdb
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any, Optional

from config import DB_PATH, TABLE_NAME

def init_database(conn: Optional[duckdb.DuckDBPyConnection] = None) -> None:
    """Initialize the DuckDB database with required schema."""
    if conn is None:
        conn = duckdb.connect(str(DB_PATH))
        should_close = True
    else:
        should_close = False
    
    conn.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
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
    
    if should_close:
        conn.close()

def insert_forecast_data(data: List[Dict[str, Any]], conn: Optional[duckdb.DuckDBPyConnection] = None) -> None:
    """Insert forecast data into database, handling duplicates."""
    if not data:
        return
        
    if conn is None:
        conn = duckdb.connect(str(DB_PATH))
        should_close = True
    else:
        should_close = False
    
    df = pd.DataFrame(data)
    
    # Use INSERT OR IGNORE to handle duplicates
    conn.execute(f"""
        INSERT OR IGNORE INTO {TABLE_NAME} 
        SELECT * FROM df
    """)
    
    if should_close:
        conn.close()

def check_existing_data(run_time: str, valid_time: str, 
                       latitude: float, longitude: float, 
                       variable: str,
                       conn: Optional[duckdb.DuckDBPyConnection] = None) -> bool:
    """Check if data for a specific point and time already exists."""
    if conn is None:
        conn = duckdb.connect(str(DB_PATH))
        should_close = True
    else:
        should_close = False
    
    result = conn.execute(f"""
        SELECT COUNT(*) 
        FROM {TABLE_NAME}
        WHERE run_time_utc = ? 
        AND valid_time_utc = ?
        AND latitude = ?
        AND longitude = ?
        AND variable = ?
    """, [run_time, valid_time, latitude, longitude, variable]).fetchone()
    
    if should_close:
        conn.close()
    
    return result[0] > 0 