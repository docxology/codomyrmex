# Wallet - Usage Examples

## Example 1: Basic Wallet Lifecycle

Create a wallet, sign a message, verify it, and generate a backup.

```python
from codomyrmex.wallet import WalletManager

# Initialize manager
wallet_mgr = WalletManager()

# Create wallet
address = wallet_mgr.create_wallet("agent_001")
print(f"Wallet created: {address}")  # 0x1a2b3c...

# Sign a message
message = b"Authorize transfer of 100 units"
signature = wallet_mgr.sign_message("agent_001", message)
print(f"Signature: {signature.hex()}")

# Verify the signature
is_valid = wallet_mgr.verify_signature("agent_001", message, signature)
print(f"Valid: {is_valid}")  # True

# Generate backup metadata
backup = wallet_mgr.backup_wallet("agent_001")
print(f"Backup: {backup}")
```

### Expected Outcome

A wallet address is created, a message is signed with HMAC-SHA256, the signature verifies correctly, and backup metadata (with key hash, never raw key) is returned.

## Example 2: Natural Ritual Recovery

Set up knowledge-based recovery and test the recovery flow.

```python
import hashlib
from codomyrmex.wallet import NaturalRitualRecovery, RitualStep, hash_response

recovery = NaturalRitualRecovery()

# Define recovery ritual with secret knowledge
steps = [
    RitualStep("What was your first pet's name?", hash_response("Whiskers")),
    RitualStep("What city were you born in?", hash_response("Portland")),
    RitualStep("What was your childhood nickname?", hash_response("Sparky")),
]
recovery.register_ritual("agent_001", steps)

# Successful recovery
success = recovery.initiate_recovery("agent_001", ["Whiskers", "Portland", "Sparky"])
print(f"Recovery succeeded: {success}")  # True

# Failed recovery (wrong answer)
failed = recovery.initiate_recovery("agent_001", ["Fluffy", "Portland", "Sparky"])
print(f"Recovery succeeded: {failed}")  # False
print(f"Remaining attempts: {recovery.get_remaining_attempts('agent_001')}")
```

### Expected Outcome

Recovery succeeds with correct answers and fails with incorrect ones. Attempt counter decrements on failure.

## Example 3: Key Rotation with Policy

Track signatures and rotate keys when policy thresholds are reached.

```python
from codomyrmex.wallet import WalletManager, KeyRotation, RotationPolicy

# Create wallet
wallet_mgr = WalletManager()
address = wallet_mgr.create_wallet("agent_002")

# Set up rotation tracking with aggressive policy
policy = RotationPolicy(max_age_days=30, max_signatures=100)
rotation = KeyRotation(policy=policy)
rotation.register_wallet("agent_002", address)

# Simulate signing operations
for _ in range(100):
    wallet_mgr.sign_message("agent_002", b"data")
    rotation.record_signature("agent_002")

# Check if rotation is needed
if rotation.needs_rotation("agent_002"):
    old_address = address
    new_address = wallet_mgr.rotate_keys("agent_002", reason="signature_limit")
    rotation.record_rotation("agent_002", old_address, new_address, "signature_limit")
    print(f"Rotated: {old_address} -> {new_address}")

# View rotation history
history = rotation.get_rotation_history("agent_002")
for record in history:
    print(f"  {record.timestamp}: {record.reason}")
```

### Expected Outcome

After 100 signatures, `needs_rotation()` returns True. Keys are rotated and the event is recorded in the audit trail.

## Example 4: Wallet Facade (Simplified API)

Use the `Wallet` class for a streamlined single-user experience.

```python
from codomyrmex.wallet import RitualStep, hash_response
from codomyrmex.wallet.wallet import Wallet

# Create and use a wallet
w = Wallet("agent_003")
address = w.create()
print(f"Active: {w.is_active}, Address: {w.address}")

# Sign and verify
sig = w.sign(b"Hello World")
assert w.verify(b"Hello World", sig)

# Set up recovery
w.setup_recovery([
    RitualStep("Color?", hash_response("Blue")),
    RitualStep("Number?", hash_response("42")),
])

# Rotate keys
new_address = w.rotate(reason="periodic")
print(f"New address: {new_address}")

# Create backup
backup = w.backup()
print(f"Backup timestamp: {backup['backup_ts']}")
```

### Expected Outcome

Complete wallet lifecycle through the simplified facade: create, sign, verify, set up recovery, rotate, and backup.

## Example 5: Backup Manager

Create and verify persistent backup files.

```python
from pathlib import Path
from codomyrmex.wallet import WalletManager, BackupManager

wallet_mgr = WalletManager()
address = wallet_mgr.create_wallet("agent_004")

# Create backup manager sharing the same key manager
backup_mgr = BackupManager(key_manager=wallet_mgr.key_manager)

# Create a backup
record = backup_mgr.create_backup(
    "agent_004", address, metadata={"note": "pre-rotation backup"}
)
print(f"Backup ID: {record['backup_id']}")

# List backups
backups = backup_mgr.list_backups("agent_004")
print(f"Total backups: {len(backups)}")

# Verify backup integrity
is_valid = backup_mgr.verify_backup("agent_004", record["backup_id"])
print(f"Backup valid: {is_valid}")  # True

# After key rotation, backup becomes stale
wallet_mgr.rotate_keys("agent_004")
is_still_valid = backup_mgr.verify_backup("agent_004", record["backup_id"])
print(f"Backup still valid: {is_still_valid}")  # False (key changed)
```

### Expected Outcome

Backup is created, listed, and verified. After key rotation, the backup's key hash no longer matches the current key, so verification returns False.

## Common Pitfalls & Troubleshooting

- **Issue**: `WalletError: User already has a wallet`
  - **Solution**: Check with `has_wallet()` before calling `create_wallet()`, or use `get_wallet_address()` to retrieve the existing wallet.

- **Issue**: `WalletNotFoundError: Wallet not found or locked`
  - **Solution**: Ensure the wallet was created in the same `WalletManager` instance (wallets are not persisted across restarts in v0.1.0).

- **Issue**: `RitualError: User is locked out`
  - **Solution**: The user has exhausted recovery attempts. An admin must call `reset_attempts()` to unlock.

- **Issue**: Recovery always fails
  - **Solution**: Ensure responses are hashed with `hash_response()` when creating `RitualStep` objects, and that the exact plaintext responses are provided during recovery (case-sensitive).

- **Issue**: Backup verification fails after rotation
  - **Solution**: This is expected. Create a new backup after each key rotation.
