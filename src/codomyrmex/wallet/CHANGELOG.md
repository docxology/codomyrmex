# Changelog for Wallet Module

All notable changes to this module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-04

### Added

- `WalletManager` class with wallet creation, signing, verification, rotation, backup, deletion, and listing.
- `NaturalRitualRecovery` class with multi-step knowledge-based recovery, attempt tracking, and lockout protection.
- `BackupManager` class for encrypted backup creation, listing, verification, and deletion.
- `KeyRotation` class with policy-based rotation tracking, audit trail, and pre/post rotation hooks.
- `Wallet` facade class combining `WalletManager` and `NaturalRitualRecovery` into a unified API.
- `RitualStep` dataclass for defining recovery ritual steps.
- `RotationRecord` dataclass for rotation audit records.
- `RotationPolicy` dataclass for configuring rotation thresholds.
- `hash_response()` convenience function for hashing ritual responses.
- Custom exception hierarchy: `WalletError`, `WalletNotFoundError`, `WalletKeyError`, `RitualError`.
- `__version__` string (`"0.1.0"`).
- `py.typed` marker for PEP 561 type hint support.
- Convenience functions: `create_wallet()`, `get_wallet_manager()`.
- Comprehensive test suite covering all classes and methods.
- Full documentation: SPEC.md, API_SPECIFICATION.md, MCP_TOOL_SPECIFICATION.md, SECURITY.md, USAGE_EXAMPLES.md.
- MCP tool specifications for `wallet_create`, `wallet_sign`, `wallet_rotate_keys`, `wallet_backup`, `wallet_recover`.

### Security

- Constant-time signature verification via `hmac.compare_digest()`.
- Key files stored with restrictive 0o600 permissions.
- Backup records contain key hashes only, never plaintext keys.
- Recovery attempt lockout after configurable threshold (default: 5 attempts).
