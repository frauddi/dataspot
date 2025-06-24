"""Core pattern dataspot for finding data concentration dataspots.

Based on the original algorithm created by [Elio Rincón @eliosf27] at Frauddi.
"""

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Pattern:
    """A concentration pattern found in the data."""

    path: str
    count: int
    percentage: float
    depth: int
    samples: List[Dict[str, Any]]

    def __post_init__(self):
        """Post-initialization hook."""
        if self.samples is None:
            self.samples = []


class Dataspot:
    """Finds concentration patterns and dataspots in datasets.

    This dataspot builds hierarchical trees of patterns and identifies
    where data concentrates, helping spot anomalies and insights.
    """

    def __init__(self):
        """Initialize the Dataspot class."""
        self.email_patterns = ["email", "email_pattern"]
        self.preprocessors: Dict[str, Callable] = {}

    def add_preprocessor(
        self, field_name: str, preprocessor: Callable[[Any], Any]
    ) -> None:
        """Add a custom preprocessor for a specific field."""
        self.preprocessors[field_name] = preprocessor

    def find(
        self,
        data: List[Dict[str, Any]],
        fields: List[str],
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> List[Pattern]:
        """Find concentration patterns in data.

        Args:
            data: List of records (dictionaries)
            fields: List of field names to analyze hierarchically
            query: Optional filters to apply to data
            **kwargs: Additional filtering options
                - min_percentage: Minimum percentage for a pattern to be included
                - max_percentage: Maximum percentage for a pattern to be included
                - min_count: Minimum count for a pattern to be included
                - max_count: Maximum count for a pattern to be included
                - min_depth: Minimum depth for a pattern to be included
                - max_depth: Maximum depth to analyze
                - contains: Pattern path must contain this text
                - exclude: Pattern path must NOT contain these texts (string or list)
                - regex: Pattern path must match this regex
                - limit: Maximum number of patterns to return

        Returns:
            List of Pattern objects sorted by percentage

        """
        # Filter data based on query
        if query:
            data = [record for record in data if self._matches_query(record, query)]

        if not data:
            return []

        # Build the pattern tree
        tree = self._build_tree(data, fields)

        # Extract patterns from tree
        patterns = self._extract_patterns(tree, len(data))

        # Apply filtering
        patterns = self._apply_filters(patterns, **kwargs)

        # Sort by percentage (highest first)
        patterns.sort(key=lambda p: p.percentage, reverse=True)

        return patterns

    def analyze(
        self,
        data: List[Dict[str, Any]],
        fields: List[str],
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Analyze data and return comprehensive insights.

        Returns:
            Dictionary with patterns, statistics, and insights

        """
        patterns = self.find(data, fields, query, **kwargs)

        # Calculate statistics
        total_records = len(data)
        if query:
            filtered_records = len([r for r in data if self._matches_query(r, query)])
        else:
            filtered_records = total_records

        # Field distribution analysis
        field_stats = self._analyze_field_distributions(data, fields)

        return {
            "patterns": patterns,
            "statistics": {
                "total_records": total_records,
                "filtered_records": filtered_records,
                "patterns_found": len(patterns),
                "max_concentration": (
                    max([p.percentage for p in patterns]) if patterns else 0
                ),
                "avg_concentration": (
                    sum([p.percentage for p in patterns]) / len(patterns)
                    if patterns
                    else 0
                ),
            },
            "field_stats": field_stats,
            "top_patterns": patterns[:5] if patterns else [],
        }

    def _build_tree(
        self, data: List[Dict[str, Any]], fields: List[str]
    ) -> Dict[str, Any]:
        """Build hierarchical tree from data based on original algorithm."""
        total = len(data)
        tree = {"children": {}}

        for record in data:
            self._add_record_to_tree(record, fields, tree, total)

        return tree

    def _add_record_to_tree(
        self,
        record: Dict[str, Any],
        fields: List[str],
        tree: Dict[str, Any],
        total: int,
    ):
        """Add a single record to the tree structure."""
        # Get all possible paths for this record (handling lists)
        paths = self._get_record_paths(record, fields)

        for path in paths:
            self._add_path_to_tree(path, tree, total, record)

    def _get_record_paths(
        self, record: Dict[str, Any], fields: List[str]
    ) -> List[List[str]]:
        """Get all possible paths for a record, handling list values."""

        def _expand_paths(
            remaining_fields: List[str], current_path: List[str]
        ) -> List[List[str]]:
            if not remaining_fields:
                return [current_path]

            field = remaining_fields[0]
            value = self._preprocess_value(field, record.get(field, ""), record)

            paths = []
            if isinstance(value, list):
                for v in value:
                    new_path = current_path + [f"{field}={v}"]
                    paths.extend(_expand_paths(remaining_fields[1:], new_path))
            else:
                new_path = current_path + [f"{field}={value}"]
                paths.extend(_expand_paths(remaining_fields[1:], new_path))

            return paths

        return _expand_paths(fields, [])

    def _add_path_to_tree(
        self, path: List[str], tree: Dict[str, Any], total: int, record: Dict[str, Any]
    ):
        """Add a complete path to the tree structure."""
        current = tree

        for i, key_value in enumerate(path):
            if "children" not in current:
                current["children"] = {}

            if key_value not in current["children"]:
                current["children"][key_value] = {
                    "count": 0,
                    "percentage": 0.0,
                    "depth": i + 1,
                    "children": {},
                    "samples": [],  # Store sample records
                }

            current = current["children"][key_value]

            # Increment count in each level
            current["count"] += 1
            current["percentage"] = round((current["count"] * 100) / total, 2)

            # Add sample record (limit to 3 to avoid memory issues)
            if len(current["samples"]) < 3:
                current["samples"].append(record.copy())

    def _extract_patterns(self, tree: Dict[str, Any], total: int) -> List[Pattern]:
        """Extract patterns from the tree structure."""
        patterns = []

        def _traverse(node: Dict[str, Any], path: str = ""):
            for key, child in node.get("children", {}).items():
                current_path = f"{path} > {key}" if path else key

                if child.get("count", 0) > 0:
                    # Get sample records from this node
                    node_samples = child.get("samples", [])

                    pattern = Pattern(
                        path=current_path,
                        count=child["count"],
                        percentage=child["percentage"],
                        depth=child["depth"],
                        samples=node_samples[:3],  # Keep first 3 samples
                    )
                    patterns.append(pattern)

                # Recursively traverse children
                _traverse(child, current_path)

        _traverse(tree)
        return patterns

    def _preprocess_value(self, field: str, value: Any, record: Dict[str, Any]) -> Any:
        """Preprocess field values based on type and custom preprocessors."""
        # Apply custom preprocessor if available
        if field in self.preprocessors:
            return self.preprocessors[field](value)

        # Handle email patterns
        if field in self.email_patterns:
            email_value = record.get("email", value)
            if isinstance(email_value, str) and "@" in email_value:
                email_local = email_value[: email_value.index("@")]
                return re.findall(r"[a-zA-Z]+", email_local)

        # Handle None values
        if value is None:
            return ""

        return value

    def _matches_query(self, record: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if a record matches query constraints."""
        for field, constraint in query.items():
            record_value = record.get(field)

            if isinstance(constraint, (list, tuple)):
                if str(record_value) not in [str(v) for v in constraint]:
                    return False
            else:
                if str(record_value) != str(constraint):
                    return False

        return True

    def _apply_filters(self, patterns: List[Pattern], **kwargs) -> List[Pattern]:
        """Apply filtering criteria to patterns."""
        filtered = patterns
        filtered = self._apply_numeric_filters(filtered, **kwargs)
        filtered = self._apply_text_filters(filtered, **kwargs)

        # Limit number of results
        if "limit" in kwargs:
            filtered = filtered[: kwargs["limit"]]

        return filtered

    def _apply_numeric_filters(
        self, patterns: List[Pattern], **kwargs
    ) -> List[Pattern]:
        """Apply numeric filters (percentage, count, depth)."""
        filtered = patterns

        for filter_name, attr in [
            ("min_percentage", "percentage"),
            ("max_percentage", "percentage"),
            ("min_count", "count"),
            ("max_count", "count"),
            ("min_depth", "depth"),
            ("max_depth", "depth"),
        ]:
            if filter_name in kwargs:
                value = kwargs[filter_name]
                if filter_name.startswith("min_"):
                    filtered = [p for p in filtered if getattr(p, attr) >= value]
                else:
                    filtered = [p for p in filtered if getattr(p, attr) <= value]

        return filtered

    def _apply_text_filters(self, patterns: List[Pattern], **kwargs) -> List[Pattern]:
        """Apply text-based filters (contains, exclude, regex)."""
        filtered = patterns

        if "contains" in kwargs:
            filtered = [p for p in filtered if kwargs["contains"] in p.path]

        if "exclude" in kwargs:
            exclude_list = kwargs["exclude"]
            if isinstance(exclude_list, str):
                exclude_list = [exclude_list]
            for exclude_text in exclude_list:
                filtered = [p for p in filtered if exclude_text not in p.path]

        if "regex" in kwargs:
            import re

            regex_pattern = re.compile(kwargs["regex"])
            filtered = [p for p in filtered if regex_pattern.search(p.path)]

        return filtered

    def _analyze_field_distributions(
        self, data: List[Dict[str, Any]], fields: List[str]
    ) -> Dict[str, Any]:
        """Analyze distribution of values in each field."""
        field_analysis = {}

        for field in fields:
            values = [record.get(field) for record in data]
            value_counts = Counter(str(v) for v in values if v is not None)

            field_analysis[field] = {
                "total_count": len(values),
                "unique_count": len(value_counts),
                "null_count": values.count(None),
                "top_values": [
                    {
                        "value": val,
                        "count": count,
                        "percentage": round((count / len(data)) * 100, 2),
                    }
                    for val, count in value_counts.most_common(5)
                ],
            }

        return field_analysis
