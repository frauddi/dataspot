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
    """Options for comprehensive data analysis.

    Args:
        min_percentage: Minimum concentration threshold (0.0-100.0).
            Filters out weak patterns. Common: 1.0 (1%), 5.0 (5%), 10.0 (10%).
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
            Focuses analysis on specific patterns. Example: "high_value" for revenue analysis.
        exclude: Pattern must NOT contain these texts.
            Removes unwanted patterns. Example: ["test", "demo"] for production analysis.
        regex: Pattern must match this regex.
            Advanced filtering. Example: "^(premium|gold)" for customer analysis.
        limit: Maximum patterns to return.
            Controls output size. Common: 20, 50, 100.
        sort_by: Sort field ('percentage', 'count', 'depth').
            Orders analysis results. Default: percentage.
        reverse: Sort descending.
            True=highest first, False=lowest first, None=auto.

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
