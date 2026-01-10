"""Backup Management Module for Codomyrmex Database Management.

This module provides database backup, restore, and recovery capabilities
with support for SQLite, PostgreSQL, and MySQL databases.
"""

import gzip
import hashlib
import os
import re
import shutil
import sqlite3
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class Backup:
    """Database backup information."""
    backup_id: str
    database_name: str
    database_type: str
    backup_type: str
    file_path: str
    size_mb: float
    created_at: datetime
    compression: str = "none"
    encryption: bool = False
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BackupResult:
    """Result of a backup operation."""
    backup_id: str
    success: bool
    duration: float
    file_size_mb: float
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    checksum: Optional[str] = None


class BackupManager:
    """Database backup and restore management system."""

    def __init__(
        self,
        workspace_dir: Optional[str] = None,
        database_url: Optional[str] = None
    ):
        """Initialize backup manager."""
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.backups_dir = self.workspace_dir / "database_backups"
        self._ensure_directories()
        self._backups: Dict[str, Backup] = {}
        self._database_url = database_url

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def _parse_database_url(self, url: str) -> Dict[str, Any]:
        """Parse database URL into components."""
        if url.startswith("sqlite"):
            match = re.match(r'sqlite:///(.+)', url)
            if match:
                return {"type": "sqlite", "database": match.group(1)}

        pattern = r'(?:postgresql|postgres|mysql)://(?:([^:]+):([^@]+)@)?([^:\/]+)(?::(\d+))?/(.+)'
        match = re.match(pattern, url)
        if match:
            db_type = "postgresql" if "postgres" in url else "mysql"
            return {
                "type": db_type,
                "user": match.group(1) or ("postgres" if db_type == "postgresql" else "root"),
                "password": match.group(2) or "",
                "host": match.group(3),
                "port": int(match.group(4)) if match.group(4) else (5432 if db_type == "postgresql" else 3306),
                "database": match.group(5)
            }

        raise CodomyrmexError(f"Invalid database URL: {url}")

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def create_backup(
        self,
        database_name: str,
        database_url: Optional[str] = None,
        backup_type: str = "full",
        compression: str = "gzip",
        include_schema: bool = True,
        include_data: bool = True
    ) -> BackupResult:
        """Create a database backup."""
        url = database_url or self._database_url
        if not url:
            raise CodomyrmexError("No database URL provided")

        db_params = self._parse_database_url(url)
        db_type = db_params["type"]

        backup_id = f"backup_{database_name}_{db_type}_{int(time.time())}"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{backup_id}_{timestamp}.sql"
        if compression == "gzip":
            backup_filename += ".gz"

        backup_path = self.backups_dir / backup_filename
        start_time = time.time()
        warnings = []

        try:
            if db_type == "sqlite":
                self._backup_sqlite(db_params["database"], str(backup_path), compression)
            elif db_type == "postgresql":
                self._backup_postgresql(db_params, str(backup_path), compression, include_schema, include_data)
            elif db_type == "mysql":
                self._backup_mysql(db_params, str(backup_path), compression, include_schema, include_data)
            else:
                raise CodomyrmexError(f"Unsupported database type: {db_type}")

            duration = time.time() - start_time
            file_size = backup_path.stat().st_size / (1024 * 1024)
            checksum = self._calculate_checksum(str(backup_path))

            backup = Backup(
                backup_id=backup_id,
                database_name=database_name,
                database_type=db_type,
                backup_type=backup_type,
                file_path=str(backup_path),
                size_mb=file_size,
                created_at=datetime.now(),
                compression=compression,
                checksum=checksum,
                metadata={
                    "include_schema": include_schema,
                    "include_data": include_data,
                }
            )

            self._backups[backup_id] = backup

            return BackupResult(
                backup_id=backup_id,
                success=True,
                duration=duration,
                file_size_mb=file_size,
                warnings=warnings,
                checksum=checksum
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to create backup {backup_id}: {e}")
            return BackupResult(
                backup_id=backup_id,
                success=False,
                duration=duration,
                file_size_mb=0.0,
                error_message=str(e)
            )

    def _backup_sqlite(self, db_path: str, backup_path: str, compression: str):
        """Backup SQLite database."""
        if not os.path.exists(db_path):
            raise CodomyrmexError(f"SQLite database not found: {db_path}")

        conn = sqlite3.connect(db_path)
        try:
            if compression == "gzip":
                with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                    for line in conn.iterdump():
                        f.write(f"{line}\n")
            else:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    for line in conn.iterdump():
                        f.write(f"{line}\n")
        finally:
            conn.close()

    def _backup_postgresql(
        self,
        params: Dict[str, Any],
        backup_path: str,
        compression: str,
        include_schema: bool,
        include_data: bool
    ):
        """Backup PostgreSQL database using pg_dump."""
        if not shutil.which("pg_dump"):
            raise CodomyrmexError("pg_dump not found. Install PostgreSQL client tools.")

        cmd = [
            "pg_dump",
            "-h", params["host"],
            "-p", str(params["port"]),
            "-U", params["user"],
            "-d", params["database"],
            "--no-password"
        ]

        if not include_data:
            cmd.append("--schema-only")
        if not include_schema:
            cmd.append("--data-only")

        env = os.environ.copy()
        env["PGPASSWORD"] = params.get("password", "")

        result = subprocess.run(cmd, capture_output=True, env=env, timeout=3600)
        if result.returncode != 0:
            raise CodomyrmexError(f"pg_dump failed: {result.stderr.decode()}")

        if compression == "gzip":
            with gzip.open(backup_path, 'wb') as f:
                f.write(result.stdout)
        else:
            with open(backup_path, 'wb') as f:
                f.write(result.stdout)

    def _backup_mysql(
        self,
        params: Dict[str, Any],
        backup_path: str,
        compression: str,
        include_schema: bool,
        include_data: bool
    ):
        """Backup MySQL database using mysqldump."""
        if not shutil.which("mysqldump"):
            raise CodomyrmexError("mysqldump not found. Install MySQL client tools.")

        cmd = [
            "mysqldump",
            "-h", params["host"],
            "-P", str(params["port"]),
            "-u", params["user"],
            f"-p{params.get('password', '')}",
            params["database"]
        ]

        if not include_data:
            cmd.append("--no-data")
        if not include_schema:
            cmd.append("--no-create-info")

        result = subprocess.run(cmd, capture_output=True, timeout=3600)
        if result.returncode != 0:
            raise CodomyrmexError(f"mysqldump failed: {result.stderr.decode()}")

        if compression == "gzip":
            with gzip.open(backup_path, 'wb') as f:
                f.write(result.stdout)
        else:
            with open(backup_path, 'wb') as f:
                f.write(result.stdout)

    def list_backups(self, database_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available backups."""
        backups = []
        for backup in self._backups.values():
            if database_name and backup.database_name != database_name:
                continue
            backups.append({
                "backup_id": backup.backup_id,
                "database_name": backup.database_name,
                "size_mb": backup.size_mb,
                "created_at": backup.created_at.isoformat(),
            })
        return sorted(backups, key=lambda b: b["created_at"], reverse=True)

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup."""
        if backup_id not in self._backups:
            return False
        backup = self._backups[backup_id]
        try:
            Path(backup.file_path).unlink(missing_ok=True)
            del self._backups[backup_id]
            return True
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return False


# Convenience functions
def backup_database(
    database_name: str,
    database_url: Optional[str] = None,
    backup_type: str = "full",
    compression: str = "gzip"
) -> BackupResult:
    """Convenience function to backup a database."""
    manager = BackupManager()
    return manager.create_backup(database_name, database_url, backup_type, compression)
