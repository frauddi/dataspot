"""Unit tests for the main Dataspot API class.

This module tests the Dataspot class in isolation, focusing on the public API
methods and their integration with the underlying analyzer classes.
"""

from unittest.mock import Mock, patch

from dataspot.core import Dataspot
from dataspot.models import Pattern


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

    @patch("dataspot.core.Finder")
    def test_find_basic(self, mock_finder_class):
        """Test basic find functionality."""
        # Mock pattern
        mock_pattern = Mock(spec=Pattern)
        mock_pattern.percentage = 66.67
        mock_pattern.path = "country=US"

        # Mock Finder
        mock_finder = Mock()
        mock_finder.execute.return_value = [mock_pattern]
        mock_finder_class.return_value = mock_finder

        result = self.dataspot.find(self.test_data, ["country", "device"])

        # Should call Finder.execute with correct parameters
        mock_finder.execute.assert_called_once_with(
            self.test_data, ["country", "device"], None
        )

        # Should return patterns
        assert len(result) == 1
        assert result[0] == mock_pattern

    @patch("dataspot.core.Finder")
    def test_find_with_query(self, mock_finder_class):
        """Test find with query parameter."""
        mock_finder = Mock()
        mock_finder.execute.return_value = []
        mock_finder_class.return_value = mock_finder

        query = {"country": "US"}
        result = self.dataspot.find(self.test_data, ["device"], query=query)

        assert result == []

        # Should pass query to Finder
        mock_finder.execute.assert_called_once_with(self.test_data, ["device"], query)

    @patch("dataspot.core.Finder")
    def test_find_with_kwargs(self, mock_finder_class):
        """Test find with additional kwargs."""
        mock_finder = Mock()
        mock_finder.execute.return_value = []
        mock_finder_class.return_value = mock_finder

        kwargs = {"min_percentage": 10, "max_depth": 3, "limit": 20}
        result = self.dataspot.find(self.test_data, ["country"], query=None, **kwargs)

        assert result == []

        # Should pass kwargs to Finder
        mock_finder.execute.assert_called_once_with(
            self.test_data, ["country"], None, **kwargs
        )

    @patch("dataspot.core.Finder")
    def test_find_preprocessor_sharing(self, mock_finder_class):
        """Test that preprocessors are shared with Finder."""
        mock_finder = Mock()
        mock_finder.execute.return_value = []
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
            {"country": "US", "device": "mobile"},
            {"country": "EU", "device": "desktop"},
        ]

    @patch("dataspot.core.Analyzer")
    def test_analyze_basic(self, mock_analyzer_class):
        """Test basic analyze functionality."""
        # Mock analyzer result
        mock_result = {
            "patterns": [],
            "insights": {"patterns_found": 0},
            "statistics": {"total_records": 2},
            "field_stats": {},
            "top_patterns": [],
        }

        mock_analyzer = Mock()
        mock_analyzer.execute.return_value = mock_result
        mock_analyzer_class.return_value = mock_analyzer

        result = self.dataspot.analyze(self.test_data, ["country", "device"])

        # Should call Analyzer.execute
        mock_analyzer.execute.assert_called_once_with(
            self.test_data, ["country", "device"], None
        )

        # Should return analysis result
        assert result == mock_result
        assert "patterns" in result
        assert "insights" in result
        assert "statistics" in result

    @patch("dataspot.core.Analyzer")
    def test_analyze_with_parameters(self, mock_analyzer_class):
        """Test analyze with query and kwargs."""
        mock_analyzer = Mock()
        mock_analyzer.execute.return_value = {}
        mock_analyzer_class.return_value = mock_analyzer

        query = {"country": "US"}
        kwargs = {"min_percentage": 15}

        result = self.dataspot.analyze(
            self.test_data, ["device"], query=query, **kwargs
        )

        assert result == {}

        # Should pass parameters to Analyzer
        mock_analyzer.execute.assert_called_once_with(
            self.test_data, ["device"], query, **kwargs
        )

    @patch("dataspot.core.Analyzer")
    def test_analyze_preprocessor_sharing(self, mock_analyzer_class):
        """Test that preprocessors are shared with Analyzer."""
        mock_analyzer = Mock()
        mock_analyzer.execute.return_value = {}
        mock_analyzer_class.return_value = mock_analyzer

        # Add a preprocessor
        test_preprocessor = lambda x: x.lower()  # noqa: E731
        self.dataspot.add_preprocessor("test_field", test_preprocessor)

        self.dataspot.analyze(self.test_data, ["country"])

        # Should set preprocessors on Analyzer
        assert mock_analyzer.preprocessors == self.dataspot._base.preprocessors


class TestDataspotTree:
    """Test cases for the tree method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.test_data = [
            {"category": "A", "type": "X"},
            {"category": "A", "type": "Y"},
            {"category": "B", "type": "X"},
        ]

    @patch("dataspot.core.Tree")
    def test_tree_basic(self, mock_tree_class):
        """Test basic tree functionality."""
        # Mock tree result
        mock_tree_result = {
            "name": "root",
            "children": [
                {
                    "name": "category=A",
                    "value": 2,
                    "percentage": 66.67,
                    "node": 1,
                    "children": [],
                }
            ],
            "value": 3,
            "percentage": 100.0,
            "node": 0,
        }

        mock_tree = Mock()
        mock_tree.execute.return_value = mock_tree_result
        mock_tree_class.return_value = mock_tree

        result = self.dataspot.tree(self.test_data, ["category", "type"])

        # Should call Tree.execute
        mock_tree.execute.assert_called_once_with(
            self.test_data, ["category", "type"], None
        )

        # Should return tree structure
        assert result == mock_tree_result
        assert "name" in result
        assert "children" in result
        assert "value" in result

    @patch("dataspot.core.Tree")
    def test_tree_with_filters(self, mock_tree_class):
        """Test tree with filtering options."""
        mock_tree = Mock()
        mock_tree.execute.return_value = {}
        mock_tree_class.return_value = mock_tree

        query = {"category": "A"}
        kwargs = {"top": 3, "min_value": 5, "max_depth": 2}

        result = self.dataspot.tree(self.test_data, ["type"], query=query, **kwargs)

        assert result == {}

        # Should pass parameters to Tree
        mock_tree.execute.assert_called_once_with(
            self.test_data, ["type"], query, **kwargs
        )

    @patch("dataspot.core.Tree")
    def test_tree_preprocessor_sharing(self, mock_tree_class):
        """Test that preprocessors are shared with Tree."""
        mock_tree = Mock()
        mock_tree.execute.return_value = {}
        mock_tree_class.return_value = mock_tree

        # Add a preprocessor
        test_preprocessor = lambda x: f"clean_{x}"  # noqa: E731
        self.dataspot.add_preprocessor("test_field", test_preprocessor)

        self.dataspot.tree(self.test_data, ["category"])

        # Should set preprocessors on Tree
        assert mock_tree.preprocessors == self.dataspot._base.preprocessors


class TestDataspotDiscover:
    """Test cases for the discover method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.test_data = [
            {"country": "US", "device": "mobile", "category": "premium"},
            {"country": "US", "device": "desktop", "category": "basic"},
            {"country": "EU", "device": "mobile", "category": "premium"},
        ]

    @patch("dataspot.core.Discovery")
    def test_discover_basic(self, mock_discovery_class):
        """Test basic discover functionality."""
        # Mock discovery result
        mock_result = {
            "top_patterns": [],
            "field_ranking": [("country", 15.0), ("device", 12.0)],
            "combinations_tried": [],
            "statistics": {"total_records": 3, "fields_analyzed": 3},
        }

        mock_discovery = Mock()
        mock_discovery.execute.return_value = mock_result
        mock_discovery_class.return_value = mock_discovery

        result = self.dataspot.discover(self.test_data)

        # Should call Discovery.execute with defaults
        mock_discovery.execute.assert_called_once_with(
            self.test_data, 3, 10, 10.0, None
        )

        # Should return discovery result
        assert result == mock_result
        assert "top_patterns" in result
        assert "field_ranking" in result

    @patch("dataspot.core.Discovery")
    def test_discover_with_parameters(self, mock_discovery_class):
        """Test discover with custom parameters."""
        mock_discovery = Mock()
        mock_discovery.execute.return_value = {}
        mock_discovery_class.return_value = mock_discovery

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

        assert result == {}

        # Should pass all parameters to Discovery
        mock_discovery.execute.assert_called_once_with(
            self.test_data, 2, 5, 15.0, query, **kwargs
        )

    @patch("dataspot.core.Discovery")
    def test_discover_preprocessor_sharing(self, mock_discovery_class):
        """Test that preprocessors are shared with Discovery."""
        mock_discovery = Mock()
        mock_discovery.execute.return_value = {}
        mock_discovery_class.return_value = mock_discovery

        # Add a preprocessor
        test_preprocessor = lambda x: x.strip()  # noqa: E731
        self.dataspot.add_preprocessor("test_field", test_preprocessor)

        self.dataspot.discover(self.test_data)

        # Should set preprocessors on Discovery
        assert mock_discovery.preprocessors == self.dataspot._base.preprocessors


class TestDataspotIntegration:
    """Test cases for integration between methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_preprocessor_consistency_across_methods(self):
        """Test that preprocessors are consistently shared across all methods."""
        # Add multiple preprocessors
        preprocessor1 = lambda x: x.upper()  # noqa: E731
        preprocessor2 = lambda x: x.strip()  # noqa: E731

        self.dataspot.add_preprocessor("field1", preprocessor1)
        self.dataspot.add_preprocessor("field2", preprocessor2)

        test_data = [{"field1": "a", "field2": "b"}]

        with (
            patch("dataspot.core.Finder") as mock_finder,
            patch("dataspot.core.Analyzer") as mock_analyzer,
            patch("dataspot.core.Tree") as mock_tree,
            patch("dataspot.core.Discovery") as mock_discovery,
        ):
            # Mock all analyzers
            for mock_class in [mock_finder, mock_analyzer, mock_tree, mock_discovery]:
                mock_instance = Mock()
                mock_instance.execute.return_value = []
                mock_class.return_value = mock_instance

            # Call all methods
            self.dataspot.find(test_data, ["field1"])
            self.dataspot.analyze(test_data, ["field1"])
            self.dataspot.tree(test_data, ["field1"])
            self.dataspot.discover(test_data)

            # All should have the same preprocessors
            expected_preprocessors = self.dataspot._base.preprocessors

            mock_finder.return_value.preprocessors = expected_preprocessors
            mock_analyzer.return_value.preprocessors = expected_preprocessors
            mock_tree.return_value.preprocessors = expected_preprocessors
            mock_discovery.return_value.preprocessors = expected_preprocessors

    @patch("dataspot.core.Finder")
    @patch("dataspot.core.Analyzer")
    def test_different_methods_same_data(self, mock_analyzer_class, mock_finder_class):
        """Test that different methods can work on the same data."""
        test_data = [{"country": "US", "device": "mobile"}]
        fields = ["country", "device"]

        # Mock returns
        mock_pattern = Mock(spec=Pattern)
        mock_pattern.percentage = 100.0

        mock_finder = Mock()
        mock_finder.execute.return_value = [mock_pattern]
        mock_finder_class.return_value = mock_finder

        mock_analyzer = Mock()
        mock_analyzer.execute.return_value = {"patterns": [mock_pattern]}
        mock_analyzer_class.return_value = mock_analyzer

        # Call both methods
        find_result = self.dataspot.find(test_data, fields)
        analyze_result = self.dataspot.analyze(test_data, fields)

        # Both should work
        assert len(find_result) == 1
        assert "patterns" in analyze_result

        # Both should have been called with same data
        mock_finder.execute.assert_called_once_with(test_data, fields, None)
        mock_analyzer.execute.assert_called_once_with(test_data, fields, None)


class TestDataspotEdgeCases:
    """Test edge cases and error conditions for Dataspot."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    @patch("dataspot.core.Finder")
    def test_empty_data_handling(self, mock_finder_class):
        """Test handling of empty data."""
        mock_finder = Mock()
        mock_finder.execute.return_value = []
        mock_finder_class.return_value = mock_finder

        result = self.dataspot.find([], ["field"])

        # Should handle empty data gracefully
        assert result == []
        mock_finder.execute.assert_called_once_with([], ["field"], None)

    @patch("dataspot.core.Analyzer")
    def test_single_record_data(self, mock_analyzer_class):
        """Test handling of single record data."""
        mock_analyzer = Mock()
        mock_analyzer.execute.return_value = {"patterns": []}
        mock_analyzer_class.return_value = mock_analyzer

        single_record = [{"field": "value"}]
        result = self.dataspot.analyze(single_record, ["field"])

        # Should handle single record gracefully
        assert "patterns" in result
        mock_analyzer.execute.assert_called_once_with(single_record, ["field"], None)

    def test_multiple_preprocessors_same_field(self):
        """Test adding multiple preprocessors to the same field."""
        preprocessor1 = lambda x: x.upper()  # noqa: E731
        preprocessor2 = lambda x: x.strip()  # noqa: E731

        # Add first preprocessor
        self.dataspot.add_preprocessor("field", preprocessor1)
        assert self.dataspot._base.preprocessors["field"] == preprocessor1

        # Add second preprocessor (should replace first)
        self.dataspot.add_preprocessor("field", preprocessor2)
        assert self.dataspot._base.preprocessors["field"] == preprocessor2

    @patch("dataspot.core.Discovery")
    def test_discover_extreme_parameters(self, mock_discovery_class):
        """Test discover with extreme parameter values."""
        mock_discovery = Mock()
        mock_discovery.execute.return_value = {}
        mock_discovery_class.return_value = mock_discovery

        test_data = [{"field": "value"}]

        # Test with extreme values
        result = self.dataspot.discover(
            test_data,
            max_fields=100,  # Very high
            max_combinations=1000,  # Very high
            min_concentration=0.1,  # Very low
        )

        assert result == {}

        # Should pass parameters through
        mock_discovery.execute.assert_called_once_with(test_data, 100, 1000, 0.1, None)

    def test_invalid_preprocessor_handling(self):
        """Test handling of invalid preprocessor functions."""
        # This should not raise an error at assignment time
        self.dataspot.add_preprocessor("field", "not_a_function")  # type: ignore

        # The error would occur when the preprocessor is actually used
        assert "field" in self.dataspot._base.preprocessors


class TestDataspotDocumentationExamples:
    """Test cases based on documentation examples."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    @patch("dataspot.core.Finder")
    def test_basic_usage_example(self, mock_finder_class):
        """Test the basic usage example from documentation."""
        # Example data from docs
        data = [
            {
                "country": "US",
                "device": "mobile",
                "amount": 150,
                "user_type": "premium",
            },
            {
                "country": "US",
                "device": "mobile",
                "amount": 200,
                "user_type": "premium",
            },
            {"country": "EU", "device": "desktop", "amount": 50, "user_type": "free"},
            {
                "country": "US",
                "device": "mobile",
                "amount": 300,
                "user_type": "premium",
            },
        ]

        # Mock expected pattern
        mock_pattern = Mock(spec=Pattern)
        mock_pattern.percentage = 75.0
        mock_pattern.count = 3
        mock_pattern.path = "country=US > device=mobile > user_type=premium"

        mock_finder = Mock()
        mock_finder.execute.return_value = [mock_pattern]
        mock_finder_class.return_value = mock_finder

        # Call as shown in docs
        concentrations = self.dataspot.find(
            data, fields=["country", "device", "user_type"]
        )

        # Should work as expected
        assert len(concentrations) == 1
        assert concentrations[0].percentage == 75.0

    @patch("dataspot.core.Discovery")
    def test_discovery_usage_example(self, mock_discovery_class):
        """Test the discovery usage example from documentation."""
        mock_pattern = Mock(spec=Pattern)
        mock_pattern.percentage = 60.0
        mock_pattern.path = "country=US > device=mobile"

        mock_result = {
            "top_patterns": [mock_pattern],
            "field_ranking": [("country", 20.0), ("device", 15.0)],
        }

        mock_discovery = Mock()
        mock_discovery.execute.return_value = mock_result
        mock_discovery_class.return_value = mock_discovery

        transactions = [{"country": "US", "device": "mobile"}]

        # Call as shown in docs
        results = self.dataspot.discover(transactions)

        # Should return expected structure
        assert "top_patterns" in results
        assert "field_ranking" in results
        assert len(results["top_patterns"]) > 0
