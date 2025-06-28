"""Models for compare analyzer (compare method) response structures."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


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
