import psycopg2
from config import Config

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