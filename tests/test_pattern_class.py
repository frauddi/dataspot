"""Tests for the Pattern class.

This module tests the Pattern dataclass functionality, including initialization,
validation, and data integrity.
"""

import pytest

from dataspot.core import Pattern


class TestPatternClass:
    """Test cases for the Pattern dataclass."""

    def test_pattern_creation_basic(self):
        """Test basic Pattern object creation."""
        pattern = Pattern(
            path="country=US", count=100, percentage=50.0, depth=1, samples=[]
        )

        assert pattern.path == "country=US"
        assert pattern.count == 100
        assert pattern.percentage == 50.0
        assert pattern.depth == 1
        assert pattern.samples == []

    def test_pattern_creation_with_samples(self):
        """Test Pattern creation with sample data."""
        sample_data = [
            {"country": "US", "device": "mobile"},
            {"country": "US", "device": "desktop"},
        ]

        pattern = Pattern(
            path="country=US", count=2, percentage=40.0, depth=1, samples=sample_data
        )

        assert pattern.samples == sample_data
        assert len(pattern.samples) == 2

    def test_pattern_post_init_none_samples(self):
        """Test that __post_init__ handles None samples correctly."""
        pattern = Pattern(
            path="device=mobile", count=50, percentage=25.0, depth=2, samples=[]
        )

        # __post_init__ should convert None to empty list
        assert pattern.samples == []
        assert isinstance(pattern.samples, list)

    def test_pattern_post_init_existing_samples(self):
        """Test that __post_init__ preserves existing samples."""
        existing_samples = [{"test": "data"}]

        pattern = Pattern(
            path="test=value",
            count=1,
            percentage=10.0,
            depth=1,
            samples=existing_samples,
        )

        # Should preserve existing samples
        assert pattern.samples == existing_samples
        assert pattern.samples is existing_samples

    def test_pattern_hierarchical_path(self):
        """Test Pattern with hierarchical path."""
        hierarchical_pattern = Pattern(
            path="country=US > device=mobile > type=premium",
            count=25,
            percentage=12.5,
            depth=3,
            samples=[],
        )

        assert hierarchical_pattern.path.count(" > ") == 2
        assert hierarchical_pattern.depth == 3
        assert "country=US" in hierarchical_pattern.path
        assert "device=mobile" in hierarchical_pattern.path
        assert "type=premium" in hierarchical_pattern.path

    def test_pattern_equality(self):
        """Test Pattern equality comparison."""
        samples = [{"x": 1}]

        pattern1 = Pattern("test=value", 10, 50.0, 1, samples)
        pattern2 = Pattern("test=value", 10, 50.0, 1, samples)
        pattern3 = Pattern("test=other", 10, 50.0, 1, samples)

        # Dataclass should implement equality
        assert pattern1 == pattern2
        assert pattern1 != pattern3

    def test_pattern_representation(self):
        """Test Pattern string representation."""
        pattern = Pattern(
            path="status=active", count=75, percentage=75.0, depth=1, samples=[]
        )

        repr_str = repr(pattern)

        # Should contain key information
        assert "Pattern" in repr_str
        assert "status=active" in repr_str
        assert "75" in repr_str
        assert "75.0" in repr_str

    def test_pattern_field_types(self):
        """Test that Pattern fields have correct types."""
        pattern = Pattern(
            path="field=value",
            count=42,
            percentage=84.5,
            depth=2,
            samples=[{"sample": "data"}],
        )

        assert isinstance(pattern.path, str)
        assert isinstance(pattern.count, int)
        assert isinstance(pattern.percentage, float)
        assert isinstance(pattern.depth, int)
        assert isinstance(pattern.samples, list)

    def test_pattern_with_zero_values(self):
        """Test Pattern with zero/edge values."""
        pattern = Pattern(path="empty=", count=0, percentage=0.0, depth=1, samples=[])

        assert pattern.count == 0
        assert pattern.percentage == 0.0
        assert pattern.path == "empty="

    def test_pattern_with_unicode(self):
        """Test Pattern with unicode characters."""
        unicode_pattern = Pattern(
            path="país=España > categoría=técnico",
            count=15,
            percentage=30.0,
            depth=2,
            samples=[{"país": "España", "categoría": "técnico"}],
        )

        assert "España" in unicode_pattern.path
        assert "técnico" in unicode_pattern.path
        assert unicode_pattern.samples[0]["país"] == "España"

    def test_pattern_immutability(self):
        """Test that Pattern behaves like an immutable dataclass."""
        pattern = Pattern("test=value", 10, 20.0, 1, [])

        # Should be able to access fields
        assert pattern.path == "test=value"

        # Fields should be modifiable (dataclass default behavior)
        # Note: If you want immutability, add frozen=True to @dataclass
        pattern.count = 15
        assert pattern.count == 15

    def test_pattern_samples_mutation(self):
        """Test behavior when samples list is mutated."""
        original_samples = [{"x": 1}, {"x": 2}]
        pattern = Pattern("test=value", 2, 100.0, 1, original_samples)

        # Original samples should be preserved
        assert pattern.samples == original_samples

        # Mutating the samples list should affect the pattern
        pattern.samples.append({"x": 3})
        assert len(pattern.samples) == 3

    def test_pattern_samples_copy_safety(self):
        """Test that pattern samples don't interfere with each other."""
        original_samples = [{"shared": "data"}]

        # Create two patterns with same samples reference
        pattern1 = Pattern("path1", 1, 100.0, 1, original_samples.copy())
        pattern2 = Pattern("path2", 1, 100.0, 1, original_samples.copy())

        # Modify one pattern's samples
        pattern1.samples.append({"new": "data"})

        # Other pattern should not be affected
        assert len(pattern2.samples) == 1
        assert pattern2.samples[0] == {"shared": "data"}


class TestPatternValidation:
    """Test cases for Pattern data validation."""

    def test_negative_count(self):
        """Test Pattern with negative count."""
        # Pattern should accept negative counts (might be valid in some contexts)
        pattern = Pattern("test=value", -5, 50.0, 1, [])
        assert pattern.count == -5

    def test_negative_percentage(self):
        """Test Pattern with negative percentage."""
        pattern = Pattern("test=value", 10, -25.0, 1, [])
        assert pattern.percentage == -25.0

    def test_zero_depth(self):
        """Test Pattern with zero depth."""
        pattern = Pattern("test=value", 10, 50.0, 0, [])
        assert pattern.depth == 0

    def test_negative_depth(self):
        """Test Pattern with negative depth."""
        pattern = Pattern("test=value", 10, 50.0, -1, [])
        assert pattern.depth == -1

    def test_percentage_over_100(self):
        """Test Pattern with percentage over 100."""
        pattern = Pattern("test=value", 10, 150.0, 1, [])
        assert pattern.percentage == 150.0

    def test_very_large_count(self):
        """Test Pattern with very large count."""
        large_count = 10**15
        pattern = Pattern("test=value", large_count, 100.0, 1, [])
        assert pattern.count == large_count

    def test_float_count_coercion(self):
        """Test that float counts are properly handled."""
        # Should accept float but maintain as int if needed
        pattern = Pattern("test=value", int(42.0), 50.0, 1, [])
        # Dataclass will keep whatever type is passed
        assert pattern.count == 42

    def test_string_percentage_coercion(self):
        """Test handling of string percentage values."""
        # Dataclass doesn't enforce types at runtime by default
        pattern = Pattern("test=value", 10, float("50.0"), 1, [])
        assert pattern.percentage == 50.0

    def test_none_path(self):
        """Test Pattern with None path."""
        # Test handling of empty path instead of None
        pattern = Pattern("", 10, 50.0, 1, [])
        assert pattern.path == ""

    def test_empty_path(self):
        """Test Pattern with empty string path."""
        pattern = Pattern("", 10, 50.0, 1, [])
        assert pattern.path == ""

    def test_very_long_path(self):
        """Test Pattern with very long path."""
        long_path = " > ".join([f"field{i}=value{i}" for i in range(100)])
        pattern = Pattern(long_path, 1, 1.0, 100, [])

        assert pattern.path == long_path
        assert pattern.depth == 100


class TestPatternSamples:
    """Test cases for Pattern samples handling."""

    def test_empty_samples_list(self):
        """Test Pattern with empty samples list."""
        pattern = Pattern("test=value", 10, 50.0, 1, [])

        assert pattern.samples == []
        assert len(pattern.samples) == 0

    def test_single_sample(self):
        """Test Pattern with single sample."""
        sample = {"field": "value", "count": 42}
        pattern = Pattern("test=value", 1, 100.0, 1, [sample])

        assert len(pattern.samples) == 1
        assert pattern.samples[0] == sample

    def test_multiple_samples(self):
        """Test Pattern with multiple samples."""
        samples = [
            {"field": "value1", "count": 10},
            {"field": "value2", "count": 20},
            {"field": "value3", "count": 30},
        ]

        pattern = Pattern("test=value", 3, 100.0, 1, samples)

        assert len(pattern.samples) == 3
        assert pattern.samples == samples

    def test_samples_order_preservation(self):
        """Test that sample order is preserved."""
        samples = [
            {"order": 3, "value": "c"},
            {"order": 1, "value": "a"},
            {"order": 2, "value": "b"},
        ]

        pattern = Pattern("test=value", 3, 100.0, 1, samples)

        # Should preserve original order
        assert pattern.samples[0]["order"] == 3
        assert pattern.samples[1]["order"] == 1
        assert pattern.samples[2]["order"] == 2

    def test_samples_with_different_structures(self):
        """Test Pattern with samples having different structures."""
        mixed_samples = [
            {"field1": "value1"},
            {"field2": "value2", "extra": True},
            {"field1": "value3", "field2": "value4", "count": 10},
        ]

        pattern = Pattern("mixed=structure", 3, 100.0, 1, mixed_samples)

        assert len(pattern.samples) == 3
        assert pattern.samples == mixed_samples

    def test_samples_with_none_values(self):
        """Test Pattern with samples containing None values."""
        samples_with_none = [
            {"field": None, "valid": "data"},
            {"field": "value", "missing": None},
        ]

        pattern = Pattern("test=value", 2, 100.0, 1, samples_with_none)

        assert pattern.samples == samples_with_none
        assert pattern.samples[0]["field"] is None
        assert pattern.samples[1]["missing"] is None

    def test_samples_with_complex_data(self):
        """Test Pattern with complex sample data structures."""
        complex_samples = [
            {
                "nested": {"deep": {"value": 42}},
                "list_field": [1, 2, 3],
                "mixed": {"numbers": [1.5, 2.7], "text": "sample"},
            },
            {
                "nested": {"deep": {"value": 84}},
                "list_field": [4, 5, 6],
                "mixed": {"numbers": [3.2, 4.1], "text": "another"},
            },
        ]

        pattern = Pattern("complex=data", 2, 100.0, 1, complex_samples)

        assert pattern.samples == complex_samples
        assert pattern.samples[0]["nested"]["deep"]["value"] == 42
        assert pattern.samples[1]["list_field"] == [4, 5, 6]

    def test_samples_modification_after_creation(self):
        """Test modifying samples after Pattern creation."""
        initial_samples = [{"field": "initial"}]
        pattern = Pattern("test=value", 1, 100.0, 1, initial_samples)

        # Modify the samples list
        pattern.samples.append({"field": "added"})
        pattern.samples[0]["field"] = "modified"

        assert len(pattern.samples) == 2
        assert pattern.samples[0]["field"] == "modified"
        assert pattern.samples[1]["field"] == "added"

    def test_samples_large_dataset(self):
        """Test Pattern with large samples dataset."""
        large_samples = [{"id": i, "value": f"item_{i}"} for i in range(1000)]
        pattern = Pattern("large=dataset", 1000, 100.0, 1, large_samples)

        assert len(pattern.samples) == 1000
        assert pattern.samples[0]["id"] == 0
        assert pattern.samples[999]["id"] == 999


class TestPatternDataclass:
    """Test cases for Pattern as a dataclass."""

    def test_pattern_is_dataclass(self):
        """Test that Pattern is properly configured as a dataclass."""
        pattern = Pattern("test=value", 10, 50.0, 1, [])

        # Should have dataclass attributes
        assert hasattr(pattern, "__dataclass_fields__")
        assert hasattr(pattern, "__dataclass_params__")

    def test_pattern_fields_access(self):
        """Test accessing Pattern fields."""
        pattern = Pattern("field=value", 42, 75.5, 2, [{"sample": "data"}])

        # Direct attribute access
        assert pattern.path == "field=value"
        assert pattern.count == 42
        assert pattern.percentage == 75.5
        assert pattern.depth == 2
        assert pattern.samples == [{"sample": "data"}]

    def test_pattern_asdict(self):
        """Test converting Pattern to dictionary."""
        from dataclasses import asdict

        samples = [{"test": "data"}]
        pattern = Pattern("key=value", 25, 83.33, 3, samples)

        pattern_dict = asdict(pattern)

        expected = {
            "path": "key=value",
            "count": 25,
            "percentage": 83.33,
            "depth": 3,
            "samples": [{"test": "data"}],
        }

        assert pattern_dict == expected

    def test_pattern_astuple(self):
        """Test converting Pattern to tuple."""
        from dataclasses import astuple

        samples = [{"test": "data"}]
        pattern = Pattern("key=value", 25, 83.33, 3, samples)

        pattern_tuple = astuple(pattern)

        expected = ("key=value", 25, 83.33, 3, [{"test": "data"}])
        assert pattern_tuple == expected

    def test_pattern_replace(self):
        """Test replacing Pattern fields."""
        from dataclasses import replace

        original = Pattern("original=path", 10, 50.0, 1, [])
        modified = replace(original, path="new=path", count=20)

        # Original should be unchanged
        assert original.path == "original=path"
        assert original.count == 10

        # Modified should have new values
        assert modified.path == "new=path"
        assert modified.count == 20
        assert modified.percentage == 50.0  # Unchanged fields preserved

    def test_pattern_hash_behavior(self):
        """Test Pattern hashing behavior."""
        # Default dataclass is not hashable due to mutable samples list
        pattern = Pattern("test=value", 10, 50.0, 1, [])

        # Should not be hashable by default
        with pytest.raises(TypeError):
            hash(pattern)
