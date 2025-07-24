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
    """Options for hierarchical tree visualization.

    Args:
        top: Top elements per tree level (1-20).
            Limits branches per node. Common: 5 (balanced), 3 (simple), 10 (detailed).
        min_count: Minimum record count per node.
            Excludes small nodes. Common: 1 (show all), 5 (significant only), 10 (major only).
        min_percentage: Minimum percentage per node (0.0-100.0).
            Excludes small percentage nodes. Common: 1.0 (1%), 5.0 (5%).
        max_count: Maximum record count per node.
            Excludes large nodes. Rare usage for outlier removal.
        max_percentage: Maximum percentage per node (0.0-100.0).
            Excludes dominant nodes. Rare usage.
        min_depth: Minimum tree depth (1+).
            Focuses on deeper patterns. Example: 2 for multi-level only.
        max_depth: Maximum tree depth (1+).
            Controls tree complexity. Common: 3-4 to avoid over-nesting.
        contains: Node name must contain this text.
            Filters tree to specific patterns. Example: "error" for error analysis.
        exclude: Node name must NOT contain these texts.
            Removes unwanted nodes. Example: ["test", "demo"].
        regex: Node name must match this regex.
            Advanced filtering. Example: "^(high|medium|low)" for risk levels.

    """

    top: int = 5
    min_count: Optional[int] = None
    min_percentage: Optional[float] = None
    max_count: Optional[int] = None
    max_percentage: Optional[float] = None
    min_depth: Optional[int] = None
    max_depth: Optional[int] = None
    contains: Optional[str] = None
    exclude: Optional[List[str]] = None
    regex: Optional[str] = None

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
