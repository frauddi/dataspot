"""Models for discovery analyzer (discover method) response structures."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from .pattern import Pattern


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
