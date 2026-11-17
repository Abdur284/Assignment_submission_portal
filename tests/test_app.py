
import sqlite3
import pytest
import sys
from pathlib import Path

# Add the main project directory to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import app as portal


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_database = tmp_path / "test_submissions.db"

    monkeypatch.setattr(portal, "DATABASE", test_database)
    portal.app.config.update(TESTING=True)

    portal.initialize_database()

    with portal.app.test_client() as test_client:
        yield test_client


def count_saved_submissions():
    with sqlite3.connect(portal.DATABASE) as connection:
        result = connection.execute(
            "SELECT COUNT(*) FROM submissions"
        ).fetchone()
        return result[0]


def test_complete_details_and_valid_url_are_saved(client):
    response = client.post("/", data={
        "student_name": "Ali Ahmed",
        "registration_number": "FA22-BCS-001",
        "assignment_title": "DevOps Lab Assignment",
        "submission_url": "https://example.com/my-assignment"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"submitted successfully" in response.data
    assert b"Ali Ahmed" in response.data
    assert count_saved_submissions() == 1


def test_missing_registration_number_is_rejected(client):
    response = client.post("/", data={
        "student_name": "Ali Ahmed",
        "registration_number": "",
        "assignment_title": "DevOps Lab Assignment",
        "submission_url": "https://example.com/my-assignment"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"All fields are required" in response.data
    assert count_saved_submissions() == 0


def test_invalid_submission_url_is_rejected(client):
    response = client.post("/", data={
        "student_name": "Ali Ahmed",
        "registration_number": "FA22-BCS-001",
        "assignment_title": "DevOps Lab Assignment",
        "submission_url": "not-a-valid-url"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"valid HTTP or HTTPS submission URL" in response.data
    assert count_saved_submissions() == 0
