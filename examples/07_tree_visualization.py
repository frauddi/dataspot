#!/usr/bin/env python3
"""Tree Visualization.

This example demonstrates how to use the Tree analyzer to create
hierarchical data structures for visualization purposes.
"""

from dataspot.analyzers.tree import Tree
from dataspot.models.tree import TreeInput, TreeOptions

# Sample e-commerce data
data = [
    {"country": "US", "device": "mobile", "category": "electronics"},
    {"country": "US", "device": "mobile", "category": "electronics"},
    {"country": "US", "device": "mobile", "category": "clothing"},
    {"country": "US", "device": "desktop", "category": "electronics"},
    {"country": "US", "device": "desktop", "category": "electronics"},
    {"country": "UK", "device": "mobile", "category": "electronics"},
    {"country": "UK", "device": "mobile", "category": "books"},
    {"country": "UK", "device": "desktop", "category": "books"},
    {"country": "DE", "device": "mobile", "category": "electronics"},
    {"country": "DE", "device": "tablet", "category": "clothing"},
]

print("🌳 Tree Visualization Examples\n")

# Basic tree visualization
print("1. Basic Tree Structure:")
tree_basic = Tree().execute(
    TreeInput(data=data, fields=["country", "device"]), TreeOptions(limit=3)
)

print(f"Root: {tree_basic.name}")
print(f"Top level children: {len(tree_basic.children)}")
for child in tree_basic.children:
    print(f"  - {child.name}: {child.value} records ({child.percentage:.1f}%)")

print("\n" + "=" * 50 + "\n")

# Tree with filters
print("2. Tree with Count Filter:")
tree_filtered = Tree().execute(
    TreeInput(data=data, fields=["country", "device", "category"]),
    TreeOptions(min_count=2, limit=3),
)

print(f"Filtered patterns: {tree_filtered.statistics.patterns_found}")
print("Country breakdown:")
for child in tree_filtered.children:
    print(f"  - {child.name}: {child.value} records")

print("\n" + "=" * 50 + "\n")

# Tree with percentage filter
print("3. Tree with Percentage Filter:")
tree_percentage = Tree().execute(
    TreeInput(data=data, fields=["country", "device"]),
    TreeOptions(limit=3),
)

print("High-concentration patterns:")
for child in tree_percentage.children:
    if child.percentage > 20:
        print(f"  - {child.name}: {child.percentage:.1f}%")

print("\n" + "=" * 50 + "\n")

# Tree with minimum percentage threshold
print("4. Tree with Minimum Percentage Threshold:")
tree_insights = Tree().execute(
    TreeInput(data=data, fields=["country", "device", "category"]),
    TreeOptions(min_percentage=15.0, limit=2),
)

print(f"Total records analyzed: {tree_insights.statistics.total_records}")
print(f"Patterns found: {tree_insights.statistics.patterns_found}")

if tree_insights.children:
    top_pattern = tree_insights.children[0]
    print(f"🌍 Top pattern: {top_pattern.name} ({top_pattern.percentage:.1f}%)")

print("\n" + "=" * 50 + "\n")

# Export tree as JSON for D3.js or other visualization libraries
print("5. JSON Export for Visualization Libraries:")
tree_json = Tree().execute(
    TreeInput(data=data, fields=["country", "device"]), TreeOptions(limit=3)
)

# Convert to dict for JSON export
tree_dict = tree_json.to_dict()
print("JSON structure keys:", list(tree_dict.keys()))
print(f"Ready for D3.js: {len(tree_dict['children'])} Top-level nodes")

# Example of how this could be used with D3.js
print("\n📊 Visualization Integration:")
print("This tree structure can be directly used with:")
print("- D3.js hierarchical layouts")
print("- Chart.js tree charts")
print("- React tree components")
print("- Custom visualization frameworks")

print("\nTree statistics:")
print(f"- Total records: {tree_json.statistics.total_records}")
print(f"- Patterns discovered: {tree_json.statistics.patterns_found}")
print(f"- Analysis depth: {len(tree_json.fields_analyzed)} levels")
