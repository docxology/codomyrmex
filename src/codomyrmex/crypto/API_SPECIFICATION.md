# Crypto Module — API Specification

**Version**: v0.1.0 | **Last Updated**: February 2026

## Module Entry Point

```python
import codomyrmex.crypto

codomyrmex.crypto.__version__  # "0.1.0"
codomyrmex.crypto.cli_commands()  # Returns dict of CLI command handlers
```

---

## graphy — Cryptography Primitives

### graphy.symmetric

```python
encrypt_aes_gcm(plaintext: bytes, key: bytes, aad: bytes | None = None) -> tuple[bytes, bytes, bytes]
    """AES-256-GCM encryption. Returns (ciphertext, nonce, tag)."""

decrypt_aes_gcm(ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes, aad: bytes | None = None) -> bytes
    """AES-256-GCM decryption. Returns plaintext."""

encrypt_chacha20(plaintext: bytes, key: bytes, aad: bytes | None = None) -> tuple[bytes, bytes, bytes]
    """ChaCha20-Poly1305 encryption. Returns (ciphertext, nonce, tag)."""

decrypt_chacha20(ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes, aad: bytes | None = None) -> bytes
    """ChaCha20-Poly1305 decryption. Returns plaintext."""
```

### graphy.asymmetric

```python
generate_rsa_keypair(key_size: int = 4096) -> tuple[RSAPrivateKey, RSAPublicKey]
    """Generate RSA keypair."""

rsa_encrypt(plaintext: bytes, public_key: RSAPublicKey) -> bytes
    """RSA-OAEP encryption."""

rsa_decrypt(ciphertext: bytes, private_key: RSAPrivateKey) -> bytes
    """RSA-OAEP decryption."""

generate_ed25519_keypair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]
    """Generate Ed25519 keypair."""

generate_x25519_keypair() -> tuple[X25519PrivateKey, X25519PublicKey]
    """Generate X25519 keypair for key exchange."""

generate_ec_keypair(curve: str = "secp256r1") -> tuple[EllipticCurvePrivateKey, EllipticCurvePublicKey]
    """Generate elliptic curve keypair."""

serialize_private_key(key: PrivateKey, password: bytes | None = None) -> bytes
    """Serialize private key to PEM format."""

serialize_public_key(key: PublicKey) -> bytes
    """Serialize public key to PEM format."""

deserialize_private_key(pem_data: bytes, password: bytes | None = None) -> PrivateKey
    """Deserialize private key from PEM format."""

deserialize_public_key(pem_data: bytes) -> PublicKey
    """Deserialize public key from PEM format."""
```

### graphy.hashing

```python
hash_data(data: bytes, algorithm: str = "sha256") -> str
    """Hash data with specified algorithm. Returns hex digest.
    Supported: sha256, sha3_256, sha512, blake2b, md5 (deprecated)."""

hash_file(filepath: str, algorithm: str = "sha256") -> str
    """Hash file contents. Returns hex digest."""

verify_hash(data: bytes, expected_hash: str, algorithm: str = "sha256") -> bool
    """Verify data matches expected hash."""
```

### graphy.signatures

```python
sign_ecdsa(data: bytes, private_key: EllipticCurvePrivateKey, hash_algo: str = "sha256") -> bytes
    """ECDSA digital signature."""

verify_ecdsa(data: bytes, signature: bytes, public_key: EllipticCurvePublicKey, hash_algo: str = "sha256") -> bool
    """Verify ECDSA signature."""

sign_eddsa(data: bytes, private_key: Ed25519PrivateKey) -> bytes
    """EdDSA (Ed25519) digital signature."""

verify_eddsa(data: bytes, signature: bytes, public_key: Ed25519PublicKey) -> bool
    """Verify EdDSA signature."""

sign_rsa_pss(data: bytes, private_key: RSAPrivateKey, hash_algo: str = "sha256") -> bytes
    """RSA-PSS digital signature."""

verify_rsa_pss(data: bytes, signature: bytes, public_key: RSAPublicKey, hash_algo: str = "sha256") -> bool
    """Verify RSA-PSS signature."""
```

### graphy.kdf

```python
derive_pbkdf2(password: bytes, salt: bytes, iterations: int = 600000, key_length: int = 32) -> bytes
    """PBKDF2-HMAC-SHA256 key derivation."""

derive_scrypt(password: bytes, salt: bytes, n: int = 2**20, r: int = 8, p: int = 1, key_length: int = 32) -> bytes
    """scrypt key derivation."""

derive_argon2id(password: bytes, salt: bytes, time_cost: int = 3, memory_cost: int = 65536, parallelism: int = 4, key_length: int = 32) -> bytes
    """Argon2id key derivation (recommended for password hashing)."""

derive_hkdf(input_key: bytes, length: int = 32, salt: bytes | None = None, info: bytes = b"") -> bytes
    """HKDF-SHA256 key derivation."""
```

### graphy.mac

```python
compute_hmac(data: bytes, key: bytes, algorithm: str = "sha256") -> bytes
    """HMAC computation."""

verify_hmac(data: bytes, key: bytes, expected_mac: bytes, algorithm: str = "sha256") -> bool
    """HMAC verification (constant-time comparison)."""

compute_poly1305(data: bytes, key: bytes) -> bytes
    """Poly1305 MAC computation."""

compute_cmac(data: bytes, key: bytes) -> bytes
    """AES-CMAC computation."""
```

### graphy.certificates

```python
generate_self_signed_cert(
    common_name: str,
    private_key: PrivateKey,
    valid_days: int = 365,
    san_dns: list[str] | None = None,
    san_ips: list[str] | None = None,
) -> Certificate
    """Generate self-signed X.509 certificate."""

generate_csr(common_name: str, private_key: PrivateKey, san_dns: list[str] | None = None) -> CertificateSigningRequest
    """Generate Certificate Signing Request."""

verify_certificate_chain(cert: Certificate, ca_cert: Certificate) -> bool
    """Verify certificate was signed by CA."""

serialize_certificate(cert: Certificate) -> bytes
    """Serialize certificate to PEM."""

deserialize_certificate(pem_data: bytes) -> Certificate
    """Deserialize certificate from PEM."""
```

---

## currency — Cryptocurrency

### currency.wallets

```python
generate_mnemonic(strength: int = 256) -> str
    """Generate BIP-39 mnemonic phrase (24 words at 256 bits)."""

mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes
    """Convert mnemonic to 64-byte seed (BIP-39)."""

create_hd_wallet(seed: bytes) -> HDWallet
    """Create BIP-32 hierarchical deterministic wallet from seed."""

derive_child_key(wallet: HDWallet, path: str = "m/44'/0'/0'/0/0") -> DerivedKey
    """Derive child key using BIP-44 path."""
```

### currency.blockchain

```python
compute_merkle_root(transactions: list[bytes]) -> bytes
    """Compute Merkle tree root from transaction hashes."""

verify_merkle_proof(tx_hash: bytes, proof: list[tuple[bytes, str]], root: bytes) -> bool
    """Verify a Merkle inclusion proof."""

build_merkle_tree(leaves: list[bytes]) -> MerkleTree
    """Build complete Merkle tree structure."""
```

### currency.transactions

```python
create_transaction(sender: str, recipient: str, amount: float, fee: float = 0.0) -> Transaction
    """Create unsigned transaction."""

sign_transaction(tx: Transaction, private_key: bytes) -> SignedTransaction
    """Sign transaction with private key."""

verify_transaction(tx: SignedTransaction, public_key: bytes) -> bool
    """Verify transaction signature."""
```

### currency.addresses

```python
generate_bitcoin_address(public_key: bytes, network: str = "mainnet") -> str
    """Generate Bitcoin address from public key (P2PKH)."""

generate_ethereum_address(public_key: bytes) -> str
    """Generate Ethereum address from public key."""

validate_bitcoin_address(address: str) -> bool
    """Validate Bitcoin address format and checksum."""

validate_ethereum_address(address: str) -> bool
    """Validate Ethereum address format and EIP-55 checksum."""
```

### currency.tokens

```python
encode_erc20_transfer(to: str, amount: int) -> bytes
    """Encode ERC-20 transfer function call data."""

decode_erc20_transfer(data: bytes) -> tuple[str, int]
    """Decode ERC-20 transfer function call data."""
```

---

## analysis — Cryptanalysis

### analysis.entropy

```python
shannon_entropy(data: bytes) -> float
    """Calculate Shannon entropy in bits per byte (0.0 to 8.0)."""

min_entropy(data: bytes) -> float
    """Calculate min-entropy (conservative entropy estimate)."""

conditional_entropy(data: bytes, block_size: int = 2) -> float
    """Calculate conditional entropy for byte sequences."""
```

### analysis.frequency

```python
frequency_analysis(data: bytes) -> dict[int, float]
    """Byte frequency distribution (value -> proportion)."""

chi_squared_test(data: bytes) -> tuple[float, float]
    """Chi-squared test for uniform distribution. Returns (statistic, p-value)."""

index_of_coincidence(data: bytes) -> float
    """Index of coincidence for cipher classification."""
```

### analysis.strength

```python
assess_password_strength(password: str) -> StrengthReport
    """Comprehensive password strength assessment."""

assess_key_strength(key: bytes, algorithm: str) -> StrengthReport
    """Assess cryptographic key strength for given algorithm."""

estimate_crack_time(entropy_bits: float) -> dict[str, str]
    """Estimate time to brute-force given entropy."""
```

### analysis.classical_breaking

```python
break_caesar(ciphertext: str) -> list[tuple[int, str, float]]
    """Break Caesar cipher. Returns list of (shift, plaintext, score) ranked by likelihood."""

break_vigenere(ciphertext: str, max_key_length: int = 20) -> list[tuple[str, str, float]]
    """Break Vigenere cipher. Returns list of (key, plaintext, score)."""

detect_cipher_type(ciphertext: str) -> dict[str, float]
    """Heuristic cipher type detection. Returns type -> confidence mapping."""
```

---

## steganography — Data Hiding

### steganography.image_lsb

```python
embed_in_image(image_path: str, data: bytes, output_path: str, bits: int = 1) -> int
    """Embed data in image using LSB steganography. Returns bytes embedded."""

extract_from_image(image_path: str, length: int, bits: int = 1) -> bytes
    """Extract hidden data from image."""

calculate_capacity(image_path: str, bits: int = 1) -> int
    """Calculate maximum embedding capacity in bytes."""
```

### steganography.text_steg

```python
embed_in_text(cover_text: str, data: bytes) -> str
    """Embed data using zero-width Unicode characters."""

extract_from_text(stego_text: str) -> bytes
    """Extract hidden data from zero-width character steganography."""
```

### steganography.detection

```python
detect_lsb_steganography(image_path: str) -> DetectionResult
    """Statistical detection of LSB steganography."""

chi_squared_detection(image_path: str) -> float
    """Chi-squared attack for LSB detection. Returns p-value."""
```

---

## encoding — Crypto Encodings

### encoding.base_encodings

```python
encode_base64(data: bytes, url_safe: bool = False) -> str
    """Base64 encode."""

decode_base64(encoded: str, url_safe: bool = False) -> bytes
    """Base64 decode."""

encode_base58(data: bytes) -> str
    """Base58 encode (Bitcoin alphabet)."""

decode_base58(encoded: str) -> bytes
    """Base58 decode."""

encode_base32(data: bytes) -> str
    """Base32 encode."""

decode_base32(encoded: str) -> bytes
    """Base32 decode."""

encode_hex(data: bytes) -> str
    """Hexadecimal encode."""

decode_hex(encoded: str) -> bytes
    """Hexadecimal decode."""
```

### encoding.pem

```python
pem_encode(data: bytes, label: str = "CERTIFICATE") -> str
    """Encode binary data as PEM."""

pem_decode(pem_text: str) -> tuple[bytes, str]
    """Decode PEM to (binary_data, label)."""

detect_pem_type(pem_text: str) -> str
    """Detect PEM content type from label."""
```

---

## random — Cryptographic Randomness

### random.csprng

```python
generate_random_bytes(length: int) -> bytes
    """Generate cryptographically secure random bytes."""

generate_random_int(min_val: int, max_val: int) -> int
    """Generate cryptographically secure random integer in range."""

generate_random_token(length: int = 32) -> str
    """Generate URL-safe random token string."""

generate_uuid4() -> str
    """Generate cryptographically random UUID v4."""
```

### random.nist_tests

```python
run_frequency_test(data: bytes) -> TestResult
    """NIST SP 800-22 Frequency (Monobit) Test."""

run_runs_test(data: bytes) -> TestResult
    """NIST SP 800-22 Runs Test."""

run_block_frequency_test(data: bytes, block_size: int = 128) -> TestResult
    """NIST SP 800-22 Block Frequency Test."""

run_all_tests(data: bytes) -> dict[str, TestResult]
    """Run complete NIST SP 800-22 test suite."""
```

---

## protocols — Cryptographic Protocols

### protocols.key_exchange

```python
dh_parameters(key_size: int = 2048) -> DHParameters
    """Generate Diffie-Hellman parameters."""

dh_keypair(parameters: DHParameters) -> tuple[DHPrivateKey, DHPublicKey]
    """Generate DH keypair from parameters."""

dh_shared_secret(private_key: DHPrivateKey, peer_public_key: DHPublicKey) -> bytes
    """Compute DH shared secret."""

ecdh_keypair() -> tuple[X25519PrivateKey, X25519PublicKey]
    """Generate X25519 keypair for ECDH."""

ecdh_shared_secret(private_key: X25519PrivateKey, peer_public_key: X25519PublicKey) -> bytes
    """Compute ECDH shared secret."""
```

### protocols.secret_sharing

```python
split_secret(secret: bytes, total_shares: int, threshold: int) -> list[tuple[int, bytes]]
    """Shamir's Secret Sharing: split secret into shares."""

reconstruct_secret(shares: list[tuple[int, bytes]]) -> bytes
    """Reconstruct secret from threshold number of shares."""

verify_share(share: tuple[int, bytes], commitment: bytes) -> bool
    """Verify share against Feldman VSS commitment."""
```

### protocols.zero_knowledge

```python
schnorr_prove(secret: int, generator: int, prime: int) -> SchnorrProof
    """Generate Schnorr zero-knowledge proof of discrete log knowledge."""

schnorr_verify(proof: SchnorrProof, public_value: int, generator: int, prime: int) -> bool
    """Verify Schnorr ZKP."""

pedersen_commit(value: int, blinding: int, g: int, h: int, p: int) -> int
    """Create Pedersen commitment."""

pedersen_verify(commitment: int, value: int, blinding: int, g: int, h: int, p: int) -> bool
    """Verify Pedersen commitment opening."""
```

---

## Exceptions

All exceptions are defined in `crypto.exceptions`:

| Exception | Description |
|---|---|
| `CryptoError` | Base exception for all crypto errors |
| `SymmetricCipherError` | Symmetric encryption/decryption failure |
| `AsymmetricCipherError` | Asymmetric encryption/decryption failure |
| `HashError` | Hashing operation failure |
| `SignatureError` | Digital signature failure |
| `KDFError` | Key derivation failure |
| `CertificateError` | Certificate operation failure |
| `WalletError` | Wallet operation failure |
| `BlockchainError` | Blockchain operation failure |
| `SteganographyError` | Steganography operation failure |
| `EncodingError` | Encoding/decoding failure |
| `ProtocolError` | Protocol operation failure |
| `RandomError` | Random generation failure |
