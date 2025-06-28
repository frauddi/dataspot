"""Pattern finder for discovering data concentration patterns."""

from typing import List

from ..models.finder import FindInput, FindOptions, FindOutput
from ..models.pattern import Pattern
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
        input: FindInput,
        options: FindOptions,
    ) -> FindOutput:
        """Find concentration patterns in data.

        Args:
            input: FindInput containing data, fields, and optional query
            options: FindOptions containing filtering and display options

        Returns:
            FindOutput dataclass with patterns and metadata

        """
        self._validate_data(input.data)

        if not input.fields:
            return FindOutput(
                patterns=[],
                total_records=len(input.data),
                total_patterns=0,
            )

        filtered_data = self._filter_data_by_query(input.data, input.query)

        if not filtered_data:
            return FindOutput(
                patterns=[],
                total_records=len(input.data),
                total_patterns=0,
            )

        tree = self._build_tree(filtered_data, input.fields)

        patterns = PatternExtractor.from_tree(tree, len(filtered_data))
        filtered_patterns = PatternFilter(patterns).apply_all(
            **options.to_filter_kwargs()
        )

        # Apply sorting if specified
        if options.sort_by:
            reverse = (
                options.reverse if options.reverse is not None else True
            )  # Default to descending
            self._sort_patterns(filtered_patterns, options.sort_by, reverse)

        return FindOutput(
            patterns=filtered_patterns,
            total_records=len(filtered_data),
            total_patterns=len(filtered_patterns),
        )

    def _sort_patterns(
        self, patterns: List[Pattern], sort_by: str, reverse: bool = True
    ) -> None:
        """Sort patterns in-place by the specified field.

        Args:
            patterns: List of patterns to sort
            sort_by: Field to sort by ('percentage', 'count', 'depth')
            reverse: Sort in descending order (True) or ascending (False)

        """
        if sort_by == "percentage":
            patterns.sort(key=lambda p: p.percentage, reverse=reverse)
        elif sort_by == "count":
            patterns.sort(key=lambda p: p.count, reverse=reverse)
        elif sort_by == "depth":
            patterns.sort(key=lambda p: p.depth, reverse=reverse)
