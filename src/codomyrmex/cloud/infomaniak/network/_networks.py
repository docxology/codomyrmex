"""Mixin for Infomaniak network and subnet operations."""

from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class NetworkSubnetMixin:
    """Network and subnet CRUD operations.

    Requires ``_conn`` and ``_safe_call`` from the base class.
    """

    def list_networks(self) -> list[dict[str, Any]]:
        """List all networks."""

        def _op():
            return [
                {
                    "id": n.id,
                    "name": n.name,
                    "status": n.status,
                    "is_shared": n.is_shared,
                    "is_external": n.is_router_external,
                    "subnets": n.subnet_ids or [],
                }
                for n in self._conn.network.networks()
            ]

        return self._safe_call(_op, "list", "networks", default=[])

    def create_network(
        self,
        name: str,
        description: str | None = None,
        is_shared: bool = False,
        **kwargs,
    ) -> dict[str, Any] | None:
        """Create a new network."""

        def _op():
            network = self._conn.network.create_network(
                name=name, description=description, is_shared=is_shared, **kwargs
            )
            logger.info("Created network: %s", network.id)
            return {"id": network.id, "name": network.name}

        return self._safe_call(_op, "create", f"network {name}")

    def delete_network(self, network_id: str) -> bool:
        """Delete a network."""

        def _op():
            self._conn.network.delete_network(network_id)
            logger.info("Deleted network: %s", network_id)
            return True

        return self._safe_call(_op, "delete", f"network {network_id}", default=False)

    def create_subnet(
        self,
        network_id: str,
        name: str,
        cidr: str,
        ip_version: int = 4,
        gateway_ip: str | None = None,
        enable_dhcp: bool = True,
        dns_nameservers: list[str] | None = None,
        **kwargs,
    ) -> dict[str, Any] | None:
        """Create a subnet in a network."""
        try:
            subnet = self._conn.network.create_subnet(
                network_id=network_id,
                name=name,
                cidr=cidr,
                ip_version=ip_version,
                gateway_ip=gateway_ip,
                is_dhcp_enabled=enable_dhcp,
                dns_nameservers=dns_nameservers or [],
                **kwargs,
            )
            logger.info("Created subnet: %s", subnet.id)
            return {"id": subnet.id, "name": subnet.name, "cidr": subnet.cidr}
        except Exception as e:
            logger.error("Failed to create subnet %s: %s", name, e)
            return None

    def list_subnets(self) -> list[dict[str, Any]]:
        """List all subnets."""
        try:
            subnets = list(self._conn.network.subnets())
            return [
                {
                    "id": s.id,
                    "name": s.name,
                    "network_id": s.network_id,
                    "cidr": s.cidr,
                    "ip_version": s.ip_version,
                    "gateway_ip": s.gateway_ip,
                    "is_dhcp_enabled": s.is_dhcp_enabled,
                }
                for s in subnets
            ]
        except Exception as e:
            logger.error("Failed to list subnets: %s", e)
            return []

    def get_subnet(self, subnet_id: str) -> dict[str, Any] | None:
        """Get a specific subnet by ID."""
        try:
            subnet = self._conn.network.get_subnet(subnet_id)
            if subnet:
                return {
                    "id": subnet.id,
                    "name": subnet.name,
                    "network_id": subnet.network_id,
                    "cidr": subnet.cidr,
                    "ip_version": subnet.ip_version,
                    "gateway_ip": subnet.gateway_ip,
                }
            return None
        except Exception as e:
            logger.error("Failed to get subnet %s: %s", subnet_id, e)
            return None

    def delete_subnet(self, subnet_id: str) -> bool:
        """Delete a subnet."""
        try:
            self._conn.network.delete_subnet(subnet_id)
            logger.info("Deleted subnet: %s", subnet_id)
            return True
        except Exception as e:
            logger.error("Failed to delete subnet %s: %s", subnet_id, e)
            return False
