import os
import tempfile
import atexit

import pytest


db_fd, db_path = tempfile.mkstemp(prefix="prosite_tests_", suffix=".sqlite3")
os.close(db_fd)
os.environ.setdefault("DATABASE_URL", f"sqlite:///{db_path}")
os.environ.setdefault("FLASK_ENV", "development")

from server.app import create_app  # noqa: E402
from server.db import Base, SessionLocal, engine, session_scope  # noqa: E402
from server.models import Company, Project, ProjectMembership, ThirdPartyLab, User  # noqa: E402
from server.auth import hash_password, validate_email  # noqa: E402


def _cleanup_temp_db() -> None:
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass


atexit.register(_cleanup_temp_db)


@pytest.fixture(scope="module")
def app():
    application = create_app()
    application.config.update({"TESTING": True})
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    SessionLocal.remove()


def _create_quality_manager() -> dict:
    password = "Password123!"
    with session_scope() as session:
        company = Company(name="Test Company")
        session.add(company)
        session.flush()

        project = Project(
            company_id=company.id,
            name="Metro Expansion",
            project_code="PRJ-001",
        )
        session.add(project)
        session.flush()

        user = User(
            email="quality.manager@example.com",
            phone="9999999999",
            full_name="Quality Manager",
            password_hash=hash_password(password),
            company_id=company.id,
            is_active=1,
        )
        session.add(user)
        session.flush()

        membership = ProjectMembership(
            project_id=project.id,
            user_id=user.id,
            role="Quality Manager",
        )
        session.add(membership)
        session.flush()

        seeded = {
            "email": user.email,
            "password": password,
            "project_id": project.id,
            "company_id": company.id,
        }

    return seeded


def test_validate_email_rejects_invalid_format():
    is_valid, message = validate_email("invalid-email")
    assert not is_valid
    assert message == "Invalid email format"


def test_create_lab_success_response_and_persistence(client):
    seeded = _create_quality_manager()

    login_response = client.post(
        "/api/auth/login",
        json={"email": seeded["email"], "password": seeded["password"]},
    )
    assert login_response.status_code == 200

    access_token = login_response.get_json()["access_token"]

    payload = {
        "project_id": seeded["project_id"],
        "lab_name": "Acme Labs",
        "lab_code": "LAB-001",
        "contact_person": "Alex Johnson",
        "phone": "9123456780",
        "email": "alex.johnson@example.com",
        "address": "Industrial Zone",
        "city": "Mumbai",
        "state": "MH",
        "pincode": "400001",
        "nabl_accreditation_number": "NABL-789",
        "nabl_accreditation_valid_till": "2030-01-01T00:00:00",
        "scope_of_accreditation": "Concrete Testing",
    }

    response = client.post(
        "/api/third-party-labs",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert body["message"] == "Lab created successfully. Pending approval."

    lab_id = body["lab"]["id"]

    with session_scope() as session:
        lab = session.query(ThirdPartyLab).filter_by(id=lab_id).one()
        assert lab.lab_name == "Acme Labs"
        assert lab.company_id == seeded["company_id"]
        assert not lab.is_approved
