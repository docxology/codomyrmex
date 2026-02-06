"""
Infomaniak Metering Client.

Provides usage and billing data retrieval.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from ..base import InfomaniakOpenStackBase

logger = logging.getLogger(__name__)


class InfomaniakMeteringClient(InfomaniakOpenStackBase):
    """
    Client for Infomaniak metering and billing operations.

    Provides methods for retrieving resource usage and billing data.
    """

    _service_name = "metering"

    # =========================================================================
    # Resource Usage
    # =========================================================================

    def get_compute_usage(
        self,
        start: datetime | None = None,
        end: datetime | None = None
    ) -> dict[str, Any]:
        """
        Get compute resource usage summary.

        Args:
            start: Start datetime (defaults to current month start)
            end: End datetime (defaults to now)
        """
        try:
            # List all instances and sum up resources
            servers = list(self._conn.compute.servers(all_projects=False))

            total_vcpus = 0
            total_ram_mb = 0
            total_disk_gb = 0
            instance_count = len(servers)

            for server in servers:
                if server.flavor:
                    flavor = self._conn.compute.get_flavor(server.flavor.get("id"))
                    if flavor:
                        total_vcpus += flavor.vcpus
                        total_ram_mb += flavor.ram
                        total_disk_gb += flavor.disk

            return {
                "instance_count": instance_count,
                "total_vcpus": total_vcpus,
                "total_ram_mb": total_ram_mb,
                "total_ram_gb": total_ram_mb / 1024 if total_ram_mb else 0,
                "total_disk_gb": total_disk_gb,
                "period_start": start.isoformat() if start else None,
                "period_end": end.isoformat() if end else None,
            }
        except Exception as e:
            logger.error(f"Failed to get compute usage: {e}")
            return {}

    def get_storage_usage(self) -> dict[str, Any]:
        """Get block storage usage summary."""
        try:
            volumes = list(self._conn.block_storage.volumes())

            total_size_gb = sum(v.size for v in volumes)
            attached_count = sum(1 for v in volumes if v.attachments)

            return {
                "volume_count": len(volumes),
                "total_size_gb": total_size_gb,
                "attached_count": attached_count,
                "unattached_count": len(volumes) - attached_count,
            }
        except Exception as e:
            logger.error(f"Failed to get storage usage: {e}")
            return {}

    def get_network_usage(self) -> dict[str, Any]:
        """Get network resource usage summary."""
        try:
            networks = list(self._conn.network.networks())
            routers = list(self._conn.network.routers())
            security_groups = list(self._conn.network.security_groups())
            floating_ips = list(self._conn.network.ips())

            return {
                "network_count": len(networks),
                "router_count": len(routers),
                "security_group_count": len(security_groups),
                "floating_ip_count": len(floating_ips),
                "floating_ips_in_use": sum(1 for fip in floating_ips if fip.port_id),
            }
        except Exception as e:
            logger.error(f"Failed to get network usage: {e}")
            return {}

    def get_object_storage_usage(self) -> dict[str, Any]:
        """Get object storage usage summary."""
        try:
            containers = list(self._conn.object_store.containers())

            total_objects = 0
            total_bytes = 0

            for container in containers:
                total_objects += container.count or 0
                total_bytes += container.bytes or 0

            return {
                "container_count": len(containers),
                "object_count": total_objects,
                "total_bytes": total_bytes,
                "total_size_gb": total_bytes / (1024**3) if total_bytes else 0,
            }
        except Exception as e:
            logger.error(f"Failed to get object storage usage: {e}")
            return {}

    def get_all_usage(self) -> dict[str, Any]:
        """Get comprehensive usage summary across all services."""
        return {
            "compute": self.get_compute_usage(),
            "storage": self.get_storage_usage(),
            "network": self.get_network_usage(),
            "object_storage": self.get_object_storage_usage(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # =========================================================================
    # Resource Listing with Usage
    # =========================================================================

    def list_resources_with_usage(self) -> list[dict[str, Any]]:
        """List all resources with their current usage metrics."""
        resources = []

        # Compute instances
        try:
            for server in self._conn.compute.servers():
                resources.append({
                    "type": "compute.instance",
                    "id": server.id,
                    "name": server.name,
                    "status": server.status,
                    "created": str(server.created_at) if server.created_at else None,
                })
        except Exception as e:
            logger.warning(f"Failed to list compute instances: {e}")

        # Volumes
        try:
            for volume in self._conn.block_storage.volumes():
                resources.append({
                    "type": "storage.volume",
                    "id": volume.id,
                    "name": volume.name,
                    "status": volume.status,
                    "size_gb": volume.size,
                })
        except Exception as e:
            logger.warning(f"Failed to list volumes: {e}")

        # Floating IPs
        try:
            for fip in self._conn.network.ips():
                resources.append({
                    "type": "network.floating_ip",
                    "id": fip.id,
                    "address": fip.floating_ip_address,
                    "status": fip.status,
                    "in_use": bool(fip.port_id),
                })
        except Exception as e:
            logger.warning(f"Failed to list floating IPs: {e}")

        return resources

    # =========================================================================
    # Quotas
    # =========================================================================

    def get_compute_quotas(self) -> dict[str, Any]:
        """Get compute quotas for the current project."""
        try:
            project_id = self._conn.current_project_id
            quotas = self._conn.compute.get_quota_set(project_id)
            return {
                "instances": quotas.instances,
                "cores": quotas.cores,
                "ram_mb": quotas.ram,
                "key_pairs": quotas.key_pairs,
                "server_groups": quotas.server_groups,
            }
        except Exception as e:
            logger.error(f"Failed to get compute quotas: {e}")
            return {}

    def get_network_quotas(self) -> dict[str, Any]:
        """Get network quotas for the current project."""
        try:
            project_id = self._conn.current_project_id
            quotas = self._conn.network.get_quota(project_id)
            return {
                "networks": quotas.networks,
                "subnets": quotas.subnets,
                "routers": quotas.routers,
                "floating_ips": quotas.floatingips,
                "security_groups": quotas.security_groups,
                "security_group_rules": quotas.security_group_rules,
            }
        except Exception as e:
            logger.error(f"Failed to get network quotas: {e}")
            return {}

    def get_storage_quotas(self) -> dict[str, Any]:
        """Get block storage quotas for the current project."""
        try:
            project_id = self._conn.current_project_id
            quotas = self._conn.block_storage.get_quota_set(project_id)
            return {
                "volumes": quotas.volumes,
                "gigabytes": quotas.gigabytes,
                "snapshots": quotas.snapshots,
                "backups": quotas.backups,
            }
        except Exception as e:
            logger.error(f"Failed to get storage quotas: {e}")
            return {}
