import duckdb

PARQUET_FILE = "./ships.parquet"

con = duckdb.connect(
    config={"allow_unsigned_extensions": "true"}
)

con.load_extension("../extensions/mobilityduck.duckdb_extension")


# 1. Can DuckDB read the Parquet?

result = con.execute(
    f"""
    SELECT *
    FROM read_parquet('{PARQUET_FILE}')
    LIMIT 5
    """
).fetchall()

print("PARQUET CONTENT:")

for row in result:
    print(row)


# 2. Check the Parquet schema

print("\nSCHEMA:")

result = con.execute(
    f"""
    DESCRIBE
    SELECT *
    FROM read_parquet('{PARQUET_FILE}')
    """
).fetchall()

for row in result:
    print(row)


# 3. Reconstruct a trajectory from the MEOS-WKB stored in Parquet

print("\nTRAJECTORY RECONSTRUCTION:")

result = con.execute(
    f"""
    SELECT
        entity_id,
        asText(
            tgeompointFromBinary(traj)
        )
    FROM read_parquet('{PARQUET_FILE}')
    LIMIT 1
    """
).fetchall()

for row in result:
    print(row)


# 4. Inspect the actual covering-column extents

print("\nCOVERING EXTENTS:")

result = con.execute(
    f"""
    SELECT
        MIN(xmin),
        MAX(xmax),
        MIN(ymin),
        MAX(ymax),
        MIN(tmin),
        MAX(tmax)
    FROM read_parquet('{PARQUET_FILE}')
    """
).fetchone()

print(result)

print("\nCOVERING COLUMN FILTER:")

result = con.execute(
    f"""
    SELECT
        entity_id,
        xmin,
        xmax,
        ymin,
        ymax,
        tmin,
        tmax
    FROM read_parquet('{PARQUET_FILE}')
    WHERE tmax >= TIMESTAMPTZ '2024-08-07 12:00:00+02'
      AND tmin < TIMESTAMPTZ '2024-08-08 00:00:00+02'
      AND xmax >= 600000
      AND xmin <= 800000
      AND ymax >= 6000000
      AND ymin <= 6200000
    """
).fetchall()

for row in result:
    print(row)


# 5. Test selective lakehouse query + trajectory reconstruction

print("\nSELECTIVE TRAJECTORY QUERY:")

result = con.execute(
    f"""
    SELECT
        entity_id,
        asText(tgeompointFromBinary(traj)) AS trajectory
    FROM read_parquet('{PARQUET_FILE}')
    WHERE entity_id = '244070564'
      AND tmax >= TIMESTAMPTZ '2024-08-07 20:00:00+02'
      AND tmin < TIMESTAMPTZ '2024-08-07 22:00:00+02'
      AND xmax >= 653500
      AND xmin <= 654100
      AND ymax >= 6056700
      AND ymin <= 6056900
    """
).fetchall()

for row in result:
    print(row)


    # 6. Check the SRID stored in the Parquet file

print("\nSRID CHECK:")

result = con.execute(
    f"""
    SELECT
        srid,
        COUNT(*) AS count
    FROM read_parquet('{PARQUET_FILE}')
    GROUP BY srid
    ORDER BY srid
    """
).fetchall()

for row in result:
    print(row)


    # mobiliy -----------------------------------------------

con.execute("INSTALL iceberg")
con.execute("LOAD iceberg")

print("Iceberg loaded successfully")

# Create an Iceberg table from the TemporalParquet file
