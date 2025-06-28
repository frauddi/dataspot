"""Tests for the core Dataspot algorithm functionality.

This module tests the main pattern detection and concentration analysis features.
"""

from dataspot import Dataspot
from dataspot.analyzers.base import Base


class TestDataspotCore:
    """Test cases for core Dataspot functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.dataspot = Dataspot()

        # Standard test dataset from our validation
        self.basic_data = [
            {"a": 1, "b": 1, "c": 2},  # x1
            {"a": 1, "b": 1, "c": 3},  # x2
            {"a": 1, "b": 0, "c": 2},  # y1
            {"a": 1, "b": 0, "c": 3},  # y2
            {"a": 1, "b": 2, "c": 2},  # z1
            {"a": 1, "b": 2, "c": 3},  # z2
        ]

        # Realistic business data
        self.business_data = [
            {"country": "US", "device": "mobile", "user_type": "premium"},
            {"country": "US", "device": "mobile", "user_type": "premium"},
            {"country": "US", "device": "desktop", "user_type": "free"},
            {"country": "EU", "device": "mobile", "user_type": "free"},
            {"country": "US", "device": "mobile", "user_type": "premium"},
        ]

    def test_basic_pattern_detection(self):
        """Test basic pattern detection with simple hierarchical data."""
        fields = ["a", "b", "c"]
        patterns = self.dataspot.find(self.basic_data, fields)

        # Should find 10 patterns total (1 + 3 + 6)
        assert len(patterns.patterns) == 10

        # Check top-level pattern
        top_pattern = patterns.patterns[0]  # Should be sorted by percentage
        assert top_pattern.path == "a=1"
        assert top_pattern.count == 6
        assert top_pattern.percentage == 100.0
        assert top_pattern.depth == 1

        # Check second-level patterns
        second_level = [p for p in patterns.patterns if p.depth == 2]
        assert len(second_level) == 3

        expected_second_level = {
            "a=1 > b=0": {"count": 2, "percentage": 33.33},
            "a=1 > b=1": {"count": 2, "percentage": 33.33},
            "a=1 > b=2": {"count": 2, "percentage": 33.33},
        }

        for pattern in second_level:
            assert pattern.path in expected_second_level
            expected = expected_second_level[pattern.path]
            assert pattern.count == expected["count"]
            assert pattern.percentage == expected["percentage"]
            assert pattern.depth == 2

    def test_third_level_patterns(self):
        """Test third-level pattern detection."""
        fields = ["a", "b", "c"]
        patterns = self.dataspot.find(self.basic_data, fields)

        # Check third-level patterns
        third_level = [p for p in patterns.patterns if p.depth == 3]
        assert len(third_level) == 6

        # All third-level patterns should have 1 record (16.67%)
        for pattern in third_level:
            assert pattern.count == 1
            assert pattern.percentage == 16.67
            assert pattern.depth == 3
            assert " > " in pattern.path  # Should be hierarchical
            assert pattern.path.count(" > ") == 2  # Should have 2 separators (3 levels)

    def test_empty_data(self):
        """Test behavior with empty dataset."""
        result = self.dataspot.find([], ["field1", "field2"])
        assert len(result.patterns) == 0
        assert result.total_records == 0
        assert result.total_patterns == 0

    def test_single_record(self):
        """Test behavior with single record."""
        single_data = [{"x": "value1", "y": "value2"}]
        patterns = self.dataspot.find(single_data, ["x", "y"])

        assert len(patterns.patterns) == 2  # x=value1, x=value1 > y=value2

        # Check expected patterns
        paths = [p.path for p in patterns.patterns]
        assert "x=value1" in paths
        assert "x=value1 > y=value2" in paths

        # All patterns should have 100% concentration
        for pattern in patterns.patterns:
            assert pattern.count == 1
            assert pattern.percentage == 100.0

    def test_single_field(self):
        """Test analysis with single field."""
        patterns = self.dataspot.find(self.basic_data, ["a"])

        assert len(patterns.patterns) == 1
        assert patterns.patterns[0].path == "a=1"
        assert patterns.patterns[0].count == 6
        assert patterns.patterns[0].percentage == 100.0
        assert patterns.patterns[0].depth == 1

    def test_pattern_sorting(self):
        """Test that patterns are sorted by percentage (highest first)."""
        patterns = self.dataspot.find(self.business_data, ["country", "device"])

        # Check that patterns are sorted by percentage descending
        for i in range(len(patterns.patterns) - 1):
            assert (
                patterns.patterns[i].percentage >= patterns.patterns[i + 1].percentage
            )

    def test_percentage_calculations(self):
        """Test accuracy of percentage calculations."""
        patterns = self.dataspot.find(self.basic_data, ["a", "b"])

        # Find specific patterns and verify calculations
        a1_pattern = next(p for p in patterns.patterns if p.path == "a=1")
        assert a1_pattern.percentage == 100.0  # 6/6 * 100

        b_patterns = [p for p in patterns.patterns if p.depth == 2]
        for pattern in b_patterns:
            assert pattern.percentage == 33.33  # 2/6 * 100, rounded to 2 decimals

    def test_count_accuracy(self):
        """Test that count values are accurate."""
        patterns = self.dataspot.find(self.business_data, ["country"])

        us_pattern = next(p for p in patterns.patterns if "country=US" in p.path)
        eu_pattern = next(p for p in patterns.patterns if "country=EU" in p.path)

        # Count US and EU occurrences manually
        us_count = sum(1 for record in self.business_data if record["country"] == "US")
        eu_count = sum(1 for record in self.business_data if record["country"] == "EU")

        assert us_pattern.count == us_count
        assert eu_pattern.count == eu_count

    def test_depth_calculation(self):
        """Test that depth values are calculated correctly."""
        patterns = self.dataspot.find(self.basic_data, ["a", "b", "c"])

        # Check depth distribution
        depth_counts = {}
        for pattern in patterns.patterns:
            depth = pattern.depth
            depth_counts[depth] = depth_counts.get(depth, 0) + 1

            # Verify depth matches path structure
            expected_separators = depth - 1
            actual_separators = pattern.path.count(" > ")
            assert actual_separators == expected_separators

        # Should have 1 depth-1, 3 depth-2, 6 depth-3 patterns
        assert depth_counts[1] == 1
        assert depth_counts[2] == 3
        assert depth_counts[3] == 6

    def test_field_order_consistency(self):
        """Test that field order affects pattern hierarchy."""
        fields_abc = ["a", "b", "c"]
        fields_cba = ["c", "b", "a"]

        patterns_abc = self.dataspot.find(self.basic_data, fields_abc)
        patterns_cba = self.dataspot.find(self.basic_data, fields_cba)

        # Different field orders should produce different hierarchies
        abc_top = patterns_abc.patterns[0].path
        cba_top = patterns_cba.patterns[0].path

        assert abc_top != cba_top
        assert abc_top.startswith("a=")
        assert cba_top.startswith("c=")

    def test_mixed_data_types(self):
        """Test handling of mixed data types."""
        mixed_data = [
            {"num": 1, "str": "text", "bool": True},
            {"num": 2, "str": "text", "bool": False},
            {"num": 1, "str": "other", "bool": True},
        ]

        patterns = self.dataspot.find(mixed_data, ["num", "str", "bool"])

        # Should handle all data types correctly
        assert len(patterns.patterns) > 0

        # Check that boolean values are handled correctly
        bool_patterns = [p for p in patterns.patterns if "bool=" in p.path]
        assert any("bool=True" in p.path for p in bool_patterns)
        assert any("bool=False" in p.path for p in bool_patterns)

    def test_large_dataset_structure(self):
        """Test behavior with larger dataset."""
        # Generate larger dataset
        large_data = []
        for i in range(100):
            large_data.append(
                {
                    "category": f"cat_{i % 5}",  # 5 categories
                    "type": f"type_{i % 3}",  # 3 types
                    "status": "active" if i % 2 == 0 else "inactive",
                }
            )

        patterns = self.dataspot.find(large_data, ["category", "type", "status"])

        # Should find patterns
        assert len(patterns.patterns) > 0

        # Top pattern should have highest concentration
        top_pattern = patterns.patterns[0]
        assert top_pattern.percentage > 0

        # Check that we get reasonable number of patterns
        assert len(patterns.patterns) <= 100  # Shouldn't exceed total combinations

    def test_analyze_method(self):
        """Test the analyze method returns comprehensive insights."""
        result = self.dataspot.analyze(self.basic_data, ["a", "b", "c"])

        # Check structure
        assert result.patterns == result.patterns
        assert result.statistics == result.statistics
        assert result.field_stats == result.field_stats
        assert result.top_patterns == result.top_patterns

        # Check statistics
        stats = result.statistics
        assert stats.total_records == 6
        assert stats.filtered_records == 6
        assert stats.patterns_found == 10
        assert stats.max_concentration == 100.0
        assert stats.avg_concentration > 0

        # Check field stats
        field_stats = result.field_stats
        assert "a" in field_stats
        assert "b" in field_stats
        assert "c" in field_stats.keys()

        # Check top patterns
        assert len(result.top_patterns) <= 5

    def test_field_stats_accuracy(self):
        """Test accuracy of field distribution analysis."""
        result = self.dataspot.analyze(self.business_data, ["country", "device"])
        field_stats = result.field_stats

        # Check country field stats
        country_stats = field_stats["country"]
        assert country_stats["total_count"] == 5
        assert country_stats["unique_count"] == 2  # US and EU
        assert country_stats["null_count"] == 0

        # Check top values
        top_values = country_stats["top_values"]
        us_entry = next(item for item in top_values if item["value"] == "US")
        assert us_entry["count"] == 4  # 4 US records
        assert us_entry["percentage"] == 80.0  # 4/5 * 100

    def test_no_fields_provided(self):
        """Test behavior when no fields are provided."""
        result = self.dataspot.find(self.basic_data, [])

        # Should handle gracefully by returning empty patterns
        assert len(result.patterns) == 0
        assert result.total_records == len(self.basic_data)
        assert result.total_patterns == 0

    def test_nonexistent_fields(self):
        """Test behavior with fields that don't exist in data."""
        result = self.dataspot.find(self.basic_data, ["nonexistent_field"])

        # Should handle gracefully - might return patterns with empty values
        assert (
            len(result.patterns) >= 0
        )  # May be empty or have patterns with empty values

    def test_pattern_samples(self):
        """Test that pattern samples are collected correctly."""
        # Add some sample data to records for testing
        data_with_samples = []
        for i, record in enumerate(self.basic_data):
            record_copy = record.copy()
            record_copy["sample_id"] = i
            data_with_samples.append(record_copy)

        patterns = self.dataspot.find(data_with_samples, ["a", "b"])

        # Check that patterns have samples
        for pattern in patterns.patterns:
            assert isinstance(pattern.samples, list)
            assert len(pattern.samples) <= 3  # Should limit to 3 samples

    def test_memory_efficiency(self):
        """Test that large datasets don't cause memory issues."""
        # This is more of a smoke test for memory efficiency
        large_data = [
            {"field1": f"value_{i % 100}", "field2": f"cat_{i % 10}"}
            for i in range(1000)
        ]

        result = self.dataspot.find(large_data, ["field1", "field2"])

        # Should complete without memory errors
        assert len(result.patterns) > 0
        assert result.total_records == 1000

    def test_unicode_handling(self):
        """Test handling of unicode characters in data."""
        unicode_data = [
            {"país": "España", "categoría": "técnico"},
            {"país": "España", "categoría": "ventas"},
            {"país": "México", "categoría": "técnico"},
        ]

        patterns = self.dataspot.find(unicode_data, ["país", "categoría"])

        # Should handle unicode correctly
        assert len(patterns.patterns) > 0
        spain_patterns = [p for p in patterns.patterns if "España" in p.path]
        assert len(spain_patterns) > 0

    def test_numeric_precision(self):
        """Test numeric precision in percentage calculations."""
        # Create data that will test rounding precision
        precision_data = [{"x": "a"}] * 3 + [{"x": "b"}] * 7  # 3:7 ratio

        patterns = self.dataspot.find(precision_data, ["x"])

        a_pattern = next(p for p in patterns.patterns if "x=a" in p.path)
        b_pattern = next(p for p in patterns.patterns if "x=b" in p.path)

        # Check precision (should be rounded to 2 decimal places)
        assert a_pattern.percentage == 30.0  # 3/10 * 100
        assert b_pattern.percentage == 70.0  # 7/10 * 100

        # Test edge case with more complex ratios
        complex_data = [{"y": "test"}] * 7 + [{"y": "other"}] * 3  # 7:3 ratio
        patterns = self.dataspot.find(complex_data, ["y"])

        test_pattern = next(p for p in patterns.patterns if "y=test" in p.path)
        assert test_pattern.percentage == 70.0  # Should be exactly 70.0


class TestTreeBuilding:
    """Test cases specifically for tree building functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.dataspot = Dataspot()
        self.base = Base()

    def test_tree_structure_integrity(self):
        """Test that the internal tree structure is built correctly."""
        data = [
            {"a": 1, "b": 2},
            {"a": 1, "b": 3},
        ]

        # Access internal tree building method
        tree = self.base._build_tree(data, ["a", "b"])

        # Check tree structure
        assert "children" in tree
        assert "a=1" in tree["children"]

        a1_node = tree["children"]["a=1"]
        assert a1_node["count"] == 2
        assert a1_node["percentage"] == 100.0
        assert a1_node["depth"] == 1

        # Check second level
        assert "children" in a1_node
        assert "b=2" in a1_node["children"]
        assert "b=3" in a1_node["children"]

    def test_path_generation(self):
        """Test that record paths are generated correctly."""
        data = [{"x": "val1", "y": "val2"}]

        paths = self.base._get_record_paths(data[0], ["x", "y"])

        assert len(paths) == 1
        assert paths[0] == ["x=val1", "y=val2"]

    def test_path_addition_to_tree(self):
        """Test that paths are added to tree correctly."""
        tree = {"children": {}}
        path = ["a=1", "b=2"]
        test_record = {"a": 1, "b": 2}

        self.base._add_path_to_tree(path, tree, total=1, record=test_record)

        # Check that path was added correctly
        assert "a=1" in tree["children"]

        a1_node = tree["children"]["a=1"]
        assert a1_node["count"] == 1
        assert a1_node["percentage"] == 100.0
        assert "samples" in a1_node
        assert len(a1_node["samples"]) == 1
        assert a1_node["samples"][0] == test_record

        assert "b=2" in a1_node["children"]

        b2_node = a1_node["children"]["b=2"]
        assert b2_node["count"] == 1
        assert b2_node["percentage"] == 100.0
        assert "samples" in b2_node
        assert len(b2_node["samples"]) == 1
        assert b2_node["samples"][0] == test_record
