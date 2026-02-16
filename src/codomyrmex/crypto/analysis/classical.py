"""Classical cipher implementations and cryptanalysis.

Provides Caesar and Vigenere cipher encryption/decryption, automated
breaking of both cipher types, and cipher type detection based on
statistical analysis.
"""

from __future__ import annotations

import string
from dataclasses import dataclass

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.crypto.analysis.frequency import (
    expected_english_frequency,
    index_of_coincidence,
)

logger = get_logger(__name__)


@dataclass
class CaesarResult:
    """Result of a Caesar cipher decryption attempt."""

    shift: int
    plaintext: str
    score: float  # Chi-squared score against English frequencies (lower = better)


@dataclass
class VigenereResult:
    """Result of a Vigenere cipher decryption attempt."""

    key: str
    plaintext: str
    score: float


def _chi_squared_score(text: str) -> float:
    """Score text against English letter frequencies using chi-squared.

    Lower scores indicate closer match to English.
    """
    english_freq = expected_english_frequency()
    text_lower = text.lower()
    alpha_chars = [c for c in text_lower if c in string.ascii_lowercase]
    total = len(alpha_chars)

    if total == 0:
        return float("inf")

    from collections import Counter

    counts = Counter(alpha_chars)
    chi2 = 0.0

    for letter in string.ascii_lowercase:
        observed = counts.get(letter, 0)
        expected = (english_freq.get(letter, 0.0) / 100.0) * total
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected

    return chi2


def caesar_encrypt(plaintext: str, shift: int) -> str:
    """Encrypt text using the Caesar cipher.

    Shifts each letter by the specified amount. Preserves case and
    passes through non-alphabetic characters unchanged.

    Args:
        plaintext: Text to encrypt.
        shift: Number of positions to shift (0-25).

    Returns:
        Encrypted ciphertext.
    """
    shift = shift % 26
    result = []

    for ch in plaintext:
        if ch in string.ascii_lowercase:
            result.append(chr((ord(ch) - ord("a") + shift) % 26 + ord("a")))
        elif ch in string.ascii_uppercase:
            result.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
        else:
            result.append(ch)

    return "".join(result)


def caesar_decrypt(ciphertext: str, shift: int) -> str:
    """Decrypt text encrypted with the Caesar cipher.

    Args:
        ciphertext: Text to decrypt.
        shift: Number of positions that was used to encrypt (0-25).

    Returns:
        Decrypted plaintext.
    """
    return caesar_encrypt(ciphertext, -shift)


def break_caesar(ciphertext: str) -> list[CaesarResult]:
    """Break a Caesar cipher by trying all 26 shifts.

    Scores each decryption against English letter frequencies and
    returns results sorted by score (best match first).

    Args:
        ciphertext: The encrypted text to break.

    Returns:
        List of 26 CaesarResult entries sorted by chi-squared score
        (lowest/best first).
    """
    results = []

    for shift in range(26):
        plaintext = caesar_decrypt(ciphertext, shift)
        score = _chi_squared_score(plaintext)
        results.append(CaesarResult(shift=shift, plaintext=plaintext, score=score))

    results.sort(key=lambda r: r.score)

    logger.debug(
        "Caesar break: best shift=%d, score=%.2f",
        results[0].shift, results[0].score,
    )
    return results


def vigenere_encrypt(plaintext: str, key: str) -> str:
    """Encrypt text using the Vigenere cipher.

    Polyalphabetic substitution where each letter is shifted by the
    corresponding key letter. Non-alphabetic characters are preserved
    and do not advance the key position.

    Args:
        plaintext: Text to encrypt.
        key: Encryption key (alphabetic characters only).

    Returns:
        Encrypted ciphertext.

    Raises:
        ValueError: If key is empty or contains non-alphabetic characters.
    """
    if not key or not key.isalpha():
        raise ValueError("Key must be a non-empty alphabetic string")

    key_lower = key.lower()
    key_len = len(key_lower)
    result = []
    key_idx = 0

    for ch in plaintext:
        if ch in string.ascii_lowercase:
            shift = ord(key_lower[key_idx % key_len]) - ord("a")
            result.append(chr((ord(ch) - ord("a") + shift) % 26 + ord("a")))
            key_idx += 1
        elif ch in string.ascii_uppercase:
            shift = ord(key_lower[key_idx % key_len]) - ord("a")
            result.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
            key_idx += 1
        else:
            result.append(ch)

    return "".join(result)


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    """Decrypt text encrypted with the Vigenere cipher.

    Args:
        ciphertext: Text to decrypt.
        key: Decryption key (same key used for encryption).

    Returns:
        Decrypted plaintext.

    Raises:
        ValueError: If key is empty or contains non-alphabetic characters.
    """
    if not key or not key.isalpha():
        raise ValueError("Key must be a non-empty alphabetic string")

    # Invert the key: each letter's shift becomes 26 - shift
    inverted_key = "".join(
        chr((26 - (ord(c) - ord("a"))) % 26 + ord("a")) for c in key.lower()
    )
    return vigenere_encrypt(ciphertext, inverted_key)


def _estimate_key_length(ciphertext: str, max_key_length: int) -> int:
    """Estimate Vigenere key length using index of coincidence.

    For each candidate key length, split the ciphertext into columns
    and compute the average IC. The key length with average IC closest
    to English (0.0667) is selected.

    Args:
        ciphertext: Alpha-only lowercase ciphertext.
        max_key_length: Maximum key length to consider.

    Returns:
        Estimated key length.
    """
    alpha_text = "".join(c for c in ciphertext.lower() if c in string.ascii_lowercase)

    if len(alpha_text) < 2:
        return 1

    best_length = 1
    best_ic_diff = float("inf")
    english_ic = 0.0667

    for kl in range(1, min(max_key_length + 1, len(alpha_text) // 2 + 1)):
        columns = ["" for _ in range(kl)]
        for i, ch in enumerate(alpha_text):
            columns[i % kl] += ch

        avg_ic = sum(index_of_coincidence(col) for col in columns) / kl
        diff = abs(avg_ic - english_ic)

        if diff < best_ic_diff:
            best_ic_diff = diff
            best_length = kl

    logger.debug("Estimated key length: %d (IC diff: %.6f)", best_length, best_ic_diff)
    return best_length


def break_vigenere(
    ciphertext: str, max_key_length: int = 20,
) -> VigenereResult:
    """Break a Vigenere cipher by finding the key.

    Uses index of coincidence to estimate key length, then breaks
    each column independently as a Caesar cipher.

    Args:
        ciphertext: The encrypted text to break.
        max_key_length: Maximum key length to consider.

    Returns:
        VigenereResult with the recovered key, decrypted text, and score.
    """
    alpha_text = "".join(c for c in ciphertext.lower() if c in string.ascii_lowercase)

    if not alpha_text:
        return VigenereResult(key="a", plaintext=ciphertext, score=float("inf"))

    key_length = _estimate_key_length(ciphertext, max_key_length)

    # Split into columns and break each as Caesar
    columns = ["" for _ in range(key_length)]
    for i, ch in enumerate(alpha_text):
        columns[i % key_length] += ch

    key_chars = []
    for col in columns:
        best_shift = 0
        best_score = float("inf")
        for shift in range(26):
            decrypted = caesar_decrypt(col, shift)
            score = _chi_squared_score(decrypted)
            if score < best_score:
                best_score = score
                best_shift = shift
        key_chars.append(chr(best_shift + ord("a")))

    key = "".join(key_chars)

    # Reduce key if it is a repetition of a shorter key
    # e.g., "sunsunsunsun" -> "sun"
    key = _reduce_repeated_key(key)

    plaintext = vigenere_decrypt(ciphertext, key)
    score = _chi_squared_score(plaintext)

    logger.debug("Vigenere break: key='%s', score=%.2f", key, score)
    return VigenereResult(key=key, plaintext=plaintext, score=score)


def _reduce_repeated_key(key: str) -> str:
    """Reduce a key that is a repetition of a shorter pattern.

    For example, "abcabc" -> "abc", "xyzxyz" -> "xyz".

    Args:
        key: The key string to reduce.

    Returns:
        The shortest repeating unit of the key.
    """
    n = len(key)
    for length in range(1, n // 2 + 1):
        if n % length == 0:
            pattern = key[:length]
            if pattern * (n // length) == key:
                return pattern
    return key


def detect_cipher_type(ciphertext: str) -> str:
    """Detect the likely cipher type based on statistical analysis.

    Uses index of coincidence and frequency distribution patterns
    to classify text as plaintext, Caesar, Vigenere, or unknown.

    Strategy:
    - High IC (>= 0.050): Monoalphabetic (plaintext or Caesar).
      Distinguish by trying Caesar break: if shift=0 scores best,
      it is plaintext; otherwise it is Caesar.
    - Medium IC (0.040-0.050): Likely Vigenere (polyalphabetic).
    - Low IC (< 0.040): Random or unknown.

    Args:
        ciphertext: Text to analyze.

    Returns:
        One of: "plaintext", "caesar", "vigenere", "random/unknown".
    """
    alpha_text = "".join(c for c in ciphertext.lower() if c in string.ascii_lowercase)

    if len(alpha_text) < 10:
        return "random/unknown"

    ic = index_of_coincidence(ciphertext)

    logger.debug("Cipher detection: IC=%.6f", ic)

    # High IC means the letter distribution has peaks (monoalphabetic)
    # Both plaintext and Caesar have high IC because Caesar preserves
    # the frequency distribution shape -- it just shifts it.
    # For short texts, IC can be noisy, so we also try Caesar breaking
    # as a secondary check when IC is borderline.
    if ic >= 0.045:
        # Try all 26 Caesar shifts and check if shift=0 (identity) is best
        results = break_caesar(ciphertext)
        best_shift = results[0].shift
        # Check if the best decryption has a good score (close to English)
        # and that it is notably better than the second-best
        if best_shift == 0:
            return "plaintext"
        elif results[0].score < 200:
            # Strong frequency match at a non-zero shift indicates Caesar
            return "caesar"
        else:
            # High IC but poor frequency match at all shifts -- unusual
            return "vigenere" if ic < 0.055 else "caesar"
    elif ic >= 0.038:
        return "vigenere"
    else:
        return "random/unknown"
