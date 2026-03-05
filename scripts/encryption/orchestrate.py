#!/usr/bin/env python3
"""
Encryption - Orchestrated Usage Example

Demonstrates actual encryption capabilities in an orchestrated manner:
- AES-GCM (authenticated encryption)
- RSA key generation and encryption
- HMAC-based JSON signing
- Key management (storing/retrieving/rotating)
- File encryption utilities
- Secure hashing functions
"""

import sys
import tempfile
import warnings
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.encryption import (
    AESGCMEncryptor,
    EncryptionError,
    Encryptor,
    KeyManager,
    Signer,
    decrypt_file,
    encrypt_file,
    generate_key,
    hash_data,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_section,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "encryption"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    setup_logging()
    print_section("Encryption Module Orchestrator Example")

    # 1. AES-GCM (Authenticated Encryption)
    print_info("Testing AES-GCM authenticated encryption (recommended)...")
    try:
        data = b"Highly sensitive secret data"
        key = generate_key(algorithm="AES")
        gcm = AESGCMEncryptor(key)

        # AAD (Additional Authenticated Data)
        aad = b"context-v1"
        ciphertext = gcm.encrypt(data, associated_data=aad)
        print_success("  AES-GCM encryption successful.")

        decrypted = gcm.decrypt(ciphertext, associated_data=aad)
        if decrypted == data:
            print_success("  AES-GCM decryption successful (Data matches).")

        # Tampering detection
        tampered = bytearray(ciphertext)
        tampered[-1] ^= 0xFF
        try:
            gcm.decrypt(bytes(tampered), associated_data=aad)
            print_error("  FAILED: AES-GCM failed to detect tampering!")
        except EncryptionError:
            print_success("  AES-GCM correctly detected tampering.")
    except Exception as e:
        print_error(f"  AES-GCM operations failed: {e}")

    # 2. RSA (Asymmetric Encryption)
    print_info("Testing RSA asymmetric encryption...")
    try:
        rsa_enc = Encryptor(algorithm="RSA")
        priv, pub = rsa_enc.generate_key_pair(2048)

        plaintext = b"RSA Secret Message"
        ciphertext = rsa_enc.encrypt(plaintext, pub)
        print_success("  RSA encryption successful.")

        decrypted = rsa_enc.decrypt(ciphertext, priv)
        if decrypted == plaintext:
            print_success("  RSA decryption successful.")
    except Exception as e:
        print_error(f"  RSA operations failed: {e}")

    # 3. HMAC Signer (Integrity & Authenticity)
    print_info("Testing Signer (HMAC)...")
    try:
        signer = Signer("my-shared-secret")
        obj = {"action": "deploy", "version": "1.2.3"}
        signed_obj = signer.sign_json(obj)
        print_success("  JSON object signed.")

        if signer.verify_json(signed_obj):
            print_success("  JSON signature verified.")

        signed_obj["action"] = "malicious-deploy"
        if not signer.verify_json(signed_obj):
            print_success("  JSON tampering detected.")
        else:
            print_error("  FAILED: Signer failed to detect tampering!")
    except Exception as e:
        print_error(f"  Signer failed: {e}")

    # 4. Key Management & Rotation
    print_info("Testing KeyManager & Rotation...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = KeyManager(key_dir=Path(tmpdir))
            key_id = "master_vault_key"

            old_key = generate_key("AES")
            mgr.store_key(key_id, old_key)
            print_success(f"  Stored key '{key_id}'.")

            # Rotate
            new_key = generate_key("AES")
            returned_old = mgr.rotate_key(key_id, new_key)
            if returned_old == old_key and mgr.get_key(key_id) == new_key:
                print_success(f"  Key rotation successful for '{key_id}'.")
    except Exception as e:
        print_error(f"  KeyManager failed: {e}")

    # 5. File Encryption Utilities
    print_info("Testing file encryption...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            key = generate_key("AES")

            input_file = test_dir / "secret.txt"
            input_file.write_text("This is a secret file content.")

            enc_file = test_dir / "secret.enc"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                if encrypt_file(input_file, enc_file, key):
                    print_success("  File encrypted via AES-CBC (legacy).")

                dec_file = test_dir / "secret.dec.txt"
                if decrypt_file(enc_file, dec_file, key):
                    print_success("  File decrypted.")
                    if dec_file.read_text() == "This is a secret file content.":
                        print_success("  Decrypted content matches original.")
    except Exception as e:
        print_error(f"  File encryption failed: {e}")

    # 6. Hashing
    print_info("Testing SHA-256 Hashing...")
    try:
        h = hash_data(b"hello world", algorithm="sha256")
        print_success(f"  SHA-256: {h}")
    except Exception as e:
        print_error(f"  Hashing failed: {e}")

    print_section("Encryption Module Orchestrator Example - COMPLETED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
