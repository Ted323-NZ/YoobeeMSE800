"""SQLite base utilities."""

from __future__ import annotations

from pathlib import Path
import os
import sqlite3
import sys
import threading
from typing import Iterable, List, Optional, Sequence, Tuple

def _default_base_dir() -> Path:
    # If running from a .pyz, store data next to the executable.
    argv0 = Path(sys.argv[0])
    if argv0.suffix == ".pyz":
        return argv0.resolve().parent
    file_path = Path(__file__).resolve()
    if any(part.endswith(".pyz") for part in file_path.parts):
        return Path.cwd()
    return file_path.parents[2]


_ENV_DB_PATH = os.getenv("CAR_RENTAL_DB_PATH")
_DB_PATH = Path(_ENV_DB_PATH).expanduser() if _ENV_DB_PATH else _default_base_dir() / "data" / "app.db"
_DB_LOCK = threading.Lock()
_CONNECTION: Optional[sqlite3.Connection] = None


def get_connection() -> sqlite3.Connection:
    """Get a singleton SQLite connection with basic thread safety."""
    global _CONNECTION
    if _CONNECTION is None:
        with _DB_LOCK:
            if _CONNECTION is None:
                _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
                _CONNECTION = sqlite3.connect(_DB_PATH.as_posix(), check_same_thread=False)
                _CONNECTION.row_factory = sqlite3.Row
    return _CONNECTION


def init_db() -> None:
    """Initialize database schema and indexes."""
    # Create tables and indexes if they do not exist.
    conn = get_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                driver_license_no TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cars (
                id TEXT PRIMARY KEY,
                plate_no TEXT NOT NULL,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                category TEXT NOT NULL,
                daily_rate TEXT NOT NULL,
                deposit TEXT NOT NULL,
                available_now INTEGER NOT NULL,
                min_rent_days INTEGER NOT NULL,
                max_rent_days INTEGER NOT NULL,
                status TEXT NOT NULL,
                mileage INTEGER NOT NULL,
                location TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                car_id TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL,
                pickup_time TEXT,
                return_time TEXT,
                base_daily_rate TEXT NOT NULL,
                addons TEXT NOT NULL,
                insurance_plan TEXT NOT NULL,
                insurance_daily_fee TEXT NOT NULL,
                late_fee_per_day TEXT NOT NULL,
                total_estimated TEXT NOT NULL,
                total_final TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id TEXT,
                action TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                detail TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_cars_plate_no ON cars(plate_no)")
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_bookings_car_dates_status
            ON bookings(car_id, start_date, end_date, status)
            """
        )


def execute(sql: str, params: Sequence[object] | None = None) -> int:
    """Execute a statement and return the last row id."""
    conn = get_connection()
    with conn:
        cursor = conn.execute(sql, params or ())
        return cursor.lastrowid


def query(sql: str, params: Sequence[object] | None = None) -> List[sqlite3.Row]:
    """Run a query and return all rows."""
    conn = get_connection()
    cursor = conn.execute(sql, params or ())
    return list(cursor.fetchall())


def executemany(sql: str, seq_of_params: Iterable[Sequence[object]]) -> None:
    """Execute a statement against a sequence of parameters."""
    conn = get_connection()
    with conn:
        conn.executemany(sql, seq_of_params)
