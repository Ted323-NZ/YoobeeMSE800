"""Booking repository (SQLite)."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import List, Optional
from uuid import UUID

from src.models.booking import Booking
from src.repositories.sqlite_base import execute, init_db, query

# Repository layer: SQL CRUD only, no business rules.


def create(booking: Booking) -> Booking:
    init_db()
    data = booking.to_dict()
    addons_text = _serialize_addons(data.get("addons"))
    execute(
        """
        INSERT INTO bookings (
            id, user_id, car_id, start_date, end_date, status, pickup_time, return_time,
            base_daily_rate, addons, insurance_plan, insurance_daily_fee, late_fee_per_day,
            total_estimated, total_final, created_at, updated_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            data["id"],
            data["user_id"],
            data["car_id"],
            data["start_date"],
            data["end_date"],
            data["status"],
            data.get("pickup_time"),
            data.get("return_time"),
            data["base_daily_rate"],
            addons_text,
            data["insurance_plan"],
            data["insurance_daily_fee"],
            data["late_fee_per_day"],
            data["total_estimated"],
            data.get("total_final"),
            data["created_at"],
            data["updated_at"],
        ),
    )
    return booking


def get_by_id(booking_id: UUID) -> Optional[Booking]:
    init_db()
    rows = query("SELECT * FROM bookings WHERE id = ?", (str(booking_id),))
    if not rows:
        return None
    return _row_to_booking(rows[0])


def list_by_user(user_id: UUID) -> List[Booking]:
    init_db()
    rows = query("SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at ASC", (str(user_id),))
    return [_row_to_booking(row) for row in rows]


def list_pending() -> List[Booking]:
    init_db()
    rows = query("SELECT * FROM bookings WHERE status = 'pending' ORDER BY created_at ASC")
    return [_row_to_booking(row) for row in rows]


def list_by_car(car_id: UUID) -> List[Booking]:
    init_db()
    rows = query("SELECT * FROM bookings WHERE car_id = ? ORDER BY created_at ASC", (str(car_id),))
    return [_row_to_booking(row) for row in rows]


def update_status(booking_id: UUID, status: str) -> None:
    init_db()
    execute(
        "UPDATE bookings SET status = ?, updated_at = ? WHERE id = ?",
        (status, _now_iso_utc(), str(booking_id)),
    )


def set_pickup_time(booking_id: UUID, pickup_time_iso: str) -> None:
    init_db()
    execute(
        "UPDATE bookings SET pickup_time = ?, updated_at = ? WHERE id = ?",
        (pickup_time_iso, _now_iso_utc(), str(booking_id)),
    )


def set_return_time(booking_id: UUID, return_time_iso: str) -> None:
    init_db()
    execute(
        "UPDATE bookings SET return_time = ?, updated_at = ? WHERE id = ?",
        (return_time_iso, _now_iso_utc(), str(booking_id)),
    )


def set_totals(booking_id: UUID, total_estimated: str, total_final: Optional[str]) -> None:
    init_db()
    execute(
        """
        UPDATE bookings
        SET total_estimated = ?, total_final = ?, updated_at = ?
        WHERE id = ?
        """,
        (total_estimated, total_final, _now_iso_utc(), str(booking_id)),
    )


def check_overlap(car_id: UUID, start_date_iso: str, end_date_iso: str) -> bool:
    init_db()
    # Overlap rule: NOT (new_end <= existing_start OR new_start >= existing_end)
    rows = query(
        """
        SELECT 1 FROM bookings
        WHERE car_id = ?
          AND status IN ('approved', 'active', 'overdue')
          AND NOT (? <= start_date OR ? >= end_date)
        LIMIT 1
        """,
        (str(car_id), end_date_iso, start_date_iso),
    )
    return bool(rows)


def _row_to_booking(row: object) -> Booking:
    data = dict(row)
    data["addons"] = _deserialize_addons(data.get("addons"))
    return Booking.from_dict(data)


def _serialize_addons(addons: object) -> str:
    if addons is None:
        return "{}"
    return json.dumps(addons, ensure_ascii=True)


def _deserialize_addons(value: object) -> dict:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    text = str(value)
    if text == "":
        return {}
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid addons JSON") from exc
    if isinstance(parsed, dict):
        return parsed
    raise ValueError("addons JSON must be an object")


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
