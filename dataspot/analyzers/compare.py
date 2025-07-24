"""Advanced temporal comparison analyzer for detecting data changes and anomalies.

This module provides the `Compare` class, which performs sophisticated comparison
analysis between two datasets (typically representing different time periods).
It's designed for monitoring data drift, detecting anomalies, fraud pattern
evolution, and understanding how data patterns change over time.

The analyzer combines statistical analysis with pattern comparison to identify
significant changes, new patterns, disappeared patterns, and trend analysis.
It's particularly valuable for continuous monitoring, alerting systems, and
business intelligence applications.

Key Features:
    - Temporal comparison between current and baseline datasets
    - Statistical significance testing for change validation
    - Pattern categorization (new, disappeared, increased, decreased, stable)
    - Advanced change metrics and thresholds
    - Fraud detection and anomaly monitoring capabilities
    - Business intelligence and trend analysis
    - Configurable alerting and significance levels

Example:
    Fraud detection comparison between months:

    >>> from dataspot.analyzers.compare import Compare
    >>> from dataspot.models.compare import CompareInput, CompareOptions
    >>>
    >>> # Initialize the comparison analyzer
    >>> compare_analyzer = Compare()
    >>>
    >>> # Previous month's transaction data (baseline)
    >>> last_month = [
    ...     {"country": "US", "payment_method": "card", "risk_score": "low"},
    ...     {"country": "US", "payment_method": "card", "risk_score": "low"},
    ...     {"country": "UK", "payment_method": "bank", "risk_score": "low"},
    ... ]
    >>>
    >>> # Current month's transaction data
    >>> this_month = [
    ...     {"country": "US", "payment_method": "card", "risk_score": "low"},
    ...     {"country": "US", "payment_method": "crypto", "risk_score": "high"},
    ...     {"country": "XX", "payment_method": "crypto", "risk_score": "high"},
    ...     {"country": "XX", "payment_method": "crypto", "risk_score": "high"},
    ... ]
    >>>
    >>> input_data = CompareInput(
    ...     current_data=this_month,
    ...     baseline_data=last_month,
    ...     fields=["country", "payment_method", "risk_score"]
    ... )
    >>>
    >>> options = CompareOptions(
    ...     statistical_significance=True,
    ...     change_threshold=0.25
    ... )
    >>>
    >>> results = compare_analyzer.execute(input_data, options)
    >>> print(f"Significant changes: {results.statistics.significant_changes}")
    >>> print(f"New patterns: {len(results.new_patterns)}")
    >>>
    >>> # Example output:
    >>> # Significant changes: 3
    >>> # New patterns: 2

Notes:
    All comparison methods support statistical significance testing and provide
    confidence scores for changes. Results include detailed change categorization
    and are suitable for automated monitoring and alerting systems.

See Also:
    - analyzers.finder: Basic pattern finding functionality
    - analyzers.stats: Statistical analysis methods
    - models.compare: Data models for comparison input and output

"""

from typing import Any, Dict, List, Optional

from ..models.compare import (
    ChangeItem,
    CompareInput,
    CompareOptions,
    CompareOutput,
    ComparisonStatistics,
)
from ..models.finder import FindInput, FindOptions
from .base import Base
from .stats import Stats


class Compare(Base):
    """Advanced temporal comparison analyzer for detecting changes and anomalies.

    The Compare class provides sophisticated comparison capabilities between two
    datasets, typically representing different time periods. It's designed for
    monitoring applications where detecting changes, trends, and anomalies is
    crucial for business operations and security.

    This analyzer specializes in:
    - Statistical comparison of pattern distributions
    - Change significance testing and validation
    - Trend analysis and pattern evolution tracking
    - Anomaly detection and fraud monitoring
    - Business intelligence and reporting
    - Automated alerting for significant changes

    The class integrates statistical analysis methods to provide reliable
    change detection with configurable sensitivity and significance testing.

    Attributes:
        statistical_methods (Stats): Statistical analysis engine for significance testing.
        Inherits preprocessing capabilities from Base class.

    Example:
        Comprehensive security monitoring comparison:

        >>> from dataspot.analyzers.compare import Compare
        >>> from dataspot.models.compare import CompareInput, CompareOptions
        >>>
        >>> # Security events from previous week (baseline)
        >>> baseline_events = [
        ...     {"source_ip": "192.168.1.1", "user_agent": "Chrome", "endpoint": "/login", "status": "success"},
        ...     {"source_ip": "192.168.1.1", "user_agent": "Chrome", "endpoint": "/dashboard", "status": "success"},
        ...     {"source_ip": "192.168.1.2", "user_agent": "Firefox", "endpoint": "/login", "status": "success"},
        ... ]
        >>>
        >>> # Security events from current week
        >>> current_events = [
        ...     {"source_ip": "192.168.1.1", "user_agent": "Chrome", "endpoint": "/login", "status": "success"},
        ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "endpoint": "/admin", "status": "failed"},
        ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "endpoint": "/admin", "status": "failed"},
        ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "endpoint": "/login", "status": "failed"},
        ... ]
        >>>
        >>> compare_analyzer = Compare()
        >>>
        >>> input_data = CompareInput(
        ...     current_data=current_events,
        ...     baseline_data=baseline_events,
        ...     fields=["source_ip", "user_agent", "status"]
        ... )
        >>>
        >>> options = CompareOptions(
        ...     statistical_significance=True,
        ...     change_threshold=0.20,  # 20% change threshold
        ...     min_percentage=5.0
        ... )
        >>>
        >>> results = compare_analyzer.execute(input_data, options)
        >>>
        >>> print(f"Comparison Results:")
        >>> print(f"- Total changes detected: {len(results.changes)}")
        >>> print(f"- Significant changes: {results.statistics.significant_changes}")
        >>> print(f"- New suspicious patterns: {len(results.new_patterns)}")
        >>> print(f"- Disappeared normal patterns: {len(results.disappeared_patterns)}")
        >>>
        >>> # Example output:
        >>> # Comparison Results:
        >>> # - Total changes detected: 8
        >>> # - Significant changes: 4
        >>> # - New suspicious patterns: 3
        >>> # - Disappeared normal patterns: 2

    Notes:
        - Statistical methods provide confidence scores for change reliability
        - Pattern categorization helps prioritize security responses
        - Change thresholds can be tuned based on business requirements
        - Supports both absolute and relative change measurements

    """

    def __init__(self):
        """Initialize Compare analyzer with statistical analysis capabilities.

        Creates a new instance with integrated statistical methods for
        significance testing and change validation. The analyzer inherits
        preprocessing capabilities from the Base class.
        """
        super().__init__()
        self.statistical_methods = Stats()

    def execute(
        self,
        input: CompareInput,
        options: Optional[CompareOptions] = None,
    ) -> CompareOutput:
        r"""Execute comprehensive temporal comparison analysis between datasets.

        Performs sophisticated comparison between current and baseline datasets
        to identify significant changes, trends, and anomalies. The analysis
        includes statistical significance testing, pattern categorization,
        and detailed change metrics suitable for monitoring and alerting.

        The comparison process includes:
        1. Data validation and preprocessing
        2. Pattern extraction from both datasets
        3. Statistical comparison and significance testing
        4. Change categorization and threshold analysis
        5. Trend analysis and pattern evolution tracking
        6. Results compilation with detailed metrics

        Args:
            input (CompareInput): Comparison input configuration containing:
                - current_data: List of dictionaries representing recent/current period data
                - baseline_data: List of dictionaries representing baseline/reference period data
                - fields: List of field names to analyze for changes
                - query: Optional dictionary for filtering both datasets before comparison
            options (CompareOptions): Comparison configuration containing:
                - statistical_significance: Whether to perform statistical significance tests
                - change_threshold: Minimum relative change to consider significant (default: 0.15)
                - min_percentage: Minimum percentage threshold for pattern inclusion
                - max_percentage: Maximum percentage threshold for pattern filtering
                - min_count: Minimum record count for pattern inclusion
                - max_count: Maximum record count for pattern filtering
                - Other filtering and analysis parameters

        Returns:
            CompareOutput: Comprehensive comparison results containing:
                - changes: Complete list of detected changes with detailed metrics
                - stable_patterns: Patterns that remained relatively unchanged
                - new_patterns: Patterns that appear only in the current dataset
                - disappeared_patterns: Patterns that appear only in the baseline dataset
                - increased_patterns: Patterns with significant increases
                - decreased_patterns: Patterns with significant decreases
                - statistics: Summary statistics of the comparison analysis
                - fields_analyzed: List of fields included in the analysis

        Raises:
            ValueError: If input data is empty or malformed
            TypeError: If data format is incorrect (not list of dictionaries)
            KeyError: If specified fields don't exist in the data

        Example:
            E-commerce conversion rate monitoring:

            >>> from dataspot.models.compare import CompareInput, CompareOptions
            >>>
            >>> # Previous quarter's customer data (baseline)
            >>> q1_customers = [
            ...     {"segment": "premium", "region": "US", "device": "mobile", "converted": "yes"},
            ...     {"segment": "premium", "region": "US", "device": "desktop", "converted": "yes"},
            ...     {"segment": "standard", "region": "EU", "device": "mobile", "converted": "no"},
            ...     {"segment": "standard", "region": "EU", "device": "mobile", "converted": "yes"},
            ... ]
            >>>
            >>> # Current quarter's customer data
            >>> q2_customers = [
            ...     {"segment": "premium", "region": "US", "device": "mobile", "converted": "yes"},
            ...     {"segment": "premium", "region": "US", "device": "mobile", "converted": "yes"},
            ...     {"segment": "premium", "region": "APAC", "device": "mobile", "converted": "yes"},
            ...     {"segment": "standard", "region": "EU", "device": "mobile", "converted": "no"},
            ... ]
            >>>
            >>> compare_analyzer = Compare()
            >>>
            >>> input_data = CompareInput(
            ...     current_data=q2_customers,
            ...     baseline_data=q1_customers,
            ...     fields=["segment", "region", "device"]
            ... )
            >>>
            >>> options = CompareOptions(
            ...     statistical_significance=True,
            ...     change_threshold=0.25,  # 25% change threshold
            ...     min_count=1
            ... )
            >>>
            >>> results = compare_analyzer.execute(input_data, options)
            >>>
            >>> # Analyze overall comparison statistics
            >>> stats = results.statistics
            >>> print(f"Comparison Overview:")
            >>> print(f"- Current period records: {stats.current_total}")
            >>> print(f"- Baseline period records: {stats.baseline_total}")
            >>> print(f"- Patterns compared: {stats.patterns_compared}")
            >>> print(f"- Significant changes: {stats.significant_changes}")
            >>>
            >>> # Review new market opportunities
            >>> print(f"\nNew Market Patterns:")
            >>> for pattern in results.new_patterns[:3]:
            ...     print(f"- {pattern.path}: {pattern.current_count} occurrences")
            ...     print(f"  Status: {pattern.status}")
            >>>
            >>> # Review performance changes
            >>> print(f"\nSignificant Changes:")
            >>> for change in results.changes[:3]:
            ...     if change.is_significant:
            ...         print(f"- Pattern: {change.path}")
            ...         print(f"  Change: {change.count_change_percentage:+.1f}%")
            ...         print(f"  Status: {change.status}")
            >>>
            >>> # Example output:
            >>> # Comparison Overview:
            >>> # - Current period records: 4
            >>> # - Baseline period records: 4
            >>> # - Patterns compared: 12
            >>> # - Significant changes: 5
            >>> #
            >>> # New Market Patterns:
            >>> # - ['premium', 'APAC', 'mobile']: 1 occurrences
            >>> #   Status: NEW
            >>> #
            >>> # Significant Changes:
            >>> # - Pattern: ['premium', 'US', 'mobile']
            >>> #   Change: +100.0%
            >>> #   Status: SIGNIFICANT_INCREASE

        Notes:
            - Statistical significance testing validates the reliability of detected changes
            - Change categorization helps prioritize business actions and responses
            - Threshold configuration allows tuning sensitivity based on business needs
            - Results are suitable for automated monitoring, alerting, and reporting systems
            - Processing time scales with the number of unique patterns in both datasets

        """
        if options is None:
            options = CompareOptions()

        # Validate input data
        self._validate_data(input.current_data)
        self._validate_data(input.baseline_data)

        current_data = input.current_data
        baseline_data = input.baseline_data

        # Apply query filters if provided
        if input.query:
            current_data = self._filter_data_by_query(current_data, input.query)
            baseline_data = self._filter_data_by_query(baseline_data, input.query)

        # Get patterns for both datasets
        current_patterns = self._get_patterns(current_data, input.fields, options)
        baseline_patterns = self._get_patterns(baseline_data, input.fields, options)

        # Compare patterns and detect changes
        changes_data = self._compare_patterns(
            current_patterns,
            baseline_patterns,
            statistical_significance=options.statistical_significance,
            change_threshold=options.change_threshold,
        )

        # Apply limit to changes if specified
        if options.limit is not None:
            changes_data = changes_data[: options.limit]

        # Convert changes to ChangeItem dataclasses
        changes = [self._dict_to_change_item(change) for change in changes_data]

        # Categorize patterns (using limited changes_data)
        categorized_patterns = self._categorize_patterns(changes_data)

        # Convert categorized patterns to ChangeItem dataclasses
        stable_patterns = [
            self._dict_to_change_item(item)
            for item in categorized_patterns["stable_patterns"]
        ]
        new_patterns = [
            self._dict_to_change_item(item)
            for item in categorized_patterns["new_patterns"]
        ]
        disappeared_patterns = [
            self._dict_to_change_item(item)
            for item in categorized_patterns["disappeared_patterns"]
        ]
        increased_patterns = [
            self._dict_to_change_item(item)
            for item in categorized_patterns["increased_patterns"]
        ]
        decreased_patterns = [
            self._dict_to_change_item(item)
            for item in categorized_patterns["decreased_patterns"]
        ]

        # Create ComparisonStatistics dataclass
        statistics = ComparisonStatistics(
            current_total=len(input.current_data),
            baseline_total=len(input.baseline_data),
            patterns_compared=len(changes),
            significant_changes=len([c for c in changes_data if c["is_significant"]]),
        )

        return CompareOutput(
            changes=changes,
            stable_patterns=stable_patterns,
            new_patterns=new_patterns,
            disappeared_patterns=disappeared_patterns,
            increased_patterns=increased_patterns,
            decreased_patterns=decreased_patterns,
            statistics=statistics,
            fields_analyzed=input.fields,
            change_threshold=options.change_threshold,
            statistical_significance=options.statistical_significance,
        )

    def _dict_to_change_item(self, change_dict: Dict[str, Any]) -> ChangeItem:
        """Convert a change dictionary to structured ChangeItem dataclass.

        Transforms internal change representation to the standard ChangeItem
        dataclass format for consistent API output. This method ensures all
        change metrics and metadata are properly structured and typed.

        Args:
            change_dict (Dict[str, Any]): Internal change dictionary containing
                all change metrics, statistical data, and categorization info.

        Returns:
            ChangeItem: Structured dataclass containing:
                - path: Pattern path identifier
                - count and percentage metrics for current and baseline
                - change calculations and statistical significance
                - categorization and status information

        Example:
            Converting internal change data:

            >>> change_data = {
            ...     "path": ["US", "card"],
            ...     "current_count": 150,
            ...     "baseline_count": 100,
            ...     "count_change": 50,
            ...     "count_change_percentage": 50.0,
            ...     "status": "INCREASE",
            ...     "is_significant": True
            ... }
            >>>
            >>> change_item = compare_analyzer._dict_to_change_item(change_data)
            >>> print(f"Pattern: {change_item.path}")
            >>> print(f"Change: {change_item.count_change_percentage:.1f}%")
            >>> print(f"Significant: {change_item.is_significant}")
            >>>
            >>> # Example output:
            >>> # Pattern: ['US', 'card']
            >>> # Change: 50.0%
            >>> # Significant: True

        Notes:
            - Ensures consistent data structure across all comparison results
            - Maintains all statistical and categorization metadata
            - Provides type safety for downstream analysis and reporting

        """
        return ChangeItem(
            path=change_dict["path"],
            current_count=change_dict["current_count"],
            baseline_count=change_dict["baseline_count"],
            count_change=change_dict["count_change"],
            count_change_percentage=change_dict["count_change_percentage"],
            relative_change=change_dict["relative_change"],
            current_percentage=change_dict["current_percentage"],
            baseline_percentage=change_dict["baseline_percentage"],
            percentage_change=change_dict["percentage_change"],
            status=change_dict["status"],
            is_new=change_dict["is_new"],
            is_disappeared=change_dict["is_disappeared"],
            is_significant=change_dict["is_significant"],
            depth=change_dict["depth"],
            statistical_significance=change_dict["statistical_significance"],
        )

    def _get_patterns(
        self, data: List[Dict[str, Any]], fields: List[str], options: CompareOptions
    ) -> Dict[str, Dict[str, Any]]:
        """Extract and organize patterns from dataset for comparison analysis.

        Uses the Finder analyzer to discover patterns in the provided dataset
        and converts them to a dictionary format optimized for comparison
        operations. This method applies all configured filters and options.

        Args:
            data (List[Dict[str, Any]]): Dataset to extract patterns from.
                Each record should be a dictionary with consistent field names.
            fields (List[str]): List of field names to analyze for pattern extraction.
            options (CompareOptions): Configuration options for pattern extraction
                including filtering thresholds and analysis parameters.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping pattern paths to their
                statistics including count, percentage, samples, and depth.

        Example:
            Extracting patterns for comparison:

            >>> data = [
            ...     {"country": "US", "payment": "card", "status": "success"},
            ...     {"country": "US", "payment": "card", "status": "success"},
            ...     {"country": "UK", "payment": "bank", "status": "failed"},
            ... ]
            >>>
            >>> fields = ["country", "payment"]
            >>> options = CompareOptions(min_percentage=20.0)
            >>>
            >>> patterns = compare_analyzer._get_patterns(data, fields, options)
            >>>
            >>> for path, stats in patterns.items():
            ...     print(f"Pattern {path}: {stats['count']} records ({stats['percentage']:.1f}%)")
            >>>
            >>> # Example output:
            >>> # Pattern ['US', 'card']: 2 records (66.7%)
            >>> # Pattern ['UK', 'bank']: 1 records (33.3%)

        Notes:
            - Applies preprocessing functions before pattern extraction
            - Filters patterns based on configured thresholds
            - Maintains pattern metadata for statistical comparison
            - Results are optimized for efficient comparison operations

        """
        from .finder import Finder

        finder = Finder()
        finder.preprocessors = self.preprocessors

        find_input = FindInput(data=data, fields=fields)
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

        # Convert to dictionary for easier comparison
        pattern_dict = {}
        for pattern in patterns.patterns:
            pattern_dict[pattern.path] = {
                "count": pattern.count,
                "percentage": pattern.percentage,
                "samples": pattern.samples,
                "depth": pattern.depth,
            }

        return pattern_dict

    def _compare_patterns(
        self,
        current_patterns: Dict[str, Dict[str, Any]],
        baseline_patterns: Dict[str, Dict[str, Any]],
        statistical_significance: bool = False,
        change_threshold: float = 0.15,
    ) -> List[Dict[str, Any]]:
        """Perform comprehensive pattern comparison with advanced statistical analysis.

        Compares current patterns against baseline patterns to detect significant
        changes, calculate change metrics, and perform statistical significance
        testing. This is the core comparison engine that generates detailed
        change analytics.

        Args:
            current_patterns (Dict[str, Dict[str, Any]]): Patterns from current dataset
                with statistics including count, percentage, and metadata.
            baseline_patterns (Dict[str, Dict[str, Any]]): Patterns from baseline dataset
                with statistics for comparison reference.
            statistical_significance (bool): Whether to perform statistical significance
                testing using advanced statistical methods. Default: False.
            change_threshold (float): Minimum relative change to consider significant.
                Values between 0.0 and 1.0 representing percentage thresholds. Default: 0.15.

        Returns:
            List[Dict[str, Any]]: List of change dictionaries containing:
                - Pattern identification and path information
                - Current and baseline counts and percentages
                - Change calculations (absolute, relative, percentage)
                - Status categorization and significance flags
                - Statistical analysis results if enabled

        Example:
            Comparing fraud detection patterns:

            >>> # Current month patterns
            >>> current = {
            ...     "['US', 'card']": {"count": 100, "percentage": 80.0},
            ...     "['XX', 'crypto']": {"count": 25, "percentage": 20.0}
            ... }
            >>>
            >>> # Previous month patterns (baseline)
            >>> baseline = {
            ...     "['US', 'card']": {"count": 120, "percentage": 90.0},
            ...     "['UK', 'bank']": {"count": 15, "percentage": 10.0}
            ... }
            >>>
            >>> changes = compare_analyzer._compare_patterns(
            ...     current, baseline,
            ...     statistical_significance=True,
            ...     change_threshold=0.20
            ... )
            >>>
            >>> for change in changes:
            ...     if change['is_significant']:
            ...         print(f"Pattern: {change['path']}")
            ...         print(f"Status: {change['status']}")
            ...         print(f"Change: {change['count_change_percentage']:+.1f}%")
            >>>
            >>> # Example output:
            >>> # Pattern: ['XX', 'crypto']
            >>> # Status: NEW
            >>> # Change: +inf%
            >>> # Pattern: ['UK', 'bank']
            >>> # Status: DISAPPEARED
            >>> # Change: -100.0%

        Notes:
            - Statistical significance testing provides confidence scores for changes
            - Change thresholds help filter noise and focus on meaningful changes
            - Status categorization enables automated alerting and prioritization
            - Results are sorted by significance and change magnitude

        """
        changes = []

        # Get all unique pattern paths
        all_paths = set(current_patterns.keys()) | set(baseline_patterns.keys())

        for path in all_paths:
            current = current_patterns.get(
                path, {"count": 0, "percentage": 0.0, "samples": []}
            )
            baseline = baseline_patterns.get(
                path, {"count": 0, "percentage": 0.0, "samples": []}
            )

            # Calculate changes
            count_change = current["count"] - baseline["count"]

            if baseline["count"] > 0:
                count_change_pct = (count_change / baseline["count"]) * 100
                relative_change = (
                    count_change / baseline["count"]
                )  # For threshold comparison
            else:
                count_change_pct = float("inf") if current["count"] > 0 else 0.0
                relative_change = float("inf") if current["count"] > 0 else 0.0

            percentage_change = current["percentage"] - baseline["percentage"]

            # Statistical significance if requested
            stats = {}
            if (
                statistical_significance
                and baseline["count"] > 0
                and current["count"] > 0
            ):
                stats = self.statistical_methods.perform_comprehensive_analysis(
                    current["count"], baseline["count"]
                )

            # Determine significance based on threshold
            is_significant = (
                abs(relative_change) >= change_threshold
                if relative_change != float("inf")
                else current["count"] > 5  # For new patterns
            )

            change_info = {
                "path": path,
                "current_count": current["count"],
                "baseline_count": baseline["count"],
                "count_change": count_change,
                "count_change_percentage": count_change_pct,
                "relative_change": relative_change,
                "current_percentage": current["percentage"],
                "baseline_percentage": baseline["percentage"],
                "percentage_change": percentage_change,
                "status": self._get_change_status(count_change_pct),
                "is_new": path not in baseline_patterns,
                "is_disappeared": path not in current_patterns,
                "is_significant": is_significant,
                "depth": current.get("depth", baseline.get("depth", 1)),
                "statistical_significance": stats,
            }

            # Only include patterns that have actual changes
            has_real_change = (
                count_change != 0
                or change_info["is_new"]
                or change_info["is_disappeared"]
            )

            if has_real_change:
                changes.append(change_info)

        # Sort by significance and magnitude
        changes.sort(
            key=lambda x: (
                x["is_significant"],
                abs(x["count_change_percentage"])
                if x["count_change_percentage"] != float("inf")
                else 1000,
            ),
            reverse=True,
        )

        return changes

    def _get_change_status(self, change_pct: float) -> str:
        """Determine descriptive status category based on change percentage.

        Categorizes changes into meaningful business status levels based on
        the magnitude and direction of change. This classification helps
        prioritize responses and understand the severity of changes.

        Args:
            change_pct (float): Percentage change value. Can be positive (increase),
                negative (decrease), or infinity (new pattern).

        Returns:
            str: Status category representing the change magnitude and direction:
                - "CRITICAL_INCREASE": >200% increase (very high priority)
                - "SIGNIFICANT_INCREASE": 100-200% increase (high priority)
                - "INCREASE": 50-100% increase (medium priority)
                - "SLIGHT_INCREASE": 15-50% increase (low priority)
                - "STABLE": -15% to +15% change (monitoring)
                - "SLIGHT_DECREASE": -15% to -50% decrease (low priority)
                - "DECREASE": -50% to -80% decrease (medium priority)
                - "CRITICAL_DECREASE": -80% to -100% decrease (high priority)
                - "NEW": New pattern (infinity change)
                - "DISAPPEARED": Pattern no longer exists

        Example:
            Categorizing different change scenarios:

            >>> # Critical fraud increase scenario
            >>> status1 = compare_analyzer._get_change_status(250.0)
            >>> print(f"Fraud spike: {status1}")
            >>>
            >>> # Normal business growth
            >>> status2 = compare_analyzer._get_change_status(35.0)
            >>> print(f"Business growth: {status2}")
            >>>
            >>> # Stable operations
            >>> status3 = compare_analyzer._get_change_status(5.0)
            >>> print(f"Stable operations: {status3}")
            >>>
            >>> # New suspicious pattern
            >>> status4 = compare_analyzer._get_change_status(float("inf"))
            >>> print(f"New pattern: {status4}")
            >>>
            >>> # Example output:
            >>> # Fraud spike: CRITICAL_INCREASE
            >>> # Business growth: INCREASE
            >>> # Stable operations: STABLE
            >>> # New pattern: NEW

        Notes:
            - Thresholds are optimized for typical business scenarios
            - Critical levels require immediate attention and investigation
            - Status categories enable automated alerting and escalation
            - New and disappeared patterns are flagged for special handling

        """
        if change_pct == float("inf"):
            return "NEW"

        # Status thresholds ordered from highest to lowest
        status_thresholds = [
            (200, "CRITICAL_INCREASE"),
            (100, "SIGNIFICANT_INCREASE"),
            (50, "INCREASE"),
            (15, "SLIGHT_INCREASE"),
            (-15, "STABLE"),
            (-50, "SLIGHT_DECREASE"),
            (-80, "DECREASE"),
            (-100, "CRITICAL_DECREASE"),
        ]

        for threshold, status in status_thresholds:
            if change_pct >= threshold:
                return status

        return "DISAPPEARED"

    def _categorize_patterns(
        self, changes: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Organize detected changes into meaningful business categories.

        Groups changes by their characteristics and business impact to enable
        focused analysis and appropriate responses. This categorization helps
        teams prioritize actions and understand different types of changes.

        Args:
            changes (List[Dict[str, Any]]): List of all detected changes with
                their status, significance, and change metrics.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Categorized changes dictionary containing:
                - stable_patterns: Patterns with minimal changes (business as usual)
                - new_patterns: Patterns appearing only in current data (opportunities/threats)
                - disappeared_patterns: Patterns only in baseline data (lost opportunities)
                - increased_patterns: Patterns with significant increases (growth/issues)
                - decreased_patterns: Patterns with significant decreases (decline/improvement)

        Example:
            Categorizing e-commerce customer behavior changes:

            >>> # Sample changes from customer analysis
            >>> changes = [
            ...     {"status": "STABLE", "is_new": False, "is_disappeared": False},
            ...     {"status": "NEW", "is_new": True, "is_disappeared": False},
            ...     {"status": "INCREASE", "is_new": False, "is_disappeared": False},
            ...     {"status": "DISAPPEARED", "is_new": False, "is_disappeared": True},
            ... ]
            >>>
            >>> categories = compare_analyzer._categorize_patterns(changes)
            >>>
            >>> print(f"Pattern Categories:")
            >>> for category, patterns in categories.items():
            ...     print(f"- {category}: {len(patterns)} patterns")
            >>>
            >>> # Example output:
            >>> # Pattern Categories:
            >>> # - stable_patterns: 1 patterns
            >>> # - new_patterns: 1 patterns
            >>> # - disappeared_patterns: 1 patterns
            >>> # - increased_patterns: 1 patterns
            >>> # - decreased_patterns: 0 patterns

        Notes:
            - Categories enable focused analysis of different change types
            - New patterns often indicate emerging opportunities or threats
            - Disappeared patterns may represent lost market segments
            - Increased/decreased patterns show trend directions
            - Stable patterns provide baseline context for changes

        """
        stable_patterns = [c for c in changes if c["status"] == "STABLE"]
        new_patterns = [c for c in changes if c["is_new"]]
        disappeared_patterns = [c for c in changes if c["is_disappeared"]]
        increased_patterns = [c for c in changes if "INCREASE" in c["status"]]
        decreased_patterns = [c for c in changes if "DECREASE" in c["status"]]

        return {
            "stable_patterns": stable_patterns,
            "new_patterns": new_patterns,
            "disappeared_patterns": disappeared_patterns,
            "increased_patterns": increased_patterns,
            "decreased_patterns": decreased_patterns,
        }
