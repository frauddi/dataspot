"""Statistical Methods Demonstration.

This script demonstrates how to use the well-documented statistical methods
for data comparison analysis. Each method is explained with practical examples
and business interpretations.

🎯 Purpose: Show how statistical methods work in practice
📊 Coverage: Chi-square, p-values, confidence intervals, effect sizes
🔬 Context: Business intelligence and data monitoring
"""

from dataspot.analyzers.stats import Stats


def demonstrate_chi_square_calculation():
    """Demonstrate chi-square statistic calculation with business examples."""
    print("📊 CHI-SQUARE STATISTIC CALCULATION")
    print("=" * 50)
    print("Theory: Measures how much observed values deviate from expected values")
    print("Formula: χ² = (Observed - Expected)² / Expected")
    print()

    stats = Stats()

    # Example 1: A/B Testing
    print("🧪 Example 1: A/B Testing Conversion Rates")
    print("-" * 45)
    current_conversions = 60  # Variant B
    baseline_conversions = 40  # Variant A
    expected = (current_conversions + baseline_conversions) / 2  # 50

    chi_square = stats.calculate_chi_square_statistic(current_conversions, expected)

    print(f"Observed (Variant B): {current_conversions} conversions")
    print(f"Expected (null hypothesis): {expected} conversions")
    print(f"Chi-square statistic: {chi_square:.2f}")
    print()

    if chi_square > 3.84:
        print("✅ Chi-square > 3.84: Likely significant difference")
    else:
        print("❌ Chi-square < 3.84: Likely not significant")

    # Example 2: Fraud Detection
    print("\n🚨 Example 2: Fraud Detection - Suspicious Transactions")
    print("-" * 55)
    current_suspicious = 150  # This month
    baseline_suspicious = 50  # Last month
    expected_fraud = (current_suspicious + baseline_suspicious) / 2  # 100

    chi_square_fraud = stats.calculate_chi_square_statistic(
        current_suspicious, expected_fraud
    )

    print(f"Observed (this month): {current_suspicious} suspicious transactions")
    print(f"Expected (historical): {expected_fraud} transactions")
    print(f"Chi-square statistic: {chi_square_fraud:.2f}")
    print()

    if chi_square_fraud > 10:
        print("🚨 CRITICAL: Chi-square very high - investigate immediately!")
    elif chi_square_fraud > 3.84:
        print("⚠️  WARNING: Chi-square elevated - monitor closely")
    else:
        print("✅ Normal: Chi-square within expected range")


def demonstrate_p_value_calculation():
    """Demonstrate p-value calculation and interpretation."""
    print("\n\n🎯 P-VALUE CALCULATION")
    print("=" * 40)
    print("Theory: Probability that observed result is due to random chance")
    print("Formula: p ≈ e^(-χ²/2) for 1 degree of freedom")
    print()

    stats = Stats()

    test_cases = [
        (1.0, "Small effect"),
        (4.0, "Medium effect"),
        (10.0, "Large effect"),
        (25.0, "Extreme effect"),
    ]

    print("Chi-square → P-value → Interpretation")
    print("-" * 40)

    for chi_sq, _ in test_cases:
        p_value = stats.calculate_p_value_from_chi_square(chi_sq)

        if p_value < 0.001:
            significance = "EXTREMELY SIGNIFICANT ⭐⭐⭐"
        elif p_value < 0.01:
            significance = "VERY SIGNIFICANT ⭐⭐"
        elif p_value < 0.05:
            significance = "SIGNIFICANT ⭐"
        else:
            significance = "NOT SIGNIFICANT ❌"

        print(f"χ²={chi_sq:4.1f} → p={p_value:.4f} → {significance}")

    print("\n📋 Business Decision Rules:")
    print("• p < 0.05: Act on this finding (95% confident)")
    print("• p < 0.01: Strong evidence (99% confident)")
    print("• p < 0.001: Extremely strong evidence (99.9% confident)")
    print("• p ≥ 0.05: Insufficient evidence to act")


def demonstrate_confidence_intervals():
    """Demonstrate confidence interval calculation and interpretation."""
    print("\n\n📏 CONFIDENCE INTERVALS")
    print("=" * 40)
    print("Theory: Range where the true difference likely exists")
    print("Formula: difference ± (1.96 × standard_error) for 95% CI")
    print()

    stats = Stats()

    # Business scenarios
    scenarios = [
        (120, 100, "Website conversions (this month vs last month)"),
        (75, 25, "Customer complaints (current vs baseline)"),
        (200, 180, "Daily active users (campaign vs control)"),
    ]

    for current, baseline, context in scenarios:
        ci = stats.calculate_confidence_interval(current, baseline)

        print(f"📊 {context}")
        print(f"   Current: {current}, Baseline: {baseline}")
        print(f"   Difference: {ci['difference']:.0f}")
        print(f"   95% CI: [{ci['lower']:.1f}, {ci['upper']:.1f}]")
        print(f"   Margin of error: ±{ci['margin_of_error']:.1f}")

        # Interpretation
        if ci["lower"] > 0:
            print("   ✅ Confident increase (lower bound > 0)")
        elif ci["upper"] < 0:
            print("   ❌ Confident decrease (upper bound < 0)")
        else:
            print("   ❓ Uncertain direction (CI includes 0)")
        print()


def demonstrate_effect_sizes():
    """Demonstrate effect size calculation and practical significance."""
    print("\n📈 EFFECT SIZES & PRACTICAL SIGNIFICANCE")
    print("=" * 50)
    print("Theory: Quantifies the practical magnitude of a difference")
    print("Purpose: Distinguish meaningful changes from trivial ones")
    print()

    stats = Stats()

    # Different effect sizes
    examples = [
        (102, 100, "Website bounce rate (tiny change)"),
        (120, 100, "Email open rate (small change)"),
        (150, 100, "Ad click-through rate (medium change)"),
        (200, 100, "Sales conversion rate (large change)"),
        (500, 100, "Security alerts (extreme change)"),
    ]

    print("Scenario → Effect Size → Business Impact")
    print("-" * 50)

    for current, baseline, context in examples:
        effect = stats.calculate_effect_size(current, baseline)

        # Business impact interpretation
        impact_map = {
            "NEGLIGIBLE": "Monitor only 👀",
            "SMALL": "Worth investigating 🔍",
            "MEDIUM": "Take action 🎯",
            "LARGE": "Immediate attention 🚨",
            "VERY_LARGE": "Critical priority ⚠️",
            "EXTREME": "Emergency response 🔥",
        }

        effect_magnitude = str(effect["effect_magnitude"])
        impact = impact_map.get(effect_magnitude, "Unknown")

        print(f"{context}")
        print(f"   {baseline} → {current} ({effect['percentage_change']:+.0f}%)")
        print(f"   Effect: {effect['effect_magnitude']} → {impact}")
        print()


def demonstrate_significance_determination():
    """Demonstrate statistical significance determination process."""
    print("\n✅ STATISTICAL SIGNIFICANCE DETERMINATION")
    print("=" * 50)
    print("Theory: Decide if results are trustworthy for business decisions")
    print("Process: Compare p-value to significance threshold (α)")
    print()

    stats = Stats()

    # Different significance levels
    p_values = [0.001, 0.01, 0.03, 0.05, 0.08, 0.15, 0.50]
    alphas = [0.01, 0.05, 0.10]

    print("P-value  │ α=0.01  │ α=0.05  │ α=0.10  │ Business Context")
    print("-" * 65)

    contexts = [
        "Medical device safety",
        "Financial fraud detection",
        "A/B test conversion",
        "Marketing campaign",
        "User experience change",
        "Exploratory analysis",
        "Preliminary investigation",
    ]

    for i, p_val in enumerate(p_values):
        row = f"{p_val:6.3f}  │"

        for alpha in alphas:
            result = stats.determine_statistical_significance(p_val, alpha)
            symbol = "  ✓    " if result["is_significant"] else "  ✗    "
            row += f"{symbol}│"

        context = contexts[i] if i < len(contexts) else "General analysis"
        row += f" {context}"
        print(row)

    print("\n📋 Interpretation Guide:")
    print("✓ = Statistically significant (act on this result)")
    print("✗ = Not significant (insufficient evidence)")
    print("\n🎯 Choosing α level:")
    print("• α=0.01: Conservative (medical, financial)")
    print("• α=0.05: Standard (most business applications)")
    print("• α=0.10: Liberal (exploratory, early research)")


def demonstrate_comprehensive_analysis():
    """Demonstrate the complete statistical analysis workflow."""
    print("\n\n🔬 COMPREHENSIVE STATISTICAL ANALYSIS")
    print("=" * 50)
    print("Complete workflow combining all statistical methods")
    print()

    stats = Stats()

    # Real business scenario
    print("📊 Scenario: E-commerce Fraud Detection")
    print("-" * 40)
    print("Comparing suspicious transaction patterns")
    print("Current period: 150 suspicious transactions")
    print("Baseline period: 75 suspicious transactions")
    print()

    # Perform comprehensive analysis
    analysis = stats.perform_comprehensive_analysis(150, 75)

    print("🔍 STATISTICAL ANALYSIS RESULTS:")
    print("=" * 40)

    # Counts and basic metrics
    counts = analysis["counts"]
    print(f"Current count: {counts['current']}")
    print(f"Baseline count: {counts['baseline']}")
    print(f"Expected under H₀: {counts['expected']:.1f}")
    print(f"Observed difference: {counts['difference']}")
    print()

    # Test statistics
    test_stats = analysis["test_statistics"]
    print(f"Chi-square statistic: {test_stats['chi_square']:.2f}")
    print(f"Z-score: {test_stats['z_score']:.2f}")
    print(f"Standard error: {test_stats['standard_error']:.2f}")
    print()

    # Significance
    print(f"P-value: {analysis['p_value']:.4f}")
    print(f"Statistically significant: {analysis['is_significant']}")
    print()

    # Confidence interval
    ci = analysis["confidence_interval"]
    print(f"95% Confidence Interval: [{ci['lower']:.1f}, {ci['upper']:.1f}]")
    print()

    # Effect size
    effect = analysis["effect_size"]
    print(f"Percentage change: {effect['percentage_change']:.0f}%")
    print(f"Effect magnitude: {effect['effect_magnitude']}")
    print(f"Cohen's d (approx): {effect['cohens_d_approx']:.2f}")
    print()

    # Business interpretation
    print("💼 BUSINESS INTERPRETATION:")
    print("=" * 30)
    print(analysis["interpretation"])
    print()

    # Decision guidance
    if analysis["is_significant"] and effect["effect_magnitude"] in [
        "LARGE",
        "VERY_LARGE",
        "EXTREME",
    ]:
        print("🚨 RECOMMENDATION: IMMEDIATE ACTION REQUIRED")
        print("• Investigate fraud patterns immediately")
        print("• Review security measures")
        print("• Alert fraud prevention team")
    elif analysis["is_significant"]:
        print("⚠️  RECOMMENDATION: MONITOR CLOSELY")
        print("• Increase monitoring frequency")
        print("• Prepare contingency plans")
        print("• Schedule follow-up analysis")
    else:
        print("✅ RECOMMENDATION: CONTINUE MONITORING")
        print("• Maintain current protocols")
        print("• Regular periodic reviews")
        print("• Document for trend analysis")


if __name__ == "__main__":
    print("🔬 STATISTICAL METHODS DEMONSTRATION")
    print("=" * 60)
    print("Complete guide to statistical calculations in Dataspot")
    print("All methods are fully documented with theory and examples")
    print()

    demonstrate_chi_square_calculation()
    demonstrate_p_value_calculation()
    demonstrate_confidence_intervals()
    demonstrate_effect_sizes()
    demonstrate_significance_determination()
    demonstrate_comprehensive_analysis()

    print("\n\n📚 SUMMARY OF DOCUMENTED METHODS:")
    print("=" * 50)
    print("✅ calculate_chi_square_statistic() - Goodness of fit test")
    print("✅ calculate_p_value_from_chi_square() - Significance probability")
    print("✅ calculate_confidence_interval() - Uncertainty quantification")
    print("✅ determine_statistical_significance() - Decision framework")
    print("✅ calculate_effect_size() - Practical magnitude")
    print("✅ calculate_standard_error() - Precision measurement")
    print("✅ calculate_z_score() - Standardized comparison")
    print("✅ perform_comprehensive_analysis() - Complete workflow")
    print()
    print("🎯 All methods include:")
    print("• Complete mathematical formulas")
    print("• Theoretical background")
    print("• Practical examples")
    print("• Business interpretations")
    print("• Usage guidelines")
    print("• References to statistical literature")
    print()
    print("📖 Each method answers specific questions:")
    print("• Chi-square: How different is this from expected?")
    print("• P-value: What's the chance this is just luck?")
    print("• Confidence interval: Where is the true value likely?")
    print("• Effect size: How big is this difference practically?")
    print("• Significance: Should I trust this result for decisions?")
    print()
    print("💡 Use these methods for:")
    print("• A/B testing analysis")
    print("• Fraud detection monitoring")
    print("• Business metrics evaluation")
    print("• Data quality assessment")
    print("• Performance monitoring")
    print("=" * 50)
