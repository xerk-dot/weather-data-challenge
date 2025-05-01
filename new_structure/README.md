# HRRR Data Ingest Tool

A CLI tool for ingesting HRRR (High-Resolution Rapid Refresh) weather forecast data from NOAA's S3 bucket.

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd weather-data-challenge/new_structure
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

## Usage

The package installs a command-line tool called `hrrr_ingest`. To use it:

1. Make sure you're in the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

2. Create a points file (e.g., `points.txt`) with latitude,longitude coordinates:
   ```
   40.7128,-74.0060
   34.0522,-118.2437
   41.8781,-87.6298
   ```

3. Run the command:
   ```bash
   hrrr_ingest points.txt --variables temperature_2m,dewpoint_2m --num-hours 1
   ```

### Command Options

- `points.txt`: Path to a file containing latitude,longitude coordinates (one per line)
- `--variables`: Comma-separated list of variables to fetch (e.g., `temperature_2m,dewpoint_2m`)
- `--num-hours`: Number of forecast hours to fetch (default: 1)
- `--run-date`: Date to fetch data for in YYYYMMDD format (default: current date)

### Example

```bash
# Fetch temperature and dewpoint for 3 hours
hrrr_ingest points.txt --variables temperature_2m,dewpoint_2m --num-hours 3

# Fetch data for a specific date
hrrr_ingest points.txt --variables temperature_2m --run-date 20250501
```

## Data Storage

The tool stores the fetched data in a DuckDB database located at `data/hrrr_forecasts.duckdb`. You can query this database using any SQL client that supports DuckDB.

## Development

To set up the development environment:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
``` 