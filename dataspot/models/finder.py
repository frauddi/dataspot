"""Models for finder (find method) response structures."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from .pattern import Pattern


@dataclass
class FindInput:
    """Input model for the find() method."""

    data: List[Dict[str, Any]]  # List of records (dictionaries) to analyze
    fields: List[str]  # List of field names to analyze hierarchically
    query: Optional[Dict[str, Any]] = None  # Optional filters to apply to data

    def to_dict(self) -> Dict[str, Any]:
        """Convert find input to dictionary."""
        return asdict(self)


@dataclass
class FindOptions:
    """Options model for the find() method."""

    min_percentage: float = 1.0  # Minimum concentration threshold (default: 1.0)
    max_percentage: Optional[float] = None  # Maximum concentration threshold
    min_count: Optional[int] = None  # Minimum record count per pattern
    max_count: Optional[int] = None  # Maximum record count per pattern
    min_depth: Optional[int] = None  # Minimum depth for patterns to be included
    max_depth: Optional[int] = None  # Maximum depth for patterns to be included
    contains: Optional[str] = None  # Pattern path must contain this text
    exclude: Optional[List[str]] = None  # Pattern path must NOT contain these texts
    regex: Optional[str] = None  # Pattern path must match this regex pattern
    limit: Optional[int] = None  # Maximum number of patterns to return
    sort_by: Optional[str] = None  # Sort field: 'percentage', 'count', 'depth'
    reverse: Optional[bool] = (
        None  # Sort in descending order (True) or ascending (False)
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert find options to dictionary."""
        return asdict(self)

    def to_kwargs(self) -> Dict[str, Any]:
        """Convert to kwargs format, excluding None values."""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                result[key] = value
        return result

    def to_filter_kwargs(self) -> Dict[str, Any]:
        """Convert to kwargs format for filtering, excluding sorting options."""
        result = {}
        sorting_fields = {"sort_by", "reverse"}
        for key, value in asdict(self).items():
            if key not in sorting_fields and value is not None:
                result[key] = value
        return result


@dataclass
class FindOutput:
    """Response model for the find() method.

    Currently find() returns List[Pattern] directly, but this model
    provides a structured wrapper for future enhancements.
    """

    patterns: List[Pattern]  # List of found patterns sorted by percentage
    total_records: int  # Total number of records analyzed
    total_patterns: int  # Total number of patterns found

    # Future expansion fields:
    # fields_analyzed: List[str]     # Fields that were analyzed
    # query_applied: Dict[str, Any]  # Query filters that were applied
    # analysis_metadata: Dict[str, Any]  # Additional analysis info

    def to_dict(self) -> Dict[str, Any]:
        """Convert find response to dictionary."""
        return asdict(self)
