from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class JobListingSchema(BaseModel):
    """Job listing data schema."""

    job_id: str
    title: str
    job_details_url: str
    job_summary: str
    company_name: str
    location: str
    country_code: str
    listing_date: datetime
    salary_label: Optional[str] = None
    work_type: Optional[str] = None
    job_classification: Optional[str] = None
    job_sub_classification: Optional[str] = None
    work_arrangements: Optional[str] = None


class JobDetailsSchema(BaseModel):
    """Job details and metadata schema."""

    job_id: str
    status: str
    is_expired: bool
    details: str
    is_verified: Optional[bool] = None
    expires_at: Optional[datetime] = None


class JobListingResponse(BaseModel):
    """Job listing response schema."""

    model_config = ConfigDict(from_attributes=True)

    job_id: str
    title: str
    job_details_url: str
    job_summary: str
    company_name: str
    location: str
    country_code: str
    listing_date: datetime
    salary_label: Optional[str] = None
    work_type: Optional[str] = None
    job_classification: Optional[str] = None
    job_sub_classification: Optional[str] = None
    work_arrangements: Optional[str] = None


class JobWithDetailsResponse(BaseModel):
    """Job listing with full details response schema."""

    model_config = ConfigDict(from_attributes=True)

    job_id: str
    title: str
    job_details_url: str
    job_summary: str
    company_name: str
    location: str
    country_code: str
    listing_date: datetime
    salary_label: Optional[str] = None
    work_type: Optional[str] = None
    job_classification: Optional[str] = None
    job_sub_classification: Optional[str] = None
    work_arrangements: Optional[str] = None
    status: Optional[str] = None
    is_expired: Optional[bool] = None
    details: Optional[str] = None
    is_verified: Optional[bool] = None
    expires_at: Optional[datetime] = None


class FavoriteJobCreate(BaseModel):
    """Schema for creating a favorite job."""

    notes: Optional[str] = None


class FavoriteJobResponse(BaseModel):
    """Favorite job response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: str
    created_at: datetime
    notes: Optional[str] = None
    job: JobListingResponse


class FavoriteStatusResponse(BaseModel):
    """Response schema for checking if a job is favorited."""

    job_id: str
    is_favorited: bool
