"""Core pattern finder for discovering data concentration patterns and anomalies.

This module provides the `Finder` class, which implements the fundamental
pattern discovery algorithms for identifying concentration patterns in
structured datasets. It serves as the core engine for pattern detection
across the Dataspot library and is used by higher-level analyzers.

The finder specializes in detecting where data concentrates around specific
field value combinations, making it essential for anomaly detection, fraud
analysis, and business intelligence applications. It provides the foundation
for all pattern-based analysis in the library.

Key Features:
    - High-performance pattern extraction algorithms
    - Flexible filtering and sorting capabilities
    - Tree-based hierarchical pattern analysis
    - Configurable concentration thresholds
    - Memory-efficient processing for large datasets
    - Integration with preprocessing and filtering systems
    - Statistical pattern validation and scoring

Example:
    Basic fraud detection pattern finding:

    >>> from dataspot.analyzers.finder import Finder
    >>> from dataspot.models.finder import FindInput, FindOptions
    >>>
    >>> # Initialize the pattern finder
    >>> finder = Finder()
    >>>
    >>> # Financial transaction data
    >>> transactions = [
    ...     {"country": "US", "payment_method": "card", "amount": 100},
    ...     {"country": "US", "payment_method": "card", "amount": 150},
    ...     {"country": "XX", "payment_method": "crypto", "amount": 10000},
    ...     {"country": "XX", "payment_method": "crypto", "amount": 15000},
    ... ]
    >>>
    >>> input_data = FindInput(
    ...     data=transactions,
    ...     fields=["country", "payment_method"]
    ... )
    >>> options = FindOptions(min_percentage=25.0, sort_by="percentage")
    >>>
    >>> results = finder.execute(input_data, options)
    >>> print(f"Found {len(results.patterns)} suspicious patterns")
    >>>
    >>> # Example output:
    >>> # Found 2 suspicious patterns

Notes:
    The Finder class is designed for high-performance pattern extraction and
    serves as the foundation for more complex analysis operations. It supports
    preprocessing, filtering, and hierarchical pattern analysis for scalable
    data processing.

See Also:
    - analyzers.analyzer: Comprehensive statistical analysis with insights
    - analyzers.discovery: Automatic field combination discovery
    - analyzers.compare: Temporal pattern comparison analysis

"""

from typing import List

from ..models.finder import FindInput, FindOptions, FindOutput
from ..models.pattern import Pattern
from .base import Base
from .filters import PatternFilter
from .pattern_extractor import PatternExtractor


class Finder(Base):
    r"""Core pattern finder for discovering concentration patterns in structured data.

    The Finder class implements the fundamental pattern discovery algorithms
    that power the Dataspot library. It specializes in identifying where data
    concentrates around specific field value combinations, making it essential
    for fraud detection, anomaly analysis, and business intelligence applications.

    This class provides:
    - High-performance tree-based pattern extraction
    - Flexible filtering and threshold configuration
    - Hierarchical pattern analysis with configurable depth
    - Statistical pattern validation and scoring
    - Memory-efficient processing for large datasets
    - Integration with preprocessing and data transformation

    The finder serves as the core engine used by higher-level analyzers like
    Discovery, Compare, and Analyzer, providing the fundamental pattern
    detection capabilities that enable advanced analysis features.

    Attributes:
        Inherits all preprocessing capabilities from Base class.

    Example:
        Comprehensive security event analysis:

        >>> from dataspot.analyzers.finder import Finder
        >>> from dataspot.models.finder import FindInput, FindOptions
        >>>
        >>> # Security event logs
        >>> security_events = [
        ...     {"source_ip": "192.168.1.1", "user_agent": "Chrome", "status": "success"},
        ...     {"source_ip": "192.168.1.1", "user_agent": "Chrome", "status": "success"},
        ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "status": "failed"},
        ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "status": "failed"},
        ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "status": "failed"},
        ...     {"source_ip": "172.16.0.1", "user_agent": "Firefox", "status": "success"},
        ... ]
        >>>
        >>> finder = Finder()
        >>>
        >>> # Add preprocessing for IP classification
        >>> finder.add_preprocessor("source_ip",
        ...     lambda ip: "internal" if ip.startswith("192.168") or ip.startswith("172.16")
        ...     else "external")
        >>>
        >>> input_data = FindInput(
        ...     data=security_events,
        ...     fields=["source_ip", "user_agent", "status"]
        ... )
        >>>
        >>> options = FindOptions(
        ...     min_percentage=30.0,
        ...     sort_by="percentage",
        ...     reverse=True
        ... )
        >>>
        >>> results = finder.execute(input_data, options)
        >>>
        >>> print(f"Pattern Analysis Results:")
        >>> print(f"- Total records analyzed: {results.total_records}")
        >>> print(f"- Significant patterns found: {len(results.patterns)}")
        >>>
        >>> print(f"\\nTop Security Patterns:")
        >>> for i, pattern in enumerate(results.patterns[:3], 1):
        ...     print(f"{i}. {pattern.path}: {pattern.percentage:.1f}% ({pattern.count} events)")
        >>>
        >>> # Example output:
        >>> # Pattern Analysis Results:
        >>> # - Total records analyzed: 6
        >>> # - Significant patterns found: 4
        >>> #
        >>> # Top Security Patterns:
        >>> # 1. ['external', 'Bot', 'failed']: 50.0% (3 events)
        >>> # 2. ['internal', 'Chrome', 'success']: 33.3% (2 events)
        >>> # 3. ['external', 'Bot']: 50.0% (3 events)

    Notes:
        - Optimized for high-volume data processing with efficient algorithms
        - Pattern extraction uses hierarchical tree structures for performance
        - Supports complex filtering and sorting configurations
        - Integrates seamlessly with preprocessing and data transformation
        - Memory usage scales linearly with data size and pattern complexity

    """

    def execute(
        self,
        input: FindInput,
        options: FindOptions,
    ) -> FindOutput:
        r"""Execute core pattern finding analysis on structured data.

        Performs comprehensive pattern discovery to identify concentration
        patterns in the provided dataset. This is the primary method for
        pattern extraction and serves as the foundation for all pattern-based
        analysis in the Dataspot library.

        The analysis process includes:
        1. Data validation and preprocessing
        2. Query filtering and data preparation
        3. Hierarchical tree construction
        4. Pattern extraction and statistical analysis
        5. Advanced filtering and threshold application
        6. Sorting and result optimization

        Args:
            input (FindInput): Pattern finding input configuration containing:
                - data: List of dictionaries representing records to analyze
                - fields: List of field names to analyze for concentration patterns
                - query: Optional dictionary for filtering records before analysis
            options (FindOptions): Pattern finding configuration containing:
                - min_percentage: Minimum percentage threshold for pattern inclusion
                - max_percentage: Maximum percentage threshold for pattern filtering
                - min_count: Minimum record count for pattern inclusion
                - max_count: Maximum record count for pattern filtering
                - min_depth: Minimum depth level for hierarchical patterns
                - max_depth: Maximum depth level for hierarchical patterns
                - contains: List of values that patterns must contain
                - exclude: List of values that patterns must not contain
                - regex: Regular expression pattern for value matching
                - limit: Maximum number of patterns to return
                - sort_by: Field to sort results by ('percentage', 'count', 'depth')
                - reverse: Whether to sort in descending order

        Returns:
            FindOutput: Pattern finding results containing:
                - patterns: List of discovered patterns with statistical measures
                - total_records: Number of records processed after filtering
                - total_patterns: Number of patterns discovered

        Raises:
            ValueError: If input data is empty or malformed
            TypeError: If data format is incorrect (not list of dictionaries)
            KeyError: If specified fields don't exist in the data

        Example:
            E-commerce customer behavior analysis:

            >>> from dataspot.models.finder import FindInput, FindOptions
            >>>
            >>> # Customer purchase behavior data
            >>> customer_data = [
            ...     {"segment": "premium", "device": "mobile", "action": "purchase", "value": 299},
            ...     {"segment": "premium", "device": "mobile", "action": "purchase", "value": 199},
            ...     {"segment": "premium", "device": "desktop", "action": "browse", "value": 0},
            ...     {"segment": "standard", "device": "mobile", "action": "browse", "value": 0},
            ...     {"segment": "standard", "device": "mobile", "action": "browse", "value": 0},
            ...     {"segment": "free", "device": "mobile", "action": "signup", "value": 0},
            ... ]
            >>>
            >>> finder = Finder()
            >>>
            >>> # Focus on high-value customer behavior
            >>> input_data = FindInput(
            ...     data=customer_data,
            ...     fields=["segment", "device", "action"],
            ...     query={"value": {"$gte": 100}}  # High-value transactions only
            ... )
            >>>
            >>> options = FindOptions(
            ...     min_percentage=15.0,
            ...     sort_by="percentage",
            ...     reverse=True,
            ...     limit=10
            ... )
            >>>
            >>> results = finder.execute(input_data, options)
            >>>
            >>> # Analyze high-value customer patterns
            >>> print(f"High-Value Customer Analysis:")
            >>> print(f"- Records processed: {results.total_records}")
            >>> print(f"- Significant patterns: {len(results.patterns)}")
            >>>
            >>> print(f"\\nKey Behavior Patterns:")
            >>> for pattern in results.patterns:
            ...     print(f"- {pattern.path}: {pattern.percentage:.1f}% concentration")
            ...     print(f"  Count: {pattern.count} customers, Depth: {pattern.depth}")
            >>>
            >>> # Example output:
            >>> # High-Value Customer Analysis:
            >>> # - Records processed: 2
            >>> # - Significant patterns: 3
            >>> #
            >>> # Key Behavior Patterns:
            >>> # - ['premium', 'mobile', 'purchase']: 100.0% concentration
            >>> #   Count: 2 customers, Depth: 3
            >>> # - ['premium', 'mobile']: 100.0% concentration
            >>> #   Count: 2 customers, Depth: 2
            >>> # - ['premium']: 100.0% concentration
            >>> #   Count: 2 customers, Depth: 1

        Example:
            Fraud detection with advanced filtering:

            >>> # Suspicious transaction patterns
            >>> transactions = [
            ...     {"country": "US", "method": "card", "amount": 100, "time": "day"},
            ...     {"country": "US", "method": "card", "amount": 150, "time": "day"},
            ...     {"country": "XX", "method": "crypto", "amount": 10000, "time": "night"},
            ...     {"country": "XX", "method": "crypto", "amount": 15000, "time": "night"},
            ...     {"country": "XX", "method": "crypto", "amount": 20000, "time": "night"},
            ... ]
            >>>
            >>> finder = Finder()
            >>>
            >>> input_data = FindInput(
            ...     data=transactions,
            ...     fields=["country", "method", "time"]
            ... )
            >>>
            >>> # Focus on suspicious patterns
            >>> options = FindOptions(
            ...     min_percentage=40.0,
            ...     min_count=2,
            ...     sort_by="count",
            ...     reverse=True,
            ...     exclude=["day"]  # Focus on non-standard hours
            ... )
            >>>
            >>> results = finder.execute(input_data, options)
            >>>
            >>> print(f"Fraud Detection Analysis:")
            >>> print(f"- Total transactions: {results.total_records}")
            >>> print(f"- Suspicious patterns: {len(results.patterns)}")
            >>>
            >>> print(f"\\nSuspicious Activity Patterns:")
            >>> for pattern in results.patterns:
            ...     print(f"- Pattern: {pattern.path}")
            ...     print(f"  Risk Level: {pattern.percentage:.1f}% concentration")
            ...     print(f"  Occurrences: {pattern.count} transactions")
            >>>
            >>> # Example output:
            >>> # Fraud Detection Analysis:
            >>> # - Total transactions: 5
            >>> # - Suspicious patterns: 2
            >>> #
            >>> # Suspicious Activity Patterns:
            >>> # - Pattern: ['XX', 'crypto', 'night']
            >>> #   Risk Level: 60.0% concentration
            >>> #   Occurrences: 3 transactions
            >>> # - Pattern: ['XX', 'crypto']
            >>> #   Risk Level: 60.0% concentration
            >>> #   Occurrences: 3 transactions

        Notes:
            - Empty field lists return empty results gracefully
            - Query filtering is applied before pattern analysis for efficiency
            - Tree-based extraction provides O(n log n) performance characteristics
            - Sorting and filtering are optimized for large result sets
            - Preprocessing functions are applied before tree construction
            - Memory usage is optimized for large datasets through streaming processing

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
        r"""Sort patterns in-place by specified criteria for optimal result presentation.

        Provides flexible sorting capabilities to organize discovered patterns
        according to business priorities and analysis requirements. Supports
        multiple sorting criteria to enable different analysis perspectives
        and reporting needs.

        Args:
            patterns (List[Pattern]): List of pattern objects to sort in-place.
                Each pattern contains statistical measures and metadata.
            sort_by (str): Sorting criteria determining the order of results:
                - "percentage": Sort by concentration percentage (business impact)
                - "count": Sort by absolute count (volume significance)
                - "depth": Sort by pattern depth (complexity analysis)
            reverse (bool): Sort order direction. Default: True for descending order.
                - True: Highest values first (most significant patterns first)
                - False: Lowest values first (ascending order)

        Example:
            Sorting patterns for different analysis perspectives:

            >>> # Sample patterns for demonstration
            >>> patterns = [
            ...     MockPattern(percentage=45.0, count=90, depth=2),
            ...     MockPattern(percentage=75.0, count=30, depth=3),
            ...     MockPattern(percentage=60.0, count=120, depth=1),
            ... ]
            >>>
            >>> # Sort by business impact (percentage)
            >>> finder._sort_patterns(patterns, "percentage", reverse=True)
            >>> print("By Business Impact:")
            >>> for p in patterns:
            ...     print(f"- {p.percentage:.1f}% concentration")
            >>>
            >>> # Sort by volume significance (count)
            >>> finder._sort_patterns(patterns, "count", reverse=True)
            >>> print("\\nBy Volume:")
            >>> for p in patterns:
            ...     print(f"- {p.count} occurrences")
            >>>
            >>> # Sort by complexity (depth)
            >>> finder._sort_patterns(patterns, "depth", reverse=False)
            >>> print("\\nBy Complexity (ascending):")
            >>> for p in patterns:
            ...     print(f"- Depth {p.depth} pattern")
            >>>
            >>> # Example output:
            >>> # By Business Impact:
            >>> # - 75.0% concentration
            >>> # - 60.0% concentration
            >>> # - 45.0% concentration
            >>> #
            >>> # By Volume:
            >>> # - 120 occurrences
            >>> # - 90 occurrences
            >>> # - 30 occurrences
            >>> #
            >>> # By Complexity (ascending):
            >>> # - Depth 1 pattern
            >>> # - Depth 2 pattern
            >>> # - Depth 3 pattern

        Notes:
            - Sorting is performed in-place for memory efficiency
            - Default descending order prioritizes most significant patterns
            - Percentage sorting is ideal for business impact analysis
            - Count sorting highlights volume-based significance
            - Depth sorting enables complexity-based analysis
            - Invalid sort criteria are silently ignored for robustness

        """
        if sort_by == "percentage":
            patterns.sort(key=lambda p: p.percentage, reverse=reverse)
        elif sort_by == "count":
            patterns.sort(key=lambda p: p.count, reverse=reverse)
        elif sort_by == "depth":
            patterns.sort(key=lambda p: p.depth, reverse=reverse)
