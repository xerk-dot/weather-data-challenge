import pytest
import numpy as np
import xarray as xr
from process import find_nearest_grid_point

def test_find_nearest_grid_point():
    # Create a simple 3x3 grid
    lats = np.array([[30.0, 30.0, 30.0],
                     [31.0, 31.0, 31.0],
                     [32.0, 32.0, 32.0]])
    lons = np.array([[-90.0, -89.0, -88.0],
                     [-90.0, -89.0, -88.0],
                     [-90.0, -89.0, -88.0]])
    
    # Create a mock dataset
    ds = xr.Dataset(
        data_vars={
            'latitude': (('y', 'x'), lats),
            'longitude': (('x', 'y'), lons.T)
        }
    )
    
    # Test case 1: Point exactly on a grid point
    lat, lon = 31.0, -89.0
    y_idx, x_idx = find_nearest_grid_point(lat, lon, ds)
    assert y_idx == 1  # Middle row
    assert x_idx == 1  # Middle column
    
    # Test case 2: Point between grid points
    lat, lon = 30.5, -89.5
    y_idx, x_idx = find_nearest_grid_point(lat, lon, ds)
    assert y_idx == 0  # First row (closer to 30.0)
    assert x_idx == 0  # First column (closer to -90.0)
    
    # Test case 3: Point outside grid
    lat, lon = 33.0, -87.0
    y_idx, x_idx = find_nearest_grid_point(lat, lon, ds)
    assert y_idx == 2  # Last row (closest to 32.0)
    assert x_idx == 2  # Last column (closest to -88.0)

def test_longitude_wrapping():
    # Create a grid with longitude wrapping
    lats = np.array([[30.0, 30.0, 30.0],
                     [31.0, 31.0, 31.0],
                     [32.0, 32.0, 32.0]])
    lons = np.array([[350.0, 351.0, 352.0],
                     [350.0, 351.0, 352.0],
                     [350.0, 351.0, 352.0]])
    
    # Create a mock dataset
    ds = xr.Dataset(
        data_vars={
            'latitude': (('y', 'x'), lats),
            'longitude': (('x', 'y'), lons.T)
        }
    )
    
    # Test case 1: Input in -180/180 convention
    lat, lon = 31.0, -10.0  # -10° is equivalent to 350°
    y_idx, x_idx = find_nearest_grid_point(lat, lon, ds)
    assert y_idx == 1  # Middle row
    assert x_idx == 0  # First column (350°)
    
    # Test case 2: Input in 0/360 convention
    lat, lon = 31.0, 351.0
    y_idx, x_idx = find_nearest_grid_point(lat, lon, ds)
    assert y_idx == 1  # Middle row
    assert x_idx == 1  # Middle column (351°)

def test_edge_cases():
    # Create a single point grid
    lats = np.array([[31.0]])
    lons = np.array([[-89.0]])
    
    # Create a mock dataset
    ds = xr.Dataset(
        data_vars={
            'latitude': (('y', 'x'), lats),
            'longitude': (('x', 'y'), lons.T)
        }
    )
    
    # Test with any point - should always return 0,0
    lat, lon = 35.0, -85.0
    y_idx, x_idx = find_nearest_grid_point(lat, lon, ds)
    assert y_idx == 0
    assert x_idx == 0 