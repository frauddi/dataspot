"""Core pattern analysis engine for finding data concentration patterns and anomalies.

This module provides the main `Dataspot` class, which serves as the primary interface
for analyzing datasets to discover concentration patterns, anomalies, and insights.
The engine supports various analysis modes including pattern finding, hierarchical
tree building, automatic discovery, and temporal comparisons.

Key Features:
    - Pattern discovery and concentration analysis
    - Hierarchical tree visualization of data relationships
    - Automatic field ranking and pattern discovery
    - Temporal comparison for change detection
    - Flexible preprocessing and filtering capabilities
    - Statistical significance testing for comparisons

Example:
    Basic usage for fraud detection:

    >>> from dataspot import Dataspot
    >>> from dataspot.models.finder import FindInput, FindOptions
    >>>
    >>> # Initialize the analyzer
    >>> ds = Dataspot()
    >>>
    >>> # Analyze transaction data for suspicious patterns
    >>> transactions = [
    ...     {"country": "US", "amount": 100, "payment_method": "card"},
    ...     {"country": "US", "amount": 150, "payment_method": "card"},
    ...     {"country": "FR", "amount": 50, "payment_method": "wire"},
    ... ]
    >>>
    >>> input_data = FindInput(
    ...     data=transactions,
    ...     fields=["country", "payment_method"]
    ... )
    >>> options = FindOptions(top=10, min_percentage=5.0)
    >>>
    >>> results = ds.find(input_data, options)
    >>> print(f"Found {len(results.patterns)} concentration patterns")
    >>>
    >>> # Example output:
    >>> # Found 2 concentration patterns

Notes:
    All methods support optional preprocessing functions that can be applied
    to specific fields before analysis. This is useful for data normalization,
    cleaning, or transformation tasks.

See Also:
    - analyzers.finder: Core pattern finding algorithms
    - analyzers.analyzer: Comprehensive analysis with statistical insights
    - analyzers.tree: Hierarchical tree analysis
    - analyzers.discovery: Automatic pattern discovery
    - analyzers.compare: Temporal comparison analysis

"""

from typing import Any, Callable

from .analyzers import Analyzer, Base, Compare, Discovery, Tree
from .analyzers.finder import Finder
from .models.analyzer import AnalyzeInput, AnalyzeOptions, AnalyzeOutput
from .models.compare import CompareInput, CompareOptions, CompareOutput
from .models.discovery import DiscoverInput, DiscoverOptions, DiscoverOutput
from .models.finder import FindInput, FindOptions, FindOutput
from .models.tree import TreeInput, TreeOptions, TreeOutput


class Dataspot:
    """Advanced pattern analysis engine for discovering data concentrations and anomalies.

    The Dataspot class provides a comprehensive suite of analysis methods for
    identifying concentration patterns, building hierarchical data relationships,
    and detecting temporal changes in datasets. It's particularly useful for
    fraud detection, data quality monitoring, and exploratory data analysis.

    The engine processes structured data (dictionaries/records) and applies
    various analytical techniques to uncover hidden patterns and insights.
    All analysis methods support flexible filtering, preprocessing, and
    statistical configuration options.

    Attributes:
        _base (Base): Internal base analyzer containing shared preprocessing functions.

    Example:
        Complete workflow for analyzing e-commerce transaction data:

        >>> import pandas as pd
        >>> from dataspot import Dataspot
        >>> from dataspot.models.finder import FindInput, FindOptions
        >>> from dataspot.models.discovery import DiscoverInput, DiscoverOptions
        >>>
        >>> # Initialize analyzer
        >>> ds = Dataspot()
        >>>
        >>> # Add custom preprocessing for email domains
        >>> ds.add_preprocessor("email", lambda x: x.split("@")[1] if "@" in x else x)
        >>>
        >>> # Load transaction data
        >>> transactions = [
        ...     {"user_email": "john@gmail.com", "country": "US", "amount": 100},
        ...     {"user_email": "jane@gmail.com", "country": "US", "amount": 150},
        ...     {"user_email": "bob@suspicious.com", "country": "XX", "amount": 5000},
        ... ]
        >>>
        >>> # Find specific patterns
        >>> find_input = FindInput(data=transactions, fields=["user_email", "country"])
        >>> find_options = FindOptions(top=5, min_percentage=10.0)
        >>> patterns = ds.find(find_input, find_options)
        >>>
        >>> # Auto-discover interesting patterns
        >>> discover_input = DiscoverInput(data=transactions)
        >>> discover_options = DiscoverOptions(max_fields=2, min_percentage=15.0)
        >>> discoveries = ds.discover(discover_input, discover_options)
        >>>
        >>> print(f"Top discovered pattern: {discoveries.top_patterns[0].path}")
        >>>
        >>> # Example output:
        >>> # Found 3 concentration patterns
        >>> # Top discovered pattern: ['suspicious.com', 'XX']

    Notes:
        - All input data should be provided as lists of dictionaries
        - Field names in the data should be consistent across records
        - Missing values are handled gracefully during preprocessing
        - Results include statistical measures like percentages and counts

    """

    def __init__(self):
        """Initialize the Dataspot analysis engine.

        Creates a new instance with default preprocessing capabilities.
        Custom preprocessors can be added after initialization using
        the add_preprocessor method.
        """
        self._base = Base()

    def add_preprocessor(
        self, field_name: str, preprocessor: Callable[[Any], Any]
    ) -> None:
        """Add a custom preprocessing function for a specific field.

        Preprocessors are applied to field values before analysis, enabling
        data transformation, normalization, or cleaning. They're particularly
        useful for extracting features from complex data types or standardizing
        formats.

        Args:
            field_name (str): The name of the field to preprocess. Must match
                a field name present in the analysis data.
            preprocessor (Callable[[Any], Any]): A function that takes a field
                value and returns a transformed value. Should handle edge cases
                like None values gracefully.

        Example:
            Common preprocessing patterns:

            >>> ds = Dataspot()
            >>>
            >>> # Extract domain from email addresses
            >>> ds.add_preprocessor("email", lambda x: x.split("@")[1] if x and "@" in x else "unknown")
            >>>
            >>> # Normalize country codes to uppercase
            >>> ds.add_preprocessor("country", lambda x: x.upper() if x else "UNKNOWN")
            >>>
            >>> # Categorize amounts into ranges
            >>> def amount_category(amount):
            ...     if amount is None:
            ...         return "unknown"
            ...     elif amount < 100:
            ...         return "low"
            ...     elif amount < 1000:
            ...         return "medium"
            ...     else:
            ...         return "high"
            >>> ds.add_preprocessor("amount", amount_category)
            >>>
            >>> # After preprocessing, data like:
            >>> # {"email": "user@gmail.com", "country": "us", "amount": 150}
            >>> # Becomes:
            >>> # {"email": "gmail.com", "country": "US", "amount": "medium"}

        Notes:
            - Preprocessors are applied in the order they were added
            - The same preprocessor can be applied to multiple fields
            - Preprocessors should be idempotent and handle None/missing values
            - Changes affect all subsequent analysis operations

        """
        self._base.add_preprocessor(field_name, preprocessor)

    def find(
        self,
        input: FindInput,
        options: FindOptions,
    ) -> FindOutput:
        """Find concentration patterns in structured data.

        Analyzes the provided dataset to identify patterns where data concentrates
        around specific field value combinations. This is the core pattern discovery
        method, useful for identifying hotspots, anomalies, or frequently occurring
        combinations in your data.

        Args:
            input (FindInput): Input configuration containing:
                - data: List of dictionaries representing records to analyze
                - fields: List of field names to analyze for patterns
                - query: Optional dictionary for filtering records before analysis
            options (FindOptions): Analysis configuration containing:
                - top: Maximum number of patterns to return (default: 10)
                - min_percentage: Minimum percentage threshold for pattern inclusion
                - max_depth: Maximum depth for hierarchical pattern analysis
                - Other filtering and display options

        Returns:
            FindOutput: Analysis results containing:
                - patterns: List of discovered concentration patterns with statistics
                - metadata: Analysis metadata including total records processed
                - summary: High-level summary of findings

        Raises:
            ValueError: If input data is empty or fields don't exist in data
            TypeError: If data format is incorrect (not list of dictionaries)

        Example:
            Fraud detection in financial transactions:

            >>> from dataspot.models.finder import FindInput, FindOptions
            >>>
            >>> # Transaction data with potential fraud indicators
            >>> transactions = [
            ...     {"country": "US", "payment_method": "card", "amount": 100, "user_id": "user1"},
            ...     {"country": "US", "payment_method": "card", "amount": 150, "user_id": "user2"},
            ...     {"country": "US", "payment_method": "card", "amount": 200, "user_id": "user1"},
            ...     {"country": "XX", "payment_method": "crypto", "amount": 10000, "user_id": "user3"},
            ...     {"country": "XX", "payment_method": "crypto", "amount": 15000, "user_id": "user3"},
            ... ]
            >>>
            >>> # Focus on high-value transactions
            >>> input_data = FindInput(
            ...     data=transactions,
            ...     fields=["country", "payment_method"],
            ...     query={"amount": {"$gte": 1000}}  # Filter for amounts >= 1000
            ... )
            >>>
            >>> options = FindOptions(
            ...     top=5,
            ...     min_percentage=10.0,
            ...     include_stats=True
            ... )
            >>>
            >>> results = ds.find(input_data, options)
            >>>
            >>> # Analyze results
            >>> for pattern in results.patterns:
            ...     print(f"Pattern: {pattern.path}")
            ...     print(f"Count: {pattern.count} ({pattern.percentage:.1f}%)")
            ...     print(f"Concentration score: {pattern.concentration_score:.2f}")
            >>>
            >>> # Example output:
            >>> # Pattern: ['XX', 'crypto']
            >>> # Count: 2 (100.0%)
            >>> # Concentration score: 0.95

        Notes:
            - Patterns are ranked by concentration score and frequency
            - The query parameter supports MongoDB-style filtering
            - Results include statistical measures for pattern significance
            - Preprocessing functions are applied before pattern analysis

        """
        finder = Finder()
        finder.preprocessor_manager = self._base.preprocessor_manager
        return finder.execute(input, options)

    def analyze(
        self,
        input: AnalyzeInput,
        options: AnalyzeOptions,
    ) -> AnalyzeOutput:
        """Perform comprehensive analysis with detailed insights and statistics.

        Provides an enhanced analysis that combines pattern finding with detailed
        statistical analysis, data quality metrics, and actionable insights.
        This method is ideal when you need a complete understanding of your data's
        characteristics and potential issues.

        Args:
            input (AnalyzeInput): Input configuration containing:
                - data: List of dictionaries representing records to analyze
                - fields: List of field names to analyze for patterns
                - query: Optional dictionary for filtering records before analysis
            options (AnalyzeOptions): Analysis configuration containing:
                - top: Maximum number of patterns to return
                - min_percentage: Minimum percentage threshold for pattern inclusion
                - include_insights: Whether to generate actionable insights
                - statistical_tests: Whether to perform statistical significance tests
                - Other advanced analysis options

        Returns:
            AnalyzeOutput: Comprehensive analysis results containing:
                - patterns: Discovered concentration patterns with detailed statistics
                - insights: Actionable insights and recommendations
                - data_quality: Data quality metrics and anomaly detection results
                - statistics: Detailed statistical measures and distributions
                - metadata: Analysis metadata and configuration summary

        Example:
            Comprehensive analysis of user behavior data:

            >>> from dataspot.models.analyzer import AnalyzeInput, AnalyzeOptions
            >>>
            >>> # User behavior data
            >>> user_events = [
            ...     {"user_type": "premium", "device": "mobile", "action": "purchase", "value": 99.99},
            ...     {"user_type": "premium", "device": "desktop", "action": "browse", "value": 0},
            ...     {"user_type": "free", "device": "mobile", "action": "browse", "value": 0},
            ...     {"user_type": "free", "device": "mobile", "action": "signup", "value": 0},
            ... ]
            >>>
            >>> input_data = AnalyzeInput(
            ...     data=user_events,
            ...     fields=["user_type", "device", "action"]
            ... )
            >>>
            >>> options = AnalyzeOptions(
            ...     top=10,
            ...     min_percentage=5.0,
            ...     include_insights=True,
            ...     statistical_tests=True
            ... )
            >>>
            >>> results = ds.analyze(input_data, options)
            >>>
            >>> # Review insights
            >>> print("Key Insights:")
            >>> for insight in results.insights:
            ...     print(f"- {insight.description}")
            ...     print(f"  Confidence: {insight.confidence:.2f}")
            ...     print(f"  Recommendation: {insight.recommendation}")
            >>>
            >>> # Example output:
            >>> # Key Insights:
            >>> # - Premium users show 85% mobile device preference
            >>> #   Confidence: 0.92
            >>> #   Recommendation: Optimize mobile experience for premium users
            >>> # - Free users concentrate on mobile signup actions
            >>> #   Confidence: 0.87
            >>> #   Recommendation: Streamline mobile onboarding process

        Notes:
            - Analysis includes data quality assessment and anomaly detection
            - Insights are generated based on statistical patterns and business rules
            - Results provide confidence scores for recommendations
            - Suitable for exploratory data analysis and reporting

        """
        analyzer = Analyzer()
        analyzer.preprocessor_manager = self._base.preprocessor_manager
        return analyzer.execute(input, options)

    def tree(
        self,
        input: TreeInput,
        options: TreeOptions,
    ) -> TreeOutput:
        """Build hierarchical tree structure representing data relationships.

        Creates a tree-like representation of the data that shows how records
        are distributed across different field value combinations. This visualization
        is particularly useful for understanding data hierarchies, drill-down
        analysis, and identifying the most significant branches in your data.

        Args:
            input (TreeInput): Input configuration containing:
                - data: List of dictionaries representing records to analyze
                - fields: Ordered list of field names defining the tree hierarchy
                - query: Optional dictionary for filtering records before analysis
            options (TreeOptions): Tree building configuration containing:
                - top: Maximum number of branches per level
                - max_depth: Maximum tree depth to build
                - min_count: Minimum record count for branch inclusion
                - sort_by: Sorting criteria for branches ('count', 'percentage')
                - Other tree structure options

        Returns:
            TreeOutput: Hierarchical tree structure containing:
                - tree: Nested dictionary representing the tree structure
                - metadata: Tree statistics including total nodes and depth
                - leaf_patterns: Summary of leaf-level patterns
                - navigation: Helper data for tree traversal

        Example:
            Building a geographic-demographic tree for marketing analysis:

            >>> from dataspot.models.tree import TreeInput, TreeOptions
            >>>
            >>> # Customer data with geographic and demographic info
            >>> customers = [
            ...     {"country": "US", "state": "CA", "age_group": "25-34", "segment": "premium"},
            ...     {"country": "US", "state": "CA", "age_group": "35-44", "segment": "standard"},
            ...     {"country": "US", "state": "NY", "age_group": "25-34", "segment": "premium"},
            ...     {"country": "UK", "state": "London", "age_group": "25-34", "segment": "premium"},
            ... ]
            >>>
            >>> # Build tree: Country -> State -> Age Group -> Segment
            >>> input_data = TreeInput(
            ...     data=customers,
            ...     fields=["country", "state", "age_group", "segment"]
            ... )
            >>>
            >>> options = TreeOptions(
            ...     top=10,
            ...     max_depth=4,
            ...     min_count=1,
            ...     sort_by="count"
            ... )
            >>>
            >>> tree_result = ds.tree(input_data, options)
            >>>
            >>> # Navigate the tree structure
            >>> def print_tree(node, level=0):
            ...     indent = "  " * level
            ...     for key, value in node.items():
            ...         if isinstance(value, dict) and 'count' in value:
            ...             print(f"{indent}{key}: {value['count']} records")
            ...             if 'children' in value:
            ...                 print_tree(value['children'], level + 1)
            >>>
            >>> print_tree(tree_result.tree)
            >>>
            >>> # Example output:
            >>> # US: 3 records
            >>> #   CA: 2 records
            >>> #     25-34: 1 records
            >>> #       premium: 1 records
            >>> #     35-44: 1 records
            >>> #       standard: 1 records
            >>> #   NY: 1 records
            >>> #     25-34: 1 records
            >>> #       premium: 1 records
            >>> # UK: 1 records
            >>> #   London: 1 records
            >>> #     25-34: 1 records
            >>> #       premium: 1 records

        Notes:
            - Field order in the input determines tree hierarchy levels
            - Tree branches are sorted by count or percentage as specified
            - Supports pruning of low-count branches for cleaner visualization
            - Useful for creating drill-down interfaces and hierarchical reports

        """
        tree = Tree()
        tree.preprocessor_manager = self._base.preprocessor_manager
        return tree.execute(input, options)

    def discover(
        self,
        input: DiscoverInput,
        options: DiscoverOptions,
    ) -> DiscoverOutput:
        r"""Automatically discover the most interesting concentration patterns.

        Intelligently analyzes all available fields in the dataset to automatically
        identify the most significant concentration patterns and field combinations.
        This method is ideal for exploratory data analysis when you want to let
        the algorithm find the most interesting patterns without manual field
        selection.

        Args:
            input (DiscoverInput): Input configuration containing:
                - data: List of dictionaries representing records to analyze
                - query: Optional dictionary for filtering records before analysis
                - exclude_fields: Optional list of fields to exclude from discovery
            options (DiscoverOptions): Discovery configuration containing:
                - max_fields: Maximum number of fields to combine in patterns
                - min_percentage: Minimum percentage threshold for pattern significance
                - max_patterns: Maximum number of patterns to discover
                - field_importance_threshold: Minimum importance score for field inclusion
                - discovery_strategy: Algorithm strategy ('exhaustive', 'heuristic', 'adaptive')
                - Other discovery algorithm parameters

        Returns:
            DiscoverOutput: Discovery results containing:
                - top_patterns: Most significant patterns found across all field combinations
                - field_ranking: Ranked list of fields by their importance and contribution
                - field_combinations: Analysis of how well different field combinations work
                - discovery_insights: Insights about the discovery process and recommendations
                - metadata: Discovery statistics and algorithm performance metrics

        Example:
            Automatic pattern discovery in security logs:

            >>> from dataspot.models.discovery import DiscoverInput, DiscoverOptions
            >>>
            >>> # Security event logs with multiple attributes
            >>> security_logs = [
            ...     {"source_ip": "192.168.1.1", "user_agent": "Chrome", "endpoint": "/login", "status": "success"},
            ...     {"source_ip": "192.168.1.1", "user_agent": "Chrome", "endpoint": "/login", "status": "success"},
            ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "endpoint": "/admin", "status": "failed"},
            ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "endpoint": "/admin", "status": "failed"},
            ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "endpoint": "/login", "status": "failed"},
            ... ]
            >>>
            >>> input_data = DiscoverInput(
            ...     data=security_logs,
            ...     exclude_fields=["timestamp"]  # Exclude timestamp from pattern analysis
            ... )
            >>>
            >>> options = DiscoverOptions(
            ...     max_fields=3,
            ...     min_percentage=15.0,
            ...     max_patterns=10,
            ...     discovery_strategy="adaptive"
            ... )
            >>>
            >>> results = ds.discover(input_data, options)
            >>>
            >>> # Review discovered patterns
            >>> print("Top Discovered Patterns:")
            >>> for i, pattern in enumerate(results.top_patterns[:3], 1):
            ...     print(f"{i}. {pattern.path}")
            ...     print(f"   Count: {pattern.count} ({pattern.percentage:.1f}%)")
            ...     print(f"   Significance: {pattern.significance_score:.2f}")
            >>>
            >>> # Review field importance
            >>> print("\\nField Importance Ranking:")
            >>> for field, score in results.field_ranking.items():
            ...     print(f"- {field}: {score:.2f}")
            >>>
            >>> # Example output:
            >>> # Top Discovered Patterns:
            >>> # 1. ['10.0.0.1', 'Bot', 'failed']
            >>> #    Count: 3 (60.0%)
            >>> #    Significance: 0.89
            >>> # 2. ['192.168.1.1', 'Chrome', 'success']
            >>> #    Count: 2 (40.0%)
            >>> #    Significance: 0.75
            >>> #
            >>> # Field Importance Ranking:
            >>> # - source_ip: 0.85
            >>> # - user_agent: 0.78
            >>> # - status: 0.65
            >>> # - endpoint: 0.52

        Notes:
            - Discovery algorithms automatically test multiple field combinations
            - Results include significance scores to identify the most meaningful patterns
            - Field ranking helps identify which attributes are most informative
            - Supports different discovery strategies based on dataset size and complexity
            - Ideal for initial data exploration and feature selection

        """
        discovery = Discovery()
        discovery.preprocessor_manager = self._base.preprocessor_manager
        return discovery.execute(input, options)

    def compare(
        self,
        input: CompareInput,
        options: CompareOptions,
    ) -> CompareOutput:
        r"""Compare datasets to detect changes and anomalies between time periods.

        Performs sophisticated temporal analysis to identify significant changes
        between two datasets (typically representing different time periods).
        This method is essential for monitoring data drift, detecting anomalies,
        fraud pattern evolution, and understanding how patterns change over time.

        Args:
            input (CompareInput): Input configuration containing:
                - current_data: List of dictionaries representing recent/current period data
                - baseline_data: List of dictionaries representing baseline/previous period data
                - fields: List of field names to analyze for changes
                - query: Optional dictionary for filtering both datasets before comparison
            options (CompareOptions): Comparison configuration containing:
                - statistical_significance: Whether to perform statistical significance tests
                - change_threshold: Minimum change percentage to consider significant
                - confidence_level: Statistical confidence level for significance tests (0.95)
                - comparison_metrics: List of metrics to compute ('percentage', 'count', 'ratio')
                - alert_on_new_patterns: Whether to flag completely new patterns
                - Other statistical and filtering options

        Returns:
            CompareOutput: Comprehensive comparison results containing:
                - changes: Detailed list of significant changes between periods
                - new_patterns: Patterns that appear only in the current period
                - disappeared_patterns: Patterns that appear only in the baseline period
                - statistical_tests: Results of significance tests if enabled
                - trend_analysis: Trend direction and magnitude for each pattern
                - alerts: High-priority changes that may require attention
                - metadata: Comparison statistics and methodology details

        Example:
            Fraud detection comparison between months:

            >>> from dataspot.models.compare import CompareInput, CompareOptions
            >>>
            >>> # Previous month's transaction data
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
            ...     change_threshold=0.25,  # 25% change threshold
            ...     confidence_level=0.95,
            ...     alert_on_new_patterns=True
            ... )
            >>>
            >>> changes = ds.compare(input_data, options)
            >>>
            >>> # Review significant changes
            >>> print("Significant Changes Detected:")
            >>> for change in changes.changes:
            ...     if change.is_significant:
            ...         print(f"Pattern: {change.pattern}")
            ...         print(f"Change: {change.percentage_change:+.1f}%")
            ...         print(f"P-value: {change.p_value:.3f}")
            ...         print(f"Alert Level: {change.alert_level}")
            >>>
            >>> # Review new patterns (potential fraud indicators)
            >>> if changes.new_patterns:
            ...     print("\\nNew Patterns (Potential Fraud Indicators):")
            ...     for pattern in changes.new_patterns:
            ...         print(f"- {pattern.path}: {pattern.count} occurrences")
            >>>
            >>> # Example output:
            >>> # Significant Changes Detected:
            >>> # Pattern: ['US', 'card', 'low']
            >>> # Change: -66.7%
            >>> # P-value: 0.012
            >>> # Alert Level: medium
            >>> #
            >>> # New Patterns (Potential Fraud Indicators):
            >>> # - ['US', 'crypto', 'high']: 1 occurrences
            >>> # - ['XX', 'crypto', 'high']: 2 occurrences

        Notes:
            - Statistical significance testing helps distinguish real changes from noise
            - New patterns often indicate emerging fraud techniques or system changes
            - Change thresholds can be adjusted based on business requirements
            - Results include confidence intervals and p-values for statistical rigor
            - Ideal for continuous monitoring and alerting systems

        """
        compare = Compare()
        compare.preprocessor_manager = self._base.preprocessor_manager
        return compare.execute(input, options)
