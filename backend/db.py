import os

import psycopg
from psycopg.rows import dict_row


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://forgeiq:forgeiq@localhost:5433/forgeiq",
)


def get_connection():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()
