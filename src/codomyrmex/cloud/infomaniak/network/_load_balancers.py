"""Mixin for Infomaniak Octavia load balancer operations."""

from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class LoadBalancerMixin:
    """Load balancer, listener, pool, member, and health monitor operations.

    Requires ``_conn`` from the base class.
    """

    # =========================================================================
    # Load Balancer CRUD
    # =========================================================================

    def list_loadbalancers(self) -> list[dict[str, Any]]:
        """List all load balancers."""
        try:
            lbs = list(self._conn.load_balancer.load_balancers())
            return [
                {
                    "id": lb.id,
                    "name": lb.name,
                    "vip_address": lb.vip_address,
                    "operating_status": lb.operating_status,
                    "provisioning_status": lb.provisioning_status,
                }
                for lb in lbs
            ]
        except Exception as e:
            logger.error("Failed to list load balancers: %s", e)
            return []

    def create_loadbalancer(
        self, name: str, subnet_id: str, vip_address: str | None = None, **kwargs
    ) -> dict[str, Any] | None:
        """Create a load balancer."""
        try:
            lb = self._conn.load_balancer.create_load_balancer(
                name=name, vip_subnet_id=subnet_id, vip_address=vip_address, **kwargs
            )
            logger.info("Created load balancer: %s", lb.id)
            return {"id": lb.id, "name": lb.name, "vip_address": lb.vip_address}
        except Exception as e:
            logger.error("Failed to create load balancer %s: %s", name, e)
            return None

    def delete_loadbalancer(self, loadbalancer_id: str, cascade: bool = False) -> bool:
        """Delete a load balancer."""
        try:
            self._conn.load_balancer.delete_load_balancer(
                loadbalancer_id, cascade=cascade
            )
            logger.info("Deleted load balancer: %s", loadbalancer_id)
            return True
        except Exception as e:
            logger.error("Failed to delete load balancer %s: %s", loadbalancer_id, e)
            return False

    # =========================================================================
    # Listener Operations
    # =========================================================================

    def list_listeners(
        self, loadbalancer_id: str | None = None
    ) -> list[dict[str, Any]]:
        """List listeners, optionally filtered by load balancer."""
        try:
            kwargs = {}
            if loadbalancer_id:
                kwargs["loadbalancer_id"] = loadbalancer_id
            listeners = list(self._conn.load_balancer.listeners(**kwargs))
            return [
                {
                    "id": listener.id,
                    "name": listener.name,
                    "protocol": listener.protocol,
                    "protocol_port": listener.protocol_port,
                    "loadbalancer_id": getattr(listener, "loadbalancer_id", None),
                }
                for listener in listeners
            ]
        except Exception as e:
            logger.error("Failed to list listeners: %s", e)
            return []

    def create_listener(
        self, loadbalancer_id: str, name: str, protocol: str, port: int, **kwargs
    ) -> dict[str, Any] | None:
        """Create a listener on a load balancer."""
        try:
            listener = self._conn.load_balancer.create_listener(
                loadbalancer_id=loadbalancer_id,
                name=name,
                protocol=protocol,
                protocol_port=port,
                **kwargs,
            )
            logger.info("Created listener: %s", listener.id)
            return {"id": listener.id, "name": listener.name, "protocol": protocol}
        except Exception as e:
            logger.error("Failed to create listener %s: %s", name, e)
            return None

    def delete_listener(self, listener_id: str) -> bool:
        """Delete a listener."""
        try:
            self._conn.load_balancer.delete_listener(listener_id)
            logger.info("Deleted listener: %s", listener_id)
            return True
        except Exception as e:
            logger.error("Failed to delete listener %s: %s", listener_id, e)
            return False

    # =========================================================================
    # Pool Operations
    # =========================================================================

    def list_pools(self, loadbalancer_id: str | None = None) -> list[dict[str, Any]]:
        """List pools, optionally filtered by load balancer."""
        try:
            kwargs = {}
            if loadbalancer_id:
                kwargs["loadbalancer_id"] = loadbalancer_id
            pools = list(self._conn.load_balancer.pools(**kwargs))
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "protocol": p.protocol,
                    "lb_algorithm": p.lb_algorithm,
                }
                for p in pools
            ]
        except Exception as e:
            logger.error("Failed to list pools: %s", e)
            return []

    def create_pool(
        self,
        name: str,
        protocol: str,
        lb_algorithm: str,
        listener_id: str | None = None,
        loadbalancer_id: str | None = None,
        **kwargs,
    ) -> dict[str, Any] | None:
        """Create a pool."""
        try:
            pool = self._conn.load_balancer.create_pool(
                name=name,
                protocol=protocol,
                lb_algorithm=lb_algorithm,
                listener_id=listener_id,
                loadbalancer_id=loadbalancer_id,
                **kwargs,
            )
            logger.info("Created pool: %s", pool.id)
            return {"id": pool.id, "name": pool.name, "protocol": protocol}
        except Exception as e:
            logger.error("Failed to create pool %s: %s", name, e)
            return None

    def delete_pool(self, pool_id: str) -> bool:
        """Delete a pool."""
        try:
            self._conn.load_balancer.delete_pool(pool_id)
            logger.info("Deleted pool: %s", pool_id)
            return True
        except Exception as e:
            logger.error("Failed to delete pool %s: %s", pool_id, e)
            return False

    # =========================================================================
    # Pool Member Operations
    # =========================================================================

    def list_pool_members(self, pool_id: str) -> list[dict[str, Any]]:
        """List members in a pool."""
        try:
            members = list(self._conn.load_balancer.members(pool_id))
            return [
                {
                    "id": m.id,
                    "name": m.name,
                    "address": m.address,
                    "protocol_port": m.protocol_port,
                    "weight": m.weight,
                    "operating_status": getattr(m, "operating_status", None),
                }
                for m in members
            ]
        except Exception as e:
            logger.error("Failed to list pool members for %s: %s", pool_id, e)
            return []

    def add_pool_member(
        self,
        pool_id: str,
        address: str,
        port: int,
        weight: int = 1,
        name: str | None = None,
        subnet_id: str | None = None,
        **kwargs,
    ) -> dict[str, Any] | None:
        """Add a member to a pool."""
        try:
            member = self._conn.load_balancer.create_member(
                pool_id,
                address=address,
                protocol_port=port,
                weight=weight,
                name=name,
                subnet_id=subnet_id,
                **kwargs,
            )
            logger.info("Added pool member: %s", member.id)
            return {"id": member.id, "address": address, "port": port}
        except Exception as e:
            logger.error("Failed to add member to pool %s: %s", pool_id, e)
            return None

    def remove_pool_member(self, pool_id: str, member_id: str) -> bool:
        """Remove a member from a pool."""
        try:
            self._conn.load_balancer.delete_member(member_id, pool_id)
            logger.info("Removed pool member: %s", member_id)
            return True
        except Exception as e:
            logger.error(
                "Failed to remove member %s from pool %s: %s", member_id, pool_id, e
            )
            return False

    # =========================================================================
    # Health Monitor Operations
    # =========================================================================

    def list_health_monitors(self, pool_id: str | None = None) -> list[dict[str, Any]]:
        """List health monitors, optionally filtered by pool."""
        try:
            kwargs = {}
            if pool_id:
                kwargs["pool_id"] = pool_id
            monitors = list(self._conn.load_balancer.health_monitors(**kwargs))
            return [
                {
                    "id": hm.id,
                    "name": hm.name,
                    "type": hm.type,
                    "delay": hm.delay,
                    "timeout": hm.timeout,
                    "max_retries": hm.max_retries,
                    "pool_id": getattr(hm, "pool_id", None),
                }
                for hm in monitors
            ]
        except Exception as e:
            logger.error("Failed to list health monitors: %s", e)
            return []

    def create_health_monitor(
        self,
        pool_id: str,
        monitor_type: str,
        delay: int,
        timeout: int,
        max_retries: int = 3,
        name: str | None = None,
        **kwargs,
    ) -> dict[str, Any] | None:
        """Create a health monitor for a pool.

        Args:
            pool_id: Pool to monitor.
            monitor_type: Monitor type (HTTP, HTTPS, PING, TCP, etc.).
            delay: Delay between checks in seconds.
            timeout: Timeout for each check in seconds.
            max_retries: Max retries before marking member down.
            name: Optional monitor name.
        """
        try:
            hm = self._conn.load_balancer.create_health_monitor(
                pool_id=pool_id,
                type=monitor_type,
                delay=delay,
                timeout=timeout,
                max_retries=max_retries,
                name=name,
                **kwargs,
            )
            logger.info("Created health monitor: %s", hm.id)
            return {"id": hm.id, "type": monitor_type, "pool_id": pool_id}
        except Exception as e:
            logger.error("Failed to create health monitor for pool %s: %s", pool_id, e)
            return None

    def delete_health_monitor(self, health_monitor_id: str) -> bool:
        """Delete a health monitor."""
        try:
            self._conn.load_balancer.delete_health_monitor(health_monitor_id)
            logger.info("Deleted health monitor: %s", health_monitor_id)
            return True
        except Exception as e:
            logger.error("Failed to delete health monitor %s: %s", health_monitor_id, e)
            return False
