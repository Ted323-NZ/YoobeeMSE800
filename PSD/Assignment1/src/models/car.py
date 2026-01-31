"""Car domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict
from uuid import UUID


class CarCategory(str, Enum):
    ECONOMY = "economy"
    COMPACT = "compact"
    SUV = "suv"
    LUXURY = "luxury"
    VAN = "van"


class CarStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


@dataclass
class Car:
    id: UUID
    plate_no: str
    make: str
    model: str
    year: int
    mileage: int
    available_now: bool
    min_rent_days: int
    max_rent_days: int
    daily_rate: Decimal
    deposit: Decimal
    category: CarCategory
    status: CarStatus
    location: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def validate(self) -> None:
        # Basic constraints to keep car data consistent.
        current_year = datetime.now(timezone.utc).year
        if self.year < 1980 or self.year > current_year + 1:
            raise ValueError("year out of range")
        if self.mileage < 0:
            raise ValueError("mileage must be >= 0")
        if self.daily_rate <= Decimal("0"):
            raise ValueError("daily_rate must be > 0")
        if self.deposit < Decimal("0"):
            raise ValueError("deposit must be >= 0")
        if self.min_rent_days < 1:
            raise ValueError("min_rent_days must be >= 1")
        if self.max_rent_days < self.min_rent_days or self.max_rent_days > 30:
            raise ValueError("max_rent_days must be >= min_rent_days and <= 30")
        self.created_at = _ensure_utc(self.created_at)
        self.updated_at = _ensure_utc(self.updated_at)

    def to_dict(self) -> Dict[str, Any]:
        # Serialize to storage-friendly types.
        return {
            "id": str(self.id),
            "plate_no": self.plate_no,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "mileage": self.mileage,
            "available_now": self.available_now,
            "min_rent_days": self.min_rent_days,
            "max_rent_days": self.max_rent_days,
            "daily_rate": str(self.daily_rate),
            "deposit": str(self.deposit),
            "category": self.category.value,
            "status": self.status.value,
            "location": self.location,
            "created_at": _dt_to_iso_utc(self.created_at),
            "updated_at": _dt_to_iso_utc(self.updated_at),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Car":
        car = cls(
            id=UUID(data["id"]),
            plate_no=data["plate_no"],
            make=data["make"],
            model=data["model"],
            year=int(data["year"]),
            mileage=int(data["mileage"]),
            available_now=bool(data["available_now"]),
            min_rent_days=int(data["min_rent_days"]),
            max_rent_days=int(data["max_rent_days"]),
            daily_rate=Decimal(str(data["daily_rate"])),
            deposit=Decimal(str(data["deposit"])),
            category=CarCategory(data["category"]),
            status=CarStatus(data["status"]),
            location=data["location"],
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )
        return car


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _dt_to_iso_utc(dt: datetime) -> str:
    dt_utc = _ensure_utc(dt)
    return dt_utc.isoformat().replace("+00:00", "Z")


def _parse_datetime(value: Any) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    text = str(value).replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    return _ensure_utc(dt)
