"""Temporal Comparison Examples.

Shows how to compare patterns between time periods to detect changes and anomalies.
"""

from dataspot import Dataspot
from dataspot.models.compare import CompareInput, CompareOptions


def main():
    """Temporal comparison examples."""
    dataspot = Dataspot()

    print("=== 1. Basic Change Detection ===")

    # Last month's data (baseline)
    baseline_data = [
        {"country": "US", "payment": "card", "amount": "medium"},
        {"country": "US", "payment": "paypal", "amount": "low"},
        {"country": "EU", "payment": "card", "amount": "medium"},
        {"country": "EU", "payment": "bank", "amount": "low"},
        {"country": "CA", "payment": "card", "amount": "high"},
    ] * 4  # 20 records

    # This month's data (current)
    current_data = [
        {"country": "US", "payment": "card", "amount": "medium"},
        {"country": "US", "payment": "crypto", "amount": "high"},  # New pattern
        {"country": "US", "payment": "crypto", "amount": "high"},
        {"country": "EU", "payment": "card", "amount": "medium"},
        {"country": "CA", "payment": "card", "amount": "high"},
        {"country": "RU", "payment": "crypto", "amount": "high"},  # New country
    ] * 3  # 18 records

    # Detect changes between periods
    comparison_result = dataspot.compare(
        CompareInput(
            current_data=current_data,
            baseline_data=baseline_data,
            fields=["country", "payment"],
        ),
        CompareOptions(change_threshold=0.20),
    )

    print(f"📊 Changes detected: {len(comparison_result.changes)}")
    print(f"📈 New patterns: {len(comparison_result.new_patterns)}")
    print(f"📉 Disappeared patterns: {len(comparison_result.disappeared_patterns)}")

    print("\n🆕 New patterns this month:")
    for pattern in comparison_result.new_patterns[:3]:
        print(f"  {pattern.path} - {pattern.current_count} occurrences")

    print("\n📈 Significant changes:")
    for change in comparison_result.changes[:3]:
        if change.is_significant:
            direction = "+" if change.percentage_change > 0 else ""
            print(f"  {change.path} - {direction}{change.percentage_change:.1f}%")

    print("\n=== 2. Fraud Detection Monitoring ===")

    # Fraud monitoring between months
    fraud_baseline = [
        {"country": "US", "method": "card", "risk": "low"},
        {"country": "US", "method": "paypal", "risk": "low"},
        {"country": "EU", "method": "card", "risk": "low"},
        {"country": "EU", "method": "bank", "risk": "medium"},
    ] * 3  # 12 records

    fraud_current = [
        {"country": "US", "method": "card", "risk": "low"},
        {"country": "RU", "method": "crypto", "risk": "high"},  # Suspicious
        {"country": "RU", "method": "crypto", "risk": "high"},
        {"country": "RU", "method": "crypto", "risk": "high"},
        {"country": "EU", "method": "bank", "risk": "medium"},
    ] * 2  # 10 records

    fraud_comparison = dataspot.compare(
        CompareInput(
            current_data=fraud_current,
            baseline_data=fraud_baseline,
            fields=["country", "method", "risk"],
        ),
        CompareOptions(change_threshold=0.10),
    )

    print(f"🚨 Fraud changes: {len(fraud_comparison.changes)}")

    # Look for high-risk new patterns
    high_risk_new = [p for p in fraud_comparison.new_patterns if "high" in p.path]
    print(f"⚠️  High-risk new patterns: {len(high_risk_new)}")
    for pattern in high_risk_new:
        print(f"  🔴 {pattern.path} - {pattern.current_count} cases")

    print("\n=== 3. A/B Testing Analysis ===")

    # A/B test baseline (balanced)
    ab_baseline = [
        {"variant": "A", "conversion": "yes"},
        {"variant": "A", "conversion": "no"},
        {"variant": "A", "conversion": "no"},
        {"variant": "B", "conversion": "yes"},
        {"variant": "B", "conversion": "no"},
        {"variant": "B", "conversion": "no"},
    ] * 2  # 12 records

    # A/B test current (B improved)
    ab_current = [
        {"variant": "A", "conversion": "yes"},
        {"variant": "A", "conversion": "no"},
        {"variant": "A", "conversion": "no"},
        {"variant": "B", "conversion": "yes"},
        {"variant": "B", "conversion": "yes"},  # B performing better
        {"variant": "B", "conversion": "yes"},
    ] * 2  # 12 records

    ab_comparison = dataspot.compare(
        CompareInput(
            current_data=ab_current,
            baseline_data=ab_baseline,
            fields=["variant", "conversion"],
        ),
        CompareOptions(statistical_significance=True),
    )

    print("🧪 A/B Test Results:")

    # Look for conversion changes
    conversion_changes = [
        c for c in ab_comparison.changes if "conversion=yes" in c.path
    ]
    for change in conversion_changes:
        if "variant=A" in change.path:
            variant = "A"
        elif "variant=B" in change.path:
            variant = "B"
        else:
            continue

        print(f"  Variant {variant} conversions: {change.percentage_change:+.1f}%")

        # Check if statistically significant
        if (
            hasattr(change, "statistical_significance")
            and change.statistical_significance
        ):
            stats = change.statistical_significance
            if "p_value" in stats:
                p_value = stats["p_value"]
                significant = (
                    "✅ Significant" if p_value < 0.05 else "❌ Not significant"
                )
                print(f"    P-value: {p_value:.3f} ({significant})")

    print("\n=== 4. Business Performance Summary ===")

    print(
        f"📊 Total comparisons analyzed: {len(comparison_result.changes) + len(fraud_comparison.changes) + len(ab_comparison.changes)}"
    )
    print(
        f"📈 Overall new patterns: {len(comparison_result.new_patterns) + len(fraud_comparison.new_patterns) + len(ab_comparison.new_patterns)}"
    )
    print(
        f"🔍 Significant changes found: {len([c for c in comparison_result.changes if c.is_significant])}"
    )


if __name__ == "__main__":
    main()
