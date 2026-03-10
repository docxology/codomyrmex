"""
Unit tests for Infomaniak Metering Client.

Tests cover:
- Base class inheritance and service name
- Compute usage (happy path, multiple servers, no-flavor, date params, error)
- Storage usage (happy path, empty volumes, error)
- Network usage (happy path, all FIPs unused, error)
- Object storage usage (happy path, error)
- Comprehensive usage (get_all_usage structure and timestamp)
- Resource listing with partial failure
- Quotas: compute, network, storage, and error paths

Total: ~19 tests in a single TestInfomaniakMetering class.
"""

from datetime import UTC, datetime

from _stubs import Stub

from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase
from codomyrmex.cloud.infomaniak.metering.client import InfomaniakMeteringClient


class TestInfomaniakMetering:
    """Comprehensive tests for InfomaniakMeteringClient."""

    # =====================================================================
    # Base Class & Service Name
    # =====================================================================

    def test_inherits_from_openstack_base(self):
        """InfomaniakMeteringClient inherits from InfomaniakOpenStackBase."""
        assert issubclass(InfomaniakMeteringClient, InfomaniakOpenStackBase)

    def test_service_name_is_metering(self, stub_openstack_connection):
        """The _service_name class attribute is set to 'metering'."""
        client = InfomaniakMeteringClient(stub_openstack_connection)
        assert client._service_name == "metering"

    # =====================================================================
    # Compute Usage
    # =====================================================================

    def test_get_compute_usage_single_server(self, stub_openstack_connection):
        """get_compute_usage sums vcpus/ram/disk from a single server's flavor."""
        stub_server = Stub()
        stub_server.flavor = {"id": "flavor-1"}

        stub_flavor = Stub()
        stub_flavor.vcpus = 4
        stub_flavor.ram = 8192
        stub_flavor.disk = 80

        stub_openstack_connection.compute.servers.return_value = [stub_server]
        stub_openstack_connection.compute.get_flavor.return_value = stub_flavor

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_compute_usage()

        assert usage["instance_count"] == 1
        assert usage["total_vcpus"] == 4
        assert usage["total_ram_mb"] == 8192
        assert usage["total_ram_gb"] == 8.0
        assert usage["total_disk_gb"] == 80

    def test_get_compute_usage_multiple_servers(self, stub_openstack_connection):
        """get_compute_usage aggregates resources across multiple servers."""
        server_a = Stub()
        server_a.flavor = {"id": "flavor-a"}
        server_b = Stub()
        server_b.flavor = {"id": "flavor-b"}

        flavor_a = Stub()
        flavor_a.vcpus = 2
        flavor_a.ram = 4096
        flavor_a.disk = 40

        flavor_b = Stub()
        flavor_b.vcpus = 8
        flavor_b.ram = 16384
        flavor_b.disk = 160

        stub_openstack_connection.compute.servers.return_value = [server_a, server_b]
        stub_openstack_connection.compute.get_flavor.side_effect = [flavor_a, flavor_b]

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_compute_usage()

        assert usage["instance_count"] == 2
        assert usage["total_vcpus"] == 10
        assert usage["total_ram_mb"] == 20480
        assert usage["total_disk_gb"] == 200

    def test_get_compute_usage_server_without_flavor(self, stub_openstack_connection):
        """Servers with flavor=None are counted but contribute zero resources."""
        server_with_flavor = Stub()
        server_with_flavor.flavor = {"id": "flavor-1"}

        server_no_flavor = Stub()
        server_no_flavor.flavor = None

        stub_flavor = Stub()
        stub_flavor.vcpus = 2
        stub_flavor.ram = 2048
        stub_flavor.disk = 20

        stub_openstack_connection.compute.servers.return_value = [
            server_with_flavor,
            server_no_flavor,
        ]
        stub_openstack_connection.compute.get_flavor.return_value = stub_flavor

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_compute_usage()

        assert usage["instance_count"] == 2
        assert usage["total_vcpus"] == 2
        assert usage["total_ram_mb"] == 2048

    def test_get_compute_usage_with_date_params(self, stub_openstack_connection):
        """get_compute_usage passes start/end as ISO strings in the result."""
        stub_openstack_connection.compute.servers.return_value = []

        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 1, 31, 23, 59, 59, tzinfo=UTC)

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_compute_usage(start=start, end=end)

        assert usage["period_start"] == start.isoformat()
        assert usage["period_end"] == end.isoformat()
        assert usage["instance_count"] == 0
        assert usage["total_vcpus"] == 0

    def test_get_compute_usage_error_returns_empty_dict(
        self, stub_openstack_connection
    ):
        """Connection error during get_compute_usage returns {} instead of raising."""
        stub_openstack_connection.compute.servers.side_effect = Exception(
            "Service unavailable"
        )

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_compute_usage()

        assert usage == {}

    # =====================================================================
    # Storage Usage
    # =====================================================================

    def test_get_storage_usage(self, stub_openstack_connection):
        """get_storage_usage sums sizes and counts attached/unattached volumes."""
        vol_attached = Stub()
        vol_attached.size = 100
        vol_attached.attachments = [{"id": "att-1"}]

        vol_unattached = Stub()
        vol_unattached.size = 50
        vol_unattached.attachments = []

        stub_openstack_connection.block_storage.volumes.return_value = [
            vol_attached,
            vol_unattached,
        ]

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_storage_usage()

        assert usage["volume_count"] == 2
        assert usage["total_size_gb"] == 150
        assert usage["attached_count"] == 1
        assert usage["unattached_count"] == 1

    def test_get_storage_usage_empty(self, stub_openstack_connection):
        """get_storage_usage with no volumes returns zero counts."""
        stub_openstack_connection.block_storage.volumes.return_value = []

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_storage_usage()

        assert usage["volume_count"] == 0
        assert usage["total_size_gb"] == 0
        assert usage["attached_count"] == 0
        assert usage["unattached_count"] == 0

    def test_get_storage_usage_error_returns_empty_dict(
        self, stub_openstack_connection
    ):
        """Connection error during get_storage_usage returns {} instead of raising."""
        stub_openstack_connection.block_storage.volumes.side_effect = Exception(
            "API timeout"
        )

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_storage_usage()

        assert usage == {}

    # =====================================================================
    # Network Usage
    # =====================================================================

    def test_get_network_usage(self, stub_openstack_connection):
        """get_network_usage counts networks, routers, SGs, FIPs, and FIPs in use."""
        fip_in_use = Stub()
        fip_in_use.port_id = "port-123"

        fip_unused = Stub()
        fip_unused.port_id = None

        stub_openstack_connection.network.networks.return_value = [
            Stub(),
            Stub(),
        ]
        stub_openstack_connection.network.routers.return_value = [Stub()]
        stub_openstack_connection.network.security_groups.return_value = [
            Stub(),
            Stub(),
            Stub(),
        ]
        stub_openstack_connection.network.ips.return_value = [fip_in_use, fip_unused]

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_network_usage()

        assert usage["network_count"] == 2
        assert usage["router_count"] == 1
        assert usage["security_group_count"] == 3
        assert usage["floating_ip_count"] == 2
        assert usage["floating_ips_in_use"] == 1

    def test_get_network_usage_all_fips_unused(self, stub_openstack_connection):
        """When all floating IPs have port_id=None, floating_ips_in_use is 0."""
        fip_a = Stub()
        fip_a.port_id = None
        fip_b = Stub()
        fip_b.port_id = None

        stub_openstack_connection.network.networks.return_value = []
        stub_openstack_connection.network.routers.return_value = []
        stub_openstack_connection.network.security_groups.return_value = []
        stub_openstack_connection.network.ips.return_value = [fip_a, fip_b]

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_network_usage()

        assert usage["floating_ip_count"] == 2
        assert usage["floating_ips_in_use"] == 0

    def test_get_network_usage_error_returns_empty_dict(
        self, stub_openstack_connection
    ):
        """Connection error during get_network_usage returns {} instead of raising."""
        stub_openstack_connection.network.networks.side_effect = Exception(
            "Connection refused"
        )

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_network_usage()

        assert usage == {}

    # =====================================================================
    # Object Storage Usage
    # =====================================================================

    def test_get_object_storage_usage(self, stub_openstack_connection):
        """get_object_storage_usage sums container counts and bytes."""
        container_a = Stub()
        container_a.count = 100
        container_a.bytes = 1024 * 1024 * 500  # 500 MB

        container_b = Stub()
        container_b.count = 50
        container_b.bytes = 1024 * 1024 * 250  # 250 MB

        stub_openstack_connection.object_store.containers.return_value = [
            container_a,
            container_b,
        ]

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_object_storage_usage()

        assert usage["container_count"] == 2
        assert usage["object_count"] == 150
        assert usage["total_bytes"] == 1024 * 1024 * 750
        assert usage["total_size_gb"] > 0

    def test_get_object_storage_usage_error_returns_empty_dict(
        self, stub_openstack_connection
    ):
        """Connection error during get_object_storage_usage returns {}."""
        stub_openstack_connection.object_store.containers.side_effect = Exception(
            "Auth expired"
        )

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_object_storage_usage()

        assert usage == {}

    # =====================================================================
    # Comprehensive Usage (get_all_usage)
    # =====================================================================

    def test_get_all_usage_structure(self, stub_openstack_connection):
        """get_all_usage returns compute, storage, network, object_storage, and timestamp."""
        # Set up minimal stubs so sub-methods succeed
        stub_openstack_connection.compute.servers.return_value = []
        stub_openstack_connection.block_storage.volumes.return_value = []
        stub_openstack_connection.network.networks.return_value = []
        stub_openstack_connection.network.routers.return_value = []
        stub_openstack_connection.network.security_groups.return_value = []
        stub_openstack_connection.network.ips.return_value = []
        stub_openstack_connection.object_store.containers.return_value = []

        client = InfomaniakMeteringClient(stub_openstack_connection)
        usage = client.get_all_usage()

        assert "compute" in usage
        assert "storage" in usage
        assert "network" in usage
        assert "object_storage" in usage
        assert "timestamp" in usage

        # Timestamp should be timezone-aware UTC (contains +00:00)
        assert "+00:00" in usage["timestamp"] or "Z" in usage["timestamp"]

    # =====================================================================
    # Resource Listing
    # =====================================================================

    def test_list_resources_with_usage_partial_failure(self, stub_openstack_connection):
        """When compute fails, volumes and FIPs still appear in the result."""
        # Compute raises
        stub_openstack_connection.compute.servers.side_effect = Exception(
            "Compute API down"
        )

        # Volumes succeed
        stub_vol = Stub()
        stub_vol.id = "vol-100"
        stub_vol.name = "data-vol"
        stub_vol.status = "in-use"
        stub_vol.size = 200
        stub_openstack_connection.block_storage.volumes.return_value = [stub_vol]

        # Floating IPs succeed
        stub_fip = Stub()
        stub_fip.id = "fip-200"
        stub_fip.floating_ip_address = "195.15.220.50"
        stub_fip.status = "ACTIVE"
        stub_fip.port_id = "port-xyz"
        stub_openstack_connection.network.ips.return_value = [stub_fip]

        client = InfomaniakMeteringClient(stub_openstack_connection)
        resources = client.list_resources_with_usage()

        # No compute instances due to error, but volumes and FIPs present
        types = [r["type"] for r in resources]
        assert "compute.instance" not in types
        assert "storage.volume" in types
        assert "network.floating_ip" in types

        vol_entry = next(r for r in resources if r["type"] == "storage.volume")
        assert vol_entry["id"] == "vol-100"
        assert vol_entry["size_gb"] == 200

        fip_entry = next(r for r in resources if r["type"] == "network.floating_ip")
        assert fip_entry["address"] == "195.15.220.50"
        assert fip_entry["in_use"] is True

    # =====================================================================
    # Quotas
    # =====================================================================

    def test_get_compute_quotas(self, stub_openstack_connection):
        """get_compute_quotas returns instance, core, ram, keypair, server_group limits."""
        stub_quotas = Stub()
        stub_quotas.instances = 20
        stub_quotas.cores = 80
        stub_quotas.ram = 204800
        stub_quotas.key_pairs = 100
        stub_quotas.server_groups = 10

        stub_openstack_connection.compute.get_quota_set.return_value = stub_quotas

        client = InfomaniakMeteringClient(stub_openstack_connection)
        quotas = client.get_compute_quotas()

        assert quotas["instances"] == 20
        assert quotas["cores"] == 80
        assert quotas["ram_mb"] == 204800
        assert quotas["key_pairs"] == 100
        assert quotas["server_groups"] == 10

        stub_openstack_connection.compute.get_quota_set.assert_called_once_with(
            "proj-test-456"
        )

    def test_get_network_quotas(self, stub_openstack_connection):
        """get_network_quotas returns network/subnet/router/FIP/SG limits."""
        stub_quotas = Stub()
        stub_quotas.networks = 50
        stub_quotas.subnets = 100
        stub_quotas.routers = 10
        stub_quotas.floatingips = 20
        stub_quotas.security_groups = 50
        stub_quotas.security_group_rules = 500

        stub_openstack_connection.network.get_quota.return_value = stub_quotas

        client = InfomaniakMeteringClient(stub_openstack_connection)
        quotas = client.get_network_quotas()

        assert quotas["networks"] == 50
        assert quotas["subnets"] == 100
        assert quotas["routers"] == 10
        assert quotas["floating_ips"] == 20
        assert quotas["security_groups"] == 50
        assert quotas["security_group_rules"] == 500

        stub_openstack_connection.network.get_quota.assert_called_once_with(
            "proj-test-456"
        )

    def test_get_storage_quotas(self, stub_openstack_connection):
        """get_storage_quotas returns volume/gigabyte/snapshot/backup limits."""
        stub_quotas = Stub()
        stub_quotas.volumes = 50
        stub_quotas.gigabytes = 5000
        stub_quotas.snapshots = 100
        stub_quotas.backups = 50

        stub_openstack_connection.block_storage.get_quota_set.return_value = stub_quotas

        client = InfomaniakMeteringClient(stub_openstack_connection)
        quotas = client.get_storage_quotas()

        assert quotas["volumes"] == 50
        assert quotas["gigabytes"] == 5000
        assert quotas["snapshots"] == 100
        assert quotas["backups"] == 50

        stub_openstack_connection.block_storage.get_quota_set.assert_called_once_with(
            "proj-test-456"
        )

    def test_get_compute_quotas_error_returns_empty_dict(
        self, stub_openstack_connection
    ):
        """Exception during get_compute_quotas returns {} instead of raising."""
        stub_openstack_connection.compute.get_quota_set.side_effect = Exception(
            "Forbidden"
        )

        client = InfomaniakMeteringClient(stub_openstack_connection)
        quotas = client.get_compute_quotas()

        assert quotas == {}


# =========================================================================


class TestInfomaniakMeteringClientExpanded:
    """Tests for InfomaniakMeteringClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.metering import InfomaniakMeteringClient

        stub_conn = Stub()
        stub_conn.current_project_id = "proj-1"
        return InfomaniakMeteringClient(connection=stub_conn), stub_conn

    def test_get_object_storage_usage(self):
        client, mc = self._make_client()
        c = Stub(count=100, bytes=2048000)
        mc.object_store.containers.return_value = [c]
        result = client.get_object_storage_usage()
        assert result["container_count"] == 1
        assert result["object_count"] == 100
        assert result["total_bytes"] == 2048000

    def test_list_resources_with_usage(self):
        client, mc = self._make_client()
        srv = Stub(id="s1", name="web", status="ACTIVE", created_at=None)
        vol = Stub(id="v1", name="data", status="in-use", size=50)
        fip = Stub(
            id="f1", floating_ip_address="1.2.3.4", status="ACTIVE", port_id="p1"
        )
        mc.compute.servers.return_value = [srv]
        mc.block_storage.volumes.return_value = [vol]
        mc.network.ips.return_value = [fip]
        result = client.list_resources_with_usage()
        assert len(result) == 3
        types = [r["type"] for r in result]
        assert "compute.instance" in types
        assert "storage.volume" in types
        assert "network.floating_ip" in types

    def test_get_network_quotas(self):
        client, mc = self._make_client()
        q = Stub(
            networks=10,
            subnets=20,
            routers=5,
            floatingips=3,
            security_groups=10,
            security_group_rules=50,
        )
        mc.network.get_quota.return_value = q
        result = client.get_network_quotas()
        assert result["networks"] == 10
        assert result["floating_ips"] == 3

    def test_get_storage_quotas(self):
        client, mc = self._make_client()
        q = Stub(volumes=20, gigabytes=1000, snapshots=10, backups=5)
        mc.block_storage.get_quota_set.return_value = q
        result = client.get_storage_quotas()
        assert result["volumes"] == 20
        assert result["gigabytes"] == 1000

    def test_get_compute_usage_error(self):
        client, mc = self._make_client()
        mc.compute.servers.side_effect = Exception("fail")
        assert client.get_compute_usage() == {}


# =========================================================================
# FACTORY METHOD TESTS FOR REMAINING CLIENTS
# =========================================================================
