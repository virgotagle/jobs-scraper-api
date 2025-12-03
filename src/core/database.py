"""Database repository initialization and FastAPI dependency."""

from typing import Generator

from .config import settings
from .exceptions import DatabaseError
from .repositories import SQLiteRepository

# Global repository instance
_repository: SQLiteRepository | None = None


def init_repository() -> SQLiteRepository:
    """Initialize and return global repository instance."""
    global _repository
    _repository = SQLiteRepository(settings.database_url)
    return _repository


def get_repository() -> Generator[SQLiteRepository, None, None]:
    """FastAPI dependency for repository injection."""
    if _repository is None:
        raise DatabaseError(
            "Repository not initialized. Application startup may have failed."
        )
    yield _repository


def close_repository() -> None:
    """Close repository and cleanup global instance."""
    global _repository
    if _repository:
        _repository.close()
        _repository = None
