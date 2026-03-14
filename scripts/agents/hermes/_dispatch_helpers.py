"""Dispatch helper functions for the Hermes sweep-and-dispatch orchestrator.

Extracted from ``dispatch_hermes.py`` to maintain the <800 LOC threshold.
Provides filesystem checkpoint/rollback and per-script dispatch orchestration.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

# Bootstrap path — not needed when package is already installed
try:
    from codomyrmex.agents.core.config import get_config
except ImportError:
    import sys

    sys.path.insert(
        0, str(Path(__file__).resolve().parent.parent.parent.parent / "src")
    )
    from codomyrmex.agents.core.config import get_config

from codomyrmex.utils.cli_helpers import print_error, print_success

# ── Filesystem Checkpoints ───────────────────────────────────────────


def resolve_checkpoint_config() -> dict:
    """Load checkpoint configuration from hermes.yaml.

    Returns:
        Checkpoint config dict, or empty dict on error.
    """
    try:
        config = get_config()
        hermes_cfg: dict = config.get("hermes", {}) if isinstance(config, dict) else {}
        return hermes_cfg.get("checkpoint", {})
    except Exception:
        return {}


def create_checkpoint(target_dir: Path, output_dir: Path) -> Path | None:
    """Create a filesystem snapshot before destructive --apply operations.

    Snapshots are stored as timestamped tar.gz archives in the configured
    checkpoint directory (default: ``~/.codomyrmex/checkpoints``).

    Args:
        target_dir: Directory being modified by apply operations.
        output_dir: Dispatch output directory (also checkpointed).

    Returns:
        Path to the checkpoint archive, or None on failure.
    """
    import tarfile

    cp_config = resolve_checkpoint_config()
    if not cp_config.get("enabled", True):
        return None

    cp_dir = Path(
        cp_config.get("snapshot_dir", "~/.codomyrmex/checkpoints")
    ).expanduser()
    cp_dir.mkdir(parents=True, exist_ok=True)

    # Enforce max_snapshots limit
    max_snapshots = int(cp_config.get("max_snapshots", 10))
    existing = sorted(cp_dir.glob("checkpoint_*.tar.gz"))
    while len(existing) >= max_snapshots:
        oldest = existing.pop(0)
        try:
            oldest.unlink()
        except OSError:
            pass

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = cp_dir / f"checkpoint_{timestamp}.tar.gz"

    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            if target_dir.exists():
                tar.add(target_dir, arcname=f"target/{target_dir.name}")
            if output_dir.exists():
                tar.add(output_dir, arcname=f"output/{output_dir.name}")
        print_success(f"  ✓ Checkpoint created: {archive_path}")
        return archive_path
    except Exception as exc:
        print_error(f"  ⚠  Checkpoint failed: {exc}")
        return None


def rollback_checkpoint(archive_path: Path, restore_to: Path) -> bool:
    """Restore files from a checkpoint archive.

    Args:
        archive_path: Path to the checkpoint tar.gz archive.
        restore_to: Base directory to extract into.

    Returns:
        True if rollback succeeded.
    """
    import tarfile

    if not archive_path.exists():
        print_error(f"  Checkpoint not found: {archive_path}")
        return False

    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=restore_to, filter="data")
        print_success(f"  ✓ Rollback from {archive_path.name} complete")
        return True
    except Exception as exc:
        print_error(f"  ⚠  Rollback failed: {exc}")
        return False
