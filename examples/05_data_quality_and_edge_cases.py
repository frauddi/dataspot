"""Data Quality and Edge Cases Examples.

Shows how Dataspot handles various data quality issues like None values, mixed types, and edge cases.
"""

from dataspot import Dataspot
from dataspot.models.finder import FindInput, FindOptions


def main():
    """Test data quality and edge cases."""
    dataspot = Dataspot()

    print("=== 1. None Value Handling ===")

    # Data with None values
    data_with_nones = [
        {"status": "active", "region": "US", "type": "premium"},
        {"status": None, "region": "US", "type": "free"},
        {"status": "active", "region": None, "type": "premium"},
        {"status": "inactive", "region": "EU", "type": None},
        {"status": None, "region": None, "type": "free"},
    ]

    result_nones = dataspot.find(
        FindInput(data=data_with_nones, fields=["status", "region"]), FindOptions()
    )
    print(f"Patterns with None values: {len(result_nones.patterns)}")

    for pattern in result_nones.patterns[:3]:
        print(f"  {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")

    print("\n=== 2. Mixed Data Types ===")

    # Data with mixed types
    mixed_data = [
        {"id": 1, "active": True, "score": "high"},
        {"id": "1", "active": "true", "score": "high"},
        {"id": 2, "active": False, "score": "low"},
        {"id": "2", "active": 0, "score": "low"},
    ]

    result_mixed = dataspot.find(
        FindInput(data=mixed_data, fields=["id", "active"]), FindOptions()
    )
    print(f"Mixed type patterns: {len(result_mixed.patterns)}")

    for pattern in result_mixed.patterns:
        print(f"  {pattern.path} - {pattern.count} records")

    print("\n=== 3. Missing Fields ===")

    # Data with missing fields
    incomplete_data = [
        {"name": "Alice", "age": 25, "dept": "Engineering"},
        {"name": "Bob", "age": 30},  # Missing dept
        {"name": "Charlie", "dept": "Sales"},  # Missing age
        {"age": 35, "dept": "Marketing"},  # Missing name
    ]

    result_incomplete = dataspot.find(
        FindInput(data=incomplete_data, fields=["dept", "age"]), FindOptions()
    )
    print(f"Incomplete data patterns: {len(result_incomplete.patterns)}")

    for pattern in result_incomplete.patterns:
        print(f"  {pattern.path} - {pattern.count} records")

    print("\n=== 4. Edge Cases ===")

    # Empty dataset
    result_empty = dataspot.find(
        FindInput(data=[], fields=["field1", "field2"]), FindOptions()
    )
    print(f"Empty dataset patterns: {len(result_empty.patterns)}")

    # Single record
    single_record = [{"type": "unique", "value": "only"}]
    result_single = dataspot.find(
        FindInput(data=single_record, fields=["type", "value"]), FindOptions()
    )
    print(f"Single record patterns: {len(result_single.patterns)}")

    # Query with non-existent value
    test_data = [{"region": "US", "product": "laptop"}]
    result_no_match = dataspot.find(
        FindInput(data=test_data, fields=["region"], query={"region": "Mars"}),
        FindOptions(),
    )
    print(f"Non-existent query patterns: {len(result_no_match.patterns)}")

    print("\n=== 5. Special Characters ===")

    # Data with special characters
    special_data = [
        {"email": "user@domain.com", "action": "login"},
        {"email": "user with spaces", "action": "logout"},
        {"email": "user/with/slashes", "action": "view_page"},
        {"email": "üser_with_ümlauts", "action": "purchase"},
    ]

    result_special = dataspot.find(
        FindInput(data=special_data, fields=["email", "action"]),
        FindOptions(contains="@"),
    )
    print(f"Email patterns (contains @): {len(result_special.patterns)}")

    for pattern in result_special.patterns:
        print(f"  {pattern.path} - {pattern.count} records")


if __name__ == "__main__":
    main()
