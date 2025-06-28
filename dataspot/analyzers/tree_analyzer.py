"""Tree analyzer for building hierarchical JSON tree structures."""

from typing import Any, Dict, List, Optional

from ..models.tree import TreeNode, TreeOutput, TreeStatistics
from .base import Base
from .filters import PatternFilter, TreeFilter
from .pattern_extractor import PatternExtractor, TreeBuilder


class Tree(Base):
    """Specialized analyzer for building hierarchical tree structures.

    Converts data patterns into clean JSON tree format suitable for
    visualization and hierarchical analysis.
    """

    def execute(
        self,
        data: List[Dict[str, Any]],
        fields: List[str],
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> TreeOutput:
        """Build and return hierarchical tree structure in JSON format.

        Args:
            data: List of records (dictionaries)
            fields: List of field names to analyze hierarchically
            query: Optional filters to apply to data
            **kwargs: Tree building and filtering options

        Returns:
            TreeOutput dataclass representing the hierarchical tree structure

        """
        # Validate input
        self._validate_data(data)

        # Filter data based on query
        filtered_data = self._filter_data_by_query(data, query)

        # Get top parameter and build empty tree if no data
        top = kwargs.get("top", 5)
        if not filtered_data:
            empty_statistics = TreeStatistics(
                total_records=len(data),
                filtered_records=0,
                patterns_found=0,
                fields_analyzed=len(fields),
            )
            return TreeOutput(
                name="root",
                children=[],
                value=0,
                percentage=0.0,
                node=0,
                top=top,
                statistics=empty_statistics,
                fields_analyzed=fields,
            )

        # Build internal tree structure
        internal_tree = self._build_tree(filtered_data, fields)
        total_records = len(filtered_data)

        # Extract patterns from tree
        all_patterns = PatternExtractor.from_tree(internal_tree, total_records)

        # Apply tree-specific filters
        filter_kwargs = TreeFilter.build_filter_kwargs(**kwargs)
        filtered_patterns = PatternFilter(all_patterns).apply_all(**filter_kwargs)

        # Build and return clean JSON tree
        tree_result = TreeBuilder(filtered_patterns, total_records, top).build()

        # Convert tree result to TreeOutput
        children = self._convert_tree_children(tree_result.get("children", []))

        statistics = TreeStatistics(
            total_records=len(data),
            filtered_records=len(filtered_data),
            patterns_found=len(filtered_patterns),
            fields_analyzed=len(fields),
        )

        return TreeOutput(
            name=tree_result.get("name", "root"),
            children=children,
            value=tree_result.get("value", 0),
            percentage=tree_result.get("percentage", 0.0),
            node=tree_result.get("node", 0),
            top=top,
            statistics=statistics,
            fields_analyzed=fields,
        )

    def _convert_tree_children(
        self, children_data: List[Dict[str, Any]]
    ) -> List[TreeNode]:
        """Recursively convert tree children dictionaries to TreeNode dataclasses.

        Args:
            children_data: List of child node dictionaries

        Returns:
            List of TreeNode dataclasses

        """
        tree_nodes = []
        for child in children_data:
            # Recursively convert children
            child_children = None
            if "children" in child and child["children"]:
                child_children = self._convert_tree_children(child["children"])

            node = TreeNode(
                name=child.get("name", ""),
                value=child.get("value", 0),
                percentage=child.get("percentage", 0.0),
                node=child.get("node", 0),
                children=child_children,
            )
            tree_nodes.append(node)

        return tree_nodes

    def _build_empty_tree(self, top: int) -> Dict[str, Any]:
        """Build empty tree structure for cases with no data.

        Args:
            top: Number of top elements per level

        Returns:
            Empty tree structure

        """
        return {
            "name": "root",
            "children": [],
            "value": 0,
            "percentage": 0.0,
            "node": 0,
            "top": top,
        }
