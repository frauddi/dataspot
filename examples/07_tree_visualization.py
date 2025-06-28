"""Tree Visualization Examples.

Shows how to use the tree() method to build hierarchical JSON structures for dashboards and visualization.
"""

import json

from dataspot import Dataspot
from dataspot.models.tree import TreeInput, TreeOptions

# Simple e-commerce data
data = [
    {
        "country": "US",
        "device": "mobile",
        "user_type": "premium",
        "category": "electronics",
    },
    {"country": "US", "device": "mobile", "user_type": "free", "category": "books"},
    {
        "country": "US",
        "device": "desktop",
        "user_type": "premium",
        "category": "electronics",
    },
    {
        "country": "EU",
        "device": "mobile",
        "user_type": "premium",
        "category": "clothing",
    },
    {
        "country": "EU",
        "device": "tablet",
        "user_type": "free",
        "category": "electronics",
    },
    {"country": "CA", "device": "mobile", "user_type": "premium", "category": "books"},
] * 2  # 12 records total


def main():
    """Tree visualization examples."""
    dataspot = Dataspot()

    print("=== 1. Basic Tree Structure ===")

    # Simple 2-level tree
    tree_basic = dataspot.tree(
        TreeInput(data=data, fields=["country", "device"]), TreeOptions(top=3)
    )
    print(f"Root value: {tree_basic.value} records")
    print(f"Top level children: {len(tree_basic.children)}")

    # Show tree as JSON
    print("\nTree structure:")
    tree_dict = tree_basic.to_dict()
    print(json.dumps(tree_dict, indent=2))

    print("\n=== 2. Filtered Tree ===")

    # Tree with filtering
    tree_filtered = dataspot.tree(
        TreeInput(data=data, fields=["country", "device", "user_type"]),
        TreeOptions(min_value=2, top=3),
    )
    print(f"Filtered tree children: {len(tree_filtered.children)}")

    print("\n=== 3. Query + Tree ===")

    # Tree with query filter
    tree_query = dataspot.tree(
        TreeInput(data=data, fields=["device", "user_type"], query={"country": "US"}),
        TreeOptions(top=3),
    )
    print(f"US-only tree value: {tree_query.value} records")
    print(f"US tree children: {len(tree_query.children)}")

    print("\n=== 4. Dashboard Structure ===")

    # Optimized for dashboard
    tree_dashboard = dataspot.tree(
        TreeInput(data=data, fields=["country", "device", "user_type"]),
        TreeOptions(min_percentage=15.0, top=2),
    )

    print("Dashboard-ready tree:")
    dashboard_dict = tree_dashboard.to_dict()
    print(json.dumps(dashboard_dict, indent=2))

    print("\n=== 5. Tree Insights ===")

    # Extract key insights
    tree_insights = dataspot.tree(
        TreeInput(data=data, fields=["country", "device"]), TreeOptions()
    )

    print(f"📊 Total records: {tree_insights.value}")
    print(f"🔝 Main patterns: {len(tree_insights.children)}")

    if tree_insights.children:
        top_pattern = tree_insights.children[0]
        print(f"🌍 Top pattern: {top_pattern.name} ({top_pattern.percentage:.1f}%)")


if __name__ == "__main__":
    main()
