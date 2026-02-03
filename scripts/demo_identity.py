#!/usr/bin/env python3
"""
scripts/demo_identity.py

Demonstrates:
1. Pseudonymity with 3-tier personas (KYC, Verified Anon, Anon).
2. Behavior-bio-cognitive verification (keystroke dynamics).
"""

import sys
from pathlib import Path
import random
import time

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from codomyrmex.identity import IdentityManager, VerificationLevel, BioCognitiveVerifier
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger("demo_identity")

def demo_personas():
    print("\n--- 1. Multi-Persona Management ---")
    id_mgr = IdentityManager()

    # Create 3 tiers of personas
    print("Creating 3 distinct personas...")
    
    # 1. KYC Persona (High Trust)
    p_kyc = id_mgr.create_persona(
        id="persona_kyc", 
        name="Alice RealName (KYC)", 
        level=VerificationLevel.KYC
    )
    print(f"Created: {p_kyc.name} [{p_kyc.level.name}]")

    # 2. Verified Anon (Medium Trust - e.g. for reputation)
    p_anon_v = id_mgr.create_persona(
        id="persona_anon_v", 
        name="Reputable Anon", 
        level=VerificationLevel.VERIFIED_ANON
    )
    print(f"Created: {p_anon_v.name} [{p_anon_v.level.name}]")

    # 3. Anon (Low Trust - Burner)
    p_anon = id_mgr.create_persona(
        id="persona_anon", 
        name="Ghost User", 
        level=VerificationLevel.ANON
    )
    print(f"Created: {p_anon.name} [{p_anon.level.name}]")

    # Switch Context
    print("\nSwitching Contexts:")
    id_mgr.set_active_persona("persona_anon")
    print(f"Active: {id_mgr.active_persona.name}")
    
    id_mgr.set_active_persona("persona_kyc")
    print(f"Active: {id_mgr.active_persona.name}")

def demo_verification():
    print("\n--- 2. Bio-Cognitive Verification ---")
    verifier = BioCognitiveVerifier()
    user_id = "user_123"
    metric = "keystroke_latency"

    print("Training baseline behavior model...")
    # Simulate training with normal behavior (mean=0.15s, std=0.02)
    for _ in range(20):
        val = random.gauss(0.15, 0.02)
        verifier.record_metric(user_id, metric, val)
    
    print("Baseline established.")

    # Test Valid Access
    val_valid = 0.16
    print(f"Verifying input ({val_valid}s)...")
    if verifier.verify(user_id, metric, val_valid):
        print("✅ ACCESS GRANTED: Behavior matches baseline.")
    else:
        print("❌ ACCESS DENIED.")

    # Test Invalid Access (Anomaly)
    val_bot = 0.05 # Too fast (bot-like)
    print(f"Verifying input ({val_bot}s)...")
    if verifier.verify(user_id, metric, val_bot):
         print("✅ ACCESS GRANTED.")
    else:
         print("❌ ACCESS DENIED: Anomaly detected (Bio-Cognitive Mismatch).")

def main():
    print("=== Secure Cognitive Agent: Identity Demo ===")
    demo_personas()
    demo_verification()
    print("\n[SUCCESS] Identity Demo Complete")

if __name__ == "__main__":
    main()
