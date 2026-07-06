import psycopg2

host = "localhost"
port = 25431
db = "postgres"
user = "postgres"
password = "mysecretpassword"


def get_db():
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=db,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()