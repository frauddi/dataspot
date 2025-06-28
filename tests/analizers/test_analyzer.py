"""Unit tests for the Analyzer class.

This module tests the Analyzer class in isolation, focusing on comprehensive
data analysis, statistics calculation, insights generation, and pattern analysis.
"""

from unittest.mock import Mock, patch

import pytest

from dataspot.analyzers.analyzer import Analyzer
from dataspot.exceptions import DataspotError
from dataspot.models.analyzer import AnalyzeOutput
from dataspot.models.finder import FindInput, FindOptions, FindOutput


class TestAnalyzerInitialization:
    """Test cases for Analyzer class initialization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = Analyzer()

    def test_initialization(self):
        """Test that Analyzer initializes correctly."""
        assert isinstance(self.analyzer, Analyzer)
        assert hasattr(self.analyzer, "preprocessor_manager")
        # Should inherit from Base
        assert hasattr(self.analyzer, "_validate_data")
        assert hasattr(self.analyzer, "_filter_data_by_query")

    def test_inheritance_from_base(self):
        """Test that Analyzer properly inherits from Base."""
        # Should have all Base methods
        assert hasattr(self.analyzer, "add_preprocessor")
        assert hasattr(self.analyzer, "_build_tree")
        assert hasattr(self.analyzer, "_analyze_field_distributions")


class TestAnalyzerExecute:
    """Test cases for the main execute method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = Analyzer()
        self.test_data = [
            {"country": "US", "device": "mobile", "amount": 100},
            {"country": "US", "device": "mobile", "amount": 150},
            {"country": "US", "device": "desktop", "amount": 200},
            {"country": "EU", "device": "mobile", "amount": 120},
            {"country": "EU", "device": "desktop", "amount": 80},
        ]

    @patch("dataspot.analyzers.analyzer.Finder")
    def test_execute_basic(self, mock_finder_class):
        """Test basic execute functionality."""
        mock_pattern = Mock()
        mock_pattern.percentage = 60.0

        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[mock_pattern],
            total_records=len(self.test_data),
            total_patterns=1,
        )
        mock_finder_class.return_value = mock_finder

        with patch("dataspot.analyzers.analyzer.Finder", return_value=mock_finder):
            result = self.analyzer.execute(self.test_data, ["country", "device"])

        # Verify the result structure
        assert isinstance(result, AnalyzeOutput)
        assert hasattr(result, "patterns")
        assert hasattr(result, "statistics")
        assert hasattr(result, "field_stats")
        assert hasattr(result, "top_patterns")

        # Verify that Finder was called with correct input and options
        mock_finder.execute.assert_called_once()
        call_args = mock_finder.execute.call_args
        assert isinstance(call_args[0][0], FindInput)  # First arg should be FindInput
        assert isinstance(
            call_args[0][1], FindOptions
        )  # Second arg should be FindOptions

    @patch("dataspot.analyzers.analyzer.Finder")
    def test_execute_with_query(self, mock_finder_class):
        """Test execute with query filtering."""
        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=2,  # Filtered data
            total_patterns=0,
        )

        query = {"country": "US"}

        with patch("dataspot.analyzers.analyzer.Finder", return_value=mock_finder):
            _ = self.analyzer.execute(self.test_data, ["device"], query=query)

        # Verify that FindInput includes the query
        mock_finder.execute.assert_called_once()
        call_args = mock_finder.execute.call_args
        find_input = call_args[0][0]
        assert isinstance(find_input, FindInput)
        assert find_input.query == query

    @patch("dataspot.analyzers.analyzer.Finder")
    def test_execute_with_kwargs(self, mock_finder_class):
        """Test execute with additional filtering options."""
        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=len(self.test_data),
            total_patterns=0,
        )

        with patch("dataspot.analyzers.analyzer.Finder", return_value=mock_finder):
            _ = self.analyzer.execute(
                self.test_data,
                ["country"],
                min_percentage=10,
                max_depth=2,
            )

        # Verify that FindOptions includes the kwargs
        mock_finder.execute.assert_called_once()
        call_args = mock_finder.execute.call_args
        find_options = call_args[0][1]
        assert isinstance(find_options, FindOptions)
        assert find_options.min_percentage == 10
        assert find_options.max_depth == 2

    def test_execute_with_invalid_data(self):
        """Test execute with invalid data."""
        with pytest.raises(DataspotError):
            self.analyzer.execute("invalid_data", ["field"])  # type: ignore

    @patch("dataspot.analyzers.analyzer.Finder")
    def test_execute_empty_data(self, mock_finder_class):
        """Test execute with empty data."""
        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=0,
            total_patterns=0,
        )
        mock_finder_class.return_value = mock_finder

        result = self.analyzer.execute([], ["field"])

        assert isinstance(result, AnalyzeOutput)
        assert result.statistics.total_records == 0
        assert result.patterns == []
        assert result.insights.patterns_found == 0


class TestAnalyzerStatistics:
    """Test cases for statistics calculation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = Analyzer()
        self.test_data = [
            {"country": "US", "amount": 100},
            {"country": "US", "amount": 150},
            {"country": "EU", "amount": 200},
            {"country": "UK", "amount": 80},
        ]

    def test_calculate_statistics_no_query(self):
        """Test statistics calculation without query."""
        stats = self.analyzer._calculate_statistics(self.test_data, None)

        assert stats["total_records"] == 4
        assert stats["filtered_records"] == 4
        assert stats["filter_ratio"] == 100.0

    def test_calculate_statistics_with_query(self):
        """Test statistics calculation with query filtering."""
        query = {"country": "US"}
        stats = self.analyzer._calculate_statistics(self.test_data, query)

        assert stats["total_records"] == 4
        assert stats["filtered_records"] == 2  # Only US records
        assert stats["filter_ratio"] == 50.0

    def test_calculate_statistics_with_no_matches(self):
        """Test statistics calculation with query that matches nothing."""
        query = {"country": "NONEXISTENT"}
        stats = self.analyzer._calculate_statistics(self.test_data, query)

        assert stats["total_records"] == 4
        assert stats["filtered_records"] == 0
        assert stats["filter_ratio"] == 0.0

    def test_calculate_statistics_empty_data(self):
        """Test statistics calculation with empty data."""
        stats = self.analyzer._calculate_statistics([], None)

        assert stats["total_records"] == 0
        assert stats["filtered_records"] == 0
        assert stats["filter_ratio"] == 0


class TestAnalyzerInsights:
    """Test cases for insights generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = Analyzer()

    def test_generate_insights_empty_patterns(self):
        """Test insights generation with no patterns."""
        insights = self.analyzer._generate_insights([])

        assert insights["patterns_found"] == 0
        assert insights["max_concentration"] == 0
        assert insights["avg_concentration"] == 0
        assert insights["concentration_distribution"] == "No patterns found"

    def test_generate_insights_with_patterns(self):
        """Test insights generation with patterns."""
        # Create mock patterns
        patterns = []
        for percentage in [80.0, 60.0, 40.0, 20.0, 10.0]:
            pattern = Mock()
            pattern.percentage = percentage
            patterns.append(pattern)

        insights = self.analyzer._generate_insights(patterns)

        assert insights["patterns_found"] == 5
        assert insights["max_concentration"] == 80.0
        assert insights["avg_concentration"] == 42.0  # (80+60+40+20+10)/5
        assert "concentration_distribution" in insights

    def test_generate_insights_single_pattern(self):
        """Test insights generation with single pattern."""
        pattern = Mock()
        pattern.percentage = 75.0
        patterns = [pattern]

        insights = self.analyzer._generate_insights(patterns)

        assert insights["patterns_found"] == 1
        assert insights["max_concentration"] == 75.0
        assert insights["avg_concentration"] == 75.0

    def test_analyze_concentration_distribution_high(self):
        """Test concentration distribution analysis - high concentration."""
        # More than 30% are high concentration (>=50%)
        concentrations = [80.0, 70.0, 60.0, 55.0, 30.0, 20.0, 10.0]  # 4/7 = 57% high

        result = self.analyzer._analyze_concentration_distribution(concentrations)
        assert result == "High concentration patterns dominant"

    def test_analyze_concentration_distribution_moderate(self):
        """Test concentration distribution analysis - moderate concentration."""
        # More than 50% are medium concentration (20-50%)
        concentrations = [45.0, 35.0, 30.0, 25.0, 15.0, 10.0]  # 4/6 = 67% medium

        result = self.analyzer._analyze_concentration_distribution(concentrations)
        assert result == "Moderate concentration patterns"

    def test_analyze_concentration_distribution_low(self):
        """Test concentration distribution analysis - low concentration."""
        # Most are low concentration (<20%)
        concentrations = [15.0, 10.0, 8.0, 5.0, 3.0]  # All low

        result = self.analyzer._analyze_concentration_distribution(concentrations)
        assert result == "Low concentration patterns prevalent"

    def test_analyze_concentration_distribution_mixed(self):
        """Test concentration distribution analysis - mixed."""
        # Equal distribution
        concentrations = [60.0, 40.0, 15.0]  # 1 high, 1 medium, 1 low

        result = self.analyzer._analyze_concentration_distribution(concentrations)
        # Should be high since 1/3 = 33% > 30% are high concentration
        assert result == "High concentration patterns dominant"


class TestAnalyzerIntegration:
    """Test cases for integration and end-to-end functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = Analyzer()

    @patch("dataspot.analyzers.analyzer.Finder")
    def test_full_execute_integration(self, mock_finder_class):
        """Test full execute method integration."""
        # Create realistic test data
        test_data = [
            {"country": "US", "device": "mobile", "category": "A"},
            {"country": "US", "device": "mobile", "category": "A"},
            {"country": "US", "device": "mobile", "category": "B"},
            {"country": "EU", "device": "desktop", "category": "A"},
            {"country": "EU", "device": "mobile", "category": "A"},
        ]

        # Mock patterns with realistic data
        mock_patterns = []
        for i, percentage in enumerate([60.0, 40.0, 20.0]):
            pattern = Mock()
            pattern.percentage = percentage
            pattern.count = 3 - i
            pattern.path = f"pattern_{i}"
            mock_patterns.append(pattern)

        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=mock_patterns,
            total_records=len(test_data),
            total_patterns=len(mock_patterns),
        )
        mock_finder_class.return_value = mock_finder

        result = self.analyzer.execute(test_data, ["country", "device", "category"])

        # Verify comprehensive result structure
        assert isinstance(result, AnalyzeOutput)
        assert len(result.patterns) == 3
        assert result.insights.patterns_found == 3
        assert result.insights.max_concentration == 60.0
        assert result.insights.avg_concentration == 40.0

        # Verify statistics
        assert result.statistics.total_records == 5
        assert result.statistics.patterns_found == 3
        assert result.statistics.max_concentration == 60.0
        assert result.statistics.avg_concentration == 40.0

        # Verify top patterns
        assert len(result.top_patterns) == 3
        assert result.top_patterns == mock_patterns

        # Verify field stats
        assert result.field_stats is not None
        assert len(result.field_stats) == 3  # country, device, category

    @patch("dataspot.analyzers.analyzer.Finder")
    def test_execute_with_query_integration(self, mock_finder_class):
        """Test execute with query filtering integration."""
        self.test_data = [
            {"country": "US", "active": True},
            {"country": "US", "active": False},
            {"country": "EU", "active": True},
        ]

        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=len(self.test_data),
            total_patterns=0,
        )
        mock_finder_class.return_value = mock_finder

        query = {"active": True}
        result = self.analyzer.execute(self.test_data, ["country"], query=query)

        # Check statistics reflect filtering
        assert result.statistics.total_records == 3
        assert result.statistics.filtered_records == 2
        assert result.statistics.filter_ratio == 66.67

    @patch("dataspot.analyzers.analyzer.Finder")
    def test_execute_no_patterns_found(self, mock_finder_class):
        """Test execute when no patterns are found."""
        test_data = [{"field": "value"}]

        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=len(test_data),
            total_patterns=0,
        )
        mock_finder_class.return_value = mock_finder

        result = self.analyzer.execute(test_data, ["field"])

        # Check handling of no patterns
        assert result.patterns == []
        assert result.insights.patterns_found == 0
        assert result.statistics.max_concentration == 0
        assert result.statistics.avg_concentration == 0
        assert result.top_patterns == []


class TestAnalyzerEdgeCases:
    """Test edge cases and error conditions for Analyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = Analyzer()

    @patch("dataspot.analyzers.analyzer.Finder")
    def test_execute_with_empty_fields(self, mock_finder_class):
        """Test execute with empty fields list."""
        test_data = [{"field": "value"}]

        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=len(test_data),
            total_patterns=0,
        )
        mock_finder_class.return_value = mock_finder

        result = self.analyzer.execute(test_data, [])
        assert result.patterns == []

    @patch("dataspot.analyzers.analyzer.Finder")
    def test_large_dataset_performance(self, mock_finder_class):
        """Test analyzer performance with larger dataset."""
        # Create larger dataset
        test_data = [
            {"category": f"cat_{i % 10}", "type": f"type_{i % 5}", "id": i}
            for i in range(1000)
        ]

        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=len(test_data),
            total_patterns=0,
        )
        mock_finder_class.return_value = mock_finder

        result = self.analyzer.execute(test_data, ["category", "type"])

        # Should complete without performance issues
        assert result.statistics.total_records == 1000
        assert result.field_stats is not None

    def test_concentration_distribution_edge_cases(self):
        """Test concentration distribution with edge cases."""
        # Empty list
        result = self.analyzer._analyze_concentration_distribution([])
        assert result == "No patterns found"

        # Single value
        result = self.analyzer._analyze_concentration_distribution([50.0])
        assert isinstance(result, str)

        # All same values
        result = self.analyzer._analyze_concentration_distribution([25.0, 25.0, 25.0])
        assert result == "Moderate concentration patterns"
