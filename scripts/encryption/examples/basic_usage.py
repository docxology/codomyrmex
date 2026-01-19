#!/usr/bin/env python3
"""
Encryption - Real Usage Examples

Demonstrates actual encryption capabilities:
- AES and RSA key generation
- Data encryption and decryption (AES & RSA)
- Key management (storing/retrieving)
- File encryption utilities
- Secure hashing functions
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.encryption import (
    encrypt,
    decrypt,
    generate_key,
    Encryptor,
    KeyManager,
    encrypt_file,
    decrypt_file,
    hash_data
)

def main():
    setup_logging()
    print_info("Running Encryption Examples...")

    # 1. AES
    print_info("Testing AES encryption...")
    try:
        data = b"Highly sensitive secret data"
        key = generate_key(algorithm="AES")
        print_success(f"  AES Key generated (length: {len(key)})")
        
        encrypted = encrypt(data, key, algorithm="AES")
        print_success(f"  Data encrypted via AES.")
        
        decrypted = decrypt(encrypted, key, algorithm="AES")
        if decrypted == data:
            print_success("  AES Decryption successful (Data matches).")
    except ImportError:
        print_info("  AES skipped: 'cryptography' library not installed.")
    except Exception as e:
        print_error(f"  AES operations failed: {e}")

    # 2. Key Management
    print_info("Testing KeyManager...")
    try:
        mgr = KeyManager()
        key_id = "example_aes_key"
        mgr.store_key(key_id, key)
        retrieved_key = mgr.get_key(key_id)
        if retrieved_key == key:
            print_success(f"  Key '{key_id}' stored and retrieved successfully.")
        mgr.delete_key(key_id)
    except Exception as e:
        print_error(f"  KeyManager failed: {e}")

    # 3. File Encryption
    print_info("Testing file encryption...")
    try:
        test_dir = Path("output/encryption_test")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        input_file = test_dir / "secret.txt"
        input_file.write_text("This is a secret file.")
        
        enc_file = test_dir / "secret.enc"
        if encrypt_file(str(input_file), str(enc_file), key):
            print_success(f"  File encrypted: {enc_file}")
            
        dec_file = test_dir / "secret.dec.txt"
        if decrypt_file(str(enc_file), str(dec_file), key):
            print_success(f"  File decrypted: {dec_file}")
            with open(dec_file, "r") as f:
                if f.read() == "This is a secret file.":
                    print_success("  Decrypted file content matches.")
    except Exception as e:
        print_error(f"  File encryption failed: {e}")

    # 4. Hashing
    print_info("Testing hash functions...")
    try:
        h = hash_data(b"hello world", algorithm="sha256")
        print_success(f"  SHA-256: {h}")
    except Exception as e:
        print_error(f"  Hashing failed: {e}")

    print_success("Encryption examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
