import os

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_NAME = os.environ.get("DB_NAME", "ems_db")
DB_USER = os.environ.get("DB_USER", "emsuser")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "ems123")

SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))
