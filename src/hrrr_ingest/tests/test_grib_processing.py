import pytest
import numpy as np
import xarray as xr
from datetime import datetime
from pathlib import Path
from process import process_grib_file

@pytest.fixture
def mock_grib_dataset(tmp_path):
    """Create a mock dataset that mimics a GRIB file."""
    # Create a simple grid
    lats = np.array([[30.0, 30.0, 30.0],
                     [31.0, 31.0, 31.0],
                     [32.0, 32.0, 32.0]])
    lons = np.array([[-90.0, -89.0, -88.0],
                     [-90.0, -89.0, -88.0],
                     [-90.0, -89.0, -88.0]])
    
    # Create temperature data
    temp_data = np.ones((3, 3)) * 293.15  # 20°C in Kelvin
    
    # Create the dataset
    ds = xr.Dataset(
        data_vars={
            'temperature_2m': (('y', 'x'), temp_data),
            'latitude': (('y', 'x'), lats),
            'longitude': (('x', 'y'), lons.T)
        }
    )
    
    # Save to netCDF file (which can be read like a GRIB)
    nc_file = tmp_path / "test.nc"
    ds.to_netcdf(nc_file)
    
    return nc_file

def test_process_grib_file(mock_grib_dataset, tmp_path):
    # Create a temporary points file
    points_file = tmp_path / "test_points.txt"
    points_file.write_text("31.0,-89.0\n32.0,-88.0")
    
    # Read points from file
    points = []
    with open(points_file) as f:
        for line in f:
            lat, lon = map(float, line.strip().split(','))
            points.append((lat, lon))
    
    # Test processing with mock dataset
    run_time = datetime(2025, 5, 1, 6, 0)
    results = process_grib_file(
        str(mock_grib_dataset),
        points,
        ['temperature_2m'],
        run_time
    )
    
    # Verify results
    assert len(results) == 2  # Two points
    for result in results:
        assert result['valid_time_utc'] == '2025-05-01T06:00:00'
        assert result['run_time_utc'] == '2025-05-01T06:00:00'
        assert result['variable'] == 'temperature_2m'
        assert result['value'] == 293.15
        assert result['source_s3'] == str(mock_grib_dataset)

def test_process_grib_file_invalid_variable(mock_grib_dataset, tmp_path):
    # Create a temporary points file
    points_file = tmp_path / "test_points.txt"
    points_file.write_text("31.0,-89.0")
    
    # Read points from file
    points = []
    with open(points_file) as f:
        for line in f:
            lat, lon = map(float, line.strip().split(','))
            points.append((lat, lon))
    
    # Test with invalid variable
    run_time = datetime(2025, 5, 1, 6, 0)
    with pytest.raises(KeyError):
        process_grib_file(
            str(mock_grib_dataset),
            points,
            ['invalid_variable'],
            run_time
        )

def test_process_grib_file_empty_points(mock_grib_dataset, tmp_path):
    # Create an empty points file
    points_file = tmp_path / "test_points.txt"
    points_file.write_text("")
    
    # Test with empty points file
    run_time = datetime(2025, 5, 1, 6, 0)
    results = process_grib_file(
        str(mock_grib_dataset),
        [],
        ['temperature_2m'],
        run_time
    )
    
    # Verify no results
    assert len(results) == 0 