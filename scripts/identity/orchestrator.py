#!/usr/bin/env python3
"""
Identity Orchestrator Example.

This script demonstrates the usage of the codomyrmex identity module,
including persona management and bio-cognitive verification.
"""

import sys
from codomyrmex.identity import (
    IdentityManager,
    BioCognitiveVerifier,
    VerificationLevel,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

def run_orchestrator():
    print("--- Starting Identity Orchestrator ---")

    # 1. Initialize Managers
    manager = IdentityManager()
    verifier = BioCognitiveVerifier()

    # 2. Create Personas for different tiers
    print("\n[Step 2] Creating personas...")
    p_anon = manager.create_persona("anon-001", "Shadow", VerificationLevel.ANON)
    p_verified = manager.create_persona("verified-001", "Researcher", VerificationLevel.VERIFIED_ANON)
    p_kyc = manager.create_persona("kyc-001", "Alice Smith", VerificationLevel.KYC)

    print(f"Created {len(manager.list_personas())} personas.")

    # 3. Bio-cognitive Enrollment
    print("\n[Step 3] Enrolling bio-cognitive baseline for Alice...")
    # Simulate Alice's keystroke flight time baseline (mean=0.12s, std=0.01)
    baseline_samples = [0.12, 0.11, 0.13, 0.12, 0.12, 0.11, 0.14, 0.12, 0.13, 0.12,
                        0.11, 0.12, 0.12, 0.13, 0.11, 0.12, 0.12, 0.14, 0.12, 0.11]
    for sample in baseline_samples:
        verifier.record_metric(p_kyc.id, "keystroke_flight_time", sample)

    print(f"Baseline confidence: {verifier.get_confidence(p_kyc.id):.2f}")

    # 4. Verification Challenges
    print("\n[Step 4] Verifying identity via behavioral metrics...")

    # A valid attempt
    current_kft = 0.125
    is_valid = verifier.verify(p_kyc.id, "keystroke_flight_time", current_kft)
    print(f"Verification for Alice (KFT={current_kft}): {'SUCCESS' if is_valid else 'FAILED'}")

    # An invalid attempt (outlier)
    attacker_kft = 0.25
    is_valid_attacker = verifier.verify(p_kyc.id, "keystroke_flight_time", attacker_kft)
    print(f"Verification for Alice (KFT={attacker_kft}): {'SUCCESS' if is_valid_attacker else 'FAILED'}")

    # 5. Context Switching
    print("\n[Step 5] Switching active persona context...")
    manager.set_active_persona(p_kyc.id)
    print(f"Active Persona: {manager.active_persona.name} ({manager.active_persona.level.value})")

    # 6. Persona Attributes and Crumbs
    print("\n[Step 6] Updating persona data...")
    manager.active_persona.add_attribute("role", "Lead Scientist")
    manager.active_persona.add_crumb("Accessed secure lab")
    manager.active_persona.add_crumb("Executed simulation-42")

    # 7. Exporting Persona Data
    print("\n[Step 7] Exporting persona...")
    exported = manager.export_persona(p_kyc.id)
    print(f"Exported Persona Data: {exported}")

    # 8. Revocation
    print("\n[Step 8] Revoking anonymized persona...")
    manager.revoke_persona(p_anon.id)
    print(f"Personas remaining: {len(manager.list_personas())}")

    print("\n--- Identity Orchestrator Finished ---")


    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "identity" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/identity/config.yaml")

if __name__ == "__main__":
    try:
        run_orchestrator()
    except Exception as e:
        logger.error(f"Orchestrator failed: {e}")
        sys.exit(1)
