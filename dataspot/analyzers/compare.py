"""Compare analyzer for temporal/segmental data comparison with advanced features."""

from typing import Any, Dict, List

from ..models.compare import (
    ChangeItem,
    CompareInput,
    CompareOptions,
    CompareOutput,
    ComparisonStatistics,
)
from ..models.finder import FindInput, FindOptions
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
        input: CompareInput,
        options: CompareOptions,
    ) -> CompareOutput:
        """Compare current data against baseline to detect changes with advanced analytics.

        Args:
            input: CompareInput containing current data, baseline data, fields, and optional query
            options: CompareOptions containing statistical and filtering parameters

        Returns:
            CompareOutput dataclass with comprehensive comparison results, changes, and alerts

        """
        # Validate input data
        self._validate_data(input.current_data)
        self._validate_data(input.baseline_data)

        current_data = input.current_data
        baseline_data = input.baseline_data

        # Apply query filters if provided
        if input.query:
            current_data = self._filter_data_by_query(current_data, input.query)
            baseline_data = self._filter_data_by_query(baseline_data, input.query)

        # Get patterns for both datasets
        current_patterns = self._get_patterns(current_data, input.fields, options)
        baseline_patterns = self._get_patterns(baseline_data, input.fields, options)

        # Compare patterns and detect changes
        changes_data = self._compare_patterns(
            current_patterns,
            baseline_patterns,
            statistical_significance=options.statistical_significance,
            change_threshold=options.change_threshold,
        )

        # Convert changes to ChangeItem dataclasses
        changes = [self._dict_to_change_item(change) for change in changes_data]

        # Categorize patterns
        categorized_patterns = self._categorize_patterns(changes_data)

        # Convert categorized patterns to ChangeItem dataclasses
        stable_patterns = [
            self._dict_to_change_item(item)
            for item in categorized_patterns["stable_patterns"]
        ]
        new_patterns = [
            self._dict_to_change_item(item)
            for item in categorized_patterns["new_patterns"]
        ]
        disappeared_patterns = [
            self._dict_to_change_item(item)
            for item in categorized_patterns["disappeared_patterns"]
        ]
        increased_patterns = [
            self._dict_to_change_item(item)
            for item in categorized_patterns["increased_patterns"]
        ]
        decreased_patterns = [
            self._dict_to_change_item(item)
            for item in categorized_patterns["decreased_patterns"]
        ]

        # Create ComparisonStatistics dataclass
        statistics = ComparisonStatistics(
            current_total=len(input.current_data),
            baseline_total=len(input.baseline_data),
            patterns_compared=len(changes),
            significant_changes=len([c for c in changes_data if c["is_significant"]]),
        )

        return CompareOutput(
            changes=changes,
            stable_patterns=stable_patterns,
            new_patterns=new_patterns,
            disappeared_patterns=disappeared_patterns,
            increased_patterns=increased_patterns,
            decreased_patterns=decreased_patterns,
            statistics=statistics,
            fields_analyzed=input.fields,
            change_threshold=options.change_threshold,
            statistical_significance=options.statistical_significance,
        )

    def _dict_to_change_item(self, change_dict: Dict[str, Any]) -> ChangeItem:
        """Convert a change dictionary to ChangeItem dataclass."""
        return ChangeItem(
            path=change_dict["path"],
            current_count=change_dict["current_count"],
            baseline_count=change_dict["baseline_count"],
            count_change=change_dict["count_change"],
            count_change_percentage=change_dict["count_change_percentage"],
            relative_change=change_dict["relative_change"],
            current_percentage=change_dict["current_percentage"],
            baseline_percentage=change_dict["baseline_percentage"],
            percentage_change=change_dict["percentage_change"],
            status=change_dict["status"],
            is_new=change_dict["is_new"],
            is_disappeared=change_dict["is_disappeared"],
            is_significant=change_dict["is_significant"],
            depth=change_dict["depth"],
            statistical_significance=change_dict["statistical_significance"],
        )

    def _get_patterns(
        self, data: List[Dict[str, Any]], fields: List[str], options: CompareOptions
    ) -> Dict[str, Dict[str, Any]]:
        """Extract patterns from data."""
        from .finder import Finder

        finder = Finder()
        finder.preprocessors = self.preprocessors

        find_input = FindInput(data=data, fields=fields)
        find_options = FindOptions(
            min_percentage=options.min_percentage,
            max_percentage=options.max_percentage,
            min_count=options.min_count,
            max_count=options.max_count,
            min_depth=options.min_depth,
            max_depth=options.max_depth,
            contains=options.contains,
            exclude=options.exclude,
            regex=options.regex,
            limit=options.limit,
            sort_by=options.sort_by,
            reverse=options.reverse,
        )
        patterns = finder.execute(find_input, find_options)

        # Convert to dictionary for easier comparison
        pattern_dict = {}
        for pattern in patterns.patterns:
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
