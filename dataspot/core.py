"""Core pattern dataspot for finding data concentration dataspots."""

from typing import Any, Callable, Dict, List, Optional

from .analyzers import Analyzer, Base, Compare, Discovery, Tree
from .models.analyzer import AnalyzeOutput
from .models.compare import CompareOutput
from .models.discovery import DiscoverOutput
from .models.finder import FindOutput
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
        data: List[Dict[str, Any]],
        fields: List[str],
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> FindOutput:
        """Find concentration patterns in data.

        This method discovers data concentration patterns across hierarchical field combinations.
        It identifies where data naturally clusters and provides insights into distribution patterns.

        Args:
            data: List of records (dictionaries) to analyze
            fields: List of field names to analyze hierarchically (e.g., ['country', 'city', 'device'])
            query: Optional filters to apply to data before analysis
                Example: {'status': 'active', 'amount': {'$gt': 100}}
            **kwargs: Additional filtering options:
                - min_percentage (float): Minimum concentration threshold (default: 1.0)
                - min_count (int): Minimum record count per pattern
                - max_count (int): Maximum record count per pattern
                - limit (int): Maximum number of patterns to return

        Returns:
            FindOutput dataclass containing:
                - patterns: List of Pattern objects with concentration data
                - total_records: Number of records analyzed
                - total_patterns: Number of patterns found

        Example:
            Basic pattern finding:
            >>> patterns = ds.find(transactions, ['country', 'payment_method'])
            >>> print(f"Found {patterns.total_patterns} patterns in {patterns.total_records} records")
            >>> top_pattern = patterns.patterns[0]
            >>> print(f"Top pattern: {top_pattern.path} ({top_pattern.percentage}%)")

            Fraud detection example:
            >>> suspicious_patterns = ds.find(
            ...     fraud_data,
            ...     ['ip_country', 'device_type', 'payment_method'],
            ...     query={'risk_score': {'$gt': 0.7}},
            ...     min_percentage=5.0
            ... )

        """
        from .analyzers.finder import Finder

        finder = Finder()
        finder.preprocessors = self._base.preprocessors
        return finder.execute(data, fields, query, **kwargs)

    def analyze(
        self,
        data: List[Dict[str, Any]],
        fields: List[str],
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> AnalyzeOutput:
        """Analyze data and return comprehensive insights.

        Returns:
            Dictionary with patterns, statistics, and insights

        """
        analyzer = Analyzer()
        analyzer.preprocessors = self._base.preprocessors
        return analyzer.execute(data, fields, query, **kwargs)

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
        data: List[Dict[str, Any]],
        max_fields: int = 3,
        max_combinations: int = 10,
        min_percentage: float = 10.0,
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> DiscoverOutput:
        """Automatically discover the most interesting concentration patterns.

        This method analyzes all available fields and automatically finds
        the combinations that show the highest concentration patterns.

        Args:
            data: List of records (dictionaries)
            max_fields: Maximum number of fields to combine (default: 3)
            max_combinations: Maximum combinations to try (default: 10)
            min_percentage: Minimum concentration to consider (default: 10%)
            query: Optional filters to apply to data
            **kwargs: Additional filtering options (same as find method)

        Returns:
            Dictionary with discovered patterns and field analysis.

        Example:
            results = dataspot.discover(data)
            print(f"Best pattern: {results['top_patterns'][0].path}")
            print(f"Most valuable fields: {results['field_ranking']}")

        """
        discovery = Discovery()
        discovery.preprocessors = self._base.preprocessors
        return discovery.execute(
            data, max_fields, max_combinations, min_percentage, query, **kwargs
        )

    def compare(
        self,
        current_data: List[Dict[str, Any]],
        baseline_data: List[Dict[str, Any]],
        fields: List[str],
        statistical_significance: bool = False,
        change_threshold: float = 0.15,
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> CompareOutput:
        """Compare datasets to detect changes and anomalies between periods.

        Args:
            current_data: Current period data
            baseline_data: Baseline period data for comparison
            fields: List of field names to analyze for changes
            statistical_significance: Calculate p-values and confidence intervals (default: False)
            change_threshold: Threshold for significant changes, 0.15 = 15% (default: 0.15)
            query: Optional filters to apply to both datasets
            **kwargs: Additional filtering options (same as find method)

        Returns:
            Dictionary with comprehensive comparison results and changes.

        Example:
            # Fraud detection comparison
            changes = dataspot.compare(
                current_data=this_month_transactions,
                baseline_data=last_month_transactions,
                fields=["country", "payment_method"],
                statistical_significance=True,
                change_threshold=0.25,
                query={"country": ["US", "EU"]},
            )

        """
        compare = Compare()
        compare.preprocessors = self._base.preprocessors
        return compare.execute(
            current_data=current_data,
            baseline_data=baseline_data,
            fields=fields,
            statistical_significance=statistical_significance,
            change_threshold=change_threshold,
            query=query,
            **kwargs,
        )
