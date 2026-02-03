
import pytest
from codomyrmex.wallet import WalletManager, NaturalRitualRecovery, RitualStep
import hashlib

def test_wallet_creation_and_signing():
    wallet_mgr = WalletManager()
    user_id = "u1"
    
    address = wallet_mgr.create_wallet(user_id)
    assert address.startswith("0x")
    assert wallet_mgr.get_wallet_address(user_id) == address
    
    sig = wallet_mgr.sign_message(user_id, b"message")
    assert len(sig) > 0
    
    with pytest.raises(ValueError):
        wallet_mgr.sign_message("u2", b"message")

def test_natural_ritual_recovery():
    recovery = NaturalRitualRecovery()
    user_id = "u1"
    
    steps = [
        RitualStep("Color?", hashlib.sha256(b"Red").hexdigest()),
        RitualStep("Animal?", hashlib.sha256(b"Cat").hexdigest())
    ]
    recovery.register_ritual(user_id, steps)
    
    # Success
    assert recovery.initiate_recovery(user_id, ["Red", "Cat"])
    
    # Failure
    assert not recovery.initiate_recovery(user_id, ["Blue", "Cat"])
    assert not recovery.initiate_recovery(user_id, ["Red", "Dog"])
    
    # Invalid user
    assert not recovery.initiate_recovery("u2", ["Red", "Cat"])
