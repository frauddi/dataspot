"""Data analyzer for comprehensive dataset insights."""

from typing import Any, Dict, List, Optional

from ..models.analyzer import (
    AnalyzeInput,
    AnalyzeOptions,
    AnalyzeOutput,
    Insights,
    Statistics,
)
from ..models.finder import FindInput, FindOptions
from .base import Base
from .finder import Finder


class Analyzer(Base):
    """Specialized analyzer for comprehensive data analysis and insights.

    Provides detailed statistics, field analysis, and pattern insights
    beyond basic pattern finding.
    """

    def execute(
        self,
        input: AnalyzeInput,
        options: AnalyzeOptions,
    ) -> AnalyzeOutput:
        """Analyze data and return comprehensive insights.

        Args:
            input: AnalyzeInput containing data, fields, and optional query
            options: AnalyzeOptions containing filtering and display options

        Returns:
            AnalyzeOutput dataclass with patterns, statistics, and insights

        """
        # Validate input
        self._validate_data(input.data)

        # Get patterns using Finder
        find_input = FindInput(data=input.data, fields=input.fields, query=input.query)
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
        patterns = Finder().execute(find_input, find_options)

        # Calculate comprehensive statistics
        base_statistics = self._calculate_statistics(input.data, input.query)

        # Analyze field distributions
        field_stats = self._analyze_field_distributions(input.data, input.fields)

        # Generate insights
        insights_data = self._generate_insights(patterns.patterns)

        # Create Statistics dataclass
        statistics = Statistics(
            total_records=base_statistics["total_records"],
            filtered_records=base_statistics["filtered_records"],
            filter_ratio=base_statistics["filter_ratio"],
            patterns_found=len(patterns.patterns),
            max_concentration=max([p.percentage for p in patterns.patterns])
            if patterns.patterns
            else 0,
            avg_concentration=(
                sum([p.percentage for p in patterns.patterns]) / len(patterns.patterns)
                if patterns.patterns
                else 0
            ),
        )

        # Create Insights dataclass
        insights = Insights(
            patterns_found=insights_data["patterns_found"],
            max_concentration=insights_data["max_concentration"],
            avg_concentration=insights_data["avg_concentration"],
            concentration_distribution=insights_data["concentration_distribution"],
        )

        return AnalyzeOutput(
            patterns=patterns.patterns,
            statistics=statistics,
            insights=insights,
            field_stats=field_stats,
            top_patterns=patterns.patterns[:5] if patterns.patterns else [],
            fields_analyzed=input.fields,
        )

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
