"""Job Scrapers API - FastAPI application for job listings."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.database import close_repository, init_repository
from src.routers import jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    init_repository()
    yield
    # Shutdown
    close_repository()


app = FastAPI(
    title="Job Scrapers API",
    description="API for accessing job listings from various job sites",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(jobs.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Job Scrapers API", "version": "1.0.0"}
