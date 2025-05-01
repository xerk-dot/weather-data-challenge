import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from cli import main
from datetime import datetime, timedelta
from typing import List, Tuple
import logging
from io import StringIO

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def test_points_file(tmp_path):
    points_file = tmp_path / "test_points.txt"
    points_file.write_text("31.0,-89.0\n32.0,-88.0")
    return str(points_file)

@pytest.fixture
def mock_download_and_process():
    with patch('cli.check_file_exists') as mock_check, \
         patch('cli.download_grib_file') as mock_download, \
         patch('cli.process_grib_file') as mock_process, \
         patch('cli.insert_forecast_data') as mock_insert:
        
        # Mock file existence check to return True
        mock_check.return_value = True
        
        # Mock download to return a temporary file
        mock_download.return_value = MagicMock()
        mock_download.return_value.unlink = MagicMock()
        
        # Mock process to return some results
        mock_process.return_value = [{
            'valid_time_utc': '2025-05-01T06:00:00',
            'run_time_utc': '2025-05-01T06:00:00',
            'latitude': 31.0,
            'longitude': -89.0,
            'variable': 'temperature_2m',
            'value': 293.15,
            'source_s3': 's3://test-bucket/test.grib2'
        }]
        
        yield mock_check, mock_download, mock_process, mock_insert

@pytest.fixture(autouse=True)
def capture_logs():
    # Capture logs in a StringIO
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    
    yield log_stream
    
    # Clean up
    root_logger.removeHandler(handler)

def test_cli_help(runner):
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'Ingest HRRR forecast data' in result.output

def test_cli_invalid_points_file(runner):
    result = runner.invoke(main, ['nonexistent.txt'])
    assert result.exit_code != 0
    assert 'Error' in result.output

def test_cli_invalid_variables(runner, test_points_file):
    result = runner.invoke(main, [
        test_points_file,
        '--variables', 'invalid_variable'
    ])
    assert result.exit_code != 0
    assert 'Error' in result.output

def test_cli_invalid_num_hours(runner, test_points_file):
    result = runner.invoke(main, [
        test_points_file,
        '--num-hours', '49'  # More than allowed 48 hours
    ])
    assert result.exit_code != 0
    assert 'Error' in result.output

def test_cli_valid_arguments(runner, test_points_file, mock_download_and_process, capture_logs):
    result = runner.invoke(main, [
        test_points_file,
        '--variables', 'temperature_2m',
        '--num-hours', '1'
    ])
    assert result.exit_code == 0
    assert 'Processing' in capture_logs.getvalue()

def test_cli_default_arguments(runner, test_points_file, mock_download_and_process, capture_logs):
    result = runner.invoke(main, [test_points_file])
    assert result.exit_code == 0
    assert 'Processing' in capture_logs.getvalue()

def test_cli_invalid_run_date(runner, test_points_file):
    result = runner.invoke(main, [
        test_points_file,
        '--run-date', 'invalid-date'
    ])
    assert result.exit_code != 0
    assert 'Error' in result.output

def test_cli_future_run_date(runner, test_points_file):
    future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    result = runner.invoke(main, [
        test_points_file,
        '--run-date', future_date
    ])
    assert result.exit_code != 0
    assert 'Error' in result.output

def test_cli_process_grib_file(runner, test_points_file, mock_download_and_process):
    mock_check, mock_download, mock_process, mock_insert = mock_download_and_process
    
    # Mock the process_grib_file function to return a mock dataset
    mock_process.return_value = [{
        'valid_time_utc': '2025-05-01T06:00:00',
        'run_time_utc': '2025-05-01T06:00:00',
        'latitude': 31.0,
        'longitude': -89.0,
        'variable': 'temperature_2m',
        'value': 293.15,
        'source_s3': 's3://test-bucket/test.grib2'
    }]
    
    result = runner.invoke(main, [
        test_points_file,
        '--variables', 'temperature_2m',
        '--num-hours', '1'
    ])
    
    assert result.exit_code == 0
    assert mock_check.called
    assert mock_download.called
    assert mock_process.called
    assert mock_insert.called 