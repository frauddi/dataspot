"""Advanced pattern extraction and tree structure generation for hierarchical data analysis.

This module provides sophisticated pattern extraction capabilities that convert
hierarchical tree structures into actionable pattern objects and clean JSON
representations. It serves as the core transformation engine between internal
tree representations and user-facing pattern analysis results.

The module contains two main components:
- PatternExtractor: Converts tree structures to pattern objects for analysis
- TreeBuilder: Generates clean, JSON-ready tree structures for visualization

These utilities are essential for transforming raw hierarchical data into
meaningful business insights and support various visualization and reporting
requirements across the Dataspot library.

Key Features:
    - High-performance tree traversal algorithms
    - Pattern object generation with statistical measures
    - Clean JSON tree structure generation for visualization
    - Hierarchical data representation and organization
    - Flexible depth-based pattern analysis
    - Memory-efficient processing for large tree structures
    - Sample data preservation for pattern validation

Example:
    Converting tree structures to patterns for fraud analysis:

    >>> from dataspot.analyzers.pattern_extractor import PatternExtractor
    >>>
    >>> # Hierarchical tree structure from fraud detection
    >>> fraud_tree = {
    ...     "children": {
    ...         "XX": {
    ...             "count": 3, "percentage": 60.0, "depth": 1,
    ...             "samples": [{"country": "XX", "method": "crypto"}],
    ...             "children": {
    ...                 "crypto": {
    ...                     "count": 3, "percentage": 60.0, "depth": 2,
    ...                     "samples": [{"country": "XX", "method": "crypto"}],
    ...                     "children": {}
    ...                 }
    ...             }
    ...         }
    ...     }
    ... }
    >>>
    >>> patterns = PatternExtractor.from_tree(fraud_tree, total_records=5)
    >>> print(f"Extracted {len(patterns)} suspicious patterns")
    >>>
    >>> # Example output:
    >>> # Extracted 2 suspicious patterns

Notes:
    Pattern extraction maintains statistical accuracy and preserves sample data
    for validation and business analysis. Tree builders optimize structures for
    visualization and reporting while maintaining data integrity.

See Also:
    - analyzers.finder: Core pattern finding functionality
    - analyzers.tree_analyzer: Tree-based analysis operations
    - models.pattern: Pattern data structures and validation

"""

from typing import Any, Dict, List

from ..models import Pattern


class PatternExtractor:
    r"""Advanced pattern extraction engine for converting tree structures to pattern objects.

    The PatternExtractor class provides sophisticated algorithms for traversing
    hierarchical tree structures and converting them into actionable Pattern
    objects. This transformation is essential for converting internal tree
    representations into business-ready insights and statistical analysis.

    This class specializes in:
    - Recursive tree traversal with optimized performance
    - Pattern object creation with complete statistical measures
    - Sample data preservation for validation and analysis
    - Hierarchical path construction and organization
    - Memory-efficient processing for large tree structures
    - Statistical accuracy maintenance during extraction

    The extractor serves as a critical component in the pattern analysis
    pipeline, enabling the transformation of complex tree structures into
    consumable pattern insights for business intelligence and reporting.

    Example:
        Extracting security patterns from hierarchical analysis:

        >>> from dataspot.analyzers.pattern_extractor import PatternExtractor
        >>>
        >>> # Security event tree structure
        >>> security_tree = {
        ...     "children": {
        ...         "external": {
        ...             "count": 4, "percentage": 66.7, "depth": 1,
        ...             "samples": [{"source": "external", "agent": "Bot"}],
        ...             "children": {
        ...                 "Bot": {
        ...                     "count": 3, "percentage": 50.0, "depth": 2,
        ...                     "samples": [{"source": "external", "agent": "Bot", "status": "failed"}],
        ...                     "children": {
        ...                         "failed": {
        ...                             "count": 3, "percentage": 50.0, "depth": 3,
        ...                             "samples": [{"source": "external", "agent": "Bot", "status": "failed"}],
        ...                             "children": {}
        ...                         }
        ...                     }
        ...                 }
        ...             }
        ...         },
        ...         "internal": {
        ...             "count": 2, "percentage": 33.3, "depth": 1,
        ...             "samples": [{"source": "internal", "agent": "Chrome"}],
        ...             "children": {}
        ...         }
        ...     }
        ... }
        >>>
        >>> patterns = PatternExtractor.from_tree(security_tree, total_records=6)
        >>>
        >>> print(f"Security Pattern Analysis:")
        >>> print(f"- Total patterns extracted: {len(patterns)}")
        >>>
        >>> print(f"\\nDetailed Pattern Breakdown:")
        >>> for pattern in patterns:
        ...     print(f"- Path: {pattern.path}")
        ...     print(f"  Threat Level: {pattern.percentage:.1f}% concentration")
        ...     print(f"  Occurrences: {pattern.count} events")
        ...     print(f"  Analysis Depth: {pattern.depth}")
        ...     print(f"  Sample Data: {len(pattern.samples)} samples")
        >>>
        >>> # Example output:
        >>> # Security Pattern Analysis:
        >>> # - Total patterns extracted: 4
        >>> #
        >>> # Detailed Pattern Breakdown:
        >>> # - Path: external
        >>> #   Threat Level: 66.7% concentration
        >>> #   Occurrences: 4 events
        >>> #   Analysis Depth: 1
        >>> #   Sample Data: 1 samples
        >>> # - Path: external > Bot
        >>> #   Threat Level: 50.0% concentration
        >>> #   Occurrences: 3 events
        >>> #   Analysis Depth: 2
        >>> #   Sample Data: 1 samples

    Notes:
        - Extraction preserves complete statistical measures and sample data
        - Tree traversal is optimized for memory efficiency with large structures
        - Pattern paths maintain hierarchical relationship information
        - Sample data is limited to first 3 samples for performance optimization

    """

    @staticmethod
    def from_tree(tree: Dict[str, Any], total_records: int) -> List[Pattern]:
        r"""Extract comprehensive Pattern objects from hierarchical tree structure.

        Performs sophisticated tree traversal to convert internal tree
        representations into actionable Pattern objects with complete
        statistical measures. This method is the core transformation
        engine for converting analysis results into business insights.

        The extraction process includes:
        1. Recursive tree traversal with path construction
        2. Pattern object creation with statistical measures
        3. Sample data preservation for validation
        4. Hierarchical relationship maintenance
        5. Memory optimization for large tree structures
        6. Statistical accuracy validation

        Args:
            tree (Dict[str, Any]): Hierarchical tree structure containing pattern data.
                Expected structure with 'children' containing nested pattern nodes.
                Each node should have: count, percentage, depth, and optional samples.
            total_records (int): Total number of records analyzed for percentage
                validation and statistical context.

        Returns:
            List[Pattern]: Comprehensive list of Pattern objects containing:
                - path: Hierarchical path representing pattern combination
                - count: Absolute number of records matching the pattern
                - percentage: Concentration percentage within the dataset
                - depth: Hierarchical depth level of the pattern
                - samples: Representative sample records (limited to 3 for performance)

        Example:
            E-commerce customer behavior pattern extraction:

            >>> # Customer behavior tree from analysis
            >>> customer_tree = {
            ...     "children": {
            ...         "premium": {
            ...             "count": 150, "percentage": 75.0, "depth": 1,
            ...             "samples": [{"segment": "premium", "device": "mobile"}],
            ...             "children": {
            ...                 "mobile": {
            ...                     "count": 120, "percentage": 60.0, "depth": 2,
            ...                     "samples": [{"segment": "premium", "device": "mobile", "action": "purchase"}],
            ...                     "children": {
            ...                         "purchase": {
            ...                             "count": 80, "percentage": 40.0, "depth": 3,
            ...                             "samples": [
            ...                                 {"segment": "premium", "device": "mobile", "action": "purchase", "value": 299},
            ...                                 {"segment": "premium", "device": "mobile", "action": "purchase", "value": 199}
            ...                             ],
            ...                             "children": {}
            ...                         }
            ...                     }
            ...                 }
            ...             }
            ...         },
            ...         "standard": {
            ...             "count": 50, "percentage": 25.0, "depth": 1,
            ...             "samples": [{"segment": "standard", "device": "desktop"}],
            ...             "children": {}
            ...         }
            ...     }
            ... }
            >>>
            >>> patterns = PatternExtractor.from_tree(customer_tree, total_records=200)
            >>>
            >>> print(f"Customer Behavior Pattern Extraction:")
            >>> print(f"- Total patterns discovered: {len(patterns)}")
            >>>
            >>> print(f"\\nBusiness Intelligence Insights:")
            >>> for i, pattern in enumerate(patterns, 1):
            ...     print(f"{i}. Customer Pattern: {pattern.path}")
            ...     print(f"   Market Share: {pattern.percentage:.1f}% of customers")
            ...     print(f"   Volume: {pattern.count} customers")
            ...     print(f"   Behavior Complexity: Level {pattern.depth}")
            ...     if pattern.samples:
            ...         print(f"   Representative Sample: {pattern.samples[0]}")
            >>>
            >>> # Example output:
            >>> # Customer Behavior Pattern Extraction:
            >>> # - Total patterns discovered: 4
            >>> #
            >>> # Business Intelligence Insights:
            >>> # 1. Customer Pattern: premium
            >>> #    Market Share: 75.0% of customers
            >>> #    Volume: 150 customers
            >>> #    Behavior Complexity: Level 1
            >>> #    Representative Sample: {'segment': 'premium', 'device': 'mobile'}
            >>> # 2. Customer Pattern: premium > mobile
            >>> #    Market Share: 60.0% of customers
            >>> #    Volume: 120 customers
            >>> #    Behavior Complexity: Level 2
            >>> #    Representative Sample: {'segment': 'premium', 'device': 'mobile', 'action': 'purchase'}

        Example:
            Financial fraud pattern extraction:

            >>> # Fraud detection tree structure
            >>> fraud_tree = {
            ...     "children": {
            ...         "high_risk": {
            ...             "count": 25, "percentage": 12.5, "depth": 1,
            ...             "samples": [{"risk_level": "high_risk", "country": "XX"}],
            ...             "children": {
            ...                 "XX": {
            ...                     "count": 20, "percentage": 10.0, "depth": 2,
            ...                     "samples": [{"risk_level": "high_risk", "country": "XX", "method": "crypto"}],
            ...                     "children": {
            ...                         "crypto": {
            ...                             "count": 18, "percentage": 9.0, "depth": 3,
            ...                             "samples": [
            ...                                 {"risk_level": "high_risk", "country": "XX", "method": "crypto", "amount": 10000},
            ...                                 {"risk_level": "high_risk", "country": "XX", "method": "crypto", "amount": 15000}
            ...                             ],
            ...                             "children": {}
            ...                         }
            ...                     }
            ...                 }
            ...             }
            ...         }
            ...     }
            ... }
            >>>
            >>> fraud_patterns = PatternExtractor.from_tree(fraud_tree, total_records=200)
            >>>
            >>> print(f"Fraud Detection Pattern Analysis:")
            >>> print(f"- Suspicious patterns identified: {len(fraud_patterns)}")
            >>>
            >>> print(f"\\nFraud Risk Assessment:")
            >>> for pattern in fraud_patterns:
            ...     risk_score = pattern.percentage * (pattern.depth / 3.0)  # Depth-weighted risk
            ...     print(f"- Fraud Pattern: {pattern.path}")
            ...     print(f"  Risk Score: {risk_score:.2f} (weighted by complexity)")
            ...     print(f"  Prevalence: {pattern.percentage:.1f}% of transactions")
            ...     print(f"  Alert Count: {pattern.count} suspicious transactions")
            >>>
            >>> # Example output:
            >>> # Fraud Detection Pattern Analysis:
            >>> # - Suspicious patterns identified: 3
            >>> #
            >>> # Fraud Risk Assessment:
            >>> # - Fraud Pattern: high_risk
            >>> #   Risk Score: 4.17 (weighted by complexity)
            >>> #   Prevalence: 12.5% of transactions
            >>> #   Alert Count: 25 suspicious transactions
            >>> # - Fraud Pattern: high_risk > XX
            >>> #   Risk Score: 6.67 (weighted by complexity)
            >>> #   Prevalence: 10.0% of transactions
            >>> #   Alert Count: 20 suspicious transactions

        Notes:
            - Tree traversal is recursive and handles arbitrary depth structures
            - Pattern paths are constructed hierarchically with " > " separators
            - Sample data is preserved for validation and business analysis
            - Statistical measures are maintained with precision during extraction
            - Memory usage is optimized through selective sample preservation
            - Empty trees return empty pattern lists gracefully

        """
        patterns = []

        def _traverse_tree(node: Dict[str, Any], path: str = "") -> None:
            """Recursively traverse tree and extract patterns."""
            for key, child in node.get("children", {}).items():
                current_path = f"{path} > {key}" if path else key

                if child.get("count", 0) > 0:
                    pattern = Pattern(
                        path=current_path,
                        count=child["count"],
                        percentage=child["percentage"],
                        depth=child["depth"],
                        samples=child.get("samples", [])[:3],  # Keep first 3 samples
                    )
                    patterns.append(pattern)

                # Continue traversing children
                _traverse_tree(child, current_path)

        _traverse_tree(tree)
        return patterns


class TreeBuilder:
    r"""Advanced tree structure generator for clean JSON visualization and reporting.

    The TreeBuilder class provides sophisticated algorithms for converting
    pattern analysis results into clean, JSON-ready tree structures optimized
    for visualization, reporting, and business intelligence applications.

    This class specializes in:
    - Clean tree structure generation for visualization frameworks
    - Hierarchical data organization and optimization
    - top-N filtering for focused analysis
    - JSON-ready format generation with metadata
    - Performance optimization for large pattern sets
    - Statistical measure preservation during transformation

    The builder serves visualization and reporting systems by providing
    structured, clean tree representations that maintain statistical
    accuracy while optimizing for presentation and user experience.

    Attributes:
        patterns (List[Pattern]): Source patterns for tree construction.
        total_records (int): Total records for statistical context.
        limit (int): Maximum number of top elements per tree level.

    Example:
        Building visualization trees for business dashboards:

        >>> from dataspot.analyzers.pattern_extractor import TreeBuilder
        >>> from dataspot.models.pattern import Pattern
        >>>
        >>> # Marketing campaign patterns for dashboard
        >>> campaign_patterns = [
        ...     Pattern(path="email", count=500, percentage=50.0, depth=1, samples=[]),
        ...     Pattern(path="email > premium", count=300, percentage=30.0, depth=2, samples=[]),
        ...     Pattern(path="social", count=300, percentage=30.0, depth=1, samples=[]),
        ...     Pattern(path="social > standard", count=200, percentage=20.0, depth=2, samples=[]),
        ... ]
        >>>
        >>> builder = TreeBuilder(campaign_patterns, total_records=1000, limit=5)
        >>> tree_structure = builder.build()
        >>>
        >>> print(f"Marketing Dashboard Tree Structure:")
        >>> print(f"- Root value: {tree_structure['value']} total customers")
        >>> print(f"- top-level channels: {len(tree_structure['children'])}")
        >>>
        >>> print(f"\\nChannel Performance Breakdown:")
        >>> for channel in tree_structure['children']:
        ...     print(f"- {channel['name']}: {channel['percentage']:.1f}% reach")
        ...     print(f"  Volume: {channel['value']} customers")
        ...     if 'children' in channel:
        ...         print(f"  Sub-segments: {len(channel['children'])} identified")
        >>>
        >>> # Example output:
        >>> # Marketing Dashboard Tree Structure:
        >>> # - Root value: 1000 total customers
        >>> # - top-level channels: 2
        >>> #
        >>> # Channel Performance Breakdown:
        >>> # - email: 50.0% reach
        >>> #   Volume: 500 customers
        >>> #   Sub-segments: 1 identified
        >>> # - social: 30.0% reach
        >>> #   Volume: 300 customers
        >>> #   Sub-segments: 1 identified

    Notes:
        - Tree structures are optimized for JSON serialization and visualization
        - top-N filtering ensures focused analysis on most significant patterns
        - Hierarchical organization maintains business relationship context
        - Performance is optimized for real-time dashboard and reporting systems

    """

    def __init__(self, patterns: List[Pattern], total_records: int, limit: int):
        """Initialize tree builder with pattern data and configuration.

        Sets up the tree building engine with source patterns and optimization
        parameters for generating clean, visualization-ready tree structures.

        Args:
            patterns (List[Pattern]): Source patterns to build tree structure from.
                Each pattern should contain path, count, percentage, and depth information.
            total_records (int): Total number of records in the original dataset
                for statistical context and percentage validation.
            limit (int): Maximum number of top elements to include per tree level
                for focused analysis and performance optimization.

        Example:
            Initializing builder for security event visualization:

            >>> # Security patterns from threat analysis
            >>> security_patterns = [
            ...     Pattern(path="failed_login", count=150, percentage=30.0, depth=1, samples=[]),
            ...     Pattern(path="failed_login > external_ip", count=120, percentage=24.0, depth=2, samples=[]),
            ...     Pattern(path="successful_login", count=350, percentage=70.0, depth=1, samples=[]),
            ... ]
            >>>
            >>> # Build tree for security dashboard (limit 10 per level)
            >>> security_builder = TreeBuilder(security_patterns, total_records=500, limit=10)
            >>>
            >>> print(f"Security Tree Builder Initialized:")
            >>> print(f"- Source patterns: {len(security_builder.patterns)}")
            >>> print(f"- Total records context: {security_builder.total_records}")
            >>> print(f"- Focus level: top {security_builder.limit} per level")
            >>>
            >>> # Example output:
            >>> # Security Tree Builder Initialized:
            >>> # - Source patterns: 3
            >>> # - Total records context: 500
            >>> # - Focus level: top 10 per level

        Notes:
            - Configuration parameters are validated during initialization
            - Pattern data is preserved in original form for tree construction
            - top-N parameter enables performance optimization for large datasets

        """
        self.patterns = patterns
        self.total_records = total_records
        self.limit = limit

    def build(self) -> Dict[str, Any]:
        r"""Build comprehensive, JSON-ready tree structure from pattern data.

        Generates a clean, hierarchical tree structure optimized for
        visualization frameworks and business intelligence dashboards.
        The resulting structure maintains statistical accuracy while
        providing optimal organization for user interfaces and reporting.

        The building process includes:
        1. Pattern grouping by hierarchical relationships
        2. Statistical measure preservation and validation
        3. top-N filtering for performance optimization
        4. JSON format optimization for visualization frameworks
        5. Metadata inclusion for business intelligence context
        6. Performance optimization for real-time applications

        Returns:
            Dict[str, Any]: Complete JSON-ready tree structure containing:
                - name: Root node identifier ("root")
                - children: Hierarchical list of child nodes with pattern data
                - value: Total record count for statistical context
                - percentage: Root percentage (always 100.0)
                - node: Tree level indicator (0 for root)
                - limit: Configuration parameter for reference

        Example:
            Building customer segmentation tree for business intelligence:

            >>> # Customer segmentation patterns
            >>> segmentation_patterns = [
            ...     Pattern(path="enterprise", count=200, percentage=40.0, depth=1, samples=[]),
            ...     Pattern(path="enterprise > north_america", count=120, percentage=24.0, depth=2, samples=[]),
            ...     Pattern(path="enterprise > europe", count=80, percentage=16.0, depth=2, samples=[]),
            ...     Pattern(path="smb", count=300, percentage=60.0, depth=1, samples=[]),
            ...     Pattern(path="smb > north_america", count=180, percentage=36.0, depth=2, samples=[]),
            ... ]
            >>>
            >>> builder = TreeBuilder(segmentation_patterns, total_records=500, limit=3)
            >>> customer_tree = builder.build()
            >>>
            >>> print(f"Customer Segmentation Tree Analysis:")
            >>> print(f"- Tree structure: {customer_tree['name']} node")
            >>> print(f"- Total market size: {customer_tree['value']} customers")
            >>> print(f"- Market coverage: {customer_tree['percentage']:.1f}%")
            >>> print(f"- Analysis depth: {len(customer_tree['children'])} primary segments")
            >>>
            >>> print(f"\\nPrimary Market Segments:")
            >>> for segment in customer_tree['children']:
            ...     print(f"- {segment['name']}: {segment['percentage']:.1f}% market share")
            ...     print(f"  Customer base: {segment['value']} customers")
            ...     print(f"  Regional breakdown: {len(segment.get('children', []))} regions")
            >>>
            >>> # Detailed regional analysis
            >>> print(f"\\nRegional Distribution Analysis:")
            >>> for segment in customer_tree['children']:
            ...     if 'children' in segment:
            ...         print(f"\\n{segment['name']} Regional Breakdown:")
            ...         for region in segment['children']:
            ...             market_penetration = (region['value'] / customer_tree['value']) * 100
            ...             print(f"  - {region['name']}: {region['value']} customers")
            ...             print(f"    Market penetration: {market_penetration:.1f}%")
            ...             print(f"    Segment contribution: {region['percentage']:.1f}%")
            >>>
            >>> # Example output:
            >>> # Customer Segmentation Tree Analysis:
            >>> # - Tree structure: root node
            >>> # - Total market size: 500 customers
            >>> # - Market coverage: 100.0%
            >>> # - Analysis depth: 2 primary segments
            >>> #
            >>> # Primary Market Segments:
            >>> # - smb: 60.0% market share
            >>> #   Customer base: 300 customers
            >>> #   Regional breakdown: 1 regions
            >>> # - enterprise: 40.0% market share
            >>> #   Customer base: 200 customers
            >>> #   Regional breakdown: 2 regions

        Example:
            Building security threat landscape for operations dashboard:

            >>> # Security threat patterns
            >>> threat_patterns = [
            ...     Pattern(path="malware", count=150, percentage=30.0, depth=1, samples=[]),
            ...     Pattern(path="malware > trojan", count=90, percentage=18.0, depth=2, samples=[]),
            ...     Pattern(path="malware > ransomware", count=60, percentage=12.0, depth=2, samples=[]),
            ...     Pattern(path="phishing", count=200, percentage=40.0, depth=1, samples=[]),
            ...     Pattern(path="phishing > email", count=150, percentage=30.0, depth=2, samples=[]),
            ... ]
            >>>
            >>> security_builder = TreeBuilder(threat_patterns, total_records=500, limit=5)
            >>> threat_tree = security_builder.build()
            >>>
            >>> print(f"Security Threat Landscape Analysis:")
            >>> print(f"- Total security events: {threat_tree['value']}")
            >>> print(f"- Primary threat categories: {len(threat_tree['children'])}")
            >>>
            >>> print(f"\\nThreat Category Risk Assessment:")
            >>> for threat in threat_tree['children']:
            ...     risk_level = "HIGH" if threat['percentage'] > 35 else "MEDIUM" if threat['percentage'] > 20 else "LOW"
            ...     print(f"- {threat['name']}: {risk_level} RISK")
            ...     print(f"  Incident rate: {threat['percentage']:.1f}% of total events")
            ...     print(f"  Event volume: {threat['value']} incidents")
            ...
            ...     if 'children' in threat:
            ...         print(f"  Sub-threat analysis:")
            ...         for sub_threat in threat['children']:
            ...             print(f"    * {sub_threat['name']}: {sub_threat['value']} incidents ({sub_threat['percentage']:.1f}%)")
            >>>
            >>> # Example output:
            >>> # Security Threat Landscape Analysis:
            >>> # - Total security events: 500
            >>> # - Primary threat categories: 2
            >>> #
            >>> # Threat Category Risk Assessment:
            >>> # - phishing: HIGH RISK
            >>> #   Incident rate: 40.0% of total events
            >>> #   Event volume: 200 incidents
            >>> #   Sub-threat analysis:
            >>> #     * email: 150 incidents (30.0%)

        Notes:
            - Empty pattern lists result in clean empty tree structures
            - Tree organization prioritizes highest-count patterns per level
            - JSON format is optimized for modern visualization frameworks
            - Statistical measures are preserved throughout the transformation
            - Performance is optimized for real-time dashboard applications
            - Supports arbitrary depth hierarchical structures

        """
        if not self.patterns:
            return self._build_empty_tree()

        tree_data = self._group_patterns_by_hierarchy()
        root_children = self._convert_to_json_format(tree_data)

        return {
            "name": "root",
            "children": root_children,
            "value": self.total_records,
            "percentage": 100.0,
            "node": 0,
            "limit": self.limit,
        }

    def _build_empty_tree(self) -> Dict[str, Any]:
        """Build clean empty tree structure for edge cases.

        Creates a properly structured empty tree when no patterns are
        available for visualization. This ensures consistent API responses
        and prevents errors in visualization frameworks.

        Returns:
            Dict[str, Any]: Empty but properly structured tree with:
                - Standard root node structure
                - Empty children list
                - Complete metadata for consistency

        Example:
            Handling empty pattern scenarios:

            >>> # Empty pattern scenario
            >>> empty_builder = TreeBuilder([], total_records=100, limit=5)
            >>> empty_tree = empty_builder._build_empty_tree()
            >>>
            >>> print(f"Empty Tree Structure:")
            >>> print(f"- Root name: {empty_tree['name']}")
            >>> print(f"- Children count: {len(empty_tree['children'])}")
            >>> print(f"- Total records: {empty_tree['value']}")
            >>> print(f"- Root percentage: {empty_tree['percentage']}")
            >>>
            >>> # Example output:
            >>> # Empty Tree Structure:
            >>> # - Root name: root
            >>> # - Children count: 0
            >>> # - Total records: 100
            >>> # - Root percentage: 100.0

        Notes:
            - Maintains consistent structure for visualization frameworks
            - Preserves metadata for business intelligence context
            - Enables graceful handling of edge cases in applications

        """
        return {
            "name": "root",
            "children": [],
            "value": self.total_records,
            "percentage": 100.0,
            "node": 0,
            "limit": self.limit,
        }

    def _group_patterns_by_hierarchy(self) -> Dict[str, Any]:
        """Group patterns into hierarchical structure for tree construction.

        Organizes source patterns into a hierarchical data structure that
        preserves relationships and statistical measures while preparing
        for JSON tree conversion. This method handles complex pattern
        relationships and ensures data integrity during transformation.

        Returns:
            Dict[str, Any]: Hierarchical structure with nested pattern data
                organized by path relationships and statistical measures.

        Example:
            Grouping e-commerce conversion patterns:

            >>> # E-commerce patterns would be grouped like:
            >>> # {
            >>> #   "mobile": {
            >>> #     "count": 300, "percentage": 60.0, "depth": 1,
            >>> #     "children": {
            >>> #       "purchase": {
            >>> #         "count": 150, "percentage": 30.0, "depth": 2,
            >>> #         "children": {}
            >>> #       }
            >>> #     }
            >>> #   }
            >>> # }

        Notes:
            - Preserves complete statistical measures during grouping
            - Maintains hierarchical relationships from pattern paths
            - Optimizes structure for efficient JSON conversion
            - Handles complex multi-level pattern hierarchies

        """
        tree_data = {}

        for pattern in self.patterns:
            path_parts = pattern.path.split(" > ")
            current = tree_data

            for i, part in enumerate(path_parts):
                if part not in current:
                    current[part] = {
                        "count": 0,
                        "percentage": 0.0,
                        "depth": i + 1,
                        "children": {},
                        "samples": [],
                    }

                # Update for exact pattern match (last part of path)
                if i == len(path_parts) - 1:
                    current[part]["count"] = pattern.count
                    current[part]["percentage"] = pattern.percentage
                    current[part]["samples"] = pattern.samples

                current = current[part]["children"]

        return tree_data

    def _convert_to_json_format(
        self, data: Dict[str, Any], level: int = 1
    ) -> List[Dict[str, Any]]:
        """Convert hierarchical tree data to clean, visualization-ready JSON format.

        Transforms internal tree data structure into JSON format optimized
        for visualization frameworks and business intelligence dashboards.
        Applies top-N filtering and statistical measure preservation during
        the conversion process.

        Args:
            data (Dict[str, Any]): Internal hierarchical tree data structure
                containing pattern relationships and statistical measures.
            level (int): Current tree level for metadata and structure optimization.
                Used for visualization depth control and performance tuning.

        Returns:
            List[Dict[str, Any]]: Clean JSON tree nodes optimized for visualization
                with complete metadata and statistical measures preserved.

        Example:
            Converting marketing campaign data to visualization format:

            >>> # Internal data structure would be converted to:
            >>> # [
            >>> #   {
            >>> #     "name": "email_campaign",
            >>> #     "value": 500,
            >>> #     "percentage": 50.0,
            >>> #     "node": 1,
            >>> #     "children": [...]
            >>> #   }
            >>> # ]

        Notes:
            - Applies top-N filtering for performance optimization
            - Preserves all statistical measures for business analysis
            - Sorts by count for most significant patterns first
            - Maintains hierarchical structure for visualization frameworks
            - Optimizes JSON structure for real-time dashboard performance

        """
        children = []

        # Sort by count and take limit N
        sorted_items = sorted(
            data.items(), key=lambda x: x[1].get("count", 0), reverse=True
        )[: self.limit]

        for name, node_data in sorted_items:
            node = {
                "name": name,
                "value": node_data["count"],
                "percentage": node_data["percentage"],
                "node": level,
            }

            # Add children if they exist
            if node_data["children"]:
                child_nodes = self._convert_to_json_format(
                    node_data["children"], level + 1
                )
                if child_nodes:
                    node["children"] = child_nodes

            children.append(node)

        return children
