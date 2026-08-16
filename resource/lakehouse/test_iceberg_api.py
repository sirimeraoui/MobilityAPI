import duckdb

# ============================================================
# CONFIGURATION
# ============================================================

COLLECTION_TABLE = "lakehouse.mobility.collection_ships"


# ============================================================
# CONNECT TO DUCKDB
# ============================================================

con = duckdb.connect(
    config={"allow_unsigned_extensions": "true"}
)

con.load_extension("../../extensions/mobilityduck.duckdb_extension")

con.execute("INSTALL iceberg")
con.execute("LOAD iceberg")

print("Iceberg and MobilityDuck extensions loaded")


# ============================================================
# CONNECT TO POLARIS
# ============================================================

con.execute("""
    CREATE OR REPLACE SECRET polaris_secret (
        TYPE iceberg,
        CLIENT_ID '9f4cc3609fdcf296',
        CLIENT_SECRET 'a482121328018941b2cce50f3a11c2ef',
        OAUTH2_SERVER_URI
            'http://localhost:8181/api/catalog/v1/oauth/tokens'
    )
""")

con.execute("""
    ATTACH 'quickstart_catalog' AS lakehouse (
        TYPE iceberg,
        SECRET polaris_secret,
        ENDPOINT 'http://localhost:8181/api/catalog'
    )
""")

print("Polaris catalog attached")


# ============================================================
# TEST 1 — CHECK NUMBER OF TRAJECTORIES
# ============================================================

print("\n=== TEST 1: ICEBERG TABLE ROW COUNT ===")

result = con.execute(f"""
    SELECT COUNT(*)
    FROM {COLLECTION_TABLE}
""").fetchone()

print("Total trajectories:", result[0])


# ============================================================
# TEST 2 — CHECK COVERING COLUMNS
# ============================================================

print("\n=== TEST 2: COVERING COLUMNS ===")

result = con.execute(f"""
    SELECT
        entity_id,
        xmin,
        xmax,
        ymin,
        ymax,
        tmin,
        tmax,
        srid
    FROM {COLLECTION_TABLE}
    LIMIT 5
""").fetchall()

for row in result:
    print(row)


# ============================================================
# TEST 3 — RECONSTRUCT A TRAJECTORY
# ============================================================

print("\n=== TEST 3: TRAJECTORY RECONSTRUCTION ===")

result = con.execute(f"""
    SELECT
        entity_id,
        asText(
            tgeompointFromBinary(traj)
        ) AS trajectory
    FROM {COLLECTION_TABLE}
    LIMIT 1
""").fetchall()

for row in result:
    print(row)


# ============================================================
# TEST 4 — SPATIOTEMPORAL FILTER
# ============================================================

print("\n=== TEST 4: SPATIOTEMPORAL FILTER ===")

result = con.execute(f"""
    SELECT
        entity_id,
        xmin,
        xmax,
        ymin,
        ymax,
        tmin,
        tmax
    FROM {COLLECTION_TABLE}
    WHERE tmax >= TIMESTAMPTZ '2024-08-07 20:00:00+02'
      AND tmin <  TIMESTAMPTZ '2024-08-07 22:00:00+02'
      AND xmax >= 653500
      AND xmin <= 654100
      AND ymax >= 6056700
      AND ymin <= 6056900
""").fetchall()

print("Matching trajectories:", len(result))

for row in result:
    print(row)


# ============================================================
# TEST 5 — RECONSTRUCT FILTERED TRAJECTORIES
# ============================================================

print("\n=== TEST 5: FILTERED TRAJECTORY RECONSTRUCTION ===")

result = con.execute(f"""
    SELECT
        entity_id,
        asText(
            tgeompointFromBinary(traj)
        ) AS trajectory
    FROM {COLLECTION_TABLE}
    WHERE tmax >= TIMESTAMPTZ '2024-08-07 20:00:00+02'
      AND tmin <  TIMESTAMPTZ '2024-08-07 22:00:00+02'
      AND xmax >= 653500
      AND xmin <= 654100
      AND ymax >= 6056700
      AND ymin <= 6056900
""").fetchall()

print("Matching trajectories:", len(result))

for row in result[:3]:
    print(row)


# ============================================================
# TEST 6 — CHECK ICEBERG QUERY PLAN
# ============================================================

print("\n=== TEST 6: ICEBERG QUERY PLAN ===")

result = con.execute(f"""
    EXPLAIN
    SELECT
        entity_id,
        asText(
            tgeompointFromBinary(traj)
        ) AS trajectory
    FROM {COLLECTION_TABLE}
    WHERE tmax >= TIMESTAMPTZ '2024-08-07 20:00:00+02'
      AND tmin <  TIMESTAMPTZ '2024-08-07 22:00:00+02'
      AND xmax >= 653500
      AND xmin <= 654100
      AND ymax >= 6056700
      AND ymin <= 6056900
""").fetchall()

for row in result:
    print(row)


# ============================================================
# TEST 7 — CHECK ICEBERG TABLE SCHEMA
# ============================================================

print("\n=== TEST 7: ICEBERG TABLE SCHEMA ===")

result = con.execute(f"""
    DESCRIBE {COLLECTION_TABLE}
""").fetchall()

for row in result:
    print(row)


# ============================================================
# DONE
# ============================================================

print("\n=== ALL API → ICEBERG TESTS COMPLETED ===")

con.close()