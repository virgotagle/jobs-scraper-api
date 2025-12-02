"""Job Scrapers API - FastAPI application for job listings."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.database import close_repository, init_repository
from src.core.exceptions import DatabaseError, InvalidInputError, JobNotFoundError
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


# Exception handlers
@app.exception_handler(JobNotFoundError)
async def job_not_found_handler(
    request: Request, exc: JobNotFoundError
) -> JSONResponse:
    """Handle job not found errors."""
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(InvalidInputError)
async def invalid_input_handler(
    request: Request, exc: InvalidInputError
) -> JSONResponse:
    """Handle invalid input errors."""
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """Handle database errors."""
    return JSONResponse(
        status_code=500,
        content={"error": "A database error occurred. Please try again later."},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors with user-friendly messages."""
    errors = []
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown"
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=422, content={"error": "Validation error", "details": errors}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred. Please try again later."},
    )


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Job Scrapers API", "version": "1.0.0"}
