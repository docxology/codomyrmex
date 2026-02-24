# crypto/protocols -- Agent Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Summary

The `crypto/protocols` submodule implements cryptographic protocols: Diffie-Hellman and ECDH key exchange, Shamir's Secret Sharing with verifiable commitments, and zero-knowledge proofs (Schnorr proofs, Pedersen commitments).

## When to Use This Module

- You need to establish a shared secret between two parties without transmitting the secret (DH / ECDH key exchange)
- You need to split a secret into N shares such that K of them can reconstruct it (Shamir's Secret Sharing)
- You need to verify that a secret share is valid without revealing the secret (share commitments)
- You need to prove knowledge of a discrete log without revealing it (Schnorr proofs)
- You need to commit to a value that can be verified later (Pedersen commitments)

## Exports

**Key Exchange:**

| Name | Kind | Purpose |
|------|------|---------|
| `DHKeyPair` | dataclass | Diffie-Hellman key pair container |
| `dh_generate_parameters` | function | Generate DH parameters (p, g) |
| `dh_generate_keypair` | function | Generate DH key pair from parameters |
| `dh_compute_shared_secret` | function | Compute shared secret from DH exchange |
| `ECDHKeyPair` | dataclass | ECDH key pair container |
| `ecdh_generate_keypair` | function | Generate ECDH key pair |
| `ecdh_compute_shared_secret` | function | Compute ECDH shared secret |

**Secret Sharing:**

| Name | Kind | Purpose |
|------|------|---------|
| `Share` | dataclass | Individual share (x, y) |
| `PRIME` | constant | Large prime for secret sharing field |
| `split_secret` | function | Split secret into N shares with threshold K |
| `reconstruct_secret` | function | Reconstruct secret from K+ shares |
| `generate_share_commitment` | function | Generate commitment for share verification |
| `verify_share` | function | Verify a share against its commitment |

**Zero-Knowledge:**

| Name | Kind | Purpose |
|------|------|---------|
| `SchnorrProof` | dataclass | Schnorr proof (commitment, challenge, response) |
| `schnorr_prove` | function | Generate Schnorr proof of discrete log knowledge |
| `schnorr_verify` | function | Verify Schnorr proof |
| `pedersen_commit` | function | Create Pedersen commitment to a value |
| `pedersen_verify` | function | Verify Pedersen commitment |

## Example Agent Usage

```python
from codomyrmex.crypto.protocols import (
    ecdh_generate_keypair, ecdh_compute_shared_secret,
    split_secret, reconstruct_secret,
    schnorr_prove, schnorr_verify,
)

# ECDH key exchange
alice = ecdh_generate_keypair()
bob = ecdh_generate_keypair()
shared_a = ecdh_compute_shared_secret(alice, bob.public_key)
shared_b = ecdh_compute_shared_secret(bob, alice.public_key)
assert shared_a == shared_b

# Secret sharing (3-of-5)
shares = split_secret(secret=42, threshold=3, num_shares=5)
recovered = reconstruct_secret(shares[:3])
assert recovered == 42

# Schnorr ZKP
proof = schnorr_prove(secret=12345)
assert schnorr_verify(proof)
```

## Constraints

- DH parameter generation can be slow for large key sizes; consider caching parameters.
- Secret sharing operates over a finite field defined by `PRIME`; secrets must be smaller.
- Zero-knowledge proofs are non-interactive (Fiat-Shamir heuristic).

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `crypto.graphy` | Asymmetric key pairs and KDF can be used with shared secrets from key exchange |
| `crypto.random` | Nonce and random value generation for proofs |
| `encryption.keys` | `derive_key_hkdf` can derive encryption keys from DH/ECDH shared secrets |
