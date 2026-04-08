# Based on section 9.2 AIS Data Cleaning from the MobilityDataScience book
# and https://github.com/mahmsakr/MobilityDataScienceClass/tree/main/Mobility%20Data%20Cleaning
from sqlalchemy import create_engine, text
import json
import zipfile
import os
import geopandas as gpd
import pandas as pd
import numpy as np

from utils import get_csv_from_zip
# Load database configuration from config.json
with open("../config.json", "r") as file:
    config = json.load(file)

# Construct the database URL for SQLAlchemy
database_url = (
    f"postgresql://{config['DB_USER']}:{config['DB_PASS']}@"
    f"{config['DB_HOST']}:{config['DB_PORT']}/{config['DB_NAME']}"
)

# Create the SQLAlchemy engine
engine = create_engine(database_url)
data_csv_path = get_csv_from_zip("aisdk-2024-08-07.zip")
data_csv_path=os.path.abspath(data_csv_path)
print(data_csv_path)
#update this based on whether you're running your db from docker or local/ this is a docker version, otherwise comment it out
container_csv_path = "/tmp/aisdk.csv"
container_name = "mobilitydb"  # Your container name
docker_cmd = f"docker cp {data_csv_path} {container_name}:{container_csv_path}"
os.system(docker_cmd)
data_csv_path= container_csv_path

# Data collection and 9.3 Cleaning Static Attribute +9.4 Voyage related Attribbutes:
try:
    # Read the SQL file CleaningStaticAttributes.sql
    with open("init.sql", "r") as sql_file:
        sql_query = sql_file.read()

    # Create a text object with parameters
    stmt = text(sql_query).bindparams(data_csv_path=data_csv_path)

    # Execute with parameter
    with engine.connect() as conn:
        # Start a transaction
        with conn.begin():
            # Execute the COPY command with parameter
            conn.execute(stmt)
            print(f"Successfully loaded data from {data_csv_path}")

except Exception as e:
    print(f"Error loading data: {e}")
    raise


# After your existing data loading code, add this:

def export_json_from_view(engine, output_file="trajectories_mf1.json"):
    query = "SELECT json_data FROM ships_json ORDER BY mmsi;"
    
    try:
        # Fetch all JSON data from the view
               # for df in pd.read_sql(query, engine,chunksize=686):
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("No data found in ships_json view")
            return []
        
        # Extract the json_data column as a list of dicts
        json_ready = df['json_data'].tolist()
        print('777777777777777777777777777777777777777777777')
        # Ensure output directory exists
        # os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to JSON file
        with open(output_file, "w") as f:
            json.dump(json_ready, f, indent=2, default=str)
        
        print(f"Successfully exported {len(json_ready)} vessels to {output_file}")
        return json_ready
        
    except Exception as e:
        print(f"Error exporting JSON: {e}")
        raise

# Call the function after your data loading
if __name__ == "__main__":

    
    # Export to JSON
    export_json_from_view(engine, "trajectories_mf1.json")
   
    
    # DROP VIEW IF EXISTS ships_json CASCADE;
    # DROP TABLE IF EXISTS Ships CASCADE;

    drop_tables_sql = """
        DROP TABLE IF EXISTS AISInputFiltered CASCADE;
        DROP TABLE IF EXISTS AISInput CASCADE;
    """
    try:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(drop_tables_sql))
                #  Ships, ships_json
        print("dropped ables (AISInput, AISInputFiltered).")
    except Exception as e:
        print(f"Error during cleanup: {e}")
