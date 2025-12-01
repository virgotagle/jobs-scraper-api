"""Database dependency for FastAPI."""

from typing import Generator

from .repositories import SQLiteRepository

# Global repository instance
_repository: SQLiteRepository | None = None


def init_repository(db_url: str = "sqlite:///jobs.db") -> None:
    """Initialize the repository."""
    global _repository
    _repository = SQLiteRepository(db_url)


def get_repository() -> Generator[SQLiteRepository, None, None]:
    """Dependency to get repository instance."""
    if _repository is None:
        raise RuntimeError("Repository not initialized")
    yield _repository


def close_repository() -> None:
    """Close the repository connection."""
    global _repository
    if _repository:
        _repository.close()
        _repository = None
