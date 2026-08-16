import os
import tempfile

import duckdb


def parquet_to_iceberg(
    parquet_bytes: bytes,
    collection_id: str,
):
    # Write the Parquet bytes to a temporary file
    with tempfile.NamedTemporaryFile(
        suffix=".parquet",
        delete=False,
    ) as tmp:
        tmp.write(parquet_bytes)
        parquet_path = tmp.name

    try:
        # Connect to DuckDB
        con = duckdb.connect(
            config={"allow_unsigned_extensions": "true"}
        )

        # MobilityDuck
        con.load_extension(
            "./extensions/mobilityduck.duckdb_extension"
        )

        # Iceberg
        con.execute("INSTALL iceberg")
        con.execute("LOAD iceberg")

        # Polaris authentication
        con.execute("""
            CREATE OR REPLACE SECRET polaris_secret (
                TYPE iceberg,
                CLIENT_ID '9f4cc3609fdcf296',
                CLIENT_SECRET 'a482121328018941b2cce50f3a11c2ef',
                OAUTH2_SERVER_URI
                    'http://localhost:8181/api/catalog/v1/oauth/tokens'
            )
        """)

        # Attach Polaris
        con.execute("""
            ATTACH 'quickstart_catalog' AS lakehouse (
                TYPE iceberg,
                SECRET polaris_secret,
                ENDPOINT 'http://localhost:8181/api/catalog'
            )
        """)

        # Make sure the namespace exists
        con.execute("""
            CREATE SCHEMA IF NOT EXISTS lakehouse.mobility
        """)

# Make sure the namespace exists
        con.execute("""
            CREATE SCHEMA IF NOT EXISTS lakehouse.mobility
        """)

        # -----------------------------------------------------
        # 6. Create Iceberg table from API-generated Parquet
        # -----------------------------------------------------

        table_name = f"lakehouse.mobility.collection_{collection_id}"

        print(f"Creating Iceberg table: {table_name}")

        con.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT *
            FROM read_parquet('{parquet_path}')
        """)

        return table_name

    finally:
        os.unlink(parquet_path)
