"""Unit tests for the Finder class.

This module tests the Finder class in isolation, focusing on its core
pattern finding functionality without external dependencies.
"""

import pytest

from dataspot.analyzers.finder import Finder
from dataspot.exceptions import DataspotError
from dataspot.models import Pattern
from dataspot.models.finder import FindOutput


class TestFinderCore:
    """Test cases for core Finder functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.finder = Finder()

    def test_initialization(self):
        """Test that Finder initializes correctly."""
        assert isinstance(self.finder, Finder)
        assert hasattr(self.finder, "preprocessor_manager")
        assert hasattr(self.finder, "preprocessors")

    def test_execute_with_empty_data(self):
        """Test execute method with empty data."""
        result = self.finder.execute([], ["field1", "field2"])

        assert isinstance(result, FindOutput)
        assert len(result.patterns) == 0
        assert result.total_records == 0
        assert result.total_patterns == 0

    def test_execute_with_empty_fields(self):
        """Test execute method with empty fields list."""
        data = [{"a": 1, "b": 2}]
        result = self.finder.execute(data, [])

        assert isinstance(result, FindOutput)
        assert len(result.patterns) == 0
        assert result.total_records == 1
        assert result.total_patterns == 0

    def test_execute_with_invalid_data(self):
        """Test execute method with invalid data."""
        with pytest.raises(DataspotError, match="Data must be a list of dictionaries"):
            self.finder.execute(None, ["field1"])  # type: ignore

    def test_execute_basic_pattern_finding(self):
        """Test basic pattern finding functionality."""
        data = [
            {"country": "US", "device": "mobile"},
            {"country": "US", "device": "desktop"},
            {"country": "EU", "device": "mobile"},
        ]

        result = self.finder.execute(data, ["country", "device"])

        assert isinstance(result, FindOutput)
        assert len(result.patterns) > 0
        assert result.total_records == 3
        assert result.total_patterns == len(result.patterns)
        assert all(isinstance(pattern, Pattern) for pattern in result.patterns)

        # Check that patterns are sorted by percentage (descending)
        percentages = [p.percentage for p in result.patterns]
        assert percentages == sorted(percentages, reverse=True)

    def test_execute_with_query_filter(self):
        """Test execute method with query filtering."""
        data = [
            {"country": "US", "device": "mobile", "active": True},
            {"country": "US", "device": "desktop", "active": False},
            {"country": "EU", "device": "mobile", "active": True},
        ]

        # Filter to only active records
        query = {"active": True}
        result = self.finder.execute(data, ["country", "device"], query=query)

        assert isinstance(result, FindOutput)
        assert len(result.patterns) > 0
        assert result.total_records == 2  # Only 2 records pass the filter

        # All patterns should be from filtered data (only active=True records)
        # This should result in 2 records being analyzed
        for pattern in result.patterns:
            assert pattern.count <= 2  # Max count should be 2 (filtered records)

    def test_execute_with_kwargs_filtering(self):
        """Test execute method with kwargs filtering."""
        data = [
            {"country": "US", "device": "mobile"},
            {"country": "US", "device": "mobile"},
            {"country": "US", "device": "desktop"},
            {"country": "EU", "device": "mobile"},
        ]

        # Filter to only patterns with at least 50% concentration
        result = self.finder.execute(data, ["country", "device"], min_percentage=50)

        assert isinstance(result, FindOutput)
        assert all(p.percentage >= 50 for p in result.patterns)
        assert result.total_records == 4
        assert result.total_patterns == len(result.patterns)

    def test_execute_with_limit(self):
        """Test execute method with limit parameter."""
        data = [
            {"country": "US", "device": "mobile"},
            {"country": "US", "device": "desktop"},
            {"country": "EU", "device": "mobile"},
            {"country": "EU", "device": "desktop"},
        ]

        result = self.finder.execute(data, ["country", "device"], limit=2)

        assert isinstance(result, FindOutput)
        assert len(result.patterns) <= 2
        assert result.total_records == 4
        assert result.total_patterns == len(result.patterns)


class TestFinderIntegration:
    """Integration tests for Finder with its dependencies."""

    def setup_method(self):
        """Set up test fixtures."""
        self.finder = Finder()

    def test_tree_building_integration(self):
        """Test that Finder correctly integrates with tree building."""
        data = [
            {"a": 1, "b": 2},
            {"a": 1, "b": 3},
            {"a": 2, "b": 2},
        ]

        # This tests the integration with _build_tree
        result = self.finder.execute(data, ["a", "b"])

        assert isinstance(result, FindOutput)
        assert len(result.patterns) > 0
        assert result.total_records == 3

        # Check that hierarchical patterns are found
        depth_1_patterns = [p for p in result.patterns if p.depth == 1]
        depth_2_patterns = [p for p in result.patterns if p.depth == 2]

        assert len(depth_1_patterns) > 0
        assert len(depth_2_patterns) > 0

    def test_pattern_extractor_integration(self):
        """Test that Finder correctly integrates with PatternExtractor."""
        data = [
            {"x": "value1", "y": "test"},
            {"x": "value1", "y": "test"},
            {"x": "value2", "y": "test"},
        ]

        result = self.finder.execute(data, ["x", "y"])

        # Check that pattern extraction works correctly
        assert isinstance(result, FindOutput)
        assert len(result.patterns) > 0
        assert result.total_records == 3

        # Verify pattern properties are correctly extracted
        for pattern in result.patterns:
            assert hasattr(pattern, "path")
            assert hasattr(pattern, "count")
            assert hasattr(pattern, "percentage")
            assert hasattr(pattern, "depth")
            assert hasattr(pattern, "samples")

            # Check percentage calculation
            assert 0 <= pattern.percentage <= 100
            assert pattern.count <= len(data)

    def test_pattern_filter_integration(self):
        """Test that Finder correctly integrates with PatternFilter."""
        data = [
            {"category": "A", "type": "X"},
            {"category": "A", "type": "Y"},
            {"category": "B", "type": "X"},
        ]

        # Test various filter combinations
        result_min_count = self.finder.execute(data, ["category", "type"], min_count=1)
        result_max_count = self.finder.execute(data, ["category", "type"], max_count=2)
        result_min_percentage = self.finder.execute(
            data, ["category", "type"], min_percentage=30
        )

        assert isinstance(result_min_count, FindOutput)
        assert isinstance(result_max_count, FindOutput)
        assert isinstance(result_min_percentage, FindOutput)

        assert all(p.count >= 1 for p in result_min_count.patterns)
        assert all(p.count <= 2 for p in result_max_count.patterns)
        assert all(p.percentage >= 30 for p in result_min_percentage.patterns)

    def test_preprocessor_integration(self):
        """Test that Finder correctly uses preprocessors."""
        data = [
            {"email": "john.doe@company.com", "type": "user"},
            {"email": "jane.smith@company.com", "type": "admin"},
        ]

        result = self.finder.execute(data, ["email", "type"])

        assert isinstance(result, FindOutput)
        assert result.total_records == 2

        # Check that email preprocessing was applied
        email_patterns = [p for p in result.patterns if "email=" in p.path]
        assert len(email_patterns) > 0

        # Should find patterns with individual email parts
        john_patterns = [p for p in result.patterns if "email=john" in p.path]
        doe_patterns = [p for p in result.patterns if "email=doe" in p.path]

        assert len(john_patterns) > 0
        assert len(doe_patterns) > 0


class TestFinderEdgeCases:
    """Test edge cases and error conditions for Finder."""

    def setup_method(self):
        """Set up test fixtures."""
        self.finder = Finder()

    def test_execute_with_none_values(self):
        """Test execute method with None values in data."""
        data = [
            {"field1": None, "field2": "value"},
            {"field1": "test", "field2": None},
            {"field1": "test", "field2": "value"},
        ]

        result = self.finder.execute(data, ["field1", "field2"])

        assert isinstance(result, FindOutput)
        assert len(result.patterns) > 0

        # Should handle None values gracefully
        for pattern in result.patterns:
            assert isinstance(pattern, Pattern)

    def test_execute_with_mixed_types(self):
        """Test execute method with mixed data types."""
        data = [
            {"field1": "string", "field2": 123},
            {"field1": 456, "field2": "another_string"},
            {"field1": True, "field2": [1, 2, 3]},
        ]

        result = self.finder.execute(data, ["field1", "field2"])

        assert isinstance(result, FindOutput)
        # Should handle mixed types without crashing

    def test_execute_with_large_dataset(self):
        """Test execute method with large dataset for performance."""
        # Create a dataset with 1000 records
        data = [
            {"category": f"cat_{i % 10}", "value": f"val_{i % 5}"} for i in range(1000)
        ]

        result = self.finder.execute(data, ["category", "value"])

        assert isinstance(result, FindOutput)
        assert len(result.patterns) > 0

        # Performance check - should complete reasonably quickly
        # and not cause memory issues

    def test_execute_with_unicode_data(self):
        """Test execute method with unicode characters."""
        data = [
            {"país": "España", "categoría": "técnico"},
            {"país": "México", "categoría": "ventas"},
            {"país": "España", "categoría": "marketing"},
        ]

        result = self.finder.execute(data, ["país", "categoría"])

        assert isinstance(result, FindOutput)
        assert len(result.patterns) > 0

        # Should handle unicode correctly
        spain_patterns = [p for p in result.patterns if "España" in p.path]
        assert len(spain_patterns) > 0

    def test_execute_with_empty_strings(self):
        """Test execute method with empty string values."""
        data = [
            {"field1": "", "field2": "value"},
            {"field1": "test", "field2": ""},
            {"field1": "", "field2": ""},
        ]

        result = self.finder.execute(data, ["field1", "field2"])

        assert isinstance(result, FindOutput)
        # Should handle empty strings gracefully
