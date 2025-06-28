"""Models for analyzer (analyze method) response structures."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from .pattern import Pattern


@dataclass
class AnalyzeInput:
    """Input model for the analyze() method."""

    data: List[Dict[str, Any]]  # List of records to analyze
    fields: List[str]  # List of field names to analyze hierarchically
    query: Optional[Dict[str, Any]] = None  # Optional filters to apply to data


@dataclass
class AnalyzeOptions:
    """Options model for the analyze() method.

    Contains the same filtering and sorting options as FindOptions
    since analyze delegates to find internally.
    """

    min_percentage: float = 1.0  # Minimum concentration percentage threshold
    max_percentage: Optional[float] = None  # Maximum concentration percentage threshold
    min_count: Optional[int] = None  # Minimum record count per pattern
    max_count: Optional[int] = None  # Maximum record count per pattern
    min_depth: Optional[int] = None  # Minimum depth for patterns to be included
    max_depth: Optional[int] = None  # Maximum depth for patterns to be included
    contains: Optional[str] = None  # Pattern path must contain this text
    exclude: Optional[List[str]] = None  # Pattern path must NOT contain these texts
    regex: Optional[str] = None  # Pattern path must match this regex pattern
    limit: Optional[int] = None  # Maximum number of patterns to return
    sort_by: Optional[str] = None  # Field to sort by ('percentage', 'count', 'depth')
    reverse: Optional[bool] = None  # Sort order (None=auto, True=desc, False=asc)


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
