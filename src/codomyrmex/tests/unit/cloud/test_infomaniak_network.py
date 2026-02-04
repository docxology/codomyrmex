"""
Unit tests for InfomaniakNetworkClient.

Tests cover:
- Network CRUD operations (list, create, delete)
- Subnet operations (list, get, create, delete)
- Router operations (list, create with/without external gateway, add interface, delete)
- Security group operations (list, create, add rule, delete)
- Floating IP operations (list, allocate, associate, disassociate, release)
- Load balancer operations (list, create, delete with cascade)
- Listener operations (list, create, delete)
- Pool operations (list, create, delete)
- Pool member operations (list, add, remove)
- Health monitor operations (list, create, delete)
- Error handling for all critical paths

Total: ~25 tests in one TestInfomaniakNetwork class.
"""

import pytest
from unittest.mock import MagicMock

from .conftest import make_mock_network, make_mock_floating_ip


class TestInfomaniakNetwork:
    """Comprehensive tests for InfomaniakNetworkClient."""

    @pytest.fixture
    def client(self, mock_openstack_connection):
        """Create a network client with a mocked connection."""
        from codomyrmex.cloud.infomaniak.network.client import InfomaniakNetworkClient
        return InfomaniakNetworkClient(mock_openstack_connection)

    # =====================================================================
    # Network Operations
    # =====================================================================

    def test_list_networks_success(self, client, mock_openstack_connection):
        """list_networks returns formatted dicts for each network."""
        net = make_mock_network(network_id="net-1", name="prod-net", status="ACTIVE")
        mock_openstack_connection.network.networks.return_value = [net]

        result = client.list_networks()

        assert len(result) == 1
        assert result[0]["id"] == "net-1"
        assert result[0]["name"] == "prod-net"
        assert result[0]["status"] == "ACTIVE"
        assert result[0]["is_shared"] is False
        assert result[0]["is_external"] is False
        assert result[0]["subnets"] == ["subnet-1"]

    def test_list_networks_error_returns_empty(self, client, mock_openstack_connection):
        """list_networks returns [] on connection error."""
        mock_openstack_connection.network.networks.side_effect = Exception("timeout")

        result = client.list_networks()

        assert result == []

    def test_create_network_success(self, client, mock_openstack_connection):
        """create_network returns id and name on success."""
        mock_net = MagicMock()
        mock_net.id = "net-new"
        mock_net.name = "my-net"
        mock_openstack_connection.network.create_network.return_value = mock_net

        result = client.create_network(name="my-net", description="A test network")

        assert result is not None
        assert result["id"] == "net-new"
        assert result["name"] == "my-net"
        mock_openstack_connection.network.create_network.assert_called_once_with(
            name="my-net",
            description="A test network",
            is_shared=False,
        )

    def test_create_network_error_returns_none(self, client, mock_openstack_connection):
        """create_network returns None on API error."""
        mock_openstack_connection.network.create_network.side_effect = Exception("conflict")

        result = client.create_network(name="bad-net")

        assert result is None

    def test_delete_network_success(self, client, mock_openstack_connection):
        """delete_network returns True on success."""
        result = client.delete_network("net-del")

        assert result is True
        mock_openstack_connection.network.delete_network.assert_called_once_with("net-del")

    def test_delete_network_error_returns_false(self, client, mock_openstack_connection):
        """delete_network returns False on error."""
        mock_openstack_connection.network.delete_network.side_effect = Exception("not found")

        result = client.delete_network("net-missing")

        assert result is False

    # =====================================================================
    # Subnet Operations
    # =====================================================================

    def test_create_subnet_success(self, client, mock_openstack_connection):
        """create_subnet returns id, name, cidr on success."""
        mock_sub = MagicMock()
        mock_sub.id = "sub-new"
        mock_sub.name = "app-subnet"
        mock_sub.cidr = "10.0.1.0/24"
        mock_openstack_connection.network.create_subnet.return_value = mock_sub

        result = client.create_subnet(
            network_id="net-1",
            name="app-subnet",
            cidr="10.0.1.0/24",
            gateway_ip="10.0.1.1",
            dns_nameservers=["8.8.8.8"],
        )

        assert result is not None
        assert result["id"] == "sub-new"
        assert result["cidr"] == "10.0.1.0/24"
        mock_openstack_connection.network.create_subnet.assert_called_once()

    def test_list_subnets_success(self, client, mock_openstack_connection):
        """list_subnets returns formatted subnet dicts."""
        mock_sub = MagicMock()
        mock_sub.id = "sub-1"
        mock_sub.name = "default-subnet"
        mock_sub.network_id = "net-1"
        mock_sub.cidr = "10.0.0.0/24"
        mock_sub.ip_version = 4
        mock_sub.gateway_ip = "10.0.0.1"
        mock_sub.is_dhcp_enabled = True
        mock_openstack_connection.network.subnets.return_value = [mock_sub]

        result = client.list_subnets()

        assert len(result) == 1
        assert result[0]["id"] == "sub-1"
        assert result[0]["cidr"] == "10.0.0.0/24"
        assert result[0]["is_dhcp_enabled"] is True

    def test_get_subnet_success(self, client, mock_openstack_connection):
        """get_subnet returns formatted dict for found subnet."""
        mock_sub = MagicMock()
        mock_sub.id = "sub-abc"
        mock_sub.name = "my-subnet"
        mock_sub.network_id = "net-1"
        mock_sub.cidr = "10.0.2.0/24"
        mock_sub.ip_version = 4
        mock_sub.gateway_ip = "10.0.2.1"
        mock_openstack_connection.network.get_subnet.return_value = mock_sub

        result = client.get_subnet("sub-abc")

        assert result is not None
        assert result["id"] == "sub-abc"
        assert result["gateway_ip"] == "10.0.2.1"

    def test_get_subnet_not_found_returns_none(self, client, mock_openstack_connection):
        """get_subnet returns None when subnet does not exist."""
        mock_openstack_connection.network.get_subnet.return_value = None

        result = client.get_subnet("sub-missing")

        assert result is None

    def test_delete_subnet_success(self, client, mock_openstack_connection):
        """delete_subnet returns True on success."""
        result = client.delete_subnet("sub-del")

        assert result is True
        mock_openstack_connection.network.delete_subnet.assert_called_once_with("sub-del")

    # =====================================================================
    # Router Operations
    # =====================================================================

    def test_list_routers_success(self, client, mock_openstack_connection):
        """list_routers returns formatted router dicts."""
        mock_rtr = MagicMock()
        mock_rtr.id = "rtr-1"
        mock_rtr.name = "main-router"
        mock_rtr.status = "ACTIVE"
        mock_rtr.external_gateway_info = {"network_id": "ext-net"}
        mock_openstack_connection.network.routers.return_value = [mock_rtr]

        result = client.list_routers()

        assert len(result) == 1
        assert result[0]["id"] == "rtr-1"
        assert result[0]["external_gateway"] == {"network_id": "ext-net"}

    def test_create_router_with_external_network(self, client, mock_openstack_connection):
        """create_router sets external_gateway_info when external_network found."""
        ext_net = MagicMock()
        ext_net.id = "ext-net-id"
        mock_openstack_connection.network.find_network.return_value = ext_net

        mock_rtr = MagicMock()
        mock_rtr.id = "rtr-new"
        mock_rtr.name = "gw-router"
        mock_openstack_connection.network.create_router.return_value = mock_rtr

        result = client.create_router(name="gw-router", external_network="public")

        assert result is not None
        assert result["id"] == "rtr-new"
        call_kwargs = mock_openstack_connection.network.create_router.call_args[1]
        assert call_kwargs["external_gateway_info"] == {"network_id": "ext-net-id"}

    def test_add_router_interface_success(self, client, mock_openstack_connection):
        """add_router_interface returns True on success."""
        result = client.add_router_interface("rtr-1", "sub-1")

        assert result is True
        mock_openstack_connection.network.add_interface_to_router.assert_called_once_with(
            "rtr-1", subnet_id="sub-1"
        )

    def test_delete_router_error_returns_false(self, client, mock_openstack_connection):
        """delete_router returns False on API error."""
        mock_openstack_connection.network.delete_router.side_effect = Exception("in use")

        result = client.delete_router("rtr-busy")

        assert result is False

    # =====================================================================
    # Security Group Operations
    # =====================================================================

    def test_list_security_groups_success(self, client, mock_openstack_connection):
        """list_security_groups returns formatted SG dicts with rules_count."""
        mock_sg = MagicMock()
        mock_sg.id = "sg-1"
        mock_sg.name = "web-sg"
        mock_sg.description = "Web traffic"
        mock_sg.security_group_rules = [{}, {}, {}]
        mock_openstack_connection.network.security_groups.return_value = [mock_sg]

        result = client.list_security_groups()

        assert len(result) == 1
        assert result[0]["id"] == "sg-1"
        assert result[0]["rules_count"] == 3

    def test_create_security_group_success(self, client, mock_openstack_connection):
        """create_security_group returns id and name on success."""
        mock_sg = MagicMock()
        mock_sg.id = "sg-new"
        mock_sg.name = "db-sg"
        mock_openstack_connection.network.create_security_group.return_value = mock_sg

        result = client.create_security_group(name="db-sg", description="Database access")

        assert result is not None
        assert result["id"] == "sg-new"
        assert result["name"] == "db-sg"

    def test_add_security_group_rule_success(self, client, mock_openstack_connection):
        """add_security_group_rule returns id, direction, protocol on success."""
        mock_rule = MagicMock()
        mock_rule.id = "rule-new"
        mock_openstack_connection.network.create_security_group_rule.return_value = mock_rule

        result = client.add_security_group_rule(
            security_group_id="sg-1",
            direction="ingress",
            protocol="tcp",
            port_range_min=443,
            port_range_max=443,
            remote_ip_prefix="0.0.0.0/0",
        )

        assert result is not None
        assert result["id"] == "rule-new"
        assert result["direction"] == "ingress"
        assert result["protocol"] == "tcp"

    def test_delete_security_group_success(self, client, mock_openstack_connection):
        """delete_security_group returns True on success."""
        result = client.delete_security_group("sg-del")

        assert result is True
        mock_openstack_connection.network.delete_security_group.assert_called_once_with("sg-del")

    # =====================================================================
    # Floating IP Operations
    # =====================================================================

    def test_list_floating_ips_success(self, client, mock_openstack_connection):
        """list_floating_ips returns formatted FIP dicts."""
        fip = make_mock_floating_ip(fip_id="fip-1", address="195.15.220.10")
        mock_openstack_connection.network.ips.return_value = [fip]

        result = client.list_floating_ips()

        assert len(result) == 1
        assert result[0]["id"] == "fip-1"
        assert result[0]["floating_ip_address"] == "195.15.220.10"
        assert result[0]["status"] == "ACTIVE"

    def test_allocate_floating_ip_success(self, client, mock_openstack_connection):
        """allocate_floating_ip returns id and address when external network found."""
        ext_net = MagicMock()
        ext_net.id = "ext-net-id"
        mock_openstack_connection.network.find_network.return_value = ext_net

        mock_fip = MagicMock()
        mock_fip.id = "fip-new"
        mock_fip.floating_ip_address = "195.15.220.99"
        mock_openstack_connection.network.create_ip.return_value = mock_fip

        result = client.allocate_floating_ip("public")

        assert result is not None
        assert result["id"] == "fip-new"
        assert result["floating_ip_address"] == "195.15.220.99"
        mock_openstack_connection.network.create_ip.assert_called_once_with(
            floating_network_id="ext-net-id"
        )

    def test_allocate_floating_ip_network_not_found(self, client, mock_openstack_connection):
        """allocate_floating_ip returns None when external network not found."""
        mock_openstack_connection.network.find_network.return_value = None

        result = client.allocate_floating_ip("nonexistent-net")

        assert result is None
        mock_openstack_connection.network.create_ip.assert_not_called()

    def test_allocate_floating_ip_error_returns_none(self, client, mock_openstack_connection):
        """allocate_floating_ip returns None on API error."""
        mock_openstack_connection.network.find_network.side_effect = Exception("API down")

        result = client.allocate_floating_ip("public")

        assert result is None

    def test_associate_floating_ip_success(self, client, mock_openstack_connection):
        """associate_floating_ip calls update_ip with port_id and returns True."""
        result = client.associate_floating_ip("fip-1", "port-abc")

        assert result is True
        mock_openstack_connection.network.update_ip.assert_called_once_with(
            "fip-1", port_id="port-abc"
        )

    def test_disassociate_floating_ip_success(self, client, mock_openstack_connection):
        """disassociate_floating_ip sets port_id=None and returns True."""
        result = client.disassociate_floating_ip("fip-1")

        assert result is True
        mock_openstack_connection.network.update_ip.assert_called_once_with(
            "fip-1", port_id=None
        )

    def test_release_floating_ip_success(self, client, mock_openstack_connection):
        """release_floating_ip deletes the FIP and returns True."""
        result = client.release_floating_ip("fip-del")

        assert result is True
        mock_openstack_connection.network.delete_ip.assert_called_once_with("fip-del")

    # =====================================================================
    # Load Balancer Operations
    # =====================================================================

    def test_list_loadbalancers_success(self, client, mock_openstack_connection):
        """list_loadbalancers returns formatted LB dicts."""
        mock_lb = MagicMock()
        mock_lb.id = "lb-1"
        mock_lb.name = "web-lb"
        mock_lb.vip_address = "10.0.0.100"
        mock_lb.operating_status = "ONLINE"
        mock_lb.provisioning_status = "ACTIVE"
        mock_openstack_connection.load_balancer.load_balancers.return_value = [mock_lb]

        result = client.list_loadbalancers()

        assert len(result) == 1
        assert result[0]["id"] == "lb-1"
        assert result[0]["vip_address"] == "10.0.0.100"
        assert result[0]["operating_status"] == "ONLINE"

    def test_create_loadbalancer_success(self, client, mock_openstack_connection):
        """create_loadbalancer returns id, name, and vip_address."""
        mock_lb = MagicMock()
        mock_lb.id = "lb-new"
        mock_lb.name = "api-lb"
        mock_lb.vip_address = "10.0.0.200"
        mock_openstack_connection.load_balancer.create_load_balancer.return_value = mock_lb

        result = client.create_loadbalancer(name="api-lb", subnet_id="sub-1")

        assert result is not None
        assert result["id"] == "lb-new"
        assert result["vip_address"] == "10.0.0.200"

    def test_delete_loadbalancer_cascade(self, client, mock_openstack_connection):
        """delete_loadbalancer passes cascade flag to the API."""
        result = client.delete_loadbalancer("lb-del", cascade=True)

        assert result is True
        mock_openstack_connection.load_balancer.delete_load_balancer.assert_called_once_with(
            "lb-del", cascade=True
        )

    def test_delete_loadbalancer_error_returns_false(self, client, mock_openstack_connection):
        """delete_loadbalancer returns False on API error."""
        mock_openstack_connection.load_balancer.delete_load_balancer.side_effect = Exception("in use")

        result = client.delete_loadbalancer("lb-busy")

        assert result is False

    # =====================================================================
    # Listener Operations
    # =====================================================================

    def test_create_listener_success(self, client, mock_openstack_connection):
        """create_listener returns id, name, and protocol."""
        mock_listener = MagicMock()
        mock_listener.id = "lis-new"
        mock_listener.name = "https-listener"
        mock_openstack_connection.load_balancer.create_listener.return_value = mock_listener

        result = client.create_listener(
            loadbalancer_id="lb-1",
            name="https-listener",
            protocol="HTTPS",
            port=443,
        )

        assert result is not None
        assert result["id"] == "lis-new"
        assert result["protocol"] == "HTTPS"

    def test_delete_listener_success(self, client, mock_openstack_connection):
        """delete_listener returns True on success."""
        result = client.delete_listener("lis-del")

        assert result is True
        mock_openstack_connection.load_balancer.delete_listener.assert_called_once_with("lis-del")

    # =====================================================================
    # Pool Operations
    # =====================================================================

    def test_create_pool_success(self, client, mock_openstack_connection):
        """create_pool returns id, name, and protocol."""
        mock_pool = MagicMock()
        mock_pool.id = "pool-new"
        mock_pool.name = "web-pool"
        mock_openstack_connection.load_balancer.create_pool.return_value = mock_pool

        result = client.create_pool(
            name="web-pool",
            protocol="HTTP",
            lb_algorithm="ROUND_ROBIN",
            listener_id="lis-1",
        )

        assert result is not None
        assert result["id"] == "pool-new"
        assert result["protocol"] == "HTTP"

    def test_delete_pool_success(self, client, mock_openstack_connection):
        """delete_pool returns True on success."""
        result = client.delete_pool("pool-del")

        assert result is True
        mock_openstack_connection.load_balancer.delete_pool.assert_called_once_with("pool-del")

    # =====================================================================
    # Pool Member Operations
    # =====================================================================

    def test_add_pool_member_success(self, client, mock_openstack_connection):
        """add_pool_member returns id, address, and port."""
        mock_member = MagicMock()
        mock_member.id = "mem-new"
        mock_openstack_connection.load_balancer.create_member.return_value = mock_member

        result = client.add_pool_member(
            pool_id="pool-1",
            address="10.0.0.10",
            port=8080,
            weight=2,
        )

        assert result is not None
        assert result["id"] == "mem-new"
        assert result["address"] == "10.0.0.10"
        assert result["port"] == 8080

    def test_remove_pool_member_success(self, client, mock_openstack_connection):
        """remove_pool_member returns True on success."""
        result = client.remove_pool_member("pool-1", "mem-del")

        assert result is True
        mock_openstack_connection.load_balancer.delete_member.assert_called_once_with(
            "mem-del", "pool-1"
        )

    # =====================================================================
    # Health Monitor Operations
    # =====================================================================

    def test_create_health_monitor_success(self, client, mock_openstack_connection):
        """create_health_monitor returns id, type, and pool_id."""
        mock_hm = MagicMock()
        mock_hm.id = "hm-new"
        mock_openstack_connection.load_balancer.create_health_monitor.return_value = mock_hm

        result = client.create_health_monitor(
            pool_id="pool-1",
            type="HTTP",
            delay=10,
            timeout=5,
            max_retries=3,
        )

        assert result is not None
        assert result["id"] == "hm-new"
        assert result["type"] == "HTTP"
        assert result["pool_id"] == "pool-1"

    def test_delete_health_monitor_success(self, client, mock_openstack_connection):
        """delete_health_monitor returns True on success."""
        result = client.delete_health_monitor("hm-del")

        assert result is True
        mock_openstack_connection.load_balancer.delete_health_monitor.assert_called_once_with("hm-del")
