"""Application entry point."""

from __future__ import annotations

from uuid import uuid4

from src.models.user import User, UserRole, UserStatus
from src.repositories import user_repo
from src.repositories.sqlite_base import init_db
from src.ui import cli


_DEFAULT_ADMIN_EMAIL = "admin@example.com"
_DEFAULT_ADMIN_NAME = "Admin"


def main() -> None:
    # Bootstraps database and default admin, then runs CLI loop.
    init_db()
    _ensure_default_admin()
    cli.main()


def _ensure_default_admin() -> None:
    existing = user_repo.get_user_by_email(_DEFAULT_ADMIN_EMAIL)
    if existing is not None:
        return
    admin = User(
        id=uuid4(),
        role=UserRole.ADMIN,
        name=_DEFAULT_ADMIN_NAME,
        email=_DEFAULT_ADMIN_EMAIL,
        phone=None,
        driver_license_no=None,
        status=UserStatus.ACTIVE,
    )
    admin.validate()
    user_repo.create_user(admin)
    print("Default admin created:")
    print(f"  email: {_DEFAULT_ADMIN_EMAIL}")


if __name__ == "__main__":
    main()
