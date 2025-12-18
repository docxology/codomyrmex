#!/usr/bin/env python3
"""
Backup Management Module for Codomyrmex Database Management.

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
from typing import Any, Optional

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class Backup:
    """Database backup information."""
    backup_id: str
    database_name: str
    database_type: str  # "sqlite", "postgresql", "mysql"
    backup_type: str  # "full", "incremental", "differential"
    file_path: str
    size_mb: float
    created_at: datetime
    compression: str = "none"
    encryption: bool = False
    checksum: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BackupResult:
    """Result of a backup operation."""
    backup_id: str
    success: bool
    duration: float
    file_size_mb: float
    error_message: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    checksum: Optional[str] = None


class BackupManager:
    """Database backup and restore management system.

    Supports:
    - SQLite: Direct file copy with optional compression
    - PostgreSQL: pg_dump/pg_restore
    - MySQL: mysqldump/mysql
    """

    def __init__(
        self,
        workspace_dir: Optional[str] = None,
        database_url: Optional[str] = None
    ):
        """Initialize backup manager.

        Args:
            workspace_dir: Directory for storing backup data
            database_url: Database connection URL (optional)
        """
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.backups_dir = self.workspace_dir / "database_backups"
        self._ensure_directories()

        self._backups: dict[str, Backup] = {}
        self._database_url = database_url

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def _parse_database_url(self, url: str) -> dict[str, Any]:
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
        """Create a database backup.

        Args:
            database_name: Friendly name for the backup
            database_url: Database connection URL (uses default if not provided)
            backup_type: Type of backup ("full", "schema", "data")
            compression: Compression method ("none", "gzip")
            include_schema: Include schema in backup
            include_data: Include data in backup

        Returns:
            Backup operation result
        """
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
                    "database_url_masked": self._mask_password(url)
                }
            )

            self._backups[backup_id] = backup

            result = BackupResult(
                backup_id=backup_id,
                success=True,
                duration=duration,
                file_size_mb=file_size,
                warnings=warnings,
                checksum=checksum
            )

            logger.info(f"Created backup {backup_id}: {file_size:.2f} MB in {duration:.2f}s")
            return result

        except Exception as e:
            duration = time.time() - start_time

            result = BackupResult(
                backup_id=backup_id,
                success=False,
                duration=duration,
                file_size_mb=0.0,
                error_message=str(e)
            )

            logger.error(f"Failed to create backup {backup_id}: {e}")
            return result

    def _backup_sqlite(self, db_path: str, backup_path: str, compression: str):
        """Backup SQLite database."""
        if not os.path.exists(db_path):
            raise CodomyrmexError(f"SQLite database not found: {db_path}")

        # Connect and dump
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
        params: dict[str, Any],
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

        try:
            if compression == "gzip":
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    env=env,
                    timeout=3600
                )
                if result.returncode != 0:
                    raise CodomyrmexError(f"pg_dump failed: {result.stderr.decode()}")

                with gzip.open(backup_path, 'wb') as f:
                    f.write(result.stdout)
            else:
                with open(backup_path, 'wb') as f:
                    result = subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        env=env,
                        timeout=3600
                    )
                    if result.returncode != 0:
                        raise CodomyrmexError(f"pg_dump failed: {result.stderr.decode()}")

        except subprocess.TimeoutExpired:
            raise CodomyrmexError("pg_dump timed out after 1 hour")

    def _backup_mysql(
        self,
        params: dict[str, Any],
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

        try:
            if compression == "gzip":
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=3600
                )
                if result.returncode != 0:
                    raise CodomyrmexError(f"mysqldump failed: {result.stderr.decode()}")

                with gzip.open(backup_path, 'wb') as f:
                    f.write(result.stdout)
            else:
                with open(backup_path, 'wb') as f:
                    result = subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        timeout=3600
                    )
                    if result.returncode != 0:
                        raise CodomyrmexError(f"mysqldump failed: {result.stderr.decode()}")

        except subprocess.TimeoutExpired:
            raise CodomyrmexError("mysqldump timed out after 1 hour")

    def restore_backup(
        self,
        backup_id: str,
        target_database_url: Optional[str] = None,
        drop_existing: bool = False
    ) -> BackupResult:
        """Restore a database from backup.

        Args:
            backup_id: ID of the backup to restore
            target_database_url: Target database URL (uses original if not provided)
            drop_existing: Drop existing database before restore

        Returns:
            Restore operation result
        """
        if backup_id not in self._backups:
            # Try to find backup file by ID pattern
            found = False
            for path in self.backups_dir.iterdir():
                if path.name.startswith(backup_id):
                    found = True
                    break
            if not found:
                raise CodomyrmexError(f"Backup not found: {backup_id}")

        backup = self._backups.get(backup_id)
        if backup:
            backup_path = backup.file_path
            db_type = backup.database_type
        else:
            raise CodomyrmexError(f"Backup metadata not found: {backup_id}")

        target_url = target_database_url or self._database_url
        if not target_url:
            raise CodomyrmexError("No target database URL provided")

        target_params = self._parse_database_url(target_url)
        start_time = time.time()

        try:
            # Verify checksum if available
            if backup.checksum:
                current_checksum = self._calculate_checksum(backup_path)
                if current_checksum != backup.checksum:
                    raise CodomyrmexError("Backup checksum mismatch - file may be corrupted")

            if db_type == "sqlite":
                self._restore_sqlite(backup_path, target_params["database"], backup.compression)
            elif db_type == "postgresql":
                self._restore_postgresql(backup_path, target_params, backup.compression, drop_existing)
            elif db_type == "mysql":
                self._restore_mysql(backup_path, target_params, backup.compression, drop_existing)
            else:
                raise CodomyrmexError(f"Unsupported database type: {db_type}")

            duration = time.time() - start_time

            result = BackupResult(
                backup_id=f"restore_{backup_id}",
                success=True,
                duration=duration,
                file_size_mb=backup.size_mb
            )

            logger.info(f"Restored backup {backup_id} in {duration:.2f}s")
            return result

        except Exception as e:
            duration = time.time() - start_time

            result = BackupResult(
                backup_id=f"restore_{backup_id}",
                success=False,
                duration=duration,
                file_size_mb=0.0,
                error_message=str(e)
            )

            logger.error(f"Failed to restore backup {backup_id}: {e}")
            return result

    def _restore_sqlite(self, backup_path: str, db_path: str, compression: str):
        """Restore SQLite database."""
        # Remove existing database
        if os.path.exists(db_path):
            os.remove(db_path)

        conn = sqlite3.connect(db_path)

        try:
            if compression == "gzip":
                with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                    sql = f.read()
            else:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    sql = f.read()

            conn.executescript(sql)
            conn.commit()
        finally:
            conn.close()

    def _restore_postgresql(
        self,
        backup_path: str,
        params: dict[str, Any],
        compression: str,
        drop_existing: bool
    ):
        """Restore PostgreSQL database using psql."""
        if not shutil.which("psql"):
            raise CodomyrmexError("psql not found. Install PostgreSQL client tools.")

        env = os.environ.copy()
        env["PGPASSWORD"] = params.get("password", "")

        if drop_existing:
            # Drop and recreate database
            drop_cmd = [
                "psql",
                "-h", params["host"],
                "-p", str(params["port"]),
                "-U", params["user"],
                "-d", "postgres",
                "-c", f"DROP DATABASE IF EXISTS {params['database']}"
            ]
            subprocess.run(drop_cmd, env=env, capture_output=True)

            create_cmd = [
                "psql",
                "-h", params["host"],
                "-p", str(params["port"]),
                "-U", params["user"],
                "-d", "postgres",
                "-c", f"CREATE DATABASE {params['database']}"
            ]
            subprocess.run(create_cmd, env=env, capture_output=True)

        cmd = [
            "psql",
            "-h", params["host"],
            "-p", str(params["port"]),
            "-U", params["user"],
            "-d", params["database"],
            "--no-password"
        ]

        try:
            if compression == "gzip":
                with gzip.open(backup_path, 'rb') as f:
                    sql_data = f.read()
                result = subprocess.run(
                    cmd,
                    input=sql_data,
                    capture_output=True,
                    env=env,
                    timeout=3600
                )
            else:
                with open(backup_path, 'rb') as f:
                    result = subprocess.run(
                        cmd,
                        stdin=f,
                        capture_output=True,
                        env=env,
                        timeout=3600
                    )

            if result.returncode != 0:
                raise CodomyrmexError(f"psql restore failed: {result.stderr.decode()}")

        except subprocess.TimeoutExpired:
            raise CodomyrmexError("psql restore timed out after 1 hour")

    def _restore_mysql(
        self,
        backup_path: str,
        params: dict[str, Any],
        compression: str,
        drop_existing: bool
    ):
        """Restore MySQL database."""
        if not shutil.which("mysql"):
            raise CodomyrmexError("mysql client not found. Install MySQL client tools.")

        if drop_existing:
            drop_cmd = [
                "mysql",
                "-h", params["host"],
                "-P", str(params["port"]),
                "-u", params["user"],
                f"-p{params.get('password', '')}",
                "-e", f"DROP DATABASE IF EXISTS {params['database']}; CREATE DATABASE {params['database']}"
            ]
            subprocess.run(drop_cmd, capture_output=True)

        cmd = [
            "mysql",
            "-h", params["host"],
            "-P", str(params["port"]),
            "-u", params["user"],
            f"-p{params.get('password', '')}",
            params["database"]
        ]

        try:
            if compression == "gzip":
                with gzip.open(backup_path, 'rb') as f:
                    sql_data = f.read()
                result = subprocess.run(
                    cmd,
                    input=sql_data,
                    capture_output=True,
                    timeout=3600
                )
            else:
                with open(backup_path, 'rb') as f:
                    result = subprocess.run(
                        cmd,
                        stdin=f,
                        capture_output=True,
                        timeout=3600
                    )

            if result.returncode != 0:
                raise CodomyrmexError(f"mysql restore failed: {result.stderr.decode()}")

        except subprocess.TimeoutExpired:
            raise CodomyrmexError("mysql restore timed out after 1 hour")

    def _mask_password(self, url: str) -> str:
        """Mask password in database URL."""
        return re.sub(r'(://[^:]+:)[^@]+(@)', r'\1***\2', url)

    def list_backups(self, database_name: Optional[str] = None) -> list[dict[str, Any]]:
        """List available backups."""
        backups = []

        for backup in self._backups.values():
            if database_name and backup.database_name != database_name:
                continue

            backups.append({
                "backup_id": backup.backup_id,
                "database_name": backup.database_name,
                "database_type": backup.database_type,
                "backup_type": backup.backup_type,
                "file_path": backup.file_path,
                "size_mb": backup.size_mb,
                "created_at": backup.created_at.isoformat(),
                "compression": backup.compression,
                "encryption": backup.encryption,
                "checksum": backup.checksum
            })

        backups.sort(key=lambda b: b["created_at"], reverse=True)
        return backups

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup."""
        if backup_id not in self._backups:
            return False

        backup = self._backups[backup_id]

        try:
            backup_file = Path(backup.file_path)
            if backup_file.exists():
                backup_file.unlink()

            del self._backups[backup_id]

            logger.info(f"Deleted backup: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete backup {backup_id}: {e}")
            return False

    def get_backup_info(self, backup_id: str) -> Optional[dict[str, Any]]:
        """Get detailed information about a backup."""
        if backup_id not in self._backups:
            return None

        backup = self._backups[backup_id]

        return {
            "backup_id": backup.backup_id,
            "database_name": backup.database_name,
            "database_type": backup.database_type,
            "backup_type": backup.backup_type,
            "file_path": backup.file_path,
            "size_mb": backup.size_mb,
            "created_at": backup.created_at.isoformat(),
            "compression": backup.compression,
            "encryption": backup.encryption,
            "checksum": backup.checksum,
            "metadata": backup.metadata
        }

    def verify_backup(self, backup_id: str) -> dict[str, Any]:
        """Verify backup integrity."""
        if backup_id not in self._backups:
            raise CodomyrmexError(f"Backup not found: {backup_id}")

        backup = self._backups[backup_id]
        issues = []

        # Check file exists
        if not os.path.exists(backup.file_path):
            issues.append("Backup file not found")
            return {"valid": False, "issues": issues}

        # Verify checksum
        if backup.checksum:
            current_checksum = self._calculate_checksum(backup.file_path)
            if current_checksum != backup.checksum:
                issues.append("Checksum mismatch - file may be corrupted")

        # Check file size
        current_size = os.path.getsize(backup.file_path) / (1024 * 1024)
        size_diff = abs(current_size - backup.size_mb)
        if size_diff > 0.1:  # More than 100KB difference
            issues.append(f"File size changed: expected {backup.size_mb:.2f} MB, got {current_size:.2f} MB")

        return {
            "valid": len(issues) == 0,
            "backup_id": backup_id,
            "file_exists": os.path.exists(backup.file_path),
            "checksum_valid": backup.checksum and not any("Checksum" in i for i in issues),
            "issues": issues
        }


def backup_database(
    database_name: str,
    database_url: Optional[str] = None,
    backup_type: str = "full",
    compression: str = "gzip"
) -> BackupResult:
    """Create a database backup.

    Args:
        database_name: Name for the backup
        database_url: Database connection URL
        backup_type: Type of backup
        compression: Compression method

    Returns:
        Backup operation result
    """
    manager = BackupManager()
    return manager.create_backup(database_name, database_url, backup_type, compression)
