"""Entropy and randomness analysis for cryptographic data.

Provides Shannon entropy, byte entropy, chi-squared uniformity testing,
and serial correlation analysis for evaluating the randomness quality
of byte sequences and strings.
"""

from __future__ import annotations

import collections
import math
from dataclasses import dataclass

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class ChiSquaredResult:
    """Result of a chi-squared uniformity test on byte data."""

    statistic: float
    p_value: float
    uniform: bool  # True if p_value > 0.05


def shannon_entropy(data: bytes | str) -> float:
    """Calculate Shannon entropy of data.

    H = -sum(p_i * log2(p_i)) for each unique symbol.

    Args:
        data: Input bytes or string to analyze.

    Returns:
        Shannon entropy in bits per symbol. Returns 0.0 for empty data.
    """
    if not data:
        return 0.0

    counts = collections.Counter(data)
    total = len(data)
    entropy = 0.0

    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    logger.debug("Shannon entropy calculated: %.4f bits over %d symbols", entropy, total)
    return entropy


def byte_entropy(data: bytes) -> float:
    """Calculate Shannon entropy over byte values (0-255).

    Maximum possible entropy is 8.0 (log2(256)) for uniformly
    distributed byte data.

    Args:
        data: Input bytes to analyze.

    Returns:
        Entropy in bits per byte. Returns 0.0 for empty data.
    """
    if not data:
        return 0.0

    counts = [0] * 256
    for b in data:
        counts[b] += 1

    total = len(data)
    entropy = 0.0

    for count in counts:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    logger.debug("Byte entropy: %.4f / 8.0 bits over %d bytes", entropy, total)
    return entropy


def _incomplete_gamma_upper(a: float, x: float) -> float:
    """Compute the regularized upper incomplete gamma function Q(a, x).

    Uses the continued fraction expansion for Q(a, x) which converges
    well for x >= a + 1, and the series expansion for P(a, x) = 1 - Q(a, x)
    when x < a + 1.

    Args:
        a: Shape parameter (positive).
        x: Integration limit (non-negative).

    Returns:
        Q(a, x) = 1 - P(a, x), the regularized upper incomplete gamma.
    """
    if x < 0.0:
        return 1.0
    if x == 0.0:
        return 1.0

    # Use series expansion for P(a, x) when x < a + 1
    if x < a + 1.0:
        # P(a, x) = e^(-x) * x^a * sum(x^n / Gamma(a + n + 1))
        # Using the series: P(a,x) = (e^{-x} x^a / Gamma(a)) * sum_{n=0}^{inf} x^n / (a*(a+1)*...*(a+n))
        ap = a
        sum_val = 1.0 / a
        delta = 1.0 / a
        for _ in range(300):
            ap += 1.0
            delta *= x / ap
            sum_val += delta
            if abs(delta) < abs(sum_val) * 1e-12:
                break
        # P(a, x) = sum_val * exp(-x + a*ln(x) - lgamma(a))
        log_val = -x + a * math.log(x) - math.lgamma(a)
        if log_val > 700:
            return 0.0
        if log_val < -700:
            return 1.0
        p = sum_val * math.exp(log_val)
        return max(0.0, min(1.0, 1.0 - p))
    else:
        # Use Lentz's continued fraction for Q(a, x)
        # Q(a,x) = exp(-x + a*ln(x) - lgamma(a)) * CF
        b = x + 1.0 - a
        c = 1.0 / 1e-30
        d = 1.0 / b
        h = d
        for i in range(1, 300):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c = b + an / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-12:
                break
        log_val = -x + a * math.log(x) - math.lgamma(a)
        if log_val > 700:
            return 1.0
        if log_val < -700:
            return 0.0
        q = h * math.exp(log_val)
        return max(0.0, min(1.0, q))


def chi_squared_test(data: bytes) -> ChiSquaredResult:
    """Perform chi-squared uniformity test on byte data.

    Compares the observed byte frequency distribution against the
    expected uniform distribution (each byte value equally likely).

    Args:
        data: Input bytes to test for uniformity.

    Returns:
        ChiSquaredResult with test statistic, approximate p-value,
        and whether data appears uniformly distributed (p > 0.05).

    Raises:
        ValueError: If data is empty.
    """
    if not data:
        raise ValueError("Cannot perform chi-squared test on empty data")

    counts = [0] * 256
    for b in data:
        counts[b] += 1

    expected = len(data) / 256.0
    chi2 = sum((count - expected) ** 2 / expected for count in counts)

    # Degrees of freedom = 255
    df = 255.0
    # P-value from upper incomplete gamma function: Q(df/2, chi2/2)
    p_value = _incomplete_gamma_upper(df / 2.0, chi2 / 2.0)

    uniform = p_value > 0.05

    logger.debug(
        "Chi-squared test: statistic=%.2f, p_value=%.6f, uniform=%s",
        chi2, p_value, uniform,
    )
    return ChiSquaredResult(statistic=chi2, p_value=p_value, uniform=uniform)


def serial_correlation(data: bytes) -> float:
    """Calculate Pearson serial correlation between consecutive bytes.

    Measures the linear correlation between each byte and the next byte
    in the sequence. Random data should have correlation near 0.

    Args:
        data: Input bytes to analyze.

    Returns:
        Pearson correlation coefficient in range [-1.0, 1.0].
        Returns 0.0 for data with fewer than 2 bytes.
    """
    n = len(data)
    if n < 2:
        return 0.0

    # x = data[0..n-2], y = data[1..n-1]
    n_pairs = n - 1
    sum_x = 0.0
    sum_y = 0.0
    sum_xy = 0.0
    sum_x2 = 0.0
    sum_y2 = 0.0

    for i in range(n_pairs):
        x = float(data[i])
        y = float(data[i + 1])
        sum_x += x
        sum_y += y
        sum_xy += x * y
        sum_x2 += x * x
        sum_y2 += y * y

    numerator = n_pairs * sum_xy - sum_x * sum_y
    denom_x = n_pairs * sum_x2 - sum_x * sum_x
    denom_y = n_pairs * sum_y2 - sum_y * sum_y

    if denom_x <= 0 or denom_y <= 0:
        return 0.0

    r = numerator / math.sqrt(denom_x * denom_y)

    # Clamp to [-1, 1] for floating point safety
    r = max(-1.0, min(1.0, r))

    logger.debug("Serial correlation: %.6f over %d pairs", r, n_pairs)
    return r
