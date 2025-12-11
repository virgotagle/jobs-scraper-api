from datetime import datetime
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from main import app
from src.core.database import get_repository
from src.core.models import JobDetailsModel, JobListingModel

client = TestClient(app)


def test_get_job_by_id_markdown_conversion():
    mock_repo = mock.Mock()

    # Setup mock job
    job = JobListingModel(
        job_id="test-job-id",
        title="Test Job",
        job_details_url="http://example.com",
        job_summary="Summary",
        company_name="Company",
        location="Location",
        country_code="US",
        listing_date=datetime.now(),
        salary_label="Salary",
        work_type="Full Time",
        job_classification="IT",
        job_sub_classification="Dev",
        work_arrangements="Remote",
    )
    job.details = JobDetailsModel(
        status="Active",
        is_expired=False,
        details="**Markdown Bold** and *Italic*",
        is_verified=True,
        expires_at=None,
    )

    # Configure mock
    mock_repo.get_job_by_id.return_value = job

    # Override dependency
    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        response = client.get("/jobs/test-job-id")
    finally:
        # Clear override
        app.dependency_overrides = {}

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-id"
    # Check if markdown is converted to HTML
    # The output should contain HTML tags
    print(data["details"])
    assert "<strong>Markdown Bold</strong>" in data["details"]
    assert "<em>Italic</em>" in data["details"]
