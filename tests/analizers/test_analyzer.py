"""Unit tests for the Analyzer class.

This module tests the Analyzer class in isolation, focusing on comprehensive
data analysis, statistics calculation, insights generation, and pattern analysis.
"""

import pytest

from dataspot.analyzers.analyzer import Analyzer
from dataspot.exceptions import DataspotError
from dataspot.models.analyzer import AnalyzeInput, AnalyzeOptions, AnalyzeOutput


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

    def test_execute_basic(self):
        """Test basic execute functionality."""
        analyze_input = AnalyzeInput(data=self.test_data, fields=["country", "device"])
        analyze_options = AnalyzeOptions()

        result = self.analyzer.execute(analyze_input, analyze_options)

        # Verify the result structure
        assert isinstance(result, AnalyzeOutput)
        assert hasattr(result, "patterns")
        assert hasattr(result, "statistics")
        assert hasattr(result, "field_stats")
        assert hasattr(result, "top_patterns")
        assert hasattr(result, "insights")

        # Should have found some patterns
        assert len(result.patterns) > 0
        assert result.statistics.total_records == 5
        assert result.statistics.patterns_found > 0

    def test_execute_with_query(self):
        """Test execute with query filtering."""
        query = {"country": "US"}
        analyze_input = AnalyzeInput(
            data=self.test_data, fields=["device"], query=query
        )
        analyze_options = AnalyzeOptions()

        result = self.analyzer.execute(analyze_input, analyze_options)

        # Should only analyze US records (filtered by query)
        assert result.statistics.total_records == 5  # Original data
        assert result.statistics.filtered_records == 3  # Only US records
        assert result.statistics.filter_ratio == 60.0

    def test_execute_with_options(self):
        """Test execute with additional filtering options."""
        analyze_input = AnalyzeInput(data=self.test_data, fields=["country"])
        analyze_options = AnalyzeOptions(min_percentage=30, max_depth=2)

        result = self.analyzer.execute(analyze_input, analyze_options)

        # All patterns should meet min_percentage threshold
        for pattern in result.patterns:
            assert pattern.percentage >= 30

    def test_execute_with_invalid_data(self):
        """Test execute with invalid data."""
        analyze_input = AnalyzeInput(data="invalid_data", fields=["field"])  # type: ignore
        analyze_options = AnalyzeOptions()

        with pytest.raises(DataspotError):
            self.analyzer.execute(analyze_input, analyze_options)

    def test_execute_empty_data(self):
        """Test execute with empty data."""
        analyze_input = AnalyzeInput(data=[], fields=["field"])
        analyze_options = AnalyzeOptions()

        result = self.analyzer.execute(analyze_input, analyze_options)

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

    def test_generate_insights_with_real_patterns(self):
        """Test insights generation with real patterns."""
        # Create test data that will produce patterns with known concentrations
        test_data = [
            {"category": "A", "type": "X"},  # A/X appears 4 times = 80%
            {"category": "A", "type": "X"},
            {"category": "A", "type": "X"},
            {"category": "A", "type": "X"},
            {"category": "B", "type": "Y"},  # B/Y appears 1 time = 20%
        ]

        analyze_input = AnalyzeInput(data=test_data, fields=["category", "type"])
        analyze_options = AnalyzeOptions()

        result = self.analyzer.execute(analyze_input, analyze_options)
        insights = self.analyzer._generate_insights(result.patterns)

        assert insights["patterns_found"] > 0
        assert insights["max_concentration"] > 0
        assert insights["avg_concentration"] > 0
        assert "concentration_distribution" in insights

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

    def test_full_execute_integration(self):
        """Test full execute method integration."""
        # Create realistic test data
        test_data = [
            {"country": "US", "device": "mobile", "category": "A"},
            {"country": "US", "device": "mobile", "category": "A"},
            {"country": "US", "device": "mobile", "category": "B"},
            {"country": "EU", "device": "desktop", "category": "A"},
            {"country": "EU", "device": "mobile", "category": "A"},
        ]

        analyze_input = AnalyzeInput(
            data=test_data, fields=["country", "device", "category"]
        )
        analyze_options = AnalyzeOptions()

        result = self.analyzer.execute(analyze_input, analyze_options)

        # Verify comprehensive result structure
        assert isinstance(result, AnalyzeOutput)
        assert len(result.patterns) > 0
        assert result.insights.patterns_found > 0
        assert result.insights.max_concentration > 0

        # Verify statistics
        assert result.statistics.total_records == 5
        assert result.statistics.patterns_found > 0
        assert result.statistics.max_concentration > 0

        # Verify top patterns
        assert len(result.top_patterns) <= 5
        assert len(result.top_patterns) <= len(result.patterns)

        # Verify field stats
        assert result.field_stats is not None
        assert len(result.field_stats) == 3  # country, device, category

    def test_execute_with_query_integration(self):
        """Test execute with query filtering integration."""
        test_data = [
            {"country": "US", "active": True},
            {"country": "US", "active": False},
            {"country": "EU", "active": True},
        ]

        query = {"active": True}
        analyze_input = AnalyzeInput(data=test_data, fields=["country"], query=query)
        analyze_options = AnalyzeOptions()

        result = self.analyzer.execute(analyze_input, analyze_options)

        # Check statistics reflect filtering
        assert result.statistics.total_records == 3
        assert result.statistics.filtered_records == 2
        assert result.statistics.filter_ratio == 66.67

    def test_execute_no_patterns_found(self):
        """Test execute when filtering eliminates all patterns."""
        test_data = [
            {"field": "value1"},
            {"field": "value2"},
            {"field": "value3"},
        ]

        # Use very high threshold to eliminate patterns
        analyze_input = AnalyzeInput(data=test_data, fields=["field"])
        analyze_options = AnalyzeOptions(min_percentage=90.0)

        result = self.analyzer.execute(analyze_input, analyze_options)

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

    def test_execute_with_empty_fields(self):
        """Test execute with empty fields list."""
        test_data = [{"field": "value"}]

        analyze_input = AnalyzeInput(data=test_data, fields=[])
        analyze_options = AnalyzeOptions()

        result = self.analyzer.execute(analyze_input, analyze_options)
        assert result.patterns == []

    def test_large_dataset_performance(self):
        """Test analyzer performance with larger dataset."""
        # Create larger dataset
        test_data = [
            {"category": f"cat_{i % 10}", "type": f"type_{i % 5}", "id": i}
            for i in range(1000)
        ]

        analyze_input = AnalyzeInput(data=test_data, fields=["category", "type"])
        analyze_options = AnalyzeOptions()

        result = self.analyzer.execute(analyze_input, analyze_options)

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

    def test_field_stats_generation(self):
        """Test field statistics generation."""
        test_data = [
            {"country": "US", "device": "mobile"},
            {"country": "US", "device": "desktop"},
            {"country": "EU", "device": "mobile"},
            {"country": None, "device": "tablet"},
        ]

        analyze_input = AnalyzeInput(data=test_data, fields=["country", "device"])
        analyze_options = AnalyzeOptions()

        result = self.analyzer.execute(analyze_input, analyze_options)

        # Check field stats structure
        assert "country" in result.field_stats
        assert "device" in result.field_stats

        country_stats = result.field_stats["country"]
        assert country_stats["total_count"] == 4
        assert country_stats["unique_count"] == 2  # US, EU
        assert country_stats["null_count"] == 1
        assert len(country_stats["top_values"]) > 0

    def test_sorting_and_filtering_options(self):
        """Test various sorting and filtering options."""
        test_data = [
            {"category": "A", "value": 1},  # A appears 3 times = 60%
            {"category": "A", "value": 2},
            {"category": "A", "value": 3},
            {"category": "B", "value": 4},  # B appears 2 times = 40%
            {"category": "B", "value": 5},
        ]

        # Test with sorting by count
        analyze_input = AnalyzeInput(data=test_data, fields=["category"])
        analyze_options = AnalyzeOptions(sort_by="count", reverse=True)

        result = self.analyzer.execute(analyze_input, analyze_options)

        assert len(result.patterns) > 0
        # Should be sorted by count descending
        if len(result.patterns) > 1:
            assert result.patterns[0].count >= result.patterns[1].count
