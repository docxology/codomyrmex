# Crypto Tests — PAI Integration

**Version**: v0.1.7 | **Last Updated**: February 2026

## PAI VERIFY Phase Mapping

The crypto test suite directly supports the PAI Algorithm's VERIFY phase. Every cryptographic operation implemented during BUILD and EXECUTE phases must be validated through these tests before deployment.

### VERIFY: Correctness Validation

| Test Category | PAI Verification Goal | Test Files |
|---|---|---|
| Round-trip tests | Confirm BUILD phase implementations are reversible | test_graphy_symmetric.py, test_encoding.py |
| Known-answer tests | Confirm outputs match authoritative standards | test_graphy_hashing.py, test_graphy_kdf.py |
| Signature verification | Confirm digital signatures are valid and verifiable | test_graphy_signatures.py |
| Protocol correctness | Confirm key exchange produces matching shared secrets | test_protocols.py |

### VERIFY: Security Validation

| Test Category | PAI Verification Goal | Test Files |
|---|---|---|
| Nonce uniqueness | Confirm no nonce reuse in encryption | test_graphy_symmetric.py |
| Key randomness | Confirm generated keys have sufficient entropy | test_random.py |
| Authentication tags | Confirm AEAD modes reject tampered ciphertext | test_graphy_symmetric.py |
| Timing safety | Confirm MAC verification is constant-time | test_graphy_mac.py |

### VERIFY: Quality Metrics

| Metric | Target | Measurement |
|---|---|---|
| Line coverage | >= 90% | `uv run pytest --cov` |
| All correctness tests pass | 100% | `uv run pytest -m crypto` |
| All security tests pass | 100% | `uv run pytest -m "crypto and security"` |
| No regressions | 0 failures | CI pipeline gate |

### VERIFY: Integration Validation

Cross-submodule test scenarios verify that the complete cryptographic workflow is sound:

1. **Key lifecycle**: Generate -> Serialize -> Deserialize -> Use -> Verify
2. **Encrypted communication**: Key exchange -> Derive key -> Encrypt -> Transmit -> Decrypt -> Verify
3. **Wallet workflow**: Mnemonic -> Seed -> HD wallet -> Derive address -> Sign transaction -> Verify

## PAI OBSERVE Phase Support

Test results from `analysis/` tests feed back into the OBSERVE phase:

- Entropy measurements confirm data quality observations.
- Frequency analysis tests validate the observation tools themselves.
- Strength assessment tests calibrate the THINK phase evaluations.

## Agent Test Execution in PAI Workflow

1. **Engineer** implements tests during BUILD phase.
2. **QATester** executes tests during VERIFY phase.
3. **Architect** reviews test architecture during THINK phase.
4. **Security Agent** audits security tests as part of VERIFY security gate.

All test results are captured as PAI artifacts and inform subsequent algorithm iterations.
