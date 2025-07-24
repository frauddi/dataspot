"""Models for compare analyzer (compare method) response structures."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class CompareInput:
    """Input model for the compare() method."""

    current_data: List[Dict[str, Any]]  # Current period data
    baseline_data: List[Dict[str, Any]]  # Baseline period data for comparison
    fields: List[str]  # List of field names to analyze for changes
    query: Optional[Dict[str, Any]] = None  # Optional filters to apply to both datasets


@dataclass
class CompareOptions:
    """Options for temporal comparison analysis.

    Args:
        statistical_significance: Enable statistical significance testing.
            Calculates p-values and confidence intervals. Recommended for scientific analysis.
        change_threshold: Minimum relative change to consider significant (0.0-1.0).
            Common: 0.05 (5%), 0.15 (15%), 0.25 (25%). Higher = less sensitive.
        min_percentage: Minimum concentration threshold (0.0-100.0).
            Filters weak patterns before comparison. Common: 1.0 (1%), 5.0 (5%).
        max_percentage: Maximum concentration threshold (0.0-100.0).
            Excludes overly concentrated patterns. Rare usage.
        min_count: Minimum record count per pattern.
            Ensures statistical validity. Common: 2, 5, 10.
        max_count: Maximum record count per pattern.
            Excludes dominant patterns. Rare usage.
        min_depth: Minimum pattern depth (1+).
            Focuses on multi-field patterns. Example: 2 for combinations only.
        max_depth: Maximum pattern depth (1+).
            Controls comparison depth. Common: 3-4.
        contains: Pattern must contain this text.
            Focuses comparison on specific patterns. Example: "fraud" for fraud analysis.
        exclude: Pattern must NOT contain these texts.
            Removes patterns from comparison. Example: ["test", "demo"].
        regex: Pattern must match this regex.
            Advanced pattern filtering. Example: "^(high|critical)" for risk patterns.
        limit: Maximum patterns to return.
            Controls output size. Common: 20, 50, 100.
        sort_by: Sort field ('percentage', 'count', 'depth').
            Orders comparison results. Default: percentage.
        reverse: Sort descending.
            True=highest first, False=lowest first, None=auto.

    """

    statistical_significance: bool = False
    change_threshold: float = 0.15
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
class ChangeItem:
    """A single change detected in comparison analysis."""

    path: str  # Pattern path that changed
    current_count: int  # Count in current period
    baseline_count: int  # Count in baseline period
    count_change: int  # Absolute count difference
    count_change_percentage: float  # Percentage count change
    relative_change: float  # Relative change (-1 to +inf)
    current_percentage: float  # Current period percentage
    baseline_percentage: float  # Baseline period percentage
    percentage_change: float  # Absolute percentage point change
    status: str  # Change status (e.g., "NEW", "STABLE", "INCREASE")
    is_new: bool  # Whether pattern is new in current period
    is_disappeared: bool  # Whether pattern disappeared
    is_significant: bool  # Whether change exceeds threshold
    depth: int  # Pattern hierarchy depth
    statistical_significance: Dict[str, Any]  # Statistical analysis if enabled

    def to_dict(self) -> Dict[str, Any]:
        """Convert change item to dictionary."""
        return asdict(self)


@dataclass
class ComparisonStatistics:
    """Summary statistics for the comparison."""

    current_total: int  # Total records in current period
    baseline_total: int  # Total records in baseline period
    patterns_compared: int  # Number of patterns compared
    significant_changes: int  # Number of significant changes detected

    def to_dict(self) -> Dict[str, Any]:
        """Convert comparison statistics to dictionary."""
        return asdict(self)


@dataclass
class CompareOutput:
    """Response model for the compare() method.

    Based on current compare.py implementation that returns:
    {
        "changes": changes,
        **categorized_patterns,      # stable_patterns, new_patterns, etc.
        "statistics": {...},
        "fields_analyzed": fields,
        "change_threshold": change_threshold,
        "statistical_significance": statistical_significance,
    }
    """

    changes: List[ChangeItem]  # All pattern changes detected
    stable_patterns: List[ChangeItem]  # Patterns with minimal change
    new_patterns: List[ChangeItem]  # Patterns only in current data
    disappeared_patterns: List[ChangeItem]  # Patterns only in baseline data
    increased_patterns: List[ChangeItem]  # Patterns that increased significantly
    decreased_patterns: List[ChangeItem]  # Patterns that decreased significantly
    statistics: ComparisonStatistics  # Summary statistics
    fields_analyzed: List[str]  # Fields used in comparison
    change_threshold: float  # Threshold used for significance
    statistical_significance: bool  # Whether statistical tests were enabled

    def to_dict(self) -> Dict[str, Any]:
        """Convert compare response to dictionary."""
        return asdict(self)
