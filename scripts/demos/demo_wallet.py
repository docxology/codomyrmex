#!/usr/bin/env python3
"""
scripts/demo_wallet.py

Demonstrates:
1. Self-Custody of keys.
2. Natural Ritual Recovery (ZKP-like knowledge proof).
3. Key Rotation.
"""

import hashlib
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)
from codomyrmex.wallet import NaturalRitualRecovery, RitualStep, WalletManager


def demo_self_custody():
    print_info("--- 1. Self-Custody Wallet ---")
    wallet_mgr = WalletManager()
    user_id = "user_main"

    # Create Wallet
    address = wallet_mgr.create_wallet(user_id)
    print_info(f"Wallet Created: {address}")

    # Sign Transaction
    msg = b"Transfer 100 units"
    sig = wallet_mgr.sign_message(user_id, msg)
    print_info(f"Signed Message: '{msg.decode()}'")
    print_info(f"Signature: {sig.hex()[:16]}...")

    # Key Rotation
    print_info("Executing Key Rotation...")
    new_address = wallet_mgr.rotate_keys(user_id)
    print_info(f"New Wallet Address: {new_address}")


def demo_recovery():
    print_info("--- 2. Natural Ritual Recovery ---")
    recovery = NaturalRitualRecovery()
    user_id = "user_main"

    print_info("Setting up 'Natural Ritual' (Secret Experience)...")
    # The ritual is a sequence of answers known only to the user
    rituals = [
        RitualStep("Location?", hashlib.sha256(b"Paris").hexdigest()),
        RitualStep("Dog Name?", hashlib.sha256(b"Barnaby").hexdigest())
    ]
    recovery.register_ritual(user_id, rituals)
    print_info("Ritual registered encrypted on-chain (simulated).")

    # Attempt Recovery - Success
    print_info("Attempting Recovery (Correct Answers)...")
    proofs = ["Paris", "Barnaby"]
    if recovery.initiate_recovery(user_id, proofs):
        print_success("RECOVERY SUCCESSFUL: Wallet access restored.")
    else:
        print_error("RECOVERY FAILED.")

    # Attempt Recovery - Failure
    print_info("Attempting Recovery (Wrong Answers)...")
    bad_proofs = ["London", "Barnaby"]
    if recovery.initiate_recovery(user_id, bad_proofs):
        print_success("RECOVERY SUCCESSFUL.")
    else:
        print_error("RECOVERY FAILED: Ritual mismatch. Access denied.")


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "demos" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    setup_logging()
    print_info("=== Secure Cognitive Agent: Wallet Demo ===")
    demo_self_custody()
    demo_recovery()
    print_success("Wallet Demo Complete")


if __name__ == "__main__":
    main()
