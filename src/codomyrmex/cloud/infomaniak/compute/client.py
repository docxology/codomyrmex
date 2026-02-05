"""
Infomaniak Compute Client (Nova).

Provides instance, image, keypair, and availability zone operations
via the OpenStack Nova API.
"""

from typing import Any, Dict, List, Optional
import logging

from ..base import InfomaniakOpenStackBase
from ...common import ComputeClient

logger = logging.getLogger(__name__)


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
    
    def list_instances(self) -> List[Dict[str, Any]]:
        """
        List all compute instances.
        
        Returns:
            List of instance dictionaries with id, name, status, etc.
        """
        try:
            servers = list(self._conn.compute.servers())
            return [self._server_to_dict(s) for s in servers]
        except Exception as e:
            logger.error(f"Failed to list instances: {e}")
            return []
    
    def get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
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
            logger.error(f"Failed to get instance {instance_id}: {e}")
            return None
    
    def create_instance(
        self,
        name: str,
        flavor: str,
        image: str,
        network: str,
        key_name: Optional[str] = None,
        security_groups: Optional[List[str]] = None,
        user_data: Optional[str] = None,
        availability_zone: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new compute instance.
        
        Args:
            name: Instance name
            flavor: Flavor name or ID
            image: Image name or ID
            network: Network name or ID
            key_name: SSH key pair name
            security_groups: List of security group names
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
                logger.error(f"Flavor not found: {flavor}")
                return None
            
            # Resolve image
            image_obj = self._conn.image.find_image(image)
            if not image_obj:
                logger.error(f"Image not found: {image}")
                return None
            
            # Resolve network
            network_obj = self._conn.network.find_network(network)
            if not network_obj:
                logger.error(f"Network not found: {network}")
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
                **kwargs
            )
            
            # Wait for server to be active
            server = self._conn.compute.wait_for_server(server)
            logger.info(f"Created instance: {server.id}")
            return self._server_to_dict(server)
            
        except Exception as e:
            logger.error(f"Failed to create instance {name}: {e}")
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
            logger.info(f"Started instance: {instance_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start instance {instance_id}: {e}")
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
            logger.info(f"Stopped instance: {instance_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop instance {instance_id}: {e}")
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
            logger.info(f"Rebooted instance: {instance_id} ({reboot_type})")
            return True
        except Exception as e:
            logger.error(f"Failed to reboot instance {instance_id}: {e}")
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
            logger.info(f"Deleted instance: {instance_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete instance {instance_id}: {e}")
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
    
    def list_images(self) -> List[Dict[str, Any]]:
        """
        List available images.
        
        Returns:
            List of image dictionaries
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
            logger.error(f"Failed to list images: {e}")
            return []
    
    def get_image(self, image_id: str) -> Optional[Dict[str, Any]]:
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
            logger.error(f"Failed to get image {image_id}: {e}")
            return None
    
    # =========================================================================
    # Flavor Operations
    # =========================================================================
    
    def list_flavors(self) -> List[Dict[str, Any]]:
        """
        List available flavors (instance types).
        
        Returns:
            List of flavor dictionaries
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
            logger.error(f"Failed to list flavors: {e}")
            return []
    
    # =========================================================================
    # Key Pair Operations
    # =========================================================================
    
    def list_keypairs(self) -> List[Dict[str, Any]]:
        """
        List SSH key pairs.
        
        Returns:
            List of keypair dictionaries
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
            logger.error(f"Failed to list keypairs: {e}")
            return []
    
    def create_keypair(
        self,
        name: str,
        public_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
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
                name=name,
                public_key=public_key
            )
            result = {
                "name": keypair.name,
                "fingerprint": keypair.fingerprint,
                "public_key": keypair.public_key,
            }
            # Include private key if it was generated
            if hasattr(keypair, "private_key") and keypair.private_key:
                result["private_key"] = keypair.private_key
            
            logger.info(f"Created keypair: {name}")
            return result
        except Exception as e:
            logger.error(f"Failed to create keypair {name}: {e}")
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
            logger.info(f"Deleted keypair: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete keypair {name}: {e}")
            return False
    
    # =========================================================================
    # Availability Zone Operations
    # =========================================================================
    
    def list_availability_zones(self) -> List[Dict[str, Any]]:
        """
        List availability zones.
        
        Returns:
            List of availability zone dictionaries
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
            logger.error(f"Failed to list availability zones: {e}")
            return []
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _server_to_dict(self, server: Any) -> Dict[str, Any]:
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
