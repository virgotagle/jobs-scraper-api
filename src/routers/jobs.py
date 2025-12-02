"""API routes for job listings."""

from typing import Optional

from fastapi import APIRouter, Depends

from ..core.database import get_repository
from ..core.exceptions import InvalidInputError, JobNotFoundError
from ..core.repositories import SQLiteRepository
from ..core.schemas import JobListingResponse, JobWithDetailsResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobListingResponse])
def get_all_jobs(
    job_classification: Optional[str] = None,
    job_sub_classification: Optional[str] = None,
    work_arrangements: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    repository: SQLiteRepository = Depends(get_repository),
) -> list[JobListingResponse]:
    """Get all job listings with optional filters."""
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


@router.get("/classifications", response_model=list[str])
def get_job_classifications(
    repository: SQLiteRepository = Depends(get_repository),
) -> list[str]:
    """Get all unique job classifications."""
    return repository.get_all_job_classifications()


@router.get("/work-arrangements", response_model=list[str])
def get_work_arrangements(
    repository: SQLiteRepository = Depends(get_repository),
) -> list[str]:
    """Get all unique work arrangements."""
    return repository.get_all_work_arrangements()


@router.get("/sub-classifications", response_model=list[str])
def get_job_sub_classifications(
    repository: SQLiteRepository = Depends(get_repository),
) -> list[str]:
    """Get all unique job sub classifications."""
    return repository.get_all_job_sub_classifications()


@router.get("/search", response_model=list[JobListingResponse])
def search_jobs(
    keyword: str,
    skip: int = 0,
    limit: int = 100,
    repository: SQLiteRepository = Depends(get_repository),
) -> list[JobListingResponse]:
    """Search jobs by keyword across title, summary, company, location, and details."""
    if not keyword or len(keyword.strip()) < 2:
        raise InvalidInputError("Search keyword must be at least 2 characters long")
    if skip < 0:
        raise InvalidInputError("skip must be a non-negative integer")
    if limit < 1 or limit > 1000:
        raise InvalidInputError("limit must be between 1 and 1000")

    jobs = repository.search_jobs(keyword=keyword, skip=skip, limit=limit)
    return [JobListingResponse.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobWithDetailsResponse)
def get_job_by_id(
    job_id: str,
    repository: SQLiteRepository = Depends(get_repository),
) -> JobWithDetailsResponse:
    """Get a specific job listing with full details."""
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
