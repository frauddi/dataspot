"""Pattern discovery for automatic field analysis and pattern finding."""

from itertools import combinations
from typing import Any, Dict, List, Tuple

from ..models.discovery import (
    CombinationTried,
    DiscoverInput,
    DiscoverOptions,
    DiscoverOutput,
    DiscoveryStatistics,
    FieldRanking,
)
from ..models.finder import FindInput, FindOptions
from ..models.pattern import Pattern
from .base import Base
from .finder import Finder


class Discovery(Base):
    """Intelligent pattern discovery that automatically finds the best field combinations.

    Analyzes all available fields and discovers the most interesting
    concentration patterns without manual field specification.
    """

    def execute(
        self,
        input: DiscoverInput,
        options: DiscoverOptions,
    ) -> DiscoverOutput:
        """Automatically discover the most interesting concentration patterns.

        Args:
            input: DiscoverInput containing data and optional query
            options: DiscoverOptions containing discovery and filtering parameters

        Returns:
            DiscoverOutput dataclass with discovered patterns and field analysis.

        """
        self._validate_data(input.data)

        data = input.data
        if input.query:
            data = self._filter_data_by_query(data, input.query)

        if not data:
            return self._build_empty_discovery_result()

        available_fields = self._detect_categorical_fields(data)
        field_scores = self._score_fields_by_potential(data, available_fields, options)

        all_patterns, combinations_tried_data = self._discover_pattern_combinations(
            data,
            field_scores,
            options,
        )

        top_patterns = self._rank_and_deduplicate_patterns(all_patterns)

        # Convert field_scores tuples to FieldRanking dataclasses
        field_ranking = [
            FieldRanking(field=field, score=score) for field, score in field_scores
        ]

        # Convert combinations_tried dictionaries to CombinationTried dataclasses
        combinations_tried = [
            CombinationTried(
                fields=combo["fields"], patterns_found=combo["patterns_found"]
            )
            for combo in combinations_tried_data
        ]

        # Create DiscoveryStatistics dataclass
        statistics = DiscoveryStatistics(
            total_records=len(data),
            fields_analyzed=len(available_fields),
            combinations_tried=len(combinations_tried),
            patterns_discovered=len(top_patterns[:20]),
            best_concentration=max([p.percentage for p in top_patterns[:20]])
            if top_patterns
            else 0,
        )

        return DiscoverOutput(
            top_patterns=top_patterns[:20],  # Top 20 patterns
            field_ranking=field_ranking,
            combinations_tried=combinations_tried,
            statistics=statistics,
            fields_analyzed=available_fields,
        )

    def _build_empty_discovery_result(self) -> DiscoverOutput:
        """Build empty discovery result for cases with no data."""
        statistics = DiscoveryStatistics(
            total_records=0,
            fields_analyzed=0,
            combinations_tried=0,
            patterns_discovered=0,
            best_concentration=0,
        )

        return DiscoverOutput(
            top_patterns=[],
            field_ranking=[],
            combinations_tried=[],
            statistics=statistics,
            fields_analyzed=[],
        )

    def _detect_categorical_fields(self, data: List[Dict[str, Any]]) -> List[str]:
        """Detect fields suitable for categorical analysis.

        Args:
            data: Input data records

        Returns:
            List of categorical field names

        """
        # Sample first 100 records to detect fields efficiently and their structure.
        sample_size = min(100, len(data))
        all_fields = set()

        for record in data[:sample_size]:
            all_fields.update(record.keys())

        # Filter for categorical suitability
        categorical_fields = []
        for field in all_fields:
            if self._is_suitable_for_analysis(data, field, sample_size):
                categorical_fields.append(field)

        return categorical_fields

    def _is_suitable_for_analysis(
        self, data: List[Dict[str, Any]], field: str, sample_size: int
    ) -> bool:
        """Check if a field is suitable for pattern analysis.

        Args:
            data: Input data records
            field: Field name to check
            sample_size: Number of records to sample

        Returns:
            True if field is suitable for analysis

        """
        values = [record.get(field) for record in data[:sample_size]]
        non_null_values = [v for v in values if v is not None]

        if len(non_null_values) < 2:
            return False

        # Check cardinality - too many unique values might not be useful
        unique_values = len({str(v) for v in non_null_values})
        total_values = len(non_null_values)
        unique_ratio = unique_values / total_values

        # Skip if only one unique value
        if unique_values <= 1:
            return False

        # For very small samples, be more lenient but still require variation
        if total_values <= 5:
            return unique_values >= 2  # At least some variation

        return (
            unique_values >= 2  # At least 2 different values
            and unique_values <= total_values * 0.8  # Not too many unique values
            and unique_ratio < 0.95  # Not mostly unique (like IDs)
        )

    def _score_fields_by_potential(
        self, data: List[Dict[str, Any]], fields: List[str], options: DiscoverOptions
    ) -> List[Tuple[str, float]]:
        """Score fields by their concentration potential.

        Args:
            data: Input data records
            fields: Fields to score
            options: Discovery options containing filtering parameters

        Returns:
            List of (field_name, score) tuples sorted by score

        """
        field_scores = []
        pattern_finder = Finder()

        for field in fields:
            try:
                find_input = FindInput(data=data, fields=[field])
                find_options = FindOptions(
                    min_percentage=5.0,
                    max_percentage=options.max_percentage,
                    min_count=options.min_count,
                    max_count=options.max_count,
                    min_depth=options.min_depth,
                    max_depth=options.max_depth,
                    contains=options.contains,
                    exclude=options.exclude,
                    regex=options.regex,
                    limit=options.limit,
                    sort_by=options.sort_by,
                    reverse=options.reverse,
                )
                patterns = pattern_finder.execute(find_input, find_options)
                score = self._calculate_field_score(patterns.patterns)
                field_scores.append((field, score))
            except Exception:
                # Skip problematic fields
                field_scores.append((field, 0))

        return sorted(field_scores, key=lambda x: x[1], reverse=True)

    def _calculate_field_score(self, patterns: List[Pattern]) -> float:
        """Calculate scoring for a field based on its patterns.

        Args:
            patterns: Patterns found for the field

        Returns:
            Numerical score for the field

        """
        if not patterns:
            return 0

        max_concentration = max(p.percentage for p in patterns)
        significant_patterns = len([p for p in patterns if p.percentage >= 10])

        # Weighted scoring formula
        return (
            max_concentration * 0.5  # Highest concentration (50%)
            + significant_patterns * 5  # Number of significant patterns
            + len(patterns) * 0.5  # Total patterns (diversity bonus)
        )

    def _discover_pattern_combinations(
        self,
        data: List[Dict[str, Any]],
        field_scores: List[Tuple[str, float]],
        options: DiscoverOptions,
    ) -> Tuple[List[Pattern], List[Dict[str, Any]]]:
        """Discover patterns using different field combinations.

        Args:
            data: Input data
            field_scores: Scored fields
            options: Discovery options containing max_fields, max_combinations, and other parameters

        Returns:
            Tuple of (all_patterns, combinations_tried)

        """
        all_patterns = []
        combinations_tried = []
        finder = Finder()

        # Get top fields for combinations
        top_fields = [
            field
            for field, score in field_scores[
                : min(options.max_fields + 2, len(field_scores))
            ]
        ]

        # Try single fields first
        for field in top_fields[: options.max_fields]:
            find_input = FindInput(data=data, fields=[field])
            find_options = FindOptions(
                min_percentage=options.min_percentage,
                max_percentage=options.max_percentage,
                min_count=options.min_count,
                max_count=options.max_count,
                min_depth=options.min_depth,
                max_depth=options.max_depth,
                contains=options.contains,
                exclude=options.exclude,
                regex=options.regex,
                limit=options.limit,
                sort_by=options.sort_by,
                reverse=options.reverse,
            )
            patterns = finder.execute(find_input, find_options)
            if patterns:
                all_patterns.extend(patterns.patterns)
                combinations_tried.append(
                    {"fields": [field], "patterns_found": len(patterns.patterns)}
                )

        # Try field combinations (2-field, 3-field, etc.)
        for combo_size in range(2, min(options.max_fields + 1, len(top_fields) + 1)):
            field_combinations = list(combinations(top_fields, combo_size))

            for fields_combo in field_combinations[: options.max_combinations]:
                find_input = FindInput(data=data, fields=list(fields_combo))
                find_options = FindOptions(
                    min_percentage=options.min_percentage,
                    max_percentage=options.max_percentage,
                    min_count=options.min_count,
                    max_count=options.max_count,
                    min_depth=options.min_depth,
                    max_depth=options.max_depth,
                    contains=options.contains,
                    exclude=options.exclude,
                    regex=options.regex,
                    limit=options.limit,
                    sort_by=options.sort_by,
                    reverse=options.reverse,
                )
                patterns = finder.execute(find_input, find_options)
                if patterns:
                    all_patterns.extend(patterns.patterns)
                    combinations_tried.append(
                        {
                            "fields": list(fields_combo),
                            "patterns_found": len(patterns.patterns),
                        }
                    )

        return all_patterns, combinations_tried

    def _rank_and_deduplicate_patterns(self, patterns: List[Pattern]) -> List[Pattern]:
        """Remove duplicates and rank patterns by quality.

        Args:
            patterns: Raw patterns from all combinations

        Returns:
            Deduplicated and ranked patterns

        """
        # Deduplicate by path
        seen_paths = {}
        for pattern in patterns:
            if pattern.path not in seen_paths:
                seen_paths[pattern.path] = pattern
            elif pattern.percentage > seen_paths[pattern.path].percentage:
                seen_paths[pattern.path] = pattern

        # Sort by percentage
        return sorted(seen_paths.values(), key=lambda p: p.percentage, reverse=True)

    def _calculate_discovery_statistics(
        self,
        data: List[Dict[str, Any]],
        available_fields: List[str],
        combinations_tried: List[Dict[str, Any]],
        top_patterns: List[Pattern],
    ) -> Dict[str, Any]:
        """Calculate comprehensive discovery statistics.

        Args:
            data: Input data
            available_fields: Fields that were available for analysis
            combinations_tried: Combinations that were tested
            top_patterns: Final top patterns

        Returns:
            Statistics dictionary

        """
        return {
            "total_records": len(data),
            "fields_analyzed": len(available_fields),
            "combinations_tried": len(combinations_tried),
            "patterns_discovered": len(top_patterns),
            "best_concentration": max([p.percentage for p in top_patterns])
            if top_patterns
            else 0,
        }
