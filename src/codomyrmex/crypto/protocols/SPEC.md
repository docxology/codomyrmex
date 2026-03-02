# Crypto Protocols -- Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Cryptographic protocol implementations covering key exchange (Diffie-Hellman, ECDH), secret sharing (Shamir's Secret Sharing with commitments), and zero-knowledge proofs (Schnorr, Pedersen commitments).

## Architecture

```
crypto/protocols/
├── __init__.py          # 16 re-exports across 3 submodules
├── key_exchange.py      # DH and ECDH key agreement
├── secret_sharing.py    # Shamir's Secret Sharing with verification
└── zero_knowledge.py    # Schnorr proofs, Pedersen commitments
```

## Key Classes and Functions

### key_exchange.py

| Name | Kind | Description |
|------|------|-------------|
| `DHKeyPair` | dataclass | Diffie-Hellman key pair (private value, public value, parameters) |
| `ECDHKeyPair` | dataclass | ECDH key pair (private key, public key, curve name) |
| `dh_generate_parameters` | function | Generate DH group parameters (prime, generator) |
| `dh_generate_keypair` | function | Generate a DH key pair from parameters |
| `dh_compute_shared_secret` | function | Compute shared secret from own private key and peer public key |
| `ecdh_generate_keypair` | function | Generate an ECDH key pair on a named curve |
| `ecdh_compute_shared_secret` | function | Compute ECDH shared secret |

### secret_sharing.py

| Name | Kind | Description |
|------|------|-------------|
| `Share` | dataclass | A single share (index, value) in Shamir's scheme |
| `PRIME` | constant | The prime modulus used for finite field arithmetic |
| `split_secret` | function | Split a secret into N shares with threshold K |
| `reconstruct_secret` | function | Reconstruct the secret from K or more shares |
| `generate_share_commitment` | function | Generate a commitment for share verification |
| `verify_share` | function | Verify a share against its commitment |

### zero_knowledge.py

| Name | Kind | Description |
|------|------|-------------|
| `SchnorrProof` | dataclass | Schnorr proof tuple (commitment, challenge, response) |
| `schnorr_prove` | function | Generate a Schnorr proof of knowledge of a discrete log |
| `schnorr_verify` | function | Verify a Schnorr proof |
| `pedersen_commit` | function | Create a Pedersen commitment to a value |
| `pedersen_verify` | function | Verify a Pedersen commitment |

## Dependencies

- Python `secrets`, `hashlib` (standard library)
- `cryptography` library (for ECDH curve operations)

## Constraints

- Shamir threshold K must satisfy 2 <= K <= N.
- DH parameter generation uses safe primes; minimum 2048-bit modulus.
- Schnorr proofs operate over a prime-order subgroup.

## Error Handling

| Error | When |
|-------|------|
| `ValueError` | Invalid threshold (K > N or K < 2), insufficient shares for reconstruction |
| `TypeError` | Wrong key type passed to shared secret computation |

## Navigation

- **Parent**: [crypto/SPEC.md](../SPEC.md)
- **Siblings**: [AGENTS.md](AGENTS.md), [README.md](README.md), [PAI.md](PAI.md)
