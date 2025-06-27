"""Statistical Methods for Data Comparison Analysis.

This module contains well-documented statistical calculation methods used in
temporal and segmental data comparisons. Each method includes comprehensive
documentation explaining the theory, mathematical formulas, interpretation,
and practical applications.

Author: Dataspot Team
"""

import math
from typing import Any, Dict


class Stats:
    """A collection of statistical methods for data comparison analysis.

    This class provides methods for calculating various statistical measures
    including chi-square tests, p-values, confidence intervals, and effect sizes.
    All methods are designed for business intelligence and data monitoring applications.
    """

    def calculate_chi_square_statistic(self, observed: int, expected: float) -> float:
        """Calculate the chi-square statistic for goodness of fit test.

        The chi-square statistic measures how much the observed frequencies
        deviate from the expected frequencies. It's the foundation for determining
        statistical significance in categorical data analysis.

        Mathematical Formula:
            χ² = Σ[(Observed - Expected)² / Expected]

        For our case with two groups:
            χ² = (observed - expected)² / expected

        Args:
            observed (int): The actual count observed in the current period
            expected (float): The expected count based on null hypothesis
                            (typically the average of current and baseline)

        Returns:
            float: Chi-square statistic value

        Theory:
            - χ² = 0: Perfect match between observed and expected
            - χ² > 0: Deviation from expected (larger values = more deviation)
            - Critical value at α=0.05: χ² ≈ 3.84 (for 1 degree of freedom)

        Example:
            >>> stats = Stats()
            >>> chi_sq = stats.calculate_chi_square_statistic(60, 50.0)
            >>> print(f"Chi-square: {chi_sq}")  # Output: 2.0

        """
        if expected <= 0:
            return 0.0

        chi_square = ((observed - expected) ** 2) / expected
        return chi_square

    def calculate_p_value_from_chi_square(
        self, chi_square: float, degrees_of_freedom: int = 1
    ) -> float:
        """Calculate p-value from chi-square statistic using exponential approximation.

        The p-value represents the probability of observing a test statistic at least
        as extreme as the one calculated, assuming the null hypothesis is true.
        In simpler terms: "What's the chance this result is just random luck?"

        Mathematical Approximation:
            For 1 degree of freedom: p ≈ e^(-χ²/2)
            (This is a simplified approximation of the actual chi-square distribution)

        Args:
            chi_square (float): The calculated chi-square statistic
            degrees_of_freedom (int): Degrees of freedom (default: 1 for two-group comparison)

        Returns:
            float: P-value between 0 and 1

        Interpretation:
            - p < 0.001: Extremely strong evidence against null hypothesis
            - p < 0.01:  Very strong evidence against null hypothesis
            - p < 0.05:  Strong evidence against null hypothesis (standard threshold)
            - p < 0.10:  Weak evidence against null hypothesis
            - p ≥ 0.10:  Little to no evidence against null hypothesis

        Example:
            >>> stats = Stats()
            >>> p_val = stats.calculate_p_value_from_chi_square(4.0)
            >>> print(f"P-value: {p_val:.4f}")  # Output: 0.1353
            >>> is_significant = p_val < 0.05   # False

        Note:
            This is a simplified approximation. For production statistical analysis,
            consider using scipy.stats.chi2.sf(chi_square, df) for exact p-values.

        """
        if chi_square <= 0:
            return 1.0

        # Simplified approximation for 1 degree of freedom
        if degrees_of_freedom == 1:
            # For very large chi-square values, set a minimum p-value
            if chi_square > 10:
                return 0.001
            p_value = math.exp(-chi_square / 2)
        else:
            # Basic approximation for other degrees of freedom
            # Note: This is very simplified and not recommended for production
            p_value = math.exp(-chi_square / (2 * degrees_of_freedom))

        return min(p_value, 1.0)

    def calculate_confidence_interval(
        self, current_count: int, baseline_count: int, confidence_level: float = 0.95
    ) -> Dict[str, float]:
        """Calculate confidence interval for the difference between two counts.

        A confidence interval provides a range of values that likely contains
        the true population parameter. It quantifies the uncertainty in our estimate.

        Mathematical Formula:
            CI = difference ± (critical_value × standard_error)

        For count differences (simplified approach):
            difference = current_count - baseline_count
            standard_error ≈ √(current_count + baseline_count)
            critical_value = 1.96 (for 95% confidence level)

        Args:
            current_count (int): Count in current period
            baseline_count (int): Count in baseline period
            confidence_level (float): Confidence level (0.95 = 95%)

        Returns:
            Dict[str, float]: Dictionary containing:
                - 'lower': Lower bound of confidence interval
                - 'upper': Upper bound of confidence interval
                - 'margin_of_error': Half-width of the interval
                - 'difference': Point estimate of difference

        Interpretation:
            If we repeated this comparison 100 times with different samples,
            approximately 95 times the true difference would fall within this interval.

        Example:
            >>> stats = Stats()
            >>> ci = stats.calculate_confidence_interval(60, 40)
            >>> print(f"95% CI: [{ci['lower']:.1f}, {ci['upper']:.1f}]")
            >>> # Output: 95% CI: [0.4, 39.6]

        Critical Values (two-tailed):
            - 90% confidence: 1.645
            - 95% confidence: 1.96
            - 99% confidence: 2.576

        Note:
            This uses a simplified approach suitable for count data comparisons.
            For more sophisticated analysis, consider using bootstrap methods or
            exact statistical distributions.

        """
        difference = current_count - baseline_count

        # Handle edge case where baseline is zero
        if baseline_count == 0:
            return {
                "lower": 0.0,
                "upper": float(current_count),
                "margin_of_error": float(current_count),
                "difference": float(difference),
            }

        # Simplified standard error calculation for count differences
        # This assumes Poisson distribution approximation for counts
        standard_error = math.sqrt(current_count + baseline_count)

        # Critical value for given confidence level (two-tailed)
        critical_values = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        critical_value = critical_values.get(confidence_level, 1.96)

        # Calculate margin of error
        margin_of_error = critical_value * standard_error

        # Calculate bounds
        lower_bound = difference - margin_of_error
        upper_bound = difference + margin_of_error

        return {
            "lower": lower_bound,
            "upper": upper_bound,
            "margin_of_error": margin_of_error,
            "difference": float(difference),
        }

    def determine_statistical_significance(
        self, p_value: float, alpha: float = 0.05
    ) -> Dict[str, Any]:
        """Determine if results are statistically significant based on p-value.

        Statistical significance is a determination about the null hypothesis:
        whether the observed effect is likely due to chance or represents a real effect.

        Null Hypothesis (H₀): There is no real difference between groups
        Alternative Hypothesis (H₁): There is a real difference between groups

        Args:
            p_value (float): Calculated p-value from statistical test
            alpha (float): Significance level threshold (default: 0.05)

        Returns:
            Dict[str, Any]: Dictionary containing:
                - 'is_significant': Boolean indicating if result is significant
                - 'significance_level': The alpha level used
                - 'interpretation': Human-readable interpretation
                - 'confidence_level': Corresponding confidence level (1 - alpha)

        Decision Rules:
            - If p ≤ α: Reject null hypothesis → Result is significant
            - If p > α: Fail to reject null hypothesis → Result is not significant

        Example:
            >>> stats = Stats()
            >>> result = stats.determine_statistical_significance(0.03)
            >>> print(result['interpretation'])
            >>> # Output: "Statistically significant at α=0.05 level"

        Common Significance Levels:
            - α = 0.10: Less stringent (90% confidence)
            - α = 0.05: Standard in most fields (95% confidence)
            - α = 0.01: More stringent (99% confidence)

        Type I & Type II Errors:
            - Type I Error (α): False positive - concluding significance when none exists
            - Type II Error (β): False negative - missing real significance

        """
        is_significant = p_value <= alpha
        confidence_level = 1 - alpha

        # Generate interpretation
        if is_significant:
            if p_value <= 0.001:
                strength = "extremely strong"
            elif p_value <= 0.01:
                strength = "very strong"
            else:
                strength = "strong"
            interpretation = f"Statistically significant (p={p_value:.4f}) - {strength} evidence against null hypothesis"
        else:
            interpretation = f"Not statistically significant (p={p_value:.4f}) - insufficient evidence to reject null hypothesis"

        return {
            "is_significant": is_significant,
            "significance_level": alpha,
            "interpretation": interpretation,
            "confidence_level": confidence_level,
            "p_value": p_value,
        }

    def calculate_effect_size(
        self, current_count: int, baseline_count: int
    ) -> Dict[str, Any]:
        """Calculate effect size measures to quantify the magnitude of difference.

        Effect size measures provide information about the practical significance
        of a finding, beyond just statistical significance. They answer:
        "How big is this difference in practical terms?"

        Calculated Measures:
            1. Absolute Difference: |current - baseline|
            2. Relative Change: (current - baseline) / baseline
            3. Cohen's d approximation: standardized mean difference
            4. Percentage Change: relative change × 100

        Args:
            current_count (int): Count in current period
            baseline_count (int): Count in baseline period

        Returns:
            Dict[str, float]: Dictionary containing:
                - 'absolute_difference': Absolute difference between counts
                - 'relative_change': Proportional change (decimal)
                - 'percentage_change': Percentage change
                - 'cohens_d_approx': Approximate Cohen's d
                - 'effect_magnitude': Categorical magnitude assessment

        Cohen's d Interpretation:
            - |d| = 0.20: Small effect
            - |d| = 0.50: Medium effect
            - |d| = 0.80: Large effect

        Example:
            >>> stats = Stats()
            >>> effect = stats.calculate_effect_size(60, 40)
            >>> print(f"Relative change: {effect['relative_change']:.2%}")
            >>> # Output: "Relative change: 50.00%"

        """
        absolute_difference = abs(current_count - baseline_count)

        # Handle edge case where baseline is zero
        if baseline_count == 0:
            if current_count == 0:
                relative_change = 0.0
                percentage_change = 0.0
            else:
                relative_change = float("inf")
                percentage_change = float("inf")
        else:
            relative_change = (current_count - baseline_count) / baseline_count
            percentage_change = relative_change * 100

        # Approximate Cohen's d for count data
        # This is a simplified approximation
        pooled_std = math.sqrt((current_count + baseline_count) / 2)
        if pooled_std > 0:
            cohens_d_approx = (current_count - baseline_count) / pooled_std
        else:
            cohens_d_approx = 0.0

        # Categorize effect magnitude using threshold table
        # Thresholds are ordered from highest to lowest for efficient lookup
        effect_thresholds = [
            (float("inf"), "EXTREME"),  # Infinite change (new patterns)
            (1.0, "VERY_LARGE"),  # 100% or more change
            (0.5, "LARGE"),  # 50% or more change
            (0.2, "MEDIUM"),  # 20% or more change
            (0.1, "SMALL"),  # 10% or more change
            (0.0, "NEGLIGIBLE"),  # Less than 10% change
        ]

        abs_change = abs(relative_change)
        effect_magnitude = "NEGLIGIBLE"  # Default fallback

        for threshold, magnitude in effect_thresholds:
            if abs_change >= threshold:
                effect_magnitude = magnitude
                break

        return {
            "absolute_difference": float(absolute_difference),
            "relative_change": relative_change,
            "percentage_change": percentage_change,
            "cohens_d_approx": cohens_d_approx,
            "effect_magnitude": effect_magnitude,
        }

    def calculate_standard_error(
        self, count1: int, count2: int, method: str = "poisson"
    ) -> float:
        """Calculate standard error for count data comparisons.

        Standard error quantifies the uncertainty in our estimate of the difference
        between two counts. It's essential for confidence interval calculations
        and statistical inference.

        Mathematical Formulas:
            Poisson approximation: SE ≈ √(count1 + count2)
            Normal approximation: SE ≈ √((count1 + count2) / 4)

        Args:
            count1 (int): First count value
            count2 (int): Second count value
            method (str): Calculation method ("poisson" or "normal")

        Returns:
            float: Standard error estimate

        Theory:
            - Standard error decreases as sample size increases
            - Smaller SE = more precise estimates
            - Used in confidence intervals and hypothesis tests

        Example:
            >>> stats = Stats()
            >>> se = stats.calculate_standard_error(60, 40)
            >>> print(f"Standard Error: {se:.2f}")  # Output: 10.00

        """
        if method == "poisson":
            # Assumes counts follow Poisson distribution
            standard_error = math.sqrt(count1 + count2)
        elif method == "normal":
            # Assumes normal approximation to binomial
            standard_error = math.sqrt((count1 + count2) / 4)
        else:
            # Default to Poisson
            standard_error = math.sqrt(count1 + count2)

        return standard_error

    def calculate_z_score(
        self, observed: float, expected: float, standard_error: float
    ) -> float:
        """Calculate z-score for standardized comparison.

        The z-score indicates how many standard deviations an observation
        is from the expected value. It's useful for comparing across different scales.

        Mathematical Formula:
            z = (observed - expected) / standard_error

        Args:
            observed (float): Observed value
            expected (float): Expected value under null hypothesis
            standard_error (float): Standard error of the estimate

        Returns:
            float: Z-score (standardized difference)

        Interpretation:
            - |z| < 1.96: Not significant at α = 0.05
            - |z| ≥ 1.96: Significant at α = 0.05
            - |z| ≥ 2.58: Significant at α = 0.01

        Example:
            >>> stats = Stats()
            >>> z = stats.calculate_z_score(60, 50, 10)
            >>> print(f"Z-score: {z:.2f}")  # Output: 1.00

        """
        if standard_error == 0:
            return 0.0

        z_score = (observed - expected) / standard_error
        return z_score

    def perform_comprehensive_analysis(
        self, current_count: int, baseline_count: int
    ) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis combining all methods.

        This is the main orchestrator method that combines all statistical calculations
        to provide a complete analysis of the difference between two counts.

        Analysis Components:
            1. Chi-square goodness of fit test
            2. P-value calculation
            3. Confidence intervals
            4. Effect size measures
            5. Significance determination
            6. Z-score calculation

        Args:
            current_count (int): Count in current period
            baseline_count (int): Count in baseline period

        Returns:
            Dict[str, Any]: Comprehensive statistical analysis

        Example:
            >>> stats = Stats()
            >>> analysis = stats.perform_comprehensive_analysis(60, 40)
            >>> print(f"Significant: {analysis['is_significant']}")
            >>> print(f"P-value: {analysis['p_value']:.4f}")
            >>> print(f"Effect size: {analysis['effect_size']['effect_magnitude']}")

        Use Cases:
            - A/B testing analysis
            - Fraud detection monitoring
            - Business metrics evaluation
            - Data quality assessment

        """
        expected_current = (current_count + baseline_count) / 2

        chi_square = self.calculate_chi_square_statistic(
            current_count, expected_current
        )

        p_value = self.calculate_p_value_from_chi_square(chi_square)

        significance = self.determine_statistical_significance(p_value)

        confidence_interval = self.calculate_confidence_interval(
            current_count, baseline_count
        )

        effect_size = self.calculate_effect_size(current_count, baseline_count)

        standard_error = self.calculate_standard_error(current_count, baseline_count)
        z_score = self.calculate_z_score(
            current_count, expected_current, standard_error
        )

        interpretation = self._generate_interpretation(
            current_count, baseline_count, significance, effect_size
        )

        return {
            "counts": {
                "current": current_count,
                "baseline": baseline_count,
                "expected": expected_current,
                "difference": current_count - baseline_count,
            },
            "test_statistics": {
                "chi_square": chi_square,
                "z_score": z_score,
                "standard_error": standard_error,
            },
            "p_value": p_value,
            "is_significant": significance["is_significant"],
            "confidence_interval": confidence_interval,
            "effect_size": effect_size,
            "significance_details": significance,
            "interpretation": interpretation,
        }

    def _generate_interpretation(
        self,
        current_count: int,
        baseline_count: int,
        significance: Dict[str, Any],
        effect_size: Dict[str, Any],
    ) -> str:
        """Generate human-readable interpretation of statistical results.

        Args:
            current_count (int): Current period count
            baseline_count (int): Baseline period count
            significance (Dict): Significance test results
            effect_size (Dict): Effect size measurements

        Returns:
            str: Human-readable interpretation

        """
        direction = "INCREASE" if current_count > baseline_count else "DECREASE"
        change_pct = abs(effect_size["percentage_change"])

        if effect_size["percentage_change"] == float("inf"):
            magnitude_desc = f"New pattern appeared ({current_count} occurrences)"
        elif baseline_count == 0:
            magnitude_desc = f"New pattern with {current_count} occurrences"
        else:
            magnitude_desc = (
                f"{change_pct:.0f}% {direction} ({baseline_count} → {current_count})"
            )

        significance_desc = (
            "statistically significant"
            if significance["is_significant"]
            else "not statistically significant"
        )
        effect_magnitude = effect_size["effect_magnitude"]

        interpretation = (
            f"Observed {magnitude_desc}. "
            f"This change is {significance_desc} (p={significance['p_value']:.3f}) "
            f"with {effect_magnitude} practical impact."
        )

        return interpretation
