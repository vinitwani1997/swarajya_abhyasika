"""
Standalone script to create an admin user.

Usage:
    python -m scripts.create_admin
    python -m scripts.create_admin --name "John Admin" --email john@library.com --password Secret123

Run from the project root (where alembic.ini lives), with the venv activated.
If --email/--password are not provided, falls back to ADMIN_EMAIL /
ADMIN_PASSWORD / ADMIN_FULL_NAME from .env.
"""

import argparse
import sys

from app.config import settings
from app.core.enums import RoleEnum, UserStatusEnum
from app.database import SessionLocal
from app.models.user import User
from app.services.security import generate_user_id, hash_password


def create_admin(full_name: str, email: str, password: str) -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            if not existing.user_id or not existing.hashed_password:
                existing.user_id = existing.user_id or generate_user_id(existing.id)
                existing.hashed_password = hash_password(password)
                existing.role = RoleEnum.admin
                existing.status = UserStatusEnum.active
                db.commit()
                print("Repaired incomplete admin record:")
                print(f"  Email:     {existing.email}")
                print(f"  User ID:   {existing.user_id}")
                print(f"  Password:  {password}")
                return

            print(f"User with email '{email}' already exists (user_id={existing.user_id}, "
                  f"role={existing.role.value}, status={existing.status.value}).")
            sys.exit(1)

        admin_user = User(
            full_name=full_name,
            email=email,
            role=RoleEnum.admin,
            status=UserStatusEnum.active,
            hashed_password=hash_password(password),
        )
        db.add(admin_user)
        db.flush()  # assigns admin_user.id without committing

        admin_user.user_id = generate_user_id(admin_user.id)
        db.commit()

        print("Admin created successfully:")
        print(f"  Full Name: {admin_user.full_name}")
        print(f"  Email:     {admin_user.email}")
        print(f"  User ID:   {admin_user.user_id}")
        print(f"  Password:  {password}")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an admin user.")
    parser.add_argument("--name", default=settings.ADMIN_FULL_NAME, help="Admin full name")
    parser.add_argument("--email", default=settings.ADMIN_EMAIL, help="Admin email")
    parser.add_argument("--password", default=settings.ADMIN_PASSWORD, help="Admin password")
    args = parser.parse_args()

    create_admin(full_name=args.name, email=args.email, password=args.password)


if __name__ == "__main__":
    main()
