# Wallet - API Specification

## Introduction

The Wallet module API provides programmatic access to self-custody wallet management, message signing, key rotation, encrypted backups, and Natural Ritual recovery. All operations are available as Python library functions.

## Classes and Interfaces

### Class: `WalletManager`

Primary interface for wallet lifecycle operations.

#### `WalletManager.__init__(storage_path=None)`

- **Description**: Initialize the wallet manager with optional key storage path.
- **Parameters**:
    - `storage_path` (Optional[Path]): Directory for key file storage. Defaults to system temp directory.

#### `WalletManager.create_wallet(user_id)`

- **Description**: Create a new wallet with generated address and private key.
- **Parameters**:
    - `user_id` (str): Unique identifier for the wallet owner.
- **Returns**: `str` - Wallet address (0x-prefixed hex string).
- **Raises**:
    - `WalletError`: If user already has a wallet.
    - `WalletKeyError`: If key storage fails.

#### `WalletManager.get_wallet_address(user_id)`

- **Description**: Retrieve wallet address for a user.
- **Parameters**:
    - `user_id` (str): User identifier.
- **Returns**: `Optional[str]` - Wallet address or None.

#### `WalletManager.has_wallet(user_id)`

- **Description**: Check if a user has a wallet.
- **Parameters**:
    - `user_id` (str): User identifier.
- **Returns**: `bool`

#### `WalletManager.sign_message(user_id, message)`

- **Description**: Sign a message using HMAC-SHA256 with the user's private key.
- **Parameters**:
    - `user_id` (str): User identifier.
    - `message` (bytes): Message to sign.
- **Returns**: `bytes` - HMAC-SHA256 signature (32 bytes).
- **Raises**:
    - `WalletNotFoundError`: If wallet or key not found.

#### `WalletManager.verify_signature(user_id, message, signature)`

- **Description**: Verify a message signature using constant-time comparison.
- **Parameters**:
    - `user_id` (str): User identifier.
    - `message` (bytes): Original message.
    - `signature` (bytes): Signature to verify.
- **Returns**: `bool` - True if valid.
- **Raises**:
    - `WalletNotFoundError`: If wallet or key not found.

#### `WalletManager.rotate_keys(user_id, reason="manual")`

- **Description**: Generate new key material and wallet address, replacing the old ones.
- **Parameters**:
    - `user_id` (str): User identifier.
    - `reason` (str): Reason for rotation (logged for audit trail).
- **Returns**: `str` - New wallet address.
- **Raises**:
    - `WalletNotFoundError`: If user has no wallet.
    - `WalletKeyError`: If key storage fails.

#### `WalletManager.backup_wallet(user_id)`

- **Description**: Generate backup metadata (never includes raw keys).
- **Parameters**:
    - `user_id` (str): User identifier.
- **Returns**: `dict` with keys: `user_id`, `wallet_id`, `key_hash`, `created_at`, `backup_ts`.
- **Raises**:
    - `WalletNotFoundError`: If user has no wallet.

#### `WalletManager.delete_wallet(user_id)`

- **Description**: Delete wallet and associated key file.
- **Parameters**:
    - `user_id` (str): User identifier.
- **Returns**: `bool` - True on success.
- **Raises**:
    - `WalletNotFoundError`: If user has no wallet.

#### `WalletManager.list_wallets()`

- **Description**: List all registered wallets.
- **Returns**: `Dict[str, str]` - Mapping of user_id to wallet_address.

---

### Class: `NaturalRitualRecovery`

Multi-factor knowledge-based key recovery system.

#### `NaturalRitualRecovery.__init__()`

- **Description**: Initialize with empty ritual store and default lockout of 5 attempts.

#### `NaturalRitualRecovery.register_ritual(user_id, steps)`

- **Description**: Register a recovery ritual for a user.
- **Parameters**:
    - `user_id` (str): User identifier.
    - `steps` (List[RitualStep]): Ordered recovery steps.
- **Raises**:
    - `RitualError`: If steps list is empty.

#### `NaturalRitualRecovery.initiate_recovery(user_id, responses)`

- **Description**: Attempt recovery by providing responses to all ritual steps.
- **Parameters**:
    - `user_id` (str): User identifier.
    - `responses` (List[str]): Response strings, one per step.
- **Returns**: `bool` - True if all responses match.
- **Raises**:
    - `RitualError`: If user is locked out.

#### `NaturalRitualRecovery.has_ritual(user_id)`

- **Returns**: `bool` - True if ritual registered.

#### `NaturalRitualRecovery.get_prompts(user_id)`

- **Returns**: `List[str]` - Ritual prompt strings.
- **Raises**: `RitualError` if no ritual registered.

#### `NaturalRitualRecovery.get_remaining_attempts(user_id)`

- **Returns**: `int` - Remaining attempts before lockout.

#### `NaturalRitualRecovery.is_locked(user_id)`

- **Returns**: `bool` - True if locked out.

#### `NaturalRitualRecovery.reset_attempts(user_id)`

- **Description**: Admin operation to reset attempt counter.

#### `NaturalRitualRecovery.unregister_ritual(user_id)`

- **Returns**: `bool` - True if a ritual was removed.

---

### Class: `BackupManager`

Encrypted wallet backup management.

#### `BackupManager.__init__(backup_dir=None, key_manager=None)`

- **Parameters**:
    - `backup_dir` (Optional[Path]): Backup storage directory.
    - `key_manager` (Optional[KeyManager]): KeyManager instance.

#### `BackupManager.create_backup(user_id, wallet_id, metadata=None)`

- **Returns**: `dict` - Backup record with `backup_id`, `user_id`, `wallet_id`, `key_hash`, `timestamp`, `metadata`.
- **Raises**: `WalletNotFoundError` if key not found.

#### `BackupManager.list_backups(user_id)`

- **Returns**: `List[dict]` - Backups sorted newest first.

#### `BackupManager.verify_backup(user_id, backup_id)`

- **Returns**: `bool` - True if backup key hash matches current key.
- **Raises**: `WalletNotFoundError` if backup or key not found.

#### `BackupManager.delete_backup(user_id, backup_id)`

- **Returns**: `bool` - True on success.

---

### Class: `KeyRotation`

Policy-driven key rotation with audit trail.

#### `KeyRotation.__init__(policy=None)`

- **Parameters**:
    - `policy` (Optional[RotationPolicy]): Rotation policy. Default: 90 days / 10000 sigs.

#### `KeyRotation.register_wallet(user_id, wallet_id)`

- **Description**: Register a wallet for rotation tracking.

#### `KeyRotation.record_signature(user_id)`

- **Description**: Increment the signature counter for a user.

#### `KeyRotation.needs_rotation(user_id)`

- **Returns**: `bool` - True if rotation is recommended by policy.

#### `KeyRotation.record_rotation(user_id, old_wallet_id, new_wallet_id, reason="scheduled")`

- **Returns**: `RotationRecord` - Audit record of the rotation.

#### `KeyRotation.get_rotation_history(user_id)`

- **Returns**: `List[RotationRecord]` - Full rotation history.
- **Raises**: `WalletNotFoundError` if no history exists.

---

### Class: `Wallet` (Facade)

Simplified unified interface combining `WalletManager` and `NaturalRitualRecovery`.

#### `Wallet.__init__(user_id, storage_path=None)`

- **Parameters**:
    - `user_id` (str): Owner's unique identifier.
    - `storage_path` (Optional[Path]): Key storage directory.

#### Properties: `address`, `is_active`

#### Methods: `create()`, `sign(message)`, `verify(message, signature)`, `rotate(reason)`, `setup_recovery(steps)`, `recover(responses)`, `backup()`, `delete()`

---

## Data Models

### `RitualStep`

- `prompt` (str): Challenge question.
- `expected_response_hash` (str): SHA-256 hex digest of expected answer.

### `RotationRecord`

- `user_id` (str): User identifier.
- `old_wallet_id` (str): Previous wallet address.
- `new_wallet_id` (str): New wallet address.
- `timestamp` (str): ISO 8601 timestamp.
- `reason` (str): Rotation reason.

### `RotationPolicy`

- `max_age_days` (int): Maximum key age in days. Default: 90.
- `max_signatures` (int): Maximum signatures before rotation. Default: 10000.
- `auto_rotate` (bool): Enable automatic rotation. Default: False.

## Convenience Functions

- `create_wallet(user_id, storage_path=None) -> str`: Quick wallet creation.
- `get_wallet_manager(storage_path=None) -> WalletManager`: Get manager instance.
- `hash_response(response: str) -> str`: Hash a ritual response.

## Versioning

Current version: `0.1.0` (accessible via `codomyrmex.wallet.__version__`).
