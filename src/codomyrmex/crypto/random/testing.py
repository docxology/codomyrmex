"""NIST SP 800-22 statistical randomness tests.

Implements a subset of the NIST Statistical Test Suite for validating
the quality of random number generators:

- **Monobit (Frequency) Test**: Checks that the proportion of 0s and 1s
  is approximately equal.
- **Runs Test**: Checks that the number of uninterrupted runs of identical
  bits is as expected for a truly random sequence.
- **Block Frequency Test**: Checks that the frequency of 1s within
  M-bit blocks is approximately M/2.

Reference: NIST Special Publication 800-22, Revision 1a.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from codomyrmex.crypto.exceptions import RandomError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_SIGNIFICANCE_LEVEL = 0.01  # alpha = 1%


@dataclass
class TestResult:
    """Result of a single NIST randomness test."""

    test_name: str
    passed: bool
    p_value: float
    statistic: float


def _bytes_to_bits(data: bytes) -> list[int]:
    """Convert a bytes object to a list of individual bits (MSB first)."""
    bits: list[int] = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def _erfc(x: float) -> float:
    """Complementary error function using math.erfc."""
    return math.erfc(x)


def monobit_test(data: bytes) -> TestResult:
    """NIST SP 800-22 Frequency (Monobit) Test.

    Determines whether the number of ones and zeros in a binary sequence
    are approximately the same, as expected for a truly random sequence.

    Args:
        data: At least 1 byte of random data to test.

    Returns:
        TestResult with the monobit test outcome.

    Raises:
        RandomError: If data is empty.
    """
    if not data:
        raise RandomError("Monobit test requires at least 1 byte of data")

    bits = _bytes_to_bits(data)
    n = len(bits)

    # Convert bits {0,1} to {-1,+1} and sum
    s_n = sum(2 * b - 1 for b in bits)
    s_obs = abs(s_n) / math.sqrt(n)
    p_value = _erfc(s_obs / math.sqrt(2))

    passed = p_value >= _SIGNIFICANCE_LEVEL
    logger.debug(
        "Monobit test: n=%d, S_n=%d, s_obs=%.4f, p_value=%.6f, passed=%s",
        n, s_n, s_obs, p_value, passed,
    )

    return TestResult(
        test_name="Monobit (Frequency) Test",
        passed=passed,
        p_value=p_value,
        statistic=s_obs,
    )


def runs_test(data: bytes) -> TestResult:
    """NIST SP 800-22 Runs Test.

    Determines whether the number of runs (uninterrupted sequences of
    identical bits) is as expected for a random sequence. A prerequisite
    monobit proportion check is applied first.

    Args:
        data: At least 1 byte of random data to test.

    Returns:
        TestResult with the runs test outcome. If the prerequisite check
        fails, p_value is set to 0.0.

    Raises:
        RandomError: If data is empty.
    """
    if not data:
        raise RandomError("Runs test requires at least 1 byte of data")

    bits = _bytes_to_bits(data)
    n = len(bits)

    # Pre-test: proportion of ones
    pi = sum(bits) / n
    tau = 2.0 / math.sqrt(n)

    if abs(pi - 0.5) >= tau:
        logger.debug(
            "Runs test: prerequisite failed, pi=%.4f, tau=%.4f", pi, tau,
        )
        return TestResult(
            test_name="Runs Test",
            passed=False,
            p_value=0.0,
            statistic=0.0,
        )

    # Count runs: V_obs is the number of positions where bit[k] != bit[k+1],
    # plus 1.
    v_obs = 1 + sum(1 for k in range(n - 1) if bits[k] != bits[k + 1])

    numerator = abs(v_obs - 2.0 * n * pi * (1.0 - pi))
    denominator = 2.0 * math.sqrt(2.0 * n) * pi * (1.0 - pi)

    if denominator == 0:
        p_value = 0.0
    else:
        p_value = _erfc(numerator / denominator)

    passed = p_value >= _SIGNIFICANCE_LEVEL
    logger.debug(
        "Runs test: n=%d, pi=%.4f, V_obs=%d, p_value=%.6f, passed=%s",
        n, pi, v_obs, p_value, passed,
    )

    return TestResult(
        test_name="Runs Test",
        passed=passed,
        p_value=p_value,
        statistic=float(v_obs),
    )


def block_frequency_test(data: bytes, block_size: int = 128) -> TestResult:
    """NIST SP 800-22 Block Frequency Test.

    Divides the bit sequence into non-overlapping blocks of *block_size*
    bits and determines whether the frequency of ones in each block is
    approximately block_size/2.

    Uses the chi-squared statistic with the regularized incomplete gamma
    function for computing the p-value.

    Args:
        data: Random data to test.
        block_size: Number of bits per block (M). Defaults to 128.

    Returns:
        TestResult with the block frequency test outcome.

    Raises:
        RandomError: If there is not enough data for at least one block.
    """
    if not data:
        raise RandomError("Block frequency test requires data")

    bits = _bytes_to_bits(data)
    n = len(bits)
    num_blocks = n // block_size

    if num_blocks == 0:
        raise RandomError(
            f"Not enough data for block_size={block_size}: "
            f"need at least {block_size} bits, got {n}"
        )

    # Compute proportion of ones in each block
    chi_squared = 0.0
    for i in range(num_blocks):
        start = i * block_size
        block = bits[start : start + block_size]
        pi_i = sum(block) / block_size
        chi_squared += (pi_i - 0.5) ** 2

    chi_squared *= 4.0 * block_size

    # p-value from incomplete gamma function:
    # P = igamc(num_blocks/2, chi_squared/2)
    # = 1 - gammainc(num_blocks/2, chi_squared/2)
    p_value = _igamc(num_blocks / 2.0, chi_squared / 2.0)

    passed = p_value >= _SIGNIFICANCE_LEVEL
    logger.debug(
        "Block frequency test: n=%d, blocks=%d, M=%d, chi2=%.4f, "
        "p_value=%.6f, passed=%s",
        n, num_blocks, block_size, chi_squared, p_value, passed,
    )

    return TestResult(
        test_name="Block Frequency Test",
        passed=passed,
        p_value=p_value,
        statistic=chi_squared,
    )


def run_nist_suite(data: bytes) -> list[TestResult]:
    """Run all implemented NIST SP 800-22 tests.

    Executes the monobit, runs, and block frequency tests on the
    provided data.

    Args:
        data: Random data to test (recommend >= 128 bytes).

    Returns:
        A list of TestResult objects, one per test.
    """
    results: list[TestResult] = []
    results.append(monobit_test(data))
    results.append(runs_test(data))

    # Only run block frequency if we have enough bits
    n_bits = len(data) * 8
    block_size = 128
    if n_bits >= block_size:
        results.append(block_frequency_test(data, block_size=block_size))
    else:
        # Use a smaller block size or skip
        results.append(
            TestResult(
                test_name="Block Frequency Test",
                passed=False,
                p_value=0.0,
                statistic=0.0,
            )
        )

    return results


# ---------------------------------------------------------------------------
# Incomplete gamma function helpers (pure Python, no scipy dependency)
# ---------------------------------------------------------------------------

def _igamc(a: float, x: float) -> float:
    """Upper regularized incomplete gamma function Q(a, x) = 1 - P(a, x).

    Uses the continued fraction representation for x >= a+1 and the
    series expansion otherwise. This is sufficient for the chi-squared
    p-value computation needed by the NIST tests.
    """
    if x < 0.0 or a <= 0.0:
        return 1.0
    if x == 0.0:
        return 1.0

    if x < a + 1.0:
        # Use series and subtract from 1
        return 1.0 - _igam_series(a, x)
    else:
        # Use continued fraction
        return _igamc_cf(a, x)


def _igam_series(a: float, x: float) -> float:
    """Lower regularized incomplete gamma P(a,x) via series expansion."""
    if x == 0.0:
        return 0.0

    lgamma_a = math.lgamma(a)
    term = 1.0 / a
    total = term

    for n in range(1, 300):
        term *= x / (a + n)
        total += term
        if abs(term) < abs(total) * 1e-15:
            break

    return total * math.exp(-x + a * math.log(x) - lgamma_a)


def _igamc_cf(a: float, x: float) -> float:
    """Upper regularized incomplete gamma Q(a,x) via continued fraction."""
    lgamma_a = math.lgamma(a)

    # Modified Lentz's method
    f = 1e-30
    c = 1e-30
    d = 1.0 / (x + 1.0 - a)
    f = d

    for i in range(1, 300):
        an = i * (a - i)
        bn = x + 2.0 * i + 1.0 - a
        d = bn + an * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = bn + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = c * d
        f *= delta
        if abs(delta - 1.0) < 1e-15:
            break

    return math.exp(-x + a * math.log(x) - lgamma_a) * f
