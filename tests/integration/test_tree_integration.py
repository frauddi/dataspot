"""Tests for Tree analyzer."""

from dataspot.analyzers.tree import Tree
from dataspot.models.tree import TreeInput, TreeOptions


class TestTree:
    """Test Tree analyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tree = Tree()

    def test_tree_basic(self, fake_transactions_data, compare_fields):
        """Test basic tree analysis."""
        result = self.tree.execute(
            TreeInput(data=fake_transactions_data, fields=compare_fields)
        )

        assert result.statistics.total_records == len(fake_transactions_data)
        assert len(result.children) > 0

    def test_tree_with_options(self, fake_transactions_data, compare_fields):
        """Test tree with depth options."""
        result = self.tree.execute(
            TreeInput(data=fake_transactions_data, fields=compare_fields),
            TreeOptions(max_depth=2, min_percentage=10.0),
        )

        assert result.statistics.total_records == len(fake_transactions_data)

    def test_tree_simple_data(self, sample_transaction):
        """Test tree with simple data."""
        result = self.tree.execute(
            TreeInput(data=[sample_transaction], fields=["brand", "currency"])
        )

        assert result.statistics.total_records == 1
        assert len(result.children) > 0
