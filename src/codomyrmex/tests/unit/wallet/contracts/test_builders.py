import pytest

from codomyrmex.wallet.contracts.builders import (
    BASE_GAS,
    CONTRACT_CREATION_GAS,
    DATA_GAS_PER_BYTE,
    DATA_GAS_PER_ZERO_BYTE,
    estimate_gas,
)


@pytest.mark.parametrize(
    ("data", "is_contract_creation", "expected_gas"),
    [
        # Empty data
        ("", False, BASE_GAS),
        ("", True, CONTRACT_CREATION_GAS),
        (None, False, BASE_GAS),  # Even if type hint says str, handling not data
        # Valid hex with zeros
        ("00000000", False, BASE_GAS + 4 * DATA_GAS_PER_ZERO_BYTE),
        # Valid hex with non-zeros
        ("01020304", False, BASE_GAS + 4 * DATA_GAS_PER_BYTE),
        # Mixed zeros and non-zeros
        (
            "01000300",
            False,
            BASE_GAS + 2 * DATA_GAS_PER_BYTE + 2 * DATA_GAS_PER_ZERO_BYTE,
        ),
        # With 0x prefix
        ("0x01020304", False, BASE_GAS + 4 * DATA_GAS_PER_BYTE),
        ("0x0000", False, BASE_GAS + 2 * DATA_GAS_PER_ZERO_BYTE),
        # Odd-length hex (treated as empty)
        ("012", False, BASE_GAS),
        ("0x012", False, BASE_GAS),
        ("0", False, BASE_GAS),
        # Contract creation with data
        ("0x00", True, CONTRACT_CREATION_GAS + DATA_GAS_PER_ZERO_BYTE),
        ("0x01", True, CONTRACT_CREATION_GAS + DATA_GAS_PER_BYTE),
        (
            "0100",
            True,
            CONTRACT_CREATION_GAS + DATA_GAS_PER_BYTE + DATA_GAS_PER_ZERO_BYTE,
        ),
    ],
)
def test_estimate_gas(data: str, is_contract_creation: bool, expected_gas: int):
    """Test gas estimation with various inputs."""
    assert estimate_gas(data, is_contract_creation) == expected_gas
