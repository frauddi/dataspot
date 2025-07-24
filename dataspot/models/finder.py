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
    """Options for pattern finding analysis.

    Args:
        min_percentage: Minimum concentration threshold (0.0-100.0).
            Filters out patterns below this percentage. Common: 1.0 (1%), 5.0 (5%).
        max_percentage: Maximum concentration threshold (0.0-100.0).
            Filters out patterns above this percentage. Useful to exclude 100% patterns.
        min_count: Minimum record count per pattern.
            Patterns with fewer records are excluded. Common: 2, 5, 10.
        max_count: Maximum record count per pattern.
            Patterns with more records are excluded. Rare but useful for outliers.
        min_depth: Minimum pattern depth (1+).
            Only includes patterns at this depth or deeper. Example: 2 for multi-field patterns.
        max_depth: Maximum pattern depth (1+).
            Limits analysis to this depth. Example: 3 to avoid over-segmentation.
        contains: Pattern path must contain this text.
            Case-sensitive string filter. Example: "fraud" matches ["country", "fraud", "high"].
        exclude: Pattern path must NOT contain these texts.
            List of strings to exclude. Example: ["test", "demo"] for production analysis.
        regex: Pattern path must match this regex.
            Advanced filtering with regex. Example: "^(US|UK)" for patterns starting with US or UK.
        limit: Maximum number of patterns to return.
            Caps results for performance. Common: 10, 50, 100.
        sort_by: Sort field ('percentage', 'count', 'depth').
            Orders results by chosen metric. Default: percentage.
        reverse: Sort in descending order.
            True=highest first, False=lowest first, None=auto (descending for percentage).

    """

    min_percentage: float = 1.0
    max_percentage: Optional[float] = None
    min_count: Optional[int] = None
    max_count: Optional[int] = None
    min_depth: Optional[int] = None
    max_depth: Optional[int] = None
    contains: Optional[str] = None
    exclude: Optional[List[str]] = None
    regex: Optional[str] = None
    limit: Optional[int] = None
    sort_by: Optional[str] = None
    reverse: Optional[bool] = None

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
