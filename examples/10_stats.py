"""Statistical Analysis Examples.

Shows how to use statistical methods for data analysis and business decisions.
"""

from dataspot import Dataspot
from dataspot.models.compare import CompareInput, CompareOptions


def main():
    """Statistical analysis examples."""
    dataspot = Dataspot()

    print("=== 1. Basic Statistical Comparison ===")

    # A/B test data
    baseline_data = [
        {"variant": "A", "conversion": "yes"},
        {"variant": "A", "conversion": "no"},
        {"variant": "A", "conversion": "no"},
        {"variant": "A", "conversion": "no"},
    ] * 25  # 100 records, 25% conversion

    current_data = [
        {"variant": "B", "conversion": "yes"},
        {"variant": "B", "conversion": "yes"},
        {"variant": "B", "conversion": "no"},
        {"variant": "B", "conversion": "no"},
    ] * 25  # 100 records, 50% conversion

    # Statistical comparison
    comparison = dataspot.compare(
        CompareInput(
            current_data=current_data,
            baseline_data=baseline_data,
            fields=["variant", "conversion"],
        ),
        CompareOptions(statistical_significance=True),
    )

    print(f"📊 Patterns compared: {len(comparison.changes)}")
    print(
        f"📈 Significant changes: {len([c for c in comparison.changes if c.is_significant])}"
    )

    # Find conversion changes
    conversion_changes = [c for c in comparison.changes if "conversion=yes" in c.path]
    for change in conversion_changes:
        print("\n🧪 Conversion Analysis:")
        print(f"  Baseline: {change.baseline_count} conversions")
        print(f"  Current: {change.current_count} conversions")
        print(f"  Change: {change.percentage_change:+.1f}%")

        # Statistical significance
        if (
            hasattr(change, "statistical_significance")
            and change.statistical_significance
        ):
            stats = change.statistical_significance
            if "p_value" in stats:
                p_value = stats["p_value"]
                confidence = (1 - p_value) * 100
                print(f"  P-value: {p_value:.4f}")
                print(f"  Confidence: {confidence:.1f}%")

                if p_value < 0.05:
                    print("  ✅ Statistically significant!")
                else:
                    print("  ❌ Not statistically significant")

    print("\n=== 2. Fraud Detection Statistics ===")

    # Fraud detection with statistical analysis
    normal_period = [
        {"country": "US", "risk": "low"},
        {"country": "US", "risk": "medium"},
        {"country": "EU", "risk": "low"},
        {"country": "EU", "risk": "medium"},
    ] * 20  # 80 records

    suspicious_period = [
        {"country": "US", "risk": "low"},
        {"country": "RU", "risk": "high"},
        {"country": "RU", "risk": "high"},
        {"country": "RU", "risk": "high"},
        {"country": "XX", "risk": "high"},
    ] * 15  # 75 records

    fraud_comparison = dataspot.compare(
        CompareInput(
            current_data=suspicious_period,
            baseline_data=normal_period,
            fields=["country", "risk"],
        ),
        CompareOptions(statistical_significance=True, change_threshold=0.10),
    )

    print(f"🚨 Fraud patterns detected: {len(fraud_comparison.new_patterns)}")

    # High-risk patterns
    high_risk_patterns = [p for p in fraud_comparison.new_patterns if "high" in p.path]
    print(f"⚠️  High-risk new patterns: {len(high_risk_patterns)}")

    for pattern in high_risk_patterns:
        # Calculate risk score based on frequency
        risk_score = (pattern.current_count / 75) * 100  # Percentage of total
        if risk_score > 10:
            alert_level = "🔴 CRITICAL"
        elif risk_score > 5:
            alert_level = "🟡 HIGH"
        else:
            alert_level = "🟢 MEDIUM"

        print(
            f"  {alert_level} {pattern.path}: {pattern.current_count} cases ({risk_score:.1f}%)"
        )

    print("\n=== 3. Business Performance Statistics ===")

    # Performance comparison with confidence intervals
    last_quarter = [
        {"region": "north", "performance": "good"},
        {"region": "north", "performance": "poor"},
        {"region": "south", "performance": "good"},
        {"region": "south", "performance": "excellent"},
    ] * 30  # 120 records

    this_quarter = [
        {"region": "north", "performance": "excellent"},
        {"region": "north", "performance": "excellent"},
        {"region": "north", "performance": "good"},
        {"region": "south", "performance": "excellent"},
        {"region": "south", "performance": "excellent"},
    ] * 25  # 125 records

    performance_comparison = dataspot.compare(
        CompareInput(
            current_data=this_quarter,
            baseline_data=last_quarter,
            fields=["region", "performance"],
        ),
        CompareOptions(statistical_significance=True),
    )

    print("📊 Performance Analysis:")

    # Look for excellent performance changes
    excellent_changes = [
        c for c in performance_comparison.changes if "excellent" in c.path
    ]
    for change in excellent_changes:
        improvement = change.current_count - change.baseline_count
        print(f"  📈 {change.path}: +{improvement} excellent ratings")
        print(f"     Change: {change.percentage_change:+.1f}%")

        if change.is_significant:
            print("     ✅ Statistically significant improvement")
        else:
            print("     ❓ Improvement not statistically significant")

    print("\n=== 4. Statistical Summary ===")

    # Overall statistics
    total_comparisons = (
        len(comparison.changes)
        + len(fraud_comparison.changes)
        + len(performance_comparison.changes)
    )
    total_significant = sum(
        [
            len([c for c in comparison.changes if c.is_significant]),
            len([c for c in fraud_comparison.changes if c.is_significant]),
            len([c for c in performance_comparison.changes if c.is_significant]),
        ]
    )

    print(f"📊 Total patterns analyzed: {total_comparisons}")
    print(f"📈 Statistically significant: {total_significant}")
    print(f"🎯 Significance rate: {(total_significant / total_comparisons) * 100:.1f}%")

    print("\n📚 Statistical Concepts Used:")
    print("  • P-values: Probability that results are due to chance")
    print("  • Confidence intervals: Range where true value likely lies")
    print("  • Statistical significance: Results unlikely due to chance")
    print("  • Effect size: Practical magnitude of differences")

    print("\n💡 Business Applications:")
    print("  • A/B testing validation")
    print("  • Fraud detection confidence")
    print("  • Performance monitoring")
    print("  • Risk assessment")


if __name__ == "__main__":
    main()
