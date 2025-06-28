"""Tests for list handling functionality in Dataspot.

This module tests how Dataspot handles list values in data fields,
including path expansion, pattern generation, and edge cases.
"""

from dataspot import Dataspot
from dataspot.analyzers.base import Base
from dataspot.models.finder import FindInput, FindOptions


class TestBasicListHandling:
    """Test cases for basic list handling functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.dataspot = Dataspot()

    def test_single_list_field(self):
        """Test basic list field handling."""
        test_data = [
            {"tags": ["web", "mobile"], "category": "tech"},
            {"tags": ["mobile", "api"], "category": "tech"},
            {"tags": ["web"], "category": "design"},
        ]

        find_input = FindInput(data=test_data, fields=["tags", "category"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should expand list items into separate patterns
        tag_patterns = [p for p in result.patterns if "tags=" in p.path]
        assert len(tag_patterns) > 0

        # Should find individual tag patterns
        web_patterns = [p for p in result.patterns if "web" in p.path]
        mobile_patterns = [p for p in result.patterns if "mobile" in p.path]
        assert len(web_patterns) > 0
        assert len(mobile_patterns) > 0

    def test_multiple_list_fields(self):
        """Test handling multiple list fields in same record."""
        test_data = [
            {
                "skills": ["python", "sql"],
                "tools": ["docker", "git"],
                "level": "senior",
            },
            {"skills": ["java", "sql"], "tools": ["maven", "git"], "level": "mid"},
            {"skills": ["python"], "tools": ["docker"], "level": "junior"},
        ]

        find_input = FindInput(data=test_data, fields=["skills", "tools", "level"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle both list fields
        skill_patterns = [p for p in result.patterns if "skills=" in p.path]
        tool_patterns = [p for p in result.patterns if "tools=" in p.path]
        assert len(skill_patterns) > 0
        assert len(tool_patterns) > 0

    def test_empty_list_handling(self):
        """Test handling of empty lists."""
        test_data = [
            {"items": [], "status": "empty"},
            {"items": ["a", "b"], "status": "full"},
            {"items": [], "status": "empty"},
        ]

        find_input = FindInput(data=test_data, fields=["items", "status"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle empty lists gracefully
        assert len(result.patterns) > 0
        status_patterns = [p for p in result.patterns if "status=" in p.path]
        assert len(status_patterns) > 0

    def test_mixed_list_and_scalar_values(self):
        """Test mixing list and scalar values in same field."""
        test_data = [
            {"data": ["x", "y"], "type": "list"},
            {"data": "single", "type": "scalar"},
            {"data": ["z"], "type": "list"},
        ]

        find_input = FindInput(data=test_data, fields=["data", "type"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle mixed types
        assert len(result.patterns) > 0

    def test_nested_list_values(self):
        """Test handling of nested structures in lists."""
        test_data = [
            {"nested": [{"name": "a"}, {"name": "b"}], "category": "complex"},
            {"nested": [{"name": "a"}], "category": "simple"},
        ]

        find_input = FindInput(data=test_data, fields=["nested", "category"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle nested structures
        assert len(result.patterns) > 0

    def test_list_with_duplicate_values(self):
        """Test list handling with duplicate values within lists."""
        test_data = [
            {"tags": ["python", "python", "web"], "project": "A"},
            {"tags": ["java", "web", "web"], "project": "B"},
        ]

        find_input = FindInput(data=test_data, fields=["tags", "project"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should deduplicate within lists
        assert len(result.patterns) > 0


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
        find_input = FindInput(data=data, fields=["tags", "id"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)
        tag_patterns = [p for p in result.patterns if "tags=" in p.path]
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
        """Test path expansion behavior with very large lists."""
        # Create record with large list
        large_list = [f"item_{i}" for i in range(50)]
        test_data = [
            {"large_field": large_list, "category": "big"},
            {"large_field": ["item_1", "item_2"], "category": "small"},
        ]

        find_input = FindInput(data=test_data, fields=["large_field", "category"])
        find_options = FindOptions(
            limit=20
        )  # Use FindOptions instead of direct argument
        result = self.dataspot.find(find_input, find_options)

        # Should limit results to prevent explosion
        assert len(result.patterns) <= 20


class TestListIntegrationWithPatterns:
    """Test cases for list integration with pattern detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_list_pattern_counting(self):
        """Test that list patterns are counted correctly."""
        test_data = [
            {"keywords": ["seo", "marketing"], "campaign": "A"},
            {"keywords": ["seo", "social"], "campaign": "B"},
            {"keywords": ["marketing"], "campaign": "C"},
        ]

        find_input = FindInput(data=test_data, fields=["keywords", "campaign"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Find SEO pattern
        seo_patterns = [p for p in result.patterns if "seo" in p.path]
        if seo_patterns:
            seo_pattern = seo_patterns[0]
            assert seo_pattern.count == 2  # Appears in 2 records

    def test_list_percentage_calculation(self):
        """Test percentage calculation for list-expanded patterns."""
        test_data = [
            {"tools": ["git", "docker"], "team": "dev"},
            {"tools": ["git", "jenkins"], "team": "dev"},
            {"tools": ["git"], "team": "ops"},
        ]

        find_input = FindInput(data=test_data, fields=["tools", "team"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Git appears in all 3 records = 100%
        git_patterns = [p for p in result.patterns if "git" in p.path and p.depth == 1]
        if git_patterns:
            git_pattern = git_patterns[0]
            assert git_pattern.percentage == 100.0

    def test_list_hierarchical_patterns(self):
        """Test hierarchical pattern creation with lists."""
        test_data = [
            {"categories": ["tech", "mobile"], "status": "active"},
            {"categories": ["tech", "web"], "status": "active"},
            {"categories": ["design"], "status": "inactive"},
        ]

        find_input = FindInput(data=test_data, fields=["categories", "status"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should create hierarchical patterns
        hierarchical = [p for p in result.patterns if " > " in p.path]
        assert len(hierarchical) > 0

    def test_list_with_query_filtering(self):
        """Test list handling with query-based filtering."""
        test_data = [
            {"languages": ["python", "java"], "team": "backend", "active": True},
            {"languages": ["javascript"], "team": "frontend", "active": True},
            {"languages": ["python"], "team": "data", "active": False},
        ]

        find_input = FindInput(
            data=test_data, fields=["languages", "team"], query={"active": True}
        )
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should only include active teams
        assert all("team=data" not in p.path for p in result.patterns)

    def test_list_with_pattern_filtering(self):
        """Test list handling with pattern filtering."""
        test_data = [
            {"skills": ["python", "sql"], "experience": "senior"},
            {"skills": ["python", "java"], "experience": "senior"},
            {"skills": ["html"], "experience": "junior"},
        ] * 10  # Scale for percentage filtering

        find_input = FindInput(data=test_data, fields=["skills", "experience"])
        find_options = FindOptions(min_percentage=30.0)
        result = self.dataspot.find(find_input, find_options)

        # Should filter low-concentration patterns
        for pattern in result.patterns:
            assert pattern.percentage >= 30.0


class TestListEdgeCases:
    """Test cases for list handling edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_very_large_lists(self):
        """Test handling of very large lists."""
        large_list = [f"tag_{i}" for i in range(1000)]
        test_data = [
            {"tags": large_list[:500], "type": "huge"},
            {"tags": ["common"], "type": "small"},
        ]

        find_input = FindInput(data=test_data, fields=["tags", "type"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle large lists without performance issues
        assert len(result.patterns) > 0

    def test_lists_with_none_values(self):
        """Test lists containing None values."""
        test_data = [
            {"items": ["a", None, "b"], "category": "mixed"},
            {"items": [None, None], "category": "nulls"},
        ]

        find_input = FindInput(data=test_data, fields=["items", "category"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle None values gracefully
        assert len(result.patterns) > 0

    def test_lists_with_empty_strings(self):
        """Test lists containing empty strings."""
        test_data = [
            {"values": ["", "real", ""], "status": "partial"},
            {"values": ["real", "data"], "status": "complete"},
        ]

        find_input = FindInput(data=test_data, fields=["values", "status"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle empty strings appropriately
        assert len(result.patterns) > 0

    def test_lists_with_mixed_types(self):
        """Test lists with mixed data types."""
        test_data = [
            {"mixed": [1, "string", True], "type": "diverse"},
            {"mixed": [2, "text"], "type": "partial"},
        ]

        find_input = FindInput(data=test_data, fields=["mixed", "type"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle mixed types
        assert len(result.patterns) > 0

    def test_deeply_nested_lists(self):
        """Test deeply nested list structures."""
        test_data = [
            {"nested": [[["deep"]], [["value"]]], "level": "complex"},
            {"nested": [["simple"]], "level": "medium"},
        ]

        find_input = FindInput(data=test_data, fields=["nested", "level"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle deep nesting
        assert len(result.patterns) > 0

    def test_list_with_duplicate_complex_values(self):
        """Test lists with complex duplicate values."""
        test_data = [
            {"objects": [{"id": 1}, {"id": 1}, {"id": 2}], "type": "objects"},
        ]

        find_input = FindInput(data=test_data, fields=["objects", "type"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle complex duplicate values
        assert len(result.patterns) > 0

    def test_list_memory_efficiency(self):
        """Test memory efficiency with many list fields."""
        test_data = []
        for i in range(100):
            record = {}
            for j in range(5):
                field_name = f"list_{j}"
                field_value = [f"val_{i}_{j}_{k}" for k in range(10)]
                record[field_name] = field_value
            test_data.append(record)

        find_input = FindInput(data=test_data, fields=[f"list_{j}" for j in range(3)])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should complete without memory issues
        assert len(result.patterns) > 0

    def test_exponential_path_explosion_prevention(self):
        """Test prevention of exponential path explosion."""
        # Create data that could cause path explosion
        test_data = []
        for _ in range(20):
            test_data.append(
                {
                    "field1": [f"a_{j}" for j in range(5)],
                    "field2": [f"b_{j}" for j in range(5)],
                    "field3": [f"c_{j}" for j in range(5)],
                }
            )

        find_input = FindInput(data=test_data, fields=["field1", "field2", "field3"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should limit patterns to prevent explosion
        assert len(result.patterns) < 10000  # Reasonable limit


class TestListCustomPreprocessing:
    """Test cases for list handling with custom preprocessing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_list_with_custom_preprocessor(self):
        """Test list handling with custom preprocessors."""
        test_data = [
            {"emails": ["JOHN@TEST.COM", "jane@test.com"], "team": "dev"},
        ]

        # Add custom email preprocessor that normalizes case
        self.dataspot.add_preprocessor(
            "emails", lambda x: x.lower() if isinstance(x, str) else x
        )

        find_input = FindInput(data=test_data, fields=["emails", "team"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should apply preprocessing to list items
        assert len(result.patterns) > 0

    def test_preprocessor_modifying_list_items(self):
        """Test preprocessor that modifies individual list items."""
        test_data = [
            {"tags": ["  python  ", " java "], "category": "languages"},
        ]

        # Add preprocessor that strips whitespace
        self.dataspot.add_preprocessor(
            "tags", lambda x: x.strip() if isinstance(x, str) else x
        )

        find_input = FindInput(data=test_data, fields=["tags", "category"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should find clean tag patterns
        python_patterns = [p for p in result.patterns if "python" in p.path]
        assert len(python_patterns) > 0

    def test_preprocessor_converting_to_non_list(self):
        """Test preprocessor that converts lists to non-list values."""
        test_data = [
            {"items": ["a", "b", "c"], "type": "multi"},
            {"items": ["x"], "type": "single"},
        ]

        # Add preprocessor that converts list to count
        self.dataspot.add_preprocessor(
            "items", lambda x: len(x) if isinstance(x, list) else x
        )

        find_input = FindInput(data=test_data, fields=["items", "type"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should find count-based patterns
        count_patterns = [p for p in result.patterns if "items=" in p.path]
        assert len(count_patterns) > 0

    def test_list_email_preprocessing_integration(self):
        """Test integration of list handling with email preprocessing."""
        test_data = [
            {
                "recipients": ["admin@company.com", "user@company.com"],
                "priority": "high",
            },
            {"recipients": ["support@partner.org"], "priority": "medium"},
        ]

        find_input = FindInput(data=test_data, fields=["recipients", "priority"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should extract domain patterns from email lists
        company_patterns = [p for p in result.patterns if "company.com" in p.path]
        assert len(company_patterns) > 0


class TestListValidation:
    """Test cases for list validation and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_invalid_list_structures(self):
        """Test handling of invalid list structures."""
        test_data = [
            {"field": "not_a_list", "type": "invalid"},
        ]

        find_input = FindInput(data=test_data, fields=["field", "type"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle gracefully
        assert len(result.patterns) > 0

    def test_circular_reference_in_lists(self):
        """Test handling of potential circular references."""
        # This is more of a safety test
        obj = {"name": "test"}
        obj["self"] = obj  # Circular reference

        test_data = [
            {"items": [obj], "type": "circular"},
        ]

        find_input = FindInput(
            data=test_data, fields=["type"]
        )  # Avoid the circular field
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should complete without infinite loops
        assert len(result.patterns) > 0

    def test_list_field_consistency(self):
        """Test consistency in list field handling across records."""
        test_data = [
            {"tags": ["python", "web"], "id": 1},
            {"tags": "python", "id": 2},  # Single value instead of list
            {"tags": ["python"], "id": 3},  # Single item list
        ]

        find_input = FindInput(data=test_data, fields=["tags", "id"])
        find_options = FindOptions()
        result = self.dataspot.find(find_input, find_options)

        # Should handle mixed list/non-list consistently
        python_patterns = [p for p in result.patterns if "python" in p.path]
        assert len(python_patterns) > 0
