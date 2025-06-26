"""Pattern discovery for automatic field analysis and pattern finding."""

from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

from ..models import Pattern
from .base import Base
from .finder import Finder


class Discovery(Base):
    """Intelligent pattern discovery that automatically finds the best field combinations.

    Analyzes all available fields and discovers the most interesting
    concentration patterns without manual field specification.
    """

    def execute(
        self,
        data: List[Dict[str, Any]],
        max_fields: int = 3,
        max_combinations: int = 10,
        min_concentration: float = 10.0,
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Automatically discover the most interesting concentration patterns.

        Args:
            data: List of records (dictionaries)
            max_fields: Maximum number of fields to combine (default: 3)
            max_combinations: Maximum combinations to try (default: 10)
            min_concentration: Minimum concentration to consider (default: 10%)
            query: Optional filters to apply to data
            **kwargs: Additional filtering options

        Returns:
            Dictionary with discovered patterns, field analysis, and recommendations

        """
        self._validate_data(data)

        if query:
            data = self._filter_data_by_query(data, query)

        if not data:
            return self._build_empty_discovery_result()

        available_fields = self._detect_categorical_fields(data)
        field_scores = self._score_fields_by_potential(data, available_fields, **kwargs)

        all_patterns, combinations_tried = self._discover_pattern_combinations(
            data,
            field_scores,
            max_fields,
            max_combinations,
            min_concentration,
            **kwargs,
        )

        top_patterns = self._rank_and_deduplicate_patterns(all_patterns)

        return {
            "top_patterns": top_patterns[:20],  # Top 20 patterns
            "field_ranking": field_scores,
            "combinations_tried": combinations_tried,
            "statistics": self._calculate_discovery_statistics(
                data, available_fields, combinations_tried, top_patterns
            ),
            "recommendations": self._generate_actionable_recommendations(
                top_patterns, field_scores
            ),
        }

    def _build_empty_discovery_result(self) -> Dict[str, Any]:
        """Build empty discovery result for cases with no data."""
        return {
            "top_patterns": [],
            "field_ranking": [],
            "combinations_tried": [],
            "statistics": {"total_records": 0, "fields_analyzed": 0},
            "recommendations": {"message": "No data provided", "suggestions": []},
        }

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
        """Check if a field is suitable for categorical analysis.

        Args:
            data: Input data
            field: Field name to check
            sample_size: Number of records to sample

        Returns:
            True if field is suitable for analysis

        """
        values = []
        for record in data[:sample_size]:
            value = record.get(field)
            if value is not None:
                values.append(str(value))

        if not values:
            return False

        unique_values = set(values)
        unique_ratio = len(unique_values) / len(values)

        # Criteria for categorical fields useful for concentration analysis

        # Fields with only one unique value are not useful for concentration analysis
        # (they always show 100% concentration)
        if len(unique_values) <= 1:
            return False

        # For very small samples, be more lenient but still require variation
        if len(values) <= 5:
            return len(unique_values) >= 2  # At least some variation

        return (
            len(unique_values) >= 2  # At least 2 different values
            and len(unique_values) <= len(values) * 0.8  # Not too many unique values
            and unique_ratio < 0.95  # Not mostly unique (like IDs)
        )

    def _score_fields_by_potential(
        self, data: List[Dict[str, Any]], fields: List[str], **kwargs
    ) -> List[Tuple[str, float]]:
        """Score fields by their concentration potential.

        Args:
            data: Input data records
            fields: Fields to score
            **kwargs: Additional options

        Returns:
            List of (field_name, score) tuples sorted by score

        """
        field_scores = []
        pattern_finder = Finder()

        for field in fields:
            try:
                patterns = pattern_finder.execute(
                    data, [field], min_percentage=5.0, **kwargs
                )
                score = self._calculate_field_score(patterns)
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
        max_fields: int,
        max_combinations: int,
        min_concentration: float,
        **kwargs,
    ) -> Tuple[List[Pattern], List[Dict[str, Any]]]:
        """Discover patterns using different field combinations.

        Args:
            data: Input data
            field_scores: Scored fields
            max_fields: Maximum fields to combine
            max_combinations: Maximum combinations to try
            min_concentration: Minimum concentration threshold
            **kwargs: Additional options

        Returns:
            Tuple of (all_patterns, combinations_tried)

        """
        all_patterns = []
        combinations_tried = []
        finder = Finder()

        # Get top fields for combinations
        top_fields = [
            field
            for field, score in field_scores[: min(max_fields + 2, len(field_scores))]
        ]

        # Try single fields first
        for field in top_fields[:max_fields]:
            patterns = finder.execute(
                data, [field], min_percentage=min_concentration, **kwargs
            )
            if patterns:
                all_patterns.extend(patterns)
                combinations_tried.append(
                    {"fields": [field], "patterns_found": len(patterns)}
                )

        # Try field combinations (2-field, 3-field, etc.)
        for combo_size in range(2, min(max_fields + 1, len(top_fields) + 1)):
            field_combinations = list(combinations(top_fields, combo_size))

            for fields_combo in field_combinations[:max_combinations]:
                patterns = finder.execute(
                    data, list(fields_combo), min_percentage=min_concentration, **kwargs
                )
                if patterns:
                    all_patterns.extend(patterns)
                    combinations_tried.append(
                        {"fields": list(fields_combo), "patterns_found": len(patterns)}
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

    def _generate_actionable_recommendations(
        self, patterns: List[Pattern], field_scores: List[Tuple[str, float]]
    ) -> Dict[str, Any]:
        """Generate actionable recommendations based on discovery results.

        Args:
            patterns: Discovered patterns
            field_scores: Field scoring results

        Returns:
            Recommendations dictionary

        """
        if not patterns:
            return {"message": "No significant patterns found", "suggestions": []}

        top_pattern = patterns[0]
        recommendations = []

        # Pattern-based recommendations
        if top_pattern.percentage > 50:
            recommendations.append(
                {
                    "type": "high_concentration",
                    "message": f"Very high concentration found: {top_pattern.path} ({top_pattern.percentage}%)",
                    "action": "Investigate this pattern - could indicate data quality issues or important business insight",
                }
            )
        elif top_pattern.percentage > 30:
            recommendations.append(
                {
                    "type": "significant_concentration",
                    "message": f"Significant concentration: {top_pattern.path} ({top_pattern.percentage}%)",
                    "action": "This pattern represents a key segment in your data",
                }
            )

        # Field-based recommendations
        if field_scores:
            best_field = field_scores[0][0]
            recommendations.append(
                {
                    "type": "best_field",
                    "message": f"Most valuable field for analysis: '{best_field}'",
                    "action": f"Focus deeper analysis on '{best_field}' and its combinations",
                }
            )

        return {
            "summary": f"Found {len(patterns)} patterns, best concentration: {top_pattern.percentage}%",
            "recommendations": recommendations,
        }
