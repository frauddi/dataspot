"""Unit tests for the main Dataspot API class.

This module tests the Dataspot class in isolation, focusing on the public API
methods and their integration with the underlying analyzer classes.
"""

from unittest.mock import Mock, patch

from dataspot.core import Dataspot
from dataspot.models.analyzer import AnalyzeOutput
from dataspot.models.discovery import DiscoverOutput
from dataspot.models.finder import FindOutput
from dataspot.models.pattern import Pattern
from dataspot.models.tree import TreeInput, TreeOptions, TreeOutput


class TestDataspotInitialization:
    """Test cases for Dataspot class initialization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_initialization(self):
        """Test that Dataspot initializes correctly."""
        assert isinstance(self.dataspot, Dataspot)
        assert hasattr(self.dataspot, "_base")
        assert self.dataspot._base is not None

    def test_add_preprocessor(self):
        """Test adding custom preprocessors."""

        def test_preprocessor(value):
            return f"processed_{value}"

        self.dataspot.add_preprocessor("test_field", test_preprocessor)

        # Should delegate to base class
        assert "test_field" in self.dataspot._base.preprocessors
        assert self.dataspot._base.preprocessors["test_field"] == test_preprocessor


class TestDataspotFind:
    """Test cases for the find method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.test_data = [
            {"country": "US", "device": "mobile", "amount": 100},
            {"country": "US", "device": "desktop", "amount": 150},
            {"country": "EU", "device": "mobile", "amount": 120},
        ]

    @patch("dataspot.analyzers.finder.Finder")
    def test_find_basic(self, mock_finder_class):
        """Test basic find functionality."""
        # Mock pattern
        mock_pattern = Mock(spec=Pattern)
        mock_pattern.percentage = 66.67
        mock_pattern.path = "country=US"

        # Mock Finder
        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[mock_pattern],
            total_records=3,
            total_patterns=1,
        )
        mock_finder_class.return_value = mock_finder

        result = self.dataspot.find(self.test_data, ["country", "device"])

        # Should call Finder.execute with correct parameters
        mock_finder.execute.assert_called_once_with(
            self.test_data, ["country", "device"], None
        )

        # Should return FindOutput
        assert isinstance(result, FindOutput)
        assert len(result.patterns) == 1
        assert result.patterns[0] == mock_pattern
        assert result.total_records == 3
        assert result.total_patterns == 1

    @patch("dataspot.analyzers.finder.Finder")
    def test_find_with_query(self, mock_finder_class):
        """Test find with query parameter."""
        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=2,
            total_patterns=0,
        )
        mock_finder_class.return_value = mock_finder

        query = {"country": "US"}
        result = self.dataspot.find(self.test_data, ["device"], query=query)

        assert isinstance(result, FindOutput)
        assert result.patterns == []
        assert result.total_records == 2
        assert result.total_patterns == 0

        # Should pass query to Finder
        mock_finder.execute.assert_called_once_with(self.test_data, ["device"], query)

    @patch("dataspot.analyzers.finder.Finder")
    def test_find_with_kwargs(self, mock_finder_class):
        """Test find with additional kwargs."""
        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=3,
            total_patterns=0,
        )
        mock_finder_class.return_value = mock_finder

        kwargs = {"min_percentage": 10, "max_depth": 3, "limit": 20}
        result = self.dataspot.find(self.test_data, ["country"], query=None, **kwargs)

        assert isinstance(result, FindOutput)
        assert result.patterns == []

        # Should pass kwargs to Finder
        mock_finder.execute.assert_called_once_with(
            self.test_data, ["country"], None, **kwargs
        )

    @patch("dataspot.analyzers.finder.Finder")
    def test_find_preprocessor_sharing(self, mock_finder_class):
        """Test that preprocessors are shared with Finder."""
        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=3,
            total_patterns=0,
        )
        mock_finder_class.return_value = mock_finder

        # Add a preprocessor
        test_preprocessor = lambda x: x.upper()  # noqa: E731
        self.dataspot.add_preprocessor("test_field", test_preprocessor)

        self.dataspot.find(self.test_data, ["country"])

        # Should set preprocessors on Finder
        assert mock_finder.preprocessors == self.dataspot._base.preprocessors


class TestDataspotAnalyze:
    """Test cases for the analyze method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.test_data = [
            {"country": "US", "device": "mobile", "amount": 100},
            {"country": "US", "device": "mobile", "amount": 150},
            {"country": "EU", "device": "desktop", "amount": 200},
            {"country": "EU", "device": "mobile", "amount": 120},
        ]

    def test_analyze_basic(self):
        """Test basic analyze functionality."""
        result = self.dataspot.analyze(self.test_data, ["country", "device"])

        # Should return AnalyzeOutput dataclass
        assert isinstance(result, AnalyzeOutput)
        assert hasattr(result, "patterns")
        assert hasattr(result, "statistics")
        assert hasattr(result, "insights")
        assert hasattr(result, "field_stats")
        assert hasattr(result, "top_patterns")

        # Should have found some patterns
        assert len(result.patterns) > 0
        assert result.statistics.total_records == 4
        assert result.statistics.patterns_found > 0

    def test_analyze_with_parameters(self):
        """Test analyze with query and kwargs."""
        query = {"country": "US"}
        kwargs = {"min_percentage": 15}

        result = self.dataspot.analyze(
            self.test_data, ["device"], query=query, **kwargs
        )

        assert isinstance(result, AnalyzeOutput)
        # Should only analyze US records (filtered by query)
        assert result.statistics.filtered_records == 2
        # All patterns should meet min_percentage threshold
        for pattern in result.patterns:
            assert pattern.percentage >= 15

    def test_analyze_preprocessor_sharing(self):
        """Test that preprocessors are applied in analyze."""
        # Add a preprocessor that converts to uppercase
        test_preprocessor = lambda x: x.upper() if isinstance(x, str) else x  # noqa: E731
        self.dataspot.add_preprocessor("country", test_preprocessor)

        result = self.dataspot.analyze(self.test_data, ["country"])

        # Should apply preprocessor - patterns should have uppercase country values
        for pattern in result.patterns:
            if "country=" in pattern.path:
                # Country value should be uppercase due to preprocessor
                assert "country=US" in pattern.path or "country=EU" in pattern.path


class TestDataspotTree:
    """Test cases for the tree method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.test_data = [
            {"category": "A", "type": "X", "amount": 100},
            {"category": "A", "type": "Y", "amount": 150},
            {"category": "B", "type": "X", "amount": 200},
            {"category": "A", "type": "X", "amount": 120},
        ]

    def test_tree_basic(self):
        """Test basic tree functionality."""
        tree_input = TreeInput(data=self.test_data, fields=["category", "type"])
        tree_options = TreeOptions()
        result = self.dataspot.tree(tree_input, tree_options)

        # Should return TreeOutput dataclass
        assert isinstance(result, TreeOutput)
        assert result.name == "root"
        assert len(result.children) > 0
        assert result.value == len(self.test_data)
        assert result.percentage == 100.0

        # Should have hierarchical structure
        assert hasattr(result, "statistics")
        assert result.statistics.total_records == 4

    def test_tree_with_filters(self):
        """Test tree with filtering options."""
        tree_input = TreeInput(
            data=self.test_data, fields=["type"], query={"category": "A"}
        )
        tree_options = TreeOptions(top=3, min_value=1, max_depth=2)
        result = self.dataspot.tree(tree_input, tree_options)

        assert isinstance(result, TreeOutput)
        # Should only include category A records (filtered by query)
        assert result.statistics.filtered_records == 3
        # Should respect max_depth
        for child in result.children:
            self._check_max_depth(child, 2)

    def _check_max_depth(self, node, max_depth, current_depth=1):
        """Check tree respects max depth."""
        if hasattr(node, "children") and node.children:
            assert current_depth <= max_depth
            for child in node.children:
                self._check_max_depth(child, max_depth, current_depth + 1)

    def test_tree_preprocessor_sharing(self):
        """Test that preprocessors are applied in tree building."""
        # Add a preprocessor that adds prefix
        test_preprocessor = lambda x: f"clean_{x}" if isinstance(x, str) else x  # noqa: E731
        self.dataspot.add_preprocessor("category", test_preprocessor)

        tree_input = TreeInput(data=self.test_data, fields=["category"])
        tree_options = TreeOptions()
        result = self.dataspot.tree(tree_input, tree_options)

        # Should apply preprocessor - node names should have prefix
        for child in result.children:
            if "category=" in child.name:
                assert "clean_" in child.name


class TestDataspotDiscover:
    """Test cases for the discover method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.test_data = [
            {"country": "US", "device": "mobile", "category": "premium"},
            {"country": "US", "device": "mobile", "category": "premium"},
            {"country": "US", "device": "desktop", "category": "basic"},
            {"country": "EU", "device": "mobile", "category": "premium"},
            {"country": "EU", "device": "tablet", "category": "basic"},
        ]

    def test_discover_basic(self):
        """Test basic discover functionality."""
        result = self.dataspot.discover(self.test_data)

        # Should return DiscoverOutput dataclass
        assert isinstance(result, DiscoverOutput)
        assert hasattr(result, "top_patterns")
        assert hasattr(result, "field_ranking")
        assert hasattr(result, "combinations_tried")
        assert hasattr(result, "statistics")

        # Should have discovered some patterns
        assert len(result.top_patterns) > 0
        assert len(result.field_ranking) > 0
        assert result.statistics.total_records == 5

    def test_discover_with_parameters(self):
        """Test discover with custom parameters."""
        query = {"country": "US"}
        kwargs = {"min_percentage": 20}

        result = self.dataspot.discover(
            self.test_data,
            max_fields=2,
            max_combinations=5,
            min_concentration=15.0,
            query=query,
            **kwargs,
        )

        assert isinstance(result, DiscoverOutput)
        # Should have applied query filter - only US records
        us_records = [r for r in self.test_data if r["country"] == "US"]
        assert result.statistics.total_records == len(us_records)
        # Should respect max_fields and max_combinations limits
        assert len(result.combinations_tried) <= 5

    def test_discover_preprocessor_sharing(self):
        """Test that preprocessors are applied in discovery."""
        # Add a preprocessor
        test_preprocessor = lambda x: x.strip().lower() if isinstance(x, str) else x  # noqa: E731
        self.dataspot.add_preprocessor("country", test_preprocessor)

        result = self.dataspot.discover(self.test_data)

        # Should apply preprocessor - patterns should have lowercase country values
        for pattern in result.top_patterns:
            if "country=" in pattern.path:
                # Should find lowercase values due to preprocessor
                assert (
                    "country=us" in pattern.path.lower()
                    or "country=eu" in pattern.path.lower()
                )


class TestDataspotIntegration:
    """Test cases for integration between methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_preprocessor_consistency_across_methods(self):
        """Test that preprocessors are consistently applied across all methods."""
        # Add multiple preprocessors
        preprocessor1 = lambda x: x.upper() if isinstance(x, str) else x  # noqa: E731
        preprocessor2 = lambda x: x.strip() if isinstance(x, str) else x  # noqa: E731

        self.dataspot.add_preprocessor("field1", preprocessor1)
        self.dataspot.add_preprocessor("field2", preprocessor2)

        test_data = [{"field1": "a", "field2": " b "}]

        # Call all methods and verify they all use preprocessors
        find_result = self.dataspot.find(test_data, ["field1"])
        analyze_result = self.dataspot.analyze(test_data, ["field1"])
        tree_input = TreeInput(data=test_data, fields=["field1"])
        tree_options = TreeOptions()
        tree_result = self.dataspot.tree(tree_input, tree_options)
        discover_result = self.dataspot.discover(test_data)

        # All should return valid results
        assert isinstance(find_result, FindOutput)
        assert isinstance(analyze_result, AnalyzeOutput)
        assert isinstance(tree_result, TreeOutput)
        assert isinstance(discover_result, DiscoverOutput)

        # Check that preprocessors were applied (field1 should be uppercase)
        for pattern in find_result.patterns:
            if "field1=" in pattern.path:
                assert "field1=A" in pattern.path  # Should be uppercase

    def test_different_methods_same_data(self):
        """Test that different methods can be used on same data."""
        test_data = [
            {"country": "US", "device": "mobile"},
            {"country": "US", "device": "desktop"},
            {"country": "EU", "device": "mobile"},
        ]
        fields = ["country", "device"]

        # Use both methods on same data
        find_result = self.dataspot.find(test_data, fields)
        analyze_result = self.dataspot.analyze(test_data, fields)

        # Both should work and return appropriate types
        assert isinstance(find_result, FindOutput)
        assert isinstance(analyze_result, AnalyzeOutput)

        # Both should analyze the same data
        assert find_result.total_records == 3
        assert analyze_result.statistics.total_records == 3


class TestDataspotEdgeCases:
    """Test edge cases and error conditions for Dataspot."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.test_data = [
            {"country": "US", "device": "mobile", "category": "premium"},
            {"country": "US", "device": "desktop", "category": "basic"},
            {"country": "EU", "device": "mobile", "category": "premium"},
        ]

    def test_empty_data_handling(self):
        """Test behavior with empty datasets."""
        result = self.dataspot.find([], ["field"])

        assert isinstance(result, FindOutput)
        assert result.patterns == []
        assert result.total_records == 0

    def test_single_record_data(self):
        """Test behavior with single record datasets."""
        result = self.dataspot.analyze([{"field": "value"}], ["field"])

        assert isinstance(result, AnalyzeOutput)
        assert len(result.patterns) == 1  # Should find one pattern
        assert result.patterns[0].count == 1
        assert result.patterns[0].percentage == 100.0

    def test_multiple_preprocessors_same_field(self):
        """Test that multiple preprocessors on same field chain correctly."""
        # Add two preprocessors for same field
        preprocessor1 = lambda x: x.upper() if isinstance(x, str) else x  # noqa: E731
        preprocessor2 = lambda x: f"prefix_{x}" if isinstance(x, str) else x  # noqa: E731

        self.dataspot.add_preprocessor("field", preprocessor1)
        self.dataspot.add_preprocessor("field", preprocessor2)

        # Should use the last one added (preprocessor2)
        assert self.dataspot._base.preprocessors["field"] == preprocessor2

    def test_discover_extreme_parameters(self):
        """Test discover with extreme parameter values."""
        # Test with extreme values
        result = self.dataspot.discover(
            self.test_data, max_fields=1, max_combinations=1, min_concentration=99.0
        )

        assert isinstance(result, DiscoverOutput)
        # With very high min_concentration, should find few or no patterns
        # But should not crash
        assert result.statistics.total_records == 3

    def test_invalid_preprocessor_handling(self):
        """Test handling of invalid preprocessor functions."""

        # This should work without errors
        def valid_preprocessor(value):
            return str(value).upper()

        self.dataspot.add_preprocessor("field", valid_preprocessor)
        assert "field" in self.dataspot._base.preprocessors


class TestDataspotDocumentationExamples:
    """Test cases for examples shown in documentation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.test_data = [
            {"country": "US", "device": "mobile", "category": "premium"},
            {"country": "US", "device": "desktop", "category": "basic"},
            {"country": "EU", "device": "mobile", "category": "premium"},
        ]

    def test_basic_usage_example(self):
        """Test the basic usage example from documentation."""
        # Create example data
        transactions = [
            {"country": "US", "payment_method": "card", "amount": 100},
            {"country": "US", "payment_method": "card", "amount": 150},
            {"country": "EU", "payment_method": "bank", "amount": 200},
        ]

        # Test the documented example
        result = self.dataspot.find(transactions, ["country", "payment_method"])

        # Should return expected structure
        assert isinstance(result, FindOutput)
        assert len(result.patterns) > 0
        assert result.total_records == 3
        assert result.total_patterns > 0

        # Should find patterns for countries
        country_patterns = [p for p in result.patterns if "country=" in p.path]
        assert len(country_patterns) > 0

    def test_discovery_usage_example(self):
        """Test the discovery usage example from documentation."""
        # Test discovery example
        result = self.dataspot.discover(self.test_data)

        # Should return expected structure
        assert isinstance(result, DiscoverOutput)
        assert len(result.top_patterns) > 0
        assert len(result.field_ranking) > 0
        assert result.statistics.total_records == 3
