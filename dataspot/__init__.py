"""Dataspot - Find data concentration patterns and dataspots."""

__version__ = "0.3.1"
__author__ = "Elio Rincón"
__email__ = "elio@frauddi.com"
__maintainer__ = "Frauddi Team"
__license__ = "MIT"
__url__ = "https://github.com/frauddi/dataspot"

# Public API exports
from dataspot.core import Dataspot
from dataspot.exceptions import (
    ConfigurationError,
    DataError,
    DataspotError,
    QueryError,
    ValidationError,
)
from dataspot.models.analyzer import AnalyzeInput, AnalyzeOptions, AnalyzeOutput
from dataspot.models.discovery import DiscoverInput, DiscoverOptions, DiscoverOutput
from dataspot.models.finder import FindInput, FindOptions, FindOutput
from dataspot.models.pattern import Pattern
from dataspot.models.tree import TreeInput, TreeOptions, TreeOutput


# Quick functions for easy usage
def find(data, fields, query=None, **kwargs):
    """Quick function to find concentration patterns.

    Args:
        data: List of records (dictionaries) to analyze
        fields: List of field names to analyze hierarchically
        query: Optional filters to apply to data
        **kwargs: Additional filtering options (min_percentage, min_count, etc.)

    Returns:
        FindOutput: Find results dataclass

    """
    dataspot = Dataspot()
    find_input = FindInput(data=data, fields=fields, query=query)
    find_options = FindOptions(**kwargs)
    return dataspot.find(find_input, find_options)


def analyze(data, fields, **kwargs):
    """Quick function to analyze data and get insights."""
    dataspot = Dataspot()
    analyze_input = AnalyzeInput(
        data=data, fields=fields, query=kwargs.pop("query", None)
    )
    analyze_options = AnalyzeOptions(**kwargs)
    return dataspot.analyze(analyze_input, analyze_options)


def tree(data, fields, query=None, **kwargs):
    """Quick function to build a tree of patterns.

    Args:
        data: List of records (dictionaries) to analyze
        fields: List of field names to analyze hierarchically
        query: Optional filters to apply to data
        **kwargs: Additional tree options (top, min_value, etc.)

    Returns:
        TreeOutput: Tree structure dataclass

    """
    dataspot = Dataspot()
    tree_input = TreeInput(data=data, fields=fields, query=query)
    tree_options = TreeOptions(**kwargs)
    return dataspot.tree(tree_input, tree_options)


def discover(data, **kwargs):
    """Quick function to discover patterns."""
    dataspot = Dataspot()
    discover_input = DiscoverInput(data=data, query=kwargs.pop("query", None))
    discover_options = DiscoverOptions(**kwargs)
    return dataspot.discover(discover_input, discover_options)


def compare(current_data, baseline_data, fields, **kwargs):
    """Quick function to compare data."""
    dataspot = Dataspot()
    return dataspot.compare(current_data, baseline_data, fields, **kwargs)


# Package metadata
__all__ = [
    # Main classes
    "Dataspot",
    "Pattern",
    # Analyze models
    "AnalyzeInput",
    "AnalyzeOptions",
    "AnalyzeOutput",
    # Discover models
    "DiscoverInput",
    "DiscoverOptions",
    "DiscoverOutput",
    # Find models
    "FindInput",
    "FindOptions",
    "FindOutput",
    # Tree models
    "TreeInput",
    "TreeOptions",
    "TreeOutput",
    # Quick functions
    "find",
    "analyze",
    "tree",
    "discover",
    "compare",
    # Exceptions
    "DataspotError",
    "ValidationError",
    "DataError",
    "QueryError",
    "ConfigurationError",
]
