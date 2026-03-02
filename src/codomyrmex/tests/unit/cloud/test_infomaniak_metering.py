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

    def test_service_name_is_metering(self, mock_openstack_connection):
        """The _service_name class attribute is set to 'metering'."""
        client = InfomaniakMeteringClient(mock_openstack_connection)
        assert client._service_name == "metering"

    # =====================================================================
    # Compute Usage
    # =====================================================================

    def test_get_compute_usage_single_server(self, mock_openstack_connection):
        """get_compute_usage sums vcpus/ram/disk from a single server's flavor."""
        mock_server = Stub()
        mock_server.flavor = {"id": "flavor-1"}

        mock_flavor = Stub()
        mock_flavor.vcpus = 4
        mock_flavor.ram = 8192
        mock_flavor.disk = 80

        mock_openstack_connection.compute.servers.return_value = [mock_server]
        mock_openstack_connection.compute.get_flavor.return_value = mock_flavor

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_compute_usage()

        assert usage["instance_count"] == 1
        assert usage["total_vcpus"] == 4
        assert usage["total_ram_mb"] == 8192
        assert usage["total_ram_gb"] == 8.0
        assert usage["total_disk_gb"] == 80

    def test_get_compute_usage_multiple_servers(self, mock_openstack_connection):
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

        mock_openstack_connection.compute.servers.return_value = [server_a, server_b]
        mock_openstack_connection.compute.get_flavor.side_effect = [flavor_a, flavor_b]

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_compute_usage()

        assert usage["instance_count"] == 2
        assert usage["total_vcpus"] == 10
        assert usage["total_ram_mb"] == 20480
        assert usage["total_disk_gb"] == 200

    def test_get_compute_usage_server_without_flavor(self, mock_openstack_connection):
        """Servers with flavor=None are counted but contribute zero resources."""
        server_with_flavor = Stub()
        server_with_flavor.flavor = {"id": "flavor-1"}

        server_no_flavor = Stub()
        server_no_flavor.flavor = None

        mock_flavor = Stub()
        mock_flavor.vcpus = 2
        mock_flavor.ram = 2048
        mock_flavor.disk = 20

        mock_openstack_connection.compute.servers.return_value = [
            server_with_flavor,
            server_no_flavor,
        ]
        mock_openstack_connection.compute.get_flavor.return_value = mock_flavor

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_compute_usage()

        assert usage["instance_count"] == 2
        assert usage["total_vcpus"] == 2
        assert usage["total_ram_mb"] == 2048

    def test_get_compute_usage_with_date_params(self, mock_openstack_connection):
        """get_compute_usage passes start/end as ISO strings in the result."""
        mock_openstack_connection.compute.servers.return_value = []

        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 1, 31, 23, 59, 59, tzinfo=UTC)

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_compute_usage(start=start, end=end)

        assert usage["period_start"] == start.isoformat()
        assert usage["period_end"] == end.isoformat()
        assert usage["instance_count"] == 0
        assert usage["total_vcpus"] == 0

    def test_get_compute_usage_error_returns_empty_dict(self, mock_openstack_connection):
        """Connection error during get_compute_usage returns {} instead of raising."""
        mock_openstack_connection.compute.servers.side_effect = Exception(
            "Service unavailable"
        )

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_compute_usage()

        assert usage == {}

    # =====================================================================
    # Storage Usage
    # =====================================================================

    def test_get_storage_usage(self, mock_openstack_connection):
        """get_storage_usage sums sizes and counts attached/unattached volumes."""
        vol_attached = Stub()
        vol_attached.size = 100
        vol_attached.attachments = [{"id": "att-1"}]

        vol_unattached = Stub()
        vol_unattached.size = 50
        vol_unattached.attachments = []

        mock_openstack_connection.block_storage.volumes.return_value = [
            vol_attached,
            vol_unattached,
        ]

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_storage_usage()

        assert usage["volume_count"] == 2
        assert usage["total_size_gb"] == 150
        assert usage["attached_count"] == 1
        assert usage["unattached_count"] == 1

    def test_get_storage_usage_empty(self, mock_openstack_connection):
        """get_storage_usage with no volumes returns zero counts."""
        mock_openstack_connection.block_storage.volumes.return_value = []

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_storage_usage()

        assert usage["volume_count"] == 0
        assert usage["total_size_gb"] == 0
        assert usage["attached_count"] == 0
        assert usage["unattached_count"] == 0

    def test_get_storage_usage_error_returns_empty_dict(self, mock_openstack_connection):
        """Connection error during get_storage_usage returns {} instead of raising."""
        mock_openstack_connection.block_storage.volumes.side_effect = Exception(
            "API timeout"
        )

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_storage_usage()

        assert usage == {}

    # =====================================================================
    # Network Usage
    # =====================================================================

    def test_get_network_usage(self, mock_openstack_connection):
        """get_network_usage counts networks, routers, SGs, FIPs, and FIPs in use."""
        fip_in_use = Stub()
        fip_in_use.port_id = "port-123"

        fip_unused = Stub()
        fip_unused.port_id = None

        mock_openstack_connection.network.networks.return_value = [
            Stub(),
            Stub(),
        ]
        mock_openstack_connection.network.routers.return_value = [Stub()]
        mock_openstack_connection.network.security_groups.return_value = [
            Stub(),
            Stub(),
            Stub(),
        ]
        mock_openstack_connection.network.ips.return_value = [fip_in_use, fip_unused]

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_network_usage()

        assert usage["network_count"] == 2
        assert usage["router_count"] == 1
        assert usage["security_group_count"] == 3
        assert usage["floating_ip_count"] == 2
        assert usage["floating_ips_in_use"] == 1

    def test_get_network_usage_all_fips_unused(self, mock_openstack_connection):
        """When all floating IPs have port_id=None, floating_ips_in_use is 0."""
        fip_a = Stub()
        fip_a.port_id = None
        fip_b = Stub()
        fip_b.port_id = None

        mock_openstack_connection.network.networks.return_value = []
        mock_openstack_connection.network.routers.return_value = []
        mock_openstack_connection.network.security_groups.return_value = []
        mock_openstack_connection.network.ips.return_value = [fip_a, fip_b]

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_network_usage()

        assert usage["floating_ip_count"] == 2
        assert usage["floating_ips_in_use"] == 0

    def test_get_network_usage_error_returns_empty_dict(self, mock_openstack_connection):
        """Connection error during get_network_usage returns {} instead of raising."""
        mock_openstack_connection.network.networks.side_effect = Exception(
            "Connection refused"
        )

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_network_usage()

        assert usage == {}

    # =====================================================================
    # Object Storage Usage
    # =====================================================================

    def test_get_object_storage_usage(self, mock_openstack_connection):
        """get_object_storage_usage sums container counts and bytes."""
        container_a = Stub()
        container_a.count = 100
        container_a.bytes = 1024 * 1024 * 500  # 500 MB

        container_b = Stub()
        container_b.count = 50
        container_b.bytes = 1024 * 1024 * 250  # 250 MB

        mock_openstack_connection.object_store.containers.return_value = [
            container_a,
            container_b,
        ]

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_object_storage_usage()

        assert usage["container_count"] == 2
        assert usage["object_count"] == 150
        assert usage["total_bytes"] == 1024 * 1024 * 750
        assert usage["total_size_gb"] > 0

    def test_get_object_storage_usage_error_returns_empty_dict(
        self, mock_openstack_connection
    ):
        """Connection error during get_object_storage_usage returns {}."""
        mock_openstack_connection.object_store.containers.side_effect = Exception(
            "Auth expired"
        )

        client = InfomaniakMeteringClient(mock_openstack_connection)
        usage = client.get_object_storage_usage()

        assert usage == {}

    # =====================================================================
    # Comprehensive Usage (get_all_usage)
    # =====================================================================

    def test_get_all_usage_structure(self, mock_openstack_connection):
        """get_all_usage returns compute, storage, network, object_storage, and timestamp."""
        # Set up minimal mocks so sub-methods succeed
        mock_openstack_connection.compute.servers.return_value = []
        mock_openstack_connection.block_storage.volumes.return_value = []
        mock_openstack_connection.network.networks.return_value = []
        mock_openstack_connection.network.routers.return_value = []
        mock_openstack_connection.network.security_groups.return_value = []
        mock_openstack_connection.network.ips.return_value = []
        mock_openstack_connection.object_store.containers.return_value = []

        client = InfomaniakMeteringClient(mock_openstack_connection)
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

    def test_list_resources_with_usage_partial_failure(
        self, mock_openstack_connection
    ):
        """When compute fails, volumes and FIPs still appear in the result."""
        # Compute raises
        mock_openstack_connection.compute.servers.side_effect = Exception(
            "Compute API down"
        )

        # Volumes succeed
        mock_vol = Stub()
        mock_vol.id = "vol-100"
        mock_vol.name = "data-vol"
        mock_vol.status = "in-use"
        mock_vol.size = 200
        mock_openstack_connection.block_storage.volumes.return_value = [mock_vol]

        # Floating IPs succeed
        mock_fip = Stub()
        mock_fip.id = "fip-200"
        mock_fip.floating_ip_address = "195.15.220.50"
        mock_fip.status = "ACTIVE"
        mock_fip.port_id = "port-xyz"
        mock_openstack_connection.network.ips.return_value = [mock_fip]

        client = InfomaniakMeteringClient(mock_openstack_connection)
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

    def test_get_compute_quotas(self, mock_openstack_connection):
        """get_compute_quotas returns instance, core, ram, keypair, server_group limits."""
        mock_quotas = Stub()
        mock_quotas.instances = 20
        mock_quotas.cores = 80
        mock_quotas.ram = 204800
        mock_quotas.key_pairs = 100
        mock_quotas.server_groups = 10

        mock_openstack_connection.compute.get_quota_set.return_value = mock_quotas

        client = InfomaniakMeteringClient(mock_openstack_connection)
        quotas = client.get_compute_quotas()

        assert quotas["instances"] == 20
        assert quotas["cores"] == 80
        assert quotas["ram_mb"] == 204800
        assert quotas["key_pairs"] == 100
        assert quotas["server_groups"] == 10

        mock_openstack_connection.compute.get_quota_set.assert_called_once_with(
            "proj-test-456"
        )

    def test_get_network_quotas(self, mock_openstack_connection):
        """get_network_quotas returns network/subnet/router/FIP/SG limits."""
        mock_quotas = Stub()
        mock_quotas.networks = 50
        mock_quotas.subnets = 100
        mock_quotas.routers = 10
        mock_quotas.floatingips = 20
        mock_quotas.security_groups = 50
        mock_quotas.security_group_rules = 500

        mock_openstack_connection.network.get_quota.return_value = mock_quotas

        client = InfomaniakMeteringClient(mock_openstack_connection)
        quotas = client.get_network_quotas()

        assert quotas["networks"] == 50
        assert quotas["subnets"] == 100
        assert quotas["routers"] == 10
        assert quotas["floating_ips"] == 20
        assert quotas["security_groups"] == 50
        assert quotas["security_group_rules"] == 500

        mock_openstack_connection.network.get_quota.assert_called_once_with(
            "proj-test-456"
        )

    def test_get_storage_quotas(self, mock_openstack_connection):
        """get_storage_quotas returns volume/gigabyte/snapshot/backup limits."""
        mock_quotas = Stub()
        mock_quotas.volumes = 50
        mock_quotas.gigabytes = 5000
        mock_quotas.snapshots = 100
        mock_quotas.backups = 50

        mock_openstack_connection.block_storage.get_quota_set.return_value = mock_quotas

        client = InfomaniakMeteringClient(mock_openstack_connection)
        quotas = client.get_storage_quotas()

        assert quotas["volumes"] == 50
        assert quotas["gigabytes"] == 5000
        assert quotas["snapshots"] == 100
        assert quotas["backups"] == 50

        mock_openstack_connection.block_storage.get_quota_set.assert_called_once_with(
            "proj-test-456"
        )

    def test_get_compute_quotas_error_returns_empty_dict(
        self, mock_openstack_connection
    ):
        """Exception during get_compute_quotas returns {} instead of raising."""
        mock_openstack_connection.compute.get_quota_set.side_effect = Exception(
            "Forbidden"
        )

        client = InfomaniakMeteringClient(mock_openstack_connection)
        quotas = client.get_compute_quotas()

        assert quotas == {}


# =========================================================================

class TestInfomaniakMeteringClientExpanded:
    """Tests for InfomaniakMeteringClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.metering import InfomaniakMeteringClient
        mock_conn = Stub()
        mock_conn.current_project_id = "proj-1"
        return InfomaniakMeteringClient(connection=mock_conn), mock_conn

    def test_get_object_storage_usage(self):
        """Test functionality: get object storage usage."""
        client, mc = self._make_client()
        c = Stub(count=100, bytes=2048000)
        mc.object_store.containers.return_value = [c]
        result = client.get_object_storage_usage()
        assert result["container_count"] == 1
        assert result["object_count"] == 100
        assert result["total_bytes"] == 2048000

    def test_list_resources_with_usage(self):
        """Test functionality: list resources with usage."""
        client, mc = self._make_client()
        srv = Stub(id="s1", name="web", status="ACTIVE", created_at=None)
        vol = Stub(id="v1", name="data", status="in-use", size=50)
        fip = Stub(id="f1", floating_ip_address="1.2.3.4", status="ACTIVE", port_id="p1")
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
        """Test functionality: get network quotas."""
        client, mc = self._make_client()
        q = Stub(networks=10, subnets=20, routers=5,
                      floatingips=3, security_groups=10, security_group_rules=50)
        mc.network.get_quota.return_value = q
        result = client.get_network_quotas()
        assert result["networks"] == 10
        assert result["floating_ips"] == 3

    def test_get_storage_quotas(self):
        """Test functionality: get storage quotas."""
        client, mc = self._make_client()
        q = Stub(volumes=20, gigabytes=1000, snapshots=10, backups=5)
        mc.block_storage.get_quota_set.return_value = q
        result = client.get_storage_quotas()
        assert result["volumes"] == 20
        assert result["gigabytes"] == 1000

    def test_get_compute_usage_error(self):
        """Test functionality: get compute usage error."""
        client, mc = self._make_client()
        mc.compute.servers.side_effect = Exception("fail")
        assert client.get_compute_usage() == {}


# =========================================================================
# FACTORY METHOD TESTS FOR REMAINING CLIENTS
# =========================================================================
