"""Text-Based Pattern Filtering Examples.

This module demonstrates how to filter patterns based on text content
using contains, exclude, and regex filters. These are useful for finding
specific pattern types or excluding unwanted patterns.
from dataspot import Dataspot
"""

# Sample web analytics data
from dataspot import Dataspot

web_analytics = []
browsers = ["chrome", "firefox", "safari", "edge", "opera"]
os_systems = ["windows", "macos", "linux", "ios", "android"]
referrers = ["google", "facebook", "twitter", "direct", "email", "ads"]
pages = ["home", "product", "cart", "checkout", "profile", "help"]

# Generate realistic web analytics data
for i in range(200):
    web_analytics.append(
        {
            "browser": browsers[i % 5],
            "os": os_systems[i % 5],
            "referrer": referrers[i % 6],
            "page": pages[i % 6],
            "mobile": "yes" if i % 3 == 0 else "no",  # 33% mobile
            "conversion": "yes" if i % 8 == 0 else "no",  # 12.5% conversion
        }
    )


def example_contains_filter():
    """Find patterns containing specific text."""
    print("=== Contains Filter Example ===")
    print("Finding all patterns related to mobile...")

    dataspot = Dataspot()

    # Find patterns containing "mobile"
    mobile_patterns = dataspot.find(
        web_analytics, ["browser", "os", "mobile"], contains="mobile"
    )

    print(f"Patterns containing 'mobile': {len(mobile_patterns)}")
    for pattern in mobile_patterns:
        print(
            f"  {pattern.path} - {pattern.count} sessions ({pattern.percentage:.1f}%)"
        )

    print("\nFinding patterns related to Apple ecosystem...")
    apple_patterns = dataspot.find(web_analytics, ["browser", "os"], contains="safari")

    print(f"Patterns containing 'safari': {len(apple_patterns)}")
    for pattern in apple_patterns:
        print(
            f"  {pattern.path} - {pattern.count} sessions ({pattern.percentage:.1f}%)"
        )
    print()


def example_exclude_filter_single():
    """Exclude patterns with unwanted text."""
    print("=== Single Exclude Filter Example ===")
    print("Analyzing patterns but excluding direct traffic...")

    dataspot = Dataspot()

    # Get all patterns first
    all_patterns = dataspot.find(web_analytics, ["referrer", "page"])
    print(f"All patterns: {len(all_patterns)}")

    # Exclude direct traffic patterns
    no_direct = dataspot.find(web_analytics, ["referrer", "page"], exclude="direct")
    print(f"Patterns excluding 'direct': {len(no_direct)}")

    print("Top patterns (no direct traffic):")
    for pattern in no_direct[:5]:
        print(
            f"  {pattern.path} - {pattern.count} sessions ({pattern.percentage:.1f}%)"
        )
    print()


def example_exclude_filter_multiple():
    """Exclude multiple unwanted terms."""
    print("=== Multiple Exclude Filter Example ===")
    print("Analyzing browser patterns, excluding mobile browsers...")

    dataspot = Dataspot()

    # Exclude multiple mobile-related terms
    desktop_patterns = dataspot.find(
        web_analytics, ["browser", "os"], exclude=["mobile", "ios", "android"]
    )

    print(f"Desktop-only patterns: {len(desktop_patterns)}")
    for pattern in desktop_patterns:
        print(
            f"  {pattern.path} - {pattern.count} sessions ({pattern.percentage:.1f}%)"
        )
    print()


def example_regex_filter():
    """Use regex for complex pattern matching."""
    print("=== Regex Filter Example ===")
    print("Finding patterns with browsers ending in 'e' or 'x'...")

    dataspot = Dataspot()

    # Find browsers ending with 'e' (chrome, edge) or 'x' (firefox)
    regex_patterns = dataspot.find(
        web_analytics, ["browser", "referrer"], regex=r"browser=(chrome|edge|firefox)"
    )

    print(f"Patterns matching regex: {len(regex_patterns)}")
    for pattern in regex_patterns:
        print(
            f"  {pattern.path} - {pattern.count} sessions ({pattern.percentage:.1f}%)"
        )

    print("\nFinding conversion patterns with regex...")
    # Find patterns that contain conversion=yes
    conversion_patterns = dataspot.find(
        web_analytics, ["referrer", "page", "conversion"], regex=r"conversion=yes"
    )

    print(f"Conversion patterns: {len(conversion_patterns)}")
    for pattern in conversion_patterns[:5]:
        print(
            f"  {pattern.path} - {pattern.count} sessions ({pattern.percentage:.1f}%)"
        )
    print()


def example_complex_text_filtering():
    """Combine text filters with other criteria."""
    print("=== Complex Text Filtering Example ===")
    print("Finding significant mobile patterns (high percentage, excluding iOS)...")

    dataspot = Dataspot()

    # Complex filtering: mobile-related, but not iOS, with good representation
    complex_patterns = dataspot.find(
        web_analytics,
        ["browser", "os", "mobile", "referrer"],
        contains="mobile",
        exclude="ios",
        min_percentage=5,
        limit=10,
    )

    print(f"Complex filtered patterns: {len(complex_patterns)}")
    for pattern in complex_patterns:
        print(f"  {pattern.path}")
        print(f"    Count: {pattern.count}, Percentage: {pattern.percentage:.1f}%")
    print()


def example_case_sensitivity():
    """Text filtering behavior with different cases."""
    print("=== Case Sensitivity Example ===")

    # Add some data with mixed cases
    mixed_case_data = web_analytics + [
        {"browser": "Chrome", "os": "Windows", "referrer": "Google"},
        {"browser": "FIREFOX", "os": "LINUX", "referrer": "FACEBOOK"},
    ]

    dataspot = Dataspot()

    # Text filters are typically case-insensitive in pattern paths
    chrome_patterns = dataspot.find(
        mixed_case_data, ["browser", "os"], contains="chrome"
    )

    print(f"Patterns containing 'chrome': {len(chrome_patterns)}")
    for pattern in chrome_patterns:
        print(f"  {pattern.path} - {pattern.count} sessions")
    print()


def example_filter_validation():
    """Demonstrate filter validation and edge cases."""
    print("=== Filter Validation Example ===")

    dataspot = Dataspot()

    # Empty contains filter - should return all patterns
    empty_contains = dataspot.find(web_analytics, ["browser"], contains="")
    all_browser = dataspot.find(web_analytics, ["browser"])
    print(f"Empty contains filter: {len(empty_contains)} patterns")
    print(f"No filter: {len(all_browser)} patterns")
    print(f"Same result: {len(empty_contains) == len(all_browser)}")

    # Non-existent pattern
    nonexistent = dataspot.find(web_analytics, ["browser"], contains="nonexistent")
    print(f"Non-existent pattern: {len(nonexistent)} patterns")

    # Exclude everything
    exclude_all = dataspot.find(
        web_analytics,
        ["browser"],
        exclude=["chrome", "firefox", "safari", "edge", "opera"],
    )
    print(f"Exclude all browsers: {len(exclude_all)} patterns")
    print()


if __name__ == "__main__":
    example_contains_filter()
    example_exclude_filter_single()
    example_exclude_filter_multiple()
    example_regex_filter()
    example_complex_text_filtering()
    example_case_sensitivity()
    example_filter_validation()
