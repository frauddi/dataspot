"""Unit tests for the Tree class.

This module tests the Tree class in isolation, focusing on its hierarchical
tree building functionality and JSON output structure.
"""

import pytest

from dataspot.analyzers.tree_analyzer import Tree
from dataspot.exceptions import DataspotError
from dataspot.models.tree import TreeOutput


class TestTreeCore:
    """Test cases for core Tree functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tree = Tree()

    def test_initialization(self):
        """Test that Tree initializes correctly."""
        assert isinstance(self.tree, Tree)
        assert hasattr(self.tree, "preprocessor_manager")
        assert hasattr(self.tree, "preprocessors")

    def test_execute_with_empty_data(self):
        """Test execute method with empty data."""
        result = self.tree.execute([], ["field1", "field2"])

        # Should return empty tree structure
        assert isinstance(result, TreeOutput)
        assert result.name == "root"
        assert result.children == []
        assert result.value == 0
        assert result.percentage == 0.0
        assert result.node == 0
        assert result.top == 5  # Default top value

    def test_execute_with_empty_fields(self):
        """Test execute method with empty fields list."""
        data = [{"a": 1, "b": 2}]
        result = self.tree.execute(data, [])

        # Should return root-only tree
        assert isinstance(result, TreeOutput)
        assert result.name == "root"
        assert result.value == 1  # One record
        assert result.percentage == 100.0

    def test_execute_with_invalid_data(self):
        """Test execute method with invalid data."""
        with pytest.raises(DataspotError, match="Data must be a list of dictionaries"):
            self.tree.execute(None, ["field1"])  # type: ignore

    def test_execute_basic_tree_building(self):
        """Test basic tree building functionality."""
        data = [
            {"country": "US", "device": "mobile"},
            {"country": "US", "device": "desktop"},
            {"country": "EU", "device": "mobile"},
        ]

        result = self.tree.execute(data, ["country", "device"])

        # Check root structure
        assert isinstance(result, TreeOutput)
        assert result.name == "root"
        assert result.value == 3
        assert result.percentage == 100.0
        assert result.node == 0
        assert result.top == 5

        # Check children exist
        assert result.children is not None
        assert len(result.children) > 0
        assert all(hasattr(child, "name") for child in result.children)

    def test_execute_with_custom_top(self):
        """Test execute method with custom top parameter."""
        data = [
            {"country": "US", "device": "mobile"},
            {"country": "EU", "device": "desktop"},
        ]

        result = self.tree.execute(data, ["country", "device"], top=3)

        assert isinstance(result, TreeOutput)
        assert result.top == 3

    def test_execute_with_query_filter(self):
        """Test execute method with query filtering."""
        data = [
            {"country": "US", "device": "mobile", "active": True},
            {"country": "US", "device": "desktop", "active": False},
            {"country": "EU", "device": "mobile", "active": True},
        ]

        # Filter to only active records
        query = {"active": True}
        result = self.tree.execute(data, ["country", "device"], query=query)

        # Should only include 2 active records
        assert isinstance(result, TreeOutput)
        assert result.value == 2
        assert result.percentage == 100.0

    def test_build_empty_tree(self):
        """Test _build_empty_tree method."""
        result = self.tree._build_empty_tree(top=10)

        expected = {
            "name": "root",
            "children": [],
            "value": 0,
            "percentage": 0.0,
            "node": 0,
            "top": 10,
        }

        assert result == expected


class TestTreeStructure:
    """Test cases for tree structure validation and properties."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tree = Tree()

    def test_tree_hierarchical_structure(self):
        """Test that tree builds correct hierarchical structure."""
        data = [
            {"level1": "A", "level2": "X", "level3": "1"},
            {"level1": "A", "level2": "X", "level3": "2"},
            {"level1": "A", "level2": "Y", "level3": "1"},
            {"level1": "B", "level2": "X", "level3": "1"},
        ]

        result = self.tree.execute(data, ["level1", "level2", "level3"])

        # Check root
        assert isinstance(result, TreeOutput)
        assert result.value == 4
        assert result.percentage == 100.0
        assert result.children

        # Check that children have proper structure
        for child in result.children:
            assert hasattr(child, "name")
            assert hasattr(child, "value")
            assert hasattr(child, "percentage")
            assert hasattr(child, "node")
            assert hasattr(child, "children")
            assert isinstance(child.children, list) or child.children is None

    def test_tree_percentage_calculations(self):
        """Test that tree calculates percentages correctly."""
        data = [
            {"category": "A", "type": "X"},
            {"category": "A", "type": "Y"},
            {"category": "B", "type": "X"},
        ]

        result = self.tree.execute(data, ["category", "type"])

        # Root should be 100%
        assert isinstance(result, TreeOutput)
        assert result.percentage == 100.0
        assert result.value == 3

        # Children percentages should be based on total
        for child in result.children:
            expected_percentage = (child.value / 3) * 100
            assert abs(child.percentage - expected_percentage) < 0.01

    def test_tree_node_numbering(self):
        """Test that tree assigns node numbers correctly."""
        data = [
            {"a": 1, "b": 2},
            {"a": 1, "b": 3},
        ]

        result = self.tree.execute(data, ["a", "b"])

        # Root should be node 0
        assert isinstance(result, TreeOutput)
        assert result.node == 0

        # Children should have incrementing node numbers
        node_numbers = [child.node for child in result.children]
        assert all(isinstance(num, int) for num in node_numbers)
        assert all(num > 0 for num in node_numbers)

    def test_tree_with_single_field(self):
        """Test tree building with single field."""
        data = [
            {"category": "A"},
            {"category": "A"},
            {"category": "B"},
        ]

        result = self.tree.execute(data, ["category"])

        assert isinstance(result, TreeOutput)
        assert result.value == 3
        assert len(result.children) >= 1

        # Children might not have 'children' field if they are leaf nodes
        for child in result.children:
            # Check if children field exists, and if so, it should be a list
            if child.children is not None:
                assert isinstance(child.children, list)

    def test_tree_with_multiple_fields(self):
        """Test tree building with multiple fields."""
        data = [
            {"field1": "A", "field2": "X", "field3": "1"},
            {"field1": "A", "field2": "Y", "field3": "2"},
        ]

        result = self.tree.execute(data, ["field1", "field2", "field3"])

        # Should build multi-level hierarchy
        assert isinstance(result, TreeOutput)
        assert result.value == 2
        assert result.children

        # Some children should have their own children
        has_grandchildren = any(
            child.children is not None and len(child.children) > 0
            for child in result.children
        )
        assert has_grandchildren


class TestTreeFiltering:
    """Test cases for tree filtering functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tree = Tree()

    def test_tree_with_min_value_filter(self):
        """Test tree building with min_value filter."""
        data = [
            {"category": "A", "type": "X"},
            {"category": "A", "type": "X"},
            {"category": "B", "type": "Y"},
        ]

        result = self.tree.execute(data, ["category", "type"], min_value=2)

        # Should only include nodes with at least 2 records
        def check_min_value(node):
            # Check the current node
            if hasattr(node, "value") and hasattr(node, "node"):
                if node.value < 2 and node.node != 0:  # Root can have any value
                    raise AssertionError(
                        f"Node with value {node.value} should have been filtered out"
                    )

            # Check children if they exist
            if hasattr(node, "children") and node.children:
                for child in node.children:
                    check_min_value(child)

        check_min_value(result)

    def test_tree_with_min_percentage_filter(self):
        """Test tree building with min_percentage filter."""
        data = [
            {"category": "A", "type": "X"},
            {"category": "A", "type": "X"},
            {"category": "A", "type": "X"},
            {"category": "B", "type": "Y"},
        ]

        result = self.tree.execute(data, ["category", "type"], min_percentage=50)

        # Should only include nodes with at least 50% concentration
        def check_min_percentage(node):
            if hasattr(node, "percentage") and hasattr(node, "node"):
                assert node.percentage >= 50 or node.node == 0  # Root can be 100%

            # Check children if they exist
            if hasattr(node, "children") and node.children:
                for child in node.children:
                    check_min_percentage(child)

        check_min_percentage(result)

    def test_tree_with_max_depth_filter(self):
        """Test tree building with max_depth filter."""
        data = [
            {"level1": "A", "level2": "X", "level3": "1", "level4": "alpha"},
            {"level1": "A", "level2": "Y", "level3": "2", "level4": "beta"},
        ]

        result = self.tree.execute(
            data, ["level1", "level2", "level3", "level4"], max_depth=2
        )

        # Should not go deeper than 2 levels
        def check_max_depth(node, current_depth=0):
            if current_depth >= 2:
                # At max depth, should not have children or have empty children
                if hasattr(node, "children") and node.children:
                    assert len(node.children) == 0 or all(
                        not hasattr(child, "children")
                        or not child.children
                        or len(child.children) == 0
                        for child in node.children
                    )
            else:
                if hasattr(node, "children") and node.children:
                    for child in node.children:
                        check_max_depth(child, current_depth + 1)

        check_max_depth(result)

    def test_tree_with_text_filters(self):
        """Test tree building with text filtering."""
        data = [
            {"category": "mobile_device", "type": "phone"},
            {"category": "desktop_computer", "type": "laptop"},
            {"category": "mobile_tablet", "type": "ipad"},
        ]

        # Filter to only include nodes containing "mobile"
        result = self.tree.execute(data, ["category", "type"], contains="mobile")

        # Check that we have some results and they contain mobile
        assert result.value > 0
        assert result.children

        # Look for nodes that should contain "mobile"
        mobile_nodes = []

        def collect_mobile_nodes(node):
            if hasattr(node, "name") and "mobile" in node.name:
                mobile_nodes.append(node)
            if hasattr(node, "children") and node.children:
                for child in node.children:
                    collect_mobile_nodes(child)

        collect_mobile_nodes(result)
        assert len(mobile_nodes) > 0, (
            "Should find at least one node containing 'mobile'"
        )


class TestTreeEdgeCases:
    """Test edge cases and error conditions for Tree."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tree = Tree()

    def test_tree_with_none_values(self):
        """Test tree building with None values in data."""
        data = [
            {"field1": None, "field2": "value"},
            {"field1": "test", "field2": None},
            {"field1": "test", "field2": "value"},
        ]

        result = self.tree.execute(data, ["field1", "field2"])

        assert isinstance(result, TreeOutput)
        assert result.value == 3
        # Should handle None values gracefully

    def test_tree_with_mixed_types(self):
        """Test tree building with mixed data types."""
        data = [
            {"field1": "string", "field2": 123},
            {"field1": 456, "field2": "another_string"},
            {"field1": True, "field2": [1, 2, 3]},
        ]

        result = self.tree.execute(data, ["field1", "field2"])

        assert isinstance(result, TreeOutput)
        assert result.value == 3
        # Should handle mixed types without crashing

    def test_tree_with_unicode_data(self):
        """Test tree building with unicode characters."""
        data = [
            {"país": "España", "categoría": "técnico"},
            {"país": "México", "categoría": "ventas"},
            {"país": "España", "categoría": "marketing"},
        ]

        result = self.tree.execute(data, ["país", "categoría"])

        assert isinstance(result, TreeOutput)
        assert result.value == 3

        # Should handle unicode correctly in node names
        has_spanish_nodes = any("España" in child.name for child in result.children)
        assert has_spanish_nodes

    def test_tree_with_large_dataset(self):
        """Test tree building with large dataset for performance."""
        # Create a dataset with 500 records
        data = [
            {"category": f"cat_{i % 10}", "value": f"val_{i % 5}", "id": i}
            for i in range(500)
        ]

        result = self.tree.execute(data, ["category", "value"], top=3)

        assert isinstance(result, TreeOutput)
        assert result.value == 500
        assert result.top == 3

        # Should complete reasonably quickly and not cause memory issues

    def test_tree_json_serializable(self):
        """Test that tree output is JSON serializable."""
        import json

        data = [
            {"category": "A", "type": "X"},
            {"category": "B", "type": "Y"},
        ]

        result = self.tree.execute(data, ["category", "type"])

        # Should be able to serialize to JSON without errors using to_dict()
        result_dict = result.to_dict()
        json_str = json.dumps(result_dict)
        assert isinstance(json_str, str)

        # Should be able to deserialize back
        parsed = json.loads(json_str)
        assert parsed == result_dict

    def test_tree_with_empty_strings(self):
        """Test tree building with empty string values."""
        data = [
            {"field1": "", "field2": "value"},
            {"field1": "test", "field2": ""},
            {"field1": "", "field2": ""},
        ]

        result = self.tree.execute(data, ["field1", "field2"])

        assert isinstance(result, TreeOutput)
        assert result.value == 3
        # Should handle empty strings gracefully
