import pytest
from codomyrmex.security.governance.contracts import Contract, ContractStatus, ContractError


def test_contract_lifecycle():
    """Test functionality: contract lifecycle."""
    contract = Contract("Service Agreement", ["Agent A", "Agent B"])

    assert contract.status == ContractStatus.DRAFT

    contract.sign("Agent A")
    assert contract.status == ContractStatus.DRAFT
    assert len(contract.signatures) == 1

    contract.sign("Agent B")
    assert contract.status == ContractStatus.ACTIVE
    assert len(contract.signatures) == 2


def test_invalid_signer():
    """Test functionality: invalid signer."""
    contract = Contract("Test", ["A", "B"])
    with pytest.raises(ContractError):
        contract.sign("outsider")


def test_duplicate_signature():
    """Test functionality: duplicate signature."""
    contract = Contract("Test", ["A", "B"])
    contract.sign("A")
    with pytest.raises(ContractError):
        contract.sign("A")
