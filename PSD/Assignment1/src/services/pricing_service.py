"""Pricing service functions."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Mapping, Optional


_QUANT = Decimal("0.01")


def compute_estimated_total(booking: Any) -> Decimal:
    """Compute base_fee + addons_fee + insurance_fee."""
    # Price is calculated per day and rounded to 2 decimals.
    rental_days = _rental_days(booking)
    base_fee = _to_decimal(booking.base_daily_rate) * rental_days
    addons_daily = _sum_addons_daily(booking.addons)
    addons_fee = addons_daily * rental_days
    insurance_fee = _to_decimal(booking.insurance_daily_fee) * rental_days
    subtotal = base_fee + addons_fee + insurance_fee
    return _q(subtotal)


def compute_cancellation_fee(booking: Any, cancelled_at_dt: datetime) -> Decimal:
    """Charge 1 * base_daily_rate if cancellation is within 24 hours of start_date."""
    if cancelled_at_dt is None:
        return Decimal("0.00")
    cancelled_at = _ensure_utc_dt(cancelled_at_dt)
    start_dt = datetime.combine(booking.start_date, time.min, tzinfo=timezone.utc)
    delta = start_dt - cancelled_at
    if delta < timedelta(hours=24):
        return _q(_to_decimal(booking.base_daily_rate))
    return Decimal("0.00")


def compute_late_fee(booking: Any) -> Decimal:
    """Compute late fee based on return_time and end_date."""
    if booking.return_time is None:
        return Decimal("0.00")
    return_time = _ensure_utc_dt(booking.return_time)
    late_days = max(0, (return_time.date() - booking.end_date).days)
    late_fee = _to_decimal(booking.late_fee_per_day) * late_days
    if late_days > 3:
        late_fee += _to_decimal(booking.base_daily_rate)
    return _q(late_fee)


def compute_final_total(booking: Any, cancelled_at_dt: Optional[datetime] = None) -> Decimal:
    """Compute subtotal + late_fee + cancel_fee - discount_total."""
    subtotal = compute_estimated_total(booking)
    late_fee = compute_late_fee(booking)
    cancel_fee = Decimal("0.00")
    if cancelled_at_dt is not None:
        cancel_fee = compute_cancellation_fee(booking, cancelled_at_dt)
    discount_total = _to_decimal(getattr(booking, "discount_total", Decimal("0")))
    total = subtotal + late_fee + cancel_fee - discount_total
    return _q(total)


def _rental_days(booking: Any) -> int:
    if hasattr(booking, "rental_days"):
        return int(booking.rental_days())
    return int((booking.end_date - booking.start_date).days)


def _sum_addons_daily(addons: Any) -> Decimal:
    # Accept dict/list input so CLI can pass flexible add-on formats.
    if not addons:
        return Decimal("0")
    if isinstance(addons, Mapping):
        values = addons.values()
    elif isinstance(addons, (list, tuple)):
        values = addons
    else:
        raise ValueError("addons must be a mapping or list of prices")
    total = Decimal("0")
    for value in values:
        total += _to_decimal(value)
    return total


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _q(value: Decimal) -> Decimal:
    # Consistent money rounding (half up) for all totals.
    return value.quantize(_QUANT, rounding=ROUND_HALF_UP)


def _ensure_utc_dt(value: Any) -> datetime:
    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime.combine(value, time.min, tzinfo=timezone.utc)
    if not isinstance(value, datetime):
        raise ValueError("datetime value required")
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
