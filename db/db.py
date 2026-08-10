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
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
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
                orientations JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
            #If temporal_properties nad temporal_values tables not exists, then create
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temporal_properties (
                id SERIAL PRIMARY KEY,
                feature_id TEXT REFERENCES moving_features(id) ON DELETE CASCADE,
                property_name TEXT NOT NULL,
                property_type TEXT NOT NULL,
                form TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        #not temporal type because i can't fix the column to treal timage etc since we can have diff types of properties
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temporal_values (
                id SERIAL PRIMARY KEY,
                property_id INTEGER REFERENCES temporal_properties(id) ON DELETE CASCADE,
                datetimes TIMESTAMPTZ[] NOT NULL,
                values JSONB NOT NULL,
                interpolation TEXT DEFAULT 'Linear',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)


        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_mfeatures_on_tg()
            RETURNS TRIGGER AS $$
            DECLARE
                target_feature_id TEXT;
                target_collection_id TEXT;
            BEGIN
                IF TG_OP = 'DELETE' THEN
                    target_feature_id := OLD.feature_id;
                    target_collection_id := OLD.collection_id;
                ELSE
                    target_feature_id := NEW.feature_id;
                    target_collection_id := NEW.collection_id;
                END IF;

                -- recompute bbox + time for the parent moving feature
                UPDATE moving_features mf
                SET
                    bbox = (
                        SELECT extent(tg.trajectory)
                        FROM temporal_geometries tg
                        WHERE tg.feature_id = target_feature_id
                        AND tg.collection_id = target_collection_id
                    ),

                    time = (
                        SELECT extent(tg.trajectory)::tstzspan
                        FROM temporal_geometries tg
                        WHERE tg.feature_id = target_feature_id
                        AND tg.collection_id = target_collection_id
                    )

                WHERE mf.id = target_feature_id
                AND mf.collection_id = target_collection_id;

                RETURN COALESCE(NEW, OLD);

            END;
            $$ LANGUAGE plpgsql;
            CREATE OR REPLACE TRIGGER trg_update_mfeatures_on_tg
            AFTER INSERT OR UPDATE OR DELETE
            ON temporal_geometries
            FOR EACH ROW
            EXECUTE FUNCTION update_mfeatures_on_tg();
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