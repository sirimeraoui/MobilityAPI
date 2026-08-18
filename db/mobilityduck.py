import duckdb


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

    finally:
        con.close()


def get_mobilityduck_connection():
    con = create_mobilityduck_connection()

    init_mobilityduck()

    try:
        yield con
    finally:
        con.close()