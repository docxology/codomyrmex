"""Cryptanalysis: entropy, frequency analysis, strength assessment, classical cipher breaking."""

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
from codomyrmex.crypto.analysis.entropy import (
    ChiSquaredResult,
    byte_entropy,
    chi_squared_test,
    serial_correlation,
    shannon_entropy,
)
from codomyrmex.crypto.analysis.frequency import (
    bigram_frequency,
    character_frequency,
    expected_english_frequency,
    index_of_coincidence,
)
from codomyrmex.crypto.analysis.strength import (
    StrengthResult,
    assess_key_strength,
    assess_password_strength,
    check_common_passwords,
    estimate_crack_time,
)

__all__ = [
    # entropy
    "ChiSquaredResult",
    "byte_entropy",
    "chi_squared_test",
    "serial_correlation",
    "shannon_entropy",
    # frequency
    "bigram_frequency",
    "character_frequency",
    "expected_english_frequency",
    "index_of_coincidence",
    # strength
    "StrengthResult",
    "assess_key_strength",
    "assess_password_strength",
    "check_common_passwords",
    "estimate_crack_time",
    # classical
    "CaesarResult",
    "VigenereResult",
    "break_caesar",
    "break_vigenere",
    "caesar_decrypt",
    "caesar_encrypt",
    "detect_cipher_type",
    "vigenere_decrypt",
    "vigenere_encrypt",
]
