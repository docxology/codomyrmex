"""Tests for the crypto random submodule.

Covers the CSPRNG utilities and the NIST SP 800-22 statistical tests.
"""

from __future__ import annotations

import os
import re
import string

import pytest

from codomyrmex.crypto.exceptions import RandomError
from codomyrmex.crypto.random import (
    NistTestResult,
    block_frequency_test,
    generate_nonce,
    generate_uuid4,
    monobit_test,
    run_nist_suite,
    runs_test,
    secure_random_bytes,
    secure_random_int,
    secure_random_string,
)

# -------------------------------------------------------------------------
# Generator tests
# -------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.crypto
class TestSecureRandomBytes:
    """Tests for secure_random_bytes."""

    def test_returns_correct_length(self) -> None:
        """Test functionality: returns correct length."""
        for n in (0, 1, 16, 32, 256, 1024):
            result = secure_random_bytes(n)
            assert len(result) == n
            assert isinstance(result, bytes)

    def test_zero_bytes(self) -> None:
        """Test functionality: zero bytes."""
        assert secure_random_bytes(0) == b""

    def test_negative_raises(self) -> None:
        """Test functionality: negative raises."""
        with pytest.raises(RandomError):
            secure_random_bytes(-1)

    def test_different_each_call(self) -> None:
        """Test functionality: different each call."""
        a = secure_random_bytes(32)
        b = secure_random_bytes(32)
        # Extremely unlikely to be equal for 32 bytes
        assert a != b


@pytest.mark.unit
@pytest.mark.crypto
class TestSecureRandomInt:
    """Tests for secure_random_int."""

    def test_within_range(self) -> None:
        """Test functionality: within range."""
        for _ in range(200):
            val = secure_random_int(10, 20)
            assert 10 <= val <= 20

    def test_single_value_range(self) -> None:
        """Test functionality: single value range."""
        assert secure_random_int(42, 42) == 42

    def test_negative_range(self) -> None:
        """Test functionality: negative range."""
        for _ in range(100):
            val = secure_random_int(-10, -1)
            assert -10 <= val <= -1

    def test_min_greater_than_max_raises(self) -> None:
        """Test functionality: min greater than max raises."""
        with pytest.raises(RandomError):
            secure_random_int(10, 5)


@pytest.mark.unit
@pytest.mark.crypto
class TestSecureRandomString:
    """Tests for secure_random_string."""

    def test_correct_length(self) -> None:
        """Test functionality: correct length."""
        for length in (0, 1, 10, 50, 100):
            result = secure_random_string(length)
            assert len(result) == length

    def test_default_charset(self) -> None:
        """Test functionality: default charset."""
        valid_chars = set(string.ascii_letters + string.digits)
        result = secure_random_string(500)
        assert all(c in valid_chars for c in result)

    def test_custom_charset(self) -> None:
        """Test functionality: custom charset."""
        result = secure_random_string(100, charset="abc")
        assert all(c in "abc" for c in result)

    def test_negative_length_raises(self) -> None:
        """Test functionality: negative length raises."""
        with pytest.raises(RandomError):
            secure_random_string(-1)

    def test_empty_charset_raises(self) -> None:
        """Test functionality: empty charset raises."""
        with pytest.raises(RandomError):
            secure_random_string(10, charset="")

    def test_zero_length(self) -> None:
        """Test functionality: zero length."""
        assert secure_random_string(0) == ""


@pytest.mark.unit
@pytest.mark.crypto
class TestGenerateUUID4:
    """Tests for generate_uuid4."""

    _UUID4_RE = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )

    def test_format(self) -> None:
        """Test functionality: format."""
        uid = generate_uuid4()
        assert self._UUID4_RE.match(uid), f"Invalid UUID4 format: {uid}"

    def test_uniqueness(self) -> None:
        """Test functionality: uniqueness."""
        uuids = {generate_uuid4() for _ in range(100)}
        assert len(uuids) == 100


@pytest.mark.unit
@pytest.mark.crypto
class TestGenerateNonce:
    """Tests for generate_nonce."""

    def test_default_length(self) -> None:
        """Test functionality: default length."""
        nonce = generate_nonce()
        assert len(nonce) == 16

    def test_custom_length(self) -> None:
        """Test functionality: custom length."""
        for size in (8, 12, 24, 32, 64):
            nonce = generate_nonce(size)
            assert len(nonce) == size

    def test_zero_size_raises(self) -> None:
        """Test functionality: zero size raises."""
        with pytest.raises(RandomError):
            generate_nonce(0)

    def test_negative_size_raises(self) -> None:
        """Test functionality: negative size raises."""
        with pytest.raises(RandomError):
            generate_nonce(-5)


# -------------------------------------------------------------------------
# NIST statistical test suite
# -------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.crypto
class TestMonobitTest:
    """Tests for the NIST monobit (frequency) test."""

    def test_passes_for_random_data(self) -> None:
        """Test functionality: passes for random data."""
        data = os.urandom(1024)
        result = monobit_test(data)
        assert isinstance(result, NistTestResult)
        assert result.test_name == "Monobit (Frequency) Test"
        assert result.passed is True
        assert result.p_value >= 0.01

    def test_fails_for_all_zeros(self) -> None:
        """Test functionality: fails for all zeros."""
        data = b"\x00" * 1024
        result = monobit_test(data)
        assert result.passed is False
        assert result.p_value < 0.01

    def test_fails_for_all_ones(self) -> None:
        """Test functionality: fails for all ones."""
        data = b"\xff" * 1024
        result = monobit_test(data)
        assert result.passed is False
        assert result.p_value < 0.01

    def test_empty_raises(self) -> None:
        """Test functionality: empty raises."""
        with pytest.raises(RandomError):
            monobit_test(b"")


@pytest.mark.unit
@pytest.mark.crypto
class TestRunsTest:
    """Tests for the NIST runs test."""

    def test_passes_for_random_data(self) -> None:
        """Test functionality: passes for random data."""
        data = os.urandom(1024)
        result = runs_test(data)
        assert isinstance(result, NistTestResult)
        assert result.test_name == "Runs Test"
        assert result.passed is True
        assert result.p_value >= 0.01

    def test_fails_for_all_zeros(self) -> None:
        """Test functionality: fails for all zeros."""
        # All zeros has pi=0.0, fails prerequisite
        data = b"\x00" * 1024
        result = runs_test(data)
        assert result.passed is False

    def test_empty_raises(self) -> None:
        """Test functionality: empty raises."""
        with pytest.raises(RandomError):
            runs_test(b"")


@pytest.mark.unit
@pytest.mark.crypto
class TestBlockFrequencyTest:
    """Tests for the NIST block frequency test."""

    def test_passes_for_random_data(self) -> None:
        """Test functionality: passes for random data."""
        data = os.urandom(1024)
        result = block_frequency_test(data)
        assert isinstance(result, NistTestResult)
        assert result.test_name == "Block Frequency Test"
        assert result.passed is True
        assert result.p_value >= 0.01

    def test_insufficient_data_raises(self) -> None:
        """Test functionality: insufficient data raises."""
        # 8 bits < default block_size of 128
        with pytest.raises(RandomError, match="Not enough data"):
            block_frequency_test(b"\xaa")

    def test_empty_raises(self) -> None:
        """Test functionality: empty raises."""
        with pytest.raises(RandomError):
            block_frequency_test(b"")

    def test_custom_block_size(self) -> None:
        """Test functionality: custom block size."""
        data = os.urandom(256)
        result = block_frequency_test(data, block_size=64)
        assert result.passed is True


@pytest.mark.unit
@pytest.mark.crypto
class TestRunNistSuite:
    """Tests for the full NIST suite runner."""

    def test_returns_three_results(self) -> None:
        """Test functionality: returns three results."""
        data = os.urandom(1024)
        results = run_nist_suite(data)
        assert len(results) == 3
        assert all(isinstance(r, NistTestResult) for r in results)

    def test_all_pass_for_random_data(self) -> None:
        """Test functionality: all pass for random data."""
        data = os.urandom(1024)
        results = run_nist_suite(data)
        for r in results:
            assert r.passed is True, f"{r.test_name} failed with p_value={r.p_value}"
