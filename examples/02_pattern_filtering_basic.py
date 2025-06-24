"""Basic Pattern Filtering Examples.

This module demonstrates how to filter patterns after analysis based on metrics
like percentage, count, and depth. These filters help you focus on the most
relevant patterns.
from dataspot import Dataspot
"""

# Sample customer support ticket data
from dataspot import Dataspot

support_data = []
categories = ["technical", "billing", "account", "feature_request", "bug"]
priorities = ["low", "medium", "high", "critical"]
statuses = ["open", "in_progress", "resolved", "closed"]

# Generate realistic support ticket data
for i in range(100):
    support_data.append(
        {
            "category": categories[i % 5],  # 20 tickets per category
            "priority": priorities[i % 4],  # 25 tickets per priority
            "status": statuses[i % 4],  # 25 tickets per status
            "department": "support" if i < 60 else "engineering",  # 60-40 split
            "region": ["north", "south", "east", "west"][i % 4],  # 25 per region
        }
    )


def example_percentage_filtering():
    """Filter patterns by minimum percentage threshold."""
    print("=== Percentage Filtering Example ===")
    print("Finding patterns that represent at least 30% of the data...")

    dataspot = Dataspot()

    # Without percentage filter
    all_patterns = dataspot.find(support_data, ["category", "priority"])
    print(f"All patterns: {len(all_patterns)}")

    # With 30% minimum percentage filter
    high_percentage = dataspot.find(
        support_data, ["category", "priority"], min_percentage=30
    )
    print(f"Patterns with ≥30%: {len(high_percentage)}")

    for pattern in high_percentage:
        print(f"  {pattern.path} - {pattern.count} tickets ({pattern.percentage:.1f}%)")
    print()


def example_count_filtering():
    """Filter patterns by record count."""
    print("=== Count Filtering Example ===")
    print("Finding patterns with at least 15 tickets...")

    dataspot = Dataspot()

    # Filter for patterns with significant volume
    high_count = dataspot.find(
        support_data, ["category", "priority", "status"], min_count=15
    )
    print(f"Patterns with ≥15 tickets: {len(high_count)}")

    for pattern in high_count[:5]:  # Show top 5
        print(f"  {pattern.path} - {pattern.count} tickets ({pattern.percentage:.1f}%)")

    print("\nFinding patterns with exactly 20-30 tickets...")
    medium_count = dataspot.find(
        support_data, ["category", "priority"], min_count=20, max_count=30
    )
    print(f"Patterns with 20-30 tickets: {len(medium_count)}")

    for pattern in medium_count:
        print(f"  {pattern.path} - {pattern.count} tickets ({pattern.percentage:.1f}%)")
    print()


def example_depth_filtering():
    """Filter patterns by depth (complexity)."""
    print("=== Depth Filtering Example ===")
    print("Analyzing pattern complexity...")

    dataspot = Dataspot()

    # Show patterns at different depth levels
    for depth in [1, 2, 3]:
        patterns = dataspot.find(
            support_data,
            ["category", "priority", "status"],
            min_depth=depth,
            max_depth=depth,
        )
        print(f"Depth {depth} patterns: {len(patterns)}")
        for pattern in patterns[:3]:  # Show top 3 per depth
            print(
                f"  {pattern.path} - {pattern.count} tickets ({pattern.percentage:.1f}%)"
            )
        print()


def example_limit_filtering():
    """Limit the number of results returned."""
    print("=== Limit Filtering Example ===")
    print("Getting top 5 most significant patterns...")

    dataspot = Dataspot()

    # Get top 5 patterns only
    top_patterns = dataspot.find(
        support_data, ["category", "priority", "status"], limit=5
    )
    print(f"Top {len(top_patterns)} patterns:")

    for i, pattern in enumerate(top_patterns, 1):
        print(
            f"  {i}. {pattern.path} - {pattern.count} tickets ({pattern.percentage:.1f}%)"
        )
    print()


def example_combined_metrics():
    """Combine multiple metric filters."""
    print("=== Combined Metrics Example ===")
    print("Finding moderately complex patterns with good representation...")

    dataspot = Dataspot()

    # Find patterns that are:
    # - At least depth 2 (somewhat complex)
    # - At least 10% representation
    # - At least 10 tickets
    # - Top 8 results
    combined = dataspot.find(
        support_data,
        ["category", "priority", "status", "department"],
        min_depth=2,
        min_percentage=10,
        min_count=10,
        limit=8,
    )

    print(f"Found {len(combined)} patterns matching all criteria:")
    for pattern in combined:
        print(f"  {pattern.path}")
        print(
            f"    Depth: {pattern.depth}, Count: {pattern.count}, Percentage: {pattern.percentage:.1f}%"
        )
    print()


def example_percentage_ranges():
    """Find patterns within specific percentage ranges."""
    print("=== Percentage Range Example ===")
    print("Finding patterns that represent 15-35% of the data...")

    dataspot = Dataspot()

    # Find patterns in the "sweet spot" - not too rare, not too common
    medium_patterns = dataspot.find(
        support_data, ["category", "priority"], min_percentage=15, max_percentage=35
    )

    print(f"Patterns in 15-35% range: {len(medium_patterns)}")
    for pattern in medium_patterns:
        print(f"  {pattern.path} - {pattern.count} tickets ({pattern.percentage:.1f}%)")
    print()


if __name__ == "__main__":
    example_percentage_filtering()
    example_count_filtering()
    example_depth_filtering()
    example_limit_filtering()
    example_combined_metrics()
    example_percentage_ranges()
