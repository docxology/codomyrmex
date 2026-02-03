
import pytest
from codomyrmex.identity import IdentityManager, VerificationLevel, BioCognitiveVerifier

def test_persona_creation():
    id_mgr = IdentityManager()
    p_kyc = id_mgr.create_persona("p1", "Alice KYC", VerificationLevel.KYC)
    p_anon = id_mgr.create_persona("p2", "Alice Anon", VerificationLevel.ANON)
    
    assert p_kyc.level == VerificationLevel.KYC
    assert p_anon.level == VerificationLevel.ANON
    assert len(id_mgr.list_personas()) == 2

def test_persona_switching():
    id_mgr = IdentityManager()
    id_mgr.create_persona("p1", "Alice", VerificationLevel.KYC)
    
    assert id_mgr.active_persona is None
    id_mgr.set_active_persona("p1")
    assert id_mgr.active_persona.name == "Alice"
    
    with pytest.raises(ValueError):
        id_mgr.set_active_persona("non_existent")

def test_biocognitive_verification():
    bio = BioCognitiveVerifier()
    user_id = "u1"
    
    # Train baseline
    for _ in range(20):
        bio.record_metric(user_id, "keystroke", 0.15)
        
    # Test valid
    assert bio.verify(user_id, "keystroke", 0.16)
    
    # Test invalid (z-score high)
    assert not bio.verify(user_id, "keystroke", 0.50)
    
    # Test missing baseline
    assert not bio.verify("u2", "keystroke", 0.15)
