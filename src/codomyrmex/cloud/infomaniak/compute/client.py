"""
Infomaniak Compute Client (Nova).

Provides instance, image, keypair, and availability zone operations
via the OpenStack Nova API.
"""

from typing import Any

from codomyrmex.cloud.common import ComputeClient
from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class InfomaniakComputeClient(InfomaniakOpenStackBase, ComputeClient):
    """
    Client for Infomaniak compute (Nova) operations.

    Provides methods for managing instances, images, keypairs,
    and availability zones.

    Usage:
        from codomyrmex.cloud.infomaniak import InfomaniakComputeClient

        client = InfomaniakComputeClient.from_env()
        instances = client.list_instances()
    """

    _service_name = "compute"

    # =========================================================================
    # Instance Operations
    # =========================================================================

    def list_instances(self) -> list[dict[str, Any]]:
        """
        list all compute instances.

        Returns:
            list of instance dictionaries with id, name, status, etc.
        """
        try:
            servers = list(self._conn.compute.servers())
            return [self._server_to_dict(s) for s in servers]
        except Exception as e:
            logger.error("Failed to list instances: %s", e)
            return []

    def get_instance(self, instance_id: str) -> dict[str, Any] | None:
        """
        Get details for a specific instance.

        Args:
            instance_id: Instance UUID

        Returns:
            Instance details dict or None if not found
        """
        try:
            server = self._conn.compute.get_server(instance_id)
            return self._server_to_dict(server) if server else None
        except Exception as e:
            logger.error("Failed to get instance %s: %s", instance_id, e)
            return None

    def create_instance(  # type: ignore
        self,
        name: str,
        flavor: str,
        image: str,
        network: str,
        key_name: str | None = None,
        security_groups: list[str] | None = None,
        user_data: str | None = None,
        availability_zone: str | None = None,
        **kwargs,
    ) -> dict[str, Any] | None:
        """
        Create a new compute instance.

        Args:
            name: Instance name
            flavor: Flavor name or ID
            image: Image name or ID
            network: Network name or ID
            key_name: SSH key pair name
            security_groups: list of security group names
            user_data: Cloud-init user data script
            availability_zone: Target availability zone
            **kwargs: Additional Nova create parameters

        Returns:
            Created instance dict or None on failure
        """
        try:
            # Resolve flavor
            flavor_obj = self._conn.compute.find_flavor(flavor)
            if not flavor_obj:
                logger.error("Flavor not found: %s", flavor)
                return None

            # Resolve image
            image_obj = self._conn.image.find_image(image)
            if not image_obj:
                logger.error("Image not found: %s", image)
                return None

            # Resolve network
            network_obj = self._conn.network.find_network(network)
            if not network_obj:
                logger.error("Network not found: %s", network)
                return None

            server = self._conn.compute.create_server(
                name=name,
                flavor_id=flavor_obj.id,
                image_id=image_obj.id,
                networks=[{"uuid": network_obj.id}],
                key_name=key_name,
                security_groups=security_groups or [],
                user_data=user_data,
                availability_zone=availability_zone,
                **kwargs,
            )

            # Wait for server to be active
            server = self._conn.compute.wait_for_server(server)
            logger.info("Created instance: %s", server.id)
            return self._server_to_dict(server)

        except Exception as e:
            logger.error("Failed to create instance %s: %s", name, e)
            return None

    def start_instance(self, instance_id: str) -> bool:
        """
        Start a stopped instance.

        Args:
            instance_id: Instance UUID

        Returns:
            True if successful
        """
        try:
            self._conn.compute.start_server(instance_id)
            logger.info("Started instance: %s", instance_id)
            return True
        except Exception as e:
            logger.error("Failed to start instance %s: %s", instance_id, e)
            return False

    def stop_instance(self, instance_id: str) -> bool:
        """
        Stop a running instance.

        Args:
            instance_id: Instance UUID

        Returns:
            True if successful
        """
        try:
            self._conn.compute.stop_server(instance_id)
            logger.info("Stopped instance: %s", instance_id)
            return True
        except Exception as e:
            logger.error("Failed to stop instance %s: %s", instance_id, e)
            return False

    def reboot_instance(self, instance_id: str, reboot_type: str = "SOFT") -> bool:
        """
        Reboot an instance.

        Args:
            instance_id: Instance UUID
            reboot_type: "SOFT" or "HARD"

        Returns:
            True if successful
        """
        try:
            self._conn.compute.reboot_server(instance_id, reboot_type)
            logger.info("Rebooted instance: %s (%s)", instance_id, reboot_type)
            return True
        except Exception as e:
            logger.error("Failed to reboot instance %s: %s", instance_id, e)
            return False

    def delete_instance(self, instance_id: str, force: bool = False) -> bool:
        """
        Delete an instance.

        Args:
            instance_id: Instance UUID
            force: Force delete even if running

        Returns:
            True if successful
        """
        try:
            self._conn.compute.delete_server(instance_id, force=force)
            logger.info("Deleted instance: %s", instance_id)
            return True
        except Exception as e:
            logger.error("Failed to delete instance %s: %s", instance_id, e)
            return False

    def terminate_instance(self, instance_id: str) -> bool:
        """
        Terminate (delete) an instance. ABC-compatible alias for delete_instance.

        Args:
            instance_id: Instance UUID

        Returns:
            True if successful
        """
        return self.delete_instance(instance_id, force=True)

    # =========================================================================
    # Image Operations
    # =========================================================================

    def list_images(self) -> list[dict[str, Any]]:
        """
        list available images.

        Returns:
            list of image dictionaries
        """
        try:
            images = list(self._conn.image.images())
            return [
                {
                    "id": img.id,
                    "name": img.name,
                    "status": img.status,
                    "min_disk": img.min_disk,
                    "min_ram": img.min_ram,
                    "size": img.size,
                    "created_at": str(img.created_at) if img.created_at else None,
                }
                for img in images
            ]
        except Exception as e:
            logger.error("Failed to list images: %s", e)
            return []

    def get_image(self, image_id: str) -> dict[str, Any] | None:
        """Get image details by ID or name."""
        try:
            image = self._conn.image.find_image(image_id)
            if image:
                return {
                    "id": image.id,
                    "name": image.name,
                    "status": image.status,
                    "min_disk": image.min_disk,
                    "min_ram": image.min_ram,
                    "size": image.size,
                }
            return None
        except Exception as e:
            logger.error("Failed to get image %s: %s", image_id, e)
            return None

    # =========================================================================
    # Flavor Operations
    # =========================================================================

    def list_flavors(self) -> list[dict[str, Any]]:
        """
        list available flavors (instance types).

        Returns:
            list of flavor dictionaries
        """
        try:
            flavors = list(self._conn.compute.flavors())
            return [
                {
                    "id": f.id,
                    "name": f.name,
                    "vcpus": f.vcpus,
                    "ram": f.ram,
                    "disk": f.disk,
                    "is_public": f.is_public,
                }
                for f in flavors
            ]
        except Exception as e:
            logger.error("Failed to list flavors: %s", e)
            return []

    # =========================================================================
    # Key Pair Operations
    # =========================================================================

    def list_keypairs(self) -> list[dict[str, Any]]:
        """
        list SSH key pairs.

        Returns:
            list of keypair dictionaries
        """
        try:
            keypairs = list(self._conn.compute.keypairs())
            return [
                {
                    "name": kp.name,
                    "fingerprint": kp.fingerprint,
                    "type": getattr(kp, "type", "ssh"),
                }
                for kp in keypairs
            ]
        except Exception as e:
            logger.error("Failed to list keypairs: %s", e)
            return []

    def create_keypair(
        self, name: str, public_key: str | None = None
    ) -> dict[str, Any] | None:
        """
        Create or import an SSH key pair.

        Args:
            name: Key pair name
            public_key: Public key to import (if None, generates new pair)

        Returns:
            Keypair dict (includes private_key if generated)
        """
        try:
            keypair = self._conn.compute.create_keypair(
                name=name, public_key=public_key
            )
            result = {
                "name": keypair.name,
                "fingerprint": keypair.fingerprint,
                "public_key": keypair.public_key,
            }
            # Include private key if it was generated
            if hasattr(keypair, "private_key") and keypair.private_key:
                result["private_key"] = keypair.private_key

            logger.info("Created keypair: %s", name)
            return result
        except Exception as e:
            logger.error("Failed to create keypair %s: %s", name, e)
            return None

    def delete_keypair(self, name: str) -> bool:
        """
        Delete an SSH key pair.

        Args:
            name: Key pair name

        Returns:
            True if successful
        """
        try:
            self._conn.compute.delete_keypair(name)
            logger.info("Deleted keypair: %s", name)
            return True
        except Exception as e:
            logger.error("Failed to delete keypair %s: %s", name, e)
            return False

    # =========================================================================
    # Availability Zone Operations
    # =========================================================================

    def list_availability_zones(self) -> list[dict[str, Any]]:
        """
        list availability zones.

        Returns:
            list of availability zone dictionaries
        """
        try:
            zones = list(self._conn.compute.availability_zones())
            return [
                {
                    "name": zone.name,
                    "state": getattr(zone, "state", {}).get("available", True),
                }
                for zone in zones
            ]
        except Exception as e:
            logger.error("Failed to list availability zones: %s", e)
            return []

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _server_to_dict(self, server: Any) -> dict[str, Any]:
        """Convert OpenStack server object to dict."""
        return {
            "id": server.id,
            "name": server.name,
            "status": server.status,
            "flavor": (getattr(server, "flavor", None) or {}).get("id"),
            "image": getattr(server, "image", {}).get("id") if server.image else None,
            "addresses": dict(server.addresses) if server.addresses else {},
            "key_name": server.key_name,
            "created_at": str(server.created_at) if server.created_at else None,
            "updated_at": str(server.updated_at) if server.updated_at else None,
            "availability_zone": getattr(server, "availability_zone", None),
            "security_groups": [
                sg.get("name") for sg in (server.security_groups or [])
            ],
        }
