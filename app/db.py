import pymysql
import pymysql.cursors

from app import config


def get_connection():
    """Returns a new DB connection with dict-style row cursors."""
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def test_connection():
    try:
        conn = get_connection()
        conn.close()
        print(f"[OK] Connected to MySQL database '{config.DB_NAME}'")
    except Exception as e:
        print(f"[ERROR] Could not connect to MySQL: {e}")
        print("        Check app/config.py / environment variables and that MySQL is running.")
