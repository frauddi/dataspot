"""Models for tree analyzer (tree method) response structures."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class TreeInput:
    """Input model for the tree() method."""

    data: List[Dict[str, Any]]  # List of records (dictionaries) to analyze
    fields: List[str]  # List of field names to analyze hierarchically
    query: Optional[Dict[str, Any]] = None  # Optional filters to apply to data

    def to_dict(self) -> Dict[str, Any]:
        """Convert tree input to dictionary."""
        return asdict(self)


@dataclass
class TreeOptions:
    """Options model for the tree() method."""

    top: int = 5  # Number of top elements to consider per level
    min_value: Optional[int] = None  # Minimum count for a node to be included
    min_percentage: Optional[float] = (
        None  # Minimum percentage for a node to be included
    )
    max_value: Optional[int] = None  # Maximum count for a node to be included
    max_percentage: Optional[float] = (
        None  # Maximum percentage for a node to be included
    )
    min_depth: Optional[int] = None  # Minimum depth for nodes to be included
    max_depth: Optional[int] = None  # Maximum depth to analyze (limits tree depth)
    contains: Optional[str] = None  # Node name must contain this text
    exclude: Optional[List[str]] = None  # Node name must NOT contain these texts
    regex: Optional[str] = None  # Node name must match this regex pattern

    def to_dict(self) -> Dict[str, Any]:
        """Convert tree options to dictionary."""
        return asdict(self)

    def to_kwargs(self) -> Dict[str, Any]:
        """Convert to kwargs format, excluding None values."""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                result[key] = value
        return result


@dataclass
class TreeNode:
    """A single node in the hierarchical tree structure."""

    name: str  # Node label (e.g., 'country=US')
    value: int  # Record count for this node
    percentage: float  # Percentage relative to parent node
    node: int  # Unique node identifier
    children: Optional[List["TreeNode"]] = None  # Child nodes if any

    def to_dict(self) -> Dict[str, Any]:
        """Convert tree node to dictionary."""
        return asdict(self)


@dataclass
class TreeStatistics:
    """Statistics for tree analysis."""

    total_records: int  # Total records in original dataset
    filtered_records: int  # Records after filtering
    patterns_found: int  # Number of patterns used to build tree
    fields_analyzed: int  # Number of fields analyzed

    def to_dict(self) -> Dict[str, Any]:
        """Convert tree statistics to dictionary."""
        return asdict(self)


@dataclass
class TreeOutput:
    """Response model for the tree() method.

    Based on current tree_analyzer.py implementation that returns:
    {
        'name': 'root',
        'children': [...],
        'value': 200,
        'percentage': 100.0,
        'node': 0,
        'top': 5,
        'statistics': {...},
        'fields_analyzed': [...]
    }
    """

    name: str  # Root node name (typically "root")
    children: List[TreeNode]  # Child nodes with hierarchical structure
    value: int  # Total number of records
    percentage: float  # Percentage of total records (typically 100.0)
    node: int  # Root node identifier (typically 0)
    top: int  # Number of top elements considered per level
    statistics: TreeStatistics  # Analysis statistics
    fields_analyzed: List[str]  # Fields that were analyzed

    def to_dict(self) -> Dict[str, Any]:
        """Convert tree response to dictionary."""
        return asdict(self)
