import duckdb
from sqlmodel import BIGINT

from backends.base import collections

# note: duckdb2 coming fall 2026 will support triggers
def create_mobilityduck_connection():
    con = duckdb.connect(
        "mobilityapi.duckdb",
        config={
            "allow_unsigned_extensions": "true"
        },
    )

    con.load_extension(
        "./extensions/mobilityduck.duckdb_extension"
    )

    return con

def init_mobilityduck():
    con = create_mobilityduck_connection()
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id VARCHAR PRIMARY KEY,
                title VARCHAR NOT NULL,
                description VARCHAR,
                update_frequency INTEGER,
                item_type VARCHAR DEFAULT 'movingfeature',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # collection_id TEXT REFERENCES collections(id),
        con.execute("""
            CREATE TABLE IF NOT EXISTS moving_features (
                id TEXT PRIMARY KEY,
                collection_id TEXT,
                type TEXT DEFAULT 'Feature',
                properties JSONB,
                bbox STBOX,
                time TSTZSPAN,
                crs JSONB DEFAULT '{"type":"Name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}}'::jsonb,
                trs JSONB DEFAULT '{"type":"Name","properties":{"name":"urn:ogc:data:time:iso8601"}}'::jsonb,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)

        con.execute("CREATE SEQUENCE IF NOT EXISTS temporal_geometries_id_seq START 1")
        #    feature_id TEXT REFERENCES moving_features(id),
        #     collection_id TEXT REFERENCES collections(id),
        con.execute("""
            CREATE TABLE IF NOT EXISTS temporal_geometries (
                id BIGINT PRIMARY KEY DEFAULT nextval('temporal_geometries_id_seq'),
                feature_id TEXT,
                collection_id TEXT,
                geometry_type TEXT,
                geometry geometry,
                trajectory tgeompoint,
                interpolation TEXT,
                base JSONB,
                orientations JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        con.execute("CREATE SEQUENCE IF NOT EXISTS temporal_properties_id_seq START 1")
        # feature_id TEXT REFERENCES moving_features(id),
        con.execute("""
            CREATE TABLE IF NOT EXISTS temporal_properties (
                id BIGINT PRIMARY KEY DEFAULT nextval('temporal_properties_id_seq'),
                feature_id TEXT,
                property_name TEXT NOT NULL,
                property_type TEXT NOT NULL,
                form TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        con.execute("CREATE SEQUENCE IF NOT EXISTS temporal_values_id_seq START 1")
        #  property_id BIGINT REFERENCES temporal_properties(id),
        con.execute("""
            CREATE TABLE IF NOT EXISTS temporal_values (
                id BIGINT PRIMARY KEY DEFAULT nextval('temporal_values_id_seq'),
                property_id BIGINT,
                datetimes TIMESTAMPTZ[] NOT NULL,
                values JSONB NOT NULL,
                interpolation TEXT DEFAULT 'Linear',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
    finally:
        con.close()


def get_mobilityduck_connection():
    con = create_mobilityduck_connection()

    init_mobilityduck()

    try:
        yield con
    finally:
        con.close()