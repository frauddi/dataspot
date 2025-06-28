"""Models for discovery analyzer (discover method) response structures."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from .pattern import Pattern


@dataclass
class DiscoverInput:
    """Input model for the discover() method."""

    data: List[Dict[str, Any]]  # List of records (dictionaries) to analyze
    query: Optional[Dict[str, Any]] = None  # Optional filters to apply to data


@dataclass
class DiscoverOptions:
    """Options model for the discover() method."""

    max_fields: int = 3  # Maximum number of fields to combine (default: 3)
    max_combinations: int = 10  # Maximum combinations to try (default: 10)
    min_percentage: float = 10.0  # Minimum concentration to consider (default: 10%)
    # Additional filtering options (same as find method)
    max_percentage: Optional[float] = None  # Maximum concentration percentage threshold
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


@dataclass
class FieldRanking:
    """Field importance ranking information."""

    field: str  # Field name
    score: float  # Calculated importance score

    def to_dict(self) -> Dict[str, Any]:
        """Convert field ranking to dictionary."""
        return asdict(self)


@dataclass
class CombinationTried:
    """Information about a field combination that was tried."""

    fields: List[str]  # Fields in this combination
    patterns_found: int  # Number of patterns found

    def to_dict(self) -> Dict[str, Any]:
        """Convert combination tried to dictionary."""
        return asdict(self)


@dataclass
class DiscoveryStatistics:
    """Statistics for discovery analysis."""

    total_records: int  # Total records analyzed
    fields_analyzed: int  # Number of fields analyzed
    combinations_tried: int  # Number of field combinations attempted
    patterns_discovered: int  # Number of patterns found
    best_concentration: float  # Highest concentration percentage found

    def to_dict(self) -> Dict[str, Any]:
        """Convert discovery statistics to dictionary."""
        return asdict(self)


@dataclass
class DiscoverOutput:
    """Response model for the discover() method.

    Based on current discovery.py implementation that returns:
    {
        "top_patterns": top_patterns[:20],
        "field_ranking": field_scores,           # List[Tuple[str, float]] -> List[FieldRanking]
        "combinations_tried": combinations_tried, # List[Dict[str, Any]] -> List[CombinationTried]
        "statistics": {...},
        "fields_analyzed": available_fields,
    }
    """

    top_patterns: List[Pattern]  # Best patterns found (top 20)
    field_ranking: List[FieldRanking]  # Fields ranked by importance score
    combinations_tried: List[CombinationTried]  # Field combinations that were tested
    statistics: DiscoveryStatistics  # Analysis statistics
    fields_analyzed: List[str]  # Fields that were available for analysis

    def to_dict(self) -> Dict[str, Any]:
        """Convert discover response to dictionary."""
        return asdict(self)
