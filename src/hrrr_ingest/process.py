"""HRRR GRIB2 data processing."""

import xarray as xr
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime, timedelta
import pandas as pd

from config import SUPPORTED_VARIABLES
from database import check_existing_data

logger = logging.getLogger(__name__)

# Map variables to their level types and step types
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

def find_nearest_grid_point(lat: float, lon: float, ds: xr.Dataset) -> Tuple[int, int]:
    """
    Find the nearest grid point to the given latitude and longitude coordinates.
    
    Args:
        lat: Target latitude
        lon: Target longitude (-180 to 180)
        ds: xarray Dataset containing the grid
        
    Returns:
        Tuple of (y_idx, x_idx) for the nearest grid point
    """
    # Convert coordinates to numpy arrays
    lats = ds.latitude.values
    lons = ds.longitude.values
    
    # Convert input longitude from -180/180 to 0/360 convention if needed
    lon_360 = lon % 360 if lon < 0 else lon
    
    # Calculate distances using numpy operations
    lat_diff = np.abs(lats - lat)
    
    # Handle longitude wrapping in 0/360 convention
    lon_diff = np.minimum(
        np.abs(lons - lon_360),
        np.abs((lons - lon_360 + 360) % 360)
    )
    
    # Calculate total distance (squared)
    total_dist = lat_diff**2 + lon_diff**2
    
    # Find indices of minimum distance
    min_idx = np.unravel_index(np.argmin(total_dist), total_dist.shape)
    
    return int(min_idx[0]), int(min_idx[1])

def process_grib_file(grib_file: str, points: List[Tuple[float, float]], variables: List[str], run_time: datetime) -> List[Dict[str, Any]]:
    """Process a GRIB2 file and extract data for specified points and variables."""
    results = []
    try:
        # Open the dataset with the correct level type for temperature_2m
        ds = xr.open_dataset(
            grib_file,
            engine="cfgrib",
            backend_kwargs={
                "filter_by_keys": {
                    "typeOfLevel": "heightAboveGround",
                    "level": 2
                }
            }
        )
        
        logger.info(f"Available variables in dataset: {list(ds.variables.keys())}")
        logger.info(f"Dataset info: {ds.attrs}")
        
        # Map our variable names to GRIB2 variable names
        var_mapping = {
            "temperature_2m": "t2m",
            "dewpoint_2m": "d2m",
            "relative_humidity_2m": "r2",
            "specific_humidity_2m": "sh2",
            "potential_temperature_2m": "pt"
        }
        
        for var in variables:
            # Get the GRIB2 variable name
            grib_var = var_mapping.get(var)
            if not grib_var:
                logger.error(f"Variable {var} not found in mapping")
                continue
                
            if grib_var not in ds.variables:
                logger.error(f"Variable {grib_var} not found in dataset")
                continue
                
            logger.info(f"Selected variable name: {grib_var}")
            logger.info(f"Variable {grib_var} data shape: {ds[grib_var].shape}")
            logger.info(f"Variable {grib_var} attributes: {ds[grib_var].attrs}")
            logger.info(f"Variable {grib_var} dimensions: {ds[grib_var].dims}")
            logger.info(f"Variable {grib_var} coordinates: {ds[grib_var].coords}")
            
            # Get the data array with all dimensions
            data_array = ds[grib_var]
            
            # Convert to numpy array for performance
            data_values = data_array.values
            logger.info(f"Data array shape: {data_values.shape}")
            logger.info(f"Data array type: {data_values.dtype}")
            
            for lat, lon in points:
                try:
                    logger.info(f"Attempting to access data at coordinates ({lat}, {lon})")
                    
                    # Find the nearest grid point
                    y_idx, x_idx = find_nearest_grid_point(lat, lon, ds)
                    logger.info(f"Nearest grid point indices: ({y_idx}, {x_idx})")
                    
                    # Get the value at the nearest grid point using numpy array
                    value = float(data_values[y_idx, x_idx])
                    logger.info(f"Extracted value: {value}")
                    
                    # Get the actual coordinates of the grid point
                    grid_lat = ds.latitude.values[y_idx, x_idx]
                    grid_lon = ds.longitude.values[y_idx, x_idx]
                    logger.info(f"Grid point coordinates: ({grid_lat}, {grid_lon})")
                    
                    # Get the valid time and convert to ISO format string
                    valid_time = pd.Timestamp(ds.valid_time.values).isoformat()
                    logger.info(f"Valid time: {valid_time}")
                    
                    # Get the step hours as an integer
                    step_hours = int(ds.step.values / np.timedelta64(1, 'h'))
                    logger.info(f"Step hours: {step_hours}")
                    
                    # Create the result dictionary
                    result = {
                        "valid_time_utc": valid_time,
                        "run_time_utc": run_time.isoformat(),
                        "latitude": lat,
                        "longitude": lon,
                        "variable": var,
                        "value": value,
                        "source_s3": f"s3://noaa-hrrr-bdp-pds/hrrr.{run_time.strftime('%Y%m%d')}/conus/hrrr.t{run_time.hour:02d}z.wrfsfcf{step_hours:02d}.grib2"
                    }
                    
                    # Check if we already have this data
                    if not check_existing_data(
                        run_time=run_time.isoformat(),
                        valid_time=valid_time,
                        latitude=lat,
                        longitude=lon,
                        variable=var
                    ):
                        results.append(result)
                        logger.info(f"Added result for point ({lat}, {lon}) at time {valid_time}")
                    else:
                        logger.info(f"Data already exists for point ({lat}, {lon}) at time {valid_time}")
                    
                except Exception as e:
                    logger.error(f"Error processing point ({lat}, {lon}) for variable {var}: {str(e)}")
                    raise  # Re-raise the exception to handle it at a higher level
                    
    except Exception as e:
        logger.error(f"Error processing GRIB file: {str(e)}")
        raise
        
    return results 