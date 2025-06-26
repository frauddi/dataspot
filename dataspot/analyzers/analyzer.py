"""Data analyzer for comprehensive dataset insights."""

from typing import Any, Dict, List, Optional

from .base import Base
from .finder import Finder


class Analyzer(Base):
    """Specialized analyzer for comprehensive data analysis and insights.

    Provides detailed statistics, field analysis, and pattern insights
    beyond basic pattern finding.
    """

    def execute(
        self,
        data: List[Dict[str, Any]],
        fields: List[str],
        query: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Analyze data and return comprehensive insights.

        Args:
            data: List of records (dictionaries)
            fields: List of field names to analyze hierarchically
            query: Optional filters to apply to data
            **kwargs: Additional filtering options

        Returns:
            Dictionary with patterns, statistics, and insights

        """
        # Validate input
        self._validate_data(data)

        # Get patterns using PatternFinder
        patterns = Finder().execute(data, fields, query, **kwargs)

        # Calculate comprehensive statistics
        statistics = self._calculate_statistics(data, query)

        # Analyze field distributions
        field_stats = self._analyze_field_distributions(data, fields)

        # Generate insights
        insights = self._generate_insights(patterns)

        return {
            "patterns": patterns,
            "insights": insights,
            "statistics": {
                **statistics,
                "patterns_found": len(patterns),
                "max_concentration": max([p.percentage for p in patterns])
                if patterns
                else 0,
                "avg_concentration": (
                    sum([p.percentage for p in patterns]) / len(patterns)
                    if patterns
                    else 0
                ),
            },
            "field_stats": field_stats,
            "top_patterns": patterns[:5] if patterns else [],
        }

    def _calculate_statistics(
        self, data: List[Dict[str, Any]], query: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive dataset statistics.

        Args:
            data: Input data records
            query: Optional query filters

        Returns:
            Statistics dictionary

        """
        total_records = len(data)

        if query:
            filtered_data = self._filter_data_by_query(data, query)
            filtered_records = len(filtered_data)
        else:
            filtered_records = total_records

        return {
            "total_records": total_records,
            "filtered_records": filtered_records,
            "filter_ratio": round(filtered_records / total_records * 100, 2)
            if total_records > 0
            else 0,
        }

    def _generate_insights(self, patterns: List) -> Dict[str, Any]:
        """Generate actionable insights from patterns.

        Args:
            patterns: List of discovered patterns

        Returns:
            Insights dictionary

        """
        if not patterns:
            return {
                "patterns_found": 0,
                "max_concentration": 0,
                "avg_concentration": 0,
                "concentration_distribution": "No patterns found",
            }

        concentrations = [p.percentage for p in patterns]

        return {
            "patterns_found": len(patterns),
            "max_concentration": max(concentrations),
            "avg_concentration": round(sum(concentrations) / len(concentrations), 2),
            "concentration_distribution": self._analyze_concentration_distribution(
                concentrations
            ),
        }

    def _analyze_concentration_distribution(self, concentrations: List[float]) -> str:
        """Analyze the distribution of concentration values.

        Args:
            concentrations: List of concentration percentages

        Returns:
            Description of concentration distribution

        """
        if not concentrations:
            return "No patterns found"

        high_concentration = len([c for c in concentrations if c >= 50])
        medium_concentration = len([c for c in concentrations if 20 <= c < 50])
        # low_concentration = len([c for c in concentrations if c < 20])

        total = len(concentrations)

        if high_concentration / total > 0.3:
            return "High concentration patterns dominant"
        elif medium_concentration / total > 0.5:
            return "Moderate concentration patterns"
        else:
            return "Low concentration patterns prevalent"
