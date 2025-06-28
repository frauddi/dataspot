"""Basic Query Filtering Examples.

Demonstrates filtering data before analysis using queries.
"""

from dataspot import Dataspot
from dataspot.models.finder import FindInput, FindOptions
from dataspot.models.tree import TreeInput, TreeOptions

# Simple e-commerce data
data = [
    {"country": "US", "device": "mobile", "user_type": "premium"},
    {"country": "US", "device": "mobile", "user_type": "free"},
    {"country": "US", "device": "desktop", "user_type": "free"},
    {"country": "EU", "device": "mobile", "user_type": "premium"},
    {"country": "EU", "device": "tablet", "user_type": "premium"},
    {"country": "CA", "device": "mobile", "user_type": "free"},
]


def main():
    """Query filtering examples."""
    dataspot = Dataspot()

    print("=== 1. Basic Query Filtering ===")

    # All patterns
    input_data = FindInput(data=data, fields=["country", "device"])
    result = dataspot.find(input_data, FindOptions())
    print(f"All patterns: {len(result.patterns)}")

    # Single field filter
    input_us = FindInput(
        data=data, fields=["country", "device"], query={"country": "US"}
    )
    result_us = dataspot.find(input_us, FindOptions())
    print(f"US only: {len(result_us.patterns)}")

    # Multiple fields filter
    input_us_mobile = FindInput(
        data=data,
        fields=["country", "device"],
        query={"country": "US", "device": "mobile"},
    )
    result_us_mobile = dataspot.find(input_us_mobile, FindOptions())
    print(f"US mobile: {len(result_us_mobile.patterns)}")

    # List values filter
    input_na = FindInput(
        data=data, fields=["country", "device"], query={"country": ["US", "CA"]}
    )
    result_na = dataspot.find(input_na, FindOptions())
    print(f"North America: {len(result_na.patterns)}")

    print("\n=== 2. Tree with Query ===")

    # Tree structure
    tree_input = TreeInput(
        data=data, fields=["country", "device"], query={"country": "US"}
    )
    tree = dataspot.tree(tree_input, TreeOptions())
    print(f"Tree value: {tree.value} records")
    print(f"Children: {len(tree.children)}")


if __name__ == "__main__":
    main()
