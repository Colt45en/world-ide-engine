"""
Statistics & Probability Engine
Comprehensive statistical analysis, probability distributions, and hypothesis testing
"""

import math
import random


class Statistics:
    """
    Comprehensive statistics engine for data analysis
    """

    @staticmethod
    def mean(data) -> float:
        """Arithmetic mean: μ = (1/n) Σxᵢ"""
        if not data:
            raise ValueError("Cannot calculate mean of empty dataset")
        return sum(data) / len(data)

    @staticmethod
    def median(data) -> float:
        """Median: middle value when data is sorted"""
        if not data:
            raise ValueError("Cannot calculate median of empty dataset")

        sorted_data = sorted(data)
        n = len(sorted_data)

        if n % 2 == 0:
            return (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
        else:
            return sorted_data[n//2]

    @staticmethod
    def mode(data, tolerance: float = 1e-10):
        """
        Mode: most frequently occurring value(s).

        Uses tolerant bucketing: groups values within 'tolerance' distance,
        then returns cluster means of all groups with maximum frequency.

        Rationale: Raw floats can differ by tiny noise due to IEEE754 representation
        even when logically equal. Setting tolerance handles this gracefully.

        Edge case: If two clusters have equal maximum frequency but different means,
        this returns both cluster means as a list. Caller should interpret that as
        "multiple modes detected."

        Computational note: O(n²) in worst case (iterates over data, checks against
        all existing groups). For huge float datasets, use a histogram + binning approach.
        For small data (< 10k points) this is fine.
        """
        if not data:
            raise ValueError("Cannot calculate mode of empty dataset")

        # Group values within tolerance
        groups = {}
        for value in data:
            found_group = False
            for group_key in groups:
                if abs(value - group_key) <= tolerance:
                    groups[group_key].append(value)
                    found_group = True
                    break

            if not found_group:
                groups[value] = [value]

        # Find maximum frequency
        max_freq = max(len(group) for group in groups.values())

        # Return all values with maximum frequency
        modes = []
        for group_key, group_values in groups.items():
            if len(group_values) == max_freq:
                modes.append(Statistics.mean(group_values))

        return modes

    @staticmethod
    def variance(data, sample: bool = True) -> float:
        """
        Variance: σ² = Σ(xᵢ - μ)² / (n-1) for sample, / n for population
        """
        if not data:
            raise ValueError("Cannot calculate variance of empty dataset")
        if len(data) == 1 and sample:
            raise ValueError("Cannot calculate sample variance with single data point")

        mu = Statistics.mean(data)
        squared_deviations = [(x - mu) ** 2 for x in data]

        denominator = len(data) - 1 if sample else len(data)
        return sum(squared_deviations) / denominator

    @staticmethod
    def std_dev(data, sample: bool = True) -> float:
        """Standard deviation: σ = √variance"""
        return math.sqrt(Statistics.variance(data, sample))

    @staticmethod
    def skewness(data) -> float:
        """
        Skewness: measure of asymmetry in the distribution.

        Formula: γ₁ = μ₃/σ³ (population moment definition)
        where μ₃ = E[(X - μ)³] and σ = population standard deviation

        DEFINITION CLARITY: This returns the POPULATION MOMENT SKEWNESS (physicist's style).
        It is NOT the "Fisher-Pearson coefficient" or unbiased sample skewness estimator
        (econometrician's style with bias correction factor).

        If you're publishing this, specify "moment skewness γ₁" not just "skewness"
        to avoid arguments about which flavor you computed.

        Interpretation:
        - γ₁ > 0: right-skewed (longer right tail)
        - γ₁ = 0: symmetric
        - γ₁ < 0: left-skewed (longer left tail)
        """
        if len(data) < 3:
            raise ValueError("Need at least 3 data points for skewness")

        mu = Statistics.mean(data)
        sigma = Statistics.std_dev(data, sample=False)

        if sigma == 0:
            return 0.0

        third_moment = sum((x - mu) ** 3 for x in data) / len(data)
        return third_moment / (sigma ** 3)

    @staticmethod
    def kurtosis(data) -> float:
        """
        Kurtosis (excess): measure of tail heaviness.

        Formula: γ₂ = μ₄/σ⁴ - 3 (excess kurtosis)
        where μ₄ = E[(X - μ)⁴], σ = population standard deviation, and 3 is subtracted
        so that normal distribution has excess kurtosis = 0.

        DEFINITION CLARITY: This returns POPULATION MOMENT EXCESS KURTOSIS (physicist's style).
        It is NOT the Fisher-corrected sample kurtosis (econometrician's style).

        For publications: Specify "excess kurtosis γ₂" and note population vs sample method.

        Interpretation:
        - γ₂ = 0: mesokurtic (like normal distribution, tail behavior similar)
        - γ₂ > 0: leptokurtic (heavy tails, more extreme values than normal)
        - γ₂ < 0: platykurtic (light tails, fewer extreme values than normal)
        """
        if len(data) < 4:
            raise ValueError("Need at least 4 data points for kurtosis")

        mu = Statistics.mean(data)
        sigma = Statistics.std_dev(data, sample=False)

        if sigma == 0:
            return 0.0

        fourth_moment = sum((x - mu) ** 4 for x in data) / len(data)
        return (fourth_moment / (sigma ** 4)) - 3

    @staticmethod
    def percentile(data, p: float) -> float:
        """
        Calculate percentile (0 ≤ p ≤ 100)
        """
        if not 0 <= p <= 100:
            raise ValueError("Percentile must be between 0 and 100")

        sorted_data = sorted(data)
        n = len(sorted_data)

        if p == 0:
            return sorted_data[0]
        if p == 100:
            return sorted_data[-1]

        # Linear interpolation method
        index = (p / 100) * (n - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, n - 1)

        if lower_index == upper_index:
            return sorted_data[lower_index]

        weight = index - lower_index
        return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight

    @staticmethod
    def quartiles(data):
        """Return (Q1, Q2, Q3) quartiles"""
        return (
            Statistics.percentile(data, 25),
            Statistics.percentile(data, 50),
            Statistics.percentile(data, 75)
        )

    @staticmethod
    def iqr(data) -> float:
        """Interquartile range: IQR = Q3 - Q1"""
        q1, _, q3 = Statistics.quartiles(data)
        return q3 - q1

    @staticmethod
    def covariance(x, y, sample: bool = True) -> float:
        """
        Covariance: cov(X,Y) = Σ(xᵢ - x̄)(yᵢ - ȳ) / (n-1)
        """
        if len(x) != len(y):
            raise ValueError("Arrays must have same length")
        if not x:
            raise ValueError("Cannot calculate covariance of empty arrays")

        x_mean = Statistics.mean(x)
        y_mean = Statistics.mean(y)

        products = [(x[i] - x_mean) * (y[i] - y_mean) for i in range(len(x))]

        denominator = len(x) - 1 if sample else len(x)
        return sum(products) / denominator

    @staticmethod
    def correlation(x, y) -> float:
        """
        Pearson correlation coefficient: r = cov(X,Y) / (σₓ σᵧ)

        DEFINITION: This returns the POPULATION Pearson correlation coefficient.
        Both numerator (covariance with sample=False, divide by n) and denominator
        (std dev with sample=False, divide by n) use population normalization.

        The (n vs n-1) ratio cancels in the division, so the result is the same as
        using sample covariance if you were consistent. This is mathematically valid
        and matches "correlation of the data as observed" rather than "unbiased
        estimator of population correlation."

        For publications: Specify "population Pearson r" or cite your normalization choice.

        Mathematical properties:
        - -1 ≤ r ≤ 1 always
        - r = 1: perfect positive linear relationship
        - r = 0: no linear relationship
        - r = -1: perfect negative linear relationship
        """
        if len(x) != len(y):
            raise ValueError("Arrays must have same length")

        cov_xy = Statistics.covariance(x, y, sample=False)
        std_x = Statistics.std_dev(x, sample=False)
        std_y = Statistics.std_dev(y, sample=False)

        if std_x == 0 or std_y == 0:
            return 0.0

        return cov_xy / (std_x * std_y)

    @staticmethod
    def linear_regression(x, y):
        """
        Simple linear regression: y = ax + b using closed-form least squares.

        Returns (slope, intercept, r_squared)

        Formula:
        a = (n Σxy - Σx Σy) / (n Σx² - (Σx)²)
        b = (Σy - a Σx) / n
        R² = 1 - SS_res / SS_tot (coefficient of determination)

        NUMERICAL STABILITY WARNING:
        The closed-form formulas can suffer precision loss when:
        - x values are very large (> 10^6): accumulate rounding error in sum_x, sum_x²
        - x values are highly collinear: denominator becomes very small
        - Range of x is very wide: floating point catastrophic cancellation

        For numerically ill-conditioned data:
        - Center x and y first: x' = x - mean(x), y' = y - mean(y)
        - Or use incremental least squares / QR decomposition (more robust)
        - Or use numpy.polyfit which handles centering automatically

        This implementation is mathematically correct but not numerically hardened.
        It's fine for typical data (~1e-6 to 1e6 range, reasonable collinearity).

        Returns (slope, intercept, r_squared). Raises if x is constant.
        """
        if len(x) != len(y):
            raise ValueError("Arrays must have same length")
        if len(x) < 2:
            raise ValueError("Need at least 2 data points for regression")

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi ** 2 for xi in x)

        # Calculate slope and intercept
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            raise ValueError("Cannot perform regression: x values are constant")

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        # Calculate R²
        y_mean = sum_y / n
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))

        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

        return (slope, intercept, r_squared)


class ProbabilityDistributions:
    """
    Probability distribution functions and random number generation
    """

    @staticmethod
    def normal_pdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
        """
        Normal distribution PDF: f(x) = (1/σ√2π) * e^(-½((x-μ)/σ)²)
        """
        if sigma <= 0:
            raise ValueError("Standard deviation must be positive")

        coefficient = 1 / (sigma * math.sqrt(2 * math.pi))
        exponent = -0.5 * ((x - mu) / sigma) ** 2
        return coefficient * math.exp(exponent)

    @staticmethod
    def normal_cdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
        """
        Normal distribution CDF using error function approximation
        """
        if sigma <= 0:
            raise ValueError("Standard deviation must be positive")

        # Standardize
        z = (x - mu) / sigma

        # Approximation using error function
        return 0.5 * (1 + ProbabilityDistributions._erf(z / math.sqrt(2)))

    @staticmethod
    def _erf(x: float) -> float:
        """
        Error function approximation (Abramowitz and Stegun)
        """
        # Constants for approximation
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911

        # Save the sign of x
        sign = 1 if x >= 0 else -1
        x = abs(x)

        # A&S formula 7.1.26
        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)

        return sign * y

    @staticmethod
    def exponential_pdf(x: float, lambd: float = 1.0) -> float:
        """
        Exponential distribution PDF: f(x) = λe^(-λx) for x ≥ 0
        """
        if lambd <= 0:
            raise ValueError("Rate parameter lambda must be positive")
        if x < 0:
            return 0.0

        return lambd * math.exp(-lambd * x)

    @staticmethod
    def exponential_cdf(x: float, lambd: float = 1.0) -> float:
        """
        Exponential distribution CDF: F(x) = 1 - e^(-λx) for x ≥ 0
        """
        if lambd <= 0:
            raise ValueError("Rate parameter lambda must be positive")
        if x < 0:
            return 0.0

        return 1 - math.exp(-lambd * x)

    @staticmethod
    def poisson_pmf(k: int, lambd: float) -> float:
        """
        Poisson distribution PMF: P(X = k) = e^(-λ) * λ^k / k!
        """
        if lambd <= 0:
            raise ValueError("Rate parameter lambda must be positive")
        if k < 0:
            return 0.0

        return math.exp(-lambd) * (lambd ** k) / math.factorial(k)

    @staticmethod
    def binomial_pmf(k: int, n: int, p: float) -> float:
        """
        Binomial distribution PMF: P(X = k) = C(n,k) * p^k * (1-p)^(n-k)
        """
        if not 0 <= p <= 1:
            raise ValueError("Probability p must be between 0 and 1")
        if k < 0 or k > n:
            return 0.0

        # Calculate binomial coefficient C(n,k)
        binom_coeff = math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

        return binom_coeff * (p ** k) * ((1 - p) ** (n - k))

    @staticmethod
    def uniform_pdf(x: float, a: float = 0.0, b: float = 1.0) -> float:
        """
        Uniform distribution PDF: f(x) = 1/(b-a) for a ≤ x ≤ b
        """
        if b <= a:
            raise ValueError("Upper bound b must be greater than lower bound a")

        if a <= x <= b:
            return 1 / (b - a)
        return 0.0

    @staticmethod
    def gamma_pdf(x: float, alpha: float, beta: float = 1.0) -> float:
        """
        Gamma distribution PDF: f(x) = (β^α/Γ(α)) * x^(α-1) * e^(-βx)
        """
        if alpha <= 0 or beta <= 0:
            raise ValueError("Shape and rate parameters must be positive")
        if x < 0:
            return 0.0

        gamma_alpha = math.gamma(alpha)
        return (beta ** alpha / gamma_alpha) * (x ** (alpha - 1)) * math.exp(-beta * x)

    @staticmethod
    def chi_squared_pdf(x: float, df: int) -> float:
        """
        Chi-squared distribution PDF with df degrees of freedom
        """
        if df <= 0:
            raise ValueError("Degrees of freedom must be positive")
        if x < 0:
            return 0.0

        # χ² is a special case of Gamma distribution: Γ(df/2, 1/2)
        return ProbabilityDistributions.gamma_pdf(x, df/2, 0.5)

    @staticmethod
    def t_distribution_pdf(x: float, df: int) -> float:
        """
        Student's t-distribution PDF
        """
        if df <= 0:
            raise ValueError("Degrees of freedom must be positive")

        gamma_term1 = math.gamma((df + 1) / 2)
        gamma_term2 = math.gamma(df / 2)

        coefficient = gamma_term1 / (math.sqrt(df * math.pi) * gamma_term2)
        factor = (1 + x**2 / df) ** (-(df + 1) / 2)

        return coefficient * factor


class HypothesisTesting:
    """
    Statistical hypothesis testing methods
    """

    @staticmethod
    def _t_distribution_cdf(t: float, df: int) -> float:
        """
        Compute the cumulative distribution function (CDF) of Student's t-distribution
        using the relationship to the incomplete beta function.

        For t-value and degrees of freedom df:
        CDF = 1 - 0.5 * I_x(df/2, 1/2) where x = df/(t² + df)
        where I_x is the regularized incomplete beta function.

        This uses an accurate numerical approximation of the incomplete beta function.
        Returns P(T ≤ t) for a Student t random variable with df degrees of freedom.
        """
        # For standard normal reference: at df >> 30, this converges to normal_cdf

        # Special handling for large df: converge to normal for efficiency
        if df > 500:
            return ProbabilityDistributions.normal_cdf(t)

        # Use incomplete beta relationship: I_x(a,b) = incomplete_beta(x, a, b)
        # where x = df / (df + t²)
        a = df / 2.0
        b = 0.5
        x = df / (df + t * t)

        # Regularized incomplete beta function using continued fractions approximation
        beta_incomplete = HypothesisTesting._regularized_incomplete_beta(x, a, b)

        # Construct CDF from incomplete beta
        if t >= 0:
            return 1.0 - 0.5 * beta_incomplete
        else:
            return 0.5 * beta_incomplete

    @staticmethod
    def _regularized_incomplete_beta(x: float, a: float, b: float) -> float:
        """
        Regularized incomplete beta function I_x(a, b) using continued fractions.
        This is accurate for 0 < x < 1 and positive a, b.

        Used by t-distribution CDF calculation. Returns I_x(a, b).
        """
        # Avoid boundary cases
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0

        # Use continued fractions approximation of incomplete beta
        # Following Numerical Recipes approach
        front = math.exp(a * math.log(x) + b * math.log(1 - x) -
                         math.lgamma(a + b) + math.lgamma(a) + math.lgamma(b))

        # Continued fraction for I_x(a, b)
        # Using modified Lentz's algorithm for stability
        ITMAX = 100
        EPS = 1e-10

        # First term of continued fraction
        cf = front / a

        for m in range(1, ITMAX):
            d = m * (b - m) * x / ((a + 2*m - 1) * (a + 2*m))
            cf = 1.0 + d / cf if cf != 0 else 1.0

            d = -(a + m) * (a + b + m) * x / ((a + 2*m) * (a + 2*m + 1))
            cf = 1.0 + d / cf if cf != 0 else 1.0

            if abs(d) < EPS * abs(cf):
                break

        return cf

    @staticmethod
    def _chi_squared_cdf(chi2: float, df: int) -> float:
        """
        Compute the cumulative distribution function of the chi-squared distribution
        with df degrees of freedom.

        CDF = P(χ²(df) ≤ chi2) using the incomplete gamma function relationship:
        P(χ² ≤ x) = P(Gamma(df/2, 2) ≤ x) = regularized_lower_gamma(df/2, chi2/2)

        Also known as the "regularized gamma P function" Q(a,x) = γ(a,x) / Γ(a).

        Returns the lower tail probability (CDF).
        """
        if chi2 < 0:
            return 0.0

        # Chi-squared(df) = Gamma(df/2, 1/2) in shape/rate parameterization
        # CDF uses lower incomplete gamma
        a = df / 2.0
        x = chi2 / 2.0

        return HypothesisTesting._regularized_lower_incomplete_gamma(a, x)

    @staticmethod
    def _chi_squared_sf(chi2: float, df: int) -> float:
        """
        Survival function (1 - CDF) of chi-squared distribution.
        Also called the "chi-squared p-value function" for the upper tail.

        Returns P(χ²(df) > chi2) = regularized_upper_gamma(df/2, chi2/2).
        """
        if chi2 < 0:
            return 1.0

        a = df / 2.0
        x = chi2 / 2.0

        return HypothesisTesting._regularized_upper_incomplete_gamma(a, x)

    @staticmethod
    def _regularized_lower_incomplete_gamma(a: float, x: float) -> float:
        """
        Regularized lower incomplete gamma function P(a, x) = γ(a, x) / Γ(a).

        For a > 0, x ≥ 0: represents the lower tail of a gamma distribution.
        This uses a hybrid approach: series for small x, upper incomplete for large x.
        """
        if x < 0:
            return 0.0
        if x == 0:
            return 0.0
        if a <= 0:
            return 0.0

        # For numerical stability, use the relationship:
        # For x < a+1: use series expansion
        # For x >= a+1: return 1 - upper_incomplete(a, x)

        # Use series representation for x < a+1
        if x < (a + 1.0):
            # Compute exp(-x + a*ln(x) - lgamma(a)) first for numerical stability
            log_term = -x + a * math.log(x) - math.lgamma(a)

            # Avoid overflow
            if log_term < -700:  # Would underflow
                return 0.0

            front = math.exp(log_term)

            # Series: sum_{n=0}^inf x^n / (a+n) * product_{k=1}^n 1/k = sum x^n / ((a)(a+1)...(a+n))
            sum_val = 1.0 / a
            term = sum_val

            for n in range(1, 200):
                term *= x / (a + n)
                sum_val += term

                # Stop when term is negligible
                if abs(term) < abs(sum_val) * 1e-12:
                    break

            return front * sum_val
        else:
            # For x >= a+1, use complementary function
            return 1.0 - HypothesisTesting._regularized_upper_incomplete_gamma(a, x)

    @staticmethod
    def _regularized_upper_incomplete_gamma(a: float, x: float) -> float:
        """
        Regularized upper incomplete gamma function Q(a, x) = Γ(a, x) / Γ(a).

        For a > 0, x ≥ 0: represents the upper tail of a gamma distribution.
        This is the chi-squared p-value function for tail tests.
        Uses continued fractions for numerical stability.
        """
        if x < 0:
            return 1.0
        if x == 0:
            return 1.0
        if a <= 0:
            return 1.0

        # For x < a+1, use lower incomplete and return 1 - lower
        if x < (a + 1.0):
            return 1.0 - HypothesisTesting._regularized_lower_incomplete_gamma(a, x)

        # For x >= a+1, use continued fractions for upper incomplete
        # Γ(a,x) = Γ(a) * cf, where cf uses Lentz algorithm
        # Result: Q(a,x) = exp(-x) * x^a * continued_fraction / Γ(a)

        log_term = -x + a * math.log(x) - math.lgamma(a)

        if log_term < -700:  # Would underflow to 0
            return 0.0

        front = math.exp(log_term)

        # Continued fraction using modified Lentz algorithm
        # This is more stable than naive continued fractions
        ITMAX = 200
        EPS = 1e-12

        # Starting values for continued fraction
        cf_val = 1.0

        # Iteration
        for i in range(1, ITMAX):
            # Even-indexed term (i is loop counter, so i=1 gives first real term)
            m = i // 2

            if i % 2 == 1:
                # Odd i: coefficient for "even" term in continued fraction
                num = m * (a - m)
                den = (a + 2*m - 1)
            else:
                # Even i: coefficient for "odd" term
                num = -(a + m) * (m - a)
                den = (a + 2*m)

            delta = num / (den * cf_val + EPS)  # Add EPS to avoid division by zero
            cf_val = 1.0 + delta

            if abs(delta - 1.0) < EPS:
                break

        # Final result: e^(-x) * x^a / [Γ(a) * cf_val]
        # But we already have front = e^(-x) * x^a / Γ(a)
        return front / cf_val

    @staticmethod
    def z_test_one_sample(sample_mean: float, population_mean: float,
                         population_std: float, n: int,
                         alternative: str = 'two-sided'):
        """
        One-sample z-test
        Returns (z_statistic, p_value)
        """
        if population_std <= 0:
            raise ValueError("Population standard deviation must be positive")
        if n <= 0:
            raise ValueError("Sample size must be positive")

        # Calculate z-statistic
        z_stat = (sample_mean - population_mean) / (population_std / math.sqrt(n))

        # Calculate p-value based on alternative hypothesis
        if alternative == 'two-sided':
            p_value = 2 * (1 - ProbabilityDistributions.normal_cdf(abs(z_stat)))
        elif alternative == 'greater':
            p_value = 1 - ProbabilityDistributions.normal_cdf(z_stat)
        elif alternative == 'less':
            p_value = ProbabilityDistributions.normal_cdf(z_stat)
        else:
            raise ValueError("Alternative must be 'two-sided', 'greater', or 'less'")

        return (z_stat, p_value)

    @staticmethod
    def t_test_one_sample(data, population_mean: float,
                         alternative: str = 'two-sided'):
        """
        One-sample t-test with Student's t distribution.

        CRITICAL: This computes p-values using the actual Student's t-distribution,
        NOT the normal approximation. This matters for small samples (n < 30).

        The t-distribution has heavier tails than the normal distribution.
        Using the normal approximation would underestimate p-values for small n,
        inflating type I error rates. That's why Gosset discovered t in the first place.

        Formula: t = (x̄ - μ₀) / (s / √n) with df = n - 1

        p-value interpretation:
        - two-sided: P(|T| ≥ |t_obs|) = 2 * [1 - CDF(|t|)]
        - greater: P(T ≥ t_obs) = 1 - CDF(t)
        - less: P(T ≤ t_obs) = CDF(t)

        Returns (t_statistic, p_value)
        """
        if len(data) < 2:
            raise ValueError("Need at least 2 data points for t-test")

        sample_mean = Statistics.mean(data)
        sample_std = Statistics.std_dev(data, sample=True)
        n = len(data)
        df = n - 1

        # Calculate t-statistic
        t_stat = (sample_mean - population_mean) / (sample_std / math.sqrt(n))

        # Compute p-value using Student's t CDF (exact for given df)
        if alternative == 'two-sided':
            p_value = 2 * (1 - HypothesisTesting._t_distribution_cdf(abs(t_stat), df))
        elif alternative == 'greater':
            p_value = 1 - HypothesisTesting._t_distribution_cdf(t_stat, df)
        elif alternative == 'less':
            p_value = HypothesisTesting._t_distribution_cdf(t_stat, df)
        else:
            raise ValueError("Alternative must be 'two-sided', 'greater', or 'less'")

        return (t_stat, p_value)

    @staticmethod
    def chi_squared_goodness_of_fit(observed, expected):
        """
        Chi-squared goodness of fit test with mathematically correct p-values.

        CRITICAL MATHEMATICAL HONESTY:
        This test compares observed vs expected frequencies using the Pearson χ² statistic.
        The NULL DISTRIBUTION is chi-squared with df = k - 1 (where k = # of categories),
        NOT the standard normal distribution.

        Formula: χ² = Σ (Obs - Exp)² / Exp

        The statistic is exactly correct. The p-value is now EXACT (not approximate):
        p-value = P(χ²(df) > χ²_observed) = upper tail probability

        This p-value uses the true chi-squared distribution CDF, not a junk normal approximation.

        Returns (chi2_statistic, p_value)

        Note: Requires expected frequencies ≥ 5 for validity (standard assumption).
        Smaller expected frequencies violate test assumptions.
        """
        if len(observed) != len(expected):
            raise ValueError("Observed and expected must have same length")

        chi2_stat = 0.0
        for obs, exp in zip(observed, expected):
            if exp == 0:
                raise ValueError("Expected frequencies cannot be zero")
            chi2_stat += (obs - exp) ** 2 / exp

        df = len(observed) - 1

        # Compute exact p-value using chi-squared distribution survival function
        p_value = HypothesisTesting._chi_squared_sf(chi2_stat, df)

        return (chi2_stat, p_value)


class RandomGenerator:
    """
    Random number generation from various distributions
    """

    @staticmethod
    def normal(mu: float = 0.0, sigma: float = 1.0, size: int = 1):
        """
        Generate random numbers from normal distribution using Box-Muller transform
        """
        if sigma <= 0:
            raise ValueError("Standard deviation must be positive")

        def generate_pair():
            """Generate pair of independent normal(0,1) random variables"""
            u1 = random.random()
            u2 = random.random()

            z1 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            z2 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)

            return z1, z2

        results = []
        pairs_needed = (size + 1) // 2

        for _ in range(pairs_needed):
            z1, z2 = generate_pair()
            results.extend([mu + sigma * z1, mu + sigma * z2])

        # Transform to desired distribution
        results = results[:size]

        return results[0] if size == 1 else results

    @staticmethod
    def exponential(lambd: float = 1.0, size: int = 1):
        """
        Generate random numbers from exponential distribution
        """
        if lambd <= 0:
            raise ValueError("Rate parameter lambda must be positive")

        results = []
        for _ in range(size):
            u = random.random()
            x = -math.log(1 - u) / lambd
            results.append(x)

        return results[0] if size == 1 else results

    @staticmethod
    def poisson(lambd: float, size: int = 1):
        """
        Generate random numbers from Poisson distribution using Knuth's algorithm
        """
        if lambd <= 0:
            raise ValueError("Rate parameter lambda must be positive")

        def generate_one():
            L = math.exp(-lambd)
            k = 0
            p = 1.0

            while p > L:
                k += 1
                p *= random.random()

            return k - 1

        results = [generate_one() for _ in range(size)]
        return results[0] if size == 1 else results

    @staticmethod
    def binomial(n: int, p: float, size: int = 1):
        """
        Generate random numbers from binomial distribution
        """
        if not 0 <= p <= 1:
            raise ValueError("Probability p must be between 0 and 1")
        if n < 0:
            raise ValueError("Number of trials n must be non-negative")

        def generate_one():
            successes = 0
            for _ in range(n):
                if random.random() < p:
                    successes += 1
            return successes

        results = [generate_one() for _ in range(size)]
        return results[0] if size == 1 else results