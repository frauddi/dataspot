"""Pattern filtering functionality for dataspot analyzers."""

import re
from typing import Any, Dict, List

from ..exceptions import DataspotError
from ..models.pattern import Pattern


class PatternFilter:
    """Clean, efficient pattern filtering with fluent interface."""

    def __init__(self, patterns: List[Pattern]):
        """Initialize filter with patterns to process."""
        self.patterns = patterns

    def apply_all(self, **kwargs) -> List[Pattern]:
        """Apply all filters and return final results.

        Args:
            **kwargs: Filter parameters

        Returns:
            Filtered and sorted patterns

        """
        filtered = self.patterns
        filtered = self._apply_numeric_filters(filtered, **kwargs)
        filtered = self._apply_text_filters(filtered, **kwargs)
        filtered = self._apply_limit(filtered, **kwargs)

        # Sort by percentage (highest first)
        return sorted(filtered, key=lambda p: p.percentage, reverse=True)

    def _apply_numeric_filters(
        self, patterns: List[Pattern], **kwargs
    ) -> List[Pattern]:
        """Apply numeric filters (percentage, count, depth).

        Args:
            patterns: Patterns to filter
            **kwargs: Filter parameters

        Returns:
            Filtered patterns

        """
        # Define filter mappings for clean processing
        numeric_filters = [
            ("min_percentage", "percentage", ">="),
            ("max_percentage", "percentage", "<="),
            ("min_count", "count", ">="),
            ("max_count", "count", "<="),
            ("min_depth", "depth", ">="),
            ("max_depth", "depth", "<="),
        ]

        filtered = patterns
        for filter_name, attr, operator in numeric_filters:
            if filter_name in kwargs:
                value = kwargs[filter_name]
                filtered = self._apply_numeric_filter(filtered, attr, operator, value)

        return filtered

    def _apply_numeric_filter(
        self, patterns: List[Pattern], attr: str, operator: str, value: float
    ) -> List[Pattern]:
        """Apply a single numeric filter.

        Args:
            patterns: Patterns to filter
            attr: Attribute name to filter on
            operator: Comparison operator (>=, <=)
            value: Threshold value

        Returns:
            Filtered patterns

        """
        if operator == ">=":
            return [
                p for p in patterns if hasattr(p, attr) and getattr(p, attr) >= value
            ]
        else:  # operator == "<="
            return [
                p for p in patterns if hasattr(p, attr) and getattr(p, attr) <= value
            ]

    def _apply_text_filters(self, patterns: List[Pattern], **kwargs) -> List[Pattern]:
        """Apply text-based filters (contains, exclude, regex).

        Args:
            patterns: Patterns to filter
            **kwargs: Filter parameters

        Returns:
            Filtered patterns

        """
        filtered = patterns

        # Contains filter
        if "contains" in kwargs:
            contains_text = kwargs["contains"]
            filtered = [p for p in filtered if contains_text in p.path]

        # Exclude filter
        if "exclude" in kwargs:
            exclude_list = self._normalize_exclude_list(kwargs["exclude"])
            for exclude_text in exclude_list:
                filtered = [p for p in filtered if exclude_text not in p.path]

        # Regex filter
        if "regex" in kwargs:
            try:
                regex_pattern = re.compile(kwargs["regex"])
                filtered = [p for p in filtered if regex_pattern.search(p.path)]
            except re.error as e:
                raise DataspotError(f"Invalid regex pattern: {e}") from e

        return filtered

    def _normalize_exclude_list(self, exclude: Any) -> List[str]:
        """Normalize exclude parameter to list format.

        Args:
            exclude: String or list of strings to exclude

        Returns:
            List of exclude strings

        """
        if isinstance(exclude, str):
            return [exclude]
        return exclude

    def _apply_limit(self, patterns: List[Pattern], **kwargs) -> List[Pattern]:
        """Apply result limit.

        Args:
            patterns: Patterns to limit
            **kwargs: Filter parameters containing 'limit'

        Returns:
            Limited patterns

        """
        if "limit" in kwargs:
            return patterns[: kwargs["limit"]]
        return patterns


class TreeFilter:
    """Specialized filter for tree method parameters."""

    @staticmethod
    def build_filter_kwargs(**kwargs) -> Dict[str, Any]:
        """Build filter kwargs for tree method.

        Args:
            **kwargs: Tree method parameters

        Returns:
            Dictionary of filter parameters

        """
        # Parameter mapping: tree param -> filter param
        param_mapping = {"min_value": "min_count", "max_value": "max_count"}

        # Direct pass-through parameters
        pass_through = [
            "min_percentage",
            "max_percentage",
            "min_depth",
            "max_depth",
            "contains",
            "exclude",
            "regex",
        ]

        filter_kwargs = {}

        # Apply parameter mapping and pass-through
        for key, value in kwargs.items():
            if value is not None:
                if key in param_mapping:
                    filter_kwargs[param_mapping[key]] = value
                elif key in pass_through:
                    filter_kwargs[key] = value

        return filter_kwargs
