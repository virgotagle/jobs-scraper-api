"""Job listing endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends

from src.core.auth import get_api_key
from src.core.config import settings
from src.core.database import get_repository
from src.core.exceptions import InvalidInputError, JobNotFoundError
from src.core.repositories import SQLiteRepository
from src.core.schemas import (
    JobListingResponse,
    JobStatsResponse,
    JobWithDetailsResponse,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


# Conditional API key dependency
def optional_api_key() -> list:
    """Return API key dependency list if authentication is required."""
    if settings.require_api_key:
        return [Depends(get_api_key)]
    return []


@router.get(
    "/", response_model=list[JobListingResponse], dependencies=optional_api_key()
)
def get_all_jobs(
    job_classification: Optional[str] = None,
    job_sub_classification: Optional[str] = None,
    work_arrangements: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    repository: SQLiteRepository = Depends(get_repository),
) -> list[JobListingResponse]:
    """Get job listings with optional filters and pagination."""
    if skip < 0:
        raise InvalidInputError("skip must be a non-negative integer")
    if limit < 1 or limit > 1000:
        raise InvalidInputError("limit must be between 1 and 1000")

    jobs = repository.get_all_jobs(
        job_classification=job_classification,
        job_sub_classification=job_sub_classification,
        work_arrangements=work_arrangements,
        skip=skip,
        limit=limit,
    )
    return [JobListingResponse.model_validate(job) for job in jobs]


@router.get(
    "/classifications", response_model=list[str], dependencies=optional_api_key()
)
def get_job_classifications(
    repository: SQLiteRepository = Depends(get_repository),
) -> list[str]:
    """Get all unique job classifications."""
    return repository.get_all_job_classifications()


@router.get(
    "/work-arrangements", response_model=list[str], dependencies=optional_api_key()
)
def get_work_arrangements(
    repository: SQLiteRepository = Depends(get_repository),
) -> list[str]:
    """Get all unique work arrangements."""
    return repository.get_all_work_arrangements()


@router.get(
    "/sub-classifications", response_model=list[str], dependencies=optional_api_key()
)
def get_job_sub_classifications(
    repository: SQLiteRepository = Depends(get_repository),
) -> list[str]:
    """Get all unique job sub classifications."""
    return repository.get_all_job_sub_classifications()


@router.get(
    "/search", response_model=list[JobListingResponse], dependencies=optional_api_key()
)
def search_jobs(
    keyword: str,
    skip: int = 0,
    limit: int = 100,
    repository: SQLiteRepository = Depends(get_repository),
) -> list[JobListingResponse]:
    """Search jobs by keyword in multiple fields."""
    if not keyword or len(keyword.strip()) < 2:
        raise InvalidInputError("Search keyword must be at least 2 characters long")
    if skip < 0:
        raise InvalidInputError("skip must be a non-negative integer")
    if limit < 1 or limit > 1000:
        raise InvalidInputError("limit must be between 1 and 1000")

    jobs = repository.search_jobs(keyword=keyword, skip=skip, limit=limit)
    return [JobListingResponse.model_validate(job) for job in jobs]


@router.get("/stats", response_model=JobStatsResponse, dependencies=optional_api_key())
def get_job_stats(
    repository: SQLiteRepository = Depends(get_repository),
) -> JobStatsResponse:
    """Get job system statistics."""
    stats = repository.get_job_stats()
    return JobStatsResponse(**stats)


@router.get(
    "/{job_id}", response_model=JobWithDetailsResponse, dependencies=optional_api_key()
)
def get_job_by_id(
    job_id: str,
    repository: SQLiteRepository = Depends(get_repository),
) -> JobWithDetailsResponse:
    """Get job listing with full details by ID."""
    job = repository.get_job_by_id(job_id)

    if not job:
        raise JobNotFoundError(f"Job with ID '{job_id}' not found")

    # Combine listing and details data
    job_data = {
        "job_id": job.job_id,
        "title": job.title,
        "job_details_url": job.job_details_url,
        "job_summary": job.job_summary,
        "company_name": job.company_name,
        "location": job.location,
        "country_code": job.country_code,
        "listing_date": job.listing_date,
        "salary_label": job.salary_label,
        "work_type": job.work_type,
        "job_classification": job.job_classification,
        "job_sub_classification": job.job_sub_classification,
        "work_arrangements": job.work_arrangements,
    }

    # Add details if available
    if job.details:
        job_data.update(
            {
                "status": job.details.status,
                "is_expired": job.details.is_expired,
                "details": job.details.details,
                "is_verified": job.details.is_verified,
                "expires_at": job.details.expires_at,
            }
        )

    return JobWithDetailsResponse(**job_data)
