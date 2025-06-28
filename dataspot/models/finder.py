"""Models for finder (find method) response structures."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from .pattern import Pattern


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
