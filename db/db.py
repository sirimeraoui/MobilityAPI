import psycopg2
from config import Config
# from sqlmodel import create_engine, text
# from sqlalchemy.ext.asyncio import AsyncEngine

def get_db():
    conn = psycopg2.connect(
        host=Config.HOST,
        port=Config.PORT,
        database=Config.DB,
        user=Config.DB_USER,
        password=Config.PASSWORD
    )
    cursor = conn.cursor()

    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()


def init_db():
    conn = psycopg2.connect(
        host=Config.HOST,
        port=Config.PORT,
        database=Config.DB,
        user=Config.DB_USER,
        password=Config.PASSWORD
    )
    cursor = conn.cursor()

    try:
        # create tables if not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                update_frequency INTEGER,
                item_type TEXT DEFAULT 'movingfeature',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moving_features (
                id TEXT PRIMARY KEY,
                collection_id TEXT REFERENCES collections(id) ON DELETE CASCADE,
                type TEXT DEFAULT 'Feature',
                properties JSONB,
                bbox STBOX,
                time TSTZSPAN,
                crs JSONB DEFAULT '{"type":"Name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}}'::jsonb,
                trs JSONB DEFAULT '{"type":"Name","properties":{"name":"urn:ogc:data:time:iso8601"}}'::jsonb,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temporal_geometries (
                id SERIAL PRIMARY KEY,
                feature_id TEXT REFERENCES moving_features(id) ON DELETE CASCADE,
                collection_id TEXT REFERENCES collections(id) ON DELETE CASCADE,
                geometry_type TEXT,
                geometry geometry,
                trajectory tgeompoint,
                interpolation TEXT,
                base JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


# engine = AsyncEngine(
#     create_engine(

#     )
# )

# async def init_db():
#     async with engine.begin() as conn:
#         statement = text("the initia table creation s here ")
#         result= await conn.execute(statement)
#         print(result.all())