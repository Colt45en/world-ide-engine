#!/usr/bin/env python3
"""
Statistics & Probability Engine - Usage Examples
Demonstration of the comprehensive statistical analysis engine
"""

from statistics_engine import Statistics, ProbabilityDistributions, HypothesisTesting, RandomGenerator
import math

def main():
    print("=== Statistics & Probability Engine Demo ===\n")

    # Example 1: Basic Statistical Analysis
    print("1. Basic Statistical Analysis")
    print("-" * 30)

    # Sample dataset
    data = [12, 15, 18, 22, 25, 28, 30, 35, 40, 45]

    print(f"Dataset: {data}")
    print(f"Mean: {Statistics.mean(data):.2f}")
    print(f"Median: {Statistics.median(data):.2f}")
    print(f"Standard Deviation: {Statistics.std_dev(data):.2f}")
    print(f"Skewness: {Statistics.skewness(data):.3f}")
    print(f"Kurtosis: {Statistics.kurtosis(data):.3f}")
    print(f"IQR: {Statistics.iqr(data):.2f}")
    print()

    # Example 2: Linear Regression
    print("2. Linear Regression Analysis")
    print("-" * 32)

    x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y = [2.1, 4.0, 6.2, 8.1, 9.8, 12.2, 14.1, 16.0, 18.2, 20.1]

    slope, intercept, r_squared = Statistics.linear_regression(x, y)
    correlation = Statistics.correlation(x, y)

    print(f"X: {x}")
    print(f"Y: {y}")
    print(f"Correlation coefficient: {correlation:.4f}")
    print(f"Regression line: y = {slope:.2f}x + {intercept:.2f}")
    print(f"R² (coefficient of determination): {r_squared:.4f}")
    print()

    # Example 3: Hypothesis Testing
    print("3. Hypothesis Testing")
    print("-" * 22)

    # One-sample t-test
    sample = [98.2, 99.1, 100.3, 101.2, 99.8, 100.1, 99.9, 100.5]
    population_mean = 100.0

    t_stat, p_value = HypothesisTesting.t_test_one_sample(sample, population_mean)

    print(f"Sample temperatures: {sample}")
    print(f"Testing if mean ≠ {population_mean}°F")
    print(f"t-statistic: {t_stat:.3f}")
    print(f"p-value: {p_value:.4f}")

    if p_value < 0.05:
        print("Result: Reject null hypothesis (significant difference)")
    else:
        print("Result: Fail to reject null hypothesis (no significant difference)")
    print()

    # Example 4: Probability Distributions
    print("4. Probability Distributions")
    print("-" * 30)

    # Normal distribution
    mu, sigma = 100, 15
    x_value = 115

    pdf_value = ProbabilityDistributions.normal_pdf(x_value, mu, sigma)
    cdf_value = ProbabilityDistributions.normal_cdf(x_value, mu, sigma)

    print(f"Normal distribution (μ={mu}, σ={sigma})")
    print(f"P(X = {x_value}) ≈ {pdf_value:.6f}")
    print(f"P(X ≤ {x_value}) ≈ {cdf_value:.4f}")
    print()

    # Example 5: Random Number Generation
    print("5. Random Number Generation")
    print("-" * 30)

    # Generate samples from different distributions
    normal_samples = RandomGenerator.normal(mu=50, sigma=10, size=5)
    exp_samples = RandomGenerator.exponential(lambd=2.0, size=5)
    poisson_samples = RandomGenerator.poisson(lambd=3.0, size=5)

    print(f"Normal(50, 10) samples: {[f'{x:.1f}' for x in normal_samples]}")
    print(f"Exponential(λ=2) samples: {[f'{x:.3f}' for x in exp_samples]}")
    print(f"Poisson(λ=3) samples: {poisson_samples}")
    print()

    # Example 6: Chi-squared Goodness of Fit Test
    print("6. Chi-squared Goodness of Fit Test")
    print("-" * 37)

    # Test if dice is fair
    observed_rolls = [18, 22, 15, 19, 16, 20]  # Observed frequencies for dice faces
    expected_rolls = [18.0] * 6  # Expected frequencies for fair dice

    chi2_stat, p_value = HypothesisTesting.chi_squared_goodness_of_fit(
        observed_rolls, expected_rolls
    )

    print(f"Observed dice rolls: {observed_rolls}")
    print(f"Expected (fair dice): {expected_rolls}")
    print(f"χ² statistic: {chi2_stat:.3f}")
    print(f"p-value: {p_value:.4f}")

    if p_value < 0.05:
        print("Result: Reject null hypothesis (dice may not be fair)")
    else:
        print("Result: Fail to reject null hypothesis (dice appears fair)")
    print()

    print("=== Demo Complete ===")
    print("The Statistics & Probability Engine provides comprehensive")
    print("mathematical tools for data analysis and statistical testing.")

if __name__ == "__main__":
    main()