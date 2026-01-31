"""Booking service functions (business rules)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from src.models.booking import Booking, BookingStatus, InsurancePlan
from src.models.car import Car, CarCategory, CarStatus
from src.models.user import User, UserStatus
from src.repositories import booking_repo, car_repo, user_repo
from src.services import pricing_service

try:
    from src.repositories import audit_repo
except ImportError:  # audit repo is optional in MVP
    audit_repo = None


_INSURANCE_DAILY_FEE = {
    InsurancePlan.NONE: Decimal("0.00"),
    InsurancePlan.BASIC: Decimal("15.00"),
    InsurancePlan.PREMIUM: Decimal("30.00"),
}
_DEFAULT_LATE_FEE_PER_DAY = Decimal("20.00")

_CATEGORY_RANK = {
    CarCategory.ECONOMY: 1,
    CarCategory.COMPACT: 2,
    CarCategory.SUV: 3,
    CarCategory.LUXURY: 4,
    CarCategory.VAN: 5,
}


def create_booking(
    customer_id: UUID,
    car_id: UUID,
    start_date: date | str,
    end_date: date | str,
    insurance_plan: InsurancePlan | str,
    addons: Optional[Dict[str, Any]] = None,
) -> Booking:
    # Validate user/car state and date range before creating a booking.
    user = _require_user(customer_id)
    if _user_is_suspended(user):
        raise ValueError("user is suspended")

    car = _require_car(car_id)
    if _car_status(car) != CarStatus.ACTIVE:
        raise ValueError("car is not active")
    if not car.available_now:
        raise ValueError("car is not available now")

    start = _parse_date(start_date)
    end = _parse_date(end_date)
    if start < _today_utc() or start >= end:
        raise ValueError("invalid date range")

    rental_days = (end - start).days
    if rental_days < 1 or rental_days > 30:
        raise ValueError("rental days out of global range")
    if rental_days < car.min_rent_days or rental_days > car.max_rent_days:
        raise ValueError("rental days out of car range")

    # Block overlapping bookings for the same car.
    if booking_repo.check_overlap(car_id, start.isoformat(), end.isoformat()):
        raise ValueError("booking dates overlap")

    plan = _parse_insurance_plan(insurance_plan)
    insurance_fee = _INSURANCE_DAILY_FEE.get(plan, Decimal("0.00"))

    booking = Booking(
        id=uuid4(),
        user_id=user.id,
        car_id=car.id,
        start_date=start,
        end_date=end,
        status=BookingStatus.PENDING,
        pickup_time=None,
        return_time=None,
        base_daily_rate=car.daily_rate,
        addons=addons or {},
        insurance_plan=plan,
        insurance_daily_fee=insurance_fee,
        late_fee_per_day=_DEFAULT_LATE_FEE_PER_DAY,
        total_estimated=Decimal("0.00"),
        total_final=None,
    )
    # Snapshot pricing inputs and compute estimated total now.
    booking.total_estimated = pricing_service.compute_estimated_total(booking)
    booking_repo.create(booking)
    return booking


def approve_booking(admin_id: UUID, booking_id: UUID) -> Booking:
    booking = _require_booking(booking_id)
    if booking_repo.check_overlap(
        booking.car_id, booking.start_date.isoformat(), booking.end_date.isoformat()
    ):
        raise ValueError("booking dates overlap")

    booking_repo.update_status(booking_id, BookingStatus.APPROVED.value)
    if booking.start_date <= _today_utc():
        car_repo.set_available_now(booking.car_id, False)

    _audit(admin_id, "approve_booking", "booking", booking.id, "{}")
    return _require_booking(booking_id)


def reject_booking(admin_id: UUID, booking_id: UUID, reason: str) -> Booking:
    _require_booking(booking_id)
    booking_repo.update_status(booking_id, BookingStatus.REJECTED.value)
    _audit(admin_id, "reject_booking", "booking", booking_id, _json_detail({"reason": reason}))
    return _require_booking(booking_id)


def cancel_booking(actor_id: UUID, booking_id: UUID, cancelled_at_dt: datetime) -> Booking:
    booking = _require_booking(booking_id)
    cancel_fee = pricing_service.compute_cancellation_fee(booking, cancelled_at_dt)
    estimated = pricing_service.compute_estimated_total(booking)
    booking.total_estimated = estimated
    booking.return_time = None
    booking.total_final = pricing_service.compute_final_total(booking, cancelled_at_dt)

    booking_repo.set_totals(booking_id, str(estimated), str(booking.total_final))
    booking_repo.update_status(booking_id, BookingStatus.CANCELLED.value)
    _audit(actor_id, "cancel_booking", "booking", booking_id, _json_detail({"cancel_fee": str(cancel_fee)}))
    return _require_booking(booking_id)


def pickup(admin_id: UUID, booking_id: UUID) -> Booking:
    booking = _require_booking(booking_id)
    if booking.status != BookingStatus.APPROVED:
        raise ValueError("booking must be approved for pickup")

    pickup_time = _now_utc()
    booking_repo.set_pickup_time(booking_id, pickup_time.isoformat().replace("+00:00", "Z"))
    booking_repo.update_status(booking_id, BookingStatus.ACTIVE.value)
    car_repo.set_available_now(booking.car_id, False)

    _audit(admin_id, "pickup", "booking", booking_id, "{}")
    return _require_booking(booking_id)


def return_car(admin_id: UUID, booking_id: UUID, return_time_dt: datetime) -> Booking:
    booking = _require_booking(booking_id)
    return_time = _ensure_utc_dt(return_time_dt)

    late_days = max(0, (return_time.date() - booking.end_date).days)
    new_status = BookingStatus.OVERDUE if late_days > 0 else BookingStatus.COMPLETED

    booking.return_time = return_time
    booking.total_estimated = pricing_service.compute_estimated_total(booking)
    booking.total_final = pricing_service.compute_final_total(booking)

    booking_repo.set_return_time(booking_id, _dt_to_iso(return_time))
    booking_repo.set_totals(booking_id, str(booking.total_estimated), str(booking.total_final))
    booking_repo.update_status(booking_id, new_status.value)

    if _is_car_available_today_after_return(booking.car_id, booking.id):
        car_repo.set_available_now(booking.car_id, True)

    _audit(admin_id, "return_car", "booking", booking_id, _json_detail({"late_days": late_days}))
    return _require_booking(booking_id)


def suggest_substitutions(booking_id: UUID) -> List[Car]:
    booking = _require_booking(booking_id)
    original_car = _require_car(booking.car_id)

    base_rate = original_car.daily_rate
    min_rate = base_rate * Decimal("0.90")
    max_rate = base_rate * Decimal("1.10")

    start_iso = booking.start_date.isoformat()
    end_iso = booking.end_date.isoformat()

    candidates: List[Car] = []
    for car in car_repo.list_available():
        if car.id == original_car.id:
            continue
        if _category_rank(car.category) < _category_rank(original_car.category):
            continue
        if car.daily_rate < min_rate or car.daily_rate > max_rate:
            continue
        if booking_repo.check_overlap(car.id, start_iso, end_iso):
            continue
        candidates.append(car)
    return candidates


def _require_user(user_id: UUID) -> User:
    user = user_repo.get_user_by_id(user_id)
    if user is None:
        raise ValueError("user not found")
    return user


def _require_car(car_id: UUID) -> Car:
    car = car_repo.get_by_id(car_id)
    if car is None:
        raise ValueError("car not found")
    return car


def _require_booking(booking_id: UUID) -> Booking:
    booking = booking_repo.get_by_id(booking_id)
    if booking is None:
        raise ValueError("booking not found")
    return booking


def _user_is_suspended(user: User) -> bool:
    value = user.status.value if hasattr(user.status, "value") else str(user.status)
    return value == UserStatus.SUSPENDED.value


def _car_status(car: Car) -> CarStatus:
    if isinstance(car.status, CarStatus):
        return car.status
    return CarStatus(str(car.status))


def _parse_insurance_plan(value: InsurancePlan | str) -> InsurancePlan:
    if isinstance(value, InsurancePlan):
        return value
    return InsurancePlan(str(value))


def _parse_date(value: date | str) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value))


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


def _ensure_utc_dt(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _dt_to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _category_rank(category: CarCategory) -> int:
    if isinstance(category, CarCategory):
        return _CATEGORY_RANK.get(category, 0)
    return _CATEGORY_RANK.get(CarCategory(str(category)), 0)


def _is_car_available_today_after_return(car_id: UUID, current_booking_id: UUID) -> bool:
    today = _today_utc()
    for booking in booking_repo.list_by_car(car_id):
        if booking.id == current_booking_id:
            continue
        status_value = booking.status.value if hasattr(booking.status, "value") else str(booking.status)
        if status_value not in (
            BookingStatus.APPROVED.value,
            BookingStatus.ACTIVE.value,
            BookingStatus.OVERDUE.value,
        ):
            continue
        if not (today < booking.start_date or today >= booking.end_date):
            return False
    return True


def _audit(actor_id: UUID, action: str, entity: str, entity_id: UUID, detail_json: str) -> None:
    if audit_repo is None:
        return
    audit_repo.log(actor_id, action, entity, entity_id, detail_json)


def _json_detail(data: Dict[str, Any]) -> str:
    try:
        import json

        return json.dumps(data, ensure_ascii=True)
    except Exception:
        return "{}"
