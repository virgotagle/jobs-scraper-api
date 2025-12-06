"""Integration tests for favorites endpoints."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app
from src.core.database import close_repository, init_repository
from src.core.security import generate_api_key, get_key_prefix, hash_api_key


@pytest.fixture
def client():
    """Create a TestClient instance."""
    return TestClient(app)


@pytest.fixture(scope="module")
def repository():
    """Initialize repository for tests."""
    db_path = Path("jobs.db")
    if not db_path.exists():
        pytest.skip("jobs.db not found - tests require actual database")

    repo = init_repository()
    yield repo
    close_repository()


@pytest.fixture(scope="module")
def api_key(repository):
    """Create a temporary API key for testing."""
    # Create unique email for test
    email = f"test_favorites_{generate_api_key()[:8]}@example.com"
    plain_key = generate_api_key()
    key_hash = hash_api_key(plain_key)

    # Create key in DB
    api_key_model = repository.create_api_key(
        key_hash=key_hash,
        key_prefix=get_key_prefix(plain_key),
        name="Test User",
        email=email,
    )

    yield plain_key

    # Cleanup
    repository.deactivate_api_key(api_key_model.id)


@pytest.fixture(scope="module")
def job_id(repository):
    """Get an existing job ID from the database."""
    jobs = repository.get_all_jobs(limit=1)
    if not jobs:
        pytest.skip("No jobs in database to favorite")
    return jobs[0].job_id


def test_favorites_lifecycle(client, api_key, job_id):
    """Test full favorites lifecycle: Add -> Status -> List -> Remove -> Status."""
    headers = {"X-API-Key": api_key}

    # 1. Add Favorite
    response = client.post(
        f"/favorites/{job_id}", headers=headers, json={"notes": "Integration test note"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["job_id"] == job_id
    assert data["notes"] == "Integration test note"

    # 2. Check Status (Should be true)
    response = client.get(f"/favorites/{job_id}/status", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_favorited"] is True
    assert response.json()["job_id"] == job_id

    # 3. List Favorites
    response = client.get("/favorites/", headers=headers)
    assert response.status_code == 200
    favorites = response.json()
    assert isinstance(favorites, list)
    # Check if our job is in the list
    found = any(
        f["job_id"] == job_id and f["notes"] == "Integration test note"
        for f in favorites
    )
    assert found, "Favorite job not found in list"

    # 4. Remove Favorite
    response = client.delete(f"/favorites/{job_id}", headers=headers)
    assert response.status_code == 200
    assert "removed" in response.json()["message"]

    # 5. Check Status (Should be false)
    response = client.get(f"/favorites/{job_id}/status", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_favorited"] is False


def test_favorites_validation(client, api_key, job_id):
    """Test validation and error cases."""
    headers = {"X-API-Key": api_key}

    # Test duplicate add (should be idempotent or handled gracefully)
    # The implementation returns existing if duplicate, so 201 or 200?
    # Spec says 201 even if existing in current implementation logic
    client.post(f"/favorites/{job_id}", headers=headers, json={})
    response = client.post(f"/favorites/{job_id}", headers=headers, json={})
    assert response.status_code == 201

    # Test remove non-existent from favorites
    client.delete(f"/favorites/{job_id}", headers=headers)  # Ensure removed
    response = client.delete(
        f"/favorites/{job_id}", headers=headers
    )  # Try remove again
    assert response.status_code == 404

    # Test add non-existent job
    response = client.post("/favorites/nonexistent_job_123", headers=headers, json={})
    assert response.status_code == 404


def test_favorites_unauthorized(client, job_id):
    """Test access without API key."""
    # No header
    response = client.get("/favorites/")
    assert response.status_code == 401

    # Invalid header
    response = client.get("/favorites/", headers={"X-API-Key": "invalid_key"})
    assert response.status_code == 401
