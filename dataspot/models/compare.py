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
    """Options model for the compare() method."""

    statistical_significance: bool = (
        False  # Calculate p-values and confidence intervals
    )
    change_threshold: float = 0.15  # Threshold for significant changes (0.15 = 15%)
    # Additional filtering options (same as find method)
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
    sort_by: Optional[str] = None  # Sort field: 'percentage', 'count', 'depth'
    reverse: Optional[bool] = (
        None  # Sort in descending order (True) or ascending (False)
    )


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
