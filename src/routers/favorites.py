"""Favorite jobs endpoints."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from ..core.auth import get_api_key
from ..core.database import get_repository
from ..core.exceptions import InvalidInputError, JobNotFoundError
from ..core.models import APIKeyModel
from ..core.repositories import SQLiteRepository
from ..core.schemas import (
    FavoriteJobCreate,
    FavoriteJobResponse,
    FavoriteStatusResponse,
)

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post(
    "/{job_id}", response_model=FavoriteJobResponse, status_code=status.HTTP_201_CREATED
)
def add_favorite_job(
    job_id: str,
    favorite_data: FavoriteJobCreate,
    api_key: APIKeyModel = Depends(get_api_key),
    repository: SQLiteRepository = Depends(get_repository),
) -> FavoriteJobResponse:
    """Add a job to user's favorites."""
    # Check if job exists
    job = repository.get_job_by_id(job_id)
    if not job:
        raise JobNotFoundError(f"Job with ID '{job_id}' not found")

    # Add to favorites
    favorite = repository.add_favorite_job(
        api_key_id=api_key.id,
        job_id=job_id,
        notes=favorite_data.notes,
    )

    return FavoriteJobResponse.model_validate(favorite)


@router.delete("/{job_id}", status_code=status.HTTP_200_OK)
def remove_favorite_job(
    job_id: str,
    api_key: APIKeyModel = Depends(get_api_key),
    repository: SQLiteRepository = Depends(get_repository),
) -> JSONResponse:
    """Remove a job from user's favorites."""
    removed = repository.remove_favorite_job(api_key_id=api_key.id, job_id=job_id)

    if not removed:
        raise JobNotFoundError(f"Job with ID '{job_id}' not found in your favorites")

    return JSONResponse(
        content={"message": f"Job '{job_id}' removed from favorites"},
        status_code=status.HTTP_200_OK,
    )


@router.get("/", response_model=list[FavoriteJobResponse])
def get_favorite_jobs(
    skip: int = 0,
    limit: int = 100,
    api_key: APIKeyModel = Depends(get_api_key),
    repository: SQLiteRepository = Depends(get_repository),
) -> list[FavoriteJobResponse]:
    """Get all favorite jobs for the authenticated user."""
    if skip < 0:
        raise InvalidInputError("skip must be a non-negative integer")
    if limit < 1 or limit > 1000:
        raise InvalidInputError("limit must be between 1 and 1000")

    favorites = repository.get_favorite_jobs(
        api_key_id=api_key.id, skip=skip, limit=limit
    )

    return [FavoriteJobResponse.model_validate(fav) for fav in favorites]


@router.get("/{job_id}/status", response_model=FavoriteStatusResponse)
def check_favorite_status(
    job_id: str,
    api_key: APIKeyModel = Depends(get_api_key),
    repository: SQLiteRepository = Depends(get_repository),
) -> FavoriteStatusResponse:
    """Check if a specific job is in user's favorites."""
    is_favorited = repository.is_job_favorited(api_key_id=api_key.id, job_id=job_id)

    return FavoriteStatusResponse(job_id=job_id, is_favorited=is_favorited)
