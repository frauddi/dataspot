"""Advanced Temporal Comparison Example.

This example demonstrates the powerful compare() method for detecting
changes and anomalies between time periods or data segments.

Key Features:
📊 Statistical significance testing
🔍 Pattern change detection
📈 Categorized pattern analysis
⚡ Simplified, focused API
"""

import dataspot

# Sample transaction data - this month
this_month_transactions = [
    {"country": "US", "payment": "credit", "amount": 100, "user_type": "premium"},
    {"country": "US", "payment": "credit", "amount": 150, "user_type": "basic"},
    {"country": "US", "payment": "crypto", "amount": 500, "user_type": "premium"},
    {"country": "US", "payment": "crypto", "amount": 300, "user_type": "premium"},
    {"country": "US", "payment": "crypto", "amount": 250, "user_type": "basic"},
    {"country": "EU", "payment": "credit", "amount": 80, "user_type": "premium"},
    {"country": "EU", "payment": "paypal", "amount": 90, "user_type": "basic"},
    {"country": "CA", "payment": "credit", "amount": 120, "user_type": "premium"},
    {"country": "CA", "payment": "crypto", "amount": 400, "user_type": "premium"},
] * 50  # Simulate more data

# Sample transaction data - last month (baseline)
last_month_transactions = [
    {"country": "US", "payment": "credit", "amount": 100, "user_type": "premium"},
    {"country": "US", "payment": "credit", "amount": 150, "user_type": "basic"},
    {"country": "US", "payment": "paypal", "amount": 75, "user_type": "basic"},
    {"country": "EU", "payment": "credit", "amount": 80, "user_type": "premium"},
    {"country": "EU", "payment": "credit", "amount": 85, "user_type": "basic"},
    {"country": "EU", "payment": "paypal", "amount": 90, "user_type": "basic"},
    {"country": "CA", "payment": "credit", "amount": 120, "user_type": "premium"},
    {"country": "CA", "payment": "paypal", "amount": 95, "user_type": "basic"},
] * 50  # Simulate more data

# Initialize dataspot
ds = dataspot.Dataspot()

print("🚀 DATASPOT TEMPORAL COMPARISON EXAMPLES")
print("=" * 60)

# Example 1: Basic Comparison
print("\n1️⃣ BASIC COMPARISON")
print("-" * 30)

basic_comparison = ds.compare(
    current_data=this_month_transactions,
    baseline_data=last_month_transactions,
    fields=["country", "payment"],
    change_threshold=0.20,  # 20% threshold
)

print(f"📊 Total Changes: {len(basic_comparison['changes'])}")
print(f"📈 Total Patterns Analyzed: {len(basic_comparison['changes'])}")
print(
    f"🔍 Statistical Significance Enabled: {basic_comparison['statistical_significance']}"
)

# Show pattern categories
categories = [
    "new_patterns",
    "disappeared_patterns",
    "increased_patterns",
    "decreased_patterns",
    "stable_patterns",
]
print("\n📋 PATTERN CATEGORIES:")
for category in categories:
    count = len(basic_comparison[category])
    if count > 0:
        category_name = category.replace("_", " ").title()
        print(f"   • {category_name}: {count}")

if basic_comparison["new_patterns"]:
    print("\n🔥 NEW PATTERNS DETECTED:")
    for pattern in basic_comparison["new_patterns"][:3]:
        print(f"   • {pattern['path']}: {pattern['current_count']} occurrences")

# Example 2: Enhanced Analysis with Statistical Significance
print("\n\n2️⃣ STATISTICAL SIGNIFICANCE ANALYSIS")
print("-" * 45)

enhanced_analysis = ds.compare(
    current_data=this_month_transactions,
    baseline_data=last_month_transactions,
    fields=["country", "payment", "user_type"],
    statistical_significance=True,
    change_threshold=0.15,  # 15% threshold
)

print("🔬 STATISTICAL ANALYSIS RESULTS:")
print(
    f"   📊 Patterns with Stats: {sum(1 for c in enhanced_analysis['changes'] if c.get('statistical_significance'))}"
)

significant_changes = [c for c in enhanced_analysis["changes"] if c["is_significant"]]
print(f"   ⚡ Significant Changes: {len(significant_changes)}")

if significant_changes:
    print("\n📈 TOP SIGNIFICANT CHANGES:")
    for change in significant_changes[:5]:
        direction = "📈" if change["count_change"] > 0 else "📉"
        print(
            f"   {direction} {change['path']}: {change['count_change_percentage']:.1f}%"
        )
        print(f"      Status: {change['status']}")

        # Show statistical significance if available
        if change.get("statistical_significance"):
            stats = change["statistical_significance"]
            if stats:
                print(f"      P-value: {stats.get('p_value', 'N/A'):.4f}")
                print(f"      Significant: {stats.get('is_significant', 'N/A')}")
        print()

# Example 3: Focused Payment Method Analysis
print("\n3️⃣ PAYMENT METHOD TREND ANALYSIS")
print("-" * 40)

payment_analysis = ds.compare(
    current_data=this_month_transactions,
    baseline_data=last_month_transactions,
    fields=["payment"],
    statistical_significance=True,
)

print("💳 PAYMENT METHOD CHANGES:")
for change in payment_analysis["changes"]:
    if "payment=" in change["path"] and change["is_significant"]:
        payment_method = change["path"].split("=")[1]
        direction = "📈 Increased" if change["count_change"] > 0 else "📉 Decreased"
        print(
            f"   • {payment_method.title()}: {direction} by {abs(change['count_change_percentage']):.1f}%"
        )
        print(
            f"     {change['baseline_count']} → {change['current_count']} transactions"
        )

# Example 4: A/B Testing Comparison
print("\n\n4️⃣ A/B TESTING COMPARISON")
print("-" * 35)

# Simulate A/B test data with clear differences
ab_current = [
    {"variant": "A", "conversion": "yes"},
    {"variant": "A", "conversion": "no"},
    {"variant": "B", "conversion": "yes"},
    {"variant": "B", "conversion": "yes"},
    {"variant": "B", "conversion": "yes"},
] * 30  # Variant B performing better

ab_baseline = [
    {"variant": "A", "conversion": "yes"},
    {"variant": "A", "conversion": "no"},
    {"variant": "A", "conversion": "no"},
    {"variant": "B", "conversion": "yes"},
    {"variant": "B", "conversion": "no"},
] * 30  # More balanced performance

ab_results = ds.compare(
    current_data=ab_current,
    baseline_data=ab_baseline,
    fields=["variant", "conversion"],
    statistical_significance=True,
    change_threshold=0.10,
)

print("🧪 A/B TEST RESULTS:")
conversion_changes = [c for c in ab_results["changes"] if "conversion=yes" in c["path"]]

for change in conversion_changes:
    variant = "A" if "variant=A" in change["path"] else "B"
    print(f"   📊 Variant {variant} Conversions:")
    print(f"      Change: {change['count_change_percentage']:.1f}%")
    print(f"      Count: {change['baseline_count']} → {change['current_count']}")
    print(f"      Status: {change['status']}")

    if change.get("statistical_significance"):
        stats = change["statistical_significance"]
        if stats:
            print(f"      P-value: {stats.get('p_value', 'N/A'):.4f}")
            print(f"      Significant: {stats.get('is_significant', 'N/A')}")
            if "confidence_interval" in stats:
                ci = stats["confidence_interval"]
                print(f"      95% CI: [{ci['lower']:.1f}, {ci['upper']:.1f}]")
    print()

# Example 5: Geographic Analysis
print("\n5️⃣ GEOGRAPHIC TREND ANALYSIS")
print("-" * 35)

geo_analysis = ds.compare(
    current_data=this_month_transactions,
    baseline_data=last_month_transactions,
    fields=["country"],
    change_threshold=0.10,
)

print("🌍 GEOGRAPHIC CHANGES:")
country_changes = [c for c in geo_analysis["changes"] if "country=" in c["path"]]

for change in sorted(
    country_changes, key=lambda x: abs(x["count_change_percentage"]), reverse=True
):
    country = change["path"].split("=")[1]
    if change["count_change_percentage"] != float(
        "inf"
    ):  # Skip new/disappeared patterns
        direction = "📈" if change["count_change"] > 0 else "📉"
        print(f"   {direction} {country}: {change['count_change_percentage']:+.1f}%")
        print(f"      Volume: {change['baseline_count']} → {change['current_count']}")
        print(f"      Status: {change['status']}")

# Example 6: Data Quality Check
print("\n\n6️⃣ DATA QUALITY MONITORING")
print("-" * 35)

# Add some data quality issues to current data
quality_current = (
    this_month_transactions
    + [
        {"country": None, "payment": "credit", "amount": 100, "user_type": "premium"},
        {"country": "UNKNOWN", "payment": None, "amount": 0, "user_type": None},
    ]
    * 5
)

quality_analysis = ds.compare(
    current_data=quality_current,
    baseline_data=last_month_transactions,
    fields=["country", "payment", "user_type"],
    change_threshold=0.05,  # Very sensitive for data quality
)

print("🔍 DATA QUALITY ANALYSIS:")
quality_issues = [
    c
    for c in quality_analysis["new_patterns"]
    if "None" in c["path"] or "UNKNOWN" in c["path"] or "null" in c["path"]
]

if quality_issues:
    print("   ⚠️  DATA QUALITY ISSUES DETECTED:")
    for issue in quality_issues:
        print(f"      • {issue['path']}: {issue['current_count']} occurrences")
else:
    print("   ✅ No data quality issues detected")

print("\n📊 SUMMARY:")
print(f"   • Total patterns analyzed: {len(quality_analysis['changes'])}")
print(f"   • New patterns: {len(quality_analysis['new_patterns'])}")
print(f"   • Disappeared patterns: {len(quality_analysis['disappeared_patterns'])}")
print(
    f"   • Significant changes: {len([c for c in quality_analysis['changes'] if c['is_significant']])}"
)

print("\n✨ DATASPOT COMPARISON COMPLETE!")
print(
    "🎯 Use these insights to understand your data trends and make informed decisions."
)
