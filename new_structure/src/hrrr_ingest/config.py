"""Configuration and constants for HRRR data ingestion."""

from pathlib import Path
from typing import List

# AWS S3 bucket for HRRR data
HRRR_BUCKET = "noaa-hrrr-bdp-pds"
HRRR_PREFIX = "hrrr"

# Supported variables and their GRIB2 identifiers
SUPPORTED_VARIABLES = {
    "surface_pressure": "sp",  # Surface pressure
    "surface_roughness": "fsr",  # Surface roughness length
    "visible_beam_downward_solar_flux": "vbdsf",  # Visible beam downward solar flux
    "visible_diffuse_downward_solar_flux": "vddsf",  # Visible diffuse downward solar flux
    "temperature_2m": "t2m",  # Temperature at 2m
    "dewpoint_2m": "d2m",  # Dewpoint temperature at 2m
    "relative_humidity_2m": "r2",  # Relative humidity at 2m
    "u_component_wind_10m": "u10",  # U-component of wind at 10m
    "v_component_wind_10m": "v10",  # V-component of wind at 10m
    "u_component_wind_80m": "u",  # U-component of wind at 80m
    "v_component_wind_80m": "v",  # V-component of wind at 80m
}

# Variable level configurations
VARIABLE_LEVELS = {
    'surface_pressure': {'typeOfLevel': 'surface', 'stepType': 'instant'},
    'surface_roughness': {'typeOfLevel': 'surface', 'stepType': 'instant'},
    'visible_beam_downward_solar_flux': {'typeOfLevel': 'surface', 'stepType': 'instant'},
    'visible_diffuse_downward_solar_flux': {'typeOfLevel': 'surface', 'stepType': 'instant'},
    'temperature_2m': {'typeOfLevel': 'heightAboveGround', 'stepType': 'instant', 'level': 2},
    'dewpoint_2m': {'typeOfLevel': 'heightAboveGround', 'stepType': 'instant', 'level': 2},
    'relative_humidity_2m': {'typeOfLevel': 'heightAboveGround', 'stepType': 'instant', 'level': 2},
    'u_component_wind_10m': {'typeOfLevel': 'heightAboveGround', 'stepType': 'instant', 'level': 10},
    'v_component_wind_10m': {'typeOfLevel': 'heightAboveGround', 'stepType': 'instant', 'level': 10},
    'u_component_wind_80m': {'typeOfLevel': 'heightAboveGround', 'stepType': 'instant', 'level': 80},
    'v_component_wind_80m': {'typeOfLevel': 'heightAboveGround', 'stepType': 'instant', 'level': 80},
}

# Default forecast run time (06z)
DEFAULT_RUN_HOUR = 6

# Database configuration
DB_PATH = Path("data.db")
TABLE_NAME = "hrrr_forecasts"

def get_s3_path(date: str, forecast_hour: int) -> str:
    """Generate S3 path for HRRR data file."""
    return f"s3://{HRRR_BUCKET}/hrrr.{date}/conus/hrrr.t06z.wrfsfcf{forecast_hour:02d}.grib2" 