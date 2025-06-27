"""Compare analyzer for temporal/segmental data comparison with advanced features."""

from typing import Any, Dict, List, Optional

from ..models import Pattern
from .base import Base
from .stats import Stats


class Compare(Base):
    """Compares datasets to detect changes and anomalies between periods with advanced analytics."""

    def __init__(self):
        """Initialize Compare analyzer with statistical methods."""
        super().__init__()
        self.statistical_methods = Stats()

    def execute(
        self,
        current_data: List[Dict[str, Any]],
        baseline_data: List[Dict[str, Any]],
        fields: List[str],
        statistical_significance: bool = True,
        change_threshold: float = 0.15,
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Compare current data against baseline to detect changes with advanced analytics.

        Args:
            current_data: Current period data
            baseline_data: Baseline period data for comparison
            fields: Fields to analyze for changes
            statistical_significance: Calculate p-values and confidence intervals
            change_threshold: Threshold for significant changes (0.15 = 15%)
            query: Optional filters to apply to both datasets
            **kwargs: Additional filtering options

        Returns:
            Dictionary with comprehensive comparison results, changes, and alerts

        """
        # Validate input data
        self._validate_data(current_data)
        self._validate_data(baseline_data)

        # Apply query filters if provided
        if query:
            current_data = self._filter_data_by_query(current_data, query)
            baseline_data = self._filter_data_by_query(baseline_data, query)

        # Get patterns for both datasets
        current_patterns = self._get_patterns(current_data, fields, **kwargs)
        baseline_patterns = self._get_patterns(baseline_data, fields, **kwargs)

        # Compare patterns and detect changes
        changes = self._compare_patterns(
            current_patterns,
            baseline_patterns,
            statistical_significance=statistical_significance,
            change_threshold=change_threshold,
        )

        # Categorize patterns
        categorized_patterns = self._categorize_patterns(changes)

        result = {
            "changes": changes,
            **categorized_patterns,
            "statistics": {
                "current_total": len(current_data),
                "baseline_total": len(baseline_data),
                "patterns_compared": len(changes),
                "significant_changes": len([c for c in changes if c["is_significant"]]),
            },
            "fields_analyzed": fields,
            "change_threshold": change_threshold,
            "statistical_significance": statistical_significance,
        }

        return result

    def _get_patterns(
        self, data: List[Dict[str, Any]], fields: List[str], **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """Extract patterns from data."""
        from .finder import Finder

        finder = Finder()
        finder.preprocessors = self.preprocessors

        patterns: List[Pattern] = finder.execute(data, fields, **kwargs)

        # Convert to dictionary for easier comparison
        pattern_dict = {}
        for pattern in patterns:
            pattern_dict[pattern.path] = {
                "count": pattern.count,
                "percentage": pattern.percentage,
                "samples": pattern.samples,
                "depth": pattern.depth,
            }

        return pattern_dict

    def _compare_patterns(
        self,
        current_patterns: Dict[str, Dict[str, Any]],
        baseline_patterns: Dict[str, Dict[str, Any]],
        statistical_significance: bool = False,
        change_threshold: float = 0.15,
    ) -> List[Dict[str, Any]]:
        """Compare current patterns against baseline with advanced metrics."""
        changes = []

        # Get all unique pattern paths
        all_paths = set(current_patterns.keys()) | set(baseline_patterns.keys())

        for path in all_paths:
            current = current_patterns.get(
                path, {"count": 0, "percentage": 0.0, "samples": []}
            )
            baseline = baseline_patterns.get(
                path, {"count": 0, "percentage": 0.0, "samples": []}
            )

            # Calculate changes
            count_change = current["count"] - baseline["count"]

            if baseline["count"] > 0:
                count_change_pct = (count_change / baseline["count"]) * 100
                relative_change = (
                    count_change / baseline["count"]
                )  # For threshold comparison
            else:
                count_change_pct = float("inf") if current["count"] > 0 else 0.0
                relative_change = float("inf") if current["count"] > 0 else 0.0

            percentage_change = current["percentage"] - baseline["percentage"]

            # Statistical significance if requested
            stats = {}
            if (
                statistical_significance
                and baseline["count"] > 0
                and current["count"] > 0
            ):
                stats = self.statistical_methods.perform_comprehensive_analysis(
                    current["count"], baseline["count"]
                )

            # Determine significance based on threshold
            is_significant = (
                abs(relative_change) >= change_threshold
                if relative_change != float("inf")
                else current["count"] > 5  # For new patterns
            )

            change_info = {
                "path": path,
                "current_count": current["count"],
                "baseline_count": baseline["count"],
                "count_change": count_change,
                "count_change_percentage": count_change_pct,
                "relative_change": relative_change,
                "current_percentage": current["percentage"],
                "baseline_percentage": baseline["percentage"],
                "percentage_change": percentage_change,
                "status": self._get_change_status(count_change_pct),
                "is_new": path not in baseline_patterns,
                "is_disappeared": path not in current_patterns,
                "is_significant": is_significant,
                "depth": current.get("depth", baseline.get("depth", 1)),
                "statistical_significance": stats,
            }

            changes.append(change_info)

        # Sort by significance and magnitude
        changes.sort(
            key=lambda x: (
                x["is_significant"],
                abs(x["count_change_percentage"])
                if x["count_change_percentage"] != float("inf")
                else 1000,
            ),
            reverse=True,
        )

        return changes

    def _get_change_status(self, change_pct: float) -> str:
        """Determine status based on change percentage."""
        if change_pct == float("inf"):
            return "NEW"

        # Status thresholds ordered from highest to lowest
        status_thresholds = [
            (200, "CRITICAL_INCREASE"),
            (100, "SIGNIFICANT_INCREASE"),
            (50, "INCREASE"),
            (15, "SLIGHT_INCREASE"),
            (-15, "STABLE"),
            (-50, "SLIGHT_DECREASE"),
            (-80, "DECREASE"),
            (-100, "CRITICAL_DECREASE"),
        ]

        for threshold, status in status_thresholds:
            if change_pct >= threshold:
                return status

        return "DISAPPEARED"

    def _categorize_patterns(
        self, changes: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize patterns into different buckets for better organization."""
        stable_patterns = [c for c in changes if c["status"] == "STABLE"]
        new_patterns = [c for c in changes if c["is_new"]]
        disappeared_patterns = [c for c in changes if c["is_disappeared"]]
        increased_patterns = [c for c in changes if "INCREASE" in c["status"]]
        decreased_patterns = [c for c in changes if "DECREASE" in c["status"]]

        return {
            "stable_patterns": stable_patterns,
            "new_patterns": new_patterns,
            "disappeared_patterns": disappeared_patterns,
            "increased_patterns": increased_patterns,
            "decreased_patterns": decreased_patterns,
        }
