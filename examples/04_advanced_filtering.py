"""Advanced Filtering Examples.

Shows how to combine query filters with pattern filters for complex analysis scenarios.
"""

from dataspot import Dataspot
from dataspot.models.finder import FindInput, FindOptions

# Simple sales data
data = [
    {
        "region": "north_america",
        "product": "laptop",
        "channel": "online",
        "segment": "enterprise",
    },
    {
        "region": "north_america",
        "product": "laptop",
        "channel": "retail",
        "segment": "enterprise",
    },
    {
        "region": "europe",
        "product": "tablet",
        "channel": "online",
        "segment": "consumer",
    },
    {
        "region": "europe",
        "product": "desktop",
        "channel": "retail",
        "segment": "enterprise",
    },
    {
        "region": "asia",
        "product": "laptop",
        "channel": "online",
        "segment": "enterprise",
    },
    {"region": "asia", "product": "tablet", "channel": "retail", "segment": "consumer"},
] * 4  # 24 records total


def main():
    """Advanced filtering examples."""
    dataspot = Dataspot()

    print("=== 1. Query + Pattern Filters ===")

    # Basic patterns (no filters)
    result_all = dataspot.find(
        FindInput(data=data, fields=["region", "product"]), FindOptions()
    )
    print(f"All patterns: {len(result_all.patterns)}")

    # Query filter + pattern filters
    result_filtered = dataspot.find(
        FindInput(
            data=data,
            fields=["region", "product", "channel"],
            query={"segment": "enterprise"},  # Query filter: enterprise only
        ),
        FindOptions(
            min_percentage=15.0,  # Pattern filter: at least 15%
            min_depth=2,  # Pattern filter: complex patterns only
            limit=5,  # Pattern filter: top 5 results
        ),
    )
    print(f"Enterprise + filtered: {len(result_filtered.patterns)}")

    print("\n=== 2. Progressive Filtering ===")

    # Step 1: Query filter only
    step1 = dataspot.find(
        FindInput(data=data, fields=["region", "product"], query={"channel": "online"}),
        FindOptions(),
    )
    print(f"Step 1 (online only): {len(step1.patterns)}")

    # Step 2: Add percentage threshold
    step2 = dataspot.find(
        FindInput(data=data, fields=["region", "product"], query={"channel": "online"}),
        FindOptions(min_percentage=20.0),
    )
    print(f"Step 2 (+ min 20%): {len(step2.patterns)}")

    # Step 3: Add text filter
    step3 = dataspot.find(
        FindInput(data=data, fields=["region", "product"], query={"channel": "online"}),
        FindOptions(min_percentage=20.0, contains="laptop"),
    )
    print(f"Step 3 (+ laptop only): {len(step3.patterns)}")

    print("\n=== 3. Comparative Analysis ===")

    # Compare online vs retail patterns
    online = dataspot.find(
        FindInput(data=data, fields=["region", "product"], query={"channel": "online"}),
        FindOptions(min_percentage=15.0),
    )

    retail = dataspot.find(
        FindInput(data=data, fields=["region", "product"], query={"channel": "retail"}),
        FindOptions(min_percentage=15.0),
    )

    print(f"Online patterns (≥15%): {len(online.patterns)}")
    print(f"Retail patterns (≥15%): {len(retail.patterns)}")

    print("\n=== 4. Complex Business Scenario ===")

    # Business question: "What are the key patterns for enterprise customers in major regions?"
    business_result = dataspot.find(
        FindInput(
            data=data,
            fields=["region", "product", "channel"],
            query={
                "region": ["north_america", "europe"],  # Major regions
                "segment": "enterprise",  # Enterprise only
            },
        ),
        FindOptions(
            min_percentage=10.0,  # Significant patterns
            exclude=["consumer"],  # Exclude consumer mentions
            limit=8,  # Top results
        ),
    )

    print(f"Business patterns: {len(business_result.patterns)}")
    for i, pattern in enumerate(business_result.patterns, 1):
        print(
            f"  {i}. {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)"
        )


if __name__ == "__main__":
    main()
