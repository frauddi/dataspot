"""Tests for Compare analyzer."""

from dataspot.analyzers.compare import Compare
from dataspot.models.compare import CompareInput, CompareOptions


class TestCompare:
    """Test Compare analyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.compare = Compare()

    def test_compare_equal_data(self, identical_dataset_small, compare_fields):
        """Test that identical data produces no changes."""
        result = self.compare.execute(
            CompareInput(
                current_data=identical_dataset_small,
                baseline_data=identical_dataset_small,
                fields=compare_fields,
            )
        )

        assert len(result.changes) == 0
        assert result.statistics.current_total == len(identical_dataset_small)

    def test_compare_different_data(
        self, baseline_dataset_small, modified_current_dataset, compare_fields
    ):
        """Test that different data produces detectable changes."""
        result = self.compare.execute(
            CompareInput(
                current_data=modified_current_dataset,
                baseline_data=baseline_dataset_small,
                fields=compare_fields,
            )
        )

        assert len(result.changes) > 0
        assert len(result.new_patterns) > 0

    def test_compare_empty_data(self, compare_fields):
        """Test compare with empty data."""
        result = self.compare.execute(
            CompareInput(current_data=[], baseline_data=[], fields=compare_fields)
        )

        assert len(result.changes) == 0
        assert result.statistics.current_total == 0

    def test_compare_with_options(
        self, baseline_dataset_small, modified_current_dataset, compare_fields
    ):
        """Test compare with specific options."""
        result = self.compare.execute(
            CompareInput(
                current_data=modified_current_dataset,
                baseline_data=baseline_dataset_small,
                fields=compare_fields,
            ),
            CompareOptions(change_threshold=0.5, min_percentage=20.0),
        )

        assert result.change_threshold == 0.5
        assert result.statistics.current_total == len(modified_current_dataset)
