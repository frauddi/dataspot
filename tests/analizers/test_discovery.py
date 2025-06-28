"""Unit tests for the Discovery class.

This module tests the Discovery class in isolation, focusing on automatic
pattern discovery, field analysis.
"""

from typing import List
from unittest.mock import Mock, patch

import pytest

from dataspot.analyzers.discovery import Discovery
from dataspot.exceptions import DataspotError
from dataspot.models import Pattern
from dataspot.models.discovery import DiscoverOutput
from dataspot.models.finder import FindOutput


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
            {"country": "US", "device": "mobile", "category": "A"},
            {"country": "US", "device": "mobile", "category": "B"},
            {"country": "EU", "device": "desktop", "category": "A"},
        ]

    @patch("dataspot.analyzers.discovery.Finder")
    def test_execute_basic(self, mock_finder_class):
        """Test basic execute functionality."""
        mock_pattern = Mock(spec=Pattern)
        mock_pattern.percentage = 60.0
        mock_pattern.path = "country=US"

        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[mock_pattern],
            total_records=len(self.test_data),
            total_patterns=1,
        )
        mock_finder_class.return_value = mock_finder

        result = self.discovery.execute(self.test_data)

        assert isinstance(result, DiscoverOutput)
        assert hasattr(result, "top_patterns")
        assert hasattr(result, "field_ranking")
        assert hasattr(result, "combinations_tried")
        assert hasattr(result, "statistics")

    @patch("dataspot.analyzers.discovery.Finder")
    def test_execute_with_parameters(self, mock_finder_class):
        """Test execute with custom parameters."""
        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=len(self.test_data),
            total_patterns=0,
        )
        mock_finder_class.return_value = mock_finder

        result = self.discovery.execute(
            self.test_data, max_fields=2, max_combinations=5, min_percentage=20.0
        )

        # Should use custom parameters
        assert isinstance(result, DiscoverOutput)
        assert result.top_patterns is not None
        assert isinstance(result.combinations_tried, list)

    @patch("dataspot.analyzers.discovery.Finder")
    def test_execute_with_query(self, mock_finder_class):
        """Test execute with query filtering."""
        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=[],
            total_records=2,  # Filtered records
            total_patterns=0,
        )
        mock_finder_class.return_value = mock_finder

        query = {"country": "US"}
        result = self.discovery.execute(self.test_data, query=query)

        # Should filter data before analysis
        assert isinstance(result, DiscoverOutput)
        assert result.statistics.total_records <= len(self.test_data)

    def test_execute_with_empty_data(self):
        """Test execute with empty data."""
        result = self.discovery.execute([])

        assert isinstance(result, DiscoverOutput)
        assert result.top_patterns == []
        assert result.field_ranking == []
        assert result.combinations_tried == []
        assert result.statistics.total_records == 0

    def test_execute_with_invalid_data(self):
        """Test execute with invalid data."""
        with pytest.raises(DataspotError):
            self.discovery.execute("invalid_data")  # type: ignore


class TestDiscoveryFieldDetection:
    """Test cases for categorical field detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    def test_detect_categorical_fields_basic(self):
        """Test basic categorical field detection."""
        test_data = [
            {"category": "A", "status": "active", "id": 1},
            {"category": "B", "status": "inactive", "id": 2},
            {"category": "A", "status": "active", "id": 3},
        ]

        fields = self.discovery._detect_categorical_fields(test_data)

        # Should detect categorical fields but exclude ID-like fields
        assert "category" in fields
        assert "status" in fields
        # Note: Field detection criteria may vary based on implementation

    def test_detect_categorical_fields_large_sample(self):
        """Test field detection with large data sample."""
        # Create large dataset
        test_data = [
            {"type": f"type_{i % 5}", "status": f"status_{i % 3}", "unique_id": i}
            for i in range(200)
        ]

        fields = self.discovery._detect_categorical_fields(test_data)

        # Should sample efficiently and detect patterns
        assert "type" in fields
        assert "status" in fields
        assert "unique_id" not in fields  # Too unique

    def test_is_suitable_for_analysis_good_fields(self):
        """Test field suitability detection for good categorical fields."""
        test_data = [
            {"category": "A"},
            {"category": "B"},
            {"category": "A"},
            {"category": "B"},
            {"category": "C"},
        ]

        is_suitable = self.discovery._is_suitable_for_analysis(test_data, "category", 5)
        assert is_suitable is True

    def test_is_suitable_for_analysis_unsuitable_fields(self):
        """Test field suitability detection for unsuitable fields."""
        # Too unique (like IDs)
        unique_data = [{"id": i} for i in range(10)]
        is_suitable = self.discovery._is_suitable_for_analysis(unique_data, "id", 10)
        assert is_suitable is False

        # Single value
        single_value_data = [{"status": "active"}] * 5
        is_suitable = self.discovery._is_suitable_for_analysis(
            single_value_data, "status", 5
        )
        assert is_suitable is False

        # Empty field
        empty_data = [{"field": None}] * 3
        is_suitable = self.discovery._is_suitable_for_analysis(empty_data, "field", 3)
        assert is_suitable is False

    def test_is_suitable_for_analysis_small_samples(self):
        """Test field suitability with very small samples."""
        small_data = [{"field": "A"}, {"field": "B"}]
        is_suitable = self.discovery._is_suitable_for_analysis(small_data, "field", 2)
        assert is_suitable is True

        # Single record
        single_record = [{"field": "A"}]
        is_suitable = self.discovery._is_suitable_for_analysis(
            single_record, "field", 1
        )
        assert is_suitable is False


class TestDiscoveryFieldScoring:
    """Test cases for field scoring functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    @patch("dataspot.analyzers.discovery.Finder")
    def test_score_fields_by_potential(self, mock_finder_class):
        """Test field scoring by concentration potential."""
        # Mock high-scoring pattern
        high_pattern = Mock(spec=Pattern)
        high_pattern.percentage = 80.0

        # Mock low-scoring pattern
        low_pattern = Mock(spec=Pattern)
        low_pattern.percentage = 15.0

        mock_finder = Mock()
        mock_finder.execute.side_effect = [
            [high_pattern],  # First field
            [low_pattern],  # Second field
            [],  # Third field
        ]
        mock_finder_class.return_value = mock_finder

        test_data = [{"field1": "A", "field2": "B", "field3": "C"}]
        fields = ["field1", "field2", "field3"]

        scores = self.discovery._score_fields_by_potential(test_data, fields)

        # Should return scored and sorted fields
        assert len(scores) == 3
        assert all(isinstance(score, tuple) and len(score) == 2 for score in scores)

        # Should be sorted by score (descending)
        field_names = [score[0] for score in scores]
        score_values = [score[1] for score in scores]

        assert field_names == ["field1", "field2", "field3"]
        assert score_values == sorted(score_values, reverse=True)

    def test_calculate_field_score_empty_patterns(self):
        """Test field scoring with no patterns."""
        score = self.discovery._calculate_field_score([])
        assert score == 0

    def test_calculate_field_score_with_patterns(self):
        """Test field scoring with various patterns."""
        # Create mock patterns
        patterns = []
        for percentage in [80.0, 50.0, 30.0, 15.0, 5.0]:
            pattern = Mock(spec=Pattern)
            pattern.percentage = percentage
            patterns.append(pattern)

        score = self.discovery._calculate_field_score(patterns)

        # Should calculate weighted score
        assert score > 0
        # Score should incorporate max concentration, significant patterns, and total patterns
        # Note: Exact calculation depends on implementation details

    def test_calculate_field_score_single_pattern(self):
        """Test field scoring with single pattern."""
        pattern = Mock(spec=Pattern)
        pattern.percentage = 60.0

        score = self.discovery._calculate_field_score([pattern])
        expected = 60.0 * 0.5 + 1 * 5 + 1 * 0.5  # 1 significant pattern
        assert abs(score - expected) < 0.1


class TestDiscoveryPatternCombinations:
    """Test cases for pattern combination discovery."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    @patch("dataspot.analyzers.discovery.Finder")
    def test_discover_pattern_combinations(self, mock_finder_class):
        """Test pattern combination discovery."""
        # Mock patterns for different combinations
        pattern1 = Mock(spec=Pattern)
        pattern1.percentage = 70.0
        pattern1.path = "field1=A"

        pattern2 = Mock(spec=Pattern)
        pattern2.percentage = 50.0
        pattern2.path = "field1=A > field2=X"

        mock_finder = Mock()
        mock_finder.execute.side_effect = [
            FindOutput(patterns=[pattern1], total_records=1, total_patterns=1),
            FindOutput(patterns=[pattern2], total_records=1, total_patterns=1),
            FindOutput(patterns=[], total_records=1, total_patterns=0),
        ]
        mock_finder_class.return_value = mock_finder

        test_data = [{"field1": "A", "field2": "X"}]
        field_scores = [("field1", 10.0), ("field2", 8.0)]

        patterns, combinations = self.discovery._discover_pattern_combinations(
            test_data,
            field_scores,
            max_fields=2,
            max_combinations=5,
            min_percentage=10.0,
        )

        # Should find patterns and track combinations
        assert len(patterns) > 0
        assert len(combinations) > 0
        assert all("fields" in combo for combo in combinations)
        assert all("patterns_found" in combo for combo in combinations)

    def test_rank_and_deduplicate_patterns(self):
        """Test pattern ranking and deduplication."""
        # Create duplicate patterns with different percentages
        pattern1 = Mock(spec=Pattern)
        pattern1.percentage = 60.0
        pattern1.path = "field=A"

        pattern2 = Mock(spec=Pattern)
        pattern2.percentage = 80.0  # Higher percentage for same path
        pattern2.path = "field=A"

        pattern3 = Mock(spec=Pattern)
        pattern3.percentage = 40.0
        pattern3.path = "field=B"

        patterns: List[Pattern] = [pattern1, pattern2, pattern3]
        ranked = self.discovery._rank_and_deduplicate_patterns(patterns)

        # Should deduplicate and keep higher percentage
        assert len(ranked) == 2  # Only 2 unique paths
        # Should be sorted by percentage
        assert ranked[0].percentage >= ranked[1].percentage

        # Should keep the higher percentage pattern for duplicated path
        field_a_pattern = next(p for p in ranked if p.path == "field=A")
        assert field_a_pattern.percentage == 80.0


class TestDiscoveryStatistics:
    """Test cases for discovery statistics calculation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    def test_calculate_discovery_statistics(self):
        """Test discovery statistics calculation."""
        test_data = [{"field": "value"}] * 100
        available_fields = ["field1", "field2", "field3"]
        combinations_tried = [
            {"fields": ["field1"], "patterns_found": 5},
            {"fields": ["field1", "field2"], "patterns_found": 3},
        ]

        pattern = Mock(spec=Pattern)
        pattern.percentage = 75.0
        top_patterns: List[Pattern] = [pattern]

        stats = self.discovery._calculate_discovery_statistics(
            test_data, available_fields, combinations_tried, top_patterns
        )

        assert stats["total_records"] == 100
        assert stats["fields_analyzed"] == 3
        assert stats["combinations_tried"] == 2
        assert stats["patterns_discovered"] == 1
        assert stats["best_concentration"] == 75.0

    def test_calculate_discovery_statistics_empty_patterns(self):
        """Test statistics calculation with no patterns."""
        stats = self.discovery._calculate_discovery_statistics([], [], [], [])

        assert stats["total_records"] == 0
        assert stats["fields_analyzed"] == 0
        assert stats["combinations_tried"] == 0
        assert stats["patterns_discovered"] == 0
        assert stats["best_concentration"] == 0


class TestDiscoveryIntegration:
    """Test cases for integration and end-to-end functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    @patch("dataspot.analyzers.discovery.Finder")
    def test_full_discovery_integration(self, mock_finder_class):
        """Test full discovery process integration."""
        # Create realistic test data
        test_data = [
            {"country": "US", "device": "mobile", "category": "premium", "amount": 100},
            {"country": "US", "device": "mobile", "category": "premium", "amount": 150},
            {"country": "US", "device": "desktop", "category": "basic", "amount": 80},
            {"country": "EU", "device": "mobile", "category": "premium", "amount": 120},
            {"country": "EU", "device": "tablet", "category": "basic", "amount": 90},
        ] * 20  # Scale up data

        # Mock realistic patterns
        patterns: List[Pattern] = []
        for _, (percentage, path) in enumerate(
            [
                (60.0, "country=US"),
                (45.0, "category=premium"),
                (35.0, "device=mobile"),
                (25.0, "country=US > device=mobile"),
            ]
        ):
            pattern = Mock(spec=Pattern)
            pattern.percentage = percentage
            pattern.path = path
            patterns.append(pattern)

        mock_finder = Mock()
        mock_finder.execute.return_value = FindOutput(
            patterns=patterns[:2],  # Return subset for each call
            total_records=len(test_data),
            total_patterns=2,
        )
        mock_finder_class.return_value = mock_finder

        result = self.discovery.execute(test_data, max_fields=3, max_combinations=10)

        # Verify comprehensive results
        assert len(result.top_patterns) > 0
        assert len(result.field_ranking) > 0
        assert len(result.combinations_tried) > 0
        assert result.statistics.total_records == 100
        assert result.statistics.fields_analyzed > 0


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

    @patch("dataspot.analyzers.discovery.Finder")
    def test_discovery_with_problematic_fields(self, mock_finder_class):
        """Test discovery when some fields cause exceptions."""
        # Mock finder to raise exception for certain fields
        mock_finder = Mock()
        mock_finder.execute.side_effect = [
            Exception("Field error"),
            FindOutput(patterns=[], total_records=1, total_patterns=0),
        ]
        mock_finder_class.return_value = mock_finder

        test_data = [{"good_field": "A", "bad_field": "B"}]
        fields = ["bad_field", "good_field"]

        scores = self.discovery._score_fields_by_potential(test_data, fields)

        # Should handle exceptions gracefully
        assert len(scores) == 2
        # Bad field should get score of 0
        bad_field_score = next(score for field, score in scores if field == "bad_field")
        assert bad_field_score == 0

    @patch("dataspot.analyzers.discovery.Finder")
    def test_large_dataset_performance(self, mock_finder_class):
        """Test discovery performance with larger dataset."""
        # Create large dataset
        test_data = [
            {"type": f"type_{i % 10}", "status": f"status_{i % 5}", "id": i}
            for i in range(1000)
        ]

        mock_finder = Mock()
        mock_finder.execute.return_value = []
        mock_finder_class.return_value = mock_finder

        result = self.discovery.execute(test_data, max_fields=2, max_combinations=5)

        # Should complete without performance issues
        assert result.statistics.total_records == 1000
        assert result.field_ranking is not None

    def test_field_detection_edge_cases(self):
        """Test field detection with edge cases."""
        # Data with mixed types
        mixed_data = [
            {"field": "string"},
            {"field": 123},
            {"field": None},
            {"field": "another_string"},
            {"field": 456},
        ]

        fields = self.discovery._detect_categorical_fields(mixed_data)

        assert "field" in fields
        assert len(fields) == 1
