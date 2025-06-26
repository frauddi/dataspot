"""Pattern finder for discovering data concentration patterns."""

from typing import Any, Dict, List, Optional

from ..models import Pattern
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
    ) -> List[Pattern]:
        """Find concentration patterns in data.

        Args:
            data: List of records (dictionaries)
            fields: List of field names to analyze hierarchically
            query: Optional filters to apply to data
            **kwargs: Additional filtering options

        Returns:
            List of Pattern objects sorted by percentage

        """
        self._validate_data(data)

        if not fields:
            return []

        filtered_data = self._filter_data_by_query(data, query)

        if not filtered_data:
            return []

        tree = self._build_tree(filtered_data, fields)

        patterns = PatternExtractor.from_tree(tree, len(filtered_data))

        return PatternFilter(patterns).apply_all(**kwargs)
