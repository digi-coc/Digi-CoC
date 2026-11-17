import argparse
import getpass
import sys

from sqlalchemy import select

from app.core.security import hash_password
from app.database.connections import SessionLocal
from app.models.organisations import Organization
from app.models.personnel import Personnel


def main():
    parser = argparse.ArgumentParser(
        description="Set a password for an existing Digi-CoC personnel account."
    )

    parser.add_argument("--organization-code", required=True)
    parser.add_argument("--personnel-code", required=True)

    args = parser.parse_args()

    password = getpass.getpass("New password (minimum 12 characters): ")
    confirmation = getpass.getpass("Confirm password: ")

    if password != confirmation:
        print("Error: passwords do not match.")
        sys.exit(1)

    try:
        password_hash = hash_password(password)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    with SessionLocal() as db:
        organization = db.scalar(
            select(Organization).where(
                Organization.organization_code == args.organization_code.strip()
            )
        )

        if organization is None:
            print("Error: organization not found.")
            sys.exit(1)

        personnel = db.scalar(
            select(Personnel).where(
                Personnel.organization_id == organization.id,
                Personnel.personnel_code == args.personnel_code.strip(),
            )
        )

        if personnel is None:
            print("Error: personnel record not found.")
            sys.exit(1)

        if not personnel.is_active:
            print("Error: personnel account is inactive.")
            sys.exit(1)

        personnel.password_hash = password_hash

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

    print("Password successfully configured.")


if __name__ == "__main__":
    main()