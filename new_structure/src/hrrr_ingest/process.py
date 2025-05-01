"""HRRR GRIB2 data processing."""

import xarray as xr
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime, timedelta
import pandas as pd

from . import config
from .config import SUPPORTED_VARIABLES
from .database import check_existing_data

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
    
    # Group variables by their level types to minimize dataset openings
    level_groups = {
        'surface': [],
        'heightAboveGround': []
    }
    
    for var in variables:
        level_info = VARIABLE_LEVELS.get(var)
        if not level_info:
            logger.error(f"No level information for variable {var}")
            continue
        level_type = level_info['typeOfLevel']
        level_groups.setdefault(level_type, []).append((var, level_info))

    # Process each level type group
    for level_type, var_info_list in level_groups.items():
        if not var_info_list:
            continue
            
        try:
            # For heightAboveGround, process each level separately
            if level_type == "heightAboveGround":
                # Group variables by their level
                level_var_groups = {}
                for var, info in var_info_list:
                    level = info.get('level')
                    if level is not None:
                        level_var_groups.setdefault(level, []).append((var, info))
                
                # Process each level group separately
                for level, level_vars in level_var_groups.items():
                    results.extend(process_level_group(grib_file, points, level_vars, run_time, level_type, level))
            else:
                # Process surface variables together
                results.extend(process_level_group(grib_file, points, var_info_list, run_time, level_type))
            
        except Exception as e:
            logger.error(f"Error processing {level_type} variables: {str(e)}")
            raise

    return results

def process_level_group(grib_file: str, points: List[Tuple[float, float]], 
                       var_info_list: List[Tuple[str, dict]], run_time: datetime,
                       level_type: str, level: int = None) -> List[Dict[str, Any]]:
    """Process a group of variables with the same level type and level."""
    results = []
    
    # Prepare filter kwargs
    filter_kwargs = {
        "typeOfLevel": level_type,
        "stepType": "instant"
    }
    
    # For heightAboveGround variables, we MUST specify the exact level
    if level_type == "heightAboveGround":
        if level is None:
            logger.error("Level must be specified for heightAboveGround variables")
            return []
        filter_kwargs["level"] = level
        
    try:
        # Open dataset with strict filtering
        ds = xr.open_dataset(
            grib_file,
            engine="cfgrib",
            backend_kwargs={
                "filter_by_keys": filter_kwargs,
                "indexpath": "",
                "read_keys": ["paramId", "shortName", "typeOfLevel", "level", "stepType"]
            }
        )
        
        logger.info(f"Available variables in dataset with filter {filter_kwargs}: {list(ds.variables.keys())}")
        
        # Process each variable in this group
        for var_name, var_info in var_info_list:
            grib_var = SUPPORTED_VARIABLES.get(var_name)
            if not grib_var:
                logger.error(f"No GRIB2 name mapping for variable {var_name}")
                continue
                
            if grib_var not in ds.variables:
                logger.error(f"Variable {var_name} ({grib_var}) not found in dataset")
                continue
                
            data_array = ds[grib_var]
            data_values = data_array.values
            
            for lat, lon in points:
                try:
                    y_idx, x_idx = find_nearest_grid_point(lat, lon, ds)
                    value = float(data_values[y_idx, x_idx])
                    
                    # Get the valid time and step hours
                    valid_time = pd.Timestamp(ds.valid_time.values).isoformat()
                    step_hours = int(ds.step.values / np.timedelta64(1, 'h'))
                    
                    result = {
                        "valid_time_utc": valid_time,
                        "run_time_utc": run_time.isoformat(),
                        "latitude": lat,
                        "longitude": lon,
                        "variable": var_name,
                        "value": value,
                        "source_s3": f"s3://noaa-hrrr-bdp-pds/hrrr.{run_time.strftime('%Y%m%d')}/conus/hrrr.t{run_time.hour:02d}z.wrfsfcf{step_hours:02d}.grib2"
                    }
                    
                    if not check_existing_data(
                        run_time=run_time.isoformat(),
                        valid_time=valid_time,
                        latitude=lat,
                        longitude=lon,
                        variable=var_name
                    ):
                        results.append(result)
                        
                except Exception as e:
                    logger.error(f"Error processing point ({lat}, {lon}) for variable {var_name}: {str(e)}")
                    continue
                    
    except Exception as e:
        logger.error(f"Error opening dataset with filter {filter_kwargs}: {str(e)}")
        raise
                
    return results 