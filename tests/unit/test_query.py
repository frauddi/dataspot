"""Tests for all query and filtering functionality in Dataspot.

This module tests query filtering, pattern filtering, QueryBuilder fluent interface,
and pre-configured queries in a comprehensive manner.
"""

import re

import pytest

from dataspot import Dataspot
from dataspot.exceptions import QueryError
from dataspot.models.finder import Pattern
from dataspot.query import (
    QueryBuilder,
    create_business_query,
    create_data_quality_query,
    create_fraud_query,
)


class TestQueryFiltering:
    """Test cases for query-based data filtering."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.dataspot = Dataspot()

        # Comprehensive test dataset
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
            {"country": "US", "device": "mobile", "user_type": "free", "amount": 80},
            {
                "country": "EU",
                "device": "desktop",
                "user_type": "premium",
                "amount": 180,
            },
        ]

    def test_single_field_query(self):
        """Test filtering with single field query."""
        query = {"country": "US"}
        patterns = self.dataspot.find(
            self.test_data, ["country", "device"], query=query
        )

        # Should only find patterns from US records
        for pattern in patterns.patterns:
            assert "country=US" in pattern.path

        # Verify count - should be based on filtered data only
        us_records = [r for r in self.test_data if r["country"] == "US"]
        top_pattern = next(p for p in patterns.patterns if p.path == "country=US")
        assert top_pattern.count == len(us_records)

    def test_multiple_field_query(self):
        """Test filtering with multiple field constraints."""
        query = {"country": "US", "device": "mobile"}
        patterns = self.dataspot.find(
            self.test_data, ["country", "device", "user_type"], query=query
        )

        # Should only include records matching both constraints
        us_mobile_records = [
            r
            for r in self.test_data
            if r["country"] == "US" and r["device"] == "mobile"
        ]

        # Top pattern should represent all filtered records
        top_pattern = patterns.patterns[0]
        assert top_pattern.count == len(us_mobile_records)

        # All patterns should at least contain the first constraint
        for pattern in patterns.patterns:
            assert "country=US" in pattern.path

    def test_list_value_query(self):
        """Test query with list of acceptable values."""
        query = {"country": ["US", "CA"]}
        patterns = self.dataspot.find(
            self.test_data, ["country", "device"], query=query
        )

        # Should include records from US and CA only
        for pattern in patterns.patterns:
            assert ("country=US" in pattern.path) or ("country=CA" in pattern.path)
            assert "country=EU" not in pattern.path

    def test_query_no_matches(self):
        """Test query that matches no records."""
        query = {"country": "XX"}  # Non-existent country
        patterns = self.dataspot.find(
            self.test_data, ["country", "device"], query=query
        )

        # Should return empty list
        assert patterns.patterns == []

    def test_empty_query(self):
        """Test behavior with empty query dict."""
        query = {}
        patterns = self.dataspot.find(
            self.test_data, ["country", "device"], query=query
        )

        # Should behave same as no query
        patterns_no_query = self.dataspot.find(self.test_data, ["country", "device"])
        assert len(patterns.patterns) == len(patterns_no_query.patterns)


class TestPatternFiltering:
    """Test cases for pattern-based filtering after analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

        # Create data that will produce diverse patterns
        self.filter_data = []
        for i in range(100):
            self.filter_data.append(
                {
                    "category": f"cat_{i % 5}",  # 5 categories (20 each)
                    "type": f"type_{i % 3}",  # 3 types (33-34 each)
                    "status": "active" if i % 2 == 0 else "inactive",  # 50-50 split
                    "priority": "high" if i < 20 else "normal",  # 20 high, 80 normal
                }
            )

    def test_min_percentage_filter(self):
        """Test minimum percentage filtering."""
        # Get all patterns first
        all_patterns = self.dataspot.find(self.filter_data, ["category", "type"])

        # Apply min percentage filter
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], min_percentage=30
        )

        # All filtered patterns should have >= 30% concentration
        for pattern in filtered.patterns:
            assert pattern.percentage >= 30.0

        # Should have fewer patterns than unfiltered
        assert len(filtered.patterns) <= len(all_patterns.patterns)

    def test_max_percentage_filter(self):
        """Test maximum percentage filtering."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], max_percentage=25
        )

        # All patterns should have <= 25% concentration
        for pattern in filtered.patterns:
            assert pattern.percentage <= 25.0

    def test_min_count_filter(self):
        """Test minimum count filtering."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], min_count=15
        )

        # All patterns should have >= 15 records
        for pattern in filtered.patterns:
            assert pattern.count >= 15

    def test_max_depth_filter(self):
        """Test maximum depth filtering."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type", "status"], max_depth=2
        )

        # All patterns should have depth <= 2
        for pattern in filtered.patterns:
            assert pattern.depth <= 2

        # Should not include any depth-3 patterns
        depth_3_patterns = [p for p in filtered.patterns if p.depth == 3]
        assert len(depth_3_patterns) == 0

    def test_contains_filter(self):
        """Test contains text filtering."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], contains="cat_1"
        )

        # All patterns should contain "cat_1" in their path
        for pattern in filtered.patterns:
            assert "cat_1" in pattern.path

    def test_exclude_filter_single(self):
        """Test exclude filtering with single term."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], exclude="cat_0"
        )

        # No patterns should contain "cat_0"
        for pattern in filtered.patterns:
            assert "cat_0" not in pattern.path

    def test_exclude_filter_list(self):
        """Test exclude filtering with list of terms."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], exclude=["cat_0", "cat_1"]
        )

        # No patterns should contain either excluded term
        for pattern in filtered.patterns:
            assert "cat_0" not in pattern.path
            assert "cat_1" not in pattern.path

    def test_regex_filter(self):
        """Test regex pattern filtering."""
        # Filter for patterns containing "cat_" followed by even numbers
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], regex=r"cat_[02468]"
        )

        # All patterns should match the regex
        regex_pattern = re.compile(r"cat_[02468]")
        for pattern in filtered.patterns:
            assert regex_pattern.search(pattern.path) is not None

    def test_limit_filter(self):
        """Test result limit filtering."""
        all_patterns = self.dataspot.find(
            self.filter_data, ["category", "type", "status"]
        )
        limited = self.dataspot.find(
            self.filter_data, ["category", "type", "status"], limit=5
        )

        # Should return at most 5 patterns
        assert len(limited.patterns) <= 5
        assert len(limited.patterns) <= len(all_patterns.patterns)

        # Should return the top patterns (highest percentage first)
        if len(all_patterns.patterns) >= 5:
            assert len(limited.patterns) == 5
            # Should be ordered by percentage descending
            for i in range(len(limited.patterns) - 1):
                assert (
                    limited.patterns[i].percentage >= limited.patterns[i + 1].percentage
                )

    def test_combined_filters(self):
        """Test combining multiple filters."""
        filtered = self.dataspot.find(
            self.filter_data,
            ["category", "type", "status"],
            min_percentage=10,
            max_depth=2,
            contains="cat",
            exclude="type_2",
            limit=10,
        )

        # Verify all filter conditions
        for pattern in filtered.patterns:
            assert pattern.percentage >= 10.0  # min_percentage
            assert pattern.depth <= 2  # max_depth
            assert "cat" in pattern.path  # contains
            assert "type_2" not in pattern.path  # exclude

        # Should respect limit
        assert len(filtered.patterns) <= 10

    def test_conflicting_filters(self):
        """Test behavior with conflicting filter values."""
        data = [{"x": i % 5} for i in range(100)]

        # Conflicting percentage filters
        filtered = self.dataspot.find(
            data,
            ["x"],
            min_percentage=50,
            max_percentage=30,  # max < min
        )

        # Should return empty list
        assert filtered.patterns == []


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
        assert isinstance(patterns.patterns, list)
        assert all(isinstance(p, Pattern) for p in patterns.patterns)

        # Should only include US patterns
        for pattern in patterns.patterns:
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
        assert len(builder_patterns.patterns) == len(direct_patterns.patterns)
        for bp, dp in zip(
            builder_patterns.patterns, direct_patterns.patterns, strict=False
        ):
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

    def test_analyze_method(self):
        """Test QueryBuilder analyze method."""
        test_data = [
            {"country": "US", "device": "mobile", "amount": 100},
            {"country": "US", "device": "desktop", "amount": 150},
            {"country": "EU", "device": "mobile", "amount": 200},
        ]

        result = self.builder.field("country", "US").analyze(
            test_data, ["country", "device"]
        )

        # Should return AnalyzeOutput dataclass
        assert hasattr(result, "patterns")
        assert hasattr(result, "statistics")
        assert hasattr(result, "field_stats")
        assert hasattr(result, "top_patterns")


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
        result = create_data_quality_query(self.dataspot).execute(test_data, ["status"])

        # Should find high concentration patterns
        assert len(result.patterns) > 0
        for pattern in result.patterns:
            assert pattern.percentage >= 50.0


class TestComplexQueryScenarios:
    """Test cases for complex query scenarios and combinations."""

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
        result = (
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
        for pattern in result.patterns:
            assert pattern.percentage >= 8.0
            assert "premium" in pattern.path
            assert ("region=north" in pattern.path) or ("region=south" in pattern.path)
            assert "segment=enterprise" in pattern.path

    def test_fraud_detection_scenario(self):
        """Test fraud detection scenario."""
        # Simulate fraud detection query - filter for active users with premium products
        result = (
            create_fraud_query(self.dataspot)
            .field("active", "True")  # Boolean converted to string
            .exclude(["basic"])
            .contains("premium")  # Look for premium in paths
            .execute(self.complex_data, ["region", "product", "active"])
        )

        # Should find relevant patterns
        assert len(result.patterns) > 0

        # Should exclude basic products and only include premium
        for pattern in result.patterns:
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
        result = premium_builder.execute(
            self.complex_data, ["region", "segment", "product"]
        )

        # Should have applied all progressive filters
        assert len(result.patterns) <= 3
        for pattern in result.patterns:
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
        regional_result = base_query.copy().execute(
            self.complex_data, ["region", "segment"]
        )

        product_result = base_query.copy().execute(
            self.complex_data, ["product", "active"]
        )

        # Both should apply same base filters
        for result in [regional_result, product_result]:
            for pattern in result.patterns:
                assert pattern.percentage >= 15.0
                assert pattern.depth <= 2

    def test_complex_query_and_filter_combination(self):
        """Test complex combination of queries and filters."""
        data = []
        for i in range(200):
            data.append(
                {
                    "region": ["north", "south", "east", "west"][i % 4],
                    "segment": ["enterprise", "small", "medium"][i % 3],
                    "status": ["active", "inactive"][i % 2],
                    "tier": ["gold", "silver", "bronze"][i % 3],
                }
            )

        # Complex filtering
        result = self.dataspot.find(
            data,
            ["region", "segment", "status"],
            query={"region": ["north", "south"]},  # Query filter
            min_percentage=8,  # Pattern filter
            max_depth=2,  # Pattern filter
            contains="enterprise",  # Pattern filter
            limit=5,  # Pattern filter
        )

        # Verify all conditions are met
        for pattern in result.patterns:
            assert pattern.percentage >= 8.0
            assert pattern.depth <= 2
            assert "enterprise" in pattern.path
            # Query filter ensures only north/south regions
            assert ("region=north" in pattern.path) or ("region=south" in pattern.path)

        assert len(result.patterns) <= 5

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

    def test_large_dataset_query_performance(self):
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
        assert len(patterns.patterns) <= 20
