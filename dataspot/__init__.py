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
from dataspot.models.pattern import Pattern
from dataspot.models.tree import TreeInput, TreeOptions, TreeOutput


# Quick functions for easy usage
def find(data, fields, **kwargs):
    """Quick function to find concentration patterns."""
    dataspot = Dataspot()
    return dataspot.find(data, fields, **kwargs)


def analyze(data, fields, **kwargs):
    """Quick function to analyze data and get insights."""
    dataspot = Dataspot()
    return dataspot.analyze(data, fields, **kwargs)


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
    return dataspot.discover(data, **kwargs)


def compare(current_data, baseline_data, fields, **kwargs):
    """Quick function to compare data."""
    dataspot = Dataspot()
    return dataspot.compare(current_data, baseline_data, fields, **kwargs)


# Package metadata
__all__ = [
    # Main classes
    "Dataspot",
    "Pattern",
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
