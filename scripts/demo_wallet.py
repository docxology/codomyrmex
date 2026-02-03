#!/usr/bin/env python3
"""
scripts/demo_wallet.py

Demonstrates:
1. Self-Custody of keys.
2. Natural Ritual Recovery (ZKP-like knowledge proof).
3. Key Rotation.
"""

import sys
from pathlib import Path
import hashlib

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from codomyrmex.wallet import WalletManager, NaturalRitualRecovery, RitualStep
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger("demo_wallet")

def demo_self_custody():
    print("\n--- 1. Self-Custody Wallet ---")
    wallet_mgr = WalletManager()
    user_id = "user_main"

    # Create Wallet
    address = wallet_mgr.create_wallet(user_id)
    print(f"Wallet Created: {address}")
    
    # Sign Transaction
    msg = b"Transfer 100 units"
    sig = wallet_mgr.sign_message(user_id, msg)
    print(f"Signed Message: '{msg.decode()}'")
    print(f"Signature: {sig.hex()[:16]}...")

    # Key Rotation
    print("\nExecuting Key Rotation...")
    new_address = wallet_mgr.rotate_keys(user_id)
    print(f"New Wallet Address: {new_address}")

def demo_recovery():
    print("\n--- 2. Natural Ritual Recovery ---")
    recovery = NaturalRitualRecovery()
    user_id = "user_main"

    print("Setting up 'Natural Ritual' (Secret Experience)...")
    # The ritual is a sequence of answers known only to the user
    # "Where did it rain on our wedding?" -> Paris
    # "What was the name of the stray dog?" -> Barnaby
    
    rituals = [
        RitualStep("Location?", hashlib.sha256(b"Paris").hexdigest()),
        RitualStep("Dog Name?", hashlib.sha256(b"Barnaby").hexdigest())
    ]
    recovery.register_ritual(user_id, rituals)
    print("Ritual registered encrypted on-chain (simulated).")

    # Attempt Recovery - Success
    print("\nAttempting Recovery (Correct Answers)...")
    proofs = ["Paris", "Barnaby"]
    if recovery.initiate_recovery(user_id, proofs):
        print("✅ RECOVERY SUCCESSFUL: Wallet access restored.")
    else:
        print("❌ RECOVERY FAILED.")

    # Attempt Recovery - Failure
    print("\nAttempting Recovery (Wrong Answers)...")
    bad_proofs = ["London", "Barnaby"]
    if recovery.initiate_recovery(user_id, bad_proofs):
        print("✅ RECOVERY SUCCESSFUL.")
    else:
        print("❌ RECOVERY FAILED: Ritual mismatch. Access denied.")

def main():
    print("=== Secure Cognitive Agent: Wallet Demo ===")
    demo_self_custody()
    demo_recovery()
    print("\n[SUCCESS] Wallet Demo Complete")

if __name__ == "__main__":
    main()
