"""Models for analyzer (analyze method) response structures."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from .pattern import Pattern


@dataclass
class Statistics:
    """Statistical analysis results."""

    total_records: int  # Total number of records in dataset
    filtered_records: int  # Number of records after filtering
    filter_ratio: float  # Percentage of records kept after filtering
    patterns_found: int  # Number of patterns discovered
    max_concentration: float  # Highest concentration percentage found
    avg_concentration: float  # Average concentration percentage

    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary."""
        return asdict(self)


@dataclass
class Insights:
    """Analysis insights and discoveries."""

    patterns_found: int  # Number of patterns discovered
    max_concentration: float  # Maximum concentration found
    avg_concentration: float  # Average concentration
    concentration_distribution: str  # Description of concentration distribution

    def to_dict(self) -> Dict[str, Any]:
        """Convert insights to dictionary."""
        return asdict(self)


@dataclass
class AnalyzeOutput:
    """Response model for the analyze() method.

    Based on current analyzer.py implementation that returns:
    {
        "patterns": patterns,
        "insights": insights,
        "statistics": {...},
        "field_stats": field_stats,
        "top_patterns": patterns[:5],
        "fields_analyzed": fields,
    }
    """

    patterns: List[Pattern]  # All found patterns
    insights: Insights  # Analysis insights
    statistics: Statistics  # Statistical summary
    field_stats: Dict[str, Any]  # Field distribution statistics
    top_patterns: List[Pattern]  # Top 5 patterns by percentage
    fields_analyzed: List[str]  # Fields that were analyzed

    def to_dict(self) -> Dict[str, Any]:
        """Convert analyze response to dictionary."""
        return asdict(self)
