# HRRR Weather Data Ingestion Tool

A command-line tool for ingesting and storing HRRR (High-Resolution Rapid Refresh) weather forecast data from NOAA.

## Features

- Downloads HRRR forecast data from AWS S3
- Processes GRIB2 files to extract specific variables
- Finds nearest grid points for given coordinates
- Stores data in a local DuckDB database
- Supports idempotent operations (skips existing data)
- Configurable variables and forecast hours

## Installation

1. Clone the repository, set up virtual environment:```bash
git clone <repository-url>
cd src/hrrr_ingest
python3 -m venv venv
source venv/bin/activate
```


2. Install dependencies:
```bash
pip3 install -e .
```

### Application Level
- Before processing, chåecks if data already exists for a specific point, time, and variable
- If data exists, logs a message and skips that data point
- Makes the process more efficient by avoiding unnecessary processing

The tool is invoked as follows:

```bash
hrrr-ingest points.txt [--run-date YYYY-MM-DD] [--variables var1,var2,...] [--num-hours N]
```

### Arguments

- `points.txt`: Required. A text file containing comma-separated latitude,longitude pairs (one per line)
- `--run-date`: Optional. The forecast run date in YYYY-MM-DD format. Defaults to today
- `--variables`: Optional. Comma-separated list of variables to ingest. Defaults to all supported variables
- `--num-hours`: Optional. Number of forecast hours to ingest. Defaults to 48

### Supported Variables

- `surface_pressure`
- `surface_roughness`
- `visible_beam_downward_solar_flux`
- `visible_diffuse_downward_solar_flux`
- `temperature_2m`
- `dewpoint_2m`
- `relative_humidity_2m`
- `u_component_wind_10m`
- `v_component_wind_10m`
- `u_component_wind_80m`
- `v_component_wind_80m`

### Example

```bash
# Ingest all variables for today's forecast
hrrr-ingest points.txt

# Ingest specific variables for a given date
hrrr-ingest points.txt --run-date 2023-04-01 --variables temperature_2m,relative_humidity_2m

# Ingest only 24 hours of forecast data
hrrr-ingest points.txt --num-hours 24
```

## Database Schema

Data is stored in a DuckDB database (`data.db`) with the following schema:

```sql
CREATE TABLE hrrr_forecasts (
    valid_time_utc TIMESTAMP,
    run_time_utc TIMESTAMP,
    latitude FLOAT,
    longitude FLOAT,
    variable VARCHAR,
    value FLOAT,
    source_s3 VARCHAR,
    PRIMARY KEY (valid_time_utc, run_time_utc, latitude, longitude, variable)
)
```

## Development

### Setup

1. Create a virtual environment:
```bash
cd new_structure
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip3 install -e .
```

3. Try a command

```bash
hrrr_ingest data_points/points_01.txt --variables surface_pressure,surface_roughness,visible_beam_downward_solar_flux,visible_diffuse_downward_solar_flux,temperature_2m,dewpoint_2m,relative_humidity_2m,u_component_wind_10m,v_component_wind_10m,u_component_wind_80m,v_component_wind_80m --num-hours 3


#Show the ingested data for all 11 required variables
duckdb data.db "WITH stats AS (SELECT variable, COUNT(*) as count, ROUND(AVG(value), 2) as avg_value, ROUND(MIN(value), 2) as min_value, ROUND(MAX(value), 2) as max_value, COUNT(DISTINCT latitude) as num_points FROM hrrr_forecasts GROUP BY variable) SELECT * FROM stats ORDER BY variable;"


#Show the data points for the three major US cities
duckdb data.db "SELECT DISTINCT latitude, longitude FROM hrrr_forecasts ORDER BY latitude;"

```
### Testing

Run tests with:
```bash
pytest
```
#### About Idempotency

The code implements idempotency in two ways:

##### Database Level
In `database.py`, there are two mechanisms to prevent duplicate data:
- The table has a PRIMARY KEY constraint on (`valid_time_utc`, `run_time_utc`, `latitude`, `longitude`, `variable`)
- The `insert_forecast_data` function uses `INSERT OR IGNORE` which will skip any rows that would violate the primary key constraint

##### Application Level 
In `process.py`, before inserting data:
- The code calls `check_existing_data` to verify if data for a specific point, time, and variable already exists
- If the data exists, it logs a message and skips that data point with `continue`

This means that:
- If you run the same command multiple times with the same parameters, it will only insert new data that doesn't already exist
- The database will reject any duplicate entries due to the primary key constraint
- The application will skip processing points that already have data, making the process more efficient

cd new_structure && PYTHONPATH=src python3 -m hrrr_ingest.cli points.txt --variables temperature_2m,dewpoint_2m --num-hours 1



