"""Mixin for Infomaniak security group operations."""

from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class SecurityGroupMixin:
    """Security group CRUD and rule management.

    Requires ``_conn`` from the base class.
    """

    def list_security_groups(self) -> list[dict[str, Any]]:
        """list all security groups."""
        try:
            sgs = list(self._conn.network.security_groups())
            return [
                {
                    "id": sg.id,
                    "name": sg.name,
                    "description": sg.description,
                    "rules_count": len(sg.security_group_rules or []),
                }
                for sg in sgs
            ]
        except Exception as e:
            logger.error("Failed to list security groups: %s", e)
            return []

    def create_security_group(
        self, name: str, description: str | None = None
    ) -> dict[str, Any] | None:
        """Create a security group."""
        try:
            sg = self._conn.network.create_security_group(
                name=name, description=description or ""
            )
            logger.info("Created security group: %s", sg.id)
            return {"id": sg.id, "name": sg.name}
        except Exception as e:
            logger.error("Failed to create security group %s: %s", name, e)
            return None

    def add_security_group_rule(
        self,
        security_group_id: str,
        direction: str = "ingress",
        protocol: str | None = None,
        port_range_min: int | None = None,
        port_range_max: int | None = None,
        remote_ip_prefix: str | None = None,
        ethertype: str = "IPv4",
        **kwargs,
    ) -> dict[str, Any] | None:
        """Add a rule to a security group.

        Args:
            security_group_id: Target security group.
            direction: "ingress" or "egress".
            protocol: "tcp", "udp", "icmp", or None for all.
            port_range_min: Starting port (None for all).
            port_range_max: Ending port (None for all).
            remote_ip_prefix: CIDR for allowed IPs (e.g., "0.0.0.0/0").
            ethertype: "IPv4" or "IPv6".
        """
        try:
            rule = self._conn.network.create_security_group_rule(
                security_group_id=security_group_id,
                direction=direction,
                protocol=protocol,
                port_range_min=port_range_min,
                port_range_max=port_range_max,
                remote_ip_prefix=remote_ip_prefix,
                ether_type=ethertype,
                **kwargs,
            )
            logger.info("Created security group rule: %s", rule.id)
            return {"id": rule.id, "direction": direction, "protocol": protocol}
        except Exception as e:
            logger.error("Failed to add rule to %s: %s", security_group_id, e)
            return None

    def delete_security_group(self, security_group_id: str) -> bool:
        """Delete a security group."""
        try:
            self._conn.network.delete_security_group(security_group_id)
            logger.info("Deleted security group: %s", security_group_id)
            return True
        except Exception as e:
            logger.error("Failed to delete security group %s: %s", security_group_id, e)
            return False
