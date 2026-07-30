import sqlite3
from typing import Optional
from fastapi import Request

DATABASE_PATH = "../build/trades.db"

def get_db_connection():
    """Dependency to get a DB connection per request."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Return dict-like objects
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query: str, params: tuple = (), fetchall: bool = True) -> list:
    """Helper for ad-hoc queries without FastAPI dependency injection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetchall:
            return [dict(row) for row in cursor.fetchall()]
        return dict(cursor.fetchone()) if cursor.fetchone() else None
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()
