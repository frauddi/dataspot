"""Pattern extraction from tree structures."""

from typing import Any, Dict, List

from ..models import Pattern


class PatternExtractor:
    """Clean pattern extraction from tree structures."""

    @staticmethod
    def from_tree(tree: Dict[str, Any], total_records: int) -> List[Pattern]:
        """Extract Pattern objects from tree structure.

        Args:
            tree: Hierarchical tree structure
            total_records: Total number of records for percentage calculation

        Returns:
            List of Pattern objects

        """
        patterns = []

        def _traverse_tree(node: Dict[str, Any], path: str = "") -> None:
            """Recursively traverse tree and extract patterns."""
            for key, child in node.get("children", {}).items():
                current_path = f"{path} > {key}" if path else key

                if child.get("count", 0) > 0:
                    pattern = Pattern(
                        path=current_path,
                        count=child["count"],
                        percentage=child["percentage"],
                        depth=child["depth"],
                        samples=child.get("samples", [])[:3],  # Keep first 3 samples
                    )
                    patterns.append(pattern)

                # Continue traversing children
                _traverse_tree(child, current_path)

        _traverse_tree(tree)
        return patterns


class TreeBuilder:
    """Build clean tree structures for JSON output."""

    def __init__(self, patterns: List[Pattern], total_records: int, top: int):
        """Initialize tree builder.

        Args:
            patterns: Filtered patterns to build tree from
            total_records: Total number of records
            top: Number of top elements per level

        """
        self.patterns = patterns
        self.total_records = total_records
        self.top = top

    def build(self) -> Dict[str, Any]:
        """Build clean tree structure from patterns.

        Returns:
            JSON-ready tree structure

        """
        if not self.patterns:
            return self._build_empty_tree()

        tree_data = self._group_patterns_by_hierarchy()
        root_children = self._convert_to_json_format(tree_data)

        return {
            "name": "root",
            "children": root_children,
            "value": self.total_records,
            "percentage": 100.0,
            "node": 0,
            "top": self.top,
        }

    def _build_empty_tree(self) -> Dict[str, Any]:
        """Build empty tree structure."""
        return {
            "name": "root",
            "children": [],
            "value": self.total_records,
            "percentage": 100.0,
            "node": 0,
            "top": self.top,
        }

    def _group_patterns_by_hierarchy(self) -> Dict[str, Any]:
        """Group patterns into hierarchical structure."""
        tree_data = {}

        for pattern in self.patterns:
            path_parts = pattern.path.split(" > ")
            current = tree_data

            for i, part in enumerate(path_parts):
                if part not in current:
                    current[part] = {
                        "count": 0,
                        "percentage": 0.0,
                        "depth": i + 1,
                        "children": {},
                        "samples": [],
                    }

                # Update for exact pattern match (last part of path)
                if i == len(path_parts) - 1:
                    current[part]["count"] = pattern.count
                    current[part]["percentage"] = pattern.percentage
                    current[part]["samples"] = pattern.samples

                current = current[part]["children"]

        return tree_data

    def _convert_to_json_format(
        self, data: Dict[str, Any], level: int = 1
    ) -> List[Dict[str, Any]]:
        """Convert tree data to clean JSON format.

        Args:
            data: Tree data structure
            level: Current tree level

        Returns:
            List of JSON tree nodes

        """
        children = []

        # Sort by count and take top N
        sorted_items = sorted(
            data.items(), key=lambda x: x[1].get("count", 0), reverse=True
        )[: self.top]

        for name, node_data in sorted_items:
            node = {
                "name": name,
                "value": node_data["count"],
                "percentage": node_data["percentage"],
                "node": level,
            }

            # Add children if they exist
            if node_data["children"]:
                child_nodes = self._convert_to_json_format(
                    node_data["children"], level + 1
                )
                if child_nodes:
                    node["children"] = child_nodes

            children.append(node)

        return children
