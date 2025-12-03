"""Repository for job and API key data access."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session, joinedload

from .exceptions import DatabaseError
from .models import APIKeyModel, Base, JobDetailsModel, JobListingModel


class SQLiteRepository:
    """Database repository for job listings, details, and API keys."""

    def __init__(self, db_url: str) -> None:
        """Initialize repository and create database tables."""
        self.db_url = db_url

        try:
            self.engine = create_engine(self.db_url)
            Base.metadata.create_all(self.engine)
        except Exception as e:
            logging.error(f"Failed to initialize database at {self.db_url}: {e}")
            raise DatabaseError(
                f"Failed to initialize database at {self.db_url}"
            ) from e

    def close(self):
        """Close database connection."""
        self.engine.dispose()

    def get_all_jobs(
        self,
        job_classification: Optional[str] = None,
        job_sub_classification: Optional[str] = None,
        work_arrangements: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobListingModel]:
        """Get job listings with optional filters and pagination."""
        with Session(self.engine) as session:
            query = session.query(JobListingModel)

            if job_classification:
                query = query.filter(
                    JobListingModel.job_classification == job_classification
                )

            if job_sub_classification:
                query = query.filter(
                    JobListingModel.job_sub_classification == job_sub_classification
                )

            if work_arrangements:
                query = query.filter(
                    JobListingModel.work_arrangements == work_arrangements
                )

            jobs = query.offset(skip).limit(limit).all()
            return jobs

    def get_job_by_id(self, job_id: str) -> Optional[JobListingModel]:
        """Get job listing with details by ID."""
        with Session(self.engine) as session:
            job = (
                session.query(JobListingModel)
                .filter(JobListingModel.job_id == job_id)
                .options(joinedload(JobListingModel.details))
                .first()
            )
            return job

    def get_all_job_classifications(self) -> list[str]:
        """Get all unique job classifications."""
        with Session(self.engine) as session:
            classifications = (
                session.query(JobListingModel.job_classification)
                .distinct()
                .filter(JobListingModel.job_classification.isnot(None))
                .all()
            )
            return [c[0] for c in classifications if c[0]]

    def get_all_work_arrangements(self) -> list[str]:
        """Get all unique work arrangements."""
        with Session(self.engine) as session:
            arrangements = (
                session.query(JobListingModel.work_arrangements)
                .distinct()
                .filter(JobListingModel.work_arrangements.isnot(None))
                .all()
            )
            return [a[0] for a in arrangements if a[0]]

    def get_all_job_sub_classifications(self) -> list[str]:
        """Get all unique job sub classifications."""
        with Session(self.engine) as session:
            sub_classifications = (
                session.query(JobListingModel.job_sub_classification)
                .distinct()
                .filter(JobListingModel.job_sub_classification.isnot(None))
                .all()
            )
            return [s[0] for s in sub_classifications if s[0]]

    def search_jobs(
        self,
        keyword: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobListingModel]:
        """Search jobs by keyword in title, summary, company, location, and details."""
        with Session(self.engine) as session:
            search_term = f"%{keyword}%"
            query = (
                session.query(JobListingModel)
                .outerjoin(JobDetailsModel)
                .filter(
                    or_(
                        JobListingModel.title.ilike(search_term),
                        JobListingModel.job_summary.ilike(search_term),
                        JobListingModel.company_name.ilike(search_term),
                        JobListingModel.location.ilike(search_term),
                        JobDetailsModel.details.ilike(search_term),
                    )
                )
            )
            jobs = query.offset(skip).limit(limit).all()
            return jobs

    def create_api_key(
        self,
        key_hash: str,
        key_prefix: str,
        name: str,
        email: str,
        company: str | None = None,
        rate_limit: int = 1000,
        expires_at: datetime | None = None,
    ) -> APIKeyModel:
        """Create and store a new API key."""
        with Session(self.engine) as session:
            api_key = APIKeyModel(
                key_hash=key_hash,
                key_prefix=key_prefix,
                name=name,
                email=email,
                company=company,
                rate_limit=rate_limit,
                expires_at=expires_at,
            )
            session.add(api_key)
            session.commit()
            session.refresh(api_key)
            return api_key

    def get_all_active_api_keys(self) -> list[APIKeyModel]:
        """Get all active API keys."""
        with Session(self.engine) as session:
            api_keys = session.query(APIKeyModel).filter(APIKeyModel.is_active).all()
            return api_keys

    def get_api_key_by_email(self, email: str) -> APIKeyModel | None:
        """Get active API key by email."""
        with Session(self.engine) as session:
            api_key = (
                session.query(APIKeyModel)
                .filter(APIKeyModel.email == email)
                .filter(APIKeyModel.is_active)
                .first()
            )
            return api_key

    def update_api_key_last_used(self, api_key_id: int) -> None:
        """Update last_used_at and increment request count."""
        with Session(self.engine) as session:
            api_key = (
                session.query(APIKeyModel).filter(APIKeyModel.id == api_key_id).first()
            )
            if api_key:
                session.query(APIKeyModel).filter(APIKeyModel.id == api_key_id).update(
                    {
                        APIKeyModel.last_used_at: datetime.now(timezone.utc),
                        APIKeyModel.request_count: APIKeyModel.request_count + 1,
                    }
                )
                session.commit()

    def get_all_api_keys(self) -> list[APIKeyModel]:
        """Get all API keys including inactive ones."""
        with Session(self.engine) as session:
            api_keys = session.query(APIKeyModel).all()
            return api_keys

    def deactivate_api_key(self, api_key_id: int) -> bool:
        """Deactivate API key by ID, return True if successful."""
        with Session(self.engine) as session:
            api_key = (
                session.query(APIKeyModel).filter(APIKeyModel.id == api_key_id).first()
            )
            if api_key:
                session.query(APIKeyModel).filter(APIKeyModel.id == api_key_id).update(
                    {APIKeyModel.is_active: False}
                )
                session.commit()
                return True
            return False
