"""Tests for Discovery analyzer."""

from dataspot.analyzers.discovery import Discovery
from dataspot.models.discovery import DiscoverInput, DiscoverOptions


class TestDiscovery:
    """Test Discovery analyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = Discovery()

    def test_discovery_basic(self, fake_transactions_data):
        """Test basic pattern discovery."""
        result = self.discovery.execute(DiscoverInput(data=fake_transactions_data))

        assert len(result.top_patterns) > 0
        assert result.statistics.total_records == len(fake_transactions_data)
        assert len(result.field_ranking) > 0

    def test_discovery_with_options(self, fake_transactions_data):
        """Test discovery with options."""
        result = self.discovery.execute(
            DiscoverInput(data=fake_transactions_data),
            DiscoverOptions(min_percentage=15.0, max_combinations=10),
        )

        assert result.statistics.total_records == len(fake_transactions_data)
        assert result.statistics.fields_analyzed > 0
        assert len(result.top_patterns) > 0
        assert len(result.field_ranking) > 0

    def test_discovery_diverse_data(self, diverse_transaction_data):
        """Test discovery with diverse data patterns."""
        result = self.discovery.execute(DiscoverInput(data=diverse_transaction_data))

        assert len(result.top_patterns) > 0
        assert result.statistics.fields_analyzed > 0
        assert result.statistics.total_records > 0
