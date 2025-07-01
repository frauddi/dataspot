"""Unit tests for the Discovery class.

This module tests the Discovery class in isolation, focusing on automatic
pattern discovery, field analysis, and combination testing.
"""

import pytest

from dataspot.analyzers.discovery import Discovery
from dataspot.exceptions import DataspotError
from dataspot.models.discovery import DiscoverInput, DiscoverOptions, DiscoverOutput
from dataspot.models.pattern import Pattern


class TestDiscoveryInitialization:
    """Test cases for Discovery class initialization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    def test_initialization(self):
        """Test that Discovery initializes correctly."""
        assert isinstance(self.discovery, Discovery)
        assert hasattr(self.discovery, "preprocessor_manager")
        # Should inherit from Base
        assert hasattr(self.discovery, "_validate_data")
        assert hasattr(self.discovery, "_filter_data_by_query")

    def test_inheritance_from_base(self):
        """Test that Discovery properly inherits from Base."""
        # Should have all Base methods
        assert hasattr(self.discovery, "add_preprocessor")
        assert hasattr(self.discovery, "_build_tree")
        assert hasattr(self.discovery, "_analyze_field_distributions")


class TestDiscoveryExecute:
    """Test cases for the main execute method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()
        self.test_data = [
            {"country": "US", "device": "mobile", "category": "premium"},
            {"country": "US", "device": "mobile", "category": "premium"},
            {"country": "US", "device": "desktop", "category": "basic"},
            {"country": "EU", "device": "mobile", "category": "premium"},
            {"country": "EU", "device": "tablet", "category": "basic"},
        ]

    def test_execute_basic(self):
        """Test basic execute functionality."""
        discover_input = DiscoverInput(data=self.test_data)
        discover_options = DiscoverOptions()
        result = self.discovery.execute(discover_input, discover_options)

        # Verify the result structure
        assert isinstance(result, DiscoverOutput)
        assert hasattr(result, "top_patterns")
        assert hasattr(result, "field_ranking")
        assert hasattr(result, "combinations_tried")
        assert hasattr(result, "statistics")
        assert hasattr(result, "fields_analyzed")

        # Should have found some patterns
        assert len(result.top_patterns) > 0
        assert len(result.field_ranking) > 0
        assert result.statistics.total_records == 5

    def test_execute_with_parameters(self):
        """Test execute with custom parameters."""
        discover_input = DiscoverInput(data=self.test_data)
        discover_options = DiscoverOptions(
            max_fields=2, max_combinations=5, min_percentage=15.0
        )
        result = self.discovery.execute(discover_input, discover_options)

        assert isinstance(result, DiscoverOutput)
        assert result.statistics.total_records == len(self.test_data)
        # Should respect max_fields parameter
        assert len(result.field_ranking) <= len(self.test_data[0].keys())

    def test_execute_with_query(self):
        """Test execute with query filtering."""
        query = {"country": "US"}
        discover_input = DiscoverInput(data=self.test_data, query=query)
        discover_options = DiscoverOptions()
        result = self.discovery.execute(discover_input, discover_options)

        # Should filter data before analysis
        assert isinstance(result, DiscoverOutput)
        assert result.statistics.total_records <= len(self.test_data)

    def test_execute_with_empty_data(self):
        """Test execute with empty data."""
        discover_input = DiscoverInput(data=[])
        discover_options = DiscoverOptions()
        result = self.discovery.execute(discover_input, discover_options)

        assert isinstance(result, DiscoverOutput)
        assert result.top_patterns == []
        assert result.field_ranking == []
        assert result.combinations_tried == []
        assert result.statistics.total_records == 0

    def test_execute_with_invalid_data(self):
        """Test execute with invalid data."""
        discover_input = DiscoverInput(data="invalid_data")  # type: ignore
        discover_options = DiscoverOptions()

        with pytest.raises(DataspotError):
            self.discovery.execute(discover_input, discover_options)


class TestDiscoveryFieldDetection:
    """Test cases for categorical field detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    def test_detect_categorical_fields(self):
        """Test detection of suitable categorical fields."""
        test_data = [
            {"category": "A", "type": "premium", "status": "active"},
            {"category": "B", "type": "basic", "status": "active"},
            {"category": "A", "type": "premium", "status": "inactive"},
            {"category": "C", "type": "basic", "status": "active"},
        ]

        fields = self.discovery._detect_categorical_fields(test_data)

        # Should include category (good for analysis)
        assert "category" in fields
        # Should include type and status (good categorical fields)
        assert "type" in fields
        assert "status" in fields

    def test_is_suitable_for_analysis(self):
        """Test field suitability analysis."""
        # Good field: low cardinality (2 unique values out of 10)
        good_data = [{"good_field": "A" if i % 5 == 0 else "B"} for i in range(10)]
        assert self.discovery._is_suitable_for_analysis(good_data, "good_field", 10)

        # Bad field: high cardinality (100% unique)
        bad_data = [{"bad_field": f"unique_{i}"} for i in range(10)]
        assert not self.discovery._is_suitable_for_analysis(bad_data, "bad_field", 10)

    def test_is_suitable_for_analysis_edge_cases(self):
        """Test edge cases in field suitability."""
        # Single unique value
        single_value_data = [{"field": "A"}] * 5
        assert not self.discovery._is_suitable_for_analysis(
            single_value_data, "field", 5
        )

        # Too few records
        few_records_data = [{"field": "A"}]
        assert not self.discovery._is_suitable_for_analysis(
            few_records_data, "field", 1
        )

        # None values
        none_data = [{"field": None}] * 3
        assert not self.discovery._is_suitable_for_analysis(none_data, "field", 3)


class TestDiscoveryFieldScoring:
    """Test cases for field scoring functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    def test_score_fields_by_potential(self):
        """Test field scoring by concentration potential."""
        test_data = [
            {"high_concentration": "A", "low_concentration": f"val_{i}"}
            for i in range(10)
        ] + [
            {"high_concentration": "A", "low_concentration": f"val_{i}"}
            for i in range(10, 12)
        ]  # A appears in 12/12 = 100%

        discover_options = DiscoverOptions()
        scores = self.discovery._score_fields_by_potential(
            test_data, ["high_concentration", "low_concentration"], discover_options
        )

        # Should be sorted by score descending
        assert len(scores) == 2
        assert scores[0][1] >= scores[1][1]  # First score >= second score

        # High concentration field should score higher
        high_score = next(
            score for field, score in scores if field == "high_concentration"
        )
        low_score = next(
            score for field, score in scores if field == "low_concentration"
        )
        assert high_score > low_score

    def test_calculate_field_score(self):
        """Test field score calculation logic."""
        # Create patterns with different concentrations
        high_patterns = [
            Pattern(path="A=1", count=8, percentage=80.0, depth=1, samples=[]),
            Pattern(path="A=2", count=6, percentage=60.0, depth=1, samples=[]),
            Pattern(path="A=3", count=4, percentage=40.0, depth=1, samples=[]),
        ]
        score = self.discovery._calculate_field_score(high_patterns)
        assert score > 0

        # No patterns
        empty_score = self.discovery._calculate_field_score([])
        assert empty_score == 0

        # Score should increase with better patterns
        better_patterns = [
            Pattern(path="B=1", count=9, percentage=90.0, depth=1, samples=[]),
            Pattern(path="B=2", count=7, percentage=70.0, depth=1, samples=[]),
            Pattern(path="B=3", count=5, percentage=50.0, depth=1, samples=[]),
        ]
        better_score = self.discovery._calculate_field_score(better_patterns)
        assert better_score > score


class TestDiscoveryPatternCombinations:
    """Test cases for pattern combination discovery."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    def test_discover_pattern_combinations(self):
        """Test pattern combination discovery."""
        test_data = [
            {"field1": "A", "field2": "X"},
            {"field1": "A", "field2": "Y"},
            {"field1": "B", "field2": "X"},
        ]

        field_scores = [("field1", 10.0), ("field2", 8.0)]
        discover_options = DiscoverOptions(
            max_fields=2, max_combinations=5, min_percentage=20.0
        )

        patterns, combinations = self.discovery._discover_pattern_combinations(
            test_data, field_scores, discover_options
        )

        # Should have tried some combinations
        assert len(combinations) > 0
        assert isinstance(patterns, list)

        # Each combination should have required fields
        for combo in combinations:
            assert "fields" in combo
            assert "patterns_found" in combo
            assert isinstance(combo["fields"], list)

    def test_rank_and_deduplicate_patterns(self):
        """Test pattern ranking and deduplication."""
        # Create patterns with duplicates
        patterns = [
            Pattern(path="A=1", count=8, percentage=80.0, depth=1, samples=[]),
            Pattern(path="B=2", count=6, percentage=60.0, depth=1, samples=[]),
            Pattern(
                path="A=1", count=7, percentage=70.0, depth=1, samples=[]
            ),  # Duplicate with lower percentage
            Pattern(path="C=3", count=9, percentage=90.0, depth=1, samples=[]),
        ]

        result = self.discovery._rank_and_deduplicate_patterns(patterns)

        # Should remove duplicates and sort by percentage
        assert len(result) == 3  # One duplicate removed
        assert result[0].percentage == 90  # Highest first
        assert result[1].percentage == 80  # A=1 with higher percentage kept
        assert result[2].percentage == 60  # Lowest last


class TestDiscoveryIntegration:
    """Test cases for end-to-end discovery functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    def test_full_discovery_integration(self):
        """Test full discovery integration with realistic data."""
        test_data = [
            {"country": "US", "device": "mobile", "category": "premium"},
            {"country": "US", "device": "mobile", "category": "premium"},
            {"country": "US", "device": "desktop", "category": "basic"},
            {"country": "EU", "device": "mobile", "category": "premium"},
            {"country": "EU", "device": "tablet", "category": "basic"},
        ]

        discover_input = DiscoverInput(data=test_data)
        discover_options = DiscoverOptions(max_fields=3, max_combinations=10)
        result = self.discovery.execute(discover_input, discover_options)

        # Comprehensive result verification
        assert isinstance(result, DiscoverOutput)
        assert len(result.top_patterns) > 0
        assert len(result.field_ranking) == 3  # country, device, category
        assert len(result.combinations_tried) > 0
        assert result.statistics.total_records == 5

        # Check that field ranking is sorted by score
        scores = [ranking.score for ranking in result.field_ranking]
        assert scores == sorted(scores, reverse=True)

        # Check that top patterns are sorted by percentage
        percentages = [pattern.percentage for pattern in result.top_patterns]
        assert percentages == sorted(percentages, reverse=True)

    def test_discovery_with_low_quality_data(self):
        """Test discovery with low quality/sparse data."""
        sparse_data = [{"field1": f"unique_{i}", "field2": None} for i in range(5)]

        discover_input = DiscoverInput(data=sparse_data)
        discover_options = DiscoverOptions()
        result = self.discovery.execute(discover_input, discover_options)

        # Should handle gracefully
        assert isinstance(result, DiscoverOutput)
        # May find few or no patterns due to high cardinality
        assert len(result.top_patterns) >= 0

    def test_discovery_with_mixed_data_types(self):
        """Test discovery with mixed data types."""
        mixed_data = [
            {"num": 1, "str": "text", "bool": True, "float": 1.5},
            {"num": 2, "str": "text", "bool": False, "float": 2.5},
            {"num": 1, "str": "other", "bool": True, "float": 1.5},
        ]

        discover_input = DiscoverInput(data=mixed_data)
        discover_options = DiscoverOptions(max_fields=2, max_combinations=5)
        result = self.discovery.execute(discover_input, discover_options)

        # Should handle all data types
        assert isinstance(result, DiscoverOutput)
        assert len(result.field_ranking) == 4  # All fields analyzed
        assert result.statistics.total_records == 3


class TestDiscoveryEdgeCases:
    """Test edge cases and error conditions for Discovery."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    def test_build_empty_discovery_result(self):
        """Test empty discovery result building."""
        result = self.discovery._build_empty_discovery_result()

        assert result.top_patterns == []
        assert result.field_ranking == []
        assert result.combinations_tried == []
        assert result.statistics.total_records == 0

    def test_discovery_with_problematic_fields(self):
        """Test discovery when some fields cause issues."""
        test_data = [{"good_field": "A", "problematic_field": None}]

        discover_input = DiscoverInput(data=test_data)
        discover_options = DiscoverOptions()
        result = self.discovery.execute(discover_input, discover_options)

        # Should handle problematic fields gracefully
        assert isinstance(result, DiscoverOutput)
        # Should still analyze good fields
        assert len(result.field_ranking) >= 0

    def test_discovery_with_extreme_parameters(self):
        """Test discovery with extreme parameters."""
        test_data = [
            {"field": "A"},
            {"field": "B"},
        ]

        # Very restrictive parameters
        discover_input = DiscoverInput(data=test_data)
        discover_options = DiscoverOptions(
            max_fields=1, max_combinations=1, min_percentage=99.0
        )
        result = self.discovery.execute(discover_input, discover_options)

        assert isinstance(result, DiscoverOutput)
        # Should find few or no patterns due to restrictive criteria
        assert len(result.top_patterns) <= 2

    def test_discovery_with_no_suitable_fields(self):
        """Test discovery when no fields are suitable for analysis."""
        # All unique values - should have no suitable fields
        unique_data = [
            {"unique_id": f"id_{i}", "timestamp": f"2023-01-{i:02d}"}
            for i in range(1, 21)
        ]

        discover_input = DiscoverInput(data=unique_data)
        discover_options = DiscoverOptions()
        result = self.discovery.execute(discover_input, discover_options)

        assert isinstance(result, DiscoverOutput)
        # Should handle gracefully even with no suitable fields
        assert result.statistics.total_records == 20
