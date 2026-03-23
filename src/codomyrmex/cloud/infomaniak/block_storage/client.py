"""
Infomaniak Block Storage Client (Cinder).

Provides volume and backup operations via the OpenStack Cinder API.
"""

from typing import Any

from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class InfomaniakVolumeClient(InfomaniakOpenStackBase):
    """
    Client for Infomaniak block storage (Cinder) operations.

    Provides methods for managing volumes and backups.

    Usage:
        from codomyrmex.cloud.infomaniak import InfomaniakVolumeClient

        client = InfomaniakVolumeClient.from_env()
        volumes = client.list_volumes()
    """

    _service_name = "block_storage"

    # =========================================================================
    # Volume Operations
    # =========================================================================

    def list_volumes(self) -> list[dict[str, Any]]:
        """
        list all block storage volumes.

        Returns:
            list of volume dictionaries
        """
        try:
            volumes = list(self._conn.block_storage.volumes())
            return [self._volume_to_dict(v) for v in volumes]
        except Exception as e:
            logger.error("Failed to list volumes: %s", e)
            return []

    def get_volume(self, volume_id: str) -> dict[str, Any] | None:
        """
        Get details for a specific volume.

        Args:
            volume_id: Volume UUID

        Returns:
            Volume details dict or None if not found
        """
        try:
            volume = self._conn.block_storage.get_volume(volume_id)
            return self._volume_to_dict(volume) if volume else None
        except Exception as e:
            logger.error("Failed to get volume %s: %s", volume_id, e)
            return None

    def create_volume(
        self,
        size: int,
        name: str,
        description: str | None = None,
        volume_type: str | None = None,
        availability_zone: str | None = None,
        snapshot_id: str | None = None,
        image_id: str | None = None,
        **kwargs,
    ) -> dict[str, Any] | None:
        """
        Create a new block storage volume.

        Args:
            size: Volume size in GB
            name: Volume name
            description: Optional description
            volume_type: Volume type (SSD, HDD, etc.)
            availability_zone: Target availability zone
            snapshot_id: Create from snapshot
            image_id: Create from image
            **kwargs: Additional Cinder create parameters

        Returns:
            Created volume dict or None on failure
        """
        try:
            volume = self._conn.block_storage.create_volume(
                size=size,
                name=name,
                description=description,
                volume_type=volume_type,
                availability_zone=availability_zone,
                snapshot_id=snapshot_id,
                image_id=image_id,
                **kwargs,
            )
            logger.info("Created volume: %s", volume.id)
            return self._volume_to_dict(volume)
        except Exception as e:
            logger.error("Failed to create volume %s: %s", name, e)
            return None

    def delete_volume(self, volume_id: str, force: bool = False) -> bool:
        """
        Delete a volume.

        Args:
            volume_id: Volume UUID
            force: Force delete even if attached

        Returns:
            True if successful
        """
        try:
            self._conn.block_storage.delete_volume(volume_id, force=force)
            logger.info("Deleted volume: %s", volume_id)
            return True
        except Exception as e:
            logger.error("Failed to delete volume %s: %s", volume_id, e)
            return False

    def extend_volume(self, volume_id: str, new_size: int) -> bool:
        """
        Extend a volume's size.

        Args:
            volume_id: Volume UUID
            new_size: New size in GB (must be larger than current)

        Returns:
            True if successful
        """
        try:
            self._conn.block_storage.extend_volume(volume_id, new_size)
            logger.info("Extended volume %s to %sGB", volume_id, new_size)
            return True
        except Exception as e:
            logger.error("Failed to extend volume %s: %s", volume_id, e)
            return False

    def attach_volume(
        self, volume_id: str, instance_id: str, device: str | None = None
    ) -> bool:
        """
        Attach a volume to an instance.

        Args:
            volume_id: Volume UUID
            instance_id: Instance UUID to attach to
            device: Device path (e.g., /dev/vdb) or None for auto

        Returns:
            True if successful
        """
        try:
            self._conn.compute.create_volume_attachment(
                server=instance_id, volume_id=volume_id, device=device
            )
            logger.info("Attached volume %s to %s", volume_id, instance_id)
            return True
        except Exception as e:
            logger.error("Failed to attach volume %s: %s", volume_id, e)
            return False

    def detach_volume(self, volume_id: str, instance_id: str) -> bool:
        """
        Detach a volume from an instance.

        Args:
            volume_id: Volume UUID
            instance_id: Instance UUID

        Returns:
            True if successful
        """
        try:
            # Find the attachment
            attachments = list(self._conn.compute.volume_attachments(instance_id))
            for attach in attachments:
                if attach.volume_id == volume_id:
                    self._conn.compute.delete_volume_attachment(
                        attach.id, server=instance_id
                    )
                    logger.info("Detached volume %s from %s", volume_id, instance_id)
                    return True
            logger.warning("Volume %s not attached to %s", volume_id, instance_id)
            return False
        except Exception as e:
            logger.error("Failed to detach volume %s: %s", volume_id, e)
            return False

    # =========================================================================
    # Backup Operations
    # =========================================================================

    def list_backups(self) -> list[dict[str, Any]]:
        """
        list volume backups.

        Returns:
            list of backup dictionaries
        """
        try:
            backups = list(self._conn.block_storage.backups())
            return [
                {
                    "id": b.id,
                    "name": b.name,
                    "status": b.status,
                    "volume_id": b.volume_id,
                    "size": b.size,
                    "created_at": str(b.created_at) if b.created_at else None,
                }
                for b in backups
            ]
        except Exception as e:
            logger.error("Failed to list backups: %s", e)
            return []

    def create_backup(
        self,
        volume_id: str,
        name: str,
        description: str | None = None,
        incremental: bool = False,
        force: bool = False,
    ) -> dict[str, Any] | None:
        """
        Create a backup of a volume.

        Args:
            volume_id: Volume UUID to backup
            name: Backup name
            description: Optional description
            incremental: Create incremental backup
            force: Force backup even if volume is in-use

        Returns:
            Created backup dict or None on failure
        """
        try:
            backup = self._conn.block_storage.create_backup(
                volume_id=volume_id,
                name=name,
                description=description,
                is_incremental=incremental,
                force=force,
            )
            logger.info("Created backup: %s", backup.id)
            return {
                "id": backup.id,
                "name": backup.name,
                "status": backup.status,
                "volume_id": backup.volume_id,
            }
        except Exception as e:
            logger.error("Failed to create backup for %s: %s", volume_id, e)
            return None

    def restore_backup(
        self, backup_id: str, volume_id: str | None = None, name: str | None = None
    ) -> dict[str, Any] | None:
        """
        Restore a backup to a new or existing volume.

        Args:
            backup_id: Backup UUID to restore
            volume_id: Optional existing volume to restore to
            name: Name for new volume (if volume_id not specified)

        Returns:
            Restored volume dict or None on failure
        """
        try:
            result = self._conn.block_storage.restore_backup(
                backup_id, volume_id=volume_id, name=name
            )
            logger.info("Restored backup %s", backup_id)
            return {"volume_id": result.volume_id}
        except Exception as e:
            logger.error("Failed to restore backup %s: %s", backup_id, e)
            return None

    def delete_backup(self, backup_id: str, force: bool = False) -> bool:
        """
        Delete a backup.

        Args:
            backup_id: Backup UUID
            force: Force delete

        Returns:
            True if successful
        """
        try:
            self._conn.block_storage.delete_backup(backup_id, force=force)
            logger.info("Deleted backup: %s", backup_id)
            return True
        except Exception as e:
            logger.error("Failed to delete backup %s: %s", backup_id, e)
            return False

    # =========================================================================
    # Snapshot Operations
    # =========================================================================

    def list_snapshots(self) -> list[dict[str, Any]]:
        """list volume snapshots."""
        try:
            snapshots = list(self._conn.block_storage.snapshots())
            return [
                {
                    "id": s.id,
                    "name": s.name,
                    "status": s.status,
                    "volume_id": s.volume_id,
                    "size": s.size,
                    "created_at": str(s.created_at) if s.created_at else None,
                }
                for s in snapshots
            ]
        except Exception as e:
            logger.error("Failed to list snapshots: %s", e)
            return []

    def create_snapshot(
        self,
        volume_id: str,
        name: str,
        description: str | None = None,
        force: bool = False,
    ) -> dict[str, Any] | None:
        """Create a volume snapshot."""
        try:
            snapshot = self._conn.block_storage.create_snapshot(
                volume_id=volume_id, name=name, description=description, force=force
            )
            logger.info("Created snapshot: %s", snapshot.id)
            return {
                "id": snapshot.id,
                "name": snapshot.name,
                "status": snapshot.status,
                "volume_id": snapshot.volume_id,
            }
        except Exception as e:
            logger.error("Failed to create snapshot for %s: %s", volume_id, e)
            return None

    def delete_snapshot(self, snapshot_id: str, force: bool = False) -> bool:
        """Delete a snapshot."""
        try:
            self._conn.block_storage.delete_snapshot(snapshot_id, force=force)
            logger.info("Deleted snapshot: %s", snapshot_id)
            return True
        except Exception as e:
            logger.error("Failed to delete snapshot %s: %s", snapshot_id, e)
            return False

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _volume_to_dict(self, volume: Any) -> dict[str, Any]:
        """Convert OpenStack volume object to dict."""
        return {
            "id": volume.id,
            "name": volume.name,
            "status": volume.status,
            "size": volume.size,
            "volume_type": volume.volume_type,
            "availability_zone": volume.availability_zone,
            "bootable": volume.is_bootable,
            "encrypted": volume.is_encrypted,
            "attachments": volume.attachments or [],
            "created_at": str(volume.created_at) if volume.created_at else None,
        }
