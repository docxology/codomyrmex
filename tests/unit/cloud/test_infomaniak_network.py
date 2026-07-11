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
from _stubs import Stub, make_stub_floating_ip, make_stub_network


class TestInfomaniakNetwork:
    """Comprehensive tests for InfomaniakNetworkClient."""

    @pytest.fixture
    def client(self, stub_openstack_connection):
        """Create a network client with a stubbed connection."""
        from codomyrmex.cloud.infomaniak.network.client import InfomaniakNetworkClient

        return InfomaniakNetworkClient(stub_openstack_connection)

    # =====================================================================
    # Network Operations
    # =====================================================================

    def test_list_networks_success(self, client, stub_openstack_connection):
        """list_networks returns formatted dicts for each network."""
        net = make_stub_network(network_id="net-1", name="prod-net", status="ACTIVE")
        stub_openstack_connection.network.networks.return_value = [net]

        result = client.list_networks()

        assert len(result) == 1
        assert result[0]["id"] == "net-1"
        assert result[0]["name"] == "prod-net"
        assert result[0]["status"] == "ACTIVE"
        assert result[0]["is_shared"] is False
        assert result[0]["is_external"] is False
        assert result[0]["subnets"] == ["subnet-1"]

    def test_list_networks_error_returns_empty(self, client, stub_openstack_connection):
        """list_networks returns [] on connection error."""
        stub_openstack_connection.network.networks.side_effect = Exception("timeout")

        result = client.list_networks()

        assert result == []

    def test_create_network_success(self, client, stub_openstack_connection):
        """create_network returns id and name on success."""
        stub_net = Stub()
        stub_net.id = "net-new"
        stub_net.name = "my-net"
        stub_openstack_connection.network.create_network.return_value = stub_net

        result = client.create_network(name="my-net", description="A test network")

        assert result is not None
        assert result["id"] == "net-new"
        assert result["name"] == "my-net"
        stub_openstack_connection.network.create_network.assert_called_once_with(
            name="my-net",
            description="A test network",
            is_shared=False,
        )

    def test_create_network_error_returns_none(self, client, stub_openstack_connection):
        """create_network returns None on API error."""
        stub_openstack_connection.network.create_network.side_effect = Exception(
            "conflict"
        )

        result = client.create_network(name="bad-net")

        assert result is None

    def test_delete_network_success(self, client, stub_openstack_connection):
        """delete_network returns True on success."""
        result = client.delete_network("net-del")

        assert result is True
        stub_openstack_connection.network.delete_network.assert_called_once_with(
            "net-del"
        )

    def test_delete_network_error_returns_false(
        self, client, stub_openstack_connection
    ):
        """delete_network returns False on error."""
        stub_openstack_connection.network.delete_network.side_effect = Exception(
            "not found"
        )

        result = client.delete_network("net-missing")

        assert result is False

    # =====================================================================
    # Subnet Operations
    # =====================================================================

    def test_create_subnet_success(self, client, stub_openstack_connection):
        """create_subnet returns id, name, cidr on success."""
        stub_sub = Stub()
        stub_sub.id = "sub-new"
        stub_sub.name = "app-subnet"
        stub_sub.cidr = "10.0.1.0/24"
        stub_openstack_connection.network.create_subnet.return_value = stub_sub

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
        stub_openstack_connection.network.create_subnet.assert_called_once()

    def test_list_subnets_success(self, client, stub_openstack_connection):
        """list_subnets returns formatted subnet dicts."""
        stub_sub = Stub()
        stub_sub.id = "sub-1"
        stub_sub.name = "default-subnet"
        stub_sub.network_id = "net-1"
        stub_sub.cidr = "10.0.0.0/24"
        stub_sub.ip_version = 4
        stub_sub.gateway_ip = "10.0.0.1"
        stub_sub.is_dhcp_enabled = True
        stub_openstack_connection.network.subnets.return_value = [stub_sub]

        result = client.list_subnets()

        assert len(result) == 1
        assert result[0]["id"] == "sub-1"
        assert result[0]["cidr"] == "10.0.0.0/24"
        assert result[0]["is_dhcp_enabled"] is True

    def test_get_subnet_success(self, client, stub_openstack_connection):
        """get_subnet returns formatted dict for found subnet."""
        stub_sub = Stub()
        stub_sub.id = "sub-abc"
        stub_sub.name = "my-subnet"
        stub_sub.network_id = "net-1"
        stub_sub.cidr = "10.0.2.0/24"
        stub_sub.ip_version = 4
        stub_sub.gateway_ip = "10.0.2.1"
        stub_openstack_connection.network.get_subnet.return_value = stub_sub

        result = client.get_subnet("sub-abc")

        assert result is not None
        assert result["id"] == "sub-abc"
        assert result["gateway_ip"] == "10.0.2.1"

    def test_get_subnet_not_found_returns_none(self, client, stub_openstack_connection):
        """get_subnet returns None when subnet does not exist."""
        stub_openstack_connection.network.get_subnet.return_value = None

        result = client.get_subnet("sub-missing")

        assert result is None

    def test_delete_subnet_success(self, client, stub_openstack_connection):
        """delete_subnet returns True on success."""
        result = client.delete_subnet("sub-del")

        assert result is True
        stub_openstack_connection.network.delete_subnet.assert_called_once_with(
            "sub-del"
        )

    # =====================================================================
    # Router Operations
    # =====================================================================

    def test_list_routers_success(self, client, stub_openstack_connection):
        """list_routers returns formatted router dicts."""
        stub_rtr = Stub()
        stub_rtr.id = "rtr-1"
        stub_rtr.name = "main-router"
        stub_rtr.status = "ACTIVE"
        stub_rtr.external_gateway_info = {"network_id": "ext-net"}
        stub_openstack_connection.network.routers.return_value = [stub_rtr]

        result = client.list_routers()

        assert len(result) == 1
        assert result[0]["id"] == "rtr-1"
        assert result[0]["external_gateway"] == {"network_id": "ext-net"}

    def test_create_router_with_external_network(
        self, client, stub_openstack_connection
    ):
        """create_router sets external_gateway_info when external_network found."""
        ext_net = Stub()
        ext_net.id = "ext-net-id"
        stub_openstack_connection.network.find_network.return_value = ext_net

        stub_rtr = Stub()
        stub_rtr.id = "rtr-new"
        stub_rtr.name = "gw-router"
        stub_openstack_connection.network.create_router.return_value = stub_rtr

        result = client.create_router(name="gw-router", external_network="public")

        assert result is not None
        assert result["id"] == "rtr-new"
        call_kwargs = stub_openstack_connection.network.create_router.call_args[1]
        assert call_kwargs["external_gateway_info"] == {"network_id": "ext-net-id"}

    def test_add_router_interface_success(self, client, stub_openstack_connection):
        """add_router_interface returns True on success."""
        result = client.add_router_interface("rtr-1", "sub-1")

        assert result is True
        stub_openstack_connection.network.add_interface_to_router.assert_called_once_with(
            "rtr-1", subnet_id="sub-1"
        )

    def test_delete_router_error_returns_false(self, client, stub_openstack_connection):
        """delete_router returns False on API error."""
        stub_openstack_connection.network.delete_router.side_effect = Exception(
            "in use"
        )

        result = client.delete_router("rtr-busy")

        assert result is False

    # =====================================================================
    # Security Group Operations
    # =====================================================================

    def test_list_security_groups_success(self, client, stub_openstack_connection):
        """list_security_groups returns formatted SG dicts with rules_count."""
        stub_sg = Stub()
        stub_sg.id = "sg-1"
        stub_sg.name = "web-sg"
        stub_sg.description = "Web traffic"
        stub_sg.security_group_rules = [{}, {}, {}]
        stub_openstack_connection.network.security_groups.return_value = [stub_sg]

        result = client.list_security_groups()

        assert len(result) == 1
        assert result[0]["id"] == "sg-1"
        assert result[0]["rules_count"] == 3

    def test_create_security_group_success(self, client, stub_openstack_connection):
        """create_security_group returns id and name on success."""
        stub_sg = Stub()
        stub_sg.id = "sg-new"
        stub_sg.name = "db-sg"
        stub_openstack_connection.network.create_security_group.return_value = stub_sg

        result = client.create_security_group(
            name="db-sg", description="Database access"
        )

        assert result is not None
        assert result["id"] == "sg-new"
        assert result["name"] == "db-sg"

    def test_add_security_group_rule_success(self, client, stub_openstack_connection):
        """add_security_group_rule returns id, direction, protocol on success."""
        stub_rule = Stub()
        stub_rule.id = "rule-new"
        stub_openstack_connection.network.create_security_group_rule.return_value = (
            stub_rule
        )

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

    def test_delete_security_group_success(self, client, stub_openstack_connection):
        """delete_security_group returns True on success."""
        result = client.delete_security_group("sg-del")

        assert result is True
        stub_openstack_connection.network.delete_security_group.assert_called_once_with(
            "sg-del"
        )

    # =====================================================================
    # Floating IP Operations
    # =====================================================================

    def test_list_floating_ips_success(self, client, stub_openstack_connection):
        """list_floating_ips returns formatted FIP dicts."""
        fip = make_stub_floating_ip(fip_id="fip-1", address="195.15.220.10")
        stub_openstack_connection.network.ips.return_value = [fip]

        result = client.list_floating_ips()

        assert len(result) == 1
        assert result[0]["id"] == "fip-1"
        assert result[0]["floating_ip_address"] == "195.15.220.10"
        assert result[0]["status"] == "ACTIVE"

    def test_allocate_floating_ip_success(self, client, stub_openstack_connection):
        """allocate_floating_ip returns id and address when external network found."""
        ext_net = Stub()
        ext_net.id = "ext-net-id"
        stub_openstack_connection.network.find_network.return_value = ext_net

        stub_fip = Stub()
        stub_fip.id = "fip-new"
        stub_fip.floating_ip_address = "195.15.220.99"
        stub_openstack_connection.network.create_ip.return_value = stub_fip

        result = client.allocate_floating_ip("public")

        assert result is not None
        assert result["id"] == "fip-new"
        assert result["floating_ip_address"] == "195.15.220.99"
        stub_openstack_connection.network.create_ip.assert_called_once_with(
            floating_network_id="ext-net-id"
        )

    def test_allocate_floating_ip_network_not_found(
        self, client, stub_openstack_connection
    ):
        """allocate_floating_ip returns None when external network not found."""
        stub_openstack_connection.network.find_network.return_value = None

        result = client.allocate_floating_ip("nonexistent-net")

        assert result is None
        stub_openstack_connection.network.create_ip.assert_not_called()

    def test_allocate_floating_ip_error_returns_none(
        self, client, stub_openstack_connection
    ):
        """allocate_floating_ip returns None on API error."""
        stub_openstack_connection.network.find_network.side_effect = Exception(
            "API down"
        )

        result = client.allocate_floating_ip("public")

        assert result is None

    def test_associate_floating_ip_success(self, client, stub_openstack_connection):
        """associate_floating_ip calls update_ip with port_id and returns True."""
        result = client.associate_floating_ip("fip-1", "port-abc")

        assert result is True
        stub_openstack_connection.network.update_ip.assert_called_once_with(
            "fip-1", port_id="port-abc"
        )

    def test_disassociate_floating_ip_success(self, client, stub_openstack_connection):
        """disassociate_floating_ip sets port_id=None and returns True."""
        result = client.disassociate_floating_ip("fip-1")

        assert result is True
        stub_openstack_connection.network.update_ip.assert_called_once_with(
            "fip-1", port_id=None
        )

    def test_release_floating_ip_success(self, client, stub_openstack_connection):
        """release_floating_ip deletes the FIP and returns True."""
        result = client.release_floating_ip("fip-del")

        assert result is True
        stub_openstack_connection.network.delete_ip.assert_called_once_with("fip-del")

    # =====================================================================
    # Load Balancer Operations
    # =====================================================================

    def test_list_loadbalancers_success(self, client, stub_openstack_connection):
        """list_loadbalancers returns formatted LB dicts."""
        stub_lb = Stub()
        stub_lb.id = "lb-1"
        stub_lb.name = "web-lb"
        stub_lb.vip_address = "10.0.0.100"
        stub_lb.operating_status = "ONLINE"
        stub_lb.provisioning_status = "ACTIVE"
        stub_openstack_connection.load_balancer.load_balancers.return_value = [stub_lb]

        result = client.list_loadbalancers()

        assert len(result) == 1
        assert result[0]["id"] == "lb-1"
        assert result[0]["vip_address"] == "10.0.0.100"
        assert result[0]["operating_status"] == "ONLINE"

    def test_create_loadbalancer_success(self, client, stub_openstack_connection):
        """create_loadbalancer returns id, name, and vip_address."""
        stub_lb = Stub()
        stub_lb.id = "lb-new"
        stub_lb.name = "api-lb"
        stub_lb.vip_address = "10.0.0.200"
        stub_openstack_connection.load_balancer.create_load_balancer.return_value = (
            stub_lb
        )

        result = client.create_loadbalancer(name="api-lb", subnet_id="sub-1")

        assert result is not None
        assert result["id"] == "lb-new"
        assert result["vip_address"] == "10.0.0.200"

    def test_delete_loadbalancer_cascade(self, client, stub_openstack_connection):
        """delete_loadbalancer passes cascade flag to the API."""
        result = client.delete_loadbalancer("lb-del", cascade=True)

        assert result is True
        stub_openstack_connection.load_balancer.delete_load_balancer.assert_called_once_with(
            "lb-del", cascade=True
        )

    def test_delete_loadbalancer_error_returns_false(
        self, client, stub_openstack_connection
    ):
        """delete_loadbalancer returns False on API error."""
        stub_openstack_connection.load_balancer.delete_load_balancer.side_effect = (
            Exception("in use")
        )

        result = client.delete_loadbalancer("lb-busy")

        assert result is False

    # =====================================================================
    # Listener Operations
    # =====================================================================

    def test_create_listener_success(self, client, stub_openstack_connection):
        """create_listener returns id, name, and protocol."""
        stub_listener = Stub()
        stub_listener.id = "lis-new"
        stub_listener.name = "https-listener"
        stub_openstack_connection.load_balancer.create_listener.return_value = (
            stub_listener
        )

        result = client.create_listener(
            loadbalancer_id="lb-1",
            name="https-listener",
            protocol="HTTPS",
            port=443,
        )

        assert result is not None
        assert result["id"] == "lis-new"
        assert result["protocol"] == "HTTPS"

    def test_delete_listener_success(self, client, stub_openstack_connection):
        """delete_listener returns True on success."""
        result = client.delete_listener("lis-del")

        assert result is True
        stub_openstack_connection.load_balancer.delete_listener.assert_called_once_with(
            "lis-del"
        )

    # =====================================================================
    # Pool Operations
    # =====================================================================

    def test_create_pool_success(self, client, stub_openstack_connection):
        """create_pool returns id, name, and protocol."""
        stub_pool = Stub()
        stub_pool.id = "pool-new"
        stub_pool.name = "web-pool"
        stub_openstack_connection.load_balancer.create_pool.return_value = stub_pool

        result = client.create_pool(
            name="web-pool",
            protocol="HTTP",
            lb_algorithm="ROUND_ROBIN",
            listener_id="lis-1",
        )

        assert result is not None
        assert result["id"] == "pool-new"
        assert result["protocol"] == "HTTP"

    def test_delete_pool_success(self, client, stub_openstack_connection):
        """delete_pool returns True on success."""
        result = client.delete_pool("pool-del")

        assert result is True
        stub_openstack_connection.load_balancer.delete_pool.assert_called_once_with(
            "pool-del"
        )

    # =====================================================================
    # Pool Member Operations
    # =====================================================================

    def test_add_pool_member_success(self, client, stub_openstack_connection):
        """add_pool_member returns id, address, and port."""
        stub_member = Stub()
        stub_member.id = "mem-new"
        stub_openstack_connection.load_balancer.create_member.return_value = stub_member

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

    def test_remove_pool_member_success(self, client, stub_openstack_connection):
        """remove_pool_member returns True on success."""
        result = client.remove_pool_member("pool-1", "mem-del")

        assert result is True
        stub_openstack_connection.load_balancer.delete_member.assert_called_once_with(
            "mem-del", "pool-1"
        )

    # =====================================================================
    # Health Monitor Operations
    # =====================================================================

    def test_create_health_monitor_success(self, client, stub_openstack_connection):
        """create_health_monitor returns id, type, and pool_id."""
        stub_hm = Stub()
        stub_hm.id = "hm-new"
        stub_openstack_connection.load_balancer.create_health_monitor.return_value = (
            stub_hm
        )

        result = client.create_health_monitor(
            pool_id="pool-1",
            monitor_type="HTTP",
            delay=10,
            timeout=5,
            max_retries=3,
        )

        assert result is not None
        assert result["id"] == "hm-new"
        assert result["type"] == "HTTP"
        assert result["pool_id"] == "pool-1"

    def test_delete_health_monitor_success(self, client, stub_openstack_connection):
        """delete_health_monitor returns True on success."""
        result = client.delete_health_monitor("hm-del")

        assert result is True
        stub_openstack_connection.load_balancer.delete_health_monitor.assert_called_once_with(
            "hm-del"
        )


# =========================================================================


class TestInfomaniakNetworkClientExpanded:
    """Tests for InfomaniakNetworkClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.network import InfomaniakNetworkClient

        stub_conn = Stub()
        return InfomaniakNetworkClient(connection=stub_conn), stub_conn

    def test_create_subnet(self):
        client, mc = self._make_client()
        sn = Stub(id="sn1", name="sub1", cidr="10.0.0.0/24")
        mc.network.create_subnet.return_value = sn
        result = client.create_subnet("n1", "sub1", "10.0.0.0/24")
        assert result["id"] == "sn1"

    def test_create_router(self):
        client, mc = self._make_client()
        rt = Stub(id="rt1", name="router1")
        mc.network.create_router.return_value = rt
        result = client.create_router("router1")
        assert result["id"] == "rt1"

    def test_add_router_interface(self):
        client, mc = self._make_client()
        assert client.add_router_interface("rt1", "sn1") is True
        mc.network.add_interface_to_router.assert_called_once_with(
            "rt1", subnet_id="sn1"
        )

    def test_delete_router(self):
        client, mc = self._make_client()
        assert client.delete_router("rt1") is True
        mc.network.delete_router.assert_called_once_with("rt1")

    def test_create_security_group(self):
        client, mc = self._make_client()
        sg = Stub(id="sg1", name="web")
        mc.network.create_security_group.return_value = sg
        result = client.create_security_group("web")
        assert result["id"] == "sg1"

    def test_delete_security_group(self):
        client, _mc = self._make_client()
        assert client.delete_security_group("sg1") is True

    def test_allocate_floating_ip(self):
        client, mc = self._make_client()
        ext = Stub(id="ext1")
        mc.network.find_network.return_value = ext
        fip = Stub(id="fip1", floating_ip_address="1.2.3.4")
        mc.network.create_ip.return_value = fip
        result = client.allocate_floating_ip("external")
        assert result["floating_ip_address"] == "1.2.3.4"

    def test_associate_floating_ip(self):
        client, mc = self._make_client()
        assert client.associate_floating_ip("fip1", "port1") is True
        mc.network.update_ip.assert_called_once_with("fip1", port_id="port1")

    def test_create_loadbalancer(self):
        client, mc = self._make_client()
        lb = Stub(id="lb1", name="web-lb", vip_address="10.0.0.5")
        mc.load_balancer.create_load_balancer.return_value = lb
        result = client.create_loadbalancer("web-lb", "sn1")
        assert result["id"] == "lb1"

    def test_delete_loadbalancer(self):
        client, _mc = self._make_client()
        assert client.delete_loadbalancer("lb1") is True

    def test_list_subnets(self):
        client, mc = self._make_client()
        sn = Stub(
            id="sn1",
            name="s",
            network_id="n1",
            cidr="10.0.0.0/24",
            ip_version=4,
            gateway_ip="10.0.0.1",
            is_dhcp_enabled=True,
        )
        mc.network.subnets.return_value = [sn]
        result = client.list_subnets()
        assert len(result) == 1
        assert result[0]["id"] == "sn1"

    def test_get_subnet(self):
        client, mc = self._make_client()
        sn = Stub(
            id="sn1",
            name="s",
            network_id="n1",
            cidr="10.0.0.0/24",
            ip_version=4,
            gateway_ip="10.0.0.1",
        )
        mc.network.get_subnet.return_value = sn
        result = client.get_subnet("sn1")
        assert result["id"] == "sn1"

    def test_delete_subnet(self):
        client, _mc = self._make_client()
        assert client.delete_subnet("sn1") is True

    def test_release_floating_ip(self):
        client, mc = self._make_client()
        assert client.release_floating_ip("fip1") is True
        mc.network.delete_ip.assert_called_once_with("fip1")

    def test_disassociate_floating_ip(self):
        client, mc = self._make_client()
        assert client.disassociate_floating_ip("fip1") is True
        mc.network.update_ip.assert_called_once_with("fip1", port_id=None)

    def test_list_listeners(self):
        client, mc = self._make_client()
        li = Stub(id="li1", name="http", protocol="HTTP", protocol_port=80)
        mc.load_balancer.listeners.return_value = [li]
        result = client.list_listeners()
        assert len(result) == 1

    def test_create_listener(self):
        client, mc = self._make_client()
        li = Stub(id="li1", name="http")
        mc.load_balancer.create_listener.return_value = li
        result = client.create_listener("lb1", "http", "HTTP", 80)
        assert result["id"] == "li1"

    def test_delete_listener(self):
        client, _mc = self._make_client()
        assert client.delete_listener("li1") is True

    def test_list_pools(self):
        client, mc = self._make_client()
        p = Stub(id="p1", name="pool1", protocol="HTTP", lb_algorithm="ROUND_ROBIN")
        mc.load_balancer.pools.return_value = [p]
        result = client.list_pools()
        assert len(result) == 1

    def test_create_pool(self):
        client, mc = self._make_client()
        p = Stub(id="p1", name="pool1")
        mc.load_balancer.create_pool.return_value = p
        result = client.create_pool("pool1", "HTTP", "ROUND_ROBIN")
        assert result["id"] == "p1"

    def test_delete_pool(self):
        client, _mc = self._make_client()
        assert client.delete_pool("p1") is True

    def test_list_pool_members(self):
        client, mc = self._make_client()
        m = Stub(id="m1", name="srv1", address="10.0.0.2", protocol_port=80, weight=1)
        mc.load_balancer.members.return_value = [m]
        result = client.list_pool_members("p1")
        assert len(result) == 1

    def test_add_pool_member(self):
        client, mc = self._make_client()
        m = Stub(id="m1")
        mc.load_balancer.create_member.return_value = m
        result = client.add_pool_member("p1", "10.0.0.2", 80)
        assert result["id"] == "m1"

    def test_remove_pool_member(self):
        client, mc = self._make_client()
        assert client.remove_pool_member("p1", "m1") is True
        mc.load_balancer.delete_member.assert_called_once_with("m1", "p1")

    def test_list_health_monitors(self):
        client, mc = self._make_client()
        hm = Stub(
            id="hm1", name="check", type="HTTP", delay=5, timeout=3, max_retries=3
        )
        mc.load_balancer.health_monitors.return_value = [hm]
        result = client.list_health_monitors()
        assert len(result) == 1

    def test_create_health_monitor(self):
        """Uses renamed monitor_type parameter."""
        client, mc = self._make_client()
        hm = Stub(id="hm1")
        mc.load_balancer.create_health_monitor.return_value = hm
        result = client.create_health_monitor(
            "p1", monitor_type="HTTP", delay=5, timeout=3
        )
        assert result["id"] == "hm1"
        assert result["type"] == "HTTP"

    def test_delete_health_monitor(self):
        client, _mc = self._make_client()
        assert client.delete_health_monitor("hm1") is True

    def test_remove_router_interface(self):
        client, mc = self._make_client()
        assert client.remove_router_interface("rt1", "sn1") is True
        mc.network.remove_interface_from_router.assert_called_once_with(
            "rt1", subnet_id="sn1"
        )

    def test_remove_router_interface_error(self):
        client, mc = self._make_client()
        mc.network.remove_interface_from_router.side_effect = Exception("fail")
        assert client.remove_router_interface("rt1", "sn1") is False

    def test_list_networks_error(self):
        """list_networks returns [] on error."""
        client, mc = self._make_client()
        mc.network.networks.side_effect = Exception("fail")
        assert client.list_networks() == []

    # --- Error-path tests for get/create/delete methods ---

    def test_create_network_error(self):
        client, mc = self._make_client()
        mc.network.create_network.side_effect = Exception("fail")
        assert client.create_network("test") is None

    def test_delete_network_error(self):
        client, mc = self._make_client()
        mc.network.delete_network.side_effect = Exception("fail")
        assert client.delete_network("n1") is False

    def test_create_subnet_error(self):
        client, mc = self._make_client()
        mc.network.create_subnet.side_effect = Exception("fail")
        assert client.create_subnet("n1", "s1", "10.0.0.0/24") is None

    def test_get_subnet_error(self):
        client, mc = self._make_client()
        mc.network.get_subnet.side_effect = Exception("fail")
        assert client.get_subnet("sn1") is None

    def test_delete_subnet_error(self):
        client, mc = self._make_client()
        mc.network.delete_subnet.side_effect = Exception("fail")
        assert client.delete_subnet("sn1") is False

    def test_create_router_error(self):
        client, mc = self._make_client()
        mc.network.create_router.side_effect = Exception("fail")
        assert client.create_router("r1") is None

    def test_add_router_interface_error(self):
        client, mc = self._make_client()
        mc.network.add_interface_to_router.side_effect = Exception("fail")
        assert client.add_router_interface("rt1", "sn1") is False

    def test_delete_router_error(self):
        client, mc = self._make_client()
        mc.network.delete_router.side_effect = Exception("fail")
        assert client.delete_router("rt1") is False

    def test_create_security_group_error(self):
        client, mc = self._make_client()
        mc.network.create_security_group.side_effect = Exception("fail")
        assert client.create_security_group("sg") is None

    def test_delete_security_group_error(self):
        client, mc = self._make_client()
        mc.network.delete_security_group.side_effect = Exception("fail")
        assert client.delete_security_group("sg1") is False

    def test_allocate_floating_ip_error(self):
        client, mc = self._make_client()
        mc.network.find_network.side_effect = Exception("fail")
        assert client.allocate_floating_ip("ext-net") is None

    def test_create_loadbalancer_error(self):
        client, mc = self._make_client()
        mc.load_balancer.create_load_balancer.side_effect = Exception("fail")
        assert client.create_loadbalancer("lb", "sn1") is None

    def test_delete_loadbalancer_error(self):
        client, mc = self._make_client()
        mc.load_balancer.delete_load_balancer.side_effect = Exception("fail")
        assert client.delete_loadbalancer("lb1") is False

    def test_create_listener_error(self):
        client, mc = self._make_client()
        mc.load_balancer.create_listener.side_effect = Exception("fail")
        assert client.create_listener("lb1", "http", "HTTP", 80) is None

    def test_delete_listener_error(self):
        client, mc = self._make_client()
        mc.load_balancer.delete_listener.side_effect = Exception("fail")
        assert client.delete_listener("li1") is False

    def test_add_security_group_rule_error(self):
        client, mc = self._make_client()
        mc.network.create_security_group_rule.side_effect = Exception("fail")
        assert client.add_security_group_rule("sg1") is None


# =========================================================================
# ADDITIONAL OBJECT STORAGE (SWIFT) CLIENT TESTS
# =========================================================================
