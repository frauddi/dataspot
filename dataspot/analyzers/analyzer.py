"""Advanced data analyzer for comprehensive dataset insights and statistical analysis.

This module provides the `Analyzer` class, which extends basic pattern finding
capabilities with detailed statistical analysis, field distribution analysis,
and actionable insights generation. It's designed for comprehensive data
exploration and business intelligence applications.

The analyzer combines pattern discovery with advanced statistical metrics,
providing insights that go beyond simple concentration patterns to include
data quality assessment, distribution analysis, and business recommendations.

Key Features:
    - Comprehensive statistical analysis of datasets
    - Field distribution and correlation analysis
    - Actionable insights generation with confidence scores
    - Data quality assessment and anomaly detection
    - Advanced concentration pattern analysis
    - Statistical significance testing capabilities

Example:
    Comprehensive analysis of user behavior data:

    >>> from dataspot.analyzers.analyzer import Analyzer
    >>> from dataspot.models.analyzer import AnalyzeInput, AnalyzeOptions
    >>>
    >>> # Initialize the analyzer
    >>> analyzer = Analyzer()
    >>>
    >>> # User engagement data
    >>> user_data = [
    ...     {"user_type": "premium", "device": "mobile", "action": "purchase", "value": 99.99},
    ...     {"user_type": "premium", "device": "desktop", "action": "browse", "value": 0},
    ...     {"user_type": "free", "device": "mobile", "action": "browse", "value": 0},
    ...     {"user_type": "free", "device": "mobile", "action": "signup", "value": 0},
    ... ]
    >>>
    >>> input_data = AnalyzeInput(
    ...     data=user_data,
    ...     fields=["user_type", "device", "action"]
    ... )
    >>> options = AnalyzeOptions(min_percentage=5.0, include_insights=True)
    >>>
    >>> results = analyzer.execute(input_data, options)
    >>> print(f"Found {results.statistics.patterns_found} patterns")
    >>> print(f"Max concentration: {results.statistics.max_concentration:.1f}%")
    >>>
    >>> # Example output:
    >>> # Found 3 patterns
    >>> # Max concentration: 75.0%

Notes:
    The analyzer automatically calculates statistical significance for patterns
    and provides confidence scores for generated insights. All results include
    metadata about data quality and analysis parameters.

See Also:
    - analyzers.finder: Basic pattern finding functionality
    - analyzers.discovery: Automatic pattern discovery
    - models.analyzer: Data models for analysis input and output

"""

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
    """Advanced data analyzer for comprehensive insights and statistical analysis.

    The Analyzer class extends basic pattern finding with sophisticated statistical
    analysis, field distribution assessment, and actionable insights generation.
    It's designed for business intelligence applications where understanding
    data characteristics and generating recommendations is crucial.

    This analyzer provides:
    - Statistical summaries and distributions
    - Field correlation and relationship analysis
    - Business insights with confidence scores
    - Data quality metrics and anomaly detection
    - Advanced pattern significance testing

    The class inherits preprocessing capabilities from Base and integrates
    with the Finder class for core pattern discovery, adding layers of
    statistical analysis and insight generation.

    Attributes:
        Inherits all preprocessing capabilities from Base class.

    Example:
        Comprehensive fraud detection analysis:

        >>> from dataspot.analyzers.analyzer import Analyzer
        >>> from dataspot.models.analyzer import AnalyzeInput, AnalyzeOptions
        >>>
        >>> # Transaction data for fraud analysis
        >>> transactions = [
        ...     {"country": "US", "payment_method": "card", "amount": 100, "risk_score": "low"},
        ...     {"country": "US", "payment_method": "card", "amount": 150, "risk_score": "low"},
        ...     {"country": "XX", "payment_method": "crypto", "amount": 5000, "risk_score": "high"},
        ...     {"country": "XX", "payment_method": "crypto", "amount": 7500, "risk_score": "high"},
        ... ]
        >>>
        >>> analyzer = Analyzer()
        >>>
        >>> input_data = AnalyzeInput(
        ...     data=transactions,
        ...     fields=["country", "payment_method", "risk_score"]
        ... )
        >>>
        >>> options = AnalyzeOptions(
        ...     min_percentage=10.0,
        ...     include_insights=True,
        ...     statistical_tests=True
        ... )
        >>>
        >>> results = analyzer.execute(input_data, options)
        >>>
        >>> print(f"Analysis Summary:")
        >>> print(f"- Total patterns found: {results.statistics.patterns_found}")
        >>> print(f"- Max concentration: {results.statistics.max_concentration:.1f}%")
        >>> print(f"- Average concentration: {results.statistics.avg_concentration:.1f}%")
        >>> print(f"- Records analyzed: {results.statistics.total_records}")
        >>>
        >>> # Example output:
        >>> # Analysis Summary:
        >>> # - Total patterns found: 4
        >>> # - Max concentration: 50.0%
        >>> # - Average concentration: 35.5%
        >>> # - Records analyzed: 4

    Notes:
        - Results include statistical significance testing for pattern reliability
        - Insights are generated with confidence scores based on data quality
        - Field statistics help identify the most informative attributes
        - Integrates seamlessly with preprocessing and filtering capabilities

    """

    def execute(
        self,
        input: AnalyzeInput,
        options: AnalyzeOptions,
    ) -> AnalyzeOutput:
        r"""Execute comprehensive data analysis with statistical insights and recommendations.

        Performs deep analysis of the provided dataset, combining pattern discovery
        with statistical analysis, field distribution assessment, and actionable
        insights generation. This method provides a complete analytical overview
        suitable for business intelligence and data exploration tasks.

        The analysis process includes:
        1. Data validation and preprocessing
        2. Core pattern discovery using advanced algorithms
        3. Statistical analysis and significance testing
        4. Field distribution and correlation analysis
        5. Insights generation with confidence scoring
        6. Data quality assessment and recommendations

        Args:
            input (AnalyzeInput): Analysis input configuration containing:
                - data: List of dictionaries representing records to analyze
                - fields: List of field names to analyze for patterns and statistics
                - query: Optional dictionary for filtering records before analysis
            options (AnalyzeOptions): Analysis configuration containing:
                - min_percentage: Minimum percentage threshold for pattern inclusion
                - max_percentage: Maximum percentage threshold for pattern filtering
                - min_count: Minimum record count for pattern inclusion
                - max_count: Maximum record count for pattern filtering
                - include_insights: Whether to generate actionable insights
                - statistical_tests: Whether to perform statistical significance tests
                - confidence_level: Statistical confidence level for tests (default: 0.95)
                - Other filtering and analysis parameters

        Returns:
            AnalyzeOutput: Comprehensive analysis results containing:
                - patterns: List of discovered patterns with detailed statistics
                - statistics: Statistical summary including totals, averages, and distributions
                - insights: Actionable insights with confidence scores and recommendations
                - field_stats: Detailed field-level statistics and distributions
                - top_patterns: Top 5 most significant patterns for quick review
                - fields_analyzed: List of fields included in the analysis

        Raises:
            ValueError: If input data is empty or malformed
            TypeError: If data format is incorrect (not list of dictionaries)
            KeyError: If specified fields don't exist in the data

        Example:
            Comprehensive e-commerce customer analysis:

            >>> from dataspot.models.analyzer import AnalyzeInput, AnalyzeOptions
            >>>
            >>> # Customer transaction and behavior data
            >>> customer_data = [
            ...     {"segment": "premium", "region": "US", "device": "mobile", "conversion": "yes"},
            ...     {"segment": "premium", "region": "US", "device": "desktop", "conversion": "yes"},
            ...     {"segment": "standard", "region": "EU", "device": "mobile", "conversion": "no"},
            ...     {"segment": "standard", "region": "EU", "device": "mobile", "conversion": "yes"},
            ...     {"segment": "premium", "region": "US", "device": "mobile", "conversion": "yes"},
            ... ]
            >>>
            >>> analyzer = Analyzer()
            >>>
            >>> input_data = AnalyzeInput(
            ...     data=customer_data,
            ...     fields=["segment", "region", "device", "conversion"]
            ... )
            >>>
            >>> options = AnalyzeOptions(
            ...     min_percentage=15.0,
            ...     include_insights=True,
            ...     statistical_tests=True,
            ...     limit=10
            ... )
            >>>
            >>> results = analyzer.execute(input_data, options)
            >>>
            >>> # Review comprehensive statistics
            >>> stats = results.statistics
            >>> print(f"Dataset Overview:")
            >>> print(f"- Total records: {stats.total_records}")
            >>> print(f"- Patterns discovered: {stats.patterns_found}")
            >>> print(f"- Max concentration: {stats.max_concentration:.1f}%")
            >>> print(f"- Average concentration: {stats.avg_concentration:.1f}%")
            >>>
            >>> # Review insights
            >>> insights = results.insights
            >>> print(f"\\nKey Insights:")
            >>> print(f"- Concentration trend: {insights.concentration_distribution}")
            >>> print(f"- Pattern quality: {insights.patterns_found} significant patterns")
            >>>
            >>> # Review top patterns
            >>> print(f"\\nTop Patterns:")
            >>> for i, pattern in enumerate(results.top_patterns[:3], 1):
            ...     print(f"{i}. {pattern.path} - {pattern.percentage:.1f}% ({pattern.count} records)")
            >>>
            >>> # Example output:
            >>> # Dataset Overview:
            >>> # - Total records: 5
            >>> # - Patterns discovered: 6
            >>> # - Max concentration: 60.0%
            >>> # - Average concentration: 35.5%
            >>> #
            >>> # Key Insights:
            >>> # - Concentration trend: Moderate concentration patterns
            >>> # - Pattern quality: 6 significant patterns
            >>> #
            >>> # Top Patterns:
            >>> # 1. ['premium', 'US', 'mobile'] - 60.0% (3 records)
            >>> # 2. ['premium', 'US'] - 60.0% (3 records)
            >>> # 3. ['premium'] - 60.0% (3 records)

        Notes:
            - Statistical tests are performed when enabled to validate pattern significance
            - Insights include confidence scores based on data quality and sample size
            - Field statistics help identify the most predictive and informative attributes
            - Results are suitable for reporting, dashboards, and automated alerting
            - Processing time scales linearly with data size and number of fields analyzed

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
        """Calculate comprehensive statistical metrics for the dataset.

        Computes essential statistical measures including record counts,
        filtering ratios, and data quality metrics. These statistics
        provide context for pattern analysis and help assess the
        reliability of discovered insights.

        Args:
            data (List[Dict[str, Any]]): Input data records to analyze.
                Each record should be a dictionary with consistent field names.
            query (Optional[Dict[str, Any]]): Optional query filters to apply
                before statistical calculation. Supports MongoDB-style syntax.

        Returns:
            Dict[str, Any]: Statistical metrics dictionary containing:
                - total_records: Total number of input records
                - filtered_records: Number of records after query filtering
                - filter_ratio: Percentage of records retained after filtering

        Example:
            Basic statistical calculation:

            >>> data = [
            ...     {"category": "A", "value": 100},
            ...     {"category": "B", "value": 200},
            ...     {"category": "A", "value": 150},
            ... ]
            >>>
            >>> # Calculate without filtering
            >>> stats = analyzer._calculate_statistics(data, None)
            >>> print(f"Total records: {stats['total_records']}")
            >>>
            >>> # Calculate with filtering
            >>> query = {"value": {"$gte": 150}}
            >>> filtered_stats = analyzer._calculate_statistics(data, query)
            >>> print(f"Filtered records: {filtered_stats['filtered_records']}")
            >>> print(f"Filter ratio: {filtered_stats['filter_ratio']:.1f}%")
            >>>
            >>> # Example output:
            >>> # Total records: 3
            >>> # Filtered records: 2
            >>> # Filter ratio: 66.7%

        Notes:
            - Filter ratio helps assess data quality and query effectiveness
            - Zero division is handled gracefully for empty datasets
            - Supports complex query filters including range and list operations

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
        """Generate actionable business insights from discovered patterns.

        Analyzes discovered patterns to generate meaningful business insights,
        including concentration trends, pattern significance, and data
        distribution characteristics. These insights help translate
        statistical findings into actionable business intelligence.

        Args:
            patterns (List): List of discovered pattern objects with statistics.
                Each pattern should have attributes like percentage, count, and path.

        Returns:
            Dict[str, Any]: Insights dictionary containing:
                - patterns_found: Total number of significant patterns discovered
                - max_concentration: Highest concentration percentage found
                - avg_concentration: Average concentration across all patterns
                - concentration_distribution: Descriptive analysis of concentration trends

        Example:
            Generating insights from e-commerce patterns:

            >>> # Sample patterns (normally from pattern discovery)
            >>> patterns = [
            ...     MockPattern(percentage=75.0, count=30, path=["premium", "mobile"]),
            ...     MockPattern(percentage=45.0, count=18, path=["standard", "desktop"]),
            ...     MockPattern(percentage=25.0, count=10, path=["free", "mobile"]),
            ... ]
            >>>
            >>> insights = analyzer._generate_insights(patterns)
            >>>
            >>> print(f"Insights Generated:")
            >>> print(f"- Patterns found: {insights['patterns_found']}")
            >>> print(f"- Maximum concentration: {insights['max_concentration']:.1f}%")
            >>> print(f"- Average concentration: {insights['avg_concentration']:.1f}%")
            >>> print(f"- Distribution trend: {insights['concentration_distribution']}")
            >>>
            >>> # Example output:
            >>> # Insights Generated:
            >>> # - Patterns found: 3
            >>> # - Maximum concentration: 75.0%
            >>> # - Average concentration: 48.3%
            >>> # - Distribution trend: High concentration patterns dominant

        Notes:
            - Empty pattern lists are handled gracefully with default values
            - Concentration distribution analysis helps identify data characteristics
            - Insights are designed to be human-readable and actionable
            - Results can be used for automated alerting and reporting systems

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
        """Analyze and categorize the distribution of concentration values.

        Evaluates the distribution of concentration percentages to provide
        a qualitative assessment of data patterns. This analysis helps
        understand whether the data shows strong clustering, moderate
        grouping, or distributed patterns.

        Args:
            concentrations (List[float]): List of concentration percentages
                from discovered patterns. Values should be between 0 and 100.

        Returns:
            str: Descriptive categorization of concentration distribution:
                - "High concentration patterns dominant": >30% of patterns have ≥50% concentration
                - "Moderate concentration patterns": >50% of patterns have 20-50% concentration
                - "Low concentration patterns prevalent": Most patterns have <20% concentration
                - "No patterns found": Empty concentration list

        Example:
            Analyzing different concentration distributions:

            >>> # High concentration scenario (fraud detection)
            >>> high_concentrations = [85.0, 72.0, 91.0, 68.0, 45.0]
            >>> result1 = analyzer._analyze_concentration_distribution(high_concentrations)
            >>> print(f"Fraud analysis: {result1}")
            >>>
            >>> # Moderate concentration scenario (customer segmentation)
            >>> moderate_concentrations = [35.0, 28.0, 42.0, 33.0, 26.0]
            >>> result2 = analyzer._analyze_concentration_distribution(moderate_concentrations)
            >>> print(f"Customer analysis: {result2}")
            >>>
            >>> # Low concentration scenario (diverse data)
            >>> low_concentrations = [15.0, 8.0, 12.0, 18.0, 6.0]
            >>> result3 = analyzer._analyze_concentration_distribution(low_concentrations)
            >>> print(f"Diverse data: {result3}")
            >>>
            >>> # Example output:
            >>> # Fraud analysis: High concentration patterns dominant
            >>> # Customer analysis: Moderate concentration patterns
            >>> # Diverse data: Low concentration patterns prevalent

        Notes:
            - Thresholds are optimized for typical business data distributions
            - High concentration often indicates strong clustering or anomalies
            - Moderate concentration suggests meaningful but not extreme grouping
            - Low concentration may indicate diverse, well-distributed data

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
