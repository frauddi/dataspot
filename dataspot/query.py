"""QueryBuilder for constructing complex queries with a fluent interface."""

from typing import Any, Dict, List, Union

from .exceptions import QueryError


class QueryBuilder:
    """Fluent interface for building complex queries for Dataspot analysis.

    Examples:
        # Simple query
        patterns = QueryBuilder(dataspot) \
            .field("country", "US") \
            .min_percentage(20) \
            .execute()

        # Complex query
        patterns = QueryBuilder(dataspot) \
            .field("country", ["US", "CA"]) \
            .min_percentage(10) \
            .max_depth(3) \
            .contains("mobile") \
            .exclude(["test", "debug"]) \
            .sort_by("percentage") \
            .limit(15) \
            .execute()

    """

    def __init__(self, dataspot_instance):
        """Initialize QueryBuilder with a Dataspot instance.

        Args:
            dataspot_instance: Instance of Dataspot class

        """
        self.dataspot = dataspot_instance
        self.data_filters = {}
        self.pattern_filters = {}
        self.sorting = {}
        self.limits = {}

    def field(self, field_name: str, value: Union[str, List[str]]):
        """Filter by field value(s).

        Args:
            field_name: Name of the field to filter
            value: Value or list of values to match

        Returns:
            QueryBuilder: Self for method chaining

        """
        self.data_filters[field_name] = value
        return self

    def min_percentage(self, percentage: float):
        """Set minimum percentage threshold for patterns.

        Args:
            percentage: Minimum percentage (0-100)

        Returns:
            QueryBuilder: Self for method chaining

        """
        if not 0 <= percentage <= 100:
            raise QueryError(f"Percentage must be between 0-100, got {percentage}")

        self.pattern_filters["min_percentage"] = percentage
        return self

    def max_percentage(self, percentage: float):
        """Set maximum percentage threshold for patterns.

        Args:
            percentage: Maximum percentage (0-100)

        Returns:
            QueryBuilder: Self for method chaining

        """
        if not 0 <= percentage <= 100:
            raise QueryError(f"Percentage must be between 0-100, got {percentage}")

        self.pattern_filters["max_percentage"] = percentage
        return self

    def min_count(self, count: int):
        """Set minimum count threshold for patterns.

        Args:
            count: Minimum number of records

        Returns:
            QueryBuilder: Self for method chaining

        """
        if count < 0:
            raise QueryError(f"Count must be non-negative, got {count}")

        self.pattern_filters["min_count"] = count
        return self

    def max_count(self, count: int):
        """Set maximum count threshold for patterns.

        Args:
            count: Maximum number of records

        Returns:
            QueryBuilder: Self for method chaining

        """
        if count < 0:
            raise QueryError(f"Count must be non-negative, got {count}")

        self.pattern_filters["max_count"] = count
        return self

    def min_depth(self, depth: int):
        """Set minimum depth for patterns.

        Args:
            depth: Minimum depth level

        Returns:
            QueryBuilder: Self for method chaining

        """
        if depth < 1:
            raise QueryError(f"Depth must be at least 1, got {depth}")

        self.pattern_filters["min_depth"] = depth
        return self

    def max_depth(self, depth: int):
        """Set maximum depth for patterns.

        Args:
            depth: Maximum depth level

        Returns:
            QueryBuilder: Self for method chaining

        """
        if depth < 1:
            raise QueryError(f"Depth must be at least 1, got {depth}")

        self.pattern_filters["max_depth"] = depth
        return self

    def contains(self, text: str):
        """Filter patterns that contain specific text.

        Args:
            text: Text that must be present in pattern path

        Returns:
            QueryBuilder: Self for method chaining

        """
        self.pattern_filters["contains"] = text
        return self

    def exclude(self, patterns: Union[str, List[str]]):
        """Exclude patterns containing specific text.

        Args:
            patterns: Text or list of texts to exclude

        Returns:
            QueryBuilder: Self for method chaining

        """
        if isinstance(patterns, str):
            patterns = [patterns]

        self.pattern_filters["exclude"] = patterns
        return self

    def regex(self, pattern: str):
        """Filter patterns using regular expression.

        Args:
            pattern: Regular expression pattern

        Returns:
            QueryBuilder: Self for method chaining

        """
        # Validate regex pattern
        import re

        try:
            re.compile(pattern)
        except re.error as e:
            raise QueryError(f"Invalid regex pattern: {e}") from e

        self.pattern_filters["regex"] = pattern
        return self

    def sort_by(self, field: str, reverse: bool = True):
        """Set sorting criteria.

        Args:
            field: Field to sort by ('percentage', 'count', 'depth')
            reverse: Sort in descending order if True

        Returns:
            QueryBuilder: Self for method chaining

        """
        valid_fields = ["percentage", "count", "depth"]
        if field not in valid_fields:
            raise QueryError(f"Sort field must be one of {valid_fields}, got '{field}'")

        self.sorting["sort_by"] = field
        self.sorting["reverse"] = reverse
        return self

    def limit(self, count: int):
        """Limit the number of results.

        Args:
            count: Maximum number of patterns to return

        Returns:
            QueryBuilder: Self for method chaining

        """
        if count < 1:
            raise QueryError(f"Limit must be at least 1, got {count}")

        self.limits["limit"] = count
        return self

    def top(self, count: int):
        """Alias for limit() - get top N results.

        Args:
            count: Number of top patterns to return

        Returns:
            QueryBuilder: Self for method chaining

        """
        return self.limit(count)

    def percentage_range(self, min_pct: float, max_pct: float):
        """Set percentage range in one call.

        Args:
            min_pct: Minimum percentage
            max_pct: Maximum percentage

        Returns:
            QueryBuilder: Self for method chaining

        """
        return self.min_percentage(min_pct).max_percentage(max_pct)

    def count_range(self, min_count: int, max_count: int):
        """Set count range in one call.

        Args:
            min_count: Minimum count
            max_count: Maximum count

        Returns:
            QueryBuilder: Self for method chaining

        """
        return self.min_count(min_count).max_count(max_count)

    def depth_range(self, min_depth: int, max_depth: int):
        """Set depth range in one call.

        Args:
            min_depth: Minimum depth
            max_depth: Maximum depth

        Returns:
            QueryBuilder: Self for method chaining

        """
        return self.min_depth(min_depth).max_depth(max_depth)

    def build_query(self) -> Dict[str, Any]:
        """Build the final query dictionary.

        Returns:
            Dictionary with all query parameters

        """
        query = {}

        # Combine all filters
        query.update(self.data_filters)
        query.update(self.pattern_filters)
        query.update(self.sorting)
        query.update(self.limits)

        return query

    def execute(self, data: List[Dict[str, Any]], fields: List[str]):
        """Execute the query and return results.

        Args:
            data: Data to analyze
            fields: Fields to analyze

        Returns:
            List of Pattern objects matching the query

        """
        query = self.build_query()

        # Separate data filters from pattern filters
        data_query = {k: v for k, v in query.items() if k in self.data_filters}
        pattern_kwargs = {k: v for k, v in query.items() if k not in self.data_filters}

        # Execute the query
        return self.dataspot.find(data, fields, query=data_query, **pattern_kwargs)

    def analyze(self, data: List[Dict[str, Any]], fields: List[str]):
        """Execute the query and return full analysis.

        Args:
            data: Data to analyze
            fields: Fields to analyze

        Returns:
            Dictionary with analysis results

        """
        query = self.build_query()

        # Separate data filters from pattern filters
        data_query = {k: v for k, v in query.items() if k in self.data_filters}
        pattern_kwargs = {k: v for k, v in query.items() if k not in self.data_filters}

        # Execute the analysis
        return self.dataspot.analyze(data, fields, query=data_query, **pattern_kwargs)

    def reset(self):
        """Reset all filters and return a clean QueryBuilder.

        Returns:
            QueryBuilder: Self with all filters cleared

        """
        self.data_filters.clear()
        self.pattern_filters.clear()
        self.sorting.clear()
        self.limits.clear()
        return self

    def copy(self):
        """Create a copy of this QueryBuilder.

        Returns:
            QueryBuilder: New instance with same filters

        """
        new_builder = QueryBuilder(self.dataspot)
        new_builder.data_filters = self.data_filters.copy()
        new_builder.pattern_filters = self.pattern_filters.copy()
        new_builder.sorting = self.sorting.copy()
        new_builder.limits = self.limits.copy()
        return new_builder

    def __repr__(self):
        """Return a string representation of the QueryBuilder."""
        query = self.build_query()
        return f"QueryBuilder({len(query)} filters: {list(query.keys())})"


# Helper functions for common query patterns
def create_fraud_query(dataspot_instance):
    """Create a QueryBuilder pre-configured for fraud detection.

    Returns:
        QueryBuilder with fraud detection defaults

    """
    return (
        QueryBuilder(dataspot_instance)
        .min_percentage(5.0)
        .max_depth(4)
        .sort_by("percentage")
    )


def create_business_query(dataspot_instance):
    """Create a QueryBuilder pre-configured for business intelligence.

    Returns:
        QueryBuilder with business analysis defaults

    """
    return (
        QueryBuilder(dataspot_instance)
        .min_percentage(10.0)
        .max_depth(3)
        .sort_by("percentage")
        .limit(20)
    )


def create_data_quality_query(dataspot_instance):
    """Create a QueryBuilder pre-configured for data quality analysis.

    Returns:
        QueryBuilder with data quality defaults

    """
    return (
        QueryBuilder(dataspot_instance)
        .min_percentage(50.0)
        .sort_by("percentage")
        .limit(10)
    )
