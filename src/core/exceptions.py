"""Custom exceptions for API error handling."""


class JobNotFoundError(Exception):
    """Raised when a requested job is not found."""

    pass


class DatabaseError(Exception):
    """Raised when a database operation fails."""

    pass


class InvalidInputError(Exception):
    """Raised when business logic validation fails."""

    pass


class UnauthorizedError(Exception):
    """Raised when API key authentication fails."""

    pass
