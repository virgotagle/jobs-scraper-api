"""Simple repository tests."""

import pytest

from src.core.repositories import SQLiteRepository


@pytest.fixture
def test_repository():
    """Create a test repository with in-memory database."""
    repo = SQLiteRepository(db_url="sqlite:///:memory:")
    yield repo
    repo.close()


def test_repository_initialization(test_repository):
    """Test repository initializes successfully."""
    assert test_repository is not None
    assert test_repository.engine is not None


def test_get_all_jobs_empty(test_repository):
    """Test getting all jobs from empty database."""
    jobs = test_repository.get_all_jobs()
    assert jobs == []


def test_get_job_by_id_not_found(test_repository):
    """Test getting non-existent job returns None."""
    job = test_repository.get_job_by_id("nonexistent-id")
    assert job is None


def test_get_all_job_classifications_empty(test_repository):
    """Test getting classifications from empty database."""
    classifications = test_repository.get_all_job_classifications()
    assert classifications == []


def test_get_all_work_arrangements_empty(test_repository):
    """Test getting work arrangements from empty database."""
    arrangements = test_repository.get_all_work_arrangements()
    assert arrangements == []


def test_search_jobs_empty(test_repository):
    """Test searching in empty database."""
    jobs = test_repository.search_jobs(keyword="test")
    assert jobs == []
