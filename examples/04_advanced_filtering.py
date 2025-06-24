"""Advanced Filtering Examples.

This module demonstrates advanced filtering scenarios including:
- Combining query filters with pattern filters
- Complex multi-criteria filtering
from dataspot import Dataspot
- Edge cases and filter interactions
- Real-world use cases
"""

# Sample sales data for advanced filtering examples
from dataspot import Dataspot

sales_data = []
regions = ["north_america", "europe", "asia_pacific", "latin_america"]
products = ["laptop", "desktop", "tablet", "smartphone", "accessories"]
channels = ["online", "retail", "partner", "direct"]
segments = ["enterprise", "mid_market", "small_business", "consumer"]

# Generate comprehensive sales data
for i in range(500):
    sales_data.append(
        {
            "region": regions[i % 4],
            "product": products[i % 5],
            "channel": channels[i % 4],
            "segment": segments[i % 4],
            "quarter": f"Q{(i % 4) + 1}",
            "rep_type": "senior" if i % 3 == 0 else "junior",
            "deal_size": "large" if i % 7 == 0 else "small",
            "revenue": (i % 10 + 1) * 1000,  # Varies from 1k to 10k
        }
    )


def example_query_plus_pattern_filters():
    """Combine query filtering with pattern filtering."""
    print("=== Query + Pattern Filters Example ===")
    print("Analyzing North America and Europe sales with specific criteria...")

    dataspot = Dataspot()

    # First filter data (query), then filter patterns
    advanced_patterns = dataspot.find(
        sales_data,
        ["region", "product", "channel", "segment"],
        query={"region": ["north_america", "europe"]},  # Query filter
        min_percentage=8,  # Pattern filter
        min_depth=2,  # Pattern filter
        contains="enterprise",  # Pattern filter
        limit=10,  # Pattern filter
    )

    print(f"Found {len(advanced_patterns)} patterns matching all criteria:")
    for pattern in advanced_patterns:
        print(f"  {pattern.path}")
        print(
            f"    Depth: {pattern.depth}, Count: {pattern.count}, "
            f"Percentage: {pattern.percentage:.1f}%"
        )
    print()


def example_multi_stage_filtering():
    """Demonstrate how filters work in stages."""
    print("=== Multi-Stage Filtering Example ===")

    dataspot = Dataspot()

    # Stage 1: All patterns
    all_patterns = dataspot.find(sales_data, ["region", "product", "channel"])
    print(f"Stage 1 - All patterns: {len(all_patterns)}")

    # Stage 2: Apply query filter
    query_filtered = dataspot.find(
        sales_data,
        ["region", "product", "channel"],
        query={"channel": ["online", "direct"]},
    )
    print(f"Stage 2 - After query filter: {len(query_filtered)}")

    # Stage 3: Apply pattern filters
    fully_filtered = dataspot.find(
        sales_data,
        ["region", "product", "channel"],
        query={"channel": ["online", "direct"]},
        min_percentage=10,
        min_count=20,
    )
    print(f"Stage 3 - After all filters: {len(fully_filtered)}")

    print("\nTop patterns after full filtering:")
    for pattern in fully_filtered[:5]:
        print(f"  {pattern.path} - {pattern.count} deals ({pattern.percentage:.1f}%)")
    print()


def example_complex_business_scenario():
    """Real-world business analysis scenario."""
    print("=== Complex Business Scenario Example ===")
    print("Finding high-value enterprise patterns in key regions...")

    dataspot = Dataspot()

    # Business question: "What are the most significant sales patterns for
    # enterprise customers in our top regions, excluding small deals?"
    business_patterns = dataspot.find(
        sales_data,
        ["region", "product", "channel", "segment", "rep_type"],
        query={
            "region": ["north_america", "europe", "asia_pacific"],
            "segment": "enterprise",
            "deal_size": "large",
        },
        min_percentage=5,
        max_depth=4,
        exclude="accessories",  # Focus on major products
        limit=15,
    )

    print(f"Enterprise patterns in key regions: {len(business_patterns)}")
    for pattern in business_patterns:
        print(f"  {pattern.path}")
        print(f"    Impact: {pattern.count} deals ({pattern.percentage:.1f}%)")
    print()


def example_comparative_analysis():
    """Compare different filter combinations."""
    print("=== Comparative Analysis Example ===")

    dataspot = Dataspot()

    # Compare online vs retail channel patterns
    online_patterns = dataspot.find(
        sales_data,
        ["product", "segment"],
        query={"channel": "online"},
        min_percentage=15,
    )

    retail_patterns = dataspot.find(
        sales_data,
        ["product", "segment"],
        query={"channel": "retail"},
        min_percentage=15,
    )

    print(f"Online channel patterns (≥15%): {len(online_patterns)}")
    print("Top online patterns:")
    for pattern in online_patterns[:3]:
        print(f"  {pattern.path} - {pattern.percentage:.1f}%")

    print(f"\nRetail channel patterns (≥15%): {len(retail_patterns)}")
    print("Top retail patterns:")
    for pattern in retail_patterns[:3]:
        print(f"  {pattern.path} - {pattern.percentage:.1f}%")
    print()


def example_progressive_filtering():
    """Progressively narrow down results."""
    print("=== Progressive Filtering Example ===")
    print("Progressively narrowing down to find specific patterns...")

    dataspot = Dataspot()

    # Step 1: Focus on enterprise segment
    step1 = dataspot.find(
        sales_data, ["region", "product", "channel"], query={"segment": "enterprise"}
    )
    print(f"Step 1 - Enterprise only: {len(step1)} patterns")

    # Step 2: Add minimum significance threshold
    step2 = dataspot.find(
        sales_data,
        ["region", "product", "channel"],
        query={"segment": "enterprise"},
        min_percentage=10,
    )
    print(f"Step 2 - + Min 10% significance: {len(step2)} patterns")

    # Step 3: Focus on complex patterns
    step3 = dataspot.find(
        sales_data,
        ["region", "product", "channel"],
        query={"segment": "enterprise"},
        min_percentage=10,
        min_depth=2,
    )
    print(f"Step 3 - + Min depth 2: {len(step3)} patterns")

    # Step 4: Exclude low-value items
    step4 = dataspot.find(
        sales_data,
        ["region", "product", "channel"],
        query={"segment": "enterprise"},
        min_percentage=10,
        min_depth=2,
        exclude="accessories",
    )
    print(f"Step 4 - + Exclude accessories: {len(step4)} patterns")

    print("\nFinal filtered patterns:")
    for pattern in step4:
        print(f"  {pattern.path} - {pattern.count} deals ({pattern.percentage:.1f}%)")
    print()


def example_edge_case_handling():
    """Handle edge cases and conflicting filters."""
    print("=== Edge Case Handling Example ===")

    dataspot = Dataspot()

    # Case 1: Conflicting percentage filters
    print("Case 1: Conflicting percentage filters (min > max)")
    conflicting = dataspot.find(
        sales_data, ["region"], min_percentage=50, max_percentage=30
    )
    print(f"Result: {len(conflicting)} patterns (should be 0)")

    # Case 2: Very restrictive filters
    print("\nCase 2: Very restrictive filters")
    restrictive = dataspot.find(
        sales_data, ["region", "product"], min_percentage=90, min_count=400
    )
    print(f"Result: {len(restrictive)} patterns (likely 0)")

    # Case 3: Query with no matches
    print("\nCase 3: Query with no matching records")
    no_match = dataspot.find(sales_data, ["region"], query={"region": "antarctica"})
    print(f"Result: {len(no_match)} patterns (should be 0)")

    # Case 4: Exclude everything
    print("\nCase 4: Exclude all possible values")
    exclude_all = dataspot.find(
        sales_data,
        ["region"],
        exclude=["north_america", "europe", "asia_pacific", "latin_america"],
    )
    print(f"Result: {len(exclude_all)} patterns (should be 0)")
    print()


def example_filter_optimization():
    """Show how filter order can affect performance."""
    print("=== Filter Optimization Example ===")
    print("Demonstrating efficient filter combinations...")

    dataspot = Dataspot()

    # Efficient: Query filter first (reduces dataset size)
    efficient_patterns = dataspot.find(
        sales_data,
        ["region", "product", "channel", "segment"],
        query={"quarter": "Q1"},  # Reduces data to 1/4
        min_percentage=10,
        min_depth=2,
        limit=5,
    )

    print(f"Efficient filtering: {len(efficient_patterns)} patterns")
    print("Results:")
    for pattern in efficient_patterns:
        print(f"  {pattern.path} - {pattern.percentage:.1f}%")

    # Note: The library handles optimization internally, but query filters
    # are conceptually applied first to reduce the analysis dataset
    print("\nNote: Query filters reduce the dataset before pattern analysis,")
    print("making subsequent pattern filters more efficient.")
    print()


def example_real_world_use_cases():
    """Practical real-world filtering scenarios."""
    print("=== Real-World Use Cases Example ===")

    dataspot = Dataspot()

    # Use case 1: Customer segmentation analysis
    print("Use Case 1: Customer Segmentation Analysis")
    segmentation = dataspot.find(
        sales_data,
        ["segment", "product", "channel"],
        query={"region": ["north_america", "europe"]},
        min_percentage=8,
        exclude="accessories",
        limit=8,
    )
    print(f"Key customer segments: {len(segmentation)} patterns")

    # Use case 2: Channel effectiveness
    print("\nUse Case 2: Channel Effectiveness Analysis")
    channels = dataspot.find(
        sales_data,
        ["channel", "segment", "product"],
        query={"deal_size": "large"},
        min_count=15,
        min_depth=2,
    )
    print(f"Effective channel patterns: {len(channels)} patterns")

    # Use case 3: Product performance
    print("\nUse Case 3: Product Performance Analysis")
    products = dataspot.find(
        sales_data,
        ["product", "region", "segment"],
        min_percentage=12,
        contains="enterprise",
        max_depth=3,
    )
    print(f"High-performing product patterns: {len(products)} patterns")
    print()


if __name__ == "__main__":
    example_query_plus_pattern_filters()
    example_multi_stage_filtering()
    example_complex_business_scenario()
    example_comparative_analysis()
    example_progressive_filtering()
    example_edge_case_handling()
    example_filter_optimization()
    example_real_world_use_cases()
