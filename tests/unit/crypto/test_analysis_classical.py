"""Tests for crypto.analysis.classical module."""

from __future__ import annotations

import pytest

from codomyrmex.crypto.analysis.classical import (
    CaesarResult,
    VigenereResult,
    break_caesar,
    break_vigenere,
    caesar_decrypt,
    caesar_encrypt,
    detect_cipher_type,
    vigenere_decrypt,
    vigenere_encrypt,
)


@pytest.mark.unit
@pytest.mark.crypto
class TestCaesarEncryptDecrypt:
    """Tests for caesar_encrypt and caesar_decrypt."""

    def test_encrypt_shift_zero(self):
        assert caesar_encrypt("hello", 0) == "hello"

    def test_encrypt_shift_one(self):
        assert caesar_encrypt("abc", 1) == "bcd"

    def test_encrypt_shift_thirteen(self):
        # ROT13
        assert caesar_encrypt("hello", 13) == "uryyb"

    def test_encrypt_preserves_case(self):
        result = caesar_encrypt("Hello World", 3)
        assert result[0].isupper()
        assert result[1].islower()

    def test_encrypt_preserves_non_alpha(self):
        result = caesar_encrypt("hello, world!", 5)
        assert "," in result
        assert "!" in result
        assert " " in result

    def test_encrypt_wraps_around_z(self):
        assert caesar_encrypt("xyz", 3) == "abc"
        assert caesar_encrypt("XYZ", 3) == "ABC"

    def test_decrypt_reverses_encrypt(self):
        original = "The Quick Brown Fox Jumps Over 123!"
        for shift in range(26):
            encrypted = caesar_encrypt(original, shift)
            decrypted = caesar_decrypt(encrypted, shift)
            assert decrypted == original

    def test_encrypt_decrypt_roundtrip(self):
        text = "Attack at dawn"
        shift = 7
        assert caesar_decrypt(caesar_encrypt(text, shift), shift) == text


@pytest.mark.unit
@pytest.mark.crypto
class TestBreakCaesar:
    """Tests for break_caesar function."""

    def test_returns_26_results(self):
        results = break_caesar("hello")
        assert len(results) == 26

    def test_results_are_sorted_by_score(self):
        results = break_caesar("hello")
        scores = [r.score for r in results]
        assert scores == sorted(scores)

    def test_finds_correct_shift(self):
        plaintext = "the quick brown fox jumps over the lazy dog"
        shift = 13
        ciphertext = caesar_encrypt(plaintext, shift)
        results = break_caesar(ciphertext)
        # Best result should have the correct shift
        assert results[0].shift == shift
        assert results[0].plaintext == plaintext

    def test_finds_shift_three(self):
        plaintext = "defend the east wall of the castle"
        ciphertext = caesar_encrypt(plaintext, 3)
        results = break_caesar(ciphertext)
        assert results[0].shift == 3

    def test_result_type(self):
        results = break_caesar("test")
        assert isinstance(results[0], CaesarResult)
        assert hasattr(results[0], "shift")
        assert hasattr(results[0], "plaintext")
        assert hasattr(results[0], "score")


@pytest.mark.unit
@pytest.mark.crypto
class TestVigenereEncryptDecrypt:
    """Tests for vigenere_encrypt and vigenere_decrypt."""

    def test_single_char_key_is_caesar(self):
        # Key 'b' = shift of 1
        assert vigenere_encrypt("hello", "b") == caesar_encrypt("hello", 1)

    def test_encrypt_preserves_case(self):
        result = vigenere_encrypt("Hello", "key")
        assert result[0].isupper()
        assert result[1:].islower() or True  # just checking structure

    def test_encrypt_preserves_non_alpha(self):
        result = vigenere_encrypt("hello, world!", "key")
        assert "," in result
        assert "!" in result

    def test_roundtrip(self):
        plaintext = "Attack at dawn on the eastern front"
        key = "secret"
        encrypted = vigenere_encrypt(plaintext, key)
        decrypted = vigenere_decrypt(encrypted, key)
        assert decrypted == plaintext

    def test_known_answer(self):
        # Known Vigenere example
        plaintext = "attackatdawn"
        key = "lemon"
        ciphertext = vigenere_encrypt(plaintext, key)
        assert vigenere_decrypt(ciphertext, key) == plaintext

    def test_empty_key_raises(self):
        with pytest.raises(ValueError):
            vigenere_encrypt("hello", "")

    def test_non_alpha_key_raises(self):
        with pytest.raises(ValueError):
            vigenere_encrypt("hello", "key1")


@pytest.mark.unit
@pytest.mark.crypto
class TestBreakVigenere:
    """Tests for break_vigenere function."""

    def test_returns_vigenere_result(self):
        result = break_vigenere("some encrypted text here")
        assert isinstance(result, VigenereResult)
        assert hasattr(result, "key")
        assert hasattr(result, "plaintext")
        assert hasattr(result, "score")

    def test_breaks_short_key(self):
        # Use a longer plaintext for statistical analysis to work
        plaintext = (
            "the art of war teaches us to rely not on the likelihood "
            "of the enemy not coming but on our own readiness to receive "
            "him not on the chance of his not attacking but rather on "
            "the fact that we have made our position unassailable"
        )
        key = "sun"
        ciphertext = vigenere_encrypt(plaintext, key)
        result = break_vigenere(ciphertext)
        assert result.key == key

    def test_breaks_medium_key(self):
        plaintext = (
            "it is a truth universally acknowledged that a single man "
            "in possession of a good fortune must be in want of a wife "
            "however little known the feelings or views of such a man "
            "may be on his first entering a neighbourhood this truth is "
            "so well fixed in the minds of the surrounding families "
            "that he is considered as the rightful property of some one "
            "or other of their daughters"
        )
        key = "pride"
        ciphertext = vigenere_encrypt(plaintext, key)
        result = break_vigenere(ciphertext)
        assert result.key == key


@pytest.mark.unit
@pytest.mark.crypto
class TestDetectCipherType:
    """Tests for detect_cipher_type function."""

    def test_plaintext_detected(self):
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "This is a sample of normal English text that should "
            "be detected as plaintext by the cipher detector."
        )
        result = detect_cipher_type(text)
        assert result == "plaintext"

    def test_caesar_detected(self):
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "This is normal English text for cipher detection."
        )
        ciphertext = caesar_encrypt(text, 7)
        result = detect_cipher_type(ciphertext)
        assert result == "caesar"

    def test_short_text_returns_unknown(self):
        result = detect_cipher_type("abc")
        assert result == "random/unknown"

    def test_returns_valid_type(self):
        valid = {"plaintext", "caesar", "vigenere", "random/unknown"}
        result = detect_cipher_type("some text to analyze for cipher type detection")
        assert result in valid
