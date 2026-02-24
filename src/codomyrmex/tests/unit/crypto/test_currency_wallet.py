"""Unit tests for codomyrmex.crypto.currency.wallet."""

from __future__ import annotations

import pytest

from codomyrmex.crypto.currency.wallet import (
    generate_mnemonic,
    mnemonic_to_seed,
    HDWallet,
    create_hd_wallet,
)


pytestmark = [pytest.mark.crypto, pytest.mark.unit]


# ---------------------------------------------------------------------------
# Mnemonic generation
# ---------------------------------------------------------------------------


class TestGenerateMnemonic:
    """Tests for BIP-39 mnemonic generation."""

    def test_default_24_words(self):
        """Test functionality: default 24 words."""
        mnemonic = generate_mnemonic()
        words = mnemonic.split()
        assert len(words) == 24, f"Expected 24 words, got {len(words)}"

    def test_12_words_with_128_bits(self):
        """Test functionality: 12 words with 128 bits."""
        mnemonic = generate_mnemonic(strength=128)
        words = mnemonic.split()
        assert len(words) == 12

    def test_all_words_are_strings(self):
        """Test functionality: all words are strings."""
        mnemonic = generate_mnemonic()
        for word in mnemonic.split():
            assert isinstance(word, str)
            assert word.isalpha()

    def test_different_mnemonics_each_call(self):
        """Test functionality: different mnemonics each call."""
        m1 = generate_mnemonic()
        m2 = generate_mnemonic()
        assert m1 != m2, "Two consecutive mnemonics should differ"


# ---------------------------------------------------------------------------
# Mnemonic to seed
# ---------------------------------------------------------------------------


class TestMnemonicToSeed:
    """Tests for BIP-39 seed derivation."""

    def test_seed_length_is_64_bytes(self):
        """Test functionality: seed length is 64 bytes."""
        mnemonic = generate_mnemonic(128)
        seed = mnemonic_to_seed(mnemonic)
        assert len(seed) == 64

    def test_deterministic_seed(self):
        """Test functionality: deterministic seed."""
        mnemonic = generate_mnemonic(128)
        s1 = mnemonic_to_seed(mnemonic)
        s2 = mnemonic_to_seed(mnemonic)
        assert s1 == s2, "Same mnemonic must produce same seed"

    def test_passphrase_changes_seed(self):
        """Test functionality: passphrase changes seed."""
        mnemonic = generate_mnemonic(128)
        s1 = mnemonic_to_seed(mnemonic, "")
        s2 = mnemonic_to_seed(mnemonic, "my-secret-passphrase")
        assert s1 != s2, "Passphrase should change derived seed"


# ---------------------------------------------------------------------------
# HD Wallet
# ---------------------------------------------------------------------------


class TestHDWallet:
    """Tests for BIP-32 HD wallet key derivation."""

    @pytest.fixture()
    def wallet(self):
        """Create a deterministic wallet from a known mnemonic."""
        mnemonic = generate_mnemonic(128)
        seed = mnemonic_to_seed(mnemonic)
        return HDWallet(seed)

    def test_master_key_depth_zero(self, wallet):
        """Test functionality: master key depth zero."""
        assert wallet.depth == 0
        assert wallet.index == 0
        assert wallet.parent_fingerprint == b"\x00\x00\x00\x00"

    def test_private_key_32_bytes(self, wallet):
        """Test functionality: private key 32 bytes."""
        assert len(wallet.private_key) == 32

    def test_chain_code_32_bytes(self, wallet):
        """Test functionality: chain code 32 bytes."""
        assert len(wallet.chain_code) == 32

    def test_child_derivation_increments_depth(self, wallet):
        """Test functionality: child derivation increments depth."""
        child = wallet.derive_child(0)
        assert child.depth == 1
        assert child.index == 0

    def test_hardened_derivation(self, wallet):
        """Test functionality: hardened derivation."""
        child = wallet.derive_child(0x80000000)
        assert child.depth == 1
        assert child.index == 0x80000000

    def test_different_indices_produce_different_keys(self, wallet):
        """Test functionality: different indices produce different keys."""
        c0 = wallet.derive_child(0)
        c1 = wallet.derive_child(1)
        assert c0.private_key != c1.private_key

    def test_parent_fingerprint_set_on_child(self, wallet):
        """Test functionality: parent fingerprint set on child."""
        child = wallet.derive_child(0)
        assert child.parent_fingerprint != b"\x00\x00\x00\x00"
        assert len(child.parent_fingerprint) == 4

    def test_multi_level_derivation(self, wallet):
        """Test functionality: multi level derivation."""
        child = wallet.derive_child(0x80000000 + 44)
        grandchild = child.derive_child(0x80000000)
        assert grandchild.depth == 2


# ---------------------------------------------------------------------------
# Address generation
# ---------------------------------------------------------------------------


class TestAddressGeneration:
    """Tests for wallet address generation."""

    @pytest.fixture()
    def wallet(self):
        mnemonic = generate_mnemonic(128)
        seed = mnemonic_to_seed(mnemonic)
        return HDWallet(seed)

    def test_bitcoin_address_starts_with_1(self, wallet):
        """Test functionality: bitcoin address starts with 1."""
        addr = wallet.get_address("bitcoin")
        assert addr.startswith("1"), f"Bitcoin mainnet address should start with '1', got {addr}"

    def test_ethereum_address_starts_with_0x(self, wallet):
        """Test functionality: ethereum address starts with 0x."""
        addr = wallet.get_address("ethereum")
        assert addr.startswith("0x")
        assert len(addr) == 42  # 0x + 40 hex chars

    def test_unsupported_network_raises(self, wallet):
        """Test functionality: unsupported network raises."""
        with pytest.raises(Exception):
            wallet.get_address("litecoin")


# ---------------------------------------------------------------------------
# Extended key serialization
# ---------------------------------------------------------------------------


class TestExtendedKeys:
    """Tests for xpub/xpriv serialization."""

    @pytest.fixture()
    def wallet(self):
        mnemonic = generate_mnemonic(128)
        seed = mnemonic_to_seed(mnemonic)
        return HDWallet(seed)

    def test_xpub_starts_with_xpub(self, wallet):
        """Test functionality: xpub starts with xpub."""
        xpub = wallet.export_xpub()
        assert xpub.startswith("xpub"), f"Expected xpub prefix, got {xpub[:10]}"

    def test_xpriv_starts_with_xprv(self, wallet):
        """Test functionality: xpriv starts with xprv."""
        xpriv = wallet.export_xpriv()
        assert xpriv.startswith("xprv"), f"Expected xprv prefix, got {xpriv[:10]}"

    def test_xpub_xpriv_differ(self, wallet):
        """Test functionality: xpub xpriv differ."""
        assert wallet.export_xpub() != wallet.export_xpriv()

    def test_child_xpub_differs_from_parent(self, wallet):
        """Test functionality: child xpub differs from parent."""
        child = wallet.derive_child(0)
        assert wallet.export_xpub() != child.export_xpub()


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------


class TestCreateHDWallet:
    """Tests for the create_hd_wallet factory."""

    def test_without_mnemonic_generates_wallet(self):
        """Test functionality: without mnemonic generates wallet."""
        w = create_hd_wallet()
        assert w.depth == 0
        assert len(w.private_key) == 32

    def test_with_mnemonic(self):
        """Test functionality: with mnemonic."""
        mnemonic = generate_mnemonic(128)
        w = create_hd_wallet(mnemonic)
        assert w.depth == 0

    def test_same_mnemonic_same_wallet(self):
        """Test functionality: same mnemonic same wallet."""
        mnemonic = generate_mnemonic(128)
        w1 = create_hd_wallet(mnemonic)
        w2 = create_hd_wallet(mnemonic)
        assert w1.private_key == w2.private_key
        assert w1.chain_code == w2.chain_code
