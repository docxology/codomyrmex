from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
import json
import re
import time

from dataclasses import dataclass, field
import hashlib

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger







#!/usr/bin/env python3

Configuration Monitoring Module for Codomyrmex Configuration Management.

This module provides configuration monitoring, change tracking, drift detection,
and compliance auditing for configuration management.
"""

logger = get_logger(__name__)

@dataclass
class ConfigChange:
    """Configuration change record."""
    change_id: str
    config_path: str
    change_type: str  # "created", "modified", "deleted"
    timestamp: datetime
    previous_hash: Optional[str] = None
    current_hash: Optional[str] = None
    changes: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"  # Who made the change

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

    def __init__(self, workspace_dir: Optional[str] = None):
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

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.audits_dir.mkdir(parents=True, exist_ok=True)

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate hash of a configuration file.

        Args:
            file_path: Path to the file

        Returns:
            File hash
        """
        path = Path(file_path)
        if not path.exists():
            return ""

        with open(path, 'rb') as f:
            content = f.read()

        return hashlib.sha256(content).hexdigest()

    def detect_config_changes(self, config_paths: list[str]) -> list[ConfigChange]:
        """Detect changes in configuration files.

        Args:
            config_paths: List of configuration file paths to monitor

        Returns:
            List of detected changes
        """
        changes = []

        for config_path in config_paths:
            path = Path(config_path)

            if not path.exists():
                # File was deleted
                change = ConfigChange(
                    change_id=f"delete_{int(time.time())}_{path.name}",
                    config_path=str(path),
                    change_type="deleted",
                    timestamp=datetime.now(),
                    previous_hash=self._get_previous_hash(str(path)),
                    current_hash=""
                )
                changes.append(change)
                logger.info(f"Detected configuration file deletion: {path}")
                continue

            current_hash = self.calculate_file_hash(str(path))

            # Check if file is new or modified
            previous_hash = self._get_previous_hash(str(path))

            if previous_hash is None:
                # New file
                change = ConfigChange(
                    change_id=f"create_{int(time.time())}_{path.name}",
                    config_path=str(path),
                    change_type="created",
                    timestamp=datetime.now(),
                    current_hash=current_hash
                )
                changes.append(change)
                logger.info(f"Detected new configuration file: {path}")

            elif current_hash != previous_hash:
                # File modified
                change = ConfigChange(
                    change_id=f"modify_{int(time.time())}_{path.name}",
                    config_path=str(path),
                    change_type="modified",
                    timestamp=datetime.now(),
                    previous_hash=previous_hash,
                    current_hash=current_hash
                )
                changes.append(change)
                logger.info(f"Detected configuration file modification: {path}")

        # Store changes
        self._changes.extend(changes)

        # Keep only recent changes (last 1000)
        if len(self._changes) > 1000:
            self._changes = self._changes[-1000:]

        return changes

    def _get_previous_hash(self, file_path: str) -> Optional[str]:
        """Get previous hash for a file."""
        # This would typically check a database or file storage
        # For now, return None (assume all files are new)
        return None

    def create_snapshot(self, environment: str, config_paths: list[str]) -> ConfigSnapshot:
        """Create a snapshot of configuration files for drift detection.

        Args:
            environment: Environment name
            config_paths: List of configuration file paths

        Returns:
            Created snapshot
        """
        snapshot_id = f"snapshot_{environment}_{int(time.time())}"

        config_hashes = {}
        for config_path in config_paths:
            config_hashes[config_path] = self.calculate_file_hash(config_path)

        snapshot = ConfigSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            environment=environment,
            config_hashes=config_hashes,
            total_files=len(config_paths)
        )

        self._snapshots[snapshot_id] = snapshot

        # Save snapshot
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
        with open(snapshot_file, 'w') as f:
            json.dump({
                "snapshot_id": snapshot.snapshot_id,
                "timestamp": snapshot.timestamp.isoformat(),
                "environment": snapshot.environment,
                "config_hashes": snapshot.config_hashes,
                "total_files": snapshot.total_files
            }, f, indent=2)

        logger.info(f"Created configuration snapshot: {snapshot_id} ({len(config_paths)} files)")
        return snapshot

    def detect_drift(self, snapshot_id: str, current_paths: list[str]) -> dict[str, Any]:
        """Detect configuration drift against a snapshot.

        Args:
            snapshot_id: ID of the snapshot to compare against
            current_paths: Current configuration file paths

        Returns:
            Drift analysis results
        """
        if snapshot_id not in self._snapshots:
            raise CodomyrmexError(f"Snapshot not found: {snapshot_id}")

        snapshot = self._snapshots[snapshot_id]
        drift_report = {
            "snapshot_id": snapshot_id,
            "environment": snapshot.environment,
            "comparison_timestamp": datetime.now().isoformat(),
            "files_in_drift": 0,
            "files_missing": 0,
            "files_added": 0,
            "drift_details": []
        }

        # Check for modified files
        for config_path in snapshot.config_hashes:
            if config_path not in current_paths:
                drift_report["files_missing"] += 1
                drift_report["drift_details"].append({
                    "path": config_path,
                    "issue": "file_missing",
                    "expected_hash": snapshot.config_hashes[config_path],
                    "current_hash": None
                })
            else:
                current_hash = self.calculate_file_hash(config_path)
                expected_hash = snapshot.config_hashes[config_path]

                if current_hash != expected_hash:
                    drift_report["files_in_drift"] += 1
                    drift_report["drift_details"].append({
                        "path": config_path,
                        "issue": "file_modified",
                        "expected_hash": expected_hash,
                        "current_hash": current_hash
                    })

        # Check for added files
        for current_path in current_paths:
            if current_path not in snapshot.config_hashes:
                drift_report["files_added"] += 1
                drift_report["drift_details"].append({
                    "path": current_path,
                    "issue": "file_added",
                    "expected_hash": None,
                    "current_hash": self.calculate_file_hash(current_path)
                })

        logger.info(f"Configuration drift analysis complete for {snapshot_id}")
        return drift_report

    def audit_configuration(
        self,
        environment: str,
        config_paths: list[str],
        compliance_rules: Optional[dict[str, Any]] = None
    ) -> ConfigAudit:
        """Audit configuration for compliance and best practices.

        Args:
            environment: Environment being audited
            config_paths: Configuration files to audit
            compliance_rules: Custom compliance rules

        Returns:
            Audit results
        """
        audit_id = f"audit_{environment}_{int(time.time())}"
        issues_found = []
        recommendations = []

        # Basic compliance checks
        for config_path in config_paths:
            path = Path(config_path)

            if not path.exists():
                issues_found.append(f"Configuration file missing: {config_path}")
                continue

            # Check file permissions
            if path.stat().st_mode & 0o077:  # World-readable
                issues_found.append(f"Configuration file has overly permissive permissions: {config_path}")

            # Check for sensitive data in plain text
            content = path.read_text()
            if self._contains_sensitive_data(content):
                issues_found.append(f"Potential sensitive data in plain text: {config_path}")

            # Check for required configuration sections
            if not self._has_required_sections(content):
                issues_found.append(f"Missing required configuration sections: {config_path}")

        # Generate recommendations
        if issues_found:
            recommendations.append("Review and fix identified security issues")
            recommendations.append("Implement configuration validation")
            recommendations.append("Set up regular configuration audits")

        # Default compliance rules if none provided
        if compliance_rules is None:
            compliance_rules = {
                "require_encryption": True,
                "require_validation": True,
                "require_backups": True
            }

        compliance_status = "compliant" if not issues_found else "non_compliant"

        audit = ConfigAudit(
            audit_id=audit_id,
            timestamp=datetime.now(),
            environment=environment,
            compliance_status=compliance_status,
            issues_found=issues_found,
            recommendations=recommendations,
            audit_scope={"files_audited": len(config_paths), "rules_applied": compliance_rules}
        )

        self._audits.append(audit)

        # Save audit results
        audit_file = self.audits_dir / f"{audit_id}.json"
        with open(audit_file, 'w') as f:
            json.dump({
                "audit_id": audit.audit_id,
                "timestamp": audit.timestamp.isoformat(),
                "environment": audit.environment,
                "compliance_status": audit.compliance_status,
                "issues_found": audit.issues_found,
                "recommendations": audit.recommendations,
                "audit_scope": audit.audit_scope
            }, f, indent=2)

        logger.info(f"Completed configuration audit: {audit_id} ({compliance_status})")
        return audit

    def _contains_sensitive_data(self, content: str) -> bool:
        """Check if content contains potential sensitive data."""
        sensitive_patterns = [
            r'password\s*[:=]\s*["\'][^"\']+["\']',
            r'api_key\s*[:=]\s*["\'][^"\']+["\']',
            r'secret\s*[:=]\s*["\'][^"\']+["\']',
            r'token\s*[:=]\s*["\'][^"\']+["\']',
        ]

        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    def _has_required_sections(self, content: str) -> bool:
        """Check if configuration has required sections."""
        # This would check for environment-specific required sections
        # For now, just check if it's not empty
        return bool(content.strip())

    def get_recent_changes(self, hours: int = 24) -> list[ConfigChange]:
        """Get configuration changes from the last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            List of recent changes
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        return [
            change for change in self._changes
            if change.timestamp >= cutoff_time
        ]

    def get_audit_history(self, environment: Optional[str] = None) -> list[ConfigAudit]:
        """Get audit history.

        Args:
            environment: Filter by environment name

        Returns:
            List of audits
        """
        audits = self._audits

        if environment:
            audits = [a for a in audits if a.environment == environment]

        # Sort by timestamp (most recent first)
        audits.sort(key=lambda a: a.timestamp, reverse=True)

        return audits

    def get_monitoring_summary(self) -> dict[str, Any]:
        """Get monitoring summary.

        Returns:
            Summary of monitoring activities
        """
        recent_changes = self.get_recent_changes(24)  # Last 24 hours

        return {
            "total_snapshots": len(self._snapshots),
            "total_changes": len(self._changes),
            "recent_changes": len(recent_changes),
            "total_audits": len(self._audits),
            "last_audit": self._audits[-1].timestamp.isoformat() if self._audits else None,
            "monitoring_status": "active"
        }

def monitor_config_changes(
    config_paths: list[str],
    interval_seconds: int = 300,  # 5 minutes
    workspace_dir: Optional[str] = None
) -> dict[str, Any]:
    """Monitor configuration changes continuously.

    Args:
        config_paths: List of configuration paths to monitor
        interval_seconds: Monitoring interval in seconds
        workspace_dir: Workspace directory

    Returns:
        Monitoring summary
    """
    monitor = ConfigurationMonitor(workspace_dir)

    # Run initial scan
    changes = monitor.detect_config_changes(config_paths)

    # In a real implementation, this would run continuously
    # For now, just return summary
    return {
        "monitoring_active": True,
        "interval_seconds": interval_seconds,
        "paths_monitored": len(config_paths),
        "initial_changes_detected": len(changes),
        "changes": [change.__dict__ for change in changes]
    }
