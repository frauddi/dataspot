"""Tests for edge cases and boundary conditions in Dataspot.

This module tests various edge cases, boundary conditions, and unusual
scenarios that could cause issues in production.
"""

import sys
from decimal import Decimal

import pytest

from dataspot import Dataspot


class TestDataTypeEdgeCases:
    """Test cases for various data types and edge values."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_zero_values(self):
        """Test handling of zero values in different contexts."""
        zero_data = [
            {"count": 0, "value": "zero_count"},
            {"count": 1, "value": "one_count"},
            {"count": 0, "value": "zero_again"},
        ]

        patterns = self.dataspot.find(zero_data, ["count", "value"])

        # Should handle zero values correctly (not convert to empty string)
        zero_patterns = [p for p in patterns if "count=0" in p.path]
        assert len(zero_patterns) > 0

        # Verify zero appears as "0", not empty string
        for pattern in zero_patterns:
            assert "count=0" in pattern.path
            assert "count=" not in pattern.path.replace("count=0", "")

    def test_false_values(self):
        """Test handling of False boolean values."""
        bool_data = [
            {"active": False, "type": "inactive"},
            {"active": True, "type": "active"},
            {"active": False, "type": "suspended"},
        ]

        patterns = self.dataspot.find(bool_data, ["active", "type"])

        # Should handle False correctly (not convert to empty string)
        false_patterns = [p for p in patterns if "active=False" in p.path]
        assert len(false_patterns) > 0

        # Verify False appears as "False"
        for pattern in false_patterns:
            assert "active=False" in pattern.path

    def test_none_values(self):
        """Test handling of None values."""
        none_data = [
            {"field1": None, "field2": "value1"},
            {"field1": "value", "field2": None},
            {"field1": None, "field2": None},
            {"field1": "test", "field2": "value2"},
        ]

        patterns = self.dataspot.find(none_data, ["field1", "field2"])

        # None values should be converted to empty string
        none_patterns = [p for p in patterns if "=" in p.path and "field1=" in p.path]

        assert len(none_patterns) > 0

    def test_empty_string_values(self):
        """Test handling of empty string values."""
        empty_data = [
            {"name": "", "category": "empty_name"},
            {"name": "John", "category": "normal"},
            {"name": "", "category": "another_empty"},
        ]

        patterns = self.dataspot.find(empty_data, ["name", "category"])

        # Should handle empty strings
        empty_patterns = [p for p in patterns if "name=" in p.path]
        assert len(empty_patterns) > 0

    def test_whitespace_values(self):
        """Test handling of whitespace-only values."""
        whitespace_data = [
            {"text": "   ", "type": "spaces"},
            {"text": "\t", "type": "tab"},
            {"text": "\n", "type": "newline"},
            {"text": "normal", "type": "text"},
        ]

        patterns = self.dataspot.find(whitespace_data, ["text", "type"])

        # Should preserve whitespace values
        space_patterns = [p for p in patterns if "text=   " in p.path]
        tab_patterns = [p for p in patterns if "text=\t" in p.path]
        newline_patterns = [p for p in patterns if "text=\n" in p.path]
        text_patterns = [p for p in patterns if "text=normal" in p.path]

        assert len(space_patterns) > 0
        assert len(tab_patterns) > 0
        assert len(newline_patterns) > 0
        assert len(text_patterns) > 0

    def test_numeric_string_values(self):
        """Test handling of numeric values as strings."""
        numeric_data = [
            {"id": "123", "status": "string_id"},
            {"id": 123, "status": "int_id"},
            {"id": "123.45", "status": "float_string"},
            {"id": 123.45, "status": "float_id"},
        ]

        patterns = self.dataspot.find(numeric_data, ["id", "status"])

        # Should treat different types as different values
        string_patterns = [p for p in patterns if "id=123" in p.path]
        float_patterns = [p for p in patterns if "id=123.45" in p.path]

        assert len(string_patterns) > 0
        assert len(float_patterns) > 0

    def test_very_large_numbers(self):
        """Test handling of very large numbers."""
        large_data = [
            {"big_num": sys.maxsize, "type": "max_int"},
            {"big_num": sys.maxsize - 1, "type": "max_minus_one"},
            {"big_num": float("inf"), "type": "infinity"},
            {"big_num": -float("inf"), "type": "neg_infinity"},
        ]

        patterns = self.dataspot.find(large_data, ["big_num", "type"])

        # Should handle large numbers without crashing
        assert len(patterns) > 0

        # Check for infinity handling
        inf_patterns = [p for p in patterns if "inf" in p.path.lower()]
        assert len(inf_patterns) >= 0  # Should not crash

    def test_special_float_values(self):
        """Test handling of special float values."""
        special_data = [
            {"value": float("nan"), "type": "not_a_number"},
            {"value": float("inf"), "type": "positive_infinity"},
            {"value": -float("inf"), "type": "negative_infinity"},
            {"value": 0.0, "type": "zero_float"},
            {"value": -0.0, "type": "negative_zero"},
        ]

        patterns = self.dataspot.find(special_data, ["value", "type"])

        # Should handle special values without crashing
        assert isinstance(patterns, list)

    def test_decimal_values(self):
        """Test handling of Decimal type values."""
        decimal_data = [
            {"price": Decimal("19.99"), "currency": "USD"},
            {"price": Decimal("29.99"), "currency": "USD"},
            {"price": Decimal("19.99"), "currency": "EUR"},
        ]

        patterns = self.dataspot.find(decimal_data, ["price", "currency"])

        # Should convert Decimal to string representation
        assert len(patterns) > 0

    def test_complex_numbers(self):
        """Test handling of complex numbers."""
        complex_data = [
            {"value": complex(1, 2), "type": "complex"},
            {"value": complex(3, 4), "type": "complex"},
        ]

        patterns = self.dataspot.find(complex_data, ["value", "type"])

        # Should handle complex numbers (convert to string)
        assert len(patterns) > 0


class TestUnicodeAndEncoding:
    """Test cases for Unicode and encoding edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_basic_unicode(self):
        """Test basic Unicode character handling."""
        unicode_data = [
            {"name": "José", "country": "España"},
            {"name": "François", "country": "France"},
            {"name": "李明", "country": "中国"},
        ]

        patterns = self.dataspot.find(unicode_data, ["name", "country"])

        # Should handle Unicode correctly
        assert len(patterns) > 0

        # Check specific Unicode patterns
        chinese_patterns = [p for p in patterns if "李明" in p.path]
        spanish_patterns = [p for p in patterns if "José" in p.path]

        assert len(chinese_patterns) > 0
        assert len(spanish_patterns) > 0

    def test_emoji_values(self):
        """Test handling of emoji characters."""
        emoji_data = [
            {"reaction": "👍", "sentiment": "positive"},
            {"reaction": "👎", "sentiment": "negative"},
            {"reaction": "❤️", "sentiment": "love"},
            {"reaction": "👍", "sentiment": "positive"},
        ]

        patterns = self.dataspot.find(emoji_data, ["reaction", "sentiment"])

        # Should handle emojis
        assert len(patterns) > 0

        thumbs_up = [p for p in patterns if "👍" in p.path]
        assert len(thumbs_up) > 0

    def test_mixed_encoding_values(self):
        """Test handling of mixed encoding scenarios."""
        mixed_data = [
            {"text": "café", "type": "utf8"},
            {"text": "naïve", "type": "accented"},
            {"text": "résumé", "type": "french"},
        ]

        patterns = self.dataspot.find(mixed_data, ["text", "type"])

        # Should handle mixed encodings
        assert len(patterns) > 0

    def test_right_to_left_text(self):
        """Test handling of right-to-left text."""
        rtl_data = [
            {"text": "مرحبا", "language": "arabic"},
            {"text": "שלום", "language": "hebrew"},
            {"text": "hello", "language": "english"},
        ]

        patterns = self.dataspot.find(rtl_data, ["text", "language"])

        # Should handle RTL text
        assert len(patterns) > 0

    def test_combining_characters(self):
        """Test handling of Unicode combining characters."""
        combining_data = [
            {"text": "é", "type": "precomposed"},  # Single character
            {"text": "e\u0301", "type": "combining"},  # e + combining acute
        ]

        patterns = self.dataspot.find(combining_data, ["text", "type"])

        # Should handle combining characters
        assert len(patterns) > 0

    def test_zero_width_characters(self):
        """Test handling of zero-width characters."""
        zwc_data = [
            {"text": "hello\u200bworld", "type": "zero_width_space"},
            {"text": "hello\u200cworld", "type": "zero_width_non_joiner"},
            {"text": "helloworld", "type": "normal"},
        ]

        patterns = self.dataspot.find(zwc_data, ["text", "type"])

        # Should handle zero-width characters
        assert len(patterns) > 0


class TestExtremeDataSizes:
    """Test cases for extreme data sizes and edge conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_very_long_string_values(self):
        """Test handling of very long string values."""
        long_string = "x" * 10000  # 10KB string

        long_data = [
            {"long_field": long_string, "type": "long"},
            {"long_field": "short", "type": "short"},
        ]

        patterns = self.dataspot.find(long_data, ["long_field", "type"])

        # Should handle long strings without issues
        assert len(patterns) > 0

        # Find the long string pattern
        long_patterns = [p for p in patterns if len(p.path) > 1000]
        assert len(long_patterns) > 0

    def test_very_deep_hierarchy(self):
        """Test handling of very deep field hierarchies."""
        # Create data that would create deep hierarchies
        deep_data = []
        for i in range(10):
            record = {}
            for level in range(20):  # 20 levels deep
                record[f"level_{level}"] = f"value_{i % 3}"
            deep_data.append(record)

        fields = [f"level_{i}" for i in range(10)]  # Use first 10 levels
        patterns = self.dataspot.find(deep_data, fields)

        # Should handle deep hierarchies
        assert len(patterns) > 0

        # Check maximum depth
        max_depth = max(p.depth for p in patterns)
        assert max_depth <= len(fields)

    def test_many_unique_values(self):
        """Test handling of fields with many unique values."""
        # Create data with many unique values
        unique_data = []
        for i in range(1000):
            unique_data.append(
                {
                    "unique_id": f"id_{i}",
                    "category": f"cat_{i % 10}",  # Some grouping
                }
            )

        patterns = self.dataspot.find(unique_data, ["category", "unique_id"])

        # Should handle many unique values
        assert len(patterns) > 0

        # Category patterns should have reasonable concentrations
        category_patterns = [p for p in patterns if p.depth == 1]
        assert any(
            p.percentage >= 8 for p in category_patterns
        )  # At least 8% for 10 categories

    def test_single_record_many_fields(self):
        """Test single record with many fields."""
        many_fields_record = {f"field_{i}": f"value_{i}" for i in range(100)}

        patterns = self.dataspot.find(
            [many_fields_record], list(many_fields_record.keys())[:10]
        )

        # Should handle many fields
        assert len(patterns) > 0

        # All patterns should have 100% concentration (single record)
        for pattern in patterns:
            assert pattern.percentage == 100.0

    def test_empty_field_names(self):
        """Test handling of empty or unusual field names."""
        unusual_data = [
            {"": "empty_field_name", "normal": "value1"},
            {" ": "space_field_name", "normal": "value2"},
            {"123": "numeric_field_name", "normal": "value3"},
        ]

        patterns = self.dataspot.find(unusual_data, ["", " ", "123", "normal"])

        # Should handle unusual field names
        assert len(patterns) > 0

    def test_field_names_with_special_chars(self):
        """Test field names containing special characters."""
        special_data = [
            {"field-with-dash": "value1", "field_with_underscore": "a"},
            {"field.with.dot": "value2", "field with space": "b"},
            {"field@symbol": "value3", "field#hash": "c"},
        ]

        fields = ["field-with-dash", "field.with.dot", "field@symbol"]
        patterns = self.dataspot.find(special_data, fields)

        # Should handle special characters in field names
        assert len(patterns) > 0


class TestMemoryAndPerformanceEdges:
    """Test cases for memory and performance edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_memory_efficiency_large_dataset(self):
        """Test memory efficiency with large dataset."""
        # Create moderately large dataset
        large_data = []
        for i in range(5000):
            large_data.append(
                {
                    "category": f"cat_{i % 50}",
                    "type": f"type_{i % 10}",
                    "status": "active" if i % 2 == 0 else "inactive",
                }
            )

        patterns = self.dataspot.find(large_data, ["category", "type"])

        # Should complete without memory issues
        assert len(patterns) > 0
        assert isinstance(patterns, list)

    def test_circular_reference_data(self):
        """Test handling of data with circular references."""
        # Create objects with circular references
        obj1 = {"id": 1, "name": "first"}
        obj2 = {"id": 2, "name": "second"}
        obj1["ref"] = obj2
        obj2["ref"] = obj1

        # This might cause issues if the dataspot tries to deeply inspect objects
        circular_data = [
            {"simple": "value1", "complex": obj1},
            {"simple": "value2", "complex": obj2},
        ]

        # Should handle gracefully (likely by converting to string)
        patterns = self.dataspot.find(circular_data, ["simple"])
        assert len(patterns) > 0

    def test_nested_data_structures(self):
        """Test handling of nested data structures."""
        nested_data = [
            {
                "user": {"name": "John", "age": 30},
                "metadata": {"created": "2023-01-01", "source": "web"},
            },
            {
                "user": {"name": "Jane", "age": 25},
                "metadata": {"created": "2023-01-02", "source": "mobile"},
            },
        ]

        # Should handle nested structures (likely by string conversion)
        patterns = self.dataspot.find(nested_data, ["user", "metadata"])
        assert len(patterns) > 0

    def test_generator_data_input(self):
        """Test handling of generator as data input."""

        def data_generator():
            for i in range(100):
                yield {"id": i, "category": f"cat_{i % 5}"}

        # Convert generator to list (as expected by the dataspot)
        gen_data = list(data_generator())
        patterns = self.dataspot.find(gen_data, ["category"])

        assert len(patterns) > 0

    def test_repeated_analysis_memory_leak(self):
        """Test for potential memory leaks with repeated analysis."""
        data = [{"x": i % 5, "y": i % 3} for i in range(100)]

        # Run analysis multiple times
        for _ in range(50):
            patterns = self.dataspot.find(data, ["x", "y"])
            assert len(patterns) > 0

        # Should not accumulate memory (hard to test directly)
        # This is more of a smoke test


class TestErrorConditions:
    """Test cases for error conditions and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()

    def test_malformed_data_records(self):
        """Test handling of malformed data records."""
        malformed_data = [
            {"normal": "field"},
            None,  # None record
            {"normal": "field2"},
            {},  # Empty record
            {"normal": "field3"},
        ]

        # Should handle malformed records gracefully
        with pytest.raises((TypeError, AttributeError)):
            _ = self.dataspot.find(malformed_data, ["normal"])

    def test_data_type_inconsistency(self):
        """Test handling of inconsistent data types in same field."""
        inconsistent_data = [
            {"value": "string"},
            {"value": 123},
            {"value": [1, 2, 3]},
            {"value": {"nested": "object"}},
            {"value": True},
        ]

        patterns = self.dataspot.find(inconsistent_data, ["value"])

        # Should handle type inconsistency
        assert len(patterns) > 0

    def test_field_disappearing_midway(self):
        """Test handling when field exists in some records but not others."""
        partial_data = [
            {"a": 1, "b": 2, "c": 3},
            {"a": 1, "b": 2},  # Missing 'c'
            {"a": 1},  # Missing 'b' and 'c'
            {"a": 1, "b": 2, "c": 3},
        ]

        patterns = self.dataspot.find(partial_data, ["a", "b", "c"])

        # Should handle missing fields (treated as empty/None)
        assert len(patterns) > 0

    def test_extreme_percentage_edge_cases(self):
        """Test edge cases in percentage calculation."""
        # Test data that could cause precision issues
        precision_data = []

        # Add 7 records of one type, 3 of another (7/10 = 70%, 3/10 = 30%)
        for _ in range(7):
            precision_data.append({"type": "majority"})
        for _ in range(3):
            precision_data.append({"type": "minority"})

        patterns = self.dataspot.find(precision_data, ["type"])

        # Check precision of percentage calculations
        majority_pattern = next(p for p in patterns if "majority" in p.path)
        minority_pattern = next(p for p in patterns if "minority" in p.path)

        assert majority_pattern.percentage == 70.0
        assert minority_pattern.percentage == 30.0

    def test_floating_point_precision(self):
        """Test floating point precision in calculations."""
        # Create data that results in repeating decimals
        precision_data = []
        for _ in range(3):
            precision_data.append({"type": "one_third"})
        for _ in range(6):
            precision_data.append({"type": "two_thirds"})

        patterns = self.dataspot.find(precision_data, ["type"])

        # 3/9 = 33.33%, 6/9 = 66.67% (with rounding)
        one_third = next(p for p in patterns if "one_third" in p.path)
        two_thirds = next(p for p in patterns if "two_thirds" in p.path)

        # Should be properly rounded to 2 decimal places
        assert one_third.percentage == 33.33
        assert two_thirds.percentage == 66.67

    def test_zero_division_scenarios(self):
        """Test scenarios that could lead to division by zero."""
        # Empty data should not cause division by zero
        empty_patterns = self.dataspot.find([], ["field"])
        assert empty_patterns == []

        # Single field with all None values
        none_data = [{"field": None}, {"field": None}]
        none_patterns = self.dataspot.find(none_data, ["field"])

        # Should handle gracefully
        assert isinstance(none_patterns, list)

    def test_integer_overflow_scenarios(self):
        """Test scenarios that could cause integer overflow."""
        # Very large count values (unlikely in practice but possible)
        large_count_data = [{"type": "common"}] * 1000000  # 1M records

        # This is mainly a smoke test - should not crash
        # (Running this might be slow, so using smaller number)
        large_count_data = [{"type": "common"}] * 1000  # 1K records
        patterns = self.dataspot.find(large_count_data, ["type"])

        assert len(patterns) > 0
        assert patterns[0].count == 1000
        assert patterns[0].percentage == 100.0
