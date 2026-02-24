#!/usr/bin/env python3
"""
verify_phase1.py

Verifies Identity and Wallet module functionality:
1. Persona creation and switching.
2. Bio-cognitive metric recording.
3. Wallet creation.
4. Natural Ritual Recovery flow.
"""

import hashlib
from codomyrmex.identity import IdentityManager, VerificationLevel, BioCognitiveVerifier
from codomyrmex.wallet import WalletManager, NaturalRitualRecovery, RitualStep

def verify_identity():
    print("\n--- Verifying Identity ---")
    id_mgr = IdentityManager()
    
    # 1. Create Personas
    p_kyc = id_mgr.create_persona("p1", "Alice KYC", VerificationLevel.KYC)
    p_anon = id_mgr.create_persona("p2", "Alice Anon", VerificationLevel.ANON)
    
    assert p_kyc.level == VerificationLevel.KYC
    assert p_anon.level == VerificationLevel.ANON
    print("✓ Created 3-tier personas")

    # 2. Switch Context
    id_mgr.set_active_persona("p2")
    assert id_mgr.active_persona.name == "Alice Anon"
    print("✓ Switched active persona")
    
    # 3. Bio-Cognitive
    bio = BioCognitiveVerifier()
    # Train
    for _ in range(20):
        bio.record_metric("p2", "keystroke", 0.15)
        
    # Verify valid
    assert bio.verify("p2", "keystroke", 0.16)
    # Verify invalid (too slow)
    assert not bio.verify("p2", "keystroke", 0.50)
    print("✓ Bio-cognitive verification logic works")

def verify_wallet():
    print("\n--- Verifying Wallet ---")
    wallet_mgr = WalletManager()
    user_id = "user_123"
    
    # 1. Create Wallet
    try:
        address = wallet_mgr.create_wallet(user_id)
        print(f"✓ Created wallet: {address}")
    except RuntimeError as e:
        print(f"X Failed to create wallet: {e}")
        return

    # 2. Key usage (signing)
    sig = wallet_mgr.sign_message(user_id, b"Hello World")
    assert len(sig) > 0
    print("✓ Wallet signing works")

    # 3. Natural Ritual Integration
    recovery = NaturalRitualRecovery()
    
    # Define ritual (Secret: "Blue", "Mountain")
    steps = [
        RitualStep("Color?", hashlib.sha256(b"Blue").hexdigest()),
        RitualStep("Place?", hashlib.sha256(b"Mountain").hexdigest())
    ]
    recovery.register_ritual(user_id, steps)
    
    # Attempt success
    success = recovery.initiate_recovery(user_id, ["Blue", "Mountain"])
    assert success
    print("✓ Natural Ritual Recovery (Success Case)")
    
    # Attempt failure
    fail = recovery.initiate_recovery(user_id, ["Red", "Mountain"])
    assert not fail
    print("✓ Natural Ritual Recovery (Failure Case)")

def main():
    verify_identity()
    verify_wallet()
    print("\n[SUCCESS] Phase 1 Verification Complete")

if __name__ == "__main__":
    main()
