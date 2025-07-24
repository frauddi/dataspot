"""Tests for Analyzer."""

from dataspot.analyzers.analyzer import Analyzer
from dataspot.models.analyzer import AnalyzeInput, AnalyzeOptions


class TestAnalyzer:
    """Test Analyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = Analyzer()

    def test_analyzer_basic(self, fake_transactions_data, compare_fields):
        """Test basic data analysis."""
        result = self.analyzer.execute(
            AnalyzeInput(data=fake_transactions_data, fields=compare_fields)
        )

        assert result.statistics.total_records == len(fake_transactions_data)
        assert len(result.patterns) > 0
        assert result.statistics.patterns_found > 0

    def test_analyzer_with_options(self, fake_transactions_data, compare_fields):
        """Test analyzer with specific options."""
        result = self.analyzer.execute(
            AnalyzeInput(data=fake_transactions_data, fields=compare_fields),
            AnalyzeOptions(min_percentage=30.0, min_count=2),
        )

        assert result.statistics.total_records == len(fake_transactions_data)
        for pattern in result.patterns:
            assert pattern.percentage >= 30.0
            assert pattern.count >= 2

    def test_analyzer_single_field(self, fake_transactions_data):
        """Test analyzer with single field."""
        result = self.analyzer.execute(
            AnalyzeInput(data=fake_transactions_data, fields=["brand"])
        )

        assert result.statistics.total_records == len(fake_transactions_data)
        assert len(result.patterns) > 0
