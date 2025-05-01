"""CLI interface for HRRR data ingestion."""

import click
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple
import sys
from io import StringIO

from .config import SUPPORTED_VARIABLES, DEFAULT_RUN_HOUR
from .database import init_database, insert_forecast_data
from .download import download_grib_file, check_file_exists
from .process import process_grib_file

def setup_logging(stream=None):
    """Configure logging with optional custom stream."""
    handlers = [logging.StreamHandler(stream or sys.stdout)]
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    return logging.getLogger(__name__)

def read_points_file(file_path: str) -> List[Tuple[float, float]]:
    """Read points from file."""
    points = []
    with open(file_path, 'r') as f:
        for line in f:
            lat, lon = map(float, line.strip().split(','))
            points.append((lat, lon))
    return points

@click.command()
@click.argument('points_file', type=click.Path(exists=True))
@click.option('--run-date', type=click.DateTime(formats=["%Y-%m-%d"]),
              help='Forecast run date (YYYY-MM-DD)')
@click.option('--variables', default=None,
              help='Comma separated list of variables to ingest')
@click.option('--num-hours', default=48, type=int,
              help='Number of forecast hours to ingest (max 48)')
def main(points_file: str, run_date: datetime, 
         variables: str, num_hours: int):
    """Ingest HRRR forecast data for specified points."""
    # Set up logging
    logger = setup_logging()
    
    # Validate num_hours
    if num_hours < 1 or num_hours > 48:
        raise click.BadParameter("Number of hours must be between 1 and 48")
    
    # Convert variables string to list if provided
    var_list = variables.split(',') if variables else list(SUPPORTED_VARIABLES.keys())
    
    # Validate variables
    invalid_vars = [v for v in var_list if v not in SUPPORTED_VARIABLES]
    if invalid_vars:
        raise click.BadParameter(f"Invalid variables: {', '.join(invalid_vars)}")
    
    # Read points file
    points = read_points_file(points_file)
    
    # Initialize database
    init_database()
    
    # Set run date to today if not provided
    if not run_date:
        run_date = datetime.now()
    
    # Set run time to 06z
    run_time = run_date.replace(hour=DEFAULT_RUN_HOUR, minute=0, second=0, microsecond=0)
    
    # Process each forecast hour
    for hour in range(num_hours):
        forecast_hour = hour
        date_str = run_time.strftime('%Y%m%d')
        
        # Check if file exists
        if not check_file_exists(date_str, forecast_hour):
            logger.warning(f"No data available for {date_str} hour {forecast_hour}")
            continue
        
        # Download GRIB file
        grib_file = download_grib_file(date_str, forecast_hour)
        if not grib_file:
            logger.error(f"Failed to download GRIB file for {date_str} hour {forecast_hour}")
            continue
        
        try:
            # Process GRIB file
            logger.info(f"Processing forecast for {date_str} hour {forecast_hour}")
            results = process_grib_file(grib_file, points, var_list, run_time)
            
            # Insert results into database
            if results:
                insert_forecast_data(results)
                logger.info(f"Successfully processed {len(results)} records for hour {forecast_hour}")
            else:
                logger.warning(f"No new data to insert for hour {forecast_hour}")
                
        finally:
            # Clean up temporary file
            grib_file.unlink()

if __name__ == '__main__':
    main() 