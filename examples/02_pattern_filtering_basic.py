"""Pattern Filtering Examples.

Shows how to filter patterns after analysis using metrics like percentage, count, and depth.
"""

from dataspot import Dataspot
from dataspot.models.finder import FindInput, FindOptions

# Simple support data
data = [
    {"category": "technical", "priority": "high", "status": "open"},
    {"category": "technical", "priority": "high", "status": "resolved"},
    {"category": "technical", "priority": "medium", "status": "open"},
    {"category": "billing", "priority": "low", "status": "closed"},
    {"category": "billing", "priority": "medium", "status": "open"},
    {"category": "feature", "priority": "low", "status": "closed"},
] * 5  # 30 records total


def main():
    """Pattern filtering examples."""
    dataspot = Dataspot()

    print("=== 1. Percentage Filtering ===")

    # All patterns
    result_all = dataspot.find(
        FindInput(data=data, fields=["category", "priority"]), FindOptions()
    )
    print(f"All patterns: {len(result_all.patterns)}")

    # High percentage patterns only
    result_high = dataspot.find(
        FindInput(data=data, fields=["category", "priority"]),
        FindOptions(min_percentage=30.0),
    )
    print(f"≥30% patterns: {len(result_high.patterns)}")

    print("\n=== 2. Count and Depth Filtering ===")

    # At least 8 records
    result_count = dataspot.find(
        FindInput(data=data, fields=["category", "priority", "status"]),
        FindOptions(min_count=8),
    )
    print(f"≥8 records: {len(result_count.patterns)}")

    # Depth 2 only (more complex patterns)
    result_depth = dataspot.find(
        FindInput(data=data, fields=["category", "priority", "status"]),
        FindOptions(min_depth=2, max_depth=2),
    )
    print(f"Depth 2: {len(result_depth.patterns)}")

    print("\n=== 3. Combined Filters ===")

    # Multiple criteria: at least 15%, at least 5 records, limit to top 3
    result_combined = dataspot.find(
        FindInput(data=data, fields=["category", "priority", "status"]),
        FindOptions(min_percentage=15.0, min_count=5, limit=3),
    )
    print(f"Combined filters: {len(result_combined.patterns)}")

    # Show top patterns
    for i, pattern in enumerate(result_combined.patterns, 1):
        print(
            f"  {i}. {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)"
        )


if __name__ == "__main__":
    main()
