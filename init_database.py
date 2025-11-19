"""Utility script to rebuild and seed the local database."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import Dict, Iterable, List

from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

# Ensure all models are registered before touching metadata
import server.models  # noqa: F401
from server.db import Base, SessionLocal, engine, init_db, session_scope
from server.models import Company, MixDesign, Project, ProjectMembership, RMCVendor, User


DEFAULT_USERS: List[Dict[str, str]] = [
    {
        "email": "admin@prosite.com",
        "phone": "+1234567890",
        "full_name": "System Admin",
        "role": "system_admin",
        "password": "Admin@2025",
        "designation": "Head Office",
    },
    {
        "email": "pm@prosite.com",
        "phone": "+1234567891",
        "full_name": "Project Manager",
        "role": "project_manager",
        "password": "PM@2025",
        "designation": "Projects",
    },
    {
        "email": "qm@prosite.com",
        "phone": "+1234567892",
        "full_name": "Quality Manager",
        "role": "quality_manager",
        "password": "QM@2025",
        "designation": "Quality",
    },
    {
        "email": "sm@prosite.com",
        "phone": "+1234567893",
        "full_name": "Safety Manager",
        "role": "safety_manager",
        "password": "SM@2025",
        "designation": "Safety",
    },
    {
        "email": "qe@prosite.com",
        "phone": "+1234567894",
        "full_name": "Quality Engineer",
        "role": "quality_engineer",
        "password": "QE@2025",
        "designation": "Quality",
    },
    {
        "email": "se@prosite.com",
        "phone": "+1234567895",
        "full_name": "Safety Engineer",
        "role": "safety_engineer",
        "password": "SE@2025",
        "designation": "Safety",
    },
    {
        "email": "engineer@prosite.com",
        "phone": "+1234567896",
        "full_name": "Building Engineer",
        "role": "building_engineer",
        "password": "BE@2025",
        "designation": "Site",
    },
    {
        "email": "supervisor@prosite.com",
        "phone": "+1234567897",
        "full_name": "Contractor Supervisor",
        "role": "contractor_supervisor",
        "password": "CS@2025",
        "designation": "Contractor",
    },
    {
        "email": "watchman@prosite.com",
        "phone": "+1234567898",
        "full_name": "Security Guard",
        "role": "watchman",
        "password": "WM@2025",
        "designation": "Security",
    },
    {
        "email": "client@prosite.com",
        "phone": "+1234567899",
        "full_name": "Client Representative",
        "role": "client",
        "password": "Client@2025",
        "designation": "Client",
    },
    {
        "email": "auditor@prosite.com",
        "phone": "+1234567800",
        "full_name": "ISO Auditor",
        "role": "auditor",
        "password": "Auditor@2025",
        "designation": "Audit",
    },
    {
        "email": "supplier@prosite.com",
        "phone": "+1234567801",
        "full_name": "Material Supplier",
        "role": "supplier",
        "password": "Supplier@2025",
        "designation": "Supply",
    },
]

PROJECT_MEMBERSHIP_ROLES: Dict[str, str] = {
    "admin@prosite.com": "ProjectAdmin",
    "pm@prosite.com": "ProjectAdmin",
    "qm@prosite.com": "QualityManager",
    "sm@prosite.com": "SafetyManager",
    "qe@prosite.com": "QualityEngineer",
    "se@prosite.com": "SafetyEngineer",
    "engineer@prosite.com": "SiteEngineer",
    "supervisor@prosite.com": "DataEntry",
    "watchman@prosite.com": "Watchman",
    "client@prosite.com": "Viewer",
    "auditor@prosite.com": "Viewer",
    "supplier@prosite.com": "RMCVendor",
}

DEFAULT_VENDORS: List[Dict[str, str]] = [
    {
        "vendor_name": "Metro ReadyMix",
        "contact_person_name": "Ravi Kumar",
        "contact_phone": "+919900112233",
        "contact_email": "sales@metrormc.com",
        "address": "Plot 21, Industrial Estate, Pune",
        "license_number": "LIC-RMC-2025-001",
        "gstin": "27ABCDE1234F1Z5",
    },
    {
        "vendor_name": "Urban Concrete Supplies",
        "contact_person_name": "Sneha Patel",
        "contact_phone": "+919900445566",
        "contact_email": "support@urbanconcrete.in",
        "address": "24 Sector Road, Navi Mumbai",
        "license_number": "LIC-RMC-2025-014",
        "gstin": "27WXYZ5678L9Z3",
    },
]

DEFAULT_MIX_DESIGNS: List[Dict[str, object]] = [
    {
        "project_name": "Metro Viaduct",
        "mix_design_id": "MD-4500-A",
        "specified_strength_psi": 4500,
        "slump_inches": 4.5,
        "air_content_percent": 5.5,
        "batch_volume": 7.5,
        "volume_unit": "cubic_meters",
        "materials": "Cement: 420 kg\nFine Aggregate: 680 kg\nCoarse Aggregate: 1180 kg\nWater: 180 kg",
        "notes": "Pump mix for pier caps",
    },
    {
        "project_name": "Residential Tower",
        "mix_design_id": "MD-3500-B",
        "specified_strength_psi": 3500,
        "slump_inches": 3.5,
        "air_content_percent": 6.0,
        "batch_volume": 6.0,
        "volume_unit": "cubic_meters",
        "materials": "Cement: 380 kg\nFine Aggregate: 720 kg\nCoarse Aggregate: 1100 kg\nWater: 195 kg",
        "notes": "Standard floor slab mix",
    },
]


def drop_database() -> None:
    """Drop all tables from the configured database."""
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    SessionLocal.remove()
    print("[OK] Database cleared")


def create_database() -> None:
    """Create all tables defined in the ORM models."""
    print("Creating tables...")
    init_db()
    print("[OK] Tables created")


def seed_default_data() -> None:
    """Populate the database with baseline company, users, vendors, and mix designs."""
    print("Seeding reference data...")

    with session_scope() as session:
        company = Company(
            name="ProSite Demo Co",
            subscribed_modules='["safety", "concrete"]',
            subscription_plan="trial",
            subscription_start_date=datetime.utcnow(),
            company_email="info@prosite-demo.com",
            company_phone="+911234567890",
            company_address="901 Silicon Avenue, Mumbai",
        )
        session.add(company)
        session.flush()

        user_records: Dict[str, User] = {}
        for user_data in DEFAULT_USERS:
            if session.query(User).filter_by(email=user_data["email"]).first():
                continue

            flags = {
                "is_support_admin": 1 if user_data["email"] == "admin@prosite.com" else 0,
                "is_system_admin": 1 if user_data["email"] == "admin@prosite.com" else 0,
                "is_company_admin": 1 if user_data["email"] in {"admin@prosite.com", "pm@prosite.com"} else 0,
            }

            user = User(
                email=user_data["email"],
                phone=user_data["phone"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                password_hash=generate_password_hash(user_data["password"]),
                designation=user_data.get("designation"),
                company_id=company.id,
                is_active=1,
                is_email_verified=1,
                **flags,
            )
            session.add(user)
            session.flush()
            user_records[user.email] = user

        project = Project(
            company_id=company.id,
            name="ProSite Head Office",
            project_code="PRJ-2025-001",
            description="Reference project seeded for local testing",
            location="Mumbai",
            client_name="ProSite Demo Client",
            start_date=datetime.utcnow(),
        )
        session.add(project)
        session.flush()

        # Create project memberships so seeded users can access data immediately.
        for email, membership_role in PROJECT_MEMBERSHIP_ROLES.items():
            user = user_records.get(email)
            if not user:
                continue

            existing = (
                session.query(ProjectMembership)
                .filter_by(project_id=project.id, user_id=user.id)
                .first()
            )
            if existing:
                continue

            membership = ProjectMembership(
                project_id=project.id,
                user_id=user.id,
                role=membership_role,
                added_by=user_records["admin@prosite.com"].id if "admin@prosite.com" in user_records else None,
                can_manage_team=1 if membership_role in {"ProjectAdmin", "QualityManager", "SafetyManager"} else 0,
                can_generate_reports=1 if membership_role not in {"Watchman"} else 0,
                can_manage_settings=1 if membership_role == "ProjectAdmin" else 0,
                can_approve_batch=1 if membership_role in {"ProjectAdmin", "QualityManager"} else 0,
                can_approve_test=1 if membership_role in {"ProjectAdmin", "QualityManager"} else 0,
                can_create_batch=1 if membership_role not in {"Client", "Viewer"} else 0,
                can_edit_batch=1 if membership_role in {"ProjectAdmin", "QualityManager", "QualityEngineer", "SiteEngineer"} else 0,
                can_create_test=1 if membership_role in {"ProjectAdmin", "QualityManager", "QualityEngineer"} else 0,
                can_edit_test=1 if membership_role in {"ProjectAdmin", "QualityManager", "QualityEngineer"} else 0,
                can_delete_batch=1 if membership_role == "ProjectAdmin" else 0,
                can_delete_test=1 if membership_role == "ProjectAdmin" else 0,
            )
            session.add(membership)

        for vendor_data in DEFAULT_VENDORS:
            vendor = RMCVendor(
                company_id=company.id,
                project_id=project.id,
                vendor_name=vendor_data["vendor_name"],
                contact_person_name=vendor_data["contact_person_name"],
                contact_phone=vendor_data["contact_phone"],
                contact_email=vendor_data["contact_email"],
                address=vendor_data.get("address"),
                license_number=vendor_data.get("license_number"),
                gstin=vendor_data.get("gstin"),
                is_active=1,
                is_approved=1,
                created_by=user_records["admin@prosite.com"].id if "admin@prosite.com" in user_records else None,
                approved_by=user_records["qm@prosite.com"].id if "qm@prosite.com" in user_records else None,
                approved_at=datetime.utcnow(),
            )
            session.add(vendor)

        for mix_data in DEFAULT_MIX_DESIGNS:
            mix = MixDesign(**mix_data)
            session.add(mix)

    print("[OK] Seed data inserted")


def run_initialization(skip_reset: bool, no_seed: bool) -> None:
    if skip_reset:
        print("Skipping schema reset; ensuring tables exist...")
        init_db()
    else:
        drop_database()
        create_database()

    if not no_seed:
        seed_default_data()


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reset and seed the local database for the ProSite application.",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Run without confirmation prompt.",
    )
    parser.add_argument(
        "--skip-reset",
        action="store_true",
        help="Do not drop and recreate tables; only seed missing data.",
    )
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="Only reset schema without inserting sample data.",
    )
    return parser.parse_args(list(argv))


def confirm_proceed() -> bool:
    prompt = "This will DROP and recreate the database. Continue? [y/N]: "
    response = input(prompt).strip().lower()
    return response in {"y", "yes"}


def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)

    if not args.yes and not args.skip_reset:
        if not confirm_proceed():
            print("Aborted by user.")
            return 0

    try:
        run_initialization(skip_reset=args.skip_reset, no_seed=args.no_seed)
    except SQLAlchemyError as exc:
        print(f"Error while initializing database: {exc}")
        return 1
    except KeyboardInterrupt:
        print("Interrupted.")
        return 1

    print("Database initialization complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
