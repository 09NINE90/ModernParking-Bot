import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    "dbname": os.environ.get("DB_NAME"),
    "host": os.environ.get("DB_HOST"),
    "port": int(os.environ.get("DB_PORT")),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
}

DB_SCHEMA = os.environ.get("DB_SCHEMA")
