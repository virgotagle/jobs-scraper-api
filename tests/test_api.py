"""Simple API endpoint tests using the actual jobs.db database."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app
from src.core.database import close_repository, init_repository


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Initialize database before tests and cleanup after."""
    db_path = Path("jobs.db")
    if not db_path.exists():
        pytest.skip("jobs.db not found - tests require actual database")

    init_repository()
    yield
    close_repository()


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Job Scrapers API", "version": "1.0.0"}


def test_get_all_jobs():
    """Test getting all jobs returns 200."""
    response = client.get("/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_jobs_with_pagination():
    """Test jobs endpoint with pagination parameters."""
    response = client.get("/jobs/?skip=0&limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_job_classifications():
    """Test getting job classifications."""
    response = client.get("/jobs/classifications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_work_arrangements():
    """Test getting work arrangements."""
    response = client.get("/jobs/work-arrangements")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_job_sub_classifications():
    """Test getting job sub classifications."""
    response = client.get("/jobs/sub-classifications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_jobs():
    """Test search endpoint with keyword."""
    response = client.get("/jobs/search?keyword=developer")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_job_by_id_not_found():
    """Test getting non-existent job returns 404."""
    response = client.get("/jobs/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
