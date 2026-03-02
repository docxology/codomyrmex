"""Automated database backup and restore operations.

Provides backup scheduling, execution, verification, and restore
for SQLite, PostgreSQL, and generic SQL databases.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class BackupFormat(Enum):
    """Supported backup formats."""
    SQL_DUMP = "sql_dump"
    FILE_COPY = "file_copy"
    COMPRESSED = "compressed"


@dataclass
class BackupMetadata:
    """Metadata for a backup."""
    backup_id: str
    source: str
    destination: str
    format: BackupFormat
    timestamp: float = field(default_factory=time.time)
    size_bytes: int = 0
    checksum: str = ""
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "backup_id": self.backup_id,
            "source": self.source,
            "destination": self.destination,
            "format": self.format.value,
            "timestamp": self.timestamp,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "success": self.success,
            "error": self.error,
        }


class DatabaseBackup:
    """Automated database backup and restore manager.

    Supports SQLite file copies and PostgreSQL pg_dump/pg_restore.
    """

    def __init__(self, backup_dir: Path) -> None:
        self._backup_dir = backup_dir
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self._backup_dir / "manifest.json"
        self._manifest: list[dict[str, Any]] = self._load_manifest()

    def _load_manifest(self) -> list[dict[str, Any]]:
        if self._manifest_path.exists():
            return json.loads(self._manifest_path.read_text())
        return []

    def _save_manifest(self) -> None:
        self._manifest_path.write_text(json.dumps(self._manifest, indent=2))

    def backup_sqlite(self, db_path: Path, backup_name: str | None = None) -> BackupMetadata:
        """Create a backup of a SQLite database."""
        name = backup_name or f"sqlite_{int(time.time())}"
        dest = self._backup_dir / f"{name}.db"

        try:
            shutil.copy2(db_path, dest)
            metadata = BackupMetadata(
                backup_id=name,
                source=str(db_path),
                destination=str(dest),
                format=BackupFormat.FILE_COPY,
                size_bytes=dest.stat().st_size,
            )
        except Exception as e:
            metadata = BackupMetadata(
                backup_id=name,
                source=str(db_path),
                destination=str(dest),
                format=BackupFormat.FILE_COPY,
                success=False,
                error=str(e),
            )

        self._manifest.append(metadata.to_dict())
        self._save_manifest()
        return metadata

    def backup_postgres(self, connection_string: str,
                        backup_name: str | None = None) -> BackupMetadata:
        """Create a pg_dump backup of a PostgreSQL database."""
        name = backup_name or f"pg_{int(time.time())}"
        dest = self._backup_dir / f"{name}.sql"

        try:
            result = subprocess.run(
                ["pg_dump", connection_string, "-f", str(dest)],
                capture_output=True, text=True, timeout=300,
            )
            success = result.returncode == 0
            metadata = BackupMetadata(
                backup_id=name,
                source=connection_string,
                destination=str(dest),
                format=BackupFormat.SQL_DUMP,
                size_bytes=dest.stat().st_size if dest.exists() else 0,
                success=success,
                error=result.stderr if not success else None,
            )
        except Exception as e:
            metadata = BackupMetadata(
                backup_id=name,
                source=connection_string,
                destination=str(dest),
                format=BackupFormat.SQL_DUMP,
                success=False,
                error=str(e),
            )

        self._manifest.append(metadata.to_dict())
        self._save_manifest()
        return metadata

    def restore_sqlite(self, backup_id: str, target_path: Path) -> bool:
        """Restore a SQLite backup to a target path."""
        entry = self._find_backup(backup_id)
        if not entry:
            logger.error("Backup %s not found", backup_id)
            return False
        source = Path(entry["destination"])
        if not source.exists():
            logger.error("Backup file missing: %s", source)
            return False
        shutil.copy2(source, target_path)
        return True

    def list_backups(self) -> list[dict[str, Any]]:
        return list(self._manifest)

    def _find_backup(self, backup_id: str) -> dict[str, Any] | None:
        for entry in self._manifest:
            if entry["backup_id"] == backup_id:
                return entry
        return None

    def prune(self, keep_last: int = 5) -> int:
        """Remove old backups, keeping the most recent N."""
        if len(self._manifest) <= keep_last:
            return 0
        to_remove = self._manifest[:-keep_last]
        self._manifest = self._manifest[-keep_last:]
        removed = 0
        for entry in to_remove:
            path = Path(entry["destination"])
            if path.exists():
                path.unlink()
                removed += 1
        self._save_manifest()
        return removed
