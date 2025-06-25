"""Basic Query Filtering Examples.

This module demonstrates how to filter data using queries before pattern analysis.
Query filtering reduces the dataset to only the records that match your criteria.
"""

from dataspot import Dataspot

# Sample e-commerce transaction data
ecommerce_data = [
    {
        "country": "US",
        "device": "mobile",
        "user_type": "premium",
        "amount": 100,
        "category": "electronics",
    },
    {
        "country": "US",
        "device": "mobile",
        "user_type": "premium",
        "amount": 200,
        "category": "books",
    },
    {
        "country": "US",
        "device": "desktop",
        "user_type": "free",
        "amount": 50,
        "category": "electronics",
    },
    {
        "country": "EU",
        "device": "mobile",
        "user_type": "free",
        "amount": 75,
        "category": "clothing",
    },
    {
        "country": "EU",
        "device": "tablet",
        "user_type": "premium",
        "amount": 150,
        "category": "electronics",
    },
    {
        "country": "CA",
        "device": "mobile",
        "user_type": "premium",
        "amount": 120,
        "category": "books",
    },
    {
        "country": "US",
        "device": "mobile",
        "user_type": "free",
        "amount": 80,
        "category": "clothing",
    },
    {
        "country": "EU",
        "device": "desktop",
        "user_type": "premium",
        "amount": 180,
        "category": "electronics",
    },
]


def example_single_field_query():
    """Filter by single field - analyze only US transactions."""
    print("=== Single Field Query Example ===")
    print("Analyzing only US transactions...")

    dataspot = Dataspot()
    query = {"country": "US"}
    patterns = dataspot.find(
        ecommerce_data, ["country", "device", "user_type"], query=query
    )

    print(f"Found {len(patterns)} patterns in US data:")
    for pattern in patterns[:5]:  # Show top 5
        print(f"  {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")
    print()


def example_multiple_field_query():
    """Filter by multiple fields - US mobile users only."""
    print("=== Multiple Field Query Example ===")
    print("Analyzing US mobile users only...")

    dataspot = Dataspot()
    query = {"country": "US", "device": "mobile"}
    patterns = dataspot.find(
        ecommerce_data, ["country", "device", "user_type"], query=query
    )

    print(f"Found {len(patterns)} patterns in US mobile data:")
    for pattern in patterns:
        print(f"  {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")
    print()


def example_list_value_query():
    """Filter by list of values - North American countries."""
    print("=== List Value Query Example ===")
    print("Analyzing North American countries (US and CA)...")

    dataspot = Dataspot()
    query = {"country": ["US", "CA"]}
    patterns = dataspot.find(ecommerce_data, ["country", "device"], query=query)

    print(f"Found {len(patterns)} patterns in North American data:")
    for pattern in patterns:
        print(f"  {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")
    print()


def example_mixed_query_types():
    """Mix single values and lists - Premium users in US/EU on mobile/tablet."""
    print("=== Mixed Query Types Example ===")
    print("Analyzing premium users in US/EU using mobile or tablet...")

    dataspot = Dataspot()
    query = {
        "country": ["US", "EU"],
        "device": ["mobile", "tablet"],
        "user_type": "premium",
    }
    patterns = dataspot.find(
        ecommerce_data, ["country", "device", "user_type"], query=query
    )

    print(f"Found {len(patterns)} patterns in filtered data:")
    for pattern in patterns:
        print(f"  {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")
    print()


def example_no_query_comparison():
    """Compare results with and without query filtering."""
    print("=== Comparison: With vs Without Query ===")

    dataspot = Dataspot()

    # Without query
    all_patterns = dataspot.find(ecommerce_data, ["device", "user_type"])
    print(f"Without query - Total patterns: {len(all_patterns)}")
    print("Top 3 patterns:")
    for pattern in all_patterns[:3]:
        print(f"  {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")

    # With query
    query = {"country": "US"}
    filtered_patterns = dataspot.find(
        ecommerce_data, ["device", "user_type"], query=query
    )
    print(f"\nWith US query - Total patterns: {len(filtered_patterns)}")
    print("Top 3 patterns:")
    for pattern in filtered_patterns[:3]:
        print(f"  {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")
    print()


def example_tree_with_query():
    """Show how tree method works with query filtering."""
    import json

    print("=== Tree Structure with Query ===")
    print("Using tree() method for hierarchical visualization")

    dataspot = Dataspot()

    # Tree without query
    print("Complete tree structure:")
    tree_all = dataspot.tree(ecommerce_data, ["country", "device"], top=3)
    print(json.dumps(tree_all, indent=2))

    # Tree with query
    print("\nFiltered tree (US only):")
    query = {"country": "US"}
    tree_filtered = dataspot.tree(
        ecommerce_data, ["device", "user_type"], query=query, top=3
    )
    print(json.dumps(tree_filtered, indent=2))
    print()


if __name__ == "__main__":
    example_single_field_query()
    example_multiple_field_query()
    example_list_value_query()
    example_mixed_query_types()
    example_no_query_comparison()
    example_tree_with_query()
