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
    """Options for automatic pattern discovery.

    Args:
        max_fields: Maximum fields per combination (1-5).
            Controls analysis complexity. Common: 3 (good balance), 2 (simple), 4 (complex).
        max_combinations: Maximum combinations to test (5-50).
            Limits computation time. Common: 10 (fast), 20 (balanced), 50 (thorough).
        min_percentage: Minimum concentration threshold (0.0-100.0).
            Filters weak patterns. Common: 5.0 (5%), 10.0 (10%), 20.0 (20%).
        max_percentage: Maximum concentration threshold (0.0-100.0).
            Excludes overly concentrated patterns. Rare usage.
        min_count: Minimum record count per pattern.
            Ensures statistical significance. Common: 2, 5, 10.
        max_count: Maximum record count per pattern.
            Excludes dominant patterns. Rare usage.
        min_depth: Minimum pattern depth (1+).
            Focuses on multi-field patterns. Example: 2 for combinations only.
        max_depth: Maximum pattern depth (1+).
            Controls analysis depth. Common: 3-4 to avoid over-segmentation.
        contains: Pattern must contain this text.
            Focuses on specific patterns. Example: "high_risk" for risk analysis.
        exclude: Pattern must NOT contain these texts.
            Removes unwanted patterns. Example: ["test", "demo"] for production.
        regex: Pattern must match this regex.
            Advanced pattern filtering. Example: "^(fraud|risk)" for security patterns.
        limit: Maximum patterns to return.
            Controls output size. Common: 10, 20, 50.
        sort_by: Sort field ('percentage', 'count', 'depth').
            Orders discovered patterns. Default: percentage.
        reverse: Sort descending.
            True=highest first, False=lowest first, None=auto.

    """

    max_fields: int = 3
    max_combinations: int = 10
    min_percentage: float = 10.0
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
