"""Authentication and authorization helpers."""

from __future__ import annotations

from typing import Optional
from uuid import uuid4

from src.models.user import User, UserRole, UserStatus
from src.repositories import user_repo


def _repo_create_user(repo: object, user: User) -> None:
    if hasattr(repo, "create_user"):
        repo.create_user(user)  # type: ignore[attr-defined]
        return
    if hasattr(repo, "create"):
        repo.create(user)  # type: ignore[attr-defined]
        return
    raise AttributeError("user_repo missing create_user")


def _repo_get_by_email(repo: object, email: str) -> Optional[User]:
    if hasattr(repo, "get_user_by_email"):
        return repo.get_user_by_email(email)  # type: ignore[attr-defined]
    if hasattr(repo, "get_by_email"):
        return repo.get_by_email(email)  # type: ignore[attr-defined]
    raise AttributeError("user_repo missing get_user_by_email")


class AuthService:
    """Auth service using the current user_repo interface."""

    def __init__(self, repo: object = user_repo) -> None:
        self._repo = repo

    def register_customer(
        self, name: str, email: str, phone: Optional[str], driver_license_no: str
    ) -> User:
        # Simple email-based registration (no password in MVP).
        user = User(
            id=uuid4(),
            role=UserRole.CUSTOMER,
            name=name,
            email=email,
            phone=phone,
            driver_license_no=driver_license_no,
            status=UserStatus.ACTIVE,
        )
        user.validate()
        _repo_create_user(self._repo, user)
        return user

    def login_by_email(self, email: str) -> User:
        # Email-only login for demo purposes.
        user = _repo_get_by_email(self._repo, email)
        if user is None:
            raise ValueError("user not found")
        return user

    def require_admin(self, user: User) -> None:
        if _role_value(user) != UserRole.ADMIN.value:
            raise ValueError("admin required")

    def require_customer(self, user: User) -> None:
        if _role_value(user) != UserRole.CUSTOMER.value:
            raise ValueError("customer required")


_DEFAULT_AUTH = AuthService(user_repo)


def register_customer(name: str, email: str, phone: Optional[str], driver_license_no: str) -> User:
    return _DEFAULT_AUTH.register_customer(name, email, phone, driver_license_no)


def login_by_email(email: str) -> User:
    return _DEFAULT_AUTH.login_by_email(email)


def require_admin(user: User) -> None:
    _DEFAULT_AUTH.require_admin(user)


def require_customer(user: User) -> None:
    _DEFAULT_AUTH.require_customer(user)


def _role_value(user: User) -> str:
    value = user.role.value if hasattr(user.role, "value") else str(user.role)
    return value
