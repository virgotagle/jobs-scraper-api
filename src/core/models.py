"""Database models for job listings, details, and API keys."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class JobListingModel(Base):
    """Job listing information from job sites."""

    __tablename__ = "job_listings"

    job_id = Column(String, primary_key=True)
    title = Column(String)
    job_details_url = Column(String)
    job_summary = Column(Text)
    company_name = Column(String)
    location = Column(String)
    country_code = Column(String)
    listing_date = Column(DateTime)
    salary_label = Column(String, nullable=True)
    work_type = Column(String, nullable=True)
    job_classification = Column(String, nullable=True)
    job_sub_classification = Column(String, nullable=True)
    work_arrangements = Column(String, nullable=True)

    # Relationship to JobDetailsModel
    details = relationship("JobDetailsModel", back_populates="listing")


class JobDetailsModel(Base):
    """Detailed job information and metadata."""

    __tablename__ = "job_details"

    job_id = Column(String, ForeignKey("job_listings.job_id"), primary_key=True)
    status = Column(String)
    is_expired = Column(Boolean)
    details = Column(Text)
    is_verified = Column(Boolean, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationship back to JobListingModel
    listing = relationship("JobListingModel", back_populates="details")


class APIKeyModel(Base):
    """API key for authentication and authorization."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key_hash = Column(String, unique=True, nullable=False, index=True)
    key_prefix = Column(String(12), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    company = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    rate_limit = Column(Integer, default=1000, nullable=False)
    request_count = Column(Integer, default=0, nullable=False)
