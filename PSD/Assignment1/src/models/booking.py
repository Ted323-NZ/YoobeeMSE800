"""Booking domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID


class BookingStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    ACTIVE = "active"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class InsurancePlan(str, Enum):
    NONE = "none"
    BASIC = "basic"
    PREMIUM = "premium"


@dataclass
class Booking:
    id: UUID
    user_id: UUID
    car_id: UUID
    start_date: date
    end_date: date
    status: BookingStatus
    base_daily_rate: Decimal
    addons: Dict[str, Any]
    insurance_plan: InsurancePlan
    insurance_daily_fee: Decimal
    late_fee_per_day: Decimal
    total_estimated: Decimal
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    pickup_time: Optional[datetime] = None
    return_time: Optional[datetime] = None
    total_final: Optional[Decimal] = None

    def rental_days(self) -> int:
        return (self.end_date - self.start_date).days

    def validate(self) -> None:
        # Basic integrity checks before saving.
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        if self.base_daily_rate <= Decimal("0"):
            raise ValueError("base_daily_rate must be > 0")
        for name, value in (
            ("insurance_daily_fee", self.insurance_daily_fee),
            ("late_fee_per_day", self.late_fee_per_day),
            ("total_estimated", self.total_estimated),
        ):
            if value < Decimal("0"):
                raise ValueError(f"{name} must be >= 0")
        if self.total_final is not None and self.total_final < Decimal("0"):
            raise ValueError("total_final must be >= 0")
        if self.pickup_time is not None:
            self.pickup_time = _ensure_utc(self.pickup_time)
        if self.return_time is not None:
            self.return_time = _ensure_utc(self.return_time)
        self.created_at = _ensure_utc(self.created_at)
        self.updated_at = _ensure_utc(self.updated_at)

    def to_dict(self) -> Dict[str, Any]:
        # Serialize to storage-friendly types (UUID/enum/decimal/datetime -> str).
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "car_id": str(self.car_id),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status.value,
            "pickup_time": _dt_to_iso_utc(self.pickup_time),
            "return_time": _dt_to_iso_utc(self.return_time),
            "base_daily_rate": str(self.base_daily_rate),
            "addons": self.addons,
            "insurance_plan": self.insurance_plan.value,
            "insurance_daily_fee": str(self.insurance_daily_fee),
            "late_fee_per_day": str(self.late_fee_per_day),
            "total_estimated": str(self.total_estimated),
            "total_final": str(self.total_final) if self.total_final is not None else None,
            "created_at": _dt_to_iso_utc(self.created_at),
            "updated_at": _dt_to_iso_utc(self.updated_at),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Booking":
        booking = cls(
            id=UUID(data["id"]),
            user_id=UUID(data["user_id"]),
            car_id=UUID(data["car_id"]),
            start_date=_parse_date(data["start_date"]),
            end_date=_parse_date(data["end_date"]),
            status=BookingStatus(data["status"]),
            pickup_time=_parse_datetime(data.get("pickup_time")),
            return_time=_parse_datetime(data.get("return_time")),
            base_daily_rate=Decimal(str(data["base_daily_rate"])),
            addons=dict(data.get("addons", {})),
            insurance_plan=InsurancePlan(data.get("insurance_plan", InsurancePlan.NONE)),
            insurance_daily_fee=Decimal(str(data["insurance_daily_fee"])),
            late_fee_per_day=Decimal(str(data["late_fee_per_day"])),
            total_estimated=Decimal(str(data["total_estimated"])),
            total_final=_parse_decimal_optional(data.get("total_final")),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )
        return booking


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _dt_to_iso_utc(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    dt_utc = _ensure_utc(dt)
    return dt_utc.isoformat().replace("+00:00", "Z")


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    return _ensure_utc(dt)


def _parse_date(value: Any) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value))


def _parse_decimal_optional(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    return Decimal(str(value))
