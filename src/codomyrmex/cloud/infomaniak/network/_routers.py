"""Mixin for Infomaniak router operations."""

from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class RouterMixin:
    """Router CRUD and interface management.

    Requires ``_conn`` from the base class.
    """

    def list_routers(self) -> list[dict[str, Any]]:
        """List all routers."""
        try:
            routers = list(self._conn.network.routers())
            return [
                {
                    "id": r.id,
                    "name": r.name,
                    "status": r.status,
                    "external_gateway": r.external_gateway_info,
                }
                for r in routers
            ]
        except Exception as e:
            logger.error("Failed to list routers: %s", e)
            return []

    def create_router(
        self, name: str, external_network: str | None = None, **kwargs
    ) -> dict[str, Any] | None:
        """Create a router with optional external gateway."""
        try:
            router_args = {"name": name, **kwargs}

            if external_network:
                ext_net = self._conn.network.find_network(external_network)
                if ext_net:
                    router_args["external_gateway_info"] = {"network_id": ext_net.id}

            router = self._conn.network.create_router(**router_args)
            logger.info("Created router: %s", router.id)
            return {"id": router.id, "name": router.name}
        except Exception as e:
            logger.error("Failed to create router %s: %s", name, e)
            return None

    def add_router_interface(self, router_id: str, subnet_id: str) -> bool:
        """Add a subnet interface to a router."""
        try:
            self._conn.network.add_interface_to_router(router_id, subnet_id=subnet_id)
            logger.info("Added interface for subnet %s to router %s", subnet_id, router_id)
            return True
        except Exception as e:
            logger.error("Failed to add interface to router %s: %s", router_id, e)
            return False

    def remove_router_interface(self, router_id: str, subnet_id: str) -> bool:
        """Remove a subnet interface from a router."""
        try:
            self._conn.network.remove_interface_from_router(
                router_id, subnet_id=subnet_id
            )
            logger.info(
                "Removed interface for subnet %s from router %s", subnet_id, router_id
            )
            return True
        except Exception as e:
            logger.error("Failed to remove interface from router %s: %s", router_id, e)
            return False

    def delete_router(self, router_id: str) -> bool:
        """Delete a router."""
        try:
            self._conn.network.delete_router(router_id)
            logger.info("Deleted router: %s", router_id)
            return True
        except Exception as e:
            logger.error("Failed to delete router %s: %s", router_id, e)
            return False
