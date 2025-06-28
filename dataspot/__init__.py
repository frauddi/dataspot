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
from dataspot.models.compare import CompareInput, CompareOptions, CompareOutput
from dataspot.models.discovery import DiscoverInput, DiscoverOptions, DiscoverOutput
from dataspot.models.finder import FindInput, FindOptions, FindOutput
from dataspot.models.pattern import Pattern
from dataspot.models.tree import TreeInput, TreeOptions, TreeOutput

# Package metadata
__all__ = [
    # Main classes
    "Dataspot",
    "Pattern",
    # Analyze models
    "AnalyzeInput",
    "AnalyzeOptions",
    "AnalyzeOutput",
    # Compare models
    "CompareInput",
    "CompareOptions",
    "CompareOutput",
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
    # Exceptions
    "DataspotError",
    "ValidationError",
    "DataError",
    "QueryError",
    "ConfigurationError",
]
