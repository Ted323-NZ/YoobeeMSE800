"""Car repository (SQLite)."""

from __future__ import annotations

import sqlite3
from typing import List, Optional
from uuid import UUID

from src.models.car import Car
from src.repositories.sqlite_base import execute, init_db, query

# Repository layer: SQL CRUD only, no business rules.


def add(car: Car) -> Car:
    init_db()
    data = car.to_dict()
    try:
        execute(
            """
            INSERT INTO cars (
                id, plate_no, make, model, year, category, daily_rate, deposit,
                available_now, min_rent_days, max_rent_days, status, mileage, location,
                created_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                data["id"],
                data["plate_no"],
                data["make"],
                data["model"],
                data["year"],
                data["category"],
                data["daily_rate"],
                data["deposit"],
                1 if data["available_now"] else 0,
                data["min_rent_days"],
                data["max_rent_days"],
                data["status"],
                data["mileage"],
                data["location"],
                data["created_at"],
                data["updated_at"],
            ),
        )
    except sqlite3.IntegrityError as exc:
        message = str(exc).lower()
        if "plate_no" in message:
            raise ValueError("plate_no must be unique") from exc
        raise
    return car


def get_by_id(car_id: UUID) -> Optional[Car]:
    init_db()
    rows = query("SELECT * FROM cars WHERE id = ?", (str(car_id),))
    if not rows:
        return None
    return Car.from_dict(dict(rows[0]))


def get_by_plate(plate_no: str) -> Optional[Car]:
    init_db()
    rows = query("SELECT * FROM cars WHERE plate_no = ?", (plate_no,))
    if not rows:
        return None
    return Car.from_dict(dict(rows[0]))


def update(car: Car) -> None:
    init_db()
    data = car.to_dict()
    execute(
        """
        UPDATE cars
        SET plate_no = ?,
            make = ?,
            model = ?,
            year = ?,
            category = ?,
            daily_rate = ?,
            deposit = ?,
            available_now = ?,
            min_rent_days = ?,
            max_rent_days = ?,
            status = ?,
            mileage = ?,
            location = ?,
            created_at = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            data["plate_no"],
            data["make"],
            data["model"],
            data["year"],
            data["category"],
            data["daily_rate"],
            data["deposit"],
            1 if data["available_now"] else 0,
            data["min_rent_days"],
            data["max_rent_days"],
            data["status"],
            data["mileage"],
            data["location"],
            data["created_at"],
            data["updated_at"],
            data["id"],
        ),
    )


def set_status(car_id: UUID, status: str) -> None:
    init_db()
    execute("UPDATE cars SET status = ? WHERE id = ?", (status, str(car_id)))


def set_available_now(car_id: UUID, available_now: bool) -> None:
    init_db()
    value = 1 if available_now else 0
    execute("UPDATE cars SET available_now = ? WHERE id = ?", (value, str(car_id)))


def list_all() -> List[Car]:
    init_db()
    rows = query("SELECT * FROM cars ORDER BY created_at ASC")
    return [Car.from_dict(dict(row)) for row in rows]


def list_available(location: Optional[str] = None) -> List[Car]:
    init_db()
    if location is None:
        rows = query(
            """
            SELECT * FROM cars
            WHERE status = 'active' AND available_now = 1
            ORDER BY created_at ASC
            """
        )
    else:
        rows = query(
            """
            SELECT * FROM cars
            WHERE status = 'active' AND available_now = 1 AND location = ?
            ORDER BY created_at ASC
            """,
            (location,),
        )
    return [Car.from_dict(dict(row)) for row in rows]
