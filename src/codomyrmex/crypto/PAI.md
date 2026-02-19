# Crypto Module — PAI Integration

**Version**: v0.1.7 | **PAI Algorithm Mapping** | **Last Updated**: February 2026

## PAI Algorithm Phase Mapping

The crypto module maps to multiple phases of the PAI Algorithm, providing cryptographic capabilities that agents can leverage during their workflow.

### OBSERVE Phase

**Submodule**: `analysis/`

- **Entropy Assessment**: Use `shannon_entropy()` and `min_entropy()` to observe the randomness quality of data, keys, and tokens encountered during reconnaissance.
- **Frequency Analysis**: Use `frequency_analysis()` and `chi_squared_test()` to observe statistical properties of unknown data or ciphertext.
- **Cipher Detection**: Use `detect_cipher_type()` to classify unknown ciphertext encountered during observation.

### THINK Phase

**Submodule**: `analysis/`

- **Strength Assessment**: Use `assess_password_strength()` and `assess_key_strength()` to evaluate cryptographic decisions. Informs whether current security parameters are adequate.
- **Crack Time Estimation**: Use `estimate_crack_time()` to reason about the practical security margin of observed configurations.
- **Algorithm Selection**: Consult `cli_commands()["crypto:algorithms"]` to enumerate available algorithms when planning cryptographic architecture.

### BUILD Phase

**Submodules**: `graphy/`, `protocols/`, `encoding/`

- **Implement Encryption**: Use `graphy.symmetric` for data-at-rest encryption, `graphy.asymmetric` for key transport.
- **Key Management**: Use `graphy.kdf` for deriving keys from passwords, `graphy.certificates` for PKI.
- **Digital Signatures**: Use `graphy.signatures` for code signing, document authentication.
- **Protocol Implementation**: Use `protocols.key_exchange` for secure channel establishment, `protocols.secret_sharing` for distributed trust.
- **Encoding**: Use `encoding` for serialization of cryptographic artifacts.

### EXECUTE Phase

**Submodules**: `currency/`, `random/`, `steganography/`

- **Blockchain Operations**: Use `currency.wallets` for wallet generation, `currency.transactions` for transaction construction and signing.
- **Address Generation**: Use `currency.addresses` for Bitcoin/Ethereum address derivation.
- **Secure Randomness**: Use `random.csprng` for generating nonces, keys, tokens during execution.
- **Data Hiding**: Use `steganography` for embedding data in cover media during execution workflows.

### VERIFY Phase

**Submodules**: `encoding/`, `analysis/`, `random/`, `graphy/`

- **Format Validation**: Use `encoding` to verify PEM, Base64, Base58 format correctness.
- **Quality Checks**: Use `analysis.entropy` to verify generated keys meet entropy thresholds.
- **Randomness Testing**: Use `random.nist_tests` to validate CSPRNG output quality.
- **Signature Verification**: Use `graphy.signatures` verify functions to authenticate artifacts.
- **Certificate Verification**: Use `graphy.certificates.verify_certificate_chain()` to validate PKI chains.
- **Hash Verification**: Use `graphy.hashing.verify_hash()` to confirm data integrity.

## Agent Capabilities

| PAI Agent Type | Primary Submodules | Use Case |
|---|---|---|
| Engineer | graphy/, protocols/, encoding/ | Implementing cryptographic features |
| Architect | analysis/, protocols/ | Evaluating security architecture |
| QATester | analysis/, random/, encoding/ | Validating cryptographic correctness |
| Security | All submodules | Full security assessment |

## Trust Gateway

Cryptographic operations that generate or manage keys require trust level `TRUSTED` or higher. Read-only operations (hashing, analysis, encoding) operate at `OBSERVED` trust level.
