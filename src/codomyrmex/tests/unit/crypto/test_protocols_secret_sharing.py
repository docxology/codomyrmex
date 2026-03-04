"""Tests for crypto protocols secret sharing (Shamir's scheme).

Validates split/reconstruct round-trips, threshold properties,
edge cases, and share commitment verification.
"""

from __future__ import annotations

import pytest

from codomyrmex.crypto.exceptions import ProtocolError
from codomyrmex.crypto.protocols.secret_sharing import (
    Share,
    generate_share_commitment,
    reconstruct_secret,
    split_secret,
    verify_share,
)


@pytest.mark.unit
@pytest.mark.crypto
class TestShamirSplitReconstruct:
    """Core split and reconstruct round-trip tests."""

    def test_3_of_5_roundtrip(self) -> None:
        """k=3, n=5: any 3 shares reconstruct the secret."""
        secret = b"my top secret data"
        shares = split_secret(secret, n=5, k=3)
        assert len(shares) == 5

        # Use first 3 shares
        recovered = reconstruct_secret(shares[:3])
        assert recovered == secret

    def test_all_shares_roundtrip(self) -> None:
        """Using all n shares also works."""
        secret = b"full share set"
        shares = split_secret(secret, n=5, k=3)
        recovered = reconstruct_secret(shares)
        assert recovered == secret

    def test_any_k_subset_works(self) -> None:
        """Any k-subset of n shares must reconstruct correctly."""
        secret = b"subset test"
        shares = split_secret(secret, n=5, k=3)

        # Try multiple 3-element subsets
        subsets = [
            [shares[0], shares[1], shares[2]],
            [shares[0], shares[2], shares[4]],
            [shares[1], shares[3], shares[4]],
            [shares[2], shares[3], shares[4]],
        ]
        for subset in subsets:
            assert reconstruct_secret(subset) == secret

    def test_fewer_than_k_shares_gives_wrong_result(self) -> None:
        """k-1 shares must NOT reconstruct the correct secret."""
        secret = b"threshold security"
        shares = split_secret(secret, n=5, k=3)

        # Only 2 shares (k-1) should give a different result
        wrong_result = reconstruct_secret(shares[:2])
        assert wrong_result != secret

    def test_2_of_2_edge_case(self) -> None:
        """Minimum threshold: k=2, n=2."""
        secret = b"edge case"
        shares = split_secret(secret, n=2, k=2)
        assert len(shares) == 2
        recovered = reconstruct_secret(shares)
        assert recovered == secret

    def test_k_equals_n(self) -> None:
        """k=n: all shares required."""
        secret = b"all required"
        shares = split_secret(secret, n=4, k=4)
        recovered = reconstruct_secret(shares)
        assert recovered == secret

    def test_single_byte_secret(self) -> None:
        secret = b"\x42"
        shares = split_secret(secret, n=3, k=2)
        recovered = reconstruct_secret(shares[:2])
        assert recovered == secret

    def test_large_secret(self) -> None:
        """Test with a 31-byte secret (near field size boundary)."""
        secret = b"A" * 31  # 248 bits, well under 256-bit PRIME
        shares = split_secret(secret, n=5, k=3)
        recovered = reconstruct_secret(shares[:3])
        assert recovered == secret


@pytest.mark.unit
@pytest.mark.crypto
class TestShamirValidation:
    """Input validation and error handling tests."""

    def test_k_less_than_2_raises(self) -> None:
        with pytest.raises(ProtocolError, match="k must be >= 2"):
            split_secret(b"secret", n=3, k=1)

    def test_n_less_than_k_raises(self) -> None:
        with pytest.raises(ProtocolError, match="n must be >= threshold k"):
            split_secret(b"secret", n=2, k=3)

    def test_empty_secret_raises(self) -> None:
        with pytest.raises(ProtocolError, match="must not be empty"):
            split_secret(b"", n=3, k=2)

    def test_reconstruct_with_one_share_raises(self) -> None:
        with pytest.raises(ProtocolError, match="at least 2 shares"):
            reconstruct_secret([Share(index=1, value=42)])

    def test_reconstruct_duplicate_indices_raises(self) -> None:
        with pytest.raises(ProtocolError, match="distinct"):
            reconstruct_secret([Share(index=1, value=10), Share(index=1, value=20)])


@pytest.mark.unit
@pytest.mark.crypto
class TestShareCommitments:
    """Share commitment generation and verification tests."""

    def test_commitment_roundtrip(self) -> None:
        secret = b"commitment test"
        shares = split_secret(secret, n=3, k=2)
        for share in shares:
            commitment = generate_share_commitment(share)
            assert verify_share(share, commitment)

    def test_tampered_share_fails_verification(self) -> None:
        secret = b"tamper test"
        shares = split_secret(secret, n=3, k=2)
        commitment = generate_share_commitment(shares[0])

        # Tamper with the share value
        tampered = Share(index=shares[0].index, value=shares[0].value + 1)
        assert not verify_share(tampered, commitment)

    def test_wrong_index_fails_verification(self) -> None:
        secret = b"index test"
        shares = split_secret(secret, n=3, k=2)
        commitment = generate_share_commitment(shares[0])

        # Use wrong index
        wrong_index = Share(index=99, value=shares[0].value)
        assert not verify_share(wrong_index, commitment)
