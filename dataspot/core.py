"""Core pattern dataspot for finding data concentration dataspots."""

from typing import Any, Callable

from .analyzers import Analyzer, Base, Compare, Discovery, Tree
from .models.analyzer import AnalyzeInput, AnalyzeOptions, AnalyzeOutput
from .models.compare import CompareInput, CompareOptions, CompareOutput
from .models.discovery import DiscoverInput, DiscoverOptions, DiscoverOutput
from .models.finder import FindInput, FindOptions, FindOutput
from .models.tree import TreeInput, TreeOptions, TreeOutput


class Dataspot:
    """Finds concentration patterns and dataspots in datasets.

    This dataspot builds hierarchical trees of patterns and identifies
    where data concentrates, helping spot anomalies and insights.
    """

    def __init__(self):
        """Initialize the Dataspot class."""
        self._base = Base()

    def add_preprocessor(
        self, field_name: str, preprocessor: Callable[[Any], Any]
    ) -> None:
        """Add a custom preprocessor for a specific field."""
        self._base.add_preprocessor(field_name, preprocessor)

    def find(
        self,
        input: FindInput,
        options: FindOptions,
    ) -> FindOutput:
        """Find concentration patterns in data.

        Args:
            input: FindInput containing data, fields, and optional query
            options: FindOptions containing filtering and display options

        Returns:
            FindOutput dataclass with patterns and metadata

        """
        from .analyzers.finder import Finder

        finder = Finder()
        finder.preprocessors = self._base.preprocessors
        return finder.execute(input, options)

    def analyze(
        self,
        input: AnalyzeInput,
        options: AnalyzeOptions,
    ) -> AnalyzeOutput:
        """Analyze data and return comprehensive insights.

        Args:
            input: AnalyzeInput containing data, fields, and optional query
            options: AnalyzeOptions containing filtering and display options

        Returns:
            AnalyzeOutput dataclass with patterns, statistics, and insights

        """
        analyzer = Analyzer()
        analyzer.preprocessors = self._base.preprocessors
        return analyzer.execute(input, options)

    def tree(
        self,
        input: TreeInput,
        options: TreeOptions,
    ) -> TreeOutput:
        """Build and return hierarchical tree structure in JSON format.

        Args:
            input: TreeInput containing data, fields, and optional query
            options: TreeOptions containing filtering and display options

        Returns:
            TreeOutput dataclass representing the hierarchical tree structure

        Example:
            tree_input = TreeInput(
                data=[{'country': 'US', 'device': 'mobile'}],
                fields=['country', 'device']
            )
            tree_options = TreeOptions(top=10, max_depth=3)
            result = dataspot.tree(tree_input, tree_options)

        """
        tree = Tree()
        tree.preprocessors = self._base.preprocessors
        return tree.execute(input, options)

    def discover(
        self,
        input: DiscoverInput,
        options: DiscoverOptions,
    ) -> DiscoverOutput:
        """Automatically discover the most interesting concentration patterns.

        This method analyzes all available fields and automatically finds
        the combinations that show the highest concentration patterns.

        Args:
            input: DiscoverInput containing data and optional query
            options: DiscoverOptions containing discovery and filtering parameters

        Returns:
            DiscoverOutput dataclass with discovered patterns and field analysis.

        Example:
            discover_input = DiscoverInput(data=data)
            discover_options = DiscoverOptions(max_fields=3, min_percentage=15.0)
            results = dataspot.discover(discover_input, discover_options)
            print(f"Best pattern: {results.top_patterns[0].path}")
            print(f"Most valuable fields: {results.field_ranking}")

        """
        discovery = Discovery()
        discovery.preprocessors = self._base.preprocessors
        return discovery.execute(input, options)

    def compare(
        self,
        input: CompareInput,
        options: CompareOptions,
    ) -> CompareOutput:
        """Compare datasets to detect changes and anomalies between periods.

        Args:
            input: CompareInput containing current data, baseline data, fields, and optional query
            options: CompareOptions containing statistical and filtering parameters

        Returns:
            CompareOutput dataclass with comprehensive comparison results and changes.

        Example:
            # Fraud detection comparison
            compare_input = CompareInput(
                current_data=this_month_transactions,
                baseline_data=last_month_transactions,
                fields=["country", "payment_method"],
                query={"country": ["US", "EU"]},
            )
            compare_options = CompareOptions(
                statistical_significance=True,
                change_threshold=0.25,
            )
            changes = dataspot.compare(compare_input, compare_options)

        """
        compare = Compare()
        compare.preprocessors = self._base.preprocessors
        return compare.execute(input, options)
