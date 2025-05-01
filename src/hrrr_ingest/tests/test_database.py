import pytest
import duckdb
from datetime import datetime
from pathlib import Path
import os

from database import init_database, insert_forecast_data, check_existing_data

@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Create a temporary test database."""
    # Create a temporary database file
    db_path = tmp_path / "test.db"
    
    # Override DB_PATH in config
    monkeypatch.setenv("DB_PATH", str(db_path))
    
    # Initialize the database
    conn = duckdb.connect(str(db_path))
    init_database()
    
    yield conn
    
    # Clean up
    conn.close()
    if db_path.exists():
        os.unlink(str(db_path))

def test_check_existing_data(test_db):
    # Test data
    test_data = [{
        'valid_time_utc': '2025-05-01T06:00:00',
        'run_time_utc': '2025-05-01T06:00:00',
        'latitude': 31.0,
        'longitude': -89.0,
        'variable': 'temperature_2m',
        'value': 293.15,
        'source_s3': 's3://test-bucket/test.grib2'
    }]
    
    # Insert data
    insert_forecast_data(test_data)
    
    # Check if data exists
    exists = check_existing_data(
        datetime.fromisoformat('2025-05-01T06:00:00'),
        datetime.fromisoformat('2025-05-01T06:00:00'),
        31.0,
        -89.0,
        'temperature_2m'
    )
    assert exists

def test_insert_data(test_db):
    # Test data
    test_data = [{
        'valid_time_utc': '2025-05-01T06:00:00',
        'run_time_utc': '2025-05-01T06:00:00',
        'latitude': 31.0,
        'longitude': -89.0,
        'variable': 'temperature_2m',
        'value': 293.15,
        'source_s3': 's3://test-bucket/test.grib2'
    }]
    
    # Insert data
    insert_forecast_data(test_data)
    
    # Verify data was inserted
    result = test_db.execute("""
        SELECT COUNT(*)
        FROM hrrr_forecasts
        WHERE variable = 'temperature_2m'
    """).fetchone()
    assert result[0] == 1

def test_insert_duplicate_data(test_db):
    # Test data
    test_data = [{
        'valid_time_utc': '2025-05-01T06:00:00',
        'run_time_utc': '2025-05-01T06:00:00',
        'latitude': 31.0,
        'longitude': -89.0,
        'variable': 'temperature_2m',
        'value': 293.15,
        'source_s3': 's3://test-bucket/test.grib2'
    }]
    
    # Insert data twice
    insert_forecast_data(test_data)
    insert_forecast_data(test_data)  # Should not create duplicate
    
    # Verify only one record exists
    result = test_db.execute("""
        SELECT COUNT(*)
        FROM hrrr_forecasts
        WHERE variable = 'temperature_2m'
    """).fetchone()
    assert result[0] == 1

def test_insert_multiple_variables(test_db):
    # Test data with multiple variables
    test_data = [
        {
            'valid_time_utc': '2025-05-01T06:00:00',
            'run_time_utc': '2025-05-01T06:00:00',
            'latitude': 31.0,
            'longitude': -89.0,
            'variable': 'temperature_2m',
            'value': 293.15,
            'source_s3': 's3://test-bucket/test.grib2'
        },
        {
            'valid_time_utc': '2025-05-01T06:00:00',
            'run_time_utc': '2025-05-01T06:00:00',
            'latitude': 31.0,
            'longitude': -89.0,
            'variable': 'surface_pressure',
            'value': 1013.25,
            'source_s3': 's3://test-bucket/test.grib2'
        }
    ]
    
    # Insert data
    insert_forecast_data(test_data)
    
    # Verify both records exist
    result = test_db.execute("""
        SELECT COUNT(*)
        FROM hrrr_forecasts
    """).fetchone()
    assert result[0] == 2 