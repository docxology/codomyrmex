"""Mixin for Infomaniak floating IP operations."""

from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class FloatingIPMixin:
    """Floating IP allocation, association, and release.

    Requires ``_conn`` from the base class.
    """

    def list_floating_ips(self) -> list[dict[str, Any]]:
        """List all floating IPs."""
        try:
            fips = list(self._conn.network.ips())
            return [
                {
                    "id": fip.id,
                    "floating_ip_address": fip.floating_ip_address,
                    "fixed_ip_address": fip.fixed_ip_address,
                    "status": fip.status,
                    "port_id": fip.port_id,
                }
                for fip in fips
            ]
        except Exception as e:
            logger.error("Failed to list floating IPs: %s", e)
            return []

    def allocate_floating_ip(self, external_network: str) -> dict[str, Any] | None:
        """Allocate a floating IP from an external network."""
        try:
            ext_net = self._conn.network.find_network(external_network)
            if not ext_net:
                logger.error("External network not found: %s", external_network)
                return None

            fip = self._conn.network.create_ip(floating_network_id=ext_net.id)
            logger.info("Allocated floating IP: %s", fip.floating_ip_address)
            return {"id": fip.id, "floating_ip_address": fip.floating_ip_address}
        except Exception as e:
            logger.error("Failed to allocate floating IP: %s", e)
            return None

    def associate_floating_ip(self, floating_ip_id: str, port_id: str) -> bool:
        """Associate a floating IP with a port."""
        try:
            self._conn.network.update_ip(floating_ip_id, port_id=port_id)
            logger.info("Associated floating IP %s with port %s", floating_ip_id, port_id)
            return True
        except Exception as e:
            logger.error("Failed to associate floating IP: %s", e)
            return False

    def release_floating_ip(self, floating_ip_id: str) -> bool:
        """Release (delete/deallocate) a floating IP."""
        try:
            self._conn.network.delete_ip(floating_ip_id)
            logger.info("Released floating IP: %s", floating_ip_id)
            return True
        except Exception as e:
            logger.error("Failed to release floating IP %s: %s", floating_ip_id, e)
            return False

    def disassociate_floating_ip(self, floating_ip_id: str) -> bool:
        """Disassociate a floating IP from its port."""
        try:
            self._conn.network.update_ip(floating_ip_id, port_id=None)
            logger.info("Disassociated floating IP: %s", floating_ip_id)
            return True
        except Exception as e:
            logger.error("Failed to disassociate floating IP %s: %s", floating_ip_id, e)
            return False
