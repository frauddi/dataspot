"""Models for tree analyzer (tree method) response structures."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


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
