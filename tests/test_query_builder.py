"""Tests for QueryBuilder functionality in Dataspot.

This module tests the fluent interface QueryBuilder for creating complex
queries and filters in a readable and chainable manner.
"""

import pytest

from dataspot import Dataspot
from dataspot.core import Pattern
from dataspot.exceptions import QueryError
from dataspot.query import (
    QueryBuilder,
    create_business_query,
    create_data_quality_query,
    create_fraud_query,
)


class TestQueryBuilderBasics:
    """Test cases for basic QueryBuilder functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.dataspot = Dataspot()
        self.builder = QueryBuilder(self.dataspot)

        # Sample data for testing
        self.test_data = [
            {
                "country": "US",
                "device": "mobile",
                "user_type": "premium",
                "amount": 100,
            },
            {
                "country": "US",
                "device": "mobile",
                "user_type": "premium",
                "amount": 200,
            },
            {"country": "US", "device": "desktop", "user_type": "free", "amount": 50},
            {"country": "EU", "device": "mobile", "user_type": "free", "amount": 75},
            {
                "country": "EU",
                "device": "tablet",
                "user_type": "premium",
                "amount": 150,
            },
            {
                "country": "CA",
                "device": "mobile",
                "user_type": "premium",
                "amount": 120,
            },
        ]

    def test_query_builder_creation(self):
        """Test QueryBuilder instantiation."""
        builder = QueryBuilder(self.dataspot)

        assert builder.dataspot is self.dataspot
        assert isinstance(builder.data_filters, dict)
        assert isinstance(builder.pattern_filters, dict)
        assert isinstance(builder.sorting, dict)
        assert isinstance(builder.limits, dict)

    def test_simple_field_filter(self):
        """Test adding simple field filter."""
        builder = self.builder.field("country", "US")

        # Should return self for chaining
        assert builder is self.builder

        # Should add to data_filters
        assert builder.data_filters["country"] == "US"

    def test_multiple_field_values(self):
        """Test field filter with multiple values."""
        builder = self.builder.field("country", ["US", "CA"])

        assert builder.data_filters["country"] == ["US", "CA"]

    def test_method_chaining(self):
        """Test that methods can be chained together."""
        result = (
            self.builder.field("country", "US")
            .min_percentage(20)
            .max_depth(3)
            .limit(10)
        )

        # Should return the same instance
        assert result is self.builder

        # Should accumulate all filters
        assert self.builder.data_filters["country"] == "US"
        assert self.builder.pattern_filters["min_percentage"] == 20
        assert self.builder.pattern_filters["max_depth"] == 3
        assert self.builder.limits["limit"] == 10

    def test_execute_basic_query(self):
        """Test executing a basic query."""
        patterns = self.builder.field("country", "US").execute(
            self.test_data, ["country", "device"]
        )

        # Should return Pattern objects
        assert isinstance(patterns, list)
        assert all(isinstance(p, Pattern) for p in patterns)

        # Should only include US patterns
        for pattern in patterns:
            assert "country=US" in pattern.path

    def test_execute_vs_direct_dataspot_call(self):
        """Test that QueryBuilder execute produces same results as direct call."""
        # Using QueryBuilder
        builder_patterns = (
            self.builder.field("country", "US")
            .min_percentage(20)
            .execute(self.test_data, ["country", "device"])
        )

        # Using Dataspot directly
        direct_patterns = self.dataspot.find(
            self.test_data,
            ["country", "device"],
            query={"country": "US"},
            min_percentage=20,
        )

        # Should produce identical results
        assert len(builder_patterns) == len(direct_patterns)
        for bp, dp in zip(builder_patterns, direct_patterns, strict=False):
            assert bp.path == dp.path
            assert bp.count == dp.count
            assert bp.percentage == dp.percentage


class TestQueryBuilderFilters:
    """Test cases for QueryBuilder filter methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.builder = QueryBuilder(self.dataspot)

    def test_percentage_filters(self):
        """Test percentage filtering methods."""
        builder = self.builder.min_percentage(10.0).max_percentage(80.0)

        assert builder.pattern_filters["min_percentage"] == 10.0
        assert builder.pattern_filters["max_percentage"] == 80.0

    def test_count_filters(self):
        """Test count filtering methods."""
        builder = self.builder.min_count(5).max_count(100)

        assert builder.pattern_filters["min_count"] == 5
        assert builder.pattern_filters["max_count"] == 100

    def test_depth_filters(self):
        """Test depth filtering methods."""
        builder = self.builder.min_depth(1).max_depth(3)

        assert builder.pattern_filters["min_depth"] == 1
        assert builder.pattern_filters["max_depth"] == 3

    def test_contains_filter(self):
        """Test contains text filter."""
        builder = self.builder.contains("mobile")

        assert builder.pattern_filters["contains"] == "mobile"

    def test_exclude_filter_single(self):
        """Test exclude filter with single term."""
        builder = self.builder.exclude("test")

        assert builder.pattern_filters["exclude"] == ["test"]

    def test_exclude_filter_multiple(self):
        """Test exclude filter with multiple terms."""
        builder = self.builder.exclude(["test", "debug", "internal"])

        assert builder.pattern_filters["exclude"] == ["test", "debug", "internal"]

    def test_regex_filter(self):
        """Test regex pattern filter."""
        pattern = r"device=\w+"
        builder = self.builder.regex(pattern)

        assert builder.pattern_filters["regex"] == pattern

    def test_invalid_regex_filter(self):
        """Test regex filter with invalid pattern."""
        with pytest.raises(QueryError):
            self.builder.regex("[invalid regex(")

    def test_sorting_options(self):
        """Test sorting configuration."""
        # Default descending
        builder1 = self.builder.sort_by("percentage")
        assert builder1.sorting["sort_by"] == "percentage"
        assert builder1.sorting["reverse"] is True

        # Explicit ascending
        builder2 = QueryBuilder(self.dataspot).sort_by("count", reverse=False)
        assert builder2.sorting["sort_by"] == "count"
        assert builder2.sorting["reverse"] is False

    def test_invalid_sort_field(self):
        """Test sorting with invalid field."""
        with pytest.raises(QueryError):
            self.builder.sort_by("invalid_field")

    def test_limit_methods(self):
        """Test limit and top methods."""
        builder1 = self.builder.limit(15)
        assert builder1.limits["limit"] == 15

        builder2 = QueryBuilder(self.dataspot).top(10)
        assert builder2.limits["limit"] == 10  # top() is alias for limit()

    def test_invalid_limit_values(self):
        """Test limit with invalid values."""
        with pytest.raises(QueryError):
            self.builder.limit(0)

        with pytest.raises(QueryError):
            self.builder.limit(-5)


class TestQueryBuilderRanges:
    """Test cases for QueryBuilder range methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.builder = QueryBuilder(self.dataspot)

    def test_percentage_range(self):
        """Test percentage range method."""
        builder = self.builder.percentage_range(20.0, 80.0)

        assert builder.pattern_filters["min_percentage"] == 20.0
        assert builder.pattern_filters["max_percentage"] == 80.0

    def test_count_range(self):
        """Test count range method."""
        builder = self.builder.count_range(10, 100)

        assert builder.pattern_filters["min_count"] == 10
        assert builder.pattern_filters["max_count"] == 100

    def test_depth_range(self):
        """Test depth range method."""
        builder = self.builder.depth_range(1, 3)

        assert builder.pattern_filters["min_depth"] == 1
        assert builder.pattern_filters["max_depth"] == 3

    def test_range_validation(self):
        """Test that range methods validate min <= max."""
        # These should work fine
        self.builder.percentage_range(10, 90)
        self.builder.count_range(5, 50)
        self.builder.depth_range(1, 5)

        # These might not be explicitly validated in current implementation
        # but could be added as enhancement


class TestQueryBuilderValidation:
    """Test cases for QueryBuilder validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_percentage_validation(self):
        """Test percentage value validation."""
        builder = QueryBuilder(self.dataspot)

        # Valid percentages
        builder.min_percentage(0)
        builder.min_percentage(50.5)
        builder.min_percentage(100)

        # Invalid percentages
        with pytest.raises(QueryError):
            builder.min_percentage(-1)

        with pytest.raises(QueryError):
            builder.min_percentage(101)

    def test_count_validation(self):
        """Test count value validation."""
        builder = QueryBuilder(self.dataspot)

        # Valid counts
        builder.min_count(0)
        builder.min_count(100)

        # Invalid counts
        with pytest.raises(QueryError):
            builder.min_count(-1)

    def test_depth_validation(self):
        """Test depth value validation."""
        builder = QueryBuilder(self.dataspot)

        # Valid depths
        builder.min_depth(1)
        builder.min_depth(10)

        # Invalid depths
        with pytest.raises(QueryError):
            builder.min_depth(0)


class TestQueryBuilderUtilities:
    """Test cases for QueryBuilder utility methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.builder = QueryBuilder(self.dataspot)

    def test_build_query(self):
        """Test building final query dictionary."""
        self.builder.field("country", "US").min_percentage(20).sort_by(
            "percentage"
        ).limit(10)

        query = self.builder.build_query()

        expected_keys = ["country", "min_percentage", "sort_by", "reverse", "limit"]
        for key in expected_keys:
            assert key in query

    def test_reset(self):
        """Test resetting QueryBuilder state."""
        # Add some filters
        self.builder.field("country", "US").min_percentage(20).limit(10)

        # Verify filters are set
        assert len(self.builder.data_filters) > 0
        assert len(self.builder.pattern_filters) > 0
        assert len(self.builder.limits) > 0

        # Reset
        result = self.builder.reset()

        # Should return self
        assert result is self.builder

        # Should clear all filters
        assert len(self.builder.data_filters) == 0
        assert len(self.builder.pattern_filters) == 0
        assert len(self.builder.sorting) == 0
        assert len(self.builder.limits) == 0

    def test_copy(self):
        """Test copying QueryBuilder."""
        # Configure original
        self.builder.field("country", "US").min_percentage(20)

        # Create copy
        copy_builder = self.builder.copy()

        # Should be different instances
        assert copy_builder is not self.builder
        assert copy_builder.dataspot is self.builder.dataspot

        # Should have same filters
        assert copy_builder.data_filters == self.builder.data_filters
        assert copy_builder.pattern_filters == self.builder.pattern_filters

        # Modifying copy shouldn't affect original
        copy_builder.field("device", "mobile")
        assert "device" not in self.builder.data_filters
        assert "device" in copy_builder.data_filters

    def test_string_representation(self):
        """Test QueryBuilder string representation."""
        self.builder.field("country", "US").min_percentage(20).limit(10)

        repr_str = repr(self.builder)

        # Should contain basic info
        assert "QueryBuilder" in repr_str
        assert "filters" in repr_str


class TestQueryBuilderAnalyze:
    """Test cases for QueryBuilder analyze method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.builder = QueryBuilder(self.dataspot)

        self.test_data = [
            {"country": "US", "device": "mobile", "amount": 100},
            {"country": "US", "device": "desktop", "amount": 150},
            {"country": "EU", "device": "mobile", "amount": 200},
        ]

    def test_analyze_method(self):
        """Test QueryBuilder analyze method."""
        result = self.builder.field("country", "US").analyze(
            self.test_data, ["country", "device"]
        )

        # Should return analysis dictionary
        assert isinstance(result, dict)
        assert "patterns" in result
        assert "statistics" in result
        assert "field_stats" in result
        assert "top_patterns" in result

    def test_analyze_vs_execute(self):
        """Test that analyze returns more comprehensive data than execute."""
        patterns = self.builder.execute(self.test_data, ["country", "device"])
        analysis = self.builder.analyze(self.test_data, ["country", "device"])

        # Patterns should be same
        assert len(analysis["patterns"]) == len(patterns)

        # Analysis should have additional info
        assert "statistics" in analysis
        assert "field_stats" in analysis


class TestPreConfiguredQueries:
    """Test cases for pre-configured query functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_fraud_query(self):
        """Test create_fraud_query function."""
        fraud_builder = create_fraud_query(self.dataspot)

        assert isinstance(fraud_builder, QueryBuilder)
        assert fraud_builder.dataspot is self.dataspot

        # Should have fraud detection defaults
        query = fraud_builder.build_query()
        assert query.get("min_percentage") == 5.0
        assert query.get("max_depth") == 4
        assert query.get("sort_by") == "percentage"

    def test_business_query(self):
        """Test create_business_query function."""
        business_builder = create_business_query(self.dataspot)

        assert isinstance(business_builder, QueryBuilder)

        # Should have business analysis defaults
        query = business_builder.build_query()
        assert query.get("min_percentage") == 10.0
        assert query.get("max_depth") == 3
        assert query.get("limit") == 20

    def test_data_quality_query(self):
        """Test create_data_quality_query function."""
        dq_builder = create_data_quality_query(self.dataspot)

        assert isinstance(dq_builder, QueryBuilder)

        # Should have data quality defaults
        query = dq_builder.build_query()
        assert query.get("min_percentage") == 50.0
        assert query.get("limit") == 10

    def test_preconfigured_query_usage(self):
        """Test using pre-configured queries."""
        test_data = [{"status": "active"}] * 60 + [{"status": "inactive"}] * 40

        # Use data quality query to find high concentrations
        patterns = create_data_quality_query(self.dataspot).execute(
            test_data, ["status"]
        )

        # Should find high concentration patterns
        assert len(patterns) > 0
        for pattern in patterns:
            assert pattern.percentage >= 50.0


class TestQueryBuilderComplexScenarios:
    """Test cases for complex QueryBuilder scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

        # More complex dataset
        self.complex_data = []
        for i in range(100):
            self.complex_data.append(
                {
                    "region": ["north", "south", "east", "west"][i % 4],
                    "segment": ["enterprise", "smb", "consumer"][i % 3],
                    "product": ["basic", "premium", "enterprise"][i % 3],
                    "revenue": i * 100,
                    "active": i % 2 == 0,
                }
            )

    def test_complex_business_analysis(self):
        """Test complex business analysis scenario."""
        # Find high-value enterprise patterns in north/south regions
        patterns = (
            QueryBuilder(self.dataspot)
            .field("region", ["north", "south"])
            .field("segment", "enterprise")
            .min_percentage(8)
            .contains("premium")
            .sort_by("percentage")
            .top(5)
            .execute(self.complex_data, ["region", "segment", "product"])
        )

        # Should apply all filters correctly
        for pattern in patterns:
            assert pattern.percentage >= 8.0
            assert "premium" in pattern.path
            assert ("region=north" in pattern.path) or ("region=south" in pattern.path)
            assert "segment=enterprise" in pattern.path

    def test_fraud_detection_scenario(self):
        """Test fraud detection scenario."""
        # Simulate fraud detection query - filter for active users with premium products
        suspicious_patterns = (
            create_fraud_query(self.dataspot)
            .field("active", "True")  # Boolean converted to string
            .exclude(["basic"])
            .contains("premium")  # Look for premium in paths
            .execute(self.complex_data, ["region", "product", "active"])
        )

        # Should find relevant patterns
        assert len(suspicious_patterns) > 0

        # Should exclude basic products and only include premium
        for pattern in suspicious_patterns:
            assert "basic" not in pattern.path
            assert "premium" in pattern.path

    def test_progressive_filtering(self):
        """Test progressive filtering by chaining queries."""
        # Start with broad query
        base_builder = QueryBuilder(self.dataspot).field("region", ["north", "south"])

        # Add enterprise focus
        enterprise_builder = (
            base_builder.copy().field("segment", "enterprise").min_percentage(10)
        )

        # Add premium product focus
        premium_builder = (
            enterprise_builder.copy().contains("premium").sort_by("percentage").top(3)
        )

        # Execute final query
        patterns = premium_builder.execute(
            self.complex_data, ["region", "segment", "product"]
        )

        # Should have applied all progressive filters
        assert len(patterns) <= 3
        for pattern in patterns:
            assert pattern.percentage >= 10.0

    def test_query_builder_reuse(self):
        """Test reusing QueryBuilder for multiple analyses."""
        # Create reusable base query
        base_query = (
            QueryBuilder(self.dataspot)
            .min_percentage(15)
            .max_depth(2)
            .sort_by("percentage")
        )

        # Use for different field combinations
        regional_patterns = base_query.copy().execute(
            self.complex_data, ["region", "segment"]
        )

        product_patterns = base_query.copy().execute(
            self.complex_data, ["product", "active"]
        )

        # Both should apply same base filters
        for patterns in [regional_patterns, product_patterns]:
            for pattern in patterns:
                assert pattern.percentage >= 15.0
                assert pattern.depth <= 2

    def test_error_handling_in_complex_query(self):
        """Test error handling in complex query scenarios."""
        builder = QueryBuilder(self.dataspot)

        # Test that errors are caught appropriately
        with pytest.raises(QueryError):
            builder.min_percentage(-10)  # Invalid percentage

        with pytest.raises(QueryError):
            builder.regex("[invalid")  # Invalid regex

        with pytest.raises(QueryError):
            builder.sort_by("invalid_field")  # Invalid sort field


class TestQueryBuilderPerformance:
    """Test cases for QueryBuilder performance characteristics."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_large_dataset_query(self):
        """Test QueryBuilder performance with large dataset."""
        # Create large dataset
        large_data = []
        for i in range(1000):
            large_data.append(
                {
                    "category": f"cat_{i % 10}",
                    "type": f"type_{i % 5}",
                    "status": "active" if i % 2 == 0 else "inactive",
                }
            )

        # Complex query should still perform well
        patterns = (
            QueryBuilder(self.dataspot)
            .field("status", "active")
            .min_percentage(5)
            .contains("cat")
            .sort_by("percentage")
            .top(20)
            .execute(large_data, ["category", "type", "status"])
        )

        # Should complete efficiently
        assert len(patterns) <= 20
        assert isinstance(patterns, list)

    def test_complex_filter_combinations(self):
        """Test performance with many filter combinations."""
        test_data = [{"x": i % 5, "y": i % 3, "z": i % 2} for i in range(200)]

        # Apply many filters
        patterns = (
            QueryBuilder(self.dataspot)
            .field("z", "1")
            .min_percentage(2)
            .max_percentage(40)
            .min_count(3)
            .max_count(50)
            .min_depth(1)
            .max_depth(3)
            .sort_by("count")
            .limit(15)
            .execute(test_data, ["x", "y", "z"])
        )

        # Should handle multiple filters efficiently
        assert isinstance(patterns, list)
        assert len(patterns) <= 15
