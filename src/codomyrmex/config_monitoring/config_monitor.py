import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.core.logger_config import get_logger

"""Configuration Monitoring Module for Codomyrmex."""

logger = get_logger(__name__)


@dataclass
class ConfigChange:
    """Configuration change record."""

    change_id: str
    config_path: str
    change_type: str  # "created", "modified", "deleted"
    timestamp: datetime
    previous_hash: str | None = None
    current_hash: str | None = None
    changes: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"


@dataclass
class ConfigAudit:
    """Configuration audit record."""

    audit_id: str
    timestamp: datetime
    environment: str
    compliance_status: str
    issues_found: list[str]
    recommendations: list[str]
    audit_scope: dict[str, Any]


@dataclass
class ConfigSnapshot:
    """Configuration snapshot for drift detection."""

    snapshot_id: str
    timestamp: datetime
    environment: str
    config_hashes: dict[str, str]
    total_files: int


class ConfigurationMonitor:
    """Configuration monitoring and auditing system."""

    def __init__(self, workspace_dir: str | Path | None = None):
        """Initialize configuration monitor.

        Args:
            workspace_dir: Workspace directory for monitoring data
        """
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.monitoring_dir = self.workspace_dir / "config_monitoring"
        self.snapshots_dir = self.monitoring_dir / "snapshots"
        self.audits_dir = self.workspace_dir / "config_audits"
        self._ensure_directories()

        self._changes: list[ConfigChange] = []
        self._snapshots: dict[str, ConfigSnapshot] = {}
        self._audits: list[ConfigAudit] = []
        self._load_local_data()
        self._load_audit_data()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.audits_dir.mkdir(parents=True, exist_ok=True)

    def _load_local_data(self) -> None:
        """Load snapshots from local storage if they exist."""
        if self.snapshots_dir.exists():
            for snap_file in self.snapshots_dir.glob("*.json"):
                try:
                    with open(snap_file) as f:
                        data = json.load(f)
                        snapshot = ConfigSnapshot(
                            snapshot_id=data["snapshot_id"],
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            environment=data["environment"],
                            config_hashes=data["config_hashes"],
                            total_files=data["total_files"],
                        )
                        self._snapshots[snapshot.snapshot_id] = snapshot
                except (json.JSONDecodeError, KeyError, ValueError, OSError) as e:
                    logger.warning(f"Failed to load snapshot {snap_file}: {e}")

    def _load_audit_data(self) -> None:
        """Load audit reports from local storage if they exist."""
        if self.audits_dir.exists():
            for audit_file in self.audits_dir.glob("*.json"):
                try:
                    with open(audit_file) as f:
                        data = json.load(f)
                        audit = ConfigAudit(
                            audit_id=data["audit_id"],
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            environment=data["environment"],
                            compliance_status=data["compliance_status"],
                            issues_found=data["issues_found"],
                            recommendations=data["recommendations"],
                            audit_scope=data["audit_scope"],
                        )
                        self._audits.append(audit)
                except (json.JSONDecodeError, KeyError, ValueError, OSError) as e:
                    logger.warning(f"Failed to load audit {audit_file}: {e}")

    def calculate_file_hash(self, file_path: str | Path) -> str:
        """Calculate SHA-256 hash of a configuration file.

        Args:
            file_path: Path to the file

        Returns:
            SHA-256 hash or empty string if file doesn't exist
        """
        path = Path(file_path)
        if not path.is_file():
            return ""

        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def record_change(
        self,
        config_path: str,
        change_type: str,
        previous_hash: str | None = None,
        current_hash: str | None = None,
        source: str = "unknown",
    ) -> ConfigChange:
        """Create and store a ConfigChange record.

        Args:
            config_path: Path to changed config file
            change_type: Type of change ("created", "modified", "deleted")
            previous_hash: Hash before change
            current_hash: Hash after change
            source: Source of change

        Returns:
            The recorded ConfigChange
        """
        change_id = f"chg_{int(time.time() * 1000)}"
        change = ConfigChange(
            change_id=change_id,
            config_path=str(config_path),
            change_type=change_type,
            timestamp=datetime.now(),
            previous_hash=previous_hash,
            current_hash=current_hash,
            source=source,
        )
        self._changes.append(change)
        if len(self._changes) > 1000:
            self._changes = self._changes[-1000:]
        return change

    def detect_config_changes(
        self, config_paths: list[str | Path]
    ) -> list[ConfigChange]:
        """Detect changes in configuration files and persist hashes.

        Args:
            config_paths: List of configuration file paths to monitor

        Returns:
            List of detected changes
        """
        changes = []
        new_hashes = {}

        for config_path in config_paths:
            path = Path(config_path)
            str_path = str(path.absolute())
            current_hash = self.calculate_file_hash(path)
            previous_hash = self._get_previous_hash(str_path)

            if not path.exists():
                if previous_hash:
                    change = self.record_change(str_path, "deleted", previous_hash, "")
                    changes.append(change)
                    logger.info(f"Detected deletion: {str_path}")
                    # Remove from new_hashes so it's removed from persistence
                    self._remove_hash(str_path)
                continue

            if previous_hash is None:
                change = self.record_change(str_path, "created", None, current_hash)
                changes.append(change)
                logger.info(f"Detected new file: {str_path}")
                new_hashes[str_path] = current_hash
            elif current_hash != previous_hash:
                change = self.record_change(
                    str_path, "modified", previous_hash, current_hash
                )
                changes.append(change)
                logger.info(f"Detected modification: {str_path}")
                new_hashes[str_path] = current_hash
            else:
                # No change, but keep it in the store
                new_hashes[str_path] = current_hash

        if new_hashes:
            self._persist_hashes(new_hashes)

        return changes

    def _get_previous_hash(self, file_path: str) -> str | None:
        """Get previous hash for a file from persistent storage."""
        hash_store_path = self.monitoring_dir / "config_hashes.json"
        if not hash_store_path.exists():
            return None
        try:
            with open(hash_store_path) as f:
                stored_hashes = json.load(f)
            return stored_hashes.get(file_path)
        except (json.JSONDecodeError, OSError):
            return None

    def _persist_hashes(self, file_hashes: dict[str, str]) -> None:
        """Persist file hashes to disk."""
        hash_store_path = self.monitoring_dir / "config_hashes.json"
        existing: dict[str, str] = {}
        if hash_store_path.exists():
            try:
                with open(hash_store_path) as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        existing.update(file_hashes)
        with open(hash_store_path, "w") as f:
            json.dump(existing, f, indent=2)

    def _remove_hash(self, file_path: str) -> None:
        """Remove a file hash from persistent storage."""
        hash_store_path = self.monitoring_dir / "config_hashes.json"
        if not hash_store_path.exists():
            return
        try:
            with open(hash_store_path) as f:
                existing = json.load(f)
            if file_path in existing:
                del existing[file_path]
                with open(hash_store_path, "w") as f:
                    json.dump(existing, f, indent=2)
        except (json.JSONDecodeError, OSError):
            pass

    def create_snapshot(
        self, environment: str, config_dir: str | Path
    ) -> ConfigSnapshot:
        """Hash all files in directory and store as ConfigSnapshot.

        Args:
            environment: Environment name
            config_dir: Directory containing configuration files

        Returns:
            Created snapshot
        """
        path = Path(config_dir)
        if not path.is_dir():
            raise CodomyrmexError(
                f"Configuration directory does not exist: {config_dir}"
            )

        config_hashes = {}
        files = [f for f in path.rglob("*") if f.is_file()]
        for f in files:
            config_hashes[str(f.absolute())] = self.calculate_file_hash(f)

        snapshot_id = f"snap_{environment}_{int(time.time())}"
        snapshot = ConfigSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            environment=environment,
            config_hashes=config_hashes,
            total_files=len(config_hashes),
        )

        self._snapshots[snapshot_id] = snapshot

        # Persist to disk
        snap_file = self.snapshots_dir / f"{snapshot_id}.json"
        with open(snap_file, "w") as f:
            json.dump(
                {
                    "snapshot_id": snapshot.snapshot_id,
                    "timestamp": snapshot.timestamp.isoformat(),
                    "environment": snapshot.environment,
                    "config_hashes": snapshot.config_hashes,
                    "total_files": snapshot.total_files,
                },
                f,
                indent=2,
            )

        return snapshot

    def detect_drift(self, snapshot_id: str, config_dir: str | Path) -> dict[str, Any]:
        """Compare current hashes in directory to snapshot.

        Args:
            snapshot_id: ID of the snapshot
            config_dir: Directory to compare

        Returns:
            Drift analysis report
        """
        if snapshot_id not in self._snapshots:
            # Try reloading from disk just in case
            self._load_local_data()
            if snapshot_id not in self._snapshots:
                raise CodomyrmexError(f"Snapshot not found: {snapshot_id}")

        snapshot = self._snapshots[snapshot_id]
        current_dir = Path(config_dir).absolute()

        current_files = {
            str(f.absolute()): self.calculate_file_hash(f)
            for f in current_dir.rglob("*")
            if f.is_file()
        }

        drift_details = []

        # Check snapshot files against current
        for path, expected_hash in snapshot.config_hashes.items():
            if path not in current_files:
                drift_details.append(
                    {
                        "path": path,
                        "issue": "deleted",
                        "expected": expected_hash,
                        "actual": None,
                    }
                )
            elif current_files[path] != expected_hash:
                drift_details.append(
                    {
                        "path": path,
                        "issue": "modified",
                        "expected": expected_hash,
                        "actual": current_files[path],
                    }
                )

        # Check current files not in snapshot
        for path, actual_hash in current_files.items():
            if path not in snapshot.config_hashes:
                drift_details.append(
                    {
                        "path": path,
                        "issue": "added",
                        "expected": None,
                        "actual": actual_hash,
                    }
                )

        return {
            "snapshot_id": snapshot_id,
            "drift_detected": len(drift_details) > 0,
            "drift_count": len(drift_details),
            "details": drift_details,
            "timestamp": datetime.now().isoformat(),
        }

    def audit_configuration(
        self,
        environment: str,
        config_dir: str | Path,
        compliance_rules: dict[str, Any] | None = None,
    ) -> ConfigAudit:
        """Perform compliance audit on configuration files.

        Args:
            environment: Environment name
            config_dir: Directory to audit
            compliance_rules: Optional rules (not fully implemented in this thin layer)

        Returns:
            ConfigAudit record
        """
        path = Path(config_dir)
        if not path.is_dir():
            raise CodomyrmexError(f"Audit directory does not exist: {config_dir}")

        issues = []
        recommendations = []
        files_audited = 0

        sensitive_patterns = [
            (
                re.compile(r'password\s*[:=]\s*["\'][^"\']+["\']', re.I),
                "Plaintext password pattern found",
            ),
            (
                re.compile(r'api_key\s*[:=]\s*["\'][^"\']+["\']', re.I),
                "Plaintext API key pattern found",
            ),
            (
                re.compile(r'secret\s*[:=]\s*["\'][^"\']+["\']', re.I),
                "Plaintext secret pattern found",
            ),
            (
                re.compile(r'token\s*[:=]\s*["\'][^"\']+["\']', re.I),
                "Plaintext token pattern found",
            ),
            (
                re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
                "Unencrypted private key found",
            ),
        ]

        for f in path.rglob("*"):
            if not f.is_file():
                continue

            files_audited += 1
            # Check permissions (on Unix-like)
            try:
                if f.stat().st_mode & 0o077:
                    issues.append(
                        f"Overly permissive permissions on {f.name}: {oct(f.stat().st_mode)}"
                    )
                    recommendations.append(
                        f"Restrict {f.name} permissions to owner-only (e.g., 600)"
                    )
            except (OSError, AttributeError):
                pass

            # Check content
            try:
                content = f.read_text(errors="ignore")
                for pattern, msg in sensitive_patterns:
                    if pattern.search(content):
                        issues.append(f"{msg} in {f.name}")
                        recommendations.append(
                            f"Move sensitive data in {f.name} to a secure secret manager"
                        )
            except Exception as e:
                logger.debug(f"Could not read {f} for audit: {e}")

        audit_id = f"audit_{environment}_{int(time.time())}"
        audit = ConfigAudit(
            audit_id=audit_id,
            timestamp=datetime.now(),
            environment=environment,
            compliance_status="non_compliant" if issues else "compliant",
            issues_found=issues,
            recommendations=list(set(recommendations)),
            audit_scope={
                "files_audited": files_audited,
                "config_dir": str(path.absolute()),
            },
        )

        self._audits.append(audit)

        # Persist audit
        audit_file = self.audits_dir / f"{audit_id}.json"
        with open(audit_file, "w") as f:
            json.dump(
                {
                    "audit_id": audit.audit_id,
                    "timestamp": audit.timestamp.isoformat(),
                    "environment": audit.environment,
                    "compliance_status": audit.compliance_status,
                    "issues_found": audit.issues_found,
                    "recommendations": audit.recommendations,
                    "audit_scope": audit.audit_scope,
                },
                f,
                indent=2,
            )

        return audit

    def get_changes(self, config_path: str | None = None) -> list[ConfigChange]:
        """Retrieve change history, optionally filtered by path.

        Args:
            config_path: Optional path to filter by

        Returns:
            List of changes
        """
        if config_path:
            abs_path = str(Path(config_path).absolute())
            return [c for c in self._changes if c.config_path == abs_path]
        return self._changes

    def get_recent_changes(self, hours: int = 24) -> list[ConfigChange]:
        """Get configuration changes from the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [c for c in self._changes if c.timestamp >= cutoff]

    def get_audit_history(self, environment: str | None = None) -> list[ConfigAudit]:
        """Get audit history."""
        audits = self._audits
        if environment:
            audits = [a for a in audits if a.environment == environment]
        return sorted(audits, key=lambda a: a.timestamp, reverse=True)

    def get_monitoring_summary(self) -> dict[str, Any]:
        """Get monitoring summary."""
        return {
            "total_snapshots": len(self._snapshots),
            "total_changes": len(self._changes),
            "recent_changes": len(self.get_recent_changes(24)),
            "total_audits": len(self._audits),
            "last_audit_at": self._audits[-1].timestamp.isoformat()
            if self._audits
            else None,
            "status": "active",
        }


def monitor_config_changes(
    config_paths: list[str | Path], workspace_dir: str | Path | None = None
) -> dict[str, Any]:
    """Monitor configuration changes once and return summary."""
    monitor = ConfigurationMonitor(workspace_dir)
    changes = monitor.detect_config_changes(config_paths)
    return {
        "paths_monitored": len(config_paths),
        "changes_detected": len(changes),
        "summary": monitor.get_monitoring_summary(),
    }
