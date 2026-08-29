import duckdb
import time



con = duckdb.connect(
    config={"allow_unsigned_extensions": "true"}
)

# MobilityDuck
con.load_extension("./extensions/mobilityduck.duckdb_extension")

# Iceberg
con.execute("INSTALL iceberg")
con.execute("LOAD iceberg")

print("MobilityDuck + Iceberg loaded")



# 2 POLARIS AUTHENTICATION

con.execute("""
    CREATE OR REPLACE SECRET polaris_secret (
        TYPE iceberg,
        CLIENT_ID '4ef64c324a3e8877',
        CLIENT_SECRET 'fd6d847d6efdb6efe4ae23c6b1d3ea9e',
        OAUTH2_SERVER_URI 'http://localhost:8181/api/catalog/v1/oauth/tokens',
        OAUTH2_GRANT_TYPE 'client_credentials',
        OAUTH2_SCOPE 'PRINCIPAL_ROLE:ALL'
    )
""")
# 3 ATTACH POLARIS


print("\nATTACHING POLARIS:")

con.execute("""
    ATTACH 'quickstart_catalog' AS lakehouse (
        TYPE iceberg,
        SECRET polaris_secret,
        ENDPOINT 'http://localhost:8181/api/catalog'
    )
""")

print("Polaris catalog attached")


# 4 CHECK MOBILITY NAMESPACE


print("\nCREATING MOBILITY NAMESPACE:")

con.execute("""
    CREATE SCHEMA IF NOT EXISTS lakehouse.mobility
""")


# 5 CHECK TABLE


print("\n=== TRAJECTORIES TABLE ===")

tables = con.execute("""
    SHOW ALL TABLES
""").fetchall()

for row in tables:
    print(row)



# 6 READ COVERING COLUMNS


print("\n=== COVERING COLUMNS ===")

rows = con.execute("""
    SELECT
        entity_id,
        xmin,
        xmax,
        ymin,
        ymax,
        tmin,
        tmax,
        srid
    FROM lakehouse.mobility.collection_ships
    LIMIT 5
""").fetchall()

for row in rows:
    print(row)

# 7RECONSTRUCT ONE TRAJECTORY


print("\n=== TRAJECTORY RECONSTRUCTION ===")

rows = con.execute("""
    SELECT
        entity_id,
        asText(tgeompointFromBinary(traj)) AS trajectory
    FROM lakehouse.mobility.collection_ships
    LIMIT 1
""").fetchall()

for row in rows:
    print(row[0])
    print("Trajectory successfully reconstructed.")


# 8 COVERING-COLUMN FILTER


print("\n=== COVERING COLUMN FILTER ===")

query = """
    SELECT
        entity_id,
        xmin,
        xmax,
        ymin,
        ymax,
        tmin,
        tmax
    FROM lakehouse.mobility.collection_ships
    WHERE tmax >= TIMESTAMPTZ '2024-08-07 20:00:00+02'
      AND tmin <  TIMESTAMPTZ '2024-08-07 22:00:00+02'
      AND xmax >= 653500
      AND xmin <= 654100
      AND ymax >= 6056700
      AND ymin <= 6056900
"""

start = time.perf_counter()

rows = con.execute(query).fetchall()

elapsed = time.perf_counter() - start

print(f"Candidate trajectories: {len(rows)}")
print(f"Query time: {elapsed:.6f} seconds")

for row in rows:
    print(row)


# 9 RECONSTRUCT TRAJECTORIES AFTER PRUNING


print("\n=== SPATIOTEMPORAL QUERY ===")

query = """
    SELECT
        entity_id,
        asText(tgeompointFromBinary(traj)) AS trajectory
    FROM lakehouse.mobility.collection_ships
    WHERE tmax >= TIMESTAMPTZ '2024-08-07 20:00:00+02'
      AND tmin <  TIMESTAMPTZ '2024-08-07 22:00:00+02'
      AND xmax >= 653500
      AND xmin <= 654100
      AND ymax >= 6056700
      AND ymin <= 6056900
"""

start = time.perf_counter()

rows = con.execute(query).fetchall()

elapsed = time.perf_counter() - start

print(f"Returned trajectories: {len(rows)}")
print(f"Query time: {elapsed:.6f} seconds")

for row in rows:
    print("\nEntity:", row[0])
    print("Trajectory:")
    print(row[1][:500], "...")




print("\nEND-TO-END ICEBERG TEST COMPLETE")