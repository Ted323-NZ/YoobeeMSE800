"""User repository (SQLite)."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from src.models.user import User
from src.repositories.sqlite_base import execute, init_db, query

# Repository layer: SQL CRUD only, no business rules.


def create_user(user: User) -> None:
    init_db()
    data = user.to_dict()
    execute(
        """
        INSERT INTO users (
            id, role, name, email, phone, driver_license_no, status, created_at, updated_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            data["id"],
            data["role"],
            data["name"],
            data["email"],
            data["phone"],
            data["driver_license_no"],
            data["status"],
            data["created_at"],
            data["updated_at"],
        ),
    )


def get_user_by_id(user_id: UUID) -> Optional[User]:
    init_db()
    rows = query("SELECT * FROM users WHERE id = ?", (str(user_id),))
    if not rows:
        return None
    return _row_to_user(rows[0])


def get_user_by_email(email: str) -> Optional[User]:
    init_db()
    rows = query("SELECT * FROM users WHERE email = ?", (email,))
    if not rows:
        return None
    return _row_to_user(rows[0])


def list_users() -> List[User]:
    init_db()
    rows = query("SELECT * FROM users ORDER BY created_at ASC")
    return [_row_to_user(row) for row in rows]


def update_user(user: User) -> None:
    init_db()
    data = user.to_dict()
    execute(
        """
        UPDATE users
        SET role = ?,
            name = ?,
            email = ?,
            phone = ?,
            driver_license_no = ?,
            status = ?,
            created_at = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            data["role"],
            data["name"],
            data["email"],
            data["phone"],
            data["driver_license_no"],
            data["status"],
            data["created_at"],
            data["updated_at"],
            data["id"],
        ),
    )


def delete_user(user_id: UUID) -> None:
    init_db()
    execute("DELETE FROM users WHERE id = ?", (str(user_id),))


def _row_to_user(row: object) -> User:
    data = dict(row)
    return User.from_dict(data)
