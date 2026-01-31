"""User domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID
import re


_EMAIL_MIN_LEN = 5
_EMAIL_MAX_LEN = 120
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


@dataclass
class User:
    id: UUID
    role: UserRole
    name: str
    email: str
    phone: Optional[str] = None
    driver_license_no: Optional[str] = None
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def validate(self) -> None:
        # Basic field validation before saving.
        email_len = len(self.email)
        if email_len < _EMAIL_MIN_LEN or email_len > _EMAIL_MAX_LEN:
            raise ValueError("email length out of range")
        if not _EMAIL_PATTERN.match(self.email):
            raise ValueError("invalid email format")
        if self.role == UserRole.CUSTOMER and not self.driver_license_no:
            raise ValueError("customer must have driver_license_no")
        self.created_at = _ensure_utc(self.created_at)
        self.updated_at = _ensure_utc(self.updated_at)

    def to_dict(self) -> Dict[str, Any]:
        # Serialize to storage-friendly types (UUID/enum/datetime -> str).
        return {
            "id": str(self.id),
            "role": self.role.value,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "driver_license_no": self.driver_license_no,
            "status": self.status.value,
            "created_at": _dt_to_iso_utc(self.created_at),
            "updated_at": _dt_to_iso_utc(self.updated_at),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        role = UserRole(data["role"])
        status = UserStatus(data.get("status", UserStatus.ACTIVE))
        user = cls(
            id=UUID(data["id"]),
            role=role,
            name=data["name"],
            email=data["email"],
            phone=data.get("phone"),
            driver_license_no=data.get("driver_license_no"),
            status=status,
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )
        return user


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _dt_to_iso_utc(dt: datetime) -> str:
    dt_utc = _ensure_utc(dt)
    return dt_utc.isoformat().replace("+00:00", "Z")


def _parse_datetime(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    text = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    return _ensure_utc(dt)
