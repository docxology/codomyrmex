"""Frequency analysis tools for cryptanalysis.

Provides character frequency counting, bigram analysis, index of
coincidence calculation, and standard English letter frequency
reference data.
"""

from __future__ import annotations

import collections
import string

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Standard English letter frequencies (percentages)
_ENGLISH_FREQUENCIES: dict[str, float] = {
    "e": 12.702,
    "t": 9.056,
    "a": 8.167,
    "o": 7.507,
    "i": 6.966,
    "n": 6.749,
    "s": 6.327,
    "h": 6.094,
    "r": 5.987,
    "d": 4.253,
    "l": 4.025,
    "c": 2.782,
    "u": 2.758,
    "m": 2.406,
    "w": 2.360,
    "f": 2.228,
    "g": 2.015,
    "y": 1.974,
    "p": 1.929,
    "b": 1.492,
    "v": 0.978,
    "k": 0.772,
    "j": 0.153,
    "x": 0.150,
    "q": 0.095,
    "z": 0.074,
}


def character_frequency(text: str) -> dict[str, float]:
    """Count frequency of each alphabetic character as a percentage.

    Only includes alphabetic characters. Case-insensitive.

    Args:
        text: Input text to analyze.

    Returns:
        Dictionary mapping lowercase letters to their frequency as
        a percentage of total alphabetic characters. Only letters
        that appear in the text are included.
    """
    text_lower = text.lower()
    alpha_chars = [c for c in text_lower if c in string.ascii_lowercase]
    total = len(alpha_chars)

    if total == 0:
        return {}

    counts = collections.Counter(alpha_chars)
    freq = {char: (count / total) * 100.0 for char, count in counts.items()}

    logger.debug("Character frequency analysis: %d unique chars from %d total", len(freq), total)
    return freq


def bigram_frequency(text: str) -> dict[str, float]:
    """Count frequency of consecutive letter pairs as a percentage.

    Only considers alphabetic characters (non-alpha characters are
    stripped before counting). Case-insensitive.

    Args:
        text: Input text to analyze.

    Returns:
        Dictionary mapping bigrams to their frequency as a percentage
        of total bigrams found.
    """
    text_lower = text.lower()
    alpha_chars = [c for c in text_lower if c in string.ascii_lowercase]
    total = len(alpha_chars) - 1

    if total <= 0:
        return {}

    bigrams: list[str] = []
    for i in range(total):
        bigrams.append(alpha_chars[i] + alpha_chars[i + 1])

    counts = collections.Counter(bigrams)
    freq = {bg: (count / total) * 100.0 for bg, count in counts.items()}

    logger.debug("Bigram frequency analysis: %d unique bigrams from %d total", len(freq), total)
    return freq


def index_of_coincidence(text: str) -> float:
    """Calculate the index of coincidence (IC) for a text.

    IC = sum(n_i * (n_i - 1)) / (N * (N - 1))

    where n_i is the count of letter i and N is the total number
    of letters. English text has IC approximately 0.0667; random text
    has IC approximately 0.0385.

    Args:
        text: Input text to analyze.

    Returns:
        Index of coincidence value. Returns 0.0 for texts with
        fewer than 2 alphabetic characters.
    """
    text_lower = text.lower()
    alpha_chars = [c for c in text_lower if c in string.ascii_lowercase]
    n = len(alpha_chars)

    if n < 2:
        return 0.0

    counts = collections.Counter(alpha_chars)
    numerator = sum(count * (count - 1) for count in counts.values())
    denominator = n * (n - 1)

    ic = numerator / denominator

    logger.debug("Index of coincidence: %.6f (N=%d)", ic, n)
    return ic


def expected_english_frequency() -> dict[str, float]:
    """Return standard English letter frequencies.

    Returns:
        Dictionary mapping each lowercase letter (a-z) to its
        expected frequency as a percentage in standard English text.
        For example, 'e' maps to 12.702.
    """
    return dict(_ENGLISH_FREQUENCIES)
