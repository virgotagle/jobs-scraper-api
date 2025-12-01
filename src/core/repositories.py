"""SQLite repository for job data storage."""

import logging
from typing import Optional

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session, joinedload

from .models import Base, JobDetailsModel, JobListingModel
from .schemas import JobDetailsSchema, JobListingSchema


class SQLiteRepository:
    """SQLite database repository for job listings and details."""

    def __init__(self, db_url: str = "sqlite:///jobs.db") -> None:
        """Initialize repository with database connection."""
        self.db_url = db_url

        try:
            self.engine = create_engine(self.db_url)
            Base.metadata.create_all(self.engine)
        except Exception as e:
            logging.error(f"Failed to initialize database at {self.db_url}: {e}")
            raise RuntimeError(f"Failed to initialize database: {e}") from e

    def close(self):
        """Close database connection and clean up resources."""
        self.engine.dispose()

    def get_all_jobs(
        self,
        job_classification: Optional[str] = None,
        job_sub_classification: Optional[str] = None,
        work_arrangements: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobListingModel]:
        """Fetch all job listings with optional filters and pagination."""
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
        """Fetch a single job listing with its details."""
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
        """Search jobs by keyword across multiple fields including details."""
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
