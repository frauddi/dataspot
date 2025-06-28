"""Pattern finder for discovering data concentration patterns."""

from typing import Any, Dict, List, Optional

from ..models.finder import FindOutput
from .base import Base
from .filters import PatternFilter
from .pattern_extractor import PatternExtractor


class Finder(Base):
    """Specialized analyzer for finding concentration patterns in data.

    Inherits common functionality from BaseDataspot and implements
    the core pattern finding algorithm.
    """

    def execute(
        self,
        data: List[Dict[str, Any]],
        fields: List[str],
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> FindOutput:
        """Find concentration patterns in data.

        Args:
            data: List of records (dictionaries)
            fields: List of field names to analyze hierarchically
            query: Optional filters to apply to data
            **kwargs: Additional filtering options

        Returns:
            FindOutput dataclass with patterns and metadata

        """
        self._validate_data(data)

        if not fields:
            return FindOutput(
                patterns=[],
                total_records=len(data),
                total_patterns=0,
            )

        filtered_data = self._filter_data_by_query(data, query)

        if not filtered_data:
            return FindOutput(
                patterns=[],
                total_records=len(data),
                total_patterns=0,
            )

        tree = self._build_tree(filtered_data, fields)

        patterns = PatternExtractor.from_tree(tree, len(filtered_data))
        filtered_patterns = PatternFilter(patterns).apply_all(**kwargs)

        return FindOutput(
            patterns=filtered_patterns,
            total_records=len(filtered_data),
            total_patterns=len(filtered_patterns),
        )
