"""Tests for query filtering and pattern filtering functionality.

This module tests all filtering capabilities including query filters,
pattern filters, and their combinations.
"""

import re

import pytest

from dataspot import Dataspot


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
        for pattern in patterns:
            assert "country=US" in pattern.path

        # Verify count - should be based on filtered data only
        us_records = [r for r in self.test_data if r["country"] == "US"]
        top_pattern = next(p for p in patterns if p.path == "country=US")
        assert top_pattern.count == len(us_records)

    def test_single_value_query_string(self):
        """Test query with single string value."""
        query = {"device": "mobile"}
        patterns = self.dataspot.find(
            self.test_data, ["device", "user_type"], query=query
        )

        # All patterns should be from mobile device records
        mobile_patterns = [p for p in patterns if "device=mobile" in p.path]
        assert len(mobile_patterns) == len(patterns)

        # Verify percentages are calculated based on filtered data
        mobile_records = [r for r in self.test_data if r["device"] == "mobile"]
        top_pattern = patterns[0]
        assert top_pattern.count <= len(mobile_records)

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
        top_pattern = patterns[0]
        assert top_pattern.count == len(us_mobile_records)

        # Should have patterns that contain both query constraints
        combined_patterns = [
            p for p in patterns if "country=US" in p.path and "device=mobile" in p.path
        ]
        assert len(combined_patterns) > 0

        # All patterns should at least contain the first constraint
        for pattern in patterns:
            assert "country=US" in pattern.path

    def test_list_value_query(self):
        """Test query with list of acceptable values."""
        query = {"country": ["US", "CA"]}
        patterns = self.dataspot.find(
            self.test_data, ["country", "device"], query=query
        )

        # Should include records from US and CA only
        for pattern in patterns:
            assert ("country=US" in pattern.path) or ("country=CA" in pattern.path)
            assert "country=EU" not in pattern.path

        # Verify total count
        us_ca_records = [r for r in self.test_data if r["country"] in ["US", "CA"]]
        total_filtered_count = sum(p.count for p in patterns if p.depth == 1)
        assert total_filtered_count == len(us_ca_records)

    def test_mixed_query_types(self):
        """Test query with mix of single values and lists."""
        query = {"country": ["US", "EU"], "device": "mobile"}
        patterns = self.dataspot.find(
            self.test_data, ["country", "device", "user_type"], query=query
        )

        # Should only include US/EU mobile records
        filtered_records = [
            r
            for r in self.test_data
            if r["country"] in ["US", "EU"] and r["device"] == "mobile"
        ]

        # Verify filtering worked correctly
        depth_1_patterns = [p for p in patterns if p.depth == 1]
        total_count = sum(p.count for p in depth_1_patterns)
        assert total_count == len(filtered_records)

    def test_query_no_matches(self):
        """Test query that matches no records."""
        query = {"country": "XX"}  # Non-existent country
        patterns = self.dataspot.find(
            self.test_data, ["country", "device"], query=query
        )

        # Should return empty list
        assert patterns == []

    def test_query_with_none_values(self):
        """Test query handling of None values."""
        data_with_none = self.test_data + [
            {"country": None, "device": "mobile", "user_type": "free"}
        ]

        query = {"country": "US"}
        patterns = self.dataspot.find(
            data_with_none, ["country", "device"], query=query
        )

        # Should not include the None record
        for pattern in patterns:
            # None values are converted to empty strings, so check we don't have those patterns
            assert "country=None" not in pattern.path
            assert not pattern.path.endswith("country=")  # No empty country values

    def test_query_type_coercion(self):
        """Test that query values are properly type-coerced for comparison."""
        # Data with mixed types
        mixed_data = [
            {"status": 1, "type": "active"},
            {"status": "1", "type": "active"},
            {"status": 2, "type": "inactive"},
        ]

        # Query with int value should match both int and string "1"
        query = {"status": 1}
        patterns = self.dataspot.find(mixed_data, ["status", "type"], query=query)

        # Should find patterns for status=1
        status_patterns = [p for p in patterns if "status=1" in p.path]
        assert len(status_patterns) > 0

    def test_empty_query(self):
        """Test behavior with empty query dict."""
        query = {}
        patterns = self.dataspot.find(
            self.test_data, ["country", "device"], query=query
        )

        # Should behave same as no query
        patterns_no_query = self.dataspot.find(self.test_data, ["country", "device"])
        assert len(patterns) == len(patterns_no_query)

    def test_query_field_not_in_data(self):
        """Test query with field that doesn't exist in data."""
        query = {"nonexistent_field": "value"}
        patterns = self.dataspot.find(
            self.test_data, ["country", "device"], query=query
        )

        # Should return empty or handle gracefully
        assert isinstance(patterns, list)


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
        for pattern in filtered:
            assert pattern.percentage >= 30.0

        # Should have fewer patterns than unfiltered
        assert len(filtered) <= len(all_patterns)

    def test_max_percentage_filter(self):
        """Test maximum percentage filtering."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], max_percentage=25
        )

        # All patterns should have <= 25% concentration
        for pattern in filtered:
            assert pattern.percentage <= 25.0

    def test_min_count_filter(self):
        """Test minimum count filtering."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], min_count=15
        )

        # All patterns should have >= 15 records
        for pattern in filtered:
            assert pattern.count >= 15

    def test_max_count_filter(self):
        """Test maximum count filtering."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], max_count=25
        )

        # All patterns should have <= 25 records
        for pattern in filtered:
            assert pattern.count <= 25

    def test_min_depth_filter(self):
        """Test minimum depth filtering."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type", "status"], min_depth=2
        )

        # All patterns should have depth >= 2
        for pattern in filtered:
            assert pattern.depth >= 2

        # Should not include any depth-1 patterns
        depth_1_patterns = [p for p in filtered if p.depth == 1]
        assert len(depth_1_patterns) == 0

    def test_max_depth_filter(self):
        """Test maximum depth filtering."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type", "status"], max_depth=2
        )

        # All patterns should have depth <= 2
        for pattern in filtered:
            assert pattern.depth <= 2

        # Should not include any depth-3 patterns
        depth_3_patterns = [p for p in filtered if p.depth == 3]
        assert len(depth_3_patterns) == 0

    def test_contains_filter(self):
        """Test contains text filtering."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], contains="cat_1"
        )

        # All patterns should contain "cat_1" in their path
        for pattern in filtered:
            assert "cat_1" in pattern.path

    def test_exclude_filter_single(self):
        """Test exclude filtering with single term."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], exclude="cat_0"
        )

        # No patterns should contain "cat_0"
        for pattern in filtered:
            assert "cat_0" not in pattern.path

    def test_exclude_filter_list(self):
        """Test exclude filtering with list of terms."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], exclude=["cat_0", "cat_1"]
        )

        # No patterns should contain either excluded term
        for pattern in filtered:
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
        for pattern in filtered:
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
        assert len(limited) <= 5
        assert len(limited) <= len(all_patterns)

        # Should return the top patterns (highest percentage first)
        if len(all_patterns) >= 5:
            assert len(limited) == 5
            # Limited patterns should be a subset of all patterns with highest percentages
            for limited_pattern in limited:
                assert limited_pattern in all_patterns
            # Should be ordered by percentage descending
            for i in range(len(limited) - 1):
                assert limited[i].percentage >= limited[i + 1].percentage

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
        for pattern in filtered:
            assert pattern.percentage >= 10.0  # min_percentage
            assert pattern.depth <= 2  # max_depth
            assert "cat" in pattern.path  # contains
            assert "type_2" not in pattern.path  # exclude

        # Should respect limit
        assert len(filtered) <= 10

    def test_percentage_range_filtering(self):
        """Test filtering within percentage range."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], min_percentage=15, max_percentage=35
        )

        # All patterns should be within the range
        for pattern in filtered:
            assert 15.0 <= pattern.percentage <= 35.0

    def test_count_range_filtering(self):
        """Test filtering within count range."""
        filtered = self.dataspot.find(
            self.filter_data, ["category", "type"], min_count=10, max_count=30
        )

        # All patterns should be within the range
        for pattern in filtered:
            assert 10 <= pattern.count <= 30

    def test_depth_range_filtering(self):
        """Test filtering within depth range."""
        filtered = self.dataspot.find(
            self.filter_data,
            ["category", "type", "status", "priority"],
            min_depth=2,
            max_depth=3,
        )

        # All patterns should be within the range
        for pattern in filtered:
            assert 2 <= pattern.depth <= 3

    def test_invalid_regex_filter(self):
        """Test behavior with invalid regex pattern."""
        with pytest.raises(re.error):
            self.dataspot.find(
                self.filter_data, ["category", "type"], regex="[invalid regex("
            )

    def test_zero_limit_filter(self):
        """Test behavior with zero limit."""
        filtered = self.dataspot.find(self.filter_data, ["category", "type"], limit=0)

        # Should return empty list
        assert filtered == []

    def test_negative_limit_filter(self):
        """Test behavior with negative limit."""
        # Implementation might handle this differently
        filtered = self.dataspot.find(self.filter_data, ["category", "type"], limit=-1)

        # Should either return empty list or handle gracefully
        assert isinstance(filtered, list)


class TestAdvancedFiltering:
    """Test cases for advanced filtering scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_filter_order_independence(self):
        """Test that filter order doesn't affect results."""
        data = [{"x": i % 3, "y": i % 2} for i in range(20)]

        # Apply same filters in different orders
        result1 = self.dataspot.find(
            data, ["x", "y"], min_percentage=10, max_depth=2, limit=5
        )

        result2 = self.dataspot.find(
            data, ["x", "y"], max_depth=2, limit=5, min_percentage=10
        )

        # Results should be identical
        assert len(result1) == len(result2)
        for p1, p2 in zip(result1, result2, strict=False):
            assert p1.path == p2.path
            assert p1.count == p2.count
            assert p1.percentage == p2.percentage

    def test_filter_edge_values(self):
        """Test filters with edge values."""
        data = [{"field": f"value_{i}"} for i in range(10)]

        # Test with 0 percentage (should include patterns with 0%)
        filtered = self.dataspot.find(data, ["field"], min_percentage=0)
        assert len(filtered) > 0

        # Test with 100 percentage (should include only 100% patterns)
        single_data = [{"field": "single_value"}]
        filtered_100 = self.dataspot.find(single_data, ["field"], max_percentage=100)
        assert all(p.percentage <= 100.0 for p in filtered_100)

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
        assert filtered == []

        # Conflicting count filters
        filtered_count = self.dataspot.find(
            data,
            ["x"],
            min_count=50,
            max_count=10,  # max < min
        )

        # Should return empty list
        assert filtered_count == []

    def test_filter_with_empty_patterns(self):
        """Test filtering when no patterns exist."""
        # Empty data
        empty_patterns = self.dataspot.find([], ["field"], min_percentage=10)
        assert empty_patterns == []

        # Data that produces no patterns after initial filtering
        no_match_data = [{"x": "value"}]
        query_no_match = {"x": "nonexistent"}
        no_patterns = self.dataspot.find(
            no_match_data, ["x"], query=query_no_match, min_percentage=50
        )
        assert no_patterns == []

    def test_filter_preserves_pattern_order(self):
        """Test that filtering preserves pattern ordering."""
        data = (
            [{"priority": "high"}] * 30  # 30% high priority
            + [{"priority": "medium"}] * 50  # 50% medium priority
            + [{"priority": "low"}] * 20  # 20% low priority
        )

        patterns = self.dataspot.find(data, ["priority"], min_percentage=25)

        # Should be ordered by percentage (highest first)
        for i in range(len(patterns) - 1):
            assert patterns[i].percentage >= patterns[i + 1].percentage

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
        for pattern in result:
            assert pattern.percentage >= 8.0
            assert pattern.depth <= 2
            assert "enterprise" in pattern.path
            # Query filter ensures only north/south regions
            assert ("region=north" in pattern.path) or ("region=south" in pattern.path)

        assert len(result) <= 5
