"""Models package for dataspot response structures."""

# This package contains the response models for each analyzer
# to provide type safety and structured responses

# Import all models from each analyzer
from .analyzer import AnalyzeOutput, Insights, Statistics
from .compare import ChangeItem, CompareOutput, ComparisonStatistics
from .discovery import (
    CombinationTried,
    DiscoverOutput,
    DiscoveryStatistics,
    FieldRanking,
)
from .finder import FindOutput
from .pattern import Pattern
from .tree import TreeNode, TreeOutput, TreeStatistics

# Export all classes for easy import
__all__ = [
    # Finder models
    "FindOutput",
    # Analyzer models
    "AnalyzeOutput",
    "Statistics",
    "Insights",
    # Tree models
    "TreeOutput",
    "TreeNode",
    "TreeStatistics",
    # Discovery models
    "DiscoverOutput",
    "FieldRanking",
    "CombinationTried",
    "DiscoveryStatistics",
    # Compare models
    "CompareOutput",
    "ChangeItem",
    "ComparisonStatistics",
    "Pattern",
]
