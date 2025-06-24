"""Custom exceptions for Dataspot."""


class DataspotError(Exception):
    """Base exception for all Dataspot errors."""

    pass


class ValidationError(DataspotError):
    """Raised when input validation fails."""

    pass


class DataError(DataspotError):
    """Raised when data processing encounters errors."""

    pass


class QueryError(DataspotError):
    """Raised when query parameters are invalid."""

    pass


class ConfigurationError(DataspotError):
    """Raised when configuration is invalid."""

    pass
