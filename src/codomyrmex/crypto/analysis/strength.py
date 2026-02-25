"""Password and cryptographic key strength assessment.

Provides entropy-based password scoring, crack time estimation,
key strength validation against algorithm requirements, and
common password checking.
"""

from __future__ import annotations

import math
import string
from dataclasses import dataclass, field

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Top 100 common passwords (sourced from multiple breach datasets)
_COMMON_PASSWORDS: set[str] = {
    "123456", "password", "12345678", "qwerty", "123456789",
    "12345", "1234", "111111", "1234567", "dragon",
    "123123", "baseball", "abc123", "football", "monkey",
    "letmein", "696969", "shadow", "master", "666666",
    "qwertyuiop", "123321", "mustang", "1234567890", "michael",
    "654321", "pussy", "superman", "1qaz2wsx", "7777777",
    "fuckyou", "121212", "000000", "qazwsx", "123qwe",
    "killer", "trustno1", "jordan", "jennifer", "zxcvbnm",
    "asdfgh", "hunter", "buster", "soccer", "harley",
    "batman", "andrew", "tigger", "sunshine", "iloveyou",
    "fuckme", "charlie", "robert", "thomas", "hockey",
    "ranger", "daniel", "starwars", "klaster", "112233",
    "george", "asshole", "computer", "michelle", "jessica",
    "pepper", "1111", "zxcvbn", "555555", "11111111",
    "131313", "freedom", "777777", "pass", "fuck",
    "maggie", "159753", "aaaaaa", "ginger", "princess",
    "joshua", "cheese", "amanda", "summer", "love",
    "ashley", "6969", "nicole", "chelsea", "biteme",
    "matthew", "access", "yankees", "987654321", "dallas",
    "austin", "thunder", "taylor", "matrix", "admin",
}

# Algorithm key length requirements in bits
_KEY_REQUIREMENTS: dict[str, list[int]] = {
    "aes": [128, 192, 256],
    "aes-128": [128],
    "aes-192": [192],
    "aes-256": [256],
    "des": [56],
    "3des": [112, 168],
    "rsa": [2048, 3072, 4096],
    "ed25519": [256],
    "chacha20": [256],
    "blowfish": [128, 192, 256, 448],
}


@dataclass
class StrengthResult:
    """Result of a password or key strength assessment."""

    score: int  # 0-100
    level: str  # "very_weak", "weak", "fair", "strong", "very_strong"
    feedback: list[str] = field(default_factory=list)
    entropy_bits: float = 0.0


def _calculate_charset_size(password: str) -> int:
    """Determine the effective character set size used in a password."""
    charset = 0
    has_lower = any(c in string.ascii_lowercase for c in password)
    has_upper = any(c in string.ascii_uppercase for c in password)
    has_digit = any(c in string.digits for c in password)
    has_special = any(c in string.punctuation for c in password)
    has_space = " " in password
    has_other = any(
        c not in string.ascii_letters + string.digits + string.punctuation + " "
        for c in password
    )

    if has_lower:
        charset += 26
    if has_upper:
        charset += 26
    if has_digit:
        charset += 10
    if has_special:
        charset += 32
    if has_space:
        charset += 1
    if has_other:
        charset += 64  # approximate for unicode chars

    return max(charset, 1)


def _score_to_level(score: int) -> str:
    """Map a numeric score (0-100) to a strength level string."""
    if score < 20:
        return "very_weak"
    elif score < 40:
        return "weak"
    elif score < 60:
        return "fair"
    elif score < 80:
        return "strong"
    else:
        return "very_strong"


def assess_password_strength(password: str) -> StrengthResult:
    """Assess the strength of a password.

    Evaluates based on entropy (charset size and length), character
    diversity, and common pattern detection. Generates actionable
    feedback.

    Args:
        password: The password to evaluate.

    Returns:
        StrengthResult with score (0-100), level, feedback, and entropy.
    """
    if not password:
        return StrengthResult(
            score=0, level="very_weak",
            feedback=["Password is empty"], entropy_bits=0.0,
        )

    feedback: list[str] = []
    length = len(password)

    # Calculate entropy
    charset_size = _calculate_charset_size(password)
    entropy_bits = length * math.log2(charset_size) if charset_size > 1 else 0.0

    # Start with entropy-based score (entropy of 128 bits = 100)
    score = min(100, int((entropy_bits / 128.0) * 100))

    # Length checks
    if length < 8:
        feedback.append("Password should be at least 8 characters long")
        score = min(score, 30)
    elif length < 12:
        feedback.append("Consider using 12 or more characters for better security")

    # Character diversity checks
    has_lower = any(c in string.ascii_lowercase for c in password)
    has_upper = any(c in string.ascii_uppercase for c in password)
    has_digit = any(c in string.digits for c in password)
    has_special = any(c in string.punctuation for c in password)

    if not has_lower:
        feedback.append("Add lowercase letters")
    if not has_upper:
        feedback.append("Add uppercase letters")
    if not has_digit:
        feedback.append("Add digits")
    if not has_special:
        feedback.append("Add special characters")

    diversity_count = sum([has_lower, has_upper, has_digit, has_special])
    if diversity_count < 2:
        score = max(0, score - 20)

    # Detect sequential characters (abc, 123, etc.)
    sequential_count = 0
    for i in range(len(password) - 2):
        if (
            ord(password[i]) + 1 == ord(password[i + 1])
            and ord(password[i + 1]) + 1 == ord(password[i + 2])
        ):
            sequential_count += 1
    if sequential_count > 0:
        feedback.append("Avoid sequential characters (e.g., abc, 123)")
        score = max(0, score - sequential_count * 5)

    # Detect repeated characters (aaa, 111)
    repeat_count = 0
    for i in range(len(password) - 2):
        if password[i] == password[i + 1] == password[i + 2]:
            repeat_count += 1
    if repeat_count > 0:
        feedback.append("Avoid repeated characters (e.g., aaa, 111)")
        score = max(0, score - repeat_count * 5)

    # Check common passwords
    if check_common_passwords(password):
        feedback.append("This is a commonly used password")
        score = min(score, 5)

    # Clamp score
    score = max(0, min(100, score))

    level = _score_to_level(score)

    logger.debug(
        "Password strength: score=%d, level=%s, entropy=%.1f bits",
        score, level, entropy_bits,
    )
    return StrengthResult(
        score=score, level=level, feedback=feedback, entropy_bits=entropy_bits,
    )


def estimate_crack_time(
    password: str, guesses_per_second: float = 1e10,
) -> float:
    """Estimate time in seconds to brute-force crack a password.

    Uses the formula: 2^entropy_bits / guesses_per_second.

    Args:
        password: The password to evaluate.
        guesses_per_second: Attack speed in guesses per second.
            Defaults to 10 billion (modern GPU cluster).

    Returns:
        Estimated seconds to exhaust the keyspace.
    """
    if not password or guesses_per_second <= 0:
        return 0.0

    charset_size = _calculate_charset_size(password)
    entropy_bits = len(password) * math.log2(charset_size) if charset_size > 1 else 0.0

    if entropy_bits == 0:
        return 0.0

    # 2^entropy / guesses_per_second
    # Use log to avoid overflow for large entropy values
    log_seconds = entropy_bits * math.log(2) - math.log(guesses_per_second)

    if log_seconds > 700:
        return float("inf")

    seconds = math.exp(log_seconds)

    logger.debug(
        "Crack time estimate: %.2e seconds (%.1f entropy bits, %.2e guesses/s)",
        seconds, entropy_bits, guesses_per_second,
    )
    return seconds


def assess_key_strength(key: bytes, algorithm: str) -> StrengthResult:
    """Assess the strength of a cryptographic key for a given algorithm.

    Validates key length against known requirements for common
    cryptographic algorithms.

    Args:
        key: The cryptographic key bytes.
        algorithm: Algorithm name (e.g., 'aes', 'aes-256', 'rsa').

    Returns:
        StrengthResult with assessment based on key length and
        algorithm requirements.
    """
    feedback: list[str] = []
    key_bits = len(key) * 8

    algo_lower = algorithm.lower().strip()
    required = _KEY_REQUIREMENTS.get(algo_lower)

    # Calculate entropy of the key bytes themselves
    from codomyrmex.crypto.analysis.entropy import byte_entropy

    entropy = byte_entropy(key) if key else 0.0

    if required is None:
        # Unknown algorithm -- assess based on key length alone
        feedback.append(f"Unknown algorithm '{algorithm}'; assessing key length only")
        if key_bits >= 256:
            score = 90
        elif key_bits >= 128:
            score = 70
        elif key_bits >= 64:
            score = 40
        else:
            score = 10
            feedback.append("Key is very short")
    else:
        min_required = min(required)
        max_required = max(required)

        if key_bits in required:
            score = 85
            feedback.append(f"Key length {key_bits} bits is valid for {algorithm}")
        elif key_bits >= max_required:
            score = 90
            feedback.append(f"Key length {key_bits} bits exceeds requirements for {algorithm}")
        elif key_bits >= min_required:
            score = 70
            feedback.append(
                f"Key length {key_bits} bits meets minimum for {algorithm} "
                f"but consider {max_required} bits"
            )
        else:
            score = 20
            feedback.append(
                f"Key length {key_bits} bits is below minimum {min_required} "
                f"bits required for {algorithm}"
            )

    # Penalize low-entropy keys (e.g., all zeros)
    if key and entropy < 4.0:
        feedback.append("Key has low byte entropy; consider using a cryptographic RNG")
        score = max(0, score - 20)

    score = max(0, min(100, score))
    level = _score_to_level(score)

    logger.debug(
        "Key strength for %s: score=%d, level=%s, %d bits, entropy=%.2f",
        algorithm, score, level, key_bits, entropy,
    )
    return StrengthResult(
        score=score, level=level, feedback=feedback, entropy_bits=float(key_bits),
    )


def check_common_passwords(password: str) -> bool:
    """Check if a password is in the list of top 100 common passwords.

    Case-insensitive comparison.

    Args:
        password: The password to check.

    Returns:
        True if the password is found in the common passwords list.
    """
    return password.lower() in _COMMON_PASSWORDS
