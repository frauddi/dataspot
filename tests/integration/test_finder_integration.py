"""Tests for Finder analyzer."""

from dataspot.analyzers.finder import Finder
from dataspot.models.finder import FindInput, FindOptions


class TestFinder:
    """Test Finder analyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.finder = Finder()

    def test_finder_basic(self, fake_transactions_data, compare_fields):
        """Test basic pattern finding."""
        result = self.finder.execute(
            FindInput(data=fake_transactions_data, fields=compare_fields)
        )

        assert len(result.patterns) > 0
        assert result.total_records == len(fake_transactions_data)

    def test_finder_with_options(self, fake_transactions_data, compare_fields):
        """Test finder with filtering options."""
        result = self.finder.execute(
            FindInput(data=fake_transactions_data, fields=compare_fields),
            FindOptions(min_percentage=20.0, min_count=1),
        )

        assert result.total_records == len(fake_transactions_data)
        for pattern in result.patterns:
            assert pattern.percentage >= 20.0
            assert pattern.count >= 1

    def test_finder_empty_data(self, compare_fields):
        """Test finder with empty data."""
        result = self.finder.execute(FindInput(data=[], fields=compare_fields))

        assert len(result.patterns) == 0
        assert result.total_records == 0
