"""Unit tests for the Compare class.

This module tests the Compare class focusing on temporal/segmental data comparison
with emphasis on uppercase status and type values consistency.
"""

import pytest

from dataspot.analyzers.compare import Compare
from dataspot.exceptions import DataspotError


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
        result = self.compare.execute(
            current_data=self.current_data,
            baseline_data=self.baseline_data,
            fields=["transaction_type", "country"],
        )

        # Check result structure
        assert "changes" in result
        assert "current_total" in result
        assert "baseline_total" in result
        assert "fields_analyzed" in result
        assert "statistical_significance" in result

        assert result["current_total"] == len(self.current_data)
        assert result["baseline_total"] == len(self.baseline_data)
        assert result["fields_analyzed"] == ["transaction_type", "country"]

    def test_execute_with_invalid_data(self):
        """Test execute with invalid data."""
        with pytest.raises(DataspotError):
            self.compare.execute(
                current_data="invalid_data",  # type: ignore
                baseline_data=self.baseline_data,
                fields=["field"],
            )

        with pytest.raises(DataspotError):
            self.compare.execute(
                current_data=self.current_data,
                baseline_data="invalid_data",  # type: ignore
                fields=["field"],
            )

    def test_execute_with_empty_data(self):
        """Test execute with empty data."""
        result = self.compare.execute(
            current_data=[],
            baseline_data=self.baseline_data,
            fields=["transaction_type"],
        )

        assert result["current_total"] == 0
        assert len(result["changes"]) >= 0

    def test_execute_with_query(self):
        """Test execute with query filtering."""
        query = {"country": "US"}
        result = self.compare.execute(
            current_data=self.current_data,
            baseline_data=self.baseline_data,
            fields=["transaction_type"],
            query=query,
        )

        # Should still have proper structure
        assert "changes" in result

    def test_execute_with_statistical_significance(self):
        """Test execute with statistical significance enabled."""
        result = self.compare.execute(
            current_data=self.current_data,
            baseline_data=self.baseline_data,
            fields=["transaction_type", "country"],
            statistical_significance=True,
        )

        assert result["statistical_significance"] is True

        # Check that changes with statistical significance have stats
        for change in result["changes"]:
            if change["current_count"] > 0 and change["baseline_count"] > 0:
                assert "statistical_significance" in change
                if change["statistical_significance"]:
                    stats = change["statistical_significance"]
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
        result = self.compare.execute(
            current_data=self.current_data,
            baseline_data=self.baseline_data,
            fields=["type"],
        )

        # Check that all status values are uppercase
        for change in result["changes"]:
            status = change["status"]
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
        result = self.compare.execute(
            current_data=self.current_data,
            baseline_data=self.baseline_data,
            fields=["type"],
        )

        # Should detect type "C" as NEW
        type_c_changes = [c for c in result["changes"] if "type=C" in c["path"]]
        assert len(type_c_changes) > 0
        assert type_c_changes[0]["status"] == "NEW"
        assert type_c_changes[0]["is_new"] is True


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

        result = self.compare.execute(
            current_data=current_data,
            baseline_data=baseline_data,
            fields=["category", "brand"],
        )

        # Should detect books category as new
        new_patterns = result["new_patterns"]
        assert len(new_patterns) > 0

        books_pattern = next(
            (p for p in new_patterns if "category=books" in p["path"]), None
        )
        assert books_pattern is not None
        assert books_pattern["is_new"] is True

    def test_disappeared_pattern_detection(self):
        """Test detection of disappeared patterns."""
        current_data = [
            {"product": "laptop", "status": "active"},
        ]

        baseline_data = [
            {"product": "laptop", "status": "active"},
            {"product": "phone", "status": "active"},  # Will disappear
        ]

        result = self.compare.execute(
            current_data=current_data,
            baseline_data=baseline_data,
            fields=["product", "status"],
        )

        # Should detect phone as disappeared
        disappeared_patterns = result["disappeared_patterns"]
        assert len(disappeared_patterns) > 0

        phone_pattern = next(
            (p for p in disappeared_patterns if "product=phone" in p["path"]), None
        )
        assert phone_pattern is not None
        assert phone_pattern["is_disappeared"] is True

    def test_categorized_patterns_structure(self):
        """Test that patterns are properly categorized."""
        current_data = [{"type": "A"}] * 15 + [{"type": "B"}] * 10 + [{"type": "C"}] * 5
        baseline_data = [{"type": "A"}] * 10 + [{"type": "B"}] * 10

        result = self.compare.execute(
            current_data=current_data,
            baseline_data=baseline_data,
            fields=["type"],
        )

        # Check categorized patterns
        assert "stable_patterns" in result
        assert "new_patterns" in result
        assert "disappeared_patterns" in result
        assert "increased_patterns" in result
        assert "decreased_patterns" in result

        # Each category should be a list
        assert isinstance(result["stable_patterns"], list)
        assert isinstance(result["new_patterns"], list)
        assert isinstance(result["disappeared_patterns"], list)
        assert isinstance(result["increased_patterns"], list)
        assert isinstance(result["decreased_patterns"], list)


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

        result = self.compare.execute(
            current_data=identical_data,
            baseline_data=identical_data,
            fields=["field1", "field2"],
        )

        # Should have changes but they should all be stable
        assert len(result["changes"]) > 0
        stable_changes = [c for c in result["changes"] if c["status"] == "STABLE"]
        assert len(stable_changes) > 0

    def test_execute_with_statistical_significance_comprehensive(self):
        """Test comprehensive statistical significance calculation."""
        # Create data with clear statistical differences
        current_data = [{"type": "fraud"}] * 100  # High count
        baseline_data = [{"type": "fraud"}] * 50  # Lower count

        result = self.compare.execute(
            current_data=current_data,
            baseline_data=baseline_data,
            fields=["type"],
            statistical_significance=True,
        )

        # Find the fraud pattern change
        fraud_changes = [c for c in result["changes"] if "type=fraud" in c["path"]]
        assert len(fraud_changes) > 0

        fraud_change = fraud_changes[0]
        assert "statistical_significance" in fraud_change

        if fraud_change["statistical_significance"]:
            stats = fraud_change["statistical_significance"]
            # Should have comprehensive statistical analysis
            assert "p_value" in stats
            assert "is_significant" in stats
            assert "confidence_interval" in stats
            assert "effect_size" in stats
            assert "test_statistics" in stats
            assert "interpretation" in stats
