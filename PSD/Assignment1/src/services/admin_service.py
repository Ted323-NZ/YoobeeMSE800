"""Admin service functions."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.models.booking import Booking
from src.models.car import Car
from src.models.user import User
from src.repositories import booking_repo, car_repo
from src.services import auth_service, booking_service

# Admin-only wrappers that delegate to repos/services.


def add_car(admin_user: User, car: Car) -> Car:
    auth_service.require_admin(admin_user)
    return car_repo.add(car)


def update_car(admin_user: User, car: Car) -> None:
    auth_service.require_admin(admin_user)
    car_repo.update(car)


def set_car_status(admin_user: User, car_id: UUID, status: str) -> None:
    auth_service.require_admin(admin_user)
    car_repo.set_status(car_id, status)


def list_cars(admin_user: User) -> List[Car]:
    auth_service.require_admin(admin_user)
    return car_repo.list_all()


def list_available_cars(admin_user: User, location: Optional[str] = None) -> List[Car]:
    auth_service.require_admin(admin_user)
    return car_repo.list_available(location)


def list_pending_bookings(admin_user: User) -> List[Booking]:
    auth_service.require_admin(admin_user)
    return booking_repo.list_pending()


def approve_booking(admin_user: User, booking_id: UUID) -> Booking:
    auth_service.require_admin(admin_user)
    return booking_service.approve_booking(admin_user.id, booking_id)


def reject_booking(admin_user: User, booking_id: UUID, reason: str) -> Booking:
    auth_service.require_admin(admin_user)
    return booking_service.reject_booking(admin_user.id, booking_id, reason)


def pickup_booking(admin_user: User, booking_id: UUID) -> Booking:
    auth_service.require_admin(admin_user)
    return booking_service.pickup(admin_user.id, booking_id)


def return_booking(admin_user: User, booking_id: UUID, return_time_dt: datetime) -> Booking:
    auth_service.require_admin(admin_user)
    return booking_service.return_car(admin_user.id, booking_id, return_time_dt)
