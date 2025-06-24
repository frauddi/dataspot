#!/usr/bin/env python3
"""Test script to verify that samples functionality works correctly."""

from dataspot import Dataspot

# Sample data for testing
test_data = [
    {"country": "US", "device": "mobile", "user": "john@example.com", "amount": 100},
    {"country": "US", "device": "mobile", "user": "jane@example.com", "amount": 150},
    {"country": "US", "device": "desktop", "user": "bob@example.com", "amount": 200},
    {"country": "EU", "device": "mobile", "user": "alice@example.com", "amount": 120},
    {"country": "EU", "device": "tablet", "user": "charlie@example.com", "amount": 180},
]


def test_samples_functionality():
    """Test that samples are correctly captured."""
    print("🧪 Testing samples functionality...")

    dataspot = Dataspot()
    patterns = dataspot.find(test_data, ["country", "device"])

    for pattern in patterns:
        print(f"\n📊 Pattern: {pattern.path}")
        print(f"   Count: {pattern.count}, Percentage: {pattern.percentage}%")
        print(f"   Samples: {len(pattern.samples)} records")

        for i, sample in enumerate(pattern.samples):
            print(f"     Sample {i+1}: {sample}")

    # Verify that samples are not empty for main patterns
    main_patterns = [p for p in patterns if p.depth == 1]
    for pattern in main_patterns:
        if pattern.count > 0:
            assert (
                len(pattern.samples) > 0
            ), f"Pattern {pattern.path} should have samples"
            assert (
                len(pattern.samples) <= 3
            ), f"Pattern {pattern.path} should have max 3 samples"

            # Verify samples are actual records
            for sample in pattern.samples:
                assert isinstance(sample, dict), "Sample should be a dictionary"
                assert "country" in sample, "Sample should contain original fields"

    print("\n✅ All tests passed! Samples functionality is working correctly.")


if __name__ == "__main__":
    test_samples_functionality()
