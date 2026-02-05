"""
Infomaniak Network Client (Neutron/Octavia).

Provides network, router, security group, and load balancer operations.
"""

from typing import Any, Dict, List, Optional
import logging

from ..base import InfomaniakOpenStackBase

logger = logging.getLogger(__name__)


class InfomaniakNetworkClient(InfomaniakOpenStackBase):
    """
    Client for Infomaniak networking (Neutron) operations.

    Provides methods for managing networks, routers, security groups,
    and load balancers.
    """

    _service_name = "network"
    
    # =========================================================================
    # Network Operations
    # =========================================================================
    
    def list_networks(self) -> List[Dict[str, Any]]:
        """List all networks."""
        try:
            networks = list(self._conn.network.networks())
            return [
                {
                    "id": n.id,
                    "name": n.name,
                    "status": n.status,
                    "is_shared": n.is_shared,
                    "is_external": n.is_router_external,
                    "subnets": n.subnet_ids or [],
                }
                for n in networks
            ]
        except Exception as e:
            logger.error(f"Failed to list networks: {e}")
            return []
    
    def create_network(
        self,
        name: str,
        description: Optional[str] = None,
        is_shared: bool = False,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Create a new network."""
        try:
            network = self._conn.network.create_network(
                name=name,
                description=description,
                is_shared=is_shared,
                **kwargs
            )
            logger.info(f"Created network: {network.id}")
            return {"id": network.id, "name": network.name}
        except Exception as e:
            logger.error(f"Failed to create network {name}: {e}")
            return None
    
    def delete_network(self, network_id: str) -> bool:
        """Delete a network."""
        try:
            self._conn.network.delete_network(network_id)
            logger.info(f"Deleted network: {network_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete network {network_id}: {e}")
            return False
    
    def create_subnet(
        self,
        network_id: str,
        name: str,
        cidr: str,
        ip_version: int = 4,
        gateway_ip: Optional[str] = None,
        enable_dhcp: bool = True,
        dns_nameservers: Optional[List[str]] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
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
                **kwargs
            )
            logger.info(f"Created subnet: {subnet.id}")
            return {"id": subnet.id, "name": subnet.name, "cidr": subnet.cidr}
        except Exception as e:
            logger.error(f"Failed to create subnet {name}: {e}")
            return None
    
    # =========================================================================
    # Router Operations
    # =========================================================================
    
    def list_routers(self) -> List[Dict[str, Any]]:
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
            logger.error(f"Failed to list routers: {e}")
            return []
    
    def create_router(
        self,
        name: str,
        external_network: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Create a router with optional external gateway."""
        try:
            router_args = {"name": name, **kwargs}
            
            if external_network:
                ext_net = self._conn.network.find_network(external_network)
                if ext_net:
                    router_args["external_gateway_info"] = {"network_id": ext_net.id}
            
            router = self._conn.network.create_router(**router_args)
            logger.info(f"Created router: {router.id}")
            return {"id": router.id, "name": router.name}
        except Exception as e:
            logger.error(f"Failed to create router {name}: {e}")
            return None
    
    def add_router_interface(
        self,
        router_id: str,
        subnet_id: str
    ) -> bool:
        """Add a subnet interface to a router."""
        try:
            self._conn.network.add_interface_to_router(router_id, subnet_id=subnet_id)
            logger.info(f"Added interface for subnet {subnet_id} to router {router_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add interface to router {router_id}: {e}")
            return False
    
    def remove_router_interface(
        self,
        router_id: str,
        subnet_id: str
    ) -> bool:
        """Remove a subnet interface from a router."""
        try:
            self._conn.network.remove_interface_from_router(router_id, subnet_id=subnet_id)
            logger.info(f"Removed interface for subnet {subnet_id} from router {router_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove interface from router {router_id}: {e}")
            return False

    def delete_router(self, router_id: str) -> bool:
        """Delete a router."""
        try:
            self._conn.network.delete_router(router_id)
            logger.info(f"Deleted router: {router_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete router {router_id}: {e}")
            return False
    
    # =========================================================================
    # Security Group Operations
    # =========================================================================
    
    def list_security_groups(self) -> List[Dict[str, Any]]:
        """List all security groups."""
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
            logger.error(f"Failed to list security groups: {e}")
            return []
    
    def create_security_group(
        self,
        name: str,
        description: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a security group."""
        try:
            sg = self._conn.network.create_security_group(
                name=name,
                description=description or ""
            )
            logger.info(f"Created security group: {sg.id}")
            return {"id": sg.id, "name": sg.name}
        except Exception as e:
            logger.error(f"Failed to create security group {name}: {e}")
            return None
    
    def add_security_group_rule(
        self,
        security_group_id: str,
        direction: str = "ingress",
        protocol: Optional[str] = None,
        port_range_min: Optional[int] = None,
        port_range_max: Optional[int] = None,
        remote_ip_prefix: Optional[str] = None,
        ethertype: str = "IPv4",
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Add a rule to a security group.
        
        Args:
            security_group_id: Target security group
            direction: "ingress" or "egress"
            protocol: "tcp", "udp", "icmp", or None for all
            port_range_min: Starting port (None for all)
            port_range_max: Ending port (None for all)
            remote_ip_prefix: CIDR for allowed IPs (e.g., "0.0.0.0/0")
            ethertype: "IPv4" or "IPv6"
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
                **kwargs
            )
            logger.info(f"Created security group rule: {rule.id}")
            return {"id": rule.id, "direction": direction, "protocol": protocol}
        except Exception as e:
            logger.error(f"Failed to add rule to {security_group_id}: {e}")
            return None
    
    def delete_security_group(self, security_group_id: str) -> bool:
        """Delete a security group."""
        try:
            self._conn.network.delete_security_group(security_group_id)
            logger.info(f"Deleted security group: {security_group_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete security group {security_group_id}: {e}")
            return False
    
    # =========================================================================
    # Floating IP Operations
    # =========================================================================
    
    def list_floating_ips(self) -> List[Dict[str, Any]]:
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
            logger.error(f"Failed to list floating IPs: {e}")
            return []
    
    def allocate_floating_ip(
        self,
        external_network: str
    ) -> Optional[Dict[str, Any]]:
        """Allocate a floating IP from an external network."""
        try:
            ext_net = self._conn.network.find_network(external_network)
            if not ext_net:
                logger.error(f"External network not found: {external_network}")
                return None
            
            fip = self._conn.network.create_ip(floating_network_id=ext_net.id)
            logger.info(f"Allocated floating IP: {fip.floating_ip_address}")
            return {"id": fip.id, "floating_ip_address": fip.floating_ip_address}
        except Exception as e:
            logger.error(f"Failed to allocate floating IP: {e}")
            return None
    
    def associate_floating_ip(
        self,
        floating_ip_id: str,
        port_id: str
    ) -> bool:
        """Associate a floating IP with a port."""
        try:
            self._conn.network.update_ip(floating_ip_id, port_id=port_id)
            logger.info(f"Associated floating IP {floating_ip_id} with port {port_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to associate floating IP: {e}")
            return False
    
    # =========================================================================
    # Load Balancer Operations (Octavia)
    # =========================================================================
    
    def list_loadbalancers(self) -> List[Dict[str, Any]]:
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
            logger.error(f"Failed to list load balancers: {e}")
            return []
    
    def create_loadbalancer(
        self,
        name: str,
        subnet_id: str,
        vip_address: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Create a load balancer."""
        try:
            lb = self._conn.load_balancer.create_load_balancer(
                name=name,
                vip_subnet_id=subnet_id,
                vip_address=vip_address,
                **kwargs
            )
            logger.info(f"Created load balancer: {lb.id}")
            return {"id": lb.id, "name": lb.name, "vip_address": lb.vip_address}
        except Exception as e:
            logger.error(f"Failed to create load balancer {name}: {e}")
            return None
    
    def delete_loadbalancer(self, loadbalancer_id: str, cascade: bool = False) -> bool:
        """Delete a load balancer."""
        try:
            self._conn.load_balancer.delete_load_balancer(
                loadbalancer_id,
                cascade=cascade
            )
            logger.info(f"Deleted load balancer: {loadbalancer_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete load balancer {loadbalancer_id}: {e}")
            return False

    # =========================================================================
    # Subnet Operations
    # =========================================================================

    def list_subnets(self) -> List[Dict[str, Any]]:
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
            logger.error(f"Failed to list subnets: {e}")
            return []

    def get_subnet(self, subnet_id: str) -> Optional[Dict[str, Any]]:
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
            logger.error(f"Failed to get subnet {subnet_id}: {e}")
            return None

    def delete_subnet(self, subnet_id: str) -> bool:
        """Delete a subnet."""
        try:
            self._conn.network.delete_subnet(subnet_id)
            logger.info(f"Deleted subnet: {subnet_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete subnet {subnet_id}: {e}")
            return False

    # =========================================================================
    # Floating IP Expanded Operations
    # =========================================================================

    def release_floating_ip(self, floating_ip_id: str) -> bool:
        """Release (delete/deallocate) a floating IP."""
        try:
            self._conn.network.delete_ip(floating_ip_id)
            logger.info(f"Released floating IP: {floating_ip_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to release floating IP {floating_ip_id}: {e}")
            return False

    def disassociate_floating_ip(self, floating_ip_id: str) -> bool:
        """Disassociate a floating IP from its port."""
        try:
            self._conn.network.update_ip(floating_ip_id, port_id=None)
            logger.info(f"Disassociated floating IP: {floating_ip_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to disassociate floating IP {floating_ip_id}: {e}")
            return False

    # =========================================================================
    # Octavia Listener Operations
    # =========================================================================

    def list_listeners(
        self, loadbalancer_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List listeners, optionally filtered by load balancer."""
        try:
            kwargs = {}
            if loadbalancer_id:
                kwargs["loadbalancer_id"] = loadbalancer_id
            listeners = list(self._conn.load_balancer.listeners(**kwargs))
            return [
                {
                    "id": l.id,
                    "name": l.name,
                    "protocol": l.protocol,
                    "protocol_port": l.protocol_port,
                    "loadbalancer_id": getattr(l, "loadbalancer_id", None),
                }
                for l in listeners
            ]
        except Exception as e:
            logger.error(f"Failed to list listeners: {e}")
            return []

    def create_listener(
        self,
        loadbalancer_id: str,
        name: str,
        protocol: str,
        port: int,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Create a listener on a load balancer."""
        try:
            listener = self._conn.load_balancer.create_listener(
                loadbalancer_id=loadbalancer_id,
                name=name,
                protocol=protocol,
                protocol_port=port,
                **kwargs
            )
            logger.info(f"Created listener: {listener.id}")
            return {"id": listener.id, "name": listener.name, "protocol": protocol}
        except Exception as e:
            logger.error(f"Failed to create listener {name}: {e}")
            return None

    def delete_listener(self, listener_id: str) -> bool:
        """Delete a listener."""
        try:
            self._conn.load_balancer.delete_listener(listener_id)
            logger.info(f"Deleted listener: {listener_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete listener {listener_id}: {e}")
            return False

    # =========================================================================
    # Octavia Pool Operations
    # =========================================================================

    def list_pools(
        self, loadbalancer_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
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
            logger.error(f"Failed to list pools: {e}")
            return []

    def create_pool(
        self,
        name: str,
        protocol: str,
        lb_algorithm: str,
        listener_id: Optional[str] = None,
        loadbalancer_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Create a pool."""
        try:
            pool = self._conn.load_balancer.create_pool(
                name=name,
                protocol=protocol,
                lb_algorithm=lb_algorithm,
                listener_id=listener_id,
                loadbalancer_id=loadbalancer_id,
                **kwargs
            )
            logger.info(f"Created pool: {pool.id}")
            return {"id": pool.id, "name": pool.name, "protocol": protocol}
        except Exception as e:
            logger.error(f"Failed to create pool {name}: {e}")
            return None

    def delete_pool(self, pool_id: str) -> bool:
        """Delete a pool."""
        try:
            self._conn.load_balancer.delete_pool(pool_id)
            logger.info(f"Deleted pool: {pool_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete pool {pool_id}: {e}")
            return False

    # =========================================================================
    # Pool Member Operations
    # =========================================================================

    def list_pool_members(self, pool_id: str) -> List[Dict[str, Any]]:
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
            logger.error(f"Failed to list pool members for {pool_id}: {e}")
            return []

    def add_pool_member(
        self,
        pool_id: str,
        address: str,
        port: int,
        weight: int = 1,
        name: Optional[str] = None,
        subnet_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Add a member to a pool."""
        try:
            member = self._conn.load_balancer.create_member(
                pool_id,
                address=address,
                protocol_port=port,
                weight=weight,
                name=name,
                subnet_id=subnet_id,
                **kwargs
            )
            logger.info(f"Added pool member: {member.id}")
            return {"id": member.id, "address": address, "port": port}
        except Exception as e:
            logger.error(f"Failed to add member to pool {pool_id}: {e}")
            return None

    def remove_pool_member(self, pool_id: str, member_id: str) -> bool:
        """Remove a member from a pool."""
        try:
            self._conn.load_balancer.delete_member(member_id, pool_id)
            logger.info(f"Removed pool member: {member_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove member {member_id} from pool {pool_id}: {e}")
            return False

    # =========================================================================
    # Health Monitor Operations
    # =========================================================================

    def list_health_monitors(
        self, pool_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
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
            logger.error(f"Failed to list health monitors: {e}")
            return []

    def create_health_monitor(
        self,
        pool_id: str,
        monitor_type: str,
        delay: int,
        timeout: int,
        max_retries: int = 3,
        name: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
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
                **kwargs
            )
            logger.info(f"Created health monitor: {hm.id}")
            return {"id": hm.id, "type": monitor_type, "pool_id": pool_id}
        except Exception as e:
            logger.error(f"Failed to create health monitor for pool {pool_id}: {e}")
            return None

    def delete_health_monitor(self, health_monitor_id: str) -> bool:
        """Delete a health monitor."""
        try:
            self._conn.load_balancer.delete_health_monitor(health_monitor_id)
            logger.info(f"Deleted health monitor: {health_monitor_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete health monitor {health_monitor_id}: {e}")
            return False
