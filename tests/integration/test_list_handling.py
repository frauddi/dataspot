"""Tests for list handling functionality in Dataspot.

This module tests how Dataspot handles list values in data fields,
including path expansion, pattern generation, and edge cases.
"""

from typing import Any

from dataspot import Dataspot
from dataspot.analyzers.base import Base


class TestBasicListHandling:
    """Test cases for basic list handling functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.dataspot = Dataspot()

    def test_single_list_field(self):
        """Test handling of single field containing lists."""
        list_data = [
            {"tags": ["premium", "new"], "user_id": 1},
            {"tags": ["free"], "user_id": 2},
            {"tags": ["premium", "active"], "user_id": 3},
        ]

        patterns = self.dataspot.find(list_data, ["tags", "user_id"])

        # Should expand list values into separate patterns
        assert len(patterns) > 0

        # Should find patterns for individual tag values
        tag_patterns = [p for p in patterns if "tags=" in p.path]
        assert len(tag_patterns) > 0

        # Should find "premium" tag in multiple records
        premium_patterns = [p for p in patterns if "tags=premium" in p.path]
        assert len(premium_patterns) > 0

    def test_multiple_list_fields(self):
        """Test handling of multiple fields containing lists."""
        multi_list_data = [
            {"tags": ["tech", "ai"], "categories": ["software", "ml"], "id": 1},
            {"tags": ["tech"], "categories": ["software"], "id": 2},
            {"tags": ["ai", "research"], "categories": ["ml", "academic"], "id": 3},
        ]

        patterns = self.dataspot.find(multi_list_data, ["tags", "categories"])

        # Should create patterns for all combinations
        assert len(patterns) > 0

        # Should find combinations like tags=tech > categories=software
        combo_patterns = [
            p for p in patterns if "tags=" in p.path and "categories=" in p.path
        ]
        assert len(combo_patterns) > 0

    def test_empty_list_handling(self):
        """Test handling of empty lists."""
        empty_list_data = [
            {"tags": [], "category": "empty"},
            {"tags": ["active"], "category": "normal"},
            {"tags": [], "category": "also_empty"},
        ]

        patterns = self.dataspot.find(empty_list_data, ["tags", "category"])

        # Should handle empty lists gracefully
        assert len(patterns) > 0

        # Should find patterns for non-empty fields
        category_patterns = [p for p in patterns if "category=" in p.path]
        assert len(category_patterns) > 0

    def test_mixed_list_and_scalar_values(self):
        """Test handling of mixed list and scalar values in same field."""
        mixed_data = [
            {"field": ["a", "b"], "type": "list"},
            {"field": "single", "type": "scalar"},
            {"field": ["c"], "type": "single_item_list"},
        ]

        patterns = self.dataspot.find(mixed_data, ["field", "type"])

        # Should handle both list and scalar values
        assert len(patterns) > 0

        # Should find patterns for both list items and scalar values
        field_patterns = [p for p in patterns if "field=" in p.path]
        assert len(field_patterns) > 0

    def test_nested_list_values(self):
        """Test handling of nested lists (lists containing lists)."""
        nested_data = [
            {"nested": [["a", "b"], ["c"]], "id": 1},
            {"nested": [["d"]], "id": 2},
        ]

        patterns = self.dataspot.find(nested_data, ["nested", "id"])

        # Should handle nested structures (likely by string conversion)
        assert len(patterns) > 0

    def test_list_with_duplicate_values(self):
        """Test handling of lists containing duplicate values."""
        duplicate_data = [
            {"tags": ["premium", "premium", "active"], "user": "user1"},
            {"tags": ["free", "free"], "user": "user2"},
        ]

        patterns = self.dataspot.find(duplicate_data, ["tags", "user"])

        # Should handle duplicates in lists appropriately
        assert len(patterns) > 0

        # Behavior with duplicates may vary by implementation
        tag_patterns = [p for p in patterns if "tags=" in p.path]
        assert len(tag_patterns) > 0


class TestListPathExpansion:
    """Test cases for path expansion when lists are involved."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.base = Base()

    def test_path_expansion_single_list(self):
        """Test path expansion with single list field."""
        data = [{"tags": ["premium", "active"], "id": 1}]

        # Test internal path generation
        paths = self.base._get_record_paths(data[0], ["tags", "id"])

        # Should generate 2 paths (one for each tag)
        assert len(paths) == 2
        assert ["tags=premium", "id=1"] in paths
        assert ["tags=active", "id=1"] in paths

        # Test actual pattern finding
        patterns = self.dataspot.find(data, ["tags", "id"])
        tag_patterns = [p for p in patterns if "tags=" in p.path]
        assert len(tag_patterns) >= 2  # At least premium and active

    def test_path_expansion_multiple_lists(self):
        """Test path expansion with multiple list fields."""
        data = [
            {"tags": ["premium", "active"], "categories": ["tech", "business"], "id": 1}
        ]

        # Test internal path generation
        paths = self.base._get_record_paths(data[0], ["tags", "categories", "id"])

        # Should generate 4 paths (2 tags × 2 categories)
        assert len(paths) == 4
        expected_paths = [
            ["tags=premium", "categories=tech", "id=1"],
            ["tags=premium", "categories=business", "id=1"],
            ["tags=active", "categories=tech", "id=1"],
            ["tags=active", "categories=business", "id=1"],
        ]
        for expected_path in expected_paths:
            assert expected_path in paths

    def test_path_expansion_mixed_fields(self):
        """Test path expansion with mix of list and scalar fields."""
        data = [{"tags": ["premium", "active"], "scalar_field": "value", "id": 1}]

        # Test internal path generation
        paths = self.base._get_record_paths(data[0], ["tags", "scalar_field", "id"])

        # Should generate 2 paths (one for each tag)
        assert len(paths) == 2
        assert ["tags=premium", "scalar_field=value", "id=1"] in paths
        assert ["tags=active", "scalar_field=value", "id=1"] in paths

    def test_path_expansion_empty_list(self):
        """Test path expansion with empty list."""
        data = [{"empty_list": [], "scalar": "value"}]

        paths = self.base._get_record_paths(data[0], ["empty_list", "scalar"])

        # Empty lists should not generate any paths
        assert len(paths) == 0

    def test_path_expansion_large_lists(self):
        """Test path expansion with large lists (performance check)."""
        # Create record with relatively large lists
        large_tags = [f"tag_{i}" for i in range(20)]
        large_categories = [f"cat_{i}" for i in range(15)]
        data = [{"tags": large_tags, "categories": large_categories, "id": 1}]

        # Test internal path generation
        paths = self.base._get_record_paths(data[0], ["tags", "categories", "id"])

        # Should generate 20 × 15 = 300 paths
        assert len(paths) == 300

        # Sample some paths to verify correctness
        assert ["tags=tag_0", "categories=cat_0", "id=1"] in paths
        assert ["tags=tag_19", "categories=cat_14", "id=1"] in paths

        # Test that actual pattern finding still works (with limits)
        patterns = self.dataspot.find(data, ["tags", "categories"], limit=100)
        assert len(patterns) <= 100  # Should respect limit


class TestListIntegrationWithPatterns:
    """Test cases for list integration with pattern detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_list_pattern_counting(self):
        """Test that list patterns are counted correctly."""
        count_data = [
            {"tags": ["premium", "active"], "region": "US"},
            {"tags": ["premium"], "region": "US"},
            {"tags": ["free"], "region": "EU"},
        ]

        patterns = self.dataspot.find(count_data, ["tags", "region"])

        # Find premium tag pattern
        premium_patterns = [
            p for p in patterns if "tags=premium" in p.path and p.depth == 1
        ]
        assert len(premium_patterns) == 1

        # Premium appears in 2 records
        premium_pattern = premium_patterns[0]
        assert premium_pattern.count == 2

    def test_list_percentage_calculation(self):
        """Test percentage calculation with list values."""
        percentage_data = [
            {"tags": ["common"], "id": 1},
            {"tags": ["common"], "id": 2},
            {"tags": ["rare"], "id": 3},
            {"tags": ["common"], "id": 4},
        ]

        patterns = self.dataspot.find(percentage_data, ["tags"])

        # Find common tag pattern
        common_patterns = [p for p in patterns if "tags=common" in p.path]
        assert len(common_patterns) == 1

        common_pattern = common_patterns[0]
        # 3 out of 4 records = 75%
        assert common_pattern.percentage == 75.0

    def test_list_hierarchical_patterns(self):
        """Test hierarchical pattern generation with lists."""
        hierarchical_data = [
            {"tags": ["tech", "ai"], "level": "advanced", "status": "active"},
            {"tags": ["tech"], "level": "beginner", "status": "active"},
            {"tags": ["ai"], "level": "advanced", "status": "inactive"},
        ]

        patterns = self.dataspot.find(hierarchical_data, ["tags", "level", "status"])

        # Should create hierarchical patterns
        depth_2_patterns = [p for p in patterns if p.depth == 2]
        depth_3_patterns = [p for p in patterns if p.depth == 3]

        assert len(depth_2_patterns) > 0
        assert len(depth_3_patterns) > 0

        # Check specific hierarchical pattern
        tech_advanced = [
            p for p in patterns if "tags=tech" in p.path and "level=advanced" in p.path
        ]
        assert len(tech_advanced) > 0

    def test_list_with_query_filtering(self):
        """Test list handling with query filtering."""
        query_data = [
            {"tags": ["premium", "active"], "region": "US", "type": "user"},
            {"tags": ["premium"], "region": "EU", "type": "user"},
            {"tags": ["free"], "region": "US", "type": "trial"},
        ]

        # Filter for US region only
        patterns = self.dataspot.find(
            query_data, ["tags", "type"], query={"region": "US"}
        )

        # Should only include US records
        assert len(patterns) > 0

        # Should find premium tag from US records
        us_patterns = [p for p in patterns if "tags=premium" in p.path]
        assert len(us_patterns) > 0

    def test_list_with_pattern_filtering(self):
        """Test list handling with pattern filtering."""
        filter_data = []
        for i in range(100):
            filter_data.append(
                {"tags": [f"tag_{i % 5}", "common"], "category": f"cat_{i % 3}"}
            )

        # Apply pattern filtering
        patterns = self.dataspot.find(
            filter_data, ["tags", "category"], min_percentage=15
        )

        # Should filter out low-percentage patterns
        for pattern in patterns:
            assert pattern.percentage >= 15.0

        # Should include common patterns
        common_patterns = [p for p in patterns if "tags=common" in p.path]
        assert len(common_patterns) > 0


class TestListEdgeCases:
    """Test cases for list handling edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_very_large_lists(self):
        """Test handling of very large lists."""
        large_list_data = [{"large_list": [f"item_{i}" for i in range(100)], "id": 1}]

        patterns = self.dataspot.find(large_list_data, ["large_list", "id"])

        # Should handle large lists without performance issues
        assert len(patterns) > 0

        # Should create patterns for list items
        list_patterns = [p for p in patterns if "large_list=" in p.path]
        assert len(list_patterns) > 0

    def test_lists_with_none_values(self):
        """Test handling of lists containing None values."""
        none_list_data = [
            {"tags": ["valid", None, "also_valid"], "id": 1},
            {"tags": [None], "id": 2},
        ]

        patterns = self.dataspot.find(none_list_data, ["tags", "id"])

        # Should handle None values in lists
        assert len(patterns) > 0

    def test_lists_with_empty_strings(self):
        """Test handling of lists containing empty strings."""
        empty_string_data = [
            {"tags": ["valid", "", "also_valid"], "id": 1},
            {"tags": [""], "id": 2},
        ]

        patterns = self.dataspot.find(empty_string_data, ["tags", "id"])

        # Should handle empty strings in lists
        assert len(patterns) > 0

    def test_lists_with_mixed_types(self):
        """Test handling of lists containing mixed data types."""
        mixed_type_data = [
            {"mixed": ["string", 123, True, None], "id": 1},
            {"mixed": [456, "another_string"], "id": 2},
        ]

        patterns = self.dataspot.find(mixed_type_data, ["mixed", "id"])

        # Should handle mixed types in lists (likely by string conversion)
        assert len(patterns) > 0

    def test_deeply_nested_lists(self):
        """Test handling of deeply nested list structures."""
        nested_data = [
            {"nested": [["a", ["b", "c"]], "d"], "id": 1},
            {"nested": [["e"]], "id": 2},
        ]

        patterns = self.dataspot.find(nested_data, ["nested", "id"])

        # Should handle nested structures (implementation-dependent)
        assert len(patterns) > 0

    def test_list_with_duplicate_complex_values(self):
        """Test handling of lists with duplicate complex values."""
        complex_duplicate_data = [
            {"items": [{"x": 1}, {"x": 1}, {"x": 2}], "id": 1},
            {"items": [{"x": 2}], "id": 2},
        ]

        patterns = self.dataspot.find(complex_duplicate_data, ["items", "id"])

        # Should handle complex duplicates (likely by string conversion)
        assert len(patterns) > 0

    def test_list_memory_efficiency(self):
        """Test memory efficiency with many list records."""
        # Create many records with lists
        many_lists_data = []
        for i in range(1000):
            many_lists_data.append(
                {"tags": [f"tag_{i % 10}", "common"], "category": f"cat_{i % 5}"}
            )

        patterns = self.dataspot.find(many_lists_data, ["tags", "category"])

        # Should handle many list records efficiently
        assert len(patterns) > 0
        assert isinstance(patterns, list)

    def test_exponential_path_explosion_prevention(self):
        """Test that exponential path explosion is handled gracefully."""
        # Create data that could cause exponential path explosion
        explosion_data = [
            {
                "field1": [f"a{i}" for i in range(10)],
                "field2": [f"b{i}" for i in range(10)],
                "field3": [f"c{i}" for i in range(10)],
            }
        ]

        # This would create 10 * 10 * 10 = 1000 paths
        patterns = self.dataspot.find(explosion_data, ["field1", "field2", "field3"])

        # Should handle without memory/performance issues
        assert len(patterns) > 0

        # Verify that paths were actually generated
        depth_3_patterns = [p for p in patterns if p.depth == 3]
        assert len(depth_3_patterns) > 0


class TestListCustomPreprocessing:
    """Test cases for list handling with custom preprocessing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_list_with_custom_preprocessor(self):
        """Test list handling when custom preprocessor returns list."""

        def list_preprocessor(value):
            if isinstance(value, str):
                return value.split(",")
            return value

        self.dataspot.add_preprocessor("tags", list_preprocessor)

        preprocessor_data = [
            {"tags": "premium,active,new", "id": 1},
            {"tags": "free", "id": 2},
        ]

        patterns = self.dataspot.find(preprocessor_data, ["tags", "id"])

        # Should handle preprocessor that converts string to list
        assert len(patterns) > 0

        # Should find individual tags
        premium_patterns = [p for p in patterns if "tags=premium" in p.path]
        assert len(premium_patterns) > 0

    def test_preprocessor_modifying_list_items(self):
        """Test custom preprocessor that modifies list items."""

        def uppercase_list_preprocessor(value):
            if isinstance(value, list):
                return [str(item).upper() for item in value]
            return value

        self.dataspot.add_preprocessor("tags", uppercase_list_preprocessor)

        uppercase_data = [
            {"tags": ["premium", "active"], "id": 1},
            {"tags": ["free"], "id": 2},
        ]

        patterns = self.dataspot.find(uppercase_data, ["tags", "id"])

        # Should find uppercase versions
        premium_patterns = [p for p in patterns if "tags=PREMIUM" in p.path]
        assert len(premium_patterns) > 0

    def test_preprocessor_converting_to_non_list(self):
        """Test custom preprocessor that converts list to non-list."""

        def join_preprocessor(value):
            if isinstance(value, list):
                return ",".join(str(item) for item in value)
            return value

        self.dataspot.add_preprocessor("tags", join_preprocessor)

        join_data = [
            {"tags": ["premium", "active"], "id": 1},
            {"tags": ["free"], "id": 2},
        ]

        patterns = self.dataspot.find(join_data, ["tags", "id"])

        # Should treat joined string as single value
        joined_patterns = [p for p in patterns if "tags=premium,active" in p.path]
        assert len(joined_patterns) > 0

    def test_list_email_preprocessing_integration(self):
        """Test list handling with email preprocessing."""
        email_list_data = [
            {
                "emails": ["john.doe@company.com", "jane.smith@company.com"],
                "department": "tech",
            },
            {"emails": ["admin@company.com"], "department": "ops"},
        ]

        # Add custom email preprocessor for the 'emails' field
        from dataspot.analyzers.preprocessors import email_preprocessor

        def list_email_preprocessor(value):
            if isinstance(value, list):
                # Apply email preprocessing to each item in the list
                result = []
                for item in value:
                    processed = email_preprocessor(item)
                    if isinstance(processed, list):
                        result.extend(processed)
                    else:
                        result.append(processed)
                return result
            return email_preprocessor(value)

        self.dataspot.add_preprocessor("emails", list_email_preprocessor)

        patterns = self.dataspot.find(email_list_data, ["emails", "department"])

        # Should apply email preprocessing to each email in list
        assert len(patterns) > 0

        # Should find patterns with email preprocessing applied
        email_patterns = [p for p in patterns if "emails=" in p.path]
        assert len(email_patterns) > 0


class TestListValidation:
    """Test cases for list validation and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_invalid_list_structures(self):
        """Test handling of invalid list-like structures."""
        invalid_data = [
            {"field": "not_a_list", "id": 1},
            {"field": 123, "id": 2},
            {"field": {"dict": "value"}, "id": 3},
        ]

        patterns = self.dataspot.find(invalid_data, ["field", "id"])

        # Should handle non-list values gracefully
        assert len(patterns) > 0

    def test_circular_reference_in_lists(self):
        """Test handling of circular references in list items."""
        circular_obj: dict[str, Any] = {"name": "circular"}
        circular_obj["self"] = circular_obj

        circular_data = [{"items": [circular_obj], "id": 1}]

        # Should handle circular references without infinite recursion
        patterns = self.dataspot.find(circular_data, ["items", "id"])
        assert len(patterns) > 0

    def test_list_field_consistency(self):
        """Test consistency when same field has lists and non-lists."""
        inconsistent_data = [
            {"field": ["a", "b"], "id": 1},
            {"field": "single_value", "id": 2},
            {"field": ["c"], "id": 3},
            {"field": None, "id": 4},
        ]

        patterns = self.dataspot.find(inconsistent_data, ["field", "id"])

        # Should handle mixed list/non-list values consistently
        assert len(patterns) > 0

        # Should find patterns for both list items and scalar values
        field_patterns = [p for p in patterns if "field=" in p.path]
        assert len(field_patterns) > 0
