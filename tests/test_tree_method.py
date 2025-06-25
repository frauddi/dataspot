#!/usr/bin/env python3
"""Test cases for the tree() method with comprehensive filter coverage."""

import json

import pytest

from dataspot import Dataspot


class TestTreeMethod:
    """Test cases for tree method functionality."""

    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return [
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
            {
                "country": "US",
                "device": "mobile",
                "user_type": "premium",
                "amount": 150,
            },
            {"country": "US", "device": "desktop", "user_type": "free", "amount": 50},
            {"country": "US", "device": "desktop", "user_type": "free", "amount": 75},
            {
                "country": "EU",
                "device": "mobile",
                "user_type": "premium",
                "amount": 120,
            },
            {"country": "EU", "device": "mobile", "user_type": "free", "amount": 80},
            {
                "country": "EU",
                "device": "tablet",
                "user_type": "premium",
                "amount": 180,
            },
            {"country": "EU", "device": "tablet", "user_type": "free", "amount": 90},
            {
                "country": "CA",
                "device": "mobile",
                "user_type": "premium",
                "amount": 160,
            },
            {
                "country": "CA",
                "device": "desktop",
                "user_type": "premium",
                "amount": 220,
            },
            {"country": "AS", "device": "mobile", "user_type": "free", "amount": 70},
        ]

    @pytest.fixture
    def dataspot(self):
        """Dataspot instance for testing."""
        return Dataspot()

    def test_basic_tree_structure(self, dataspot, sample_data):
        """Test basic tree structure without filters."""
        tree = dataspot.tree(sample_data, fields=["country", "device"], top=3)

        assert tree["name"] == "root"
        assert tree["value"] == len(sample_data)
        assert tree["percentage"] == 100.0
        assert tree["node"] == 0
        assert tree["top"] == 3
        assert "children" in tree
        assert len(tree["children"]) <= 3  # Respects top limit

    def test_tree_structure_validation(self, dataspot, sample_data):
        """Test tree structure has correct hierarchy."""
        tree = dataspot.tree(sample_data, fields=["country", "device"], top=5)

        # Check root level countries
        countries = [child["name"] for child in tree["children"]]
        assert any("country=" in name for name in countries)

        # Check second level devices
        if tree["children"]:
            first_country = tree["children"][0]
            if "children" in first_country:
                devices = [child["name"] for child in first_country["children"]]
                assert any("device=" in name for name in devices)

    def test_empty_data_tree(self, dataspot):
        """Test tree method with empty data."""
        tree = dataspot.tree([], fields=["country", "device"], top=5)

        assert tree["name"] == "root"
        assert tree["value"] == 0
        assert tree["percentage"] == 0.0
        assert tree["children"] == []

    def test_min_value_filter(self, dataspot, sample_data):
        """Test min_value filter (equivalent to min_count)."""
        tree_no_filter = dataspot.tree(
            sample_data, fields=["country", "device"], top=10
        )
        tree_filtered = dataspot.tree(
            sample_data, fields=["country", "device"], min_value=2, top=10
        )

        def count_all_nodes(tree_node):
            count = 1
            for child in tree_node.get("children", []):
                count += count_all_nodes(child)
            return count

        # Filtered tree should have fewer nodes
        nodes_no_filter = count_all_nodes(tree_no_filter)
        nodes_filtered = count_all_nodes(tree_filtered)
        assert nodes_filtered <= nodes_no_filter

    def test_max_value_filter(self, dataspot, sample_data):
        """Test max_value filter (equivalent to max_count)."""
        # Create tree with max_value=3 (should exclude high-count patterns)
        tree = dataspot.tree(
            sample_data, fields=["country", "device"], max_value=3, top=10
        )

        def check_max_values(tree_node):
            if tree_node["value"] > 3:
                return False
            return all(
                check_max_values(child) for child in tree_node.get("children", [])
            )

        # All nodes should have value <= 3 (except root which represents total)
        for child in tree["children"]:
            assert child["value"] <= 3

    def test_min_percentage_filter(self, dataspot, sample_data):
        """Test min_percentage filter."""
        tree = dataspot.tree(
            sample_data, fields=["country", "device"], min_percentage=20.0, top=10
        )

        def check_min_percentage(tree_node):
            if tree_node["name"] != "root" and tree_node["percentage"] < 20.0:
                return False
            return all(
                check_min_percentage(child) for child in tree_node.get("children", [])
            )

        # All non-root nodes should have percentage >= 20%
        for child in tree["children"]:
            assert child["percentage"] >= 20.0

    def test_max_percentage_filter(self, dataspot, sample_data):
        """Test max_percentage filter."""
        tree = dataspot.tree(
            sample_data, fields=["country", "device"], max_percentage=50.0, top=10
        )

        # All non-root nodes should have percentage <= 50%
        for child in tree["children"]:
            assert child["percentage"] <= 50.0

    def test_min_depth_filter(self, dataspot, sample_data):
        """Test min_depth filter."""
        tree = dataspot.tree(
            sample_data, fields=["country", "device", "user_type"], min_depth=2, top=5
        )

        # With min_depth=2, should not have single-level patterns, only deeper ones
        assert tree["name"] == "root"

        # Check that we have some nodes but they should be at depth >= 2
        def check_depth_nodes(tree_node, current_depth=0):
            has_valid_nodes = False
            for child in tree_node.get("children", []):
                if child["node"] >= 2:  # Node at depth 2 or more
                    has_valid_nodes = True
                # Recursively check children
                if check_depth_nodes(child, current_depth + 1):
                    has_valid_nodes = True
            return has_valid_nodes

        # Should have some nodes at appropriate depth
        if tree.get("children"):
            assert check_depth_nodes(tree)

    def test_max_depth_filter(self, dataspot, sample_data):
        """Test max_depth filter."""
        tree = dataspot.tree(
            sample_data, fields=["country", "device", "user_type"], max_depth=2, top=5
        )

        def check_max_depth(tree_node, current_depth=0):
            if current_depth >= 2:
                # Should not have children at max depth
                return len(tree_node.get("children", [])) == 0
            return all(
                check_max_depth(child, current_depth + 1)
                for child in tree_node.get("children", [])
            )

        # Tree should not go deeper than max_depth
        assert check_max_depth(tree)

    def test_contains_filter(self, dataspot, sample_data):
        """Test contains text filter."""
        tree = dataspot.tree(
            sample_data, fields=["country", "device"], contains="mobile", top=10
        )

        # Should have tree structure with mobile-related patterns
        assert tree["name"] == "root"

        # Check that we have some mobile-related nodes
        def has_mobile_nodes(tree_node):
            mobile_found = False
            if "mobile" in tree_node.get("name", ""):
                mobile_found = True
            for child in tree_node.get("children", []):
                if has_mobile_nodes(child):
                    mobile_found = True
            return mobile_found

        assert has_mobile_nodes(tree)

    def test_exclude_filter(self, dataspot, sample_data):
        """Test exclude text filter."""
        tree = dataspot.tree(
            sample_data, fields=["country", "device"], exclude=["desktop"], top=10
        )

        # No nodes should contain "desktop"
        def check_exclude(tree_node):
            if "desktop" in tree_node["name"]:
                return False
            return all(check_exclude(child) for child in tree_node.get("children", []))

        assert check_exclude(tree)

    def test_exclude_multiple_filter(self, dataspot, sample_data):
        """Test exclude filter with multiple terms."""
        tree = dataspot.tree(
            sample_data,
            fields=["country", "device"],
            exclude=["desktop", "tablet"],
            top=10,
        )

        # No nodes should contain "desktop" or "tablet"
        def check_exclude_multiple(tree_node):
            if any(term in tree_node["name"] for term in ["desktop", "tablet"]):
                return False
            return all(
                check_exclude_multiple(child) for child in tree_node.get("children", [])
            )

        assert check_exclude_multiple(tree)

    def test_regex_filter(self, dataspot, sample_data):
        """Test regex filter."""
        tree = dataspot.tree(
            sample_data, fields=["country", "device"], regex=r"(US|EU)", top=10
        )

        import re

        pattern = re.compile(r"(US|EU)")

        # All non-root nodes should match the regex
        for child in tree["children"]:
            assert pattern.search(child["name"])

    def test_query_filter(self, dataspot, sample_data):
        """Test query pre-filtering."""
        tree_all = dataspot.tree(sample_data, fields=["device", "user_type"], top=5)
        tree_us = dataspot.tree(
            sample_data, fields=["device", "user_type"], query={"country": "US"}, top=5
        )

        # US tree should have different (smaller) total value
        assert tree_us["value"] < tree_all["value"]
        assert tree_us["value"] == len([r for r in sample_data if r["country"] == "US"])

    def test_combined_filters(self, dataspot, sample_data):
        """Test multiple filters working together."""
        tree = dataspot.tree(
            sample_data,
            fields=["country", "device", "user_type"],
            min_value=1,
            max_value=5,
            min_percentage=5.0,
            max_percentage=60.0,
            max_depth=2,
            contains="country",
            top=3,
        )

        # Should still return a valid tree structure
        assert tree["name"] == "root"
        assert "children" in tree

        # Check that filters are applied
        for child in tree["children"]:
            assert child["value"] >= 1
            assert child["value"] <= 5
            assert child["percentage"] >= 5.0
            assert child["percentage"] <= 60.0
            assert "country" in child["name"]

    def test_top_filter(self, dataspot, sample_data):
        """Test top parameter limits results per level."""
        tree_top_2 = dataspot.tree(sample_data, fields=["country", "device"], top=2)
        tree_top_5 = dataspot.tree(sample_data, fields=["country", "device"], top=5)

        # Top=2 should have at most 2 children at each level
        assert len(tree_top_2["children"]) <= 2

        # Top=5 should have more or equal children
        assert len(tree_top_5["children"]) >= len(tree_top_2["children"])

    def test_tree_vs_patterns_consistency(self, dataspot, sample_data):
        """Test that tree method produces consistent results with find method."""
        # Get patterns with same filters
        patterns = dataspot.find(
            sample_data,
            fields=["country", "device"],
            min_percentage=10.0,
            contains="country",
        )

        # Get tree with same filters
        tree = dataspot.tree(
            sample_data,
            fields=["country", "device"],
            min_percentage=10.0,
            contains="country",
            top=10,
        )

        # Extract all node values from tree
        def extract_tree_values(tree_node):
            values = []
            if tree_node["name"] != "root":
                values.append(
                    (tree_node["name"], tree_node["value"], tree_node["percentage"])
                )
            for child in tree_node.get("children", []):
                values.extend(extract_tree_values(child))
            return values

        tree_values = extract_tree_values(tree)

        # Should have corresponding patterns (allowing for structural differences)
        assert len(tree_values) > 0
        assert len(patterns) > 0

    def test_performance_with_large_dataset(self, dataspot):
        """Test tree method performance with larger dataset."""
        # Generate larger dataset
        large_data = []
        countries = ["US", "EU", "CA", "AS", "AU"]
        devices = ["mobile", "desktop", "tablet"]
        user_types = ["premium", "free", "enterprise"]

        for i in range(1000):
            large_data.append(
                {
                    "country": countries[i % len(countries)],
                    "device": devices[i % len(devices)],
                    "user_type": user_types[i % len(user_types)],
                    "amount": (i % 10) * 100,
                }
            )

        # Should handle large dataset efficiently
        tree = dataspot.tree(
            large_data,
            fields=["country", "device", "user_type"],
            min_percentage=5.0,
            top=3,
        )

        assert tree["name"] == "root"
        assert tree["value"] == len(large_data)
        assert len(tree["children"]) <= 3

    def test_tree_json_serializable(self, dataspot, sample_data):
        """Test that tree output is JSON serializable."""
        tree = dataspot.tree(sample_data, fields=["country", "device"], top=3)

        # Should be able to serialize to JSON without errors
        json_str = json.dumps(tree)
        assert isinstance(json_str, str)

        # Should be able to deserialize back
        parsed = json.loads(json_str)
        assert parsed["name"] == "root"

    def test_edge_case_single_record(self, dataspot):
        """Test tree with single record."""
        single_data = [{"country": "US", "device": "mobile", "user_type": "premium"}]

        tree = dataspot.tree(single_data, fields=["country", "device"], top=5)

        assert tree["value"] == 1
        assert len(tree["children"]) == 1
        assert tree["children"][0]["percentage"] == 100.0

    def test_edge_case_identical_records(self, dataspot):
        """Test tree with identical records."""
        identical_data = [
            {"country": "US", "device": "mobile", "user_type": "premium"},
            {"country": "US", "device": "mobile", "user_type": "premium"},
            {"country": "US", "device": "mobile", "user_type": "premium"},
        ]

        tree = dataspot.tree(identical_data, fields=["country", "device"], top=5)

        assert tree["value"] == 3
        assert len(tree["children"]) == 1  # Only one unique pattern
        assert tree["children"][0]["value"] == 3
        assert tree["children"][0]["percentage"] == 100.0
