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
    # classical
    "CaesarResult",
    # entropy
    "ChiSquaredResult",
    # strength
    "StrengthResult",
    "VigenereResult",
    "assess_key_strength",
    "assess_password_strength",
    # frequency
    "bigram_frequency",
    "break_caesar",
    "break_vigenere",
    "byte_entropy",
    "caesar_decrypt",
    "caesar_encrypt",
    "character_frequency",
    "check_common_passwords",
    "chi_squared_test",
    "detect_cipher_type",
    "estimate_crack_time",
    "expected_english_frequency",
    "index_of_coincidence",
    "serial_correlation",
    "shannon_entropy",
    "vigenere_decrypt",
    "vigenere_encrypt",
]
