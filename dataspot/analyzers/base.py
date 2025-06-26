"""Base class for all dataspot analyzers with shared functionality."""

from collections import Counter
from typing import Any, Callable, Dict, List, Optional

from ..exceptions import DataspotError
from .preprocessors import Preprocessor


class Base:
    """Base class containing shared functionality for all dataspot analyzers.

    This class provides common methods for data preprocessing, tree building,
    filtering, and pattern matching used across all analyzer implementations.
    """

    def __init__(self):
        """Initialize base analyzer with preprocessor manager."""
        self.preprocessor_manager = Preprocessor()

    def add_preprocessor(
        self, field_name: str, preprocessor: Callable[[Any], Any]
    ) -> None:
        """Add a custom preprocessor for a specific field.

        Args:
            field_name: Name of the field to preprocess
            preprocessor: Function to apply to field values

        """
        self.preprocessor_manager.add_custom_preprocessor(field_name, preprocessor)

    # Backward compatibility properties

    @property
    def preprocessors(self) -> Dict[str, Callable]:
        """Backward compatibility property for preprocessors."""
        return self.preprocessor_manager.custom_preprocessors

    @preprocessors.setter
    def preprocessors(self, value: Dict[str, Callable]) -> None:
        """Backward compatibility setter for preprocessors."""
        self.preprocessor_manager.custom_preprocessors = value

    def _validate_data(self, data: List[Dict[str, Any]]) -> None:
        """Validate input data format and raise appropriate errors."""
        if not isinstance(data, list):
            raise DataspotError("Data must be a list of dictionaries")

        if data and not isinstance(data[0], dict):
            raise DataspotError("Data must contain dictionary records")

    def _filter_data_by_query(
        self, data: List[Dict[str, Any]], query: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter data based on query constraints.

        Args:
            data: Input data records
            query: Optional filtering criteria

        Returns:
            Filtered data records

        """
        if not query:
            return data

        return [record for record in data if self._matches_query(record, query)]

    def _matches_query(self, record: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if a record matches query constraints.

        Args:
            record: Data record to check
            query: Query constraints

        Returns:
            True if record matches all query constraints

        """
        for field, constraint in query.items():
            record_value = record.get(field)

            if isinstance(constraint, (list, tuple)):
                if str(record_value) not in [str(v) for v in constraint]:
                    return False
            else:
                if str(record_value) != str(constraint):
                    return False

        return True

    def _build_tree(
        self, data: List[Dict[str, Any]], fields: List[str]
    ) -> Dict[str, Any]:
        """Build hierarchical tree from data using optimized algorithm.

        Args:
            data: Input data records
            fields: Fields to analyze hierarchically

        Returns:
            Tree structure with counts and percentages

        """
        total = len(data)
        tree = {"children": {}}

        for record in data:
            self._add_record_to_tree(record, fields, tree, total)

        return tree

    def _add_record_to_tree(
        self,
        record: Dict[str, Any],
        fields: List[str],
        tree: Dict[str, Any],
        total: int,
    ) -> None:
        """Add a single record to the tree structure.

        Args:
            record: Record to add
            fields: Fields to process
            tree: Tree structure to update
            total: Total number of records for percentage calculation

        """
        paths = self._get_record_paths(record, fields)

        for path in paths:
            self._add_path_to_tree(path, tree, total, record)

    def _get_record_paths(
        self, record: Dict[str, Any], fields: List[str]
    ) -> List[List[str]]:
        """Generate all possible paths for a record, handling list values.

        Args:
            record: Record to process
            fields: Fields to extract paths from

        Returns:
            List of path combinations

        """

        def _expand_paths(
            remaining_fields: List[str], current_path: List[str]
        ) -> List[List[str]]:
            if not remaining_fields:
                return [current_path]

            field = remaining_fields[0]
            value = self._preprocess_value(field, record.get(field, ""), record)

            paths = []
            if isinstance(value, list):
                for v in value:
                    new_path = current_path + [f"{field}={v}"]
                    paths.extend(_expand_paths(remaining_fields[1:], new_path))
            else:
                new_path = current_path + [f"{field}={value}"]
                paths.extend(_expand_paths(remaining_fields[1:], new_path))

            return paths

        return _expand_paths(fields, [])

    def _add_path_to_tree(
        self, path: List[str], tree: Dict[str, Any], total: int, record: Dict[str, Any]
    ) -> None:
        """Add a complete path to the tree structure.

        Args:
            path: Path components to add
            tree: Tree structure to update
            total: Total records for percentage calculation
            record: Source record for samples

        """
        current = tree

        for i, key_value in enumerate(path):
            if "children" not in current:
                current["children"] = {}

            if key_value not in current["children"]:
                current["children"][key_value] = {
                    "count": 0,
                    "percentage": 0.0,
                    "depth": i + 1,
                    "children": {},
                    "samples": [],
                }

            current = current["children"][key_value]
            current["count"] += 1
            current["percentage"] = round((current["count"] * 100) / total, 2)

            # Add sample record (limit to 3 for memory efficiency)
            if len(current["samples"]) < 3:
                current["samples"].append(record.copy())

    def _preprocess_value(self, field: str, value: Any, record: Dict[str, Any]) -> Any:
        """Preprocess field values based on type and custom preprocessors.

        Args:
            field: Field name
            value: Field value
            record: Complete record for context

        Returns:
            Preprocessed value

        """
        return self.preprocessor_manager.preprocess_value(field, value, record)

    def _analyze_field_distributions(
        self, data: List[Dict[str, Any]], fields: List[str]
    ) -> Dict[str, Any]:
        """Analyze distribution of values in each field.

        Args:
            data: Input data records
            fields: Fields to analyze

        Returns:
            Field distribution statistics

        """
        field_analysis = {}

        for field in fields:
            values = [record.get(field) for record in data]
            value_counts = Counter(str(v) for v in values if v is not None)

            field_analysis[field] = {
                "total_count": len(values),
                "unique_count": len(value_counts),
                "null_count": values.count(None),
                "top_values": [
                    {
                        "value": val,
                        "count": count,
                        "percentage": round((count / len(data)) * 100, 2),
                    }
                    for val, count in value_counts.most_common(5)
                ],
            }

        return field_analysis
