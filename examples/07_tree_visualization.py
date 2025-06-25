"""Tree Visualization Examples.

This module demonstrates how to use the tree() method to build hierarchical
JSON structures for data visualization and analysis. Perfect for building
interactive dashboards, tree visualizations, and understanding data flow.
"""

import json

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
        "device": "mobile",
        "user_type": "premium",
        "amount": 150,
        "category": "electronics",
    },
    {
        "country": "US",
        "device": "desktop",
        "user_type": "free",
        "amount": 50,
        "category": "electronics",
    },
    {
        "country": "US",
        "device": "desktop",
        "user_type": "free",
        "amount": 75,
        "category": "books",
    },
    {
        "country": "EU",
        "device": "mobile",
        "user_type": "premium",
        "amount": 120,
        "category": "clothing",
    },
    {
        "country": "EU",
        "device": "mobile",
        "user_type": "free",
        "amount": 80,
        "category": "electronics",
    },
    {
        "country": "EU",
        "device": "tablet",
        "user_type": "premium",
        "amount": 180,
        "category": "electronics",
    },
    {
        "country": "EU",
        "device": "tablet",
        "user_type": "free",
        "amount": 90,
        "category": "clothing",
    },
    {
        "country": "CA",
        "device": "mobile",
        "user_type": "premium",
        "amount": 160,
        "category": "books",
    },
    {
        "country": "CA",
        "device": "desktop",
        "user_type": "premium",
        "amount": 220,
        "category": "electronics",
    },
    {
        "country": "AS",
        "device": "mobile",
        "user_type": "free",
        "amount": 70,
        "category": "clothing",
    },
]


def example_basic_tree():
    """Show a basic tree structure."""
    print("=== Basic Tree Structure ===")
    print("Building hierarchical tree for country → device → user_type")

    dataspot = Dataspot()
    tree = dataspot.tree(
        ecommerce_data, fields=["country", "device", "user_type"], top=5
    )

    print(json.dumps(tree, indent=2))
    print()


def example_filtered_tree():
    """Tree with filtering to show only significant patterns."""
    print("=== Filtered Tree (min_value=2) ===")
    print("Only showing patterns with at least 2 records")

    dataspot = Dataspot()
    tree = dataspot.tree(
        ecommerce_data, fields=["country", "device"], min_value=2, top=3
    )

    print(json.dumps(tree, indent=2))
    print()


def example_percentage_filtered_tree():
    """Tree filtered by percentage to focus on major concentrations."""
    print("=== Percentage Filtered Tree (min_percentage=20%) ===")
    print("Only showing patterns representing at least 20% of data")

    dataspot = Dataspot()
    tree = dataspot.tree(
        ecommerce_data, fields=["device", "user_type"], min_percentage=20.0, top=10
    )

    print(json.dumps(tree, indent=2))
    print()


def example_query_filtered_tree():
    """Tree with query pre-filtering for focused analysis."""
    print("=== Query Filtered Tree (US only) ===")
    print("Analyzing device and user patterns for US customers only")

    dataspot = Dataspot()
    tree = dataspot.tree(
        ecommerce_data,
        fields=["device", "user_type", "category"],
        query={"country": "US"},
        top=5,
    )

    print(json.dumps(tree, indent=2))
    print()


def example_tree_vs_patterns():
    """Compare tree structure vs pattern list for the same data."""
    print("=== Tree vs Patterns Comparison ===")

    dataspot = Dataspot()
    fields = ["country", "device"]

    # Get patterns (flat list)
    patterns = dataspot.find(ecommerce_data, fields, min_percentage=15)
    print("Patterns (flat list):")
    for pattern in patterns[:5]:
        print(f"  {pattern.path} → {pattern.percentage}% ({pattern.count} records)")

    print("\nTree (hierarchical JSON):")
    # Get tree (hierarchical structure)
    tree = dataspot.tree(ecommerce_data, fields, min_percentage=15, top=5)
    print(json.dumps(tree, indent=2))
    print()


def example_multi_level_analysis():
    """Deep tree analysis showing multiple levels of hierarchy."""
    print("=== Multi-Level Tree Analysis ===")
    print("4-level hierarchy: country → device → user_type → category")

    dataspot = Dataspot()
    tree = dataspot.tree(
        ecommerce_data,
        fields=["country", "device", "user_type", "category"],
        min_value=1,  # Include all patterns
        top=3,  # Top 3 at each level
    )

    print(json.dumps(tree, indent=2))
    print()


def example_tree_for_dashboard():
    """Tree structure optimized for dashboard visualization."""
    print("=== Dashboard-Ready Tree ===")
    print("Optimized tree for interactive dashboard with key metrics")

    dataspot = Dataspot()

    # Primary analysis - country breakdown
    country_tree = dataspot.tree(
        ecommerce_data, fields=["country", "device"], min_percentage=10, top=4
    )

    print("Country Breakdown:")
    print(json.dumps(country_tree, indent=2))

    # Secondary analysis - user behavior
    print("\n" + "=" * 50)
    user_tree = dataspot.tree(
        ecommerce_data, fields=["user_type", "category"], min_percentage=15, top=3
    )

    print("User Behavior Breakdown:")
    print(json.dumps(user_tree, indent=2))
    print()


def example_tree_insights():
    """Extract insights from tree structure."""
    print("=== Tree Insights Analysis ===")

    dataspot = Dataspot()
    tree = dataspot.tree(
        ecommerce_data, fields=["country", "device", "user_type"], top=3
    )

    print("Key Insights from Tree:")
    print(f"📊 Total records analyzed: {tree['value']}")
    print(f"🔝 Top level shows: {len(tree.get('children', []))} main patterns")

    # Analyze top country
    if tree.get("children"):
        top_country = tree["children"][0]
        print(
            f"🌍 Top concentration: {top_country['name']} with {top_country['percentage']}%"
        )

        # Analyze devices within top country
        if top_country.get("children"):
            top_device = top_country["children"][0]
            print(
                f"📱 Top device in {top_country['name']}: {top_device['name']} ({top_device['percentage']}%)"
            )

    print("\nFull Tree Structure:")
    print(json.dumps(tree, indent=2))
    print()


if __name__ == "__main__":
    example_basic_tree()
    example_filtered_tree()
    example_percentage_filtered_tree()
    example_query_filtered_tree()
    example_tree_vs_patterns()
    example_multi_level_analysis()
    example_tree_for_dashboard()
    example_tree_insights()
