"""Text Pattern Filtering Examples.

Shows how to filter patterns based on text content using contains, exclude, and regex filters.
"""

from dataspot import Dataspot
from dataspot.models.finder import FindInput, FindOptions

# Simple web analytics data
data = [
    {"browser": "chrome", "os": "windows", "device": "desktop"},
    {"browser": "chrome", "os": "android", "device": "mobile"},
    {"browser": "safari", "os": "ios", "device": "mobile"},
    {"browser": "safari", "os": "macos", "device": "desktop"},
    {"browser": "firefox", "os": "linux", "device": "desktop"},
    {"browser": "edge", "os": "windows", "device": "desktop"},
] * 3  # 18 records total


def main():
    """Text pattern filtering examples."""
    dataspot = Dataspot()

    print("=== 1. Contains Filter ===")

    # All patterns
    result_all = dataspot.find(
        FindInput(data=data, fields=["browser", "device"]), FindOptions()
    )
    print(f"All patterns: {len(result_all.patterns)}")

    # Patterns containing "mobile"
    result_mobile = dataspot.find(
        FindInput(data=data, fields=["browser", "device"]),
        FindOptions(contains="mobile"),
    )
    print(f"Contains 'mobile': {len(result_mobile.patterns)}")

    print("\n=== 2. Exclude Filter ===")

    # Exclude mobile patterns
    result_no_mobile = dataspot.find(
        FindInput(data=data, fields=["browser", "device"]),
        FindOptions(exclude=["mobile"]),
    )
    print(f"Exclude 'mobile': {len(result_no_mobile.patterns)}")

    # Exclude multiple terms
    result_desktop_only = dataspot.find(
        FindInput(data=data, fields=["browser", "os"]),
        FindOptions(exclude=["android", "ios"]),
    )
    print(f"Desktop OS only: {len(result_desktop_only.patterns)}")

    print("\n=== 3. Regex Filter ===")

    # Chrome or Safari browsers
    result_regex = dataspot.find(
        FindInput(data=data, fields=["browser", "device"]),
        FindOptions(regex=r"(chrome|safari)"),
    )
    print(f"Chrome or Safari: {len(result_regex.patterns)}")

    print("\n=== 4. Combined Text Filters ===")

    # Contains + exclude + percentage threshold
    result_combined = dataspot.find(
        FindInput(data=data, fields=["browser", "os", "device"]),
        FindOptions(contains="windows", exclude=["edge"], min_percentage=10.0),
    )
    print(f"Combined filters: {len(result_combined.patterns)}")

    # Show results
    for i, pattern in enumerate(result_combined.patterns, 1):
        print(
            f"  {i}. {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)"
        )


if __name__ == "__main__":
    main()
