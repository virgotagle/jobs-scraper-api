"""FastAPI dependencies for API key authentication."""

from fastapi import Depends, Header
from fastapi.security import APIKeyHeader

from .database import get_repository
from .exceptions import UnauthorizedError
from .models import APIKeyModel
from .repositories import SQLiteRepository
from .security import verify_api_key

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    repository: SQLiteRepository = Depends(get_repository),
) -> APIKeyModel:
    """Validate and return API key from X-API-Key header."""
    if not x_api_key:
        raise UnauthorizedError("API key is required. Include X-API-Key header.")

    api_keys = repository.get_all_active_api_keys()

    for api_key_model in api_keys:
        if verify_api_key(x_api_key, str(api_key_model.key_hash)):
            repository.update_api_key_last_used(api_key_model.id.value)
            return api_key_model

    raise UnauthorizedError("Invalid API key")


def get_optional_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    repository: SQLiteRepository = Depends(get_repository),
) -> APIKeyModel | None:
    """Validate API key if provided, return None if missing or invalid."""
    if not x_api_key:
        return None

    try:
        return get_api_key(x_api_key, repository)
    except UnauthorizedError:
        return None
