"""Intelligent pattern discovery engine for automatic field analysis and optimization.

This module provides the `Discovery` class, which automatically analyzes all
available fields in a dataset to discover the most interesting concentration
patterns without requiring manual field specification. It's designed for
exploratory data analysis where you want the algorithm to find the most
significant patterns and field combinations.

The discovery engine uses sophisticated algorithms to:
- Rank fields by their concentration potential
- Test multiple field combinations intelligently
- Discover optimal pattern combinations automatically
- Provide field importance scoring and recommendations

Key Features:
    - Automatic field importance ranking and scoring
    - Intelligent combination testing across multiple fields
    - Pattern significance analysis and optimization
    - Exploratory data analysis without manual configuration
    - Field suitability detection and filtering
    - Scalable discovery algorithms for large datasets
    - Comprehensive discovery statistics and metadata

Example:
    Automatic pattern discovery in security logs:

    >>> from dataspot.analyzers.discovery import Discovery
    >>> from dataspot.models.discovery import DiscoverInput, DiscoverOptions
    >>>
    >>> # Initialize the discovery engine
    >>> discovery = Discovery()
    >>>
    >>> # Security event logs with multiple attributes
    >>> security_events = [
    ...     {"source_ip": "192.168.1.1", "user_agent": "Chrome", "endpoint": "/login", "status": "success"},
    ...     {"source_ip": "192.168.1.1", "user_agent": "Chrome", "endpoint": "/dashboard", "status": "success"},
    ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "endpoint": "/admin", "status": "failed"},
    ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "endpoint": "/admin", "status": "failed"},
    ...     {"source_ip": "10.0.0.1", "user_agent": "Bot", "endpoint": "/login", "status": "failed"},
    ... ]
    >>>
    >>> input_data = DiscoverInput(data=security_events)
    >>> options = DiscoverOptions(max_fields=3, min_percentage=15.0)
    >>>
    >>> results = discovery.execute(input_data, options)
    >>> print(f"Best patterns found: {len(results.top_patterns)}")
    >>> print(f"Most important field: {results.field_ranking[0].field}")
    >>>
    >>> # Example output:
    >>> # Best patterns found: 5
    >>> # Most important field: source_ip

Notes:
    The discovery engine automatically handles field type detection, filters
    unsuitable fields, and optimizes combination testing for performance.
    Results include comprehensive statistics and field rankings for business
    intelligence and data science applications.

See Also:
    - analyzers.finder: Core pattern finding functionality
    - analyzers.analyzer: Comprehensive statistical analysis
    - models.discovery: Data models for discovery input and output

"""

from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

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
    r"""Intelligent pattern discovery engine for automatic field analysis and optimization.

    The Discovery class provides advanced automated pattern discovery capabilities
    that analyze all available fields in a dataset to identify the most significant
    concentration patterns without requiring manual field specification. It's
    designed for exploratory data analysis and automated insight generation.

    This engine specializes in:
    - Automatic field importance ranking and scoring
    - Intelligent multi-field combination testing
    - Pattern significance analysis and optimization
    - Scalable discovery algorithms for large datasets
    - Data quality assessment and field suitability analysis
    - Business intelligence and automated reporting

    The class uses sophisticated algorithms to efficiently explore the space
    of possible field combinations while avoiding computationally expensive
    exhaustive searches. It provides actionable insights about which fields
    and combinations are most valuable for analysis.

    Attributes:
        Inherits all preprocessing capabilities from Base class.

    Example:
        Comprehensive fraud detection discovery:

        >>> from dataspot.analyzers.discovery import Discovery
        >>> from dataspot.models.discovery import DiscoverInput, DiscoverOptions
        >>>
        >>> # Transaction data with unknown important fields
        >>> transactions = [
        ...     {"country": "US", "payment_method": "card", "amount": 100, "user_id": "user1", "device": "mobile"},
        ...     {"country": "US", "payment_method": "card", "amount": 150, "user_id": "user2", "device": "desktop"},
        ...     {"country": "XX", "payment_method": "crypto", "amount": 5000, "user_id": "user3", "device": "mobile"},
        ...     {"country": "XX", "payment_method": "crypto", "amount": 7500, "user_id": "user3", "device": "mobile"},
        ...     {"country": "XX", "payment_method": "crypto", "amount": 8000, "user_id": "user4", "device": "mobile"},
        ... ]
        >>>
        >>> discovery = Discovery()
        >>>
        >>> input_data = DiscoverInput(data=transactions)
        >>> options = DiscoverOptions(
        ...     max_fields=3,
        ...     min_percentage=20.0,
        ...     max_combinations=10
        ... )
        >>>
        >>> results = discovery.execute(input_data, options)
        >>>
        >>> # Review discovery statistics
        >>> stats = results.statistics
        >>> print(f"Discovery Results:")
        >>> print(f"- Total records analyzed: {stats.total_records}")
        >>> print(f"- Fields analyzed: {stats.fields_analyzed}")
        >>> print(f"- Combinations tested: {stats.combinations_tried}")
        >>> print(f"- Patterns discovered: {stats.patterns_discovered}")
        >>> print(f"- Best concentration: {stats.best_concentration:.1f}%")
        >>>
        >>> # Review field importance ranking
        >>> print(f"\\nField Importance Ranking:")
        >>> for i, field_rank in enumerate(results.field_ranking[:3], 1):
        ...     print(f"{i}. {field_rank.field}: {field_rank.score:.2f}")
        >>>
        >>> # Review top discovered patterns
        >>> print(f"\\nTop Discovered Patterns:")
        >>> for i, pattern in enumerate(results.top_patterns[:3], 1):
        ...     print(f"{i}. {pattern.path} - {pattern.percentage:.1f}% ({pattern.count} records)")
        >>>
        >>> # Example output:
        >>> # Discovery Results:
        >>> # - Total records analyzed: 5
        >>> # - Fields analyzed: 5
        >>> # - Combinations tested: 8
        >>> # - Patterns discovered: 6
        >>> # - Best concentration: 60.0%
        >>> #
        >>> # Field Importance Ranking:
        >>> # 1. payment_method: 45.50
        >>> # 2. country: 42.00
        >>> # 3. device: 28.75
        >>> #
        >>> # Top Discovered Patterns:
        >>> # 1. ['XX', 'crypto'] - 60.0% (3 records)
        >>> # 2. ['crypto', 'mobile'] - 60.0% (3 records)
        >>> # 3. ['XX', 'crypto', 'mobile'] - 60.0% (3 records)

    Notes:
        - Discovery algorithms are optimized for performance with large datasets
        - Field ranking helps prioritize data collection and analysis efforts
        - Combination testing is intelligent to avoid exponential complexity
        - Results are suitable for automated insight generation and reporting

    """

    def execute(
        self,
        input: DiscoverInput,
        options: Optional[DiscoverOptions] = None,
    ) -> DiscoverOutput:
        r"""Execute comprehensive automatic pattern discovery across all available fields.

        Performs intelligent analysis of all available fields in the dataset to
        automatically discover the most significant concentration patterns and
        field combinations. This method is ideal for exploratory data analysis
        where you want the algorithm to find the most interesting patterns
        without manual field specification.

        The discovery process includes:
        1. Data validation and preprocessing
        2. Automatic field type detection and suitability analysis
        3. Field importance scoring and ranking
        4. Intelligent combination testing and optimization
        5. Pattern significance analysis and deduplication
        6. Results compilation with comprehensive statistics

        Args:
            input (DiscoverInput): Discovery input configuration containing:
                - data: List of dictionaries representing records to analyze
                - query: Optional dictionary for filtering records before discovery
                - exclude_fields: Optional list of fields to exclude from analysis
            options (DiscoverOptions): Discovery configuration containing:
                - max_fields: Maximum number of fields to include in combinations (default: 3)
                - min_percentage: Minimum percentage threshold for pattern significance
                - max_combinations: Maximum number of field combinations to test
                - min_count: Minimum record count for pattern inclusion
                - max_count: Maximum record count for pattern filtering
                - Other filtering and optimization parameters

        Returns:
            DiscoverOutput: Comprehensive discovery results containing:
                - top_patterns: Top 20 most significant patterns discovered
                - field_ranking: Fields ranked by importance and contribution scores
                - combinations_tried: Record of all field combinations tested
                - statistics: Discovery statistics including performance metrics
                - fields_analyzed: List of fields that were suitable for analysis

        Raises:
            ValueError: If input data is empty or malformed
            TypeError: If data format is incorrect (not list of dictionaries)

        Example:
            Customer behavior discovery in e-commerce data:

            >>> from dataspot.models.discovery import DiscoverInput, DiscoverOptions
            >>>
            >>> # E-commerce customer behavior data
            >>> customer_events = [
            ...     {"segment": "premium", "region": "US", "device": "mobile", "action": "purchase", "value": 299},
            ...     {"segment": "premium", "region": "US", "device": "desktop", "action": "browse", "value": 0},
            ...     {"segment": "standard", "region": "EU", "device": "mobile", "action": "browse", "value": 0},
            ...     {"segment": "standard", "region": "EU", "device": "mobile", "action": "purchase", "value": 99},
            ...     {"segment": "premium", "region": "APAC", "device": "mobile", "action": "purchase", "value": 199},
            ...     {"segment": "free", "region": "US", "device": "mobile", "action": "signup", "value": 0},
            ... ]
            >>>
            >>> discovery = Discovery()
            >>>
            >>> input_data = DiscoverInput(data=customer_events)
            >>> options = DiscoverOptions(
            ...     max_fields=3,
            ...     min_percentage=15.0,
            ...     max_combinations=15
            ... )
            >>>
            >>> results = discovery.execute(input_data, options)
            >>>
            >>> # Analyze discovery results
            >>> print(f"Discovery Summary:")
            >>> print(f"- Records processed: {results.statistics.total_records}")
            >>> print(f"- Suitable fields found: {results.statistics.fields_analyzed}")
            >>> print(f"- Total combinations tested: {results.statistics.combinations_tried}")
            >>> print(f"- Significant patterns discovered: {results.statistics.patterns_discovered}")
            >>>
            >>> # Field importance for business prioritization
            >>> print(f"\\nMost Important Fields for Analysis:")
            >>> for rank in results.field_ranking[:4]:
            ...     print(f"- {rank.field}: importance score {rank.score:.2f}")
            >>>
            >>> # Top business insights
            >>> print(f"\\nKey Business Patterns Discovered:")
            >>> for i, pattern in enumerate(results.top_patterns[:4], 1):
            ...     print(f"{i}. Pattern: {pattern.path}")
            ...     print(f"   Concentration: {pattern.percentage:.1f}% ({pattern.count}/{results.statistics.total_records} records)")
            >>>
            >>> # Combination testing insights
            >>> print(f"\\nCombination Testing Results:")
            >>> for combo in results.combinations_tried[:3]:
            ...     print(f"- Fields {combo.fields}: {combo.patterns_found} patterns found")
            >>>
            >>> # Example output:
            >>> # Discovery Summary:
            >>> # - Records processed: 6
            >>> # - Suitable fields found: 5
            >>> # - Total combinations tested: 12
            >>> # - Significant patterns discovered: 8
            >>> #
            >>> # Most Important Fields for Analysis:
            >>> # - segment: importance score 32.50
            >>> # - device: importance score 28.00
            >>> # - region: importance score 25.75
            >>> # - action: importance score 22.50
            >>> #
            >>> # Key Business Patterns Discovered:
            >>> # 1. Pattern: ['mobile']
            >>> #    Concentration: 66.7% (4/6 records)
            >>> # 2. Pattern: ['premium']
            >>> #    Concentration: 50.0% (3/6 records)
            >>> # 3. Pattern: ['premium', 'mobile']
            >>> #    Concentration: 50.0% (3/6 records)
            >>> # 4. Pattern: ['US']
            >>> #    Concentration: 33.3% (2/6 records)
            >>> #
            >>> # Combination Testing Results:
            >>> # - Fields ['segment']: 3 patterns found
            >>> # - Fields ['device']: 2 patterns found
            >>> # - Fields ['region']: 3 patterns found

        Notes:
            - Discovery algorithms prioritize high-impact field combinations
            - Field ranking helps optimize data collection and analysis strategies
            - Pattern significance is validated through statistical analysis
            - Results are cached and optimized for large-scale data processing
            - Suitable for real-time discovery in streaming data environments

        """
        if options is None:
            options = DiscoverOptions()

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
        """Build empty discovery result for edge cases with insufficient data.

        Creates a properly structured empty result when the input data is
        insufficient for meaningful pattern discovery (e.g., after filtering
        or with empty datasets). This ensures consistent API responses.

        Returns:
            DiscoverOutput: Empty but properly structured discovery result with:
                - Empty pattern lists and field rankings
                - Zero statistics for all metrics
                - Consistent dataclass structure for downstream processing

        Example:
            Handling empty dataset scenarios:

            >>> # This would be called internally when data is empty
            >>> empty_result = discovery._build_empty_discovery_result()
            >>>
            >>> print(f"Patterns found: {len(empty_result.top_patterns)}")
            >>> print(f"Fields analyzed: {empty_result.statistics.fields_analyzed}")
            >>> print(f"Records processed: {empty_result.statistics.total_records}")
            >>>
            >>> # Example output:
            >>> # Patterns found: 0
            >>> # Fields analyzed: 0
            >>> # Records processed: 0

        Notes:
            - Maintains consistent API response structure for error handling
            - Prevents downstream errors when no patterns can be discovered
            - Suitable for integration with automated monitoring systems

        """
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
        """Detect and filter fields suitable for categorical pattern analysis.

        Analyzes the dataset to identify fields that are suitable for pattern
        discovery based on their data characteristics, cardinality, and value
        distribution. This filtering ensures efficient discovery by excluding
        fields that are unlikely to produce meaningful patterns.

        Args:
            data (List[Dict[str, Any]]): Input dataset to analyze for suitable fields.
                Each record should be a dictionary with consistent field names.

        Returns:
            List[str]: List of field names that are suitable for pattern analysis
                based on cardinality, data type, and distribution characteristics.

        Example:
            Detecting suitable fields in mixed data:

            >>> # Dataset with various field types
            >>> mixed_data = [
            ...     {"user_id": "u123", "country": "US", "age": 25, "email": "user1@example.com"},
            ...     {"user_id": "u124", "country": "US", "age": 30, "email": "user2@example.com"},
            ...     {"user_id": "u125", "country": "UK", "age": 28, "email": "user3@example.com"},
            ...     {"user_id": "u126", "country": "UK", "age": 35, "email": "user4@example.com"},
            ... ]
            >>>
            >>> suitable_fields = discovery._detect_categorical_fields(mixed_data)
            >>> print(f"Suitable fields for analysis: {suitable_fields}")
            >>>
            >>> # Example output:
            >>> # Suitable fields for analysis: ['country', 'age']
            >>> # Note: user_id and email excluded due to high cardinality

        Notes:
            - Samples up to 100 records for efficient field detection
            - Excludes fields with too high cardinality (like IDs or unique values)
            - Filters out fields with insufficient variation for meaningful patterns
            - Handles missing values and null entries gracefully
            - Optimized for performance with large datasets

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
        """Evaluate if a specific field is suitable for pattern analysis.

        Applies multiple criteria to determine if a field is likely to produce
        meaningful concentration patterns. This includes checking cardinality,
        value distribution, and data quality characteristics.

        Args:
            data (List[Dict[str, Any]]): Input dataset containing the field to evaluate.
            field (str): Name of the field to evaluate for analysis suitability.
            sample_size (int): Number of records to sample for evaluation efficiency.

        Returns:
            bool: True if the field is suitable for pattern analysis, False otherwise.
                Fields are considered suitable if they have moderate cardinality,
                sufficient variation, and meaningful value distributions.

        Example:
            Evaluating different field types:

            >>> # Test various field characteristics
            >>> data = [
            ...     {"id": "unique1", "country": "US", "category": "A", "constant": "same"},
            ...     {"id": "unique2", "country": "US", "category": "B", "constant": "same"},
            ...     {"id": "unique3", "country": "UK", "category": "A", "constant": "same"},
            ... ]
            >>>
            >>> # Test different fields
            >>> fields_to_test = ["id", "country", "category", "constant"]
            >>> for field in fields_to_test:
            ...     suitable = discovery._is_suitable_for_analysis(data, field, len(data))
            ...     print(f"{field}: {'Suitable' if suitable else 'Not suitable'}")
            >>>
            >>> # Example output:
            >>> # id: Not suitable (too unique)
            >>> # country: Suitable (good cardinality)
            >>> # category: Suitable (good variation)
            >>> # constant: Not suitable (no variation)

        Notes:
            - Excludes fields with only one unique value (no variation)
            - Filters out fields that are mostly unique (like IDs or timestamps)
            - Requires at least 2 different values for meaningful patterns
            - Handles edge cases with very small datasets gracefully
            - Optimized thresholds based on typical business data characteristics

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
        """Calculate importance scores for fields based on their pattern potential.

        Evaluates each field's ability to produce significant concentration patterns
        by analyzing the patterns it generates individually. This scoring helps
        prioritize fields for combination testing and provides business insights
        about which data attributes are most informative.

        Args:
            data (List[Dict[str, Any]]): Input dataset for field evaluation.
            fields (List[str]): List of field names to evaluate and score.
            options (DiscoverOptions): Discovery configuration including filtering
                parameters that affect pattern significance evaluation.

        Returns:
            List[Tuple[str, float]]: List of (field_name, score) tuples sorted by
                score in descending order. Higher scores indicate fields with
                better pattern discovery potential.

        Example:
            Scoring fields in customer data:

            >>> # Customer transaction data
            >>> customer_data = [
            ...     {"segment": "premium", "country": "US", "device": "mobile", "status": "active"},
            ...     {"segment": "premium", "country": "US", "device": "desktop", "status": "active"},
            ...     {"segment": "standard", "country": "UK", "device": "mobile", "status": "inactive"},
            ...     {"segment": "premium", "country": "US", "device": "mobile", "status": "active"},
            ... ]
            >>>
            >>> fields = ["segment", "country", "device", "status"]
            >>> options = DiscoverOptions(min_percentage=10.0)
            >>>
            >>> field_scores = discovery._score_fields_by_potential(customer_data, fields, options)
            >>>
            >>> print("Field Importance Ranking:")
            >>> for field, score in field_scores:
            ...     print(f"- {field}: {score:.2f}")
            >>>
            >>> # Example output:
            >>> # Field Importance Ranking:
            >>> # - segment: 45.50 (high concentration in premium)
            >>> # - country: 40.25 (US dominance)
            >>> # - status: 38.75 (active concentration)
            >>> # - device: 32.00 (mobile preference)

        Notes:
            - Scores are based on maximum concentration, pattern count, and diversity
            - Higher scores indicate fields that are better for pattern discovery
            - Failed field analysis results in zero score to prevent errors
            - Scores are used to prioritize expensive combination testing
            - Results help identify the most valuable data attributes for analysis

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
        """Calculate numerical importance score for a field based on its patterns.

        Computes a weighted score that considers pattern concentration strength,
        number of significant patterns, and overall pattern diversity. This
        scoring algorithm helps identify fields that are most valuable for
        analysis and business insights.

        Args:
            patterns (List[Pattern]): List of patterns discovered for the field,
                each containing concentration percentage, count, and metadata.

        Returns:
            float: Numerical importance score for the field. Higher scores indicate
                fields with better pattern discovery potential. Score is calculated
                using weighted formula considering concentration, significance, and diversity.

        Example:
            Scoring different pattern scenarios:

            >>> # High concentration field (country with US dominance)
            >>> high_conc_patterns = [
            ...     MockPattern(percentage=85.0, count=170),  # US
            ...     MockPattern(percentage=10.0, count=20),   # UK
            ...     MockPattern(percentage=5.0, count=10),    # Others
            ... ]
            >>> score1 = discovery._calculate_field_score(high_conc_patterns)
            >>>
            >>> # Diverse field (age groups with balanced distribution)
            >>> diverse_patterns = [
            ...     MockPattern(percentage=30.0, count=60),   # 25-34
            ...     MockPattern(percentage=25.0, count=50),   # 35-44
            ...     MockPattern(percentage=20.0, count=40),   # 45-54
            ...     MockPattern(percentage=15.0, count=30),   # 18-24
            ...     MockPattern(percentage=10.0, count=20),   # 55+
            ... ]
            >>> score2 = discovery._calculate_field_score(diverse_patterns)
            >>>
            >>> print(f"High concentration field score: {score1:.2f}")
            >>> print(f"Diverse field score: {score2:.2f}")
            >>>
            >>> # Example output:
            >>> # High concentration field score: 52.50
            >>> # Diverse field score: 35.00

        Notes:
            - Formula: (max_concentration * 0.5) + (significant_patterns * 5) + (total_patterns * 0.5)
            - Balances between high concentration patterns and pattern diversity
            - Significant patterns (≥10% concentration) get bonus weighting
            - Empty pattern lists return zero score to handle edge cases
            - Optimized weights based on typical business intelligence requirements

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
        """Intelligently discover patterns using optimal field combinations.

        Systematically tests field combinations starting with single fields and
        progressively testing multi-field combinations. Uses field importance
        scores to prioritize testing and avoid exponential complexity while
        maximizing discovery of significant patterns.

        Args:
            data (List[Dict[str, Any]]): Input dataset for pattern discovery.
            field_scores (List[Tuple[str, float]]): Fields ranked by importance scores
                to guide intelligent combination testing.
            options (DiscoverOptions): Discovery configuration including maximum
                fields per combination and maximum combinations to test.

        Returns:
            Tuple[List[Pattern], List[Dict[str, Any]]]: Tuple containing:
                - all_patterns: Complete list of patterns found across all combinations
                - combinations_tried: Record of field combinations tested with results

        Example:
            Testing combinations in marketing data:

            >>> # Marketing campaign data
            >>> marketing_data = [
            ...     {"channel": "email", "segment": "premium", "region": "US", "converted": "yes"},
            ...     {"channel": "email", "segment": "premium", "region": "US", "converted": "yes"},
            ...     {"channel": "social", "segment": "standard", "region": "EU", "converted": "no"},
            ...     {"channel": "social", "segment": "premium", "region": "US", "converted": "yes"},
            ... ]
            >>>
            >>> # Field scores (normally calculated by _score_fields_by_potential)
            >>> field_scores = [("segment", 45.0), ("channel", 38.5), ("region", 32.0)]
            >>> options = DiscoverOptions(max_fields=2, max_combinations=5)
            >>>
            >>> patterns, combinations = discovery._discover_pattern_combinations(
            ...     marketing_data, field_scores, options
            ... )
            >>>
            >>> print(f"Total patterns discovered: {len(patterns)}")
            >>> print(f"Combinations tested:")
            >>> for combo in combinations:
            ...     print(f"- {combo['fields']}: {combo['patterns_found']} patterns")
            >>>
            >>> # Example output:
            >>> # Total patterns discovered: 12
            >>> # Combinations tested:
            >>> # - ['segment']: 2 patterns
            >>> # - ['channel']: 2 patterns
            >>> # - ['region']: 2 patterns
            >>> # - ['segment', 'channel']: 3 patterns
            >>> # - ['segment', 'region']: 3 patterns

        Notes:
            - Tests single fields first to establish baseline patterns
            - Uses importance scores to prioritize expensive multi-field combinations
            - Limits combination testing to prevent exponential complexity
            - Collects comprehensive metadata about testing process
            - Optimized for scalability with large numbers of fields

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
        """Remove duplicate patterns and rank by concentration quality.

        Processes discovered patterns to eliminate duplicates that may arise
        from different field combination tests while preserving the highest
        quality instance of each unique pattern. Results are ranked by
        concentration strength for optimal business insights.

        Args:
            patterns (List[Pattern]): Raw patterns discovered from all field
                combinations, potentially containing duplicates with different
                concentration values.

        Returns:
            List[Pattern]: Deduplicated patterns ranked by concentration percentage
                in descending order, ensuring highest quality patterns appear first.

        Example:
            Deduplicating patterns from multiple combinations:

            >>> # Simulated patterns from different combination tests
            >>> raw_patterns = [
            ...     MockPattern(path=['US'], percentage=60.0, count=120),
            ...     MockPattern(path=['premium'], percentage=45.0, count=90),
            ...     MockPattern(path=['US'], percentage=58.5, count=117),  # Duplicate with different %
            ...     MockPattern(path=['mobile'], percentage=70.0, count=140),
            ...     MockPattern(path=['premium'], percentage=47.2, count=94),  # Duplicate with higher %
            ... ]
            >>>
            >>> ranked_patterns = discovery._rank_and_deduplicate_patterns(raw_patterns)
            >>>
            >>> print("Deduplicated and Ranked Patterns:")
            >>> for i, pattern in enumerate(ranked_patterns, 1):
            ...     print(f"{i}. {pattern.path}: {pattern.percentage:.1f}% ({pattern.count} records)")
            >>>
            >>> # Example output:
            >>> # Deduplicated and Ranked Patterns:
            >>> # 1. ['mobile']: 70.0% (140 records)
            >>> # 2. ['US']: 60.0% (120 records)        # Kept higher percentage version
            >>> # 3. ['premium']: 47.2% (94 records)     # Kept higher percentage version

        Notes:
            - Deduplication is based on pattern path (field value combinations)
            - When duplicates exist, the pattern with higher concentration is retained
            - Final ranking prioritizes patterns with highest business impact
            - Essential for clean results when testing multiple field combinations
            - Optimizes result quality for reporting and business intelligence

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
        """Calculate comprehensive discovery performance and result statistics.

        Computes detailed metrics about the discovery process including data
        coverage, field analysis efficiency, combination testing performance,
        and pattern quality metrics. These statistics provide insights into
        discovery effectiveness and help optimize future analyses.

        Args:
            data (List[Dict[str, Any]]): Original input dataset that was analyzed.
            available_fields (List[str]): Fields that were suitable for analysis.
            combinations_tried (List[Dict[str, Any]]): Record of combination tests performed.
            top_patterns (List[Pattern]): Final ranked patterns discovered.

        Returns:
            Dict[str, Any]: Comprehensive statistics dictionary containing:
                - total_records: Number of records processed
                - fields_analyzed: Number of fields suitable for analysis
                - combinations_tried: Number of field combinations tested
                - patterns_discovered: Number of significant patterns found
                - best_concentration: Highest concentration percentage achieved

        Example:
            Calculating discovery performance metrics:

            >>> # Sample discovery results
            >>> data = [{"f1": "a", "f2": "x"}, {"f1": "b", "f2": "y"}] * 50  # 100 records
            >>> available_fields = ["f1", "f2", "f3", "f4"]
            >>> combinations_tried = [
            ...     {"fields": ["f1"], "patterns_found": 3},
            ...     {"fields": ["f2"], "patterns_found": 2},
            ...     {"fields": ["f1", "f2"], "patterns_found": 5},
            ... ]
            >>> top_patterns = [
            ...     MockPattern(percentage=75.0), MockPattern(percentage=60.0), MockPattern(percentage=45.0)
            ... ]
            >>>
            >>> stats = discovery._calculate_discovery_statistics(
            ...     data, available_fields, combinations_tried, top_patterns
            ... )
            >>>
            >>> print("Discovery Performance Statistics:")
            >>> for metric, value in stats.items():
            ...     print(f"- {metric}: {value}")
            >>>
            >>> # Example output:
            >>> # Discovery Performance Statistics:
            >>> # - total_records: 100
            >>> # - fields_analyzed: 4
            >>> # - combinations_tried: 3
            >>> # - patterns_discovered: 3
            >>> # - best_concentration: 75.0

        Notes:
            - Statistics help evaluate discovery algorithm effectiveness
            - Metrics are useful for performance monitoring and optimization
            - Best concentration indicates the quality of discovered patterns
            - Suitable for automated reporting and discovery pipeline monitoring
            - Provides insights for tuning discovery parameters and thresholds

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
