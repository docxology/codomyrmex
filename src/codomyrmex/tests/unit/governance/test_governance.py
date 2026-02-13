"""Tests for the governance module.

Tests cover:
- Module import
- ContractStatus enum values
- Party creation
- Contract construction
- Contract signing by valid party
- Contract auto-activates when all sign
- Contract sign rejects non-party
- Contract sign rejects duplicate signature
- Contract sign rejects non-DRAFT status
- Contract termination
"""

import pytest

from codomyrmex.governance.contracts import (
    Contract,
    ContractStatus,
    Party,
    Signature,
)


@pytest.mark.unit
def test_module_import():
    """governance module is importable."""
    from codomyrmex import governance
    assert governance is not None


@pytest.mark.unit
def test_contract_status_enum():
    """ContractStatus has expected members."""
    assert ContractStatus.DRAFT.name == "DRAFT"
    assert ContractStatus.ACTIVE.name == "ACTIVE"
    assert ContractStatus.TERMINATED.name == "TERMINATED"
    assert ContractStatus.DISPUTED.name == "DISPUTED"


@pytest.mark.unit
def test_party_creation():
    """Party dataclass stores id, name, and role."""
    party = Party(id="p1", name="Alice", role="buyer")
    assert party.id == "p1"
    assert party.name == "Alice"
    assert party.role == "buyer"


@pytest.mark.unit
def test_contract_construction():
    """Contract is created in DRAFT status with UUID."""
    parties = [Party(id="a", name="Alice", role="buyer")]
    contract = Contract(title="Sale Agreement", text="Terms here", parties=parties)
    assert contract.title == "Sale Agreement"
    assert contract.text == "Terms here"
    assert contract.status == ContractStatus.DRAFT
    assert contract.id is not None
    assert contract.signatures == []


@pytest.mark.unit
def test_contract_sign_valid_party():
    """Valid party can sign a DRAFT contract."""
    parties = [
        Party(id="a", name="Alice", role="buyer"),
        Party(id="b", name="Bob", role="seller"),
    ]
    contract = Contract(title="Deal", text="Terms", parties=parties)
    contract.sign("a")
    assert len(contract.signatures) == 1
    assert contract.signatures[0].signer_id == "a"
    assert contract.status == ContractStatus.DRAFT


@pytest.mark.unit
def test_contract_auto_activates_on_all_signatures():
    """Contract auto-activates when all parties have signed."""
    parties = [
        Party(id="a", name="Alice", role="buyer"),
        Party(id="b", name="Bob", role="seller"),
    ]
    contract = Contract(title="Deal", text="Terms", parties=parties)
    contract.sign("a")
    contract.sign("b")
    assert contract.status == ContractStatus.ACTIVE


@pytest.mark.unit
def test_contract_sign_rejects_non_party():
    """Signing by a non-party raises ValueError."""
    parties = [Party(id="a", name="Alice", role="buyer")]
    contract = Contract(title="Deal", text="Terms", parties=parties)
    with pytest.raises(ValueError, match="not a party"):
        contract.sign("unknown_id")


@pytest.mark.unit
def test_contract_sign_rejects_duplicate():
    """Same party cannot sign twice."""
    parties = [
        Party(id="a", name="Alice", role="buyer"),
        Party(id="b", name="Bob", role="seller"),
    ]
    contract = Contract(title="Deal", text="Terms", parties=parties)
    contract.sign("a")
    with pytest.raises(ValueError, match="already signed"):
        contract.sign("a")


@pytest.mark.unit
def test_contract_sign_rejects_non_draft():
    """Signing a non-DRAFT contract raises ValueError."""
    parties = [Party(id="a", name="Alice", role="buyer")]
    contract = Contract(title="Deal", text="Terms", parties=parties)
    contract.sign("a")  # Auto-activates (single party)
    assert contract.status == ContractStatus.ACTIVE
    with pytest.raises(ValueError, match="DRAFT"):
        contract.sign("a")


@pytest.mark.unit
def test_contract_terminate():
    """Contract.terminate sets status to TERMINATED."""
    parties = [Party(id="a", name="Alice", role="buyer")]
    contract = Contract(title="Deal", text="Terms", parties=parties)
    contract.terminate()
    assert contract.status == ContractStatus.TERMINATED


@pytest.mark.unit
def test_contract_repr():
    """Contract repr includes title and status."""
    parties = [Party(id="a", name="Alice", role="buyer")]
    contract = Contract(title="Test Contract", text="Body", parties=parties)
    r = repr(contract)
    assert "Test Contract" in r
    assert "DRAFT" in r
