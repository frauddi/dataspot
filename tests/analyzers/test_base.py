"""Unit tests for the Base class.

This module tests the Base class in isolation, focusing on its core
functionality including tree building, preprocessing, query filtering,
and data validation that is shared across all analyzers.
"""

import pytest

from dataspot.analyzers.base import Base
from dataspot.exceptions import DataspotError


class TestBaseInitialization:
    """Test cases for Base class initialization and setup."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base = Base()

    def test_initialization(self):
        """Test that Base initializes correctly."""
        assert isinstance(self.base, Base)
        assert hasattr(self.base, "preprocessor_manager")
        assert self.base.preprocessor_manager is not None

    def test_preprocessors_property(self):
        """Test preprocessors property getter and setter."""
        # Initially should be empty
        assert self.base.preprocessors == {}

        # Test setting
        test_preprocessor = lambda x: x.upper()  # noqa: E731
        test_dict = {"test_field": test_preprocessor}
        self.base.preprocessors = test_dict

        assert self.base.preprocessors == test_dict

    def test_add_preprocessor(self):
        """Test adding custom preprocessors."""

        def test_preprocessor(value):
            return f"processed_{value}"

        self.base.add_preprocessor("test_field", test_preprocessor)

        assert "test_field" in self.base.preprocessors
        assert self.base.preprocessors["test_field"] == test_preprocessor


class TestBaseDataValidation:
    """Test cases for data validation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base = Base()

    def test_validate_data_with_valid_data(self):
        """Test data validation with valid input."""
        valid_data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]

        # Should not raise any exception
        self.base._validate_data(valid_data)

    def test_validate_data_with_empty_list(self):
        """Test data validation with empty list."""
        empty_data = []

        # Should not raise any exception
        self.base._validate_data(empty_data)

    def test_validate_data_with_none(self):
        """Test data validation with None input."""
        with pytest.raises(DataspotError, match="Data must be a list of dictionaries"):
            self.base._validate_data(None)  # type: ignore

    def test_validate_data_with_string(self):
        """Test data validation with string input."""
        with pytest.raises(DataspotError, match="Data must be a list of dictionaries"):
            self.base._validate_data("not a list")  # type: ignore

    def test_validate_data_with_non_dict_records(self):
        """Test data validation with non-dictionary records."""
        invalid_data = ["string1", "string2"]

        with pytest.raises(DataspotError, match="Data must contain dictionary records"):
            self.base._validate_data(invalid_data)  # type: ignore

    def test_validate_data_with_mixed_types(self):
        """Test data validation with mixed record types."""
        mixed_data = [{"valid": "dict"}, "invalid_string"]

        # Should pass because it only checks the first record
        self.base._validate_data(mixed_data)  # type: ignore


class TestBaseQueryFiltering:
    """Test cases for query filtering functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base = Base()
        self.test_data = [
            {"country": "US", "device": "mobile", "active": True},
            {"country": "EU", "device": "desktop", "active": False},
            {"country": "US", "device": "desktop", "active": True},
            {"country": "EU", "device": "mobile", "active": True},
        ]

    def test_filter_data_by_query_no_query(self):
        """Test query filtering with no query."""
        result = self.base._filter_data_by_query(self.test_data, None)

        assert result == self.test_data
        assert len(result) == 4

    def test_filter_data_by_query_single_constraint(self):
        """Test query filtering with single constraint."""
        query = {"country": "US"}
        result = self.base._filter_data_by_query(self.test_data, query)

        assert len(result) == 2
        assert all(record["country"] == "US" for record in result)

    def test_filter_data_by_query_multiple_constraints(self):
        """Test query filtering with multiple constraints."""
        query = {"country": "US", "active": True}
        result = self.base._filter_data_by_query(self.test_data, query)

        assert len(result) == 2
        assert all(
            record["country"] == "US" and record["active"] is True for record in result
        )

    def test_filter_data_by_query_list_constraint(self):
        """Test query filtering with list constraint."""
        query = {"country": ["US", "EU"]}
        result = self.base._filter_data_by_query(self.test_data, query)

        assert len(result) == 4  # All records match

        # Test with partial list
        query = {"country": ["US"]}
        result = self.base._filter_data_by_query(self.test_data, query)
        assert len(result) == 2

    def test_filter_data_by_query_no_matches(self):
        """Test query filtering with no matching records."""
        query = {"country": "NONEXISTENT"}
        result = self.base._filter_data_by_query(self.test_data, query)

        assert len(result) == 0
        assert result == []

    def test_matches_query_basic(self):
        """Test basic query matching logic."""
        record = {"country": "US", "device": "mobile"}

        assert self.base._matches_query(record, {"country": "US"})
        assert not self.base._matches_query(record, {"country": "EU"})
        assert self.base._matches_query(record, {"country": "US", "device": "mobile"})
        assert not self.base._matches_query(
            record, {"country": "US", "device": "desktop"}
        )

    def test_matches_query_with_types(self):
        """Test query matching with different data types."""
        record = {"number": 123, "boolean": True, "string": "test"}

        # String conversion should work
        assert self.base._matches_query(record, {"number": "123"})
        assert self.base._matches_query(record, {"number": 123})
        assert self.base._matches_query(record, {"boolean": "True"})
        assert self.base._matches_query(record, {"boolean": True})

    def test_matches_query_missing_field(self):
        """Test query matching with missing fields."""
        record = {"country": "US"}

        # Missing field should not match
        assert not self.base._matches_query(record, {"missing_field": "value"})


class TestBaseTreeBuilding:
    """Test cases for tree building functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base = Base()

    def test_build_tree_basic(self):
        """Test basic tree building."""
        data = [
            {"country": "US", "device": "mobile"},
            {"country": "US", "device": "desktop"},
            {"country": "EU", "device": "mobile"},
        ]

        tree = self.base._build_tree(data, ["country", "device"])

        assert "children" in tree
        assert "country=US" in tree["children"]
        assert "country=EU" in tree["children"]

        us_node = tree["children"]["country=US"]
        assert us_node["count"] == 2
        assert us_node["percentage"] == 66.67
        assert us_node["depth"] == 1

    def test_build_tree_empty_data(self):
        """Test tree building with empty data."""
        tree = self.base._build_tree([], ["field1"])

        assert tree == {"children": {}}

    def test_build_tree_single_field(self):
        """Test tree building with single field."""
        data = [{"category": "A"}, {"category": "B"}, {"category": "A"}]

        tree = self.base._build_tree(data, ["category"])

        assert "category=A" in tree["children"]
        assert "category=B" in tree["children"]

        a_node = tree["children"]["category=A"]
        assert a_node["count"] == 2
        assert a_node["percentage"] == 66.67

    def test_build_tree_multiple_levels(self):
        """Test tree building with multiple hierarchy levels."""
        data = [
            {"level1": "A", "level2": "X", "level3": "1"},
            {"level1": "A", "level2": "X", "level3": "2"},
            {"level1": "A", "level2": "Y", "level3": "1"},
        ]

        tree = self.base._build_tree(data, ["level1", "level2", "level3"])

        # Check level 1
        assert "level1=A" in tree["children"]
        level1_node = tree["children"]["level1=A"]
        assert level1_node["count"] == 3
        assert level1_node["depth"] == 1

        # Check level 2
        assert "level2=X" in level1_node["children"]
        assert "level2=Y" in level1_node["children"]
        level2_x_node = level1_node["children"]["level2=X"]
        assert level2_x_node["count"] == 2
        assert level2_x_node["depth"] == 2

        # Check level 3
        assert "level3=1" in level2_x_node["children"]
        assert "level3=2" in level2_x_node["children"]

    def test_get_record_paths_simple(self):
        """Test path generation for simple records."""
        record = {"a": "value1", "b": "value2"}
        paths = self.base._get_record_paths(record, ["a", "b"])

        assert len(paths) == 1
        assert paths[0] == ["a=value1", "b=value2"]

    def test_get_record_paths_with_lists(self):
        """Test path generation with list values."""
        record = {"tags": ["tag1", "tag2"], "category": "test"}
        paths = self.base._get_record_paths(record, ["tags", "category"])

        assert len(paths) == 2
        assert ["tags=tag1", "category=test"] in paths
        assert ["tags=tag2", "category=test"] in paths

    def test_get_record_paths_multiple_lists(self):
        """Test path generation with multiple list fields."""
        record = {"tags": ["a", "b"], "categories": ["x", "y"]}
        paths = self.base._get_record_paths(record, ["tags", "categories"])

        assert len(paths) == 4
        expected_paths = [
            ["tags=a", "categories=x"],
            ["tags=a", "categories=y"],
            ["tags=b", "categories=x"],
            ["tags=b", "categories=y"],
        ]
        for expected_path in expected_paths:
            assert expected_path in paths

    def test_add_path_to_tree(self):
        """Test adding individual paths to tree."""
        tree = {"children": {}}
        path = ["country=US", "device=mobile"]
        record = {"country": "US", "device": "mobile", "id": 1}

        self.base._add_path_to_tree(path, tree, total=10, record=record)

        # Check first level
        assert "country=US" in tree["children"]
        us_node = tree["children"]["country=US"]
        assert us_node["count"] == 1
        assert us_node["percentage"] == 10.0
        assert us_node["depth"] == 1
        assert len(us_node["samples"]) == 1
        assert us_node["samples"][0] == record

        # Check second level
        assert "device=mobile" in us_node["children"]
        mobile_node = us_node["children"]["device=mobile"]
        assert mobile_node["count"] == 1
        assert mobile_node["percentage"] == 10.0
        assert mobile_node["depth"] == 2

    def test_samples_limit(self):
        """Test that samples are limited to 3 records."""
        tree = {"children": {}}
        path = ["test=value"]

        # Add 5 records
        for i in range(5):
            record = {"test": "value", "id": i}
            self.base._add_path_to_tree(path, tree, total=5, record=record)

        node = tree["children"]["test=value"]
        assert node["count"] == 5
        assert len(node["samples"]) == 3  # Limited to 3


class TestBasePreprocessing:
    """Test cases for preprocessing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base = Base()

    def test_preprocess_value_default(self):
        """Test default preprocessing behavior."""
        record = {"field": "value"}
        result = self.base._preprocess_value("field", "value", record)

        # Should delegate to preprocessor manager
        assert result == "value"  # Default behavior

    def test_preprocess_value_with_custom_preprocessor(self):
        """Test preprocessing with custom preprocessor."""

        def custom_preprocessor(value):
            return f"processed_{value}"

        self.base.add_preprocessor("test_field", custom_preprocessor)

        record = {"test_field": "value"}
        result = self.base._preprocess_value("test_field", "value", record)

        assert result == "processed_value"

    def test_preprocess_value_email_default(self):
        """Test default email preprocessing."""
        record = {"email": "john.doe@example.com"}
        result = self.base._preprocess_value("email", "john.doe@example.com", record)

        # Should extract alphabetic parts
        assert result == ["john", "doe"]


class TestBaseFieldAnalysis:
    """Test cases for field analysis functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base = Base()

    def test_analyze_field_distributions(self):
        """Test field distribution analysis."""
        data = [
            {"category": "A", "type": "X", "status": None},
            {"category": "A", "type": "Y", "status": "active"},
            {"category": "B", "type": "X", "status": "active"},
            {"category": "B", "type": "X", "status": "inactive"},
        ]

        analysis = self.base._analyze_field_distributions(
            data, ["category", "type", "status"]
        )

        # Check category analysis
        category_analysis = analysis["category"]
        assert category_analysis["total_count"] == 4
        assert category_analysis["unique_count"] == 2
        assert category_analysis["null_count"] == 0
        assert len(category_analysis["top_values"]) == 2

        # Check top values
        top_category = category_analysis["top_values"][0]
        assert top_category["count"] == 2
        assert top_category["percentage"] == 50.0

        # Check status analysis (with nulls)
        status_analysis = analysis["status"]
        assert status_analysis["null_count"] == 1
        assert status_analysis["unique_count"] == 2  # active, inactive (None excluded)

    def test_analyze_field_distributions_empty_data(self):
        """Test field analysis with empty data."""
        analysis = self.base._analyze_field_distributions([], ["field1"])

        field_analysis = analysis["field1"]
        assert field_analysis["total_count"] == 0
        assert field_analysis["unique_count"] == 0
        assert field_analysis["null_count"] == 0
        assert field_analysis["top_values"] == []


class TestBaseEdgeCases:
    """Test edge cases and error conditions for Base."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base = Base()

    def test_tree_building_with_none_values(self):
        """Test tree building with None values."""
        data = [
            {"field1": None, "field2": "value"},
            {"field1": "test", "field2": None},
        ]

        tree = self.base._build_tree(data, ["field1", "field2"])

        # Should handle None values (converted to empty string)
        assert "children" in tree
        # The exact behavior depends on preprocessing, but should not crash

    def test_tree_building_with_empty_strings(self):
        """Test tree building with empty string values."""
        data = [
            {"field": "", "other": "value"},
            {"field": "test", "other": ""},
        ]

        tree = self.base._build_tree(data, ["field", "other"])

        assert "children" in tree
        # Should handle empty strings gracefully

    def test_tree_building_with_unicode(self):
        """Test tree building with unicode characters."""
        data = [
            {"país": "España", "categoría": "técnico"},
            {"país": "México", "categoría": "ventas"},
        ]

        tree = self.base._build_tree(data, ["país", "categoría"])

        assert "children" in tree
        # Should handle unicode correctly

    def test_large_tree_performance(self):
        """Test tree building performance with larger dataset."""
        # Create dataset with 1000 records
        data = [
            {"category": f"cat_{i % 10}", "value": f"val_{i % 5}"} for i in range(1000)
        ]

        tree = self.base._build_tree(data, ["category", "value"])

        assert "children" in tree
        assert len(tree["children"]) <= 10  # 10 categories

        # Should complete without performance issues
