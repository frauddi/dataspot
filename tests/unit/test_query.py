"""Tests for all query and filtering functionality in Dataspot.

This module tests query filtering, pattern filtering, QueryBuilder fluent interface,
and pre-configured queries in a comprehensive manner.
"""

import re

import pytest

from dataspot import Dataspot
from dataspot.exceptions import QueryError
from dataspot.models.finder import FindInput, FindOptions, Pattern
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
        find_input = FindInput(
            data=self.test_data, fields=["country", "device"], query={"country": "US"}
        )
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should only find patterns from US records
        for pattern in result.patterns:
            assert "country=US" in pattern.path

        # Verify count - should be based on filtered data only
        us_records = [r for r in self.test_data if r["country"] == "US"]
        top_pattern = next(p for p in result.patterns if p.path == "country=US")
        assert top_pattern.count == len(us_records)

    def test_multiple_field_query(self):
        """Test filtering with multiple field constraints."""
        find_input = FindInput(
            data=self.test_data,
            fields=["country", "device", "user_type"],
            query={"country": "US", "device": "mobile"},
        )
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should only include records matching both constraints
        us_mobile_records = [
            r
            for r in self.test_data
            if r["country"] == "US" and r["device"] == "mobile"
        ]

        # Top pattern should represent all filtered records
        top_pattern = result.patterns[0]
        assert top_pattern.count == len(us_mobile_records)

        # All patterns should at least contain the first constraint
        for pattern in result.patterns:
            assert "country=US" in pattern.path

    def test_list_value_query(self):
        """Test query with list of acceptable values."""
        find_input = FindInput(
            data=self.test_data,
            fields=["country", "device"],
            query={"country": ["US", "CA"]},
        )
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should include records from US and CA only
        for pattern in result.patterns:
            assert ("country=US" in pattern.path) or ("country=CA" in pattern.path)
            assert "country=EU" not in pattern.path

    def test_query_no_matches(self):
        """Test query that matches no records."""
        find_input = FindInput(
            data=self.test_data,
            fields=["country", "device"],
            query={"country": "XX"},  # Non-existent country
        )
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should return empty list
        assert result.patterns == []

    def test_empty_query(self):
        """Test behavior with empty query dict."""
        find_input_with_query = FindInput(
            data=self.test_data, fields=["country", "device"], query={}
        )
        find_options = FindOptions()
        result_with_query = self.dataspot.find(find_input_with_query, find_options)

        # Should behave same as no query
        find_input_no_query = FindInput(
            data=self.test_data, fields=["country", "device"]
        )
        result_no_query = self.dataspot.find(find_input_no_query, find_options)
        assert len(result_with_query.patterns) == len(result_no_query.patterns)


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
        find_input = FindInput(data=self.filter_data, fields=["category", "type"])
        find_options_all = FindOptions()
        all_result = self.dataspot.find(find_input, find_options_all)

        # Apply min percentage filter
        find_options_filtered = FindOptions(min_percentage=30.0)
        filtered_result = self.dataspot.find(find_input, find_options_filtered)

        # All filtered patterns should have >= 30% concentration
        for pattern in filtered_result.patterns:
            assert pattern.percentage >= 30.0

        # Should have fewer patterns than unfiltered
        assert len(filtered_result.patterns) <= len(all_result.patterns)

    def test_max_percentage_filter(self):
        """Test maximum percentage filtering."""
        find_input = FindInput(data=self.filter_data, fields=["category", "type"])
        find_options = FindOptions(max_percentage=25.0)
        result = self.dataspot.find(find_input, find_options)

        # All patterns should have <= 25% concentration
        for pattern in result.patterns:
            assert pattern.percentage <= 25.0

    def test_min_count_filter(self):
        """Test minimum count filtering."""
        find_input = FindInput(data=self.filter_data, fields=["category", "type"])
        find_options = FindOptions(min_count=15)
        result = self.dataspot.find(find_input, find_options)

        # All patterns should have >= 15 records
        for pattern in result.patterns:
            assert pattern.count >= 15

    def test_max_depth_filter(self):
        """Test maximum depth filtering."""
        find_input = FindInput(
            data=self.filter_data, fields=["category", "type", "status"]
        )
        find_options = FindOptions(max_depth=2)
        result = self.dataspot.find(find_input, find_options)

        # All patterns should have depth <= 2
        for pattern in result.patterns:
            assert pattern.depth <= 2

        # Should not include any depth-3 patterns
        depth_3_patterns = [p for p in result.patterns if p.depth == 3]
        assert len(depth_3_patterns) == 0

    def test_contains_filter(self):
        """Test contains text filtering."""
        find_input = FindInput(data=self.filter_data, fields=["category", "type"])
        find_options = FindOptions(contains="cat_1")
        result = self.dataspot.find(find_input, find_options)

        # All patterns should contain "cat_1" in their path
        for pattern in result.patterns:
            assert "cat_1" in pattern.path

    def test_exclude_filter_single(self):
        """Test exclude filtering with single term."""
        find_input = FindInput(data=self.filter_data, fields=["category", "type"])
        find_options = FindOptions(exclude=["cat_0"])
        result = self.dataspot.find(find_input, find_options)

        # No patterns should contain "cat_0"
        for pattern in result.patterns:
            assert "cat_0" not in pattern.path

    def test_exclude_filter_list(self):
        """Test exclude filtering with list of terms."""
        find_input = FindInput(data=self.filter_data, fields=["category", "type"])
        find_options = FindOptions(exclude=["cat_0", "cat_1"])
        result = self.dataspot.find(find_input, find_options)

        # No patterns should contain either excluded term
        for pattern in result.patterns:
            assert "cat_0" not in pattern.path
            assert "cat_1" not in pattern.path

    def test_regex_filter(self):
        """Test regex pattern filtering."""
        # Filter for patterns containing "cat_" followed by even numbers
        find_input = FindInput(data=self.filter_data, fields=["category", "type"])
        find_options = FindOptions(regex=r"cat_[02468]")
        result = self.dataspot.find(find_input, find_options)

        # All patterns should match the regex
        regex_pattern = re.compile(r"cat_[02468]")
        for pattern in result.patterns:
            assert regex_pattern.search(pattern.path) is not None

    def test_limit_filter(self):
        """Test result limit filtering."""
        find_input = FindInput(
            data=self.filter_data, fields=["category", "type", "status"]
        )
        find_options_all = FindOptions()
        all_result = self.dataspot.find(find_input, find_options_all)

        find_options_limited = FindOptions(limit=5)
        limited_result = self.dataspot.find(find_input, find_options_limited)

        # Should return at most 5 patterns
        assert len(limited_result.patterns) <= 5
        assert len(limited_result.patterns) <= len(all_result.patterns)

        # Should return the top patterns (highest percentage first)
        if len(all_result.patterns) >= 5:
            assert len(limited_result.patterns) == 5
            # Should be ordered by percentage descending
            for i in range(len(limited_result.patterns) - 1):
                assert (
                    limited_result.patterns[i].percentage
                    >= limited_result.patterns[i + 1].percentage
                )

    def test_combined_filters(self):
        """Test combining multiple filters."""
        find_input = FindInput(
            data=self.filter_data, fields=["category", "type", "status"]
        )
        find_options = FindOptions(
            min_percentage=10.0,
            max_depth=2,
            contains="cat",
            exclude=["type_2"],
            limit=10,
        )
        result = self.dataspot.find(find_input, find_options)

        # Verify all filter conditions
        for pattern in result.patterns:
            assert pattern.percentage >= 10.0  # min_percentage
            assert pattern.depth <= 2  # max_depth
            assert "cat" in pattern.path  # contains
            assert "type_2" not in pattern.path  # exclude

        # Should respect limit
        assert len(result.patterns) <= 10

    def test_conflicting_filters(self):
        """Test behavior with conflicting filter values."""
        data = [{"x": i % 5} for i in range(100)]

        # Conflicting percentage filters
        find_input = FindInput(data=data, fields=["x"])
        find_options = FindOptions(
            min_percentage=50.0, max_percentage=30.0
        )  # max < min
        result = self.dataspot.find(find_input, find_options)

        # Should return empty list
        assert result.patterns == []


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
        builder_result = (
            self.builder.field("country", "US")
            .min_percentage(20)
            .execute(self.test_data, ["country", "device"])
        )

        # Using Dataspot directly
        find_input = FindInput(
            data=self.test_data, fields=["country", "device"], query={"country": "US"}
        )
        find_options = FindOptions(min_percentage=20.0)
        direct_result = self.dataspot.find(find_input, find_options)

        # Should produce identical results
        assert len(builder_result.patterns) == len(direct_result.patterns)
        for bp, dp in zip(
            builder_result.patterns, direct_result.patterns, strict=False
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
        ]

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
        """Test using pre-configured queries with actual data."""
        # Test fraud detection query
        fraud_query = create_fraud_query(self.dataspot)
        fraud_patterns = fraud_query.execute(self.test_data, ["country", "device"])

        assert len(fraud_patterns.patterns) >= 0
        # Should apply fraud detection defaults (min_percentage=5.0, max_depth=4)
        for pattern in fraud_patterns.patterns:
            assert pattern.percentage >= 5.0
            assert pattern.depth <= 4


class TestComplexQueryScenarios:
    """Test cases for complex query scenarios and combinations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
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
        ]

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
        """Test complex business intelligence scenario."""
        business_query = create_business_query(self.dataspot)

        # Chain multiple filters
        patterns = (
            business_query.field("country", "US")
            .min_percentage(15.0)
            .execute(self.test_data, ["country", "device", "user_type"])
        )

        # Should apply business defaults and additional filters
        assert len(patterns.patterns) >= 0
        for pattern in patterns.patterns:
            assert "country=US" in pattern.path
            assert pattern.percentage >= 15.0

    def test_fraud_detection_scenario(self):
        """Test fraud detection analysis scenario."""
        fraud_query = create_fraud_query(self.dataspot)

        patterns = (
            fraud_query.field("user_type", "premium")
            .contains("mobile")
            .execute(self.test_data, ["user_type", "device", "country"])
        )

        # Should find patterns meeting fraud detection criteria
        assert len(patterns.patterns) >= 0
        for pattern in patterns.patterns:
            assert "user_type=premium" in pattern.path
            assert "mobile" in pattern.path

    def test_progressive_filtering(self):
        """Test progressive filtering approach."""
        # Start broad
        broad_query = QueryBuilder(self.dataspot).min_percentage(10.0)
        broad_patterns = broad_query.execute(self.test_data, ["country", "device"])

        # Narrow down
        narrow_query = broad_query.copy().min_percentage(30.0).contains("US")
        narrow_patterns = narrow_query.execute(self.test_data, ["country", "device"])

        # Narrow should have fewer or equal patterns
        assert len(narrow_patterns.patterns) <= len(broad_patterns.patterns)

    def test_query_builder_reuse(self):
        """Test reusing QueryBuilder for multiple analyses."""
        base_query = QueryBuilder(self.dataspot).min_percentage(10.0)

        # Use for different field combinations
        country_patterns = base_query.execute(self.test_data, ["country"])
        device_patterns = base_query.execute(self.test_data, ["device"])
        combined_patterns = base_query.execute(self.test_data, ["country", "device"])

        # Should work for all combinations
        assert len(country_patterns.patterns) >= 0
        assert len(device_patterns.patterns) >= 0
        assert len(combined_patterns.patterns) >= 0

    def test_complex_query_and_filter_combination(self):
        """Test complex combination of query and pattern filters."""
        # Complex filtering scenario
        find_input = FindInput(
            data=self.test_data,
            fields=["country", "device", "user_type"],
            query={"country": ["US", "EU"]},  # Multiple countries
        )
        find_options = FindOptions(
            min_percentage=5.0, max_depth=2, contains="mobile", limit=10
        )
        result = self.dataspot.find(find_input, find_options)

        # Should apply all filters correctly
        for pattern in result.patterns:
            # Should only include US or EU
            assert ("country=US" in pattern.path) or ("country=EU" in pattern.path)
            assert pattern.percentage >= 5.0
            assert pattern.depth <= 2
            assert "mobile" in pattern.path

        assert len(result.patterns) <= 10

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
        """Test query performance with larger dataset."""
        # Generate larger dataset
        large_data = []
        for i in range(1000):
            large_data.append(
                {
                    "category": f"cat_{i % 10}",
                    "type": f"type_{i % 5}",
                    "status": "active" if i % 2 == 0 else "inactive",
                }
            )

        perf_query = create_data_quality_query(self.dataspot)
        patterns = perf_query.execute(large_data, ["category", "type"])

        # Should complete efficiently
        assert len(patterns.patterns) >= 0
