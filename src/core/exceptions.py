"""Custom exception classes for the Jobs API."""


class JobNotFoundError(Exception):
    """Raised when a requested job is not found."""

    pass


class DatabaseError(Exception):
    """Raised when a database operation fails."""

    pass


class InvalidInputError(Exception):
    """Raised when business logic validation fails."""

    pass
