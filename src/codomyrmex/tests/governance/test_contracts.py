import pytest
from codomyrmex.governance.contracts import Contract, Party, ContractStatus

def test_contract_lifecycle():
    parties = [
        Party(id="agent-a", name="Agent A", role="Buyer"),
        Party(id="agent-b", name="Agent B", role="Seller")
    ]
    contract = Contract("Service Agreement", "Terms...", parties)
    
    assert contract.status == ContractStatus.DRAFT
    
    contract.sign("agent-a")
    assert contract.status == ContractStatus.DRAFT
    assert len(contract.signatures) == 1
    
    contract.sign("agent-b")
    assert contract.status == ContractStatus.ACTIVE
    assert len(contract.signatures) == 2

def test_invalid_signer():
    contract = Contract("Test", "...", [Party("a", "A", "Role")])
    with pytest.raises(ValueError, match="not a party"):
        contract.sign("outsider")

def test_duplicate_signature():
    contract = Contract("Test", "...", [Party("a", "A", "Role")])
    contract.sign("a")
    with pytest.raises(ValueError, match="already signed"):
        contract.sign("a")
