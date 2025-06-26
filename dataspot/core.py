"""Core pattern dataspot for finding data concentration dataspots."""

from typing import Any, Callable, Dict, List, Optional

from .analyzers import Analyzer, Base, Discovery, Finder, Tree
from .models import Pattern


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
    ) -> List[Pattern]:
        """Find concentration patterns in data.

        Args:
            data: List of records (dictionaries)
            fields: List of field names to analyze hierarchically
            query: Optional filters to apply to data
            **kwargs: Additional filtering options
                - min_percentage: Minimum percentage for a pattern to be included
                - max_percentage: Maximum percentage for a pattern to be included
                - min_count: Minimum count for a pattern to be included
                - max_count: Maximum count for a pattern to be included
                - min_depth: Minimum depth for a pattern to be included
                - max_depth: Maximum depth to analyze
                - contains: Pattern path must contain this text
                - exclude: Pattern path must NOT contain these texts (string or list)
                - regex: Pattern path must match this regex
                - limit: Maximum number of patterns to return

        Returns:
            List of Pattern objects sorted by percentage

        """
        finder = Finder()
        finder.preprocessors = self._base.preprocessors
        return finder.execute(data, fields, query, **kwargs)

    def analyze(
        self,
        data: List[Dict[str, Any]],
        fields: List[str],
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Analyze data and return comprehensive insights.

        Returns:
            Dictionary with patterns, statistics, and insights

        """
        analyzer = Analyzer()
        analyzer.preprocessors = self._base.preprocessors
        return analyzer.execute(data, fields, query, **kwargs)

    def tree(
        self,
        data: List[Dict[str, Any]],
        fields: List[str],
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Build and return hierarchical tree structure in JSON format.

        Args:
            data: List of records (dictionaries)
            fields: List of field names to analyze hierarchically
            query: Optional filters to apply to data
            **kwargs: Additional filtering options
                - top: Number of top elements to consider per level (default: 5)
                - min_value: Minimum count for a node to be included
                - min_percentage: Minimum percentage for a node to be included
                - max_value: Maximum count for a node to be included
                - max_percentage: Maximum percentage for a node to be included
                - min_depth: Minimum depth for nodes to be included
                - max_depth: Maximum depth to analyze (limits tree depth)
                - contains: Node name must contain this text
                - exclude: Node name must NOT contain these texts
                - regex: Node name must match this regex pattern

        Returns:
            Dictionary representing the hierarchical tree structure

        Example:
            {
                'name': 'root',
                'children': [
                    {
                        'name': 'country=US',
                        'value': 150,
                        'percentage': 75.0,
                        'node': 1,
                        'children': [
                            {
                                'name': 'device=mobile',
                                'value': 120,
                                'percentage': 60.0,
                                'node': 2
                            }
                        ]
                    }
                ],
                'value': 200,
                'percentage': 100.0,
                'node': 0,
                'top': 5
            }

        """
        tree = Tree()
        tree.preprocessors = self._base.preprocessors
        return tree.execute(data, fields, query, **kwargs)

    def discover(
        self,
        data: List[Dict[str, Any]],
        max_fields: int = 3,
        max_combinations: int = 10,
        min_concentration: float = 10.0,
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Automatically discover the most interesting concentration patterns.

        This method analyzes all available fields and automatically finds
        the combinations that show the highest concentration patterns.

        Args:
            data: List of records (dictionaries)
            max_fields: Maximum number of fields to combine (default: 3)
            max_combinations: Maximum combinations to try (default: 10)
            min_concentration: Minimum concentration to consider (default: 10%)
            query: Optional filters to apply to data
            **kwargs: Additional filtering options (same as find method)

        Returns:
            Dictionary with discovered patterns, field analysis, and recommendations

        Example:
            results = dataspot.discover(data)
            print(f"Best pattern: {results['top_patterns'][0].path}")
            print(f"Most valuable fields: {results['field_ranking']}")

        """
        discovery = Discovery()
        discovery.preprocessors = self._base.preprocessors
        return discovery.execute(
            data, max_fields, max_combinations, min_concentration, query, **kwargs
        )
