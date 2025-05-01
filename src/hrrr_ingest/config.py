"""Configuration and constants for HRRR data ingestion."""

from pathlib import Path
from typing import List

# AWS S3 bucket for HRRR data
HRRR_BUCKET = "noaa-hrrr-bdp-pds"
HRRR_PREFIX = "hrrr"

# Supported variables and their GRIB2 identifiers
SUPPORTED_VARIABLES = {
    "surface_pressure": "sp",
    "surface_roughness": "sr",
    "visible_beam_downward_solar_flux": "vbdsf",
    "visible_diffuse_downward_solar_flux": "vddsf",
    "temperature_2m": "t2m",
    "dewpoint_2m": "d2m",
    "relative_humidity_2m": "r2",
    "u_component_wind_10m": "u10",
    "v_component_wind_10m": "v10",
    "u_component_wind_80m": "u",  # At 80m level
    "v_component_wind_80m": "v",  # At 80m level
}

# Default forecast run time (06z)
DEFAULT_RUN_HOUR = 6

# Database configuration
DB_PATH = Path("data.db")
TABLE_NAME = "hrrr_forecasts"

def get_s3_path(date: str, forecast_hour: int) -> str:
    """Generate S3 path for HRRR data file."""
    return f"s3://{HRRR_BUCKET}/{HRRR_PREFIX}.{date}/conus/hrrr.t{forecast_hour:02d}z.wrfsfcf00.grib2" 