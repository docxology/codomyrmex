#!/usr/bin/env python3
"""
Encryption utilities for hashing, encrypting, and key generation.

Usage:
    python crypto_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import hashlib
import secrets
import base64


def generate_key(length: int = 32, encoding: str = "hex") -> str:
    """Generate a secure random key."""
    key_bytes = secrets.token_bytes(length)
    if encoding == "hex":
        return key_bytes.hex()
    elif encoding == "base64":
        return base64.b64encode(key_bytes).decode()
    else:
        return key_bytes.hex()


def hash_data(data: str, algorithm: str = "sha256") -> str:
    """Hash data using specified algorithm."""
    algorithms = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
        "blake2b": hashlib.blake2b,
    }
    
    if algorithm not in algorithms:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    return algorithms[algorithm](data.encode()).hexdigest()


def hash_file(file_path: str, algorithm: str = "sha256") -> str:
    """Hash a file."""
    algorithms = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
    }
    
    if algorithm not in algorithms:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    h = algorithms[algorithm]()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def encode_base64(data: str) -> str:
    """Base64 encode a string."""
    return base64.b64encode(data.encode()).decode()


def decode_base64(data: str) -> str:
    """Base64 decode a string."""
    return base64.b64decode(data.encode()).decode()


def main():
    parser = argparse.ArgumentParser(description="Cryptographic utilities")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Generate key command
    gen_parser = subparsers.add_parser("generate-key", help="Generate secure key")
    gen_parser.add_argument("--length", "-l", type=int, default=32, help="Key length in bytes")
    gen_parser.add_argument("--encoding", "-e", choices=["hex", "base64"], default="hex")
    gen_parser.add_argument("--count", "-n", type=int, default=1, help="Number of keys")
    
    # Hash command
    hash_parser = subparsers.add_parser("hash", help="Hash data or file")
    hash_parser.add_argument("input", help="Data to hash or file path with -f")
    hash_parser.add_argument("--algorithm", "-a", default="sha256",
                            choices=["md5", "sha1", "sha256", "sha512", "blake2b"])
    hash_parser.add_argument("--file", "-f", action="store_true", help="Input is a file")
    
    # Base64 command
    b64_parser = subparsers.add_parser("base64", help="Base64 encode/decode")
    b64_parser.add_argument("input", help="Data to encode/decode")
    b64_parser.add_argument("--decode", "-d", action="store_true", help="Decode instead of encode")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🔐 Cryptographic Utilities\n")
        print("Commands:")
        print("  generate-key  Generate secure random keys")
        print("  hash          Hash data or files")
        print("  base64        Base64 encode/decode")
        print("\nExamples:")
        print("  python crypto_utils.py generate-key -l 32")
        print("  python crypto_utils.py hash 'my data' -a sha256")
        print("  python crypto_utils.py hash file.txt -f")
        print("  python crypto_utils.py base64 'hello world'")
        return 0
    
    if args.command == "generate-key":
        print(f"🔑 Generating {args.count} key(s) ({args.length} bytes, {args.encoding}):\n")
        for i in range(args.count):
            key = generate_key(args.length, args.encoding)
            print(f"  {key}")
    
    elif args.command == "hash":
        if args.file:
            if not Path(args.input).exists():
                print(f"❌ File not found: {args.input}")
                return 1
            result = hash_file(args.input, args.algorithm)
            print(f"📄 File: {args.input}")
        else:
            result = hash_data(args.input, args.algorithm)
            print(f"📝 Data: {args.input[:50]}...")
        
        print(f"🔒 {args.algorithm.upper()}: {result}")
    
    elif args.command == "base64":
        if args.decode:
            result = decode_base64(args.input)
            print(f"📥 Decoded: {result}")
        else:
            result = encode_base64(args.input)
            print(f"📤 Encoded: {result}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
