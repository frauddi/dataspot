"""Advanced hierarchical tree analyzer for building interactive visualization structures.

This module provides the `Tree` class, which specializes in converting pattern
analysis results into clean, hierarchical JSON tree structures optimized for
modern visualization frameworks and interactive dashboards. It serves as the
bridge between pattern analysis and user-facing visualizations.

The tree analyzer combines pattern extraction with sophisticated tree building
algorithms to create navigation-ready hierarchical structures that maintain
statistical accuracy while optimizing for user experience and performance.

Key Features:
    - Clean JSON tree generation for visualization frameworks
    - Hierarchical data organization with statistical preservation
    - Interactive navigation structure with depth control
    - Performance optimization for real-time dashboards
    - Statistical metadata integration for business intelligence
    - Configurable filtering and tree pruning capabilities
    - Framework-agnostic JSON output for universal compatibility

Example:
    Building interactive customer segmentation tree:

    >>> from dataspot.analyzers.tree import Tree
    >>> from dataspot.models.tree import TreeInput, TreeOptions
    >>>
    >>> # Initialize the tree analyzer
    >>> tree_analyzer = Tree()
    >>>
    >>> # Customer segmentation data
    >>> customers = [
    ...     {"segment": "enterprise", "region": "north_america", "industry": "technology"},
    ...     {"segment": "enterprise", "region": "north_america", "industry": "finance"},
    ...     {"segment": "smb", "region": "europe", "industry": "retail"},
    ...     {"segment": "smb", "region": "europe", "industry": "technology"},
    ... ]
    >>>
    >>> input_data = TreeInput(
    ...     data=customers,
    ...     fields=["segment", "region", "industry"]
    ... )
    >>> options = TreeOptions(top=5, min_count=1)
    >>>
    >>> tree_result = tree_analyzer.execute(input_data, options)
    >>> print(f"Tree structure: {len(tree_result.children)} main segments")
    >>>
    >>> # Example output:
    >>> # Tree structure: 2 main segments

Notes:
    The Tree analyzer is optimized for interactive visualizations and provides
    clean JSON structures compatible with D3.js, Chart.js, and other modern
    visualization frameworks. All statistical measures are preserved during
    tree construction for accurate business intelligence reporting.

See Also:
    - analyzers.finder: Core pattern finding functionality
    - analyzers.pattern_extractor: Pattern extraction and tree building utilities
    - models.tree: Tree data structures and configuration models

"""

from typing import Any, Dict, List, Optional

from ..models.tree import TreeInput, TreeNode, TreeOptions, TreeOutput, TreeStatistics
from .base import Base
from .filters import PatternFilter, TreeFilter
from .pattern_extractor import PatternExtractor, TreeBuilder


class Tree(Base):
    r"""Advanced hierarchical tree analyzer for interactive visualization and reporting.

    The Tree class provides sophisticated algorithms for converting pattern analysis
    results into clean, hierarchical JSON tree structures optimized for modern
    visualization frameworks and business intelligence dashboards. It specializes
    in creating navigation-ready structures that maintain statistical accuracy
    while optimizing for user experience and performance.

    This analyzer specializes in:
    - Clean JSON tree generation for visualization frameworks
    - Hierarchical data organization with statistical preservation
    - Interactive navigation structures with configurable depth
    - Performance optimization for real-time dashboard applications
    - Statistical metadata integration for business intelligence
    - Framework-agnostic output compatible with modern libraries

    The class serves as the primary interface for converting complex pattern
    analysis into user-friendly tree visualizations suitable for executive
    dashboards, operational monitoring, and data exploration interfaces.

    Attributes:
        Inherits all preprocessing capabilities from Base class.

    Example:
        Comprehensive security threat landscape visualization:

        >>> from dataspot.analyzers.tree import Tree
        >>> from dataspot.models.tree import TreeInput, TreeOptions
        >>>
        >>> # Security event data for threat landscape analysis
        >>> security_events = [
        ...     {"threat_type": "malware", "source": "external", "severity": "high", "target": "server"},
        ...     {"threat_type": "malware", "source": "external", "severity": "high", "target": "workstation"},
        ...     {"threat_type": "malware", "source": "internal", "severity": "medium", "target": "server"},
        ...     {"threat_type": "phishing", "source": "external", "severity": "high", "target": "user"},
        ...     {"threat_type": "phishing", "source": "external", "severity": "medium", "target": "user"},
        ...     {"threat_type": "ddos", "source": "external", "severity": "critical", "target": "infrastructure"},
        ... ]
        >>>
        >>> tree = Tree()
        >>>
        >>> # Add preprocessing for risk categorization
        >>> tree.add_preprocessor("severity",
        ...     lambda x: "critical_risk" if x == "critical" else "high_risk" if x == "high" else "medium_risk")
        >>>
        >>> input_data = TreeInput(
        ...     data=security_events,
        ...     fields=["threat_type", "source", "severity"]
        ... )
        >>>
        >>> options = TreeOptions(
        ...     top=10,
        ...     min_count=1,
        ...     sort_by="count"
        ... )
        >>>
        >>> threat_tree = tree.execute(input_data, options)
        >>>
        >>> print(f"Security Threat Landscape Tree:")
        >>> print(f"- Root structure: {threat_tree.name}")
        >>> print(f"- Total security events: {threat_tree.value}")
        >>> print(f"- Coverage: {threat_tree.percentage:.1f}%")
        >>> print(f"- Primary threat categories: {len(threat_tree.children)}")
        >>>
        >>> print(f"\\nThreat Category Breakdown:")
        >>> for category in threat_tree.children:
        ...     print(f"- {category.name}: {category.percentage:.1f}% ({category.value} incidents)")
        ...     if category.children:
        ...         print(f"  Sub-categories: {len(category.children)} attack vectors")
        ...         for subcategory in category.children[:2]:  # Show top 2
        ...             print(f"    * {subcategory.name}: {subcategory.value} incidents")
        >>>
        >>> # Tree statistics for operations dashboard
        >>> stats = threat_tree.statistics
        >>> print(f"\\nOperational Intelligence:")
        >>> print(f"- Events processed: {stats.total_records}")
        >>> print(f"- Patterns identified: {stats.patterns_found}")
        >>> print(f"- Analysis depth: {stats.fields_analyzed} levels")
        >>>
        >>> # Example output:
        >>> # Security Threat Landscape Tree:
        >>> # - Root structure: root
        >>> # - Total security events: 6
        >>> # - Coverage: 100.0%
        >>> # - Primary threat categories: 3
        >>> #
        >>> # Threat Category Breakdown:
        >>> # - malware: 50.0% (3 incidents)
        >>> #   Sub-categories: 2 attack vectors
        >>> #     * external: 2 incidents
        >>> #     * internal: 1 incidents
        >>> # - phishing: 33.3% (2 incidents)
        >>> #   Sub-categories: 1 attack vectors
        >>> #     * external: 2 incidents

    Notes:
        - Tree structures are optimized for JSON serialization and visualization
        - Statistical measures are preserved throughout the transformation process
        - Output is compatible with D3.js, Chart.js, and other visualization libraries
        - Performance is optimized for real-time dashboard and monitoring applications
        - Supports arbitrary depth hierarchical analysis with configurable pruning

    """

    def execute(
        self,
        input: TreeInput,
        options: Optional[TreeOptions] = None,
    ) -> TreeOutput:
        r"""Execute comprehensive hierarchical tree construction for visualization.

        Performs sophisticated tree building analysis to convert pattern data into
        clean, hierarchical JSON structures optimized for interactive visualization
        and business intelligence dashboards. This method serves as the primary
        interface for creating navigation-ready tree structures from complex data.

        The tree building process includes:
        1. Data validation and preprocessing
        2. Query filtering and data preparation
        3. Internal tree structure construction
        4. Pattern extraction and statistical analysis
        5. Tree-specific filtering and optimization
        6. Clean JSON structure generation with metadata

        Args:
            input (TreeInput): Tree construction input configuration containing:
                - data: List of dictionaries representing records to analyze
                - fields: Ordered list of field names defining the tree hierarchy
                - query: Optional dictionary for filtering records before analysis
            options (TreeOptions): Tree building configuration containing:
                - top: Maximum number of branches per tree level
                - min_count: Minimum record count for branch inclusion
                - max_count: Maximum record count for branch filtering
                - min_percentage: Minimum percentage threshold for branch inclusion
                - max_percentage: Maximum percentage threshold for branch filtering
                - sort_by: Sorting criteria for tree branches ('count', 'percentage')
                - Other tree structure and filtering options

        Returns:
            TreeOutput: Comprehensive tree structure containing:
                - name: Root node identifier
                - children: Hierarchical list of TreeNode objects with nested structure
                - value: Total record count at root level
                - percentage: Root coverage percentage (typically 100.0)
                - node: Tree level indicator (0 for root)
                - top: Configuration parameter for reference
                - statistics: Tree construction statistics and metadata
                - fields_analyzed: List of fields included in the hierarchical analysis

        Raises:
            ValueError: If input data is empty or malformed
            TypeError: If data format is incorrect (not list of dictionaries)
            KeyError: If specified fields don't exist in the data

        Example:
            E-commerce customer journey tree for conversion analysis:

            >>> from dataspot.models.tree import TreeInput, TreeOptions
            >>>
            >>> # Customer journey data with conversion funnel
            >>> customer_journeys = [
            ...     {"channel": "organic", "device": "mobile", "action": "visit", "outcome": "bounce"},
            ...     {"channel": "organic", "device": "mobile", "action": "visit", "outcome": "browse"},
            ...     {"channel": "organic", "device": "mobile", "action": "browse", "outcome": "cart"},
            ...     {"channel": "organic", "device": "desktop", "action": "visit", "outcome": "browse"},
            ...     {"channel": "organic", "device": "desktop", "action": "browse", "outcome": "purchase"},
            ...     {"channel": "paid", "device": "mobile", "action": "visit", "outcome": "purchase"},
            ...     {"channel": "paid", "device": "mobile", "action": "visit", "outcome": "browse"},
            ...     {"channel": "email", "device": "desktop", "action": "visit", "outcome": "purchase"},
            ... ]
            >>>
            >>> tree = Tree()
            >>>
            >>> input_data = TreeInput(
            ...     data=customer_journeys,
            ...     fields=["channel", "device", "action", "outcome"]
            ... )
            >>>
            >>> options = TreeOptions(
            ...     top=5,
            ...     min_percentage=10.0,
            ...     sort_by="count"
            ... )
            >>>
            >>> journey_tree = tree.execute(input_data, options)
            >>>
            >>> # Analyze conversion funnel structure
            >>> print(f"E-commerce Conversion Funnel Analysis:")
            >>> print(f"- Total customer interactions: {journey_tree.value}")
            >>> print(f"- Primary acquisition channels: {len(journey_tree.children)}")
            >>>
            >>> print(f"\\nChannel Performance Breakdown:")
            >>> for channel in journey_tree.children:
            ...     print(f"\\n{channel.name.upper()} CHANNEL:")
            ...     print(f"- Traffic volume: {channel.value} interactions ({channel.percentage:.1f}%)")
            ...
            ...     if channel.children:
            ...         print(f"- Device breakdown:")
            ...         for device in channel.children:
            ...             print(f"  * {device.name}: {device.value} users ({device.percentage:.1f}%)")
            ...
            ...             if device.children:
            ...                 # Analyze user actions
            ...                 print(f"    User actions:")
            ...                 for action in device.children:
            ...                     print(f"      - {action.name}: {action.value} sessions")
            ...
            ...                     if action.children:
            ...                         # Analyze conversion outcomes
            ...                         conversion_rate = 0
            ...                         for outcome in action.children:
            ...                             if outcome.name == "purchase":
            ...                                 conversion_rate = (outcome.value / action.value) * 100
            ...                         if conversion_rate > 0:
            ...                             print(f"        Conversion rate: {conversion_rate:.1f}%")
            >>>
            >>> # Business intelligence summary
            >>> stats = journey_tree.statistics
            >>> print(f"\\nBusiness Intelligence Summary:")
            >>> print(f"- Total touchpoints analyzed: {stats.total_records}")
            >>> print(f"- Conversion patterns identified: {stats.patterns_found}")
            >>> print(f"- Funnel depth analyzed: {stats.fields_analyzed} stages")
            >>>
            >>> # Example output:
            >>> # E-commerce Conversion Funnel Analysis:
            >>> # - Total customer interactions: 8
            >>> # - Primary acquisition channels: 3
            >>> #
            >>> # ORGANIC CHANNEL:
            >>> # - Traffic volume: 5 interactions (62.5%)
            >>> # - Device breakdown:
            >>> #   * mobile: 3 users (37.5%)
            >>> #     User actions:
            >>> #       - visit: 2 sessions
            >>> #       - browse: 1 sessions
            >>> #   * desktop: 2 users (25.0%)
            >>> #     User actions:
            >>> #       - visit: 1 sessions
            >>> #       - browse: 1 sessions
            >>> #         Conversion rate: 100.0%

        Example:
            Financial risk assessment tree for portfolio analysis:

            >>> # Investment portfolio risk analysis data
            >>> portfolio_data = [
            ...     {"asset_class": "equity", "geography": "domestic", "sector": "technology", "risk": "high"},
            ...     {"asset_class": "equity", "geography": "domestic", "sector": "technology", "risk": "medium"},
            ...     {"asset_class": "equity", "geography": "international", "sector": "healthcare", "risk": "medium"},
            ...     {"asset_class": "bonds", "geography": "domestic", "sector": "government", "risk": "low"},
            ...     {"asset_class": "bonds", "geography": "domestic", "sector": "corporate", "risk": "medium"},
            ...     {"asset_class": "alternative", "geography": "global", "sector": "real_estate", "risk": "high"},
            ... ]
            >>>
            >>> tree = Tree()
            >>>
            >>> input_data = TreeInput(
            ...     data=portfolio_data,
            ...     fields=["asset_class", "geography", "sector", "risk"]
            ... )
            >>>
            >>> options = TreeOptions(
            ...     top=8,
            ...     min_count=1,
            ...     sort_by="percentage"
            ... )
            >>>
            >>> portfolio_tree = tree.execute(input_data, options)
            >>>
            >>> # Portfolio risk analysis
            >>> print(f"Investment Portfolio Risk Analysis:")
            >>> print(f"- Total portfolio positions: {portfolio_tree.value}")
            >>> print(f"- Asset class diversification: {len(portfolio_tree.children)} classes")
            >>>
            >>> print(f"\\nRisk Assessment by Asset Class:")
            >>> for asset_class in portfolio_tree.children:
            ...     print(f"\\n{asset_class.name.upper()}:")
            ...     print(f"- Portfolio allocation: {asset_class.percentage:.1f}%")
            ...     print(f"- Position count: {asset_class.value} positions")
            ...
            ...     if asset_class.children:
            ...         print(f"- Geographic breakdown:")
            ...         for geography in asset_class.children:
            ...             print(f"  * {geography.name}: {geography.percentage:.1f}% allocation")
            ...
            ...             if geography.children:
            ...                 # Risk concentration analysis
            ...                 risk_distribution = {}
            ...                 total_positions = 0
            ...
            ...                 for sector in geography.children:
            ...                     total_positions += sector.value
            ...                     if sector.children:
            ...                         for risk in sector.children:
            ...                             risk_level = risk.name
            ...                             risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + risk.value
            ...
            ...                 if risk_distribution:
            ...                     print(f"    Risk profile:")
            ...                     for risk_level, count in risk_distribution.items():
            ...                         risk_pct = (count / total_positions) * 100 if total_positions > 0 else 0
            ...                         print(f"      - {risk_level}: {risk_pct:.1f}% ({count} positions)")
            >>>
            >>> # Risk management insights
            >>> print(f"\\nRisk Management Intelligence:")
            >>> print(f"- Investment positions analyzed: {portfolio_tree.statistics.total_records}")
            >>> print(f"- Risk patterns identified: {portfolio_tree.statistics.patterns_found}")
            >>> print(f"- Analysis granularity: {portfolio_tree.statistics.fields_analyzed} levels")
            >>>
            >>> # Example output:
            >>> # Investment Portfolio Risk Analysis:
            >>> # - Total portfolio positions: 6
            >>> # - Asset class diversification: 3 classes
            >>> #
            >>> # EQUITY:
            >>> # - Portfolio allocation: 50.0%
            >>> # - Position count: 3 positions
            >>> # - Geographic breakdown:
            >>> #   * domestic: 33.3% allocation
            >>> #     Risk profile:
            >>> #       - high: 50.0% (1 positions)
            >>> #       - medium: 50.0% (1 positions)

        Notes:
            - Empty data results in properly structured empty trees with metadata
            - Field order determines hierarchical levels in the tree structure
            - Statistical measures are preserved throughout tree construction
            - Tree pruning is applied based on configured thresholds for performance
            - JSON output is optimized for modern visualization frameworks
            - Memory usage scales efficiently with data size and tree complexity

        """
        if options is None:
            options = TreeOptions()

        # Validate input
        self._validate_data(input.data)

        # Filter data based on query
        filtered_data = self._filter_data_by_query(input.data, input.query)

        # Build empty tree if no data
        if not filtered_data:
            empty_statistics = TreeStatistics(
                total_records=len(input.data),
                filtered_records=0,
                patterns_found=0,
                fields_analyzed=len(input.fields),
            )
            return TreeOutput(
                name="root",
                children=[],
                value=0,
                percentage=0.0,
                node=0,
                top=options.top,
                statistics=empty_statistics,
                fields_analyzed=input.fields,
            )

        # Build internal tree structure
        internal_tree = self._build_tree(filtered_data, input.fields)
        total_records = len(filtered_data)

        # Extract patterns from tree
        all_patterns = PatternExtractor.from_tree(internal_tree, total_records)

        # Apply tree-specific filters
        filter_kwargs = TreeFilter.build_filter_kwargs(**options.to_kwargs())
        filtered_patterns = PatternFilter(all_patterns).apply_all(**filter_kwargs)

        # Build and return clean JSON tree
        tree_result = TreeBuilder(filtered_patterns, total_records, options.top).build()

        # Convert tree result to TreeOutput
        children = self._convert_tree_children(tree_result.get("children", []))

        statistics = TreeStatistics(
            total_records=len(input.data),
            filtered_records=len(filtered_data),
            patterns_found=len(filtered_patterns),
            fields_analyzed=len(input.fields),
        )

        return TreeOutput(
            name=tree_result.get("name", "root"),
            children=children,
            value=tree_result.get("value", 0),
            percentage=tree_result.get("percentage", 0.0),
            node=tree_result.get("node", 0),
            top=options.top,
            statistics=statistics,
            fields_analyzed=input.fields,
        )

    def _convert_tree_children(
        self, children_data: List[Dict[str, Any]]
    ) -> List[TreeNode]:
        """Convert raw tree data to structured TreeNode objects recursively.

        Transforms dictionary-based tree data into strongly-typed TreeNode
        dataclasses, ensuring type safety and consistent API structure
        throughout the tree hierarchy. This conversion enables reliable
        access to tree properties and maintains data integrity.

        Args:
            children_data (List[Dict[str, Any]]): List of child node dictionaries
                containing tree structure data with names, values, percentages,
                and nested children information.

        Returns:
            List[TreeNode]: List of properly structured TreeNode dataclasses
                with recursive children conversion and complete metadata preservation.

        Example:
            Converting marketing funnel tree data:

            >>> # Raw tree data from tree building process
            >>> raw_tree_data = [
            ...     {
            ...         "name": "email_marketing",
            ...         "value": 500,
            ...         "percentage": 50.0,
            ...         "node": 1,
            ...         "children": [
            ...             {
            ...                 "name": "newsletter",
            ...                 "value": 300,
            ...                 "percentage": 30.0,
            ...                 "node": 2,
            ...                 "children": []
            ...             }
            ...         ]
            ...     }
            ... ]
            >>>
            >>> tree_nodes = tree._convert_tree_children(raw_tree_data)
            >>>
            >>> print(f"Tree Conversion Results:")
            >>> for node in tree_nodes:
            ...     print(f"- Channel: {node.name}")
            ...     print(f"  Reach: {node.value} customers ({node.percentage:.1f}%)")
            ...     print(f"  Tree level: {node.node}")
            ...     print(f"  Sub-channels: {len(node.children or [])}")
            ...
            ...     if node.children:
            ...         for child in node.children:
            ...             print(f"    * {child.name}: {child.value} customers")
            >>>
            >>> # Example output:
            >>> # Tree Conversion Results:
            >>> # - Channel: email_marketing
            >>> #   Reach: 500 customers (50.0%)
            >>> #   Tree level: 1
            >>> #   Sub-channels: 1
            >>> #     * newsletter: 300 customers

        Notes:
            - Recursive conversion ensures complete tree structure transformation
            - Type safety is enforced through TreeNode dataclass conversion
            - Missing data fields are handled gracefully with default values
            - Children relationships are preserved throughout the conversion process
            - Memory efficiency is maintained through selective data copying

        """
        tree_nodes = []
        for child in children_data:
            # Recursively convert children
            child_children = None
            if "children" in child and child["children"]:
                child_children = self._convert_tree_children(child["children"])

            node = TreeNode(
                name=child.get("name", ""),
                value=child.get("value", 0),
                percentage=child.get("percentage", 0.0),
                node=child.get("node", 0),
                children=child_children,
            )
            tree_nodes.append(node)

        return tree_nodes

    def _build_empty_tree(self, top: int) -> Dict[str, Any]:
        """Build clean empty tree structure for edge cases and error handling.

        Creates a properly structured empty tree when no data is available
        for tree construction. This ensures consistent API responses and
        prevents errors in visualization frameworks when datasets are empty
        or completely filtered out.

        Args:
            top (int): Maximum number of top elements per tree level,
                preserved in empty tree structure for configuration consistency.

        Returns:
            Dict[str, Any]: Empty but properly structured tree dictionary with:
                - Standard root node structure
                - Empty children list
                - Zero values for statistical measures
                - Complete metadata for API consistency

        Example:
            Handling empty dataset scenarios gracefully:

            >>> # Empty tree construction
            >>> empty_tree = tree._build_empty_tree(top=5)
            >>>
            >>> print(f"Empty Tree Structure:")
            >>> print(f"- Root name: {empty_tree['name']}")
            >>> print(f"- Children count: {len(empty_tree['children'])}")
            >>> print(f"- Root value: {empty_tree['value']}")
            >>> print(f"- Coverage percentage: {empty_tree['percentage']}")
            >>> print(f"- Tree level: {empty_tree['node']}")
            >>> print(f"- Configuration preserved: top={empty_tree['top']}")
            >>>
            >>> # Example output:
            >>> # Empty Tree Structure:
            >>> # - Root name: root
            >>> # - Children count: 0
            >>> # - Root value: 0
            >>> # - Coverage percentage: 0.0
            >>> # - Tree level: 0
            >>> # - Configuration preserved: top=5

        Notes:
            - Maintains consistent structure for visualization framework integration
            - Preserves configuration parameters for debugging and validation
            - Enables graceful handling of edge cases in production applications
            - Supports reliable error handling in automated dashboard systems

        """
        return {
            "name": "root",
            "children": [],
            "value": 0,
            "percentage": 0.0,
            "node": 0,
            "top": top,
        }
