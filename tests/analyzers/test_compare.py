"""Tests for Compare analyzer functionality."""

import pytest

from dataspot.analyzers.compare import Compare
from dataspot.exceptions import DataspotError
from dataspot.models.compare import CompareInput, CompareOptions


class TestCompareInitialization:
    """Test cases for Compare class initialization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compare = Compare()

    def test_initialization(self):
        """Test that Compare initializes correctly."""
        assert isinstance(self.compare, Compare)
        assert hasattr(self.compare, "preprocessor_manager")
        assert hasattr(self.compare, "statistical_methods")
        # Should inherit from Base
        assert hasattr(self.compare, "_validate_data")
        assert hasattr(self.compare, "_filter_data_by_query")

    def test_inheritance_from_base(self):
        """Test that Compare properly inherits from Base."""
        # Should have all Base methods
        assert hasattr(self.compare, "add_preprocessor")
        assert hasattr(self.compare, "_build_tree")


class TestCompareExecute:
    """Test cases for the main execute method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compare = Compare()

        # Current period data (larger dataset)
        self.current_data = [
            {"transaction_type": "payment", "country": "US", "amount": 100},
            {"transaction_type": "payment", "country": "US", "amount": 150},
            {"transaction_type": "payment", "country": "CA", "amount": 200},
            {"transaction_type": "refund", "country": "US", "amount": 50},
            {"transaction_type": "payment", "country": "MX", "amount": 300},
        ]

        # Baseline period data (smaller dataset)
        self.baseline_data = [
            {"transaction_type": "payment", "country": "US", "amount": 100},
            {"transaction_type": "payment", "country": "CA", "amount": 200},
        ]

    def test_execute_basic(self):
        """Test basic execute functionality."""
        compare_input = CompareInput(
            current_data=self.current_data,
            baseline_data=self.baseline_data,
            fields=["transaction_type", "country"],
        )
        compare_options = CompareOptions()
        result = self.compare.execute(compare_input, compare_options)

        # Check result structure
        assert result.changes is not None
        assert result.statistics is not None
        assert result.statistics.current_total == len(self.current_data)
        assert result.statistics.baseline_total == len(self.baseline_data)
        assert result.fields_analyzed == ["transaction_type", "country"]
        assert result.statistical_significance is False  # Default value

        assert result.statistics.current_total == len(self.current_data)
        assert result.statistics.baseline_total == len(self.baseline_data)
        assert result.fields_analyzed == ["transaction_type", "country"]

    def test_execute_with_invalid_data(self):
        """Test execute with invalid data."""
        compare_input = CompareInput(
            current_data="invalid_data",  # type: ignore
            baseline_data=self.baseline_data,
            fields=["field"],
        )
        compare_options = CompareOptions()

        with pytest.raises(DataspotError):
            self.compare.execute(compare_input, compare_options)

        compare_input = CompareInput(
            current_data=self.current_data,
            baseline_data="invalid_data",  # type: ignore
            fields=["field"],
        )

        with pytest.raises(DataspotError):
            self.compare.execute(compare_input, compare_options)

    def test_execute_with_empty_data(self):
        """Test execute with empty data."""
        compare_input = CompareInput(
            current_data=[],
            baseline_data=self.baseline_data,
            fields=["transaction_type"],
        )
        compare_options = CompareOptions()
        result = self.compare.execute(compare_input, compare_options)

        assert result.statistics.current_total == 0
        assert len(result.changes) >= 0

    def test_execute_with_query(self):
        """Test execute with query filtering."""
        query = {"country": "US"}
        compare_input = CompareInput(
            current_data=self.current_data,
            baseline_data=self.baseline_data,
            fields=["transaction_type"],
            query=query,
        )
        compare_options = CompareOptions()
        result = self.compare.execute(compare_input, compare_options)

        # Should still have proper structure
        assert result.changes is not None

    def test_execute_with_statistical_significance(self):
        """Test execute with statistical significance enabled."""
        compare_input = CompareInput(
            current_data=self.current_data,
            baseline_data=self.baseline_data,
            fields=["transaction_type", "country"],
        )
        compare_options = CompareOptions(statistical_significance=True)
        result = self.compare.execute(compare_input, compare_options)

        assert result.statistical_significance is True

        # Check that changes with statistical significance have stats
        for change in result.changes:
            if change.current_count > 0 and change.baseline_count > 0:
                assert change.statistical_significance is not None
                if change.statistical_significance:
                    stats = change.statistical_significance
                    assert "p_value" in stats
                    assert "is_significant" in stats
                    assert "confidence_interval" in stats


class TestCompareStatusUppercase:
    """Test cases specifically for uppercase status values."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compare = Compare()

        # Data designed to create different status types
        self.current_data = (
            [{"type": "A"}] * 20  # Will create significant increase
            + [{"type": "B"}] * 10  # Will create stable or slight change
            + [{"type": "C"}] * 5  # New pattern
        )

        self.baseline_data = (
            [{"type": "A"}] * 10  # Half the current amount
            + [{"type": "B"}] * 10  # Same amount
        )

    def test_status_values_are_uppercase(self):
        """Test that all status values are returned in uppercase."""
        compare_input = CompareInput(
            current_data=self.current_data,
            baseline_data=self.baseline_data,
            fields=["type"],
        )
        compare_options = CompareOptions()
        result = self.compare.execute(compare_input, compare_options)

        # Check that all status values are uppercase
        for change in result.changes:
            status = change.status
            assert status.isupper(), f"Status '{status}' should be uppercase"
            assert status in [
                "NEW",
                "DISAPPEARED",
                "STABLE",
                "SLIGHT_INCREASE",
                "INCREASE",
                "SIGNIFICANT_INCREASE",
                "CRITICAL_INCREASE",
                "SLIGHT_DECREASE",
                "DECREASE",
                "CRITICAL_DECREASE",
            ]

    def test_new_and_disappeared_patterns(self):
        """Test detection of new and disappeared patterns."""
        compare_input = CompareInput(
            current_data=self.current_data,
            baseline_data=self.baseline_data,
            fields=["type"],
        )
        compare_options = CompareOptions()
        result = self.compare.execute(compare_input, compare_options)

        # Should detect type "C" as NEW
        type_c_changes = [c for c in result.changes if "type=C" in c.path]
        assert len(type_c_changes) > 0
        assert type_c_changes[0].status == "NEW"
        assert type_c_changes[0].is_new is True


class TestCompareChanges:
    """Test cases for change detection functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compare = Compare()

    def test_new_pattern_detection(self):
        """Test detection of new patterns."""
        current_data = [
            {"category": "electronics", "brand": "apple"},
            {"category": "electronics", "brand": "samsung"},
            {"category": "books", "brand": "penguin"},  # New pattern
        ]

        baseline_data = [
            {"category": "electronics", "brand": "apple"},
            {"category": "electronics", "brand": "samsung"},
        ]

        compare_input = CompareInput(
            current_data=current_data,
            baseline_data=baseline_data,
            fields=["category", "brand"],
        )
        compare_options = CompareOptions()
        result = self.compare.execute(compare_input, compare_options)

        # Should detect books category as new
        new_patterns = result.new_patterns
        assert len(new_patterns) > 0

        books_pattern = next(
            (p for p in new_patterns if "category=books" in p.path), None
        )
        assert books_pattern is not None
        assert books_pattern.is_new is True

    def test_disappeared_pattern_detection(self):
        """Test detection of disappeared patterns."""
        current_data = [
            {"product": "laptop", "status": "active"},
        ]

        baseline_data = [
            {"product": "laptop", "status": "active"},
            {"product": "phone", "status": "active"},  # Will disappear
        ]

        compare_input = CompareInput(
            current_data=current_data,
            baseline_data=baseline_data,
            fields=["product", "status"],
        )
        compare_options = CompareOptions()
        result = self.compare.execute(compare_input, compare_options)

        # Should detect phone as disappeared
        disappeared_patterns = result.disappeared_patterns
        assert len(disappeared_patterns) > 0

        phone_pattern = next(
            (p for p in disappeared_patterns if "product=phone" in p.path), None
        )
        assert phone_pattern is not None
        assert phone_pattern.is_disappeared is True

    def test_categorized_patterns_structure(self):
        """Test that patterns are properly categorized."""
        current_data = [{"type": "A"}] * 15 + [{"type": "B"}] * 10 + [{"type": "C"}] * 5
        baseline_data = [{"type": "A"}] * 10 + [{"type": "B"}] * 10

        compare_input = CompareInput(
            current_data=current_data, baseline_data=baseline_data, fields=["type"]
        )
        compare_options = CompareOptions()
        result = self.compare.execute(compare_input, compare_options)

        # Check categorized patterns
        assert result.stable_patterns is not None
        assert result.new_patterns is not None
        assert result.disappeared_patterns is not None
        assert result.increased_patterns is not None
        assert result.decreased_patterns is not None

        # Each category should be a list
        assert isinstance(result.stable_patterns, list)
        assert isinstance(result.new_patterns, list)
        assert isinstance(result.disappeared_patterns, list)
        assert isinstance(result.increased_patterns, list)
        assert isinstance(result.decreased_patterns, list)


class TestCompareEdgeCases:
    """Test cases for edge cases and error conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compare = Compare()

    def test_execute_with_identical_data(self):
        """Test execute with identical current and baseline data."""
        identical_data = [
            {"field1": "value1", "field2": "value2"},
            {"field1": "value3", "field2": "value4"},
        ]

        compare_input = CompareInput(
            current_data=identical_data,
            baseline_data=identical_data,
            fields=["field1", "field2"],
        )
        compare_options = CompareOptions()
        result = self.compare.execute(compare_input, compare_options)

        # Identical data should have no changes at all
        assert len(result.changes) == 0
        assert result.statistics.significant_changes == 0
        assert len(result.new_patterns) == 0
        assert len(result.disappeared_patterns) == 0

    def test_execute_with_statistical_significance_comprehensive(self):
        """Test comprehensive statistical significance calculation."""
        # Create data with clear statistical differences
        current_data = [{"type": "fraud"}] * 100  # High count
        baseline_data = [{"type": "fraud"}] * 50  # Lower count

        compare_input = CompareInput(
            current_data=current_data, baseline_data=baseline_data, fields=["type"]
        )
        compare_options = CompareOptions(statistical_significance=True)
        result = self.compare.execute(compare_input, compare_options)

        # Find the fraud pattern change
        fraud_changes = [c for c in result.changes if "type=fraud" in c.path]
        assert len(fraud_changes) > 0

        fraud_change = fraud_changes[0]
        assert fraud_change.statistical_significance is not None

        if fraud_change.statistical_significance:
            stats = fraud_change.statistical_significance
            # Should have comprehensive statistical analysis
            assert "p_value" in stats
            assert "is_significant" in stats
            assert "confidence_interval" in stats
            assert "effect_size" in stats
            assert "test_statistics" in stats
            assert "interpretation" in stats
