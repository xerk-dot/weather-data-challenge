import click
from datetime import datetime
from pathlib import Path
from typing import Optional

@click.command()
@click.argument('points_file', type=click.Path(exists=True))
@click.option('--run-date', type=click.DateTime(formats=["%Y-%m-%d"]),
              help='Forecast run date (YYYY-MM-DD)')
@click.option('--variables', default=None,
              help='Comma separated list of variables to ingest')
@click.option('--num-hours', default=48, type=int,
              help='Number of forecast hours to ingest')
def main(points_file: str, run_date: Optional[datetime], 
         variables: Optional[str], num_hours: int):
    """Ingest HRRR forecast data for specified points."""
    # Convert variables string to list if provided
    var_list = variables.split(',') if variables else None
    
    # Read points file
    points = read_points_file(points_file)
    
    # Initialize database
    init_database()
    
    # Download and process HRRR data
    process_hrrr_data(points, run_date, var_list, num_hours)