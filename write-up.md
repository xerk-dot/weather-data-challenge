## Q&A

### Q: How long did you spend working on the problem? What difficulties, if any, did you run into along the way?
**A:** I started work at 1:10pm.

### Q: Please list any AI assistants you used to complete your solution, along with a description of how you used them. Be specific about the key prompts that you used, any areas where you found the assistant got stuck and needed help, or places where you wrote skeleton code that you asked the assistant to complete, for example.
**A: Primarily Claude Sonnet 3.5, in Cursor.**

Prompts I used:
1. Basic Setup
   - Prompt: *submits the .md*
   - Output:
   ```python
   # Strong ecosystem for scientific/weather data
   import xarray as xr
   import cfgrib  # For GRIB2 files
   
   # Good DuckDB integration
   import duckdb
   
   # Excellent CLI libraries
   import typer
   import click
   
   # AWS SDK for S3 access 
   import boto3
   ```


2. Database Connection
   - Prompt: "Show me how to connect to the database"
   - Output: "conn = create_connection('localhost:5432')"

3. Data Processing
   - Prompt: "Help me transform this CSV data"
   - Output: "df = pd.read_csv('data.csv'); df.head()"
   



### Q: Describe how you would deploy your solution as a production service. How would you schedule the ingestion routines as new data becomes available? What data storage technology would you use to make the data more readily available to analysts and researchers? What monitoring would you put in place to ensure system correctness?
**A:** [Your answer about production deployment strategy]

### Q: As specified here, your solution will only ingest data for a single run date. How would you scale it up to support large-scale backfills of many data points across years worth of data? What performance improvements would you likely need to implement? Try to be as specific as possible.
**A:** [Your answer about scaling strategy and performance improvements]