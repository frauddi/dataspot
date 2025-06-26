"""Dataspot - Find data concentration patterns and dataspots."""

__version__ = "0.3.0"
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
from dataspot.models import Pattern

# from .query import QueryBuilder  # Will add when we create it
# from .utils import quick_analysis, find_concentrations, top_patterns  # Will add when we create it


# Quick functions for easy usage
def find(data, fields, **kwargs):
    """Quick function to find concentration patterns."""
    dataspot = Dataspot()
    return dataspot.find(data, fields, **kwargs)


def analyze(data, fields, **kwargs):
    """Quick function to analyze data and get insights."""
    dataspot = Dataspot()
    return dataspot.analyze(data, fields, **kwargs)


def tree(data, fields, **kwargs):
    """Quick function to build a tree of patterns."""
    dataspot = Dataspot()
    return dataspot.tree(data, fields, **kwargs)


def discover(data, **kwargs):
    """Quick function to discover patterns."""
    dataspot = Dataspot()
    return dataspot.discover(data, **kwargs)


# Package metadata
__all__ = [
    # Main classes
    "Dataspot",
    "Pattern",
    # Quick functions
    "find",
    "analyze",
    "tree",
    "discover",
    # Exceptions
    "DataspotError",
    "ValidationError",
    "DataError",
    "QueryError",
    "ConfigurationError",
]
