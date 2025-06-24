"""Data Quality and Edge Cases Examples.

This module demonstrates how Dataspot handles various data quality issues
and edge cases including:
- None/null values
from dataspot import Dataspot
- Type coercion
- Missing fields
- Empty datasets
- Mixed data types
"""

from dataspot import Dataspot


def example_none_value_handling():
    """Demonstrate how Dataspot handles None/null values."""
    print("=== None Value Handling Example ===")
    print("Analyzing data with None/null values...")

    # Data with None values
    data_with_nones = [
        {"status": "active", "region": "US", "type": "premium"},
        {"status": None, "region": "US", "type": "free"},
        {"status": "active", "region": None, "type": "premium"},
        {"status": "inactive", "region": "EU", "type": None},
        {"status": "active", "region": "US", "type": "premium"},
        {"status": None, "region": None, "type": "free"},
    ]

    dataspot = Dataspot()
    patterns = dataspot.find(data_with_nones, ["status", "region", "type"])

    print(f"Found {len(patterns)} patterns with None values:")
    for pattern in patterns[:8]:  # Show more patterns to see None handling
        print(f"  {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")

    # Query filtering with None values
    print("\nFiltering data where region is not None...")
    filtered = dataspot.find(
        data_with_nones, ["status", "type"], query={"region": "US"}
    )  # Only US records
    print(f"US-only patterns: {len(filtered)}")
    for pattern in filtered:
        print(f"  {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")
    print()


def example_type_coercion():
    """Demonstrate type coercion and mixed data types."""
    print("=== Type Coercion Example ===")
    print("Analyzing data with mixed types...")

    # Data with mixed types - strings, numbers, booleans
    mixed_type_data = [
        {"id": 1, "active": True, "score": "high", "category": "A"},
        {"id": "1", "active": "true", "score": "high", "category": "A"},
        {"id": 2, "active": False, "score": "low", "category": "B"},
        {"id": "2", "active": "false", "score": "low", "category": "B"},
        {"id": 3, "active": True, "score": "medium", "category": "A"},
        {"id": "3", "active": 1, "score": "medium", "category": "A"},
    ]

    dataspot = Dataspot()

    # Show how different representations are handled
    patterns = dataspot.find(mixed_type_data, ["id", "active"])
    print(f"Patterns with mixed types: {len(patterns)}")
    for pattern in patterns:
        print(f"  {pattern.path} - {pattern.count} records")

    # Query with type coercion
    print("\nQuerying with different types...")

    # Query with integer
    int_query = dataspot.find(mixed_type_data, ["active", "category"], query={"id": 1})
    print(f"Query id=1 (int): {len(int_query)} patterns")

    # Query with string
    str_query = dataspot.find(
        mixed_type_data, ["active", "category"], query={"id": "1"}
    )
    print(f"Query id='1' (str): {len(str_query)} patterns")
    print()


def example_missing_fields():
    """Handle records with missing fields."""
    print("=== Missing Fields Example ===")
    print("Analyzing data with inconsistent schema...")

    # Data with some records missing fields
    inconsistent_data = [
        {"name": "Alice", "age": 25, "department": "Engineering"},
        {"name": "Bob", "age": 30},  # Missing department
        {"name": "Charlie", "department": "Sales"},  # Missing age
        {"name": "Diana", "age": 28, "department": "Engineering"},
        {"name": "Eve"},  # Missing age and department
        {"age": 35, "department": "Marketing"},  # Missing name
    ]

    dataspot = Dataspot()

    # Analyze with fields that may be missing
    patterns = dataspot.find(inconsistent_data, ["department", "age"])
    print(f"Patterns with potentially missing fields: {len(patterns)}")
    for pattern in patterns:
        print(f"  {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")

    # Query for records with specific field values
    print("\nQuerying for specific department...")
    dept_patterns = dataspot.find(
        inconsistent_data, ["name", "age"], query={"department": "Engineering"}
    )
    print(f"Engineering patterns: {len(dept_patterns)}")
    for pattern in dept_patterns:
        print(f"  {pattern.path} - {pattern.count} records")
    print()


def example_empty_and_edge_datasets():
    """Handle empty and very small datasets."""
    print("=== Empty and Edge Datasets Example ===")

    dataspot = Dataspot()

    # Empty dataset
    print("1. Empty dataset:")
    empty_patterns = dataspot.find([], ["field1", "field2"])
    print(f"   Patterns from empty data: {len(empty_patterns)}")

    # Single record
    print("\n2. Single record:")
    single_record = [{"type": "unique", "value": "only"}]
    single_patterns = dataspot.find(single_record, ["type", "value"])
    print(f"   Patterns from single record: {len(single_patterns)}")
    for pattern in single_patterns:
        print(
            f"   {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)"
        )

    # Two identical records
    print("\n3. Two identical records:")
    identical_records = [
        {"status": "active", "type": "premium"},
        {"status": "active", "type": "premium"},
    ]
    identical_patterns = dataspot.find(identical_records, ["status", "type"])
    print(f"   Patterns from identical records: {len(identical_patterns)}")
    for pattern in identical_patterns:
        print(
            f"   {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)"
        )
    print()


def example_special_characters_and_strings():
    """Handle special characters and unusual strings."""
    print("=== Special Characters Example ===")
    print("Analyzing data with special characters...")

    # Data with special characters, spaces, and unusual strings
    special_data = [
        {"user": "user@domain.com", "action": "login", "device": "mobile"},
        {"user": "user with spaces", "action": "logout", "device": "desktop"},
        {"user": "user/with/slashes", "action": "view_page", "device": "tablet"},
        {"user": "user@domain.com", "action": "login", "device": "mobile"},
        {"user": "üser_with_ümlauts", "action": "purchase", "device": "mobile"},
        {"user": "user-with-dashes", "action": "login", "device": "desktop"},
    ]

    dataspot = Dataspot()

    patterns = dataspot.find(special_data, ["user", "action"])
    print(f"Patterns with special characters: {len(patterns)}")
    for pattern in patterns:
        print(f"  {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")

    # Filter patterns containing special characters
    print("\nFiltering patterns with @ symbol...")
    email_patterns = dataspot.find(special_data, ["user", "device"], contains="@")
    print(f"Email-related patterns: {len(email_patterns)}")
    for pattern in email_patterns:
        print(f"  {pattern.path} - {pattern.count} records")
    print()


def example_query_edge_cases():
    """Handle query edge cases and error handling."""
    print("=== Query Edge Cases Example ===")

    dataspot = Dataspot()

    test_data = [
        {"region": "US", "product": "laptop", "status": "active"},
        {"region": "EU", "product": "desktop", "status": "inactive"},
        {"region": "US", "product": "tablet", "status": "active"},
    ]

    # Query for non-existent values
    print("1. Query for non-existent values:")
    no_match = dataspot.find(test_data, ["region", "product"], query={"region": "Mars"})
    print(f"   Non-existent region patterns: {len(no_match)}")

    # Query for non-existent fields
    print("\n2. Query for non-existent fields:")
    no_field = dataspot.find(
        test_data, ["region", "product"], query={"nonexistent_field": "value"}
    )
    print(f"   Non-existent field patterns: {len(no_field)}")

    # Empty query
    print("\n3. Empty query:")
    empty_query = dataspot.find(test_data, ["region", "product"], query={})
    no_query = dataspot.find(test_data, ["region", "product"])
    print(f"   Empty query patterns: {len(empty_query)}")
    print(f"   No query patterns: {len(no_query)}")
    print(f"   Results are same: {len(empty_query) == len(no_query)}")

    # Query with empty list
    print("\n4. Query with empty list:")
    empty_list = dataspot.find(test_data, ["region", "product"], query={"region": []})
    print(f"   Empty list query patterns: {len(empty_list)}")
    print()


def example_large_dataset_behavior():
    """Test behavior with larger datasets."""
    print("=== Large Dataset Behavior Example ===")
    print("Testing with larger dataset...")

    # Generate larger dataset
    large_data = []
    for i in range(1000):
        large_data.append(
            {
                "category": f"cat_{i % 10}",  # 10 categories
                "subcategory": f"sub_{i % 25}",  # 25 subcategories
                "region": f"region_{i % 5}",  # 5 regions
                "status": "active" if i % 3 == 0 else "inactive",
            }
        )

    dataspot = Dataspot()

    # Analyze large dataset
    patterns = dataspot.find(large_data, ["category", "region", "status"])
    print(f"Total patterns from 1000 records: {len(patterns)}")

    # Apply filters to reduce results
    filtered = dataspot.find(
        large_data, ["category", "region", "status"], min_percentage=5, limit=10
    )
    print(f"Filtered patterns (≥5%, top 10): {len(filtered)}")

    # Check performance with complex filtering
    complex_filtered = dataspot.find(
        large_data,
        ["category", "subcategory", "region", "status"],
        min_count=20,
        contains="cat_",
        exclude="sub_0",
        limit=15,
    )
    print(f"Complex filtered patterns: {len(complex_filtered)}")

    print("Large dataset analysis completed successfully!")
    print()


if __name__ == "__main__":
    example_none_value_handling()
    example_type_coercion()
    example_missing_fields()
    example_empty_and_edge_datasets()
    example_special_characters_and_strings()
    example_query_edge_cases()
    example_large_dataset_behavior()
