"""Simple CLI for the car rental system."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence, Tuple
from uuid import UUID, uuid4
import traceback

from src.models.car import Car, CarCategory, CarStatus
from src.models.user import User
from src.repositories import booking_repo, car_repo, user_repo
from src.services import admin_service, auth_service, booking_service, pricing_service

# Predefined add-ons for demo input.
_ADDON_OPTIONS: List[Tuple[str, Decimal]] = [
    ("gps", Decimal("5.00")),
    ("child_seat", Decimal("3.50")),
    ("extra_driver", Decimal("7.00")),
    ("wifi", Decimal("4.00")),
]


_AUTH_SERVICE = None
if hasattr(auth_service, "AuthService"):
    try:
        _AUTH_SERVICE = auth_service.AuthService(user_repo)
    except Exception:
        _AUTH_SERVICE = None


def main() -> None:
    # Top-level menu loop.
    while True:
        print("\n=== Car Rental System ===")
        print("1) Customer")
        print("2) Admin")
        print("9) Exit")
        choice = input("Select: ").strip()
        if choice == "1":
            try:
                _customer_menu()
            except SystemExit:
                return
        elif choice == "2":
            try:
                _admin_menu()
            except SystemExit:
                return
        elif choice == "9":
            return
        else:
            _print_error("Invalid choice.")


def _customer_menu() -> None:
    current_user: Optional[User] = None
    while True:
        _print_session("Customer", current_user)
        print("1) Register")
        print("2) Login")
        print("3) List available cars")
        print("4) Create booking")
        print("5) View my bookings")
        print("0) Back")
        print("9) Exit")
        choice = input("Select: ").strip()
        if choice == "1":
            current_user = _handle_register()
        elif choice == "2":
            current_user = _handle_login(require_role="customer")
        elif choice == "3":
            _handle_list_available_cars()
        elif choice == "4":
            if current_user is None:
                _print_error("Please login first.")
                continue
            _handle_create_booking(current_user)
        elif choice == "5":
            if current_user is None:
                _print_error("Please login first.")
                continue
            _handle_view_bookings(current_user)
        elif choice == "0":
            return
        elif choice == "9":
            raise SystemExit
        else:
            _print_error("Invalid choice.")


def _admin_menu() -> None:
    admin_user: Optional[User] = None
    while True:
        _print_session("Admin", admin_user)
        print("1) Login")
        print("2) Add car")
        print("3) List cars")
        print("4) List pending bookings")
        print("5) Approve booking")
        print("6) Reject booking")
        print("0) Back")
        print("9) Exit")
        choice = input("Select: ").strip()
        if choice == "1":
            admin_user = _handle_login(require_role="admin")
        elif choice == "2":
            if admin_user is None:
                _print_error("Please login first.")
                continue
            _handle_add_car(admin_user)
        elif choice == "3":
            if admin_user is None:
                _print_error("Please login first.")
                continue
            _handle_list_cars(admin_user)
        elif choice == "4":
            if admin_user is None:
                _print_error("Please login first.")
                continue
            _handle_list_pending(admin_user)
        elif choice == "5":
            if admin_user is None:
                _print_error("Please login first.")
                continue
            _handle_approve_booking(admin_user)
        elif choice == "6":
            if admin_user is None:
                _print_error("Please login first.")
                continue
            _handle_reject_booking(admin_user)
        elif choice == "0":
            return
        elif choice == "9":
            raise SystemExit
        else:
            _print_error("Invalid choice.")


def _handle_register() -> Optional[User]:
    name = _input_text("Name: ")
    email = _input_email("Email: ")
    phone = _input_text("Phone (optional): ", allow_empty=True) or None
    license_no = _input_text("Driver license no: ")
    try:
        user = _auth_register_customer(name, email, phone, license_no)
        _print_success(f"Registered: {user.id}")
        return user
    except Exception as exc:
        _print_exception("Register failed", exc)
        return None


def _handle_login(require_role: str) -> Optional[User]:
    email = _input_email("Email: ")
    try:
        user = _auth_login_by_email(email)
        if require_role == "admin":
            _auth_require_admin(user)
        else:
            _auth_require_customer(user)
        _print_success(f"Logged in: {user.name}")
        return user
    except Exception as exc:
        _print_exception("Login failed", exc)
        return None


def _handle_list_available_cars() -> None:
    cars = car_repo.list_available()
    if not cars:
        _print_error("No available cars.")
        return
    _print_list("Available cars", cars, _format_car)


def _handle_create_booking(user: User) -> None:
    cars = car_repo.list_available()
    car = _select_from_list("Select a car", cars, _format_car)
    if car is None:
        return

    start_date, end_date = _input_booking_dates(car)
    insurance_plan = _input_choice(
        "Insurance plan", ["none", "basic", "premium"], default="none"
    )
    _print_addon_options()
    addons = _input_addons()

    try:
        booking = booking_service.create_booking(
            user.id, car.id, start_date, end_date, insurance_plan, addons
        )
        estimate = pricing_service.compute_estimated_total(booking)
        _print_success(f"Booking created: {booking.id}")
        print(f"Estimated total: {estimate}")
    except Exception as exc:
        _print_exception("Create booking failed", exc)


def _handle_view_bookings(user: User) -> None:
    bookings = booking_repo.list_by_user(user.id)
    if not bookings:
        _print_error("No bookings.")
        return
    booking = _select_from_list("My bookings", bookings, _format_booking)
    if booking is None:
        return
    _print_success("Booking details")
    print(_format_booking_detail(booking))


def _handle_add_car(admin_user: User) -> None:
    plate_no = _input_text("Plate no: ")
    make = _input_text("Make: ")
    model = _input_text("Model: ")
    year = _input_int("Year: ", min_value=1980, max_value=_current_year() + 1)
    mileage = _input_int("Mileage: ", min_value=0)
    category = _input_category()
    daily_rate = _input_decimal("Daily rate: ", min_value=Decimal("0.01"))
    deposit = _input_decimal("Deposit: ", min_value=Decimal("0.00"))
    min_rent_days = _input_int("Min rent days: ", min_value=1, max_value=30)
    max_rent_days = _input_int("Max rent days: ", min_value=min_rent_days, max_value=30)
    location = _input_text("Location [Auckland]: ", default="Auckland")

    car = Car(
        id=uuid4(),
        plate_no=plate_no,
        make=make,
        model=model,
        year=year,
        mileage=mileage,
        available_now=True,
        min_rent_days=min_rent_days,
        max_rent_days=max_rent_days,
        daily_rate=daily_rate,
        deposit=deposit,
        category=category,
        status=CarStatus.ACTIVE,
        location=location,
    )
    try:
        car.validate()
        admin_service.add_car(admin_user, car)
        _print_success(f"Car added: {car.id}")
    except Exception as exc:
        _print_exception("Add car failed", exc)


def _handle_list_cars(admin_user: User) -> None:
    cars = admin_service.list_cars(admin_user)
    if not cars:
        _print_error("No cars.")
        return
    _print_list("All cars", cars, _format_car)


def _handle_list_pending(admin_user: User) -> None:
    bookings = admin_service.list_pending_bookings(admin_user)
    if not bookings:
        _print_error("No pending bookings.")
        return
    _print_list("Pending bookings", bookings, _format_booking)


def _handle_approve_booking(admin_user: User) -> None:
    bookings = admin_service.list_pending_bookings(admin_user)
    booking = _select_from_list("Approve booking", bookings, _format_booking)
    if booking is None:
        return
    try:
        updated = admin_service.approve_booking(admin_user, booking.id)
        _print_success(f"Approved: {updated.id}")
    except Exception as exc:
        _print_exception("Approve failed", exc)


def _handle_reject_booking(admin_user: User) -> None:
    bookings = admin_service.list_pending_bookings(admin_user)
    booking = _select_from_list("Reject booking", bookings, _format_booking)
    if booking is None:
        return
    reason = _input_text("Reason [N/A]: ", default="N/A")
    try:
        updated = admin_service.reject_booking(admin_user, booking.id, reason)
        _print_success(f"Rejected: {updated.id}")
    except Exception as exc:
        _print_exception("Reject failed", exc)


def _auth_register_customer(name: str, email: str, phone: Optional[str], license_no: str) -> User:
    if _AUTH_SERVICE is not None and hasattr(_AUTH_SERVICE, "register_customer"):
        return _AUTH_SERVICE.register_customer(name, email, phone, license_no)
    if hasattr(auth_service, "register_customer"):
        return auth_service.register_customer(name, email, phone, license_no)
    raise AttributeError("Auth service not implemented: register_customer")


def _auth_login_by_email(email: str) -> User:
    if _AUTH_SERVICE is not None:
        if hasattr(_AUTH_SERVICE, "login_by_email"):
            return _AUTH_SERVICE.login_by_email(email)
        if hasattr(_AUTH_SERVICE, "login"):
            return _AUTH_SERVICE.login(email)
    if hasattr(auth_service, "login_by_email"):
        return auth_service.login_by_email(email)
    if hasattr(auth_service, "login"):
        return auth_service.login(email)
    raise AttributeError("Auth service not implemented: login")


def _auth_require_admin(user: User) -> None:
    if _AUTH_SERVICE is not None and hasattr(_AUTH_SERVICE, "require_admin"):
        _AUTH_SERVICE.require_admin(user)
        return
    if hasattr(auth_service, "require_admin"):
        auth_service.require_admin(user)
        return
    raise AttributeError("Auth service not implemented: require_admin")


def _auth_require_customer(user: User) -> None:
    if _AUTH_SERVICE is not None and hasattr(_AUTH_SERVICE, "require_customer"):
        _AUTH_SERVICE.require_customer(user)
        return
    if hasattr(auth_service, "require_customer"):
        auth_service.require_customer(user)
        return
    raise AttributeError("Auth service not implemented: require_customer")


def _input_booking_dates(car: Car) -> Tuple[date, date]:
    # Capture start date + rental days to match car-specific limits.
    while True:
        tomorrow = date.today() + timedelta(days=1)
        start_date = _input_date("Start date", default=tomorrow)
        if start_date < date.today():
            _print_error("Start date must be today or later.")
            continue
        min_days = max(1, car.min_rent_days)
        max_days = min(30, car.max_rent_days)
        rental_days = _input_int(
            f"Rental days ({min_days}-{max_days}): ",
            min_value=min_days,
            max_value=max_days,
        )
        end_date = start_date + timedelta(days=rental_days)
        return start_date, end_date


def _input_date(label: str, default: Optional[date] = None) -> date:
    while True:
        default_text = f" [{default.isoformat()}]" if default else ""
        text = input(f"{label} (YYYY-MM-DD){default_text}: ").strip()
        if not text and default is not None:
            return default
        if not text:
            _print_error("Date is required. Use YYYY-MM-DD.")
            continue
        try:
            return date.fromisoformat(text)
        except ValueError:
            _print_error("Invalid date format. Use YYYY-MM-DD.")


def _input_text(prompt: str, default: Optional[str] = None, allow_empty: bool = False) -> str:
    while True:
        text = input(prompt).strip()
        if text:
            return text
        if default is not None:
            return default
        if allow_empty:
            return ""
        _print_error("Input required.")


def _input_email(prompt: str) -> str:
    while True:
        text = _input_text(prompt)
        if _is_valid_email(text):
            return text
        _print_error("Invalid email format. Example: name@example.com")


def _input_choice(label: str, options: Sequence[str], default: Optional[str] = None) -> str:
    options_text = "/".join(options)
    default_text = f" [{default}]" if default else ""
    while True:
        text = input(f"{label} ({options_text}){default_text}: ").strip().lower()
        if not text and default is not None:
            return default
        if text in options:
            return text
        _print_error(f"Invalid choice. Options: {options_text}")


def _input_int(prompt: str, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
    while True:
        text = input(prompt).strip()
        if not text:
            _print_error("Input required.")
            continue
        try:
            value = int(text)
        except ValueError:
            _print_error("Invalid number.")
            continue
        if min_value is not None and value < min_value:
            _print_error(f"Value must be >= {min_value}.")
            continue
        if max_value is not None and value > max_value:
            _print_error(f"Value must be <= {max_value}.")
            continue
        return value


def _input_decimal(prompt: str, min_value: Optional[Decimal] = None) -> Decimal:
    while True:
        text = input(prompt).strip()
        if not text:
            _print_error("Input required.")
            continue
        try:
            value = Decimal(text)
        except Exception:
            _print_error("Invalid decimal.")
            continue
        if min_value is not None and value < min_value:
            _print_error(f"Value must be >= {min_value}.")
            continue
        return value


def _input_category() -> CarCategory:
    while True:
        text = input("Category (economy/compact/suv/luxury/van): ").strip().lower()
        if not text:
            _print_error("Input required.")
            continue
        try:
            return CarCategory(text)
        except Exception:
            _print_error("Invalid category.")


def _input_addons() -> Dict[str, str]:
    text = input(
        "Add-ons (numbers e.g. 1,3 or name:price; Enter to skip): "
    ).strip()
    if not text or text.lower() in {"blank", "none", "n"}:
        return {}
    result: Dict[str, str] = {}
    parts = [p.strip() for p in text.split(",") if p.strip()]
    for part in parts:
        if part.isdigit():
            idx = int(part)
            if idx < 1 or idx > len(_ADDON_OPTIONS):
                _print_error(f"Add-on selection out of range: {part}")
                continue
            name, price = _ADDON_OPTIONS[idx - 1]
            result[name] = str(price)
            continue
        if ":" in part:
            name, price = part.split(":", 1)
            try:
                Decimal(price.strip())
            except Exception:
                _print_error(f"Invalid add-on price: {price}")
                continue
            result[name.strip()] = price.strip()
            continue
        _print_error(f"Invalid add-on entry: {part}")
    return result


def _select_from_list(
    title: str, items: Sequence[Any], formatter: Any
) -> Optional[Any]:
    # Map user-friendly index to the actual object.
    if not items:
        _print_error("No items available.")
        return None
    _print_list(title, items, formatter)
    while True:
        text = input("Select # (0=Back, 9=Exit): ").strip()
        if text == "0":
            return None
        if text == "9":
            raise SystemExit
        if not text.isdigit():
            _print_error("Please enter a number.")
            continue
        idx = int(text)
        if idx < 1 or idx > len(items):
            _print_error("Selection out of range.")
            continue
        return items[idx - 1]


def _print_list(title: str, items: Sequence[Any], formatter: Any) -> None:
    print(f"\n{title}:")
    for idx, item in enumerate(items, 1):
        print(f"{idx}) {formatter(item)}")


def _print_addon_options() -> None:
    print("\nAvailable add-ons:")
    for idx, (name, price) in enumerate(_ADDON_OPTIONS, 1):
        print(f"{idx}) {name} (${price})")


def _print_session(label: str, user: Optional[User]) -> None:
    if user is None:
        print(f"\n--- {label} Menu (not logged in) ---")
    else:
        role = user.role.value if hasattr(user.role, "value") else str(user.role)
        print(f"\n--- {label} Menu (user: {user.name}, role: {role}) ---")


def _print_success(message: str) -> None:
    print(f"✅ {message}")


def _print_error(message: str) -> None:
    print(f"❌ {message}")


def _print_exception(message: str, exc: Exception) -> None:
    print(f"❌ {message}: {exc}")
    traceback.print_exc()


def _format_car(car: Car) -> str:
    return (
        f"{car.make} {car.model} | plate={car.plate_no} | "
        f"rate={car.daily_rate} | days={car.min_rent_days}-{car.max_rent_days} | "
        f"location={car.location} | available={car.available_now}"
    )


def _format_booking(booking: Any) -> str:
    status = booking.status.value if hasattr(booking.status, "value") else str(booking.status)
    return (
        f"car={booking.car_id} | {booking.start_date} -> {booking.end_date} | "
        f"status={status} | total={booking.total_estimated}"
    )


def _format_booking_detail(booking: Any) -> str:
    return (
        f"Booking ID: {booking.id}\n"
        f"Car ID: {booking.car_id}\n"
        f"Dates: {booking.start_date} -> {booking.end_date}\n"
        f"Status: {booking.status}\n"
        f"Estimated: {booking.total_estimated}\n"
        f"Final: {booking.total_final}\n"
    )


def _is_valid_email(email: str) -> bool:
    if "@" not in email:
        return False
    local, _, domain = email.partition("@")
    if not local or not domain:
        return False
    if "." not in domain:
        return False
    return True


def _current_year() -> int:
    return date.today().year


if __name__ == "__main__":
    main()
