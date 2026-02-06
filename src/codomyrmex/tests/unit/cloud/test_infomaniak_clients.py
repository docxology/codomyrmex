"""
Unit tests for Infomaniak cloud clients.

Tests cover:
- InfomaniakComputeClient
- InfomaniakVolumeClient
- InfomaniakNetworkClient
- InfomaniakObjectStorageClient (Swift) / InfomaniakS3Client (S3)
- InfomaniakIdentityClient
- InfomaniakDNSClient
- InfomaniakHeatClient
- InfomaniakMeteringClient
- InfomaniakNewsletterClient (42 tests with instance-level mocking)
- Exception hierarchy and error classification
- classify_openstack_error (20 tests) and classify_http_error (12 tests)
- Base classes: OpenStackBase, S3Base, RESTBase (context manager, close, validate)
- Authentication utilities (create_openstack_connection, create_s3_client)
- Factory methods (from_credentials)
- Module-level exports and CloudConfig integration

Total: 316 tests across 33 test classes.
"""

from unittest.mock import MagicMock, patch

import pytest

# =========================================================================
# Test Authentication Module
# =========================================================================

class TestInfomaniakCredentials:
    """Tests for InfomaniakCredentials dataclass."""

    def test_credentials_from_env(self):
        """Test loading credentials from environment variables."""
        with patch.dict("os.environ", {
            "INFOMANIAK_APP_CREDENTIAL_ID": "test-id",
            "INFOMANIAK_APP_CREDENTIAL_SECRET": "test-secret",
            "INFOMANIAK_AUTH_URL": "https://test.api/identity/v3/",
            "INFOMANIAK_REGION": "dc3-b",
        }):
            from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

            creds = InfomaniakCredentials.from_env()

            assert creds.application_credential_id == "test-id"
            assert creds.application_credential_secret == "test-secret"
            assert creds.auth_url == "https://test.api/identity/v3/"
            assert creds.region == "dc3-b"

    def test_s3_credentials_from_env(self):
        """Test loading S3 credentials from environment variables."""
        with patch.dict("os.environ", {
            "INFOMANIAK_S3_ACCESS_KEY": "s3-access",
            "INFOMANIAK_S3_SECRET_KEY": "s3-secret",
            "INFOMANIAK_S3_ENDPOINT": "https://s3.test.cloud/",
        }):
            from codomyrmex.cloud.infomaniak.auth import InfomaniakS3Credentials

            creds = InfomaniakS3Credentials.from_env()

            assert creds.access_key == "s3-access"
            assert creds.secret_key == "s3-secret"
            assert creds.endpoint_url == "https://s3.test.cloud/"


# =========================================================================
# Test Auth Error Paths
# =========================================================================

class TestAuthErrorPaths:
    """Tests for authentication error paths and defaults."""

    def test_credentials_missing_env_vars(self):
        """Missing INFOMANIAK_APP_CREDENTIAL_ID/SECRET raises InfomaniakAuthError."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakAuthError,
            InfomaniakCredentials,
        )

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(InfomaniakAuthError, match="Missing required environment variables"):
                InfomaniakCredentials.from_env()

    def test_s3_credentials_missing_env_vars(self):
        """Missing INFOMANIAK_S3_ACCESS_KEY/SECRET raises InfomaniakAuthError."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakAuthError,
            InfomaniakS3Credentials,
        )

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(InfomaniakAuthError, match="Missing required environment variables"):
                InfomaniakS3Credentials.from_env()

    def test_credentials_default_values(self):
        """Credentials use correct default auth_url and region when not overridden."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        with patch.dict("os.environ", {
            "INFOMANIAK_APP_CREDENTIAL_ID": "id-123",
            "INFOMANIAK_APP_CREDENTIAL_SECRET": "secret-456",
        }, clear=True):
            creds = InfomaniakCredentials.from_env()

            assert creds.auth_url == "https://api.pub1.infomaniak.cloud/identity/v3/"
            assert creds.region == "dc3-a"
            assert creds.project_id is None

    def test_s3_credentials_default_values(self):
        """S3 credentials use correct default endpoint and region when not overridden."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakS3Credentials

        with patch.dict("os.environ", {
            "INFOMANIAK_S3_ACCESS_KEY": "s3-key",
            "INFOMANIAK_S3_SECRET_KEY": "s3-secret",
        }, clear=True):
            creds = InfomaniakS3Credentials.from_env()

            assert creds.endpoint_url == "https://s3.pub1.infomaniak.cloud/"
            assert creds.region == "us-east-1"


# =========================================================================
# Test Factory Methods (from_credentials)
# =========================================================================

class TestFactoryMethods:
    """Tests for from_credentials class methods on various clients."""

    def test_compute_from_credentials(self):
        """Compute.from_credentials creates InfomaniakCredentials and calls create_openstack_connection."""
        with patch(
            "codomyrmex.cloud.infomaniak.auth.InfomaniakCredentials"
        ) as MockCreds, patch(
            "codomyrmex.cloud.infomaniak.auth.create_openstack_connection"
        ) as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

            client = InfomaniakComputeClient.from_credentials(
                application_credential_id="cred-id",
                application_credential_secret="cred-secret",
                region="dc3-b",
            )

            MockCreds.assert_called_once()
            mock_connect.assert_called_once()
            assert client._conn is mock_conn

    def test_s3_from_credentials(self):
        """S3Client.from_credentials calls boto3.client correctly."""
        import sys
        mock_boto3_module = MagicMock()
        mock_s3 = MagicMock()
        mock_boto3_module.client.return_value = mock_s3
        with patch.dict(sys.modules, {"boto3": mock_boto3_module}):
            from codomyrmex.cloud.infomaniak.object_storage import InfomaniakS3Client

            client = InfomaniakS3Client.from_credentials(
                access_key="ak-123",
                secret_key="sk-456",
                endpoint_url="https://s3.custom.cloud/",
                region="eu-west-1",
            )

            mock_boto3_module.client.assert_called_once_with(
                "s3",
                endpoint_url="https://s3.custom.cloud/",
                aws_access_key_id="ak-123",
                aws_secret_access_key="sk-456",
                region_name="eu-west-1",
            )
            assert client._client is mock_s3

    def test_object_storage_from_credentials(self):
        """ObjectStorageClient.from_credentials calls create_openstack_connection."""
        with patch(
            "codomyrmex.cloud.infomaniak.auth.InfomaniakCredentials"
        ) as MockCreds, patch(
            "codomyrmex.cloud.infomaniak.auth.create_openstack_connection"
        ) as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            from codomyrmex.cloud.infomaniak.object_storage import (
                InfomaniakObjectStorageClient,
            )

            client = InfomaniakObjectStorageClient.from_credentials(
                application_credential_id="oc-id",
                application_credential_secret="oc-secret",
            )

            MockCreds.assert_called_once()
            mock_connect.assert_called_once()
            assert client._conn is mock_conn

    def test_identity_from_credentials(self):
        """IdentityClient.from_credentials calls create_openstack_connection."""
        with patch(
            "codomyrmex.cloud.infomaniak.auth.InfomaniakCredentials"
        ) as MockCreds, patch(
            "codomyrmex.cloud.infomaniak.auth.create_openstack_connection"
        ) as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn

            from codomyrmex.cloud.infomaniak.identity import InfomaniakIdentityClient

            client = InfomaniakIdentityClient.from_credentials(
                application_credential_id="id-id",
                application_credential_secret="id-secret",
                region="dc3-b",
            )

            MockCreds.assert_called_once()
            mock_connect.assert_called_once()
            assert client._conn is mock_conn


# =========================================================================
# Test Compute Client
# =========================================================================

class TestInfomaniakComputeClient:
    """Tests for InfomaniakComputeClient."""

    @pytest.fixture
    def mock_connection(self):
        """Create a mock OpenStack connection."""
        return MagicMock()

    def _make_mock_server(
        self,
        server_id="server-123",
        name="test-server",
        status="ACTIVE",
    ):
        """Helper to build a mock server object."""
        mock_server = MagicMock()
        mock_server.id = server_id
        mock_server.name = name
        mock_server.status = status
        mock_server.flavor = {"id": "flavor-1"}
        mock_server.image = {"id": "image-1"}
        mock_server.addresses = {"network1": [{"addr": "10.0.0.1"}]}
        mock_server.key_name = "my-key"
        mock_server.created_at = None
        mock_server.updated_at = None
        mock_server.availability_zone = "dc3-a"
        mock_server.security_groups = [{"name": "default"}]
        return mock_server

    def test_list_instances(self, mock_connection):
        """Test listing compute instances."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

        mock_server = self._make_mock_server()
        mock_connection.compute.servers.return_value = [mock_server]

        client = InfomaniakComputeClient(mock_connection)
        instances = client.list_instances()

        assert len(instances) == 1
        assert instances[0]["id"] == "server-123"
        assert instances[0]["name"] == "test-server"
        assert instances[0]["status"] == "ACTIVE"

    def test_list_flavors(self, mock_connection):
        """Test listing available flavors."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

        mock_flavor = MagicMock()
        mock_flavor.id = "a1-ram2-disk20-perf1"
        mock_flavor.name = "a1-ram2-disk20-perf1"
        mock_flavor.vcpus = 1
        mock_flavor.ram = 2048
        mock_flavor.disk = 20
        mock_flavor.is_public = True

        mock_connection.compute.flavors.return_value = [mock_flavor]

        client = InfomaniakComputeClient(mock_connection)
        flavors = client.list_flavors()

        assert len(flavors) == 1
        assert flavors[0]["vcpus"] == 1
        assert flavors[0]["ram"] == 2048

    def test_list_keypairs(self, mock_connection):
        """Test listing SSH key pairs."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

        mock_keypair = MagicMock()
        mock_keypair.name = "my-key"
        mock_keypair.fingerprint = "aa:bb:cc:dd"
        mock_keypair.type = "ssh"

        mock_connection.compute.keypairs.return_value = [mock_keypair]

        client = InfomaniakComputeClient(mock_connection)
        keypairs = client.list_keypairs()

        assert len(keypairs) == 1
        assert keypairs[0]["name"] == "my-key"

    # --- Expanded Compute Tests ---

    def test_get_instance(self, mock_connection):
        """Test getting a specific instance by ID."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

        mock_server = self._make_mock_server(server_id="srv-abc")
        mock_connection.compute.get_server.return_value = mock_server

        client = InfomaniakComputeClient(mock_connection)
        result = client.get_instance("srv-abc")

        assert result is not None
        assert result["id"] == "srv-abc"
        mock_connection.compute.get_server.assert_called_once_with("srv-abc")

    def test_create_instance(self, mock_connection):
        """Test creating a new compute instance."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

        mock_flavor_obj = MagicMock()
        mock_flavor_obj.id = "flavor-1"
        mock_image_obj = MagicMock()
        mock_image_obj.id = "image-1"
        mock_network_obj = MagicMock()
        mock_network_obj.id = "net-1"

        mock_connection.compute.find_flavor.return_value = mock_flavor_obj
        mock_connection.image.find_image.return_value = mock_image_obj
        mock_connection.network.find_network.return_value = mock_network_obj

        created_server = self._make_mock_server(server_id="new-srv")
        mock_connection.compute.create_server.return_value = created_server
        mock_connection.compute.wait_for_server.return_value = created_server

        client = InfomaniakComputeClient(mock_connection)
        result = client.create_instance(
            name="new-server",
            flavor="a1-ram2-disk20-perf1",
            image="Ubuntu 22.04",
            network="my-network",
            key_name="my-key",
        )

        assert result is not None
        assert result["id"] == "new-srv"
        mock_connection.compute.create_server.assert_called_once()
        mock_connection.compute.wait_for_server.assert_called_once()

    def test_start_instance(self, mock_connection):
        """Test starting a stopped instance."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

        client = InfomaniakComputeClient(mock_connection)
        result = client.start_instance("srv-stopped")

        assert result is True
        mock_connection.compute.start_server.assert_called_once_with("srv-stopped")

    def test_stop_instance(self, mock_connection):
        """Test stopping a running instance."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

        client = InfomaniakComputeClient(mock_connection)
        result = client.stop_instance("srv-running")

        assert result is True
        mock_connection.compute.stop_server.assert_called_once_with("srv-running")

    def test_reboot_instance(self, mock_connection):
        """Test rebooting an instance with SOFT reboot."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

        client = InfomaniakComputeClient(mock_connection)
        result = client.reboot_instance("srv-123", reboot_type="SOFT")

        assert result is True
        mock_connection.compute.reboot_server.assert_called_once_with("srv-123", "SOFT")

    def test_delete_instance(self, mock_connection):
        """Test deleting a compute instance."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

        client = InfomaniakComputeClient(mock_connection)
        result = client.delete_instance("srv-to-delete")

        assert result is True
        mock_connection.compute.delete_server.assert_called_once_with(
            "srv-to-delete", force=False
        )

    def test_list_instances_error(self, mock_connection):
        """Connection error returns empty list instead of raising."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

        mock_connection.compute.servers.side_effect = Exception("Connection refused")

        client = InfomaniakComputeClient(mock_connection)
        instances = client.list_instances()

        assert instances == []

    def test_list_images(self, mock_connection):
        """Test listing available images."""
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient

        mock_image = MagicMock()
        mock_image.id = "img-ubuntu"
        mock_image.name = "Ubuntu 22.04"
        mock_image.status = "active"
        mock_image.min_disk = 10
        mock_image.min_ram = 512
        mock_image.size = 2147483648
        mock_image.created_at = None

        mock_connection.image.images.return_value = [mock_image]

        client = InfomaniakComputeClient(mock_connection)
        images = client.list_images()

        assert len(images) == 1
        assert images[0]["id"] == "img-ubuntu"
        assert images[0]["name"] == "Ubuntu 22.04"
        assert images[0]["min_disk"] == 10


# =========================================================================
# Test Volume Client
# =========================================================================

class TestInfomaniakVolumeClient:
    """Tests for InfomaniakVolumeClient."""

    @pytest.fixture
    def mock_connection(self):
        return MagicMock()

    def test_list_volumes(self, mock_connection):
        """Test listing block storage volumes."""
        from codomyrmex.cloud.infomaniak.block_storage import InfomaniakVolumeClient

        mock_volume = MagicMock()
        mock_volume.id = "vol-123"
        mock_volume.name = "test-volume"
        mock_volume.status = "available"
        mock_volume.size = 100
        mock_volume.volume_type = "ssd"
        mock_volume.availability_zone = "dc3-a"
        mock_volume.is_bootable = False
        mock_volume.is_encrypted = False
        mock_volume.attachments = []
        mock_volume.created_at = None

        mock_connection.block_storage.volumes.return_value = [mock_volume]

        client = InfomaniakVolumeClient(mock_connection)
        volumes = client.list_volumes()

        assert len(volumes) == 1
        assert volumes[0]["id"] == "vol-123"
        assert volumes[0]["size"] == 100

    def test_list_snapshots(self, mock_connection):
        """Test listing volume snapshots."""
        from codomyrmex.cloud.infomaniak.block_storage import InfomaniakVolumeClient

        mock_snapshot = MagicMock()
        mock_snapshot.id = "snap-123"
        mock_snapshot.name = "test-snapshot"
        mock_snapshot.status = "available"
        mock_snapshot.volume_id = "vol-123"
        mock_snapshot.size = 100
        mock_snapshot.created_at = None

        mock_connection.block_storage.snapshots.return_value = [mock_snapshot]

        client = InfomaniakVolumeClient(mock_connection)
        snapshots = client.list_snapshots()

        assert len(snapshots) == 1
        assert snapshots[0]["id"] == "snap-123"

    # --- Expanded Volume Tests ---

    def test_create_volume(self, mock_connection):
        """Test creating a new block storage volume."""
        from codomyrmex.cloud.infomaniak.block_storage import InfomaniakVolumeClient

        mock_vol = MagicMock()
        mock_vol.id = "vol-new"
        mock_vol.name = "new-volume"
        mock_vol.status = "creating"
        mock_vol.size = 50
        mock_vol.volume_type = "ssd"
        mock_vol.availability_zone = "dc3-a"
        mock_vol.is_bootable = False
        mock_vol.is_encrypted = False
        mock_vol.attachments = []
        mock_vol.created_at = None

        mock_connection.block_storage.create_volume.return_value = mock_vol

        client = InfomaniakVolumeClient(mock_connection)
        result = client.create_volume(size=50, name="new-volume", volume_type="ssd")

        assert result is not None
        assert result["id"] == "vol-new"
        assert result["size"] == 50
        mock_connection.block_storage.create_volume.assert_called_once()

    def test_delete_volume(self, mock_connection):
        """Test deleting a block storage volume."""
        from codomyrmex.cloud.infomaniak.block_storage import InfomaniakVolumeClient

        client = InfomaniakVolumeClient(mock_connection)
        result = client.delete_volume("vol-del")

        assert result is True
        mock_connection.block_storage.delete_volume.assert_called_once_with(
            "vol-del", force=False
        )

    def test_extend_volume(self, mock_connection):
        """Test extending a volume to a larger size."""
        from codomyrmex.cloud.infomaniak.block_storage import InfomaniakVolumeClient

        client = InfomaniakVolumeClient(mock_connection)
        result = client.extend_volume("vol-123", 200)

        assert result is True
        mock_connection.block_storage.extend_volume.assert_called_once_with("vol-123", 200)

    def test_attach_volume(self, mock_connection):
        """Test attaching a volume to an instance."""
        from codomyrmex.cloud.infomaniak.block_storage import InfomaniakVolumeClient

        client = InfomaniakVolumeClient(mock_connection)
        result = client.attach_volume("vol-123", "srv-456")

        assert result is True
        mock_connection.compute.create_volume_attachment.assert_called_once_with(
            server="srv-456",
            volume_id="vol-123",
            device=None,
        )

    def test_detach_volume(self, mock_connection):
        """Test detaching a volume from an instance."""
        from codomyrmex.cloud.infomaniak.block_storage import InfomaniakVolumeClient

        mock_attach = MagicMock()
        mock_attach.id = "attach-1"
        mock_attach.volume_id = "vol-123"

        mock_connection.compute.volume_attachments.return_value = [mock_attach]

        client = InfomaniakVolumeClient(mock_connection)
        result = client.detach_volume("vol-123", "srv-456")

        assert result is True
        mock_connection.compute.delete_volume_attachment.assert_called_once_with(
            "attach-1", server="srv-456"
        )

    def test_list_backups(self, mock_connection):
        """Test listing volume backups."""
        from codomyrmex.cloud.infomaniak.block_storage import InfomaniakVolumeClient

        mock_backup = MagicMock()
        mock_backup.id = "bkp-123"
        mock_backup.name = "daily-backup"
        mock_backup.status = "available"
        mock_backup.volume_id = "vol-123"
        mock_backup.size = 50
        mock_backup.created_at = None

        mock_connection.block_storage.backups.return_value = [mock_backup]

        client = InfomaniakVolumeClient(mock_connection)
        backups = client.list_backups()

        assert len(backups) == 1
        assert backups[0]["id"] == "bkp-123"
        assert backups[0]["name"] == "daily-backup"
        assert backups[0]["volume_id"] == "vol-123"


# =========================================================================
# Test Network Client
# =========================================================================

class TestInfomaniakNetworkClient:
    """Tests for InfomaniakNetworkClient."""

    @pytest.fixture
    def mock_connection(self):
        return MagicMock()

    def test_list_networks(self, mock_connection):
        """Test listing networks."""
        from codomyrmex.cloud.infomaniak.network import InfomaniakNetworkClient

        mock_network = MagicMock()
        mock_network.id = "net-123"
        mock_network.name = "test-network"
        mock_network.status = "ACTIVE"
        mock_network.is_shared = False
        mock_network.is_router_external = False
        mock_network.subnet_ids = ["subnet-1"]

        mock_connection.network.networks.return_value = [mock_network]

        client = InfomaniakNetworkClient(mock_connection)
        networks = client.list_networks()

        assert len(networks) == 1
        assert networks[0]["id"] == "net-123"

    def test_list_security_groups(self, mock_connection):
        """Test listing security groups."""
        from codomyrmex.cloud.infomaniak.network import InfomaniakNetworkClient

        mock_sg = MagicMock()
        mock_sg.id = "sg-123"
        mock_sg.name = "default"
        mock_sg.description = "Default security group"
        mock_sg.security_group_rules = [{}]

        mock_connection.network.security_groups.return_value = [mock_sg]

        client = InfomaniakNetworkClient(mock_connection)
        sgs = client.list_security_groups()

        assert len(sgs) == 1
        assert sgs[0]["name"] == "default"

    # --- Expanded Network Tests ---

    def test_create_network(self, mock_connection):
        """Test creating a new network."""
        from codomyrmex.cloud.infomaniak.network import InfomaniakNetworkClient

        mock_net = MagicMock()
        mock_net.id = "net-new"
        mock_net.name = "new-network"

        mock_connection.network.create_network.return_value = mock_net

        client = InfomaniakNetworkClient(mock_connection)
        result = client.create_network(name="new-network", description="A test network")

        assert result is not None
        assert result["id"] == "net-new"
        assert result["name"] == "new-network"
        mock_connection.network.create_network.assert_called_once()

    def test_delete_network(self, mock_connection):
        """Test deleting a network."""
        from codomyrmex.cloud.infomaniak.network import InfomaniakNetworkClient

        client = InfomaniakNetworkClient(mock_connection)
        result = client.delete_network("net-del")

        assert result is True
        mock_connection.network.delete_network.assert_called_once_with("net-del")

    def test_list_routers(self, mock_connection):
        """Test listing routers."""
        from codomyrmex.cloud.infomaniak.network import InfomaniakNetworkClient

        mock_router = MagicMock()
        mock_router.id = "rtr-123"
        mock_router.name = "main-router"
        mock_router.status = "ACTIVE"
        mock_router.external_gateway_info = {"network_id": "ext-net-1"}

        mock_connection.network.routers.return_value = [mock_router]

        client = InfomaniakNetworkClient(mock_connection)
        routers = client.list_routers()

        assert len(routers) == 1
        assert routers[0]["id"] == "rtr-123"
        assert routers[0]["name"] == "main-router"
        assert routers[0]["external_gateway"] == {"network_id": "ext-net-1"}

    def test_list_floating_ips(self, mock_connection):
        """Test listing floating IPs."""
        from codomyrmex.cloud.infomaniak.network import InfomaniakNetworkClient

        mock_fip = MagicMock()
        mock_fip.id = "fip-123"
        mock_fip.floating_ip_address = "195.15.220.10"
        mock_fip.fixed_ip_address = "10.0.0.5"
        mock_fip.status = "ACTIVE"
        mock_fip.port_id = "port-abc"

        mock_connection.network.ips.return_value = [mock_fip]

        client = InfomaniakNetworkClient(mock_connection)
        fips = client.list_floating_ips()

        assert len(fips) == 1
        assert fips[0]["floating_ip_address"] == "195.15.220.10"
        assert fips[0]["status"] == "ACTIVE"

    def test_create_security_group_rule(self, mock_connection):
        """Test adding a rule to a security group."""
        from codomyrmex.cloud.infomaniak.network import InfomaniakNetworkClient

        mock_rule = MagicMock()
        mock_rule.id = "rule-123"

        mock_connection.network.create_security_group_rule.return_value = mock_rule

        client = InfomaniakNetworkClient(mock_connection)
        result = client.add_security_group_rule(
            security_group_id="sg-123",
            direction="ingress",
            protocol="tcp",
            port_range_min=443,
            port_range_max=443,
            remote_ip_prefix="0.0.0.0/0",
        )

        assert result is not None
        assert result["id"] == "rule-123"
        assert result["direction"] == "ingress"
        assert result["protocol"] == "tcp"
        mock_connection.network.create_security_group_rule.assert_called_once()

    def test_list_load_balancers(self, mock_connection):
        """Test listing load balancers via Octavia."""
        from codomyrmex.cloud.infomaniak.network import InfomaniakNetworkClient

        mock_lb = MagicMock()
        mock_lb.id = "lb-123"
        mock_lb.name = "web-lb"
        mock_lb.vip_address = "10.0.0.100"
        mock_lb.operating_status = "ONLINE"
        mock_lb.provisioning_status = "ACTIVE"

        mock_connection.load_balancer.load_balancers.return_value = [mock_lb]

        client = InfomaniakNetworkClient(mock_connection)
        lbs = client.list_loadbalancers()

        assert len(lbs) == 1
        assert lbs[0]["id"] == "lb-123"
        assert lbs[0]["name"] == "web-lb"
        assert lbs[0]["vip_address"] == "10.0.0.100"


# =========================================================================
# Test Object Storage Client (Swift)
# =========================================================================

class TestInfomaniakObjectStorageClient:
    """Tests for InfomaniakObjectStorageClient (Swift API)."""

    @pytest.fixture
    def mock_connection(self):
        return MagicMock()

    def test_list_containers(self, mock_connection):
        """Test listing Swift containers."""
        from codomyrmex.cloud.infomaniak.object_storage import (
            InfomaniakObjectStorageClient,
        )

        mock_container_1 = MagicMock()
        mock_container_1.name = "container-a"
        mock_container_2 = MagicMock()
        mock_container_2.name = "container-b"

        mock_connection.object_store.containers.return_value = [
            mock_container_1,
            mock_container_2,
        ]

        client = InfomaniakObjectStorageClient(mock_connection)
        containers = client.list_containers()

        assert len(containers) == 2
        assert "container-a" in containers
        assert "container-b" in containers

    def test_create_container(self, mock_connection):
        """Test creating a Swift container."""
        from codomyrmex.cloud.infomaniak.object_storage import (
            InfomaniakObjectStorageClient,
        )

        client = InfomaniakObjectStorageClient(mock_connection)
        result = client.create_container("my-container")

        assert result is True
        mock_connection.object_store.create_container.assert_called_once_with("my-container")

    def test_upload_object(self, mock_connection):
        """Test uploading an object to a Swift container."""
        from codomyrmex.cloud.infomaniak.object_storage import (
            InfomaniakObjectStorageClient,
        )

        client = InfomaniakObjectStorageClient(mock_connection)
        result = client.upload_object("my-container", "test.txt", b"hello swift")

        assert result is True
        mock_connection.object_store.upload_object.assert_called_once_with(
            container="my-container",
            name="test.txt",
            data=b"hello swift",
            content_type=None,
        )

    def test_download_object(self, mock_connection):
        """Test downloading an object from a Swift container."""
        from codomyrmex.cloud.infomaniak.object_storage import (
            InfomaniakObjectStorageClient,
        )

        mock_connection.object_store.download_object.return_value = b"swift data"

        client = InfomaniakObjectStorageClient(mock_connection)
        data = client.download_object("my-container", "test.txt")

        assert data == b"swift data"
        mock_connection.object_store.download_object.assert_called_once_with(
            "my-container", "test.txt"
        )

    def test_delete_object(self, mock_connection):
        """Test deleting an object from a Swift container."""
        from codomyrmex.cloud.infomaniak.object_storage import (
            InfomaniakObjectStorageClient,
        )

        client = InfomaniakObjectStorageClient(mock_connection)
        result = client.delete_object("my-container", "test.txt")

        assert result is True
        mock_connection.object_store.delete_object.assert_called_once_with(
            "test.txt", container="my-container"
        )


# =========================================================================
# Test S3 Client
# =========================================================================

class TestInfomaniakS3Client:
    """Tests for InfomaniakS3Client (S3-compatible)."""

    def test_list_buckets(self):
        """Test listing S3 buckets."""
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakS3Client

        mock_client = MagicMock()
        mock_client.list_buckets.return_value = {
            "Buckets": [
                {"Name": "bucket1"},
                {"Name": "bucket2"},
            ]
        }

        client = InfomaniakS3Client(mock_client)
        buckets = client.list_buckets()

        assert len(buckets) == 2
        assert "bucket1" in buckets

    def test_upload_data(self):
        """Test uploading data to S3."""
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakS3Client

        mock_client = MagicMock()

        client = InfomaniakS3Client(mock_client)
        result = client.upload_data("test-bucket", "test-key", b"hello world")

        assert result is True
        mock_client.put_object.assert_called_once()

    def test_download_data(self):
        """Test downloading data from S3."""
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakS3Client

        mock_body = MagicMock()
        mock_body.read.return_value = b"hello world"

        mock_client = MagicMock()
        mock_client.get_object.return_value = {"Body": mock_body}

        client = InfomaniakS3Client(mock_client)
        data = client.download_data("test-bucket", "test-key")

        assert data == b"hello world"

    # --- Expanded S3 Tests ---

    def test_delete_object(self):
        """Test deleting an S3 object."""
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakS3Client

        mock_client = MagicMock()

        client = InfomaniakS3Client(mock_client)
        result = client.delete_object("test-bucket", "test-key")

        assert result is True
        mock_client.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="test-key"
        )

    def test_list_objects(self):
        """Test listing objects in an S3 bucket."""
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakS3Client

        mock_client = MagicMock()
        mock_client.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "file1.txt"},
                {"Key": "file2.txt"},
                {"Key": "dir/file3.txt"},
            ]
        }

        client = InfomaniakS3Client(mock_client)
        objects = client.list_objects("my-bucket")

        assert len(objects) == 3
        assert "file1.txt" in objects
        assert "dir/file3.txt" in objects

    def test_generate_presigned_url(self):
        """Test generating a presigned URL for temporary S3 access."""
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakS3Client

        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = (
            "https://s3.pub1.infomaniak.cloud/bucket/key?signature=abc123"
        )

        client = InfomaniakS3Client(mock_client)
        url = client.generate_presigned_url("my-bucket", "my-key", expires_in=7200)

        assert url is not None
        assert "s3.pub1.infomaniak.cloud" in url
        mock_client.generate_presigned_url.assert_called_once_with(
            ClientMethod="get_object",
            Params={"Bucket": "my-bucket", "Key": "my-key"},
            ExpiresIn=7200,
        )

    def test_bucket_exists(self):
        """Test checking if an S3 bucket exists."""
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakS3Client

        mock_client = MagicMock()
        # head_bucket succeeds for existing bucket
        mock_client.head_bucket.return_value = {}

        client = InfomaniakS3Client(mock_client)
        assert client.bucket_exists("existing-bucket") is True

        # head_bucket raises for non-existing bucket
        mock_client.head_bucket.side_effect = Exception("404 Not Found")
        assert client.bucket_exists("missing-bucket") is False


# =========================================================================
# Test Identity Client
# =========================================================================

class TestInfomaniakIdentityClient:
    """Tests for InfomaniakIdentityClient (Keystone)."""

    @pytest.fixture
    def mock_connection(self):
        conn = MagicMock()
        conn.current_user_id = "user-abc"
        conn.current_project_id = "proj-xyz"
        return conn

    def test_get_current_user(self, mock_connection):
        """Test getting the current authenticated user."""
        from codomyrmex.cloud.infomaniak.identity import InfomaniakIdentityClient

        mock_user = MagicMock()
        mock_user.id = "user-abc"
        mock_user.name = "test-user"
        mock_user.email = "test@example.com"
        mock_user.domain_id = "domain-1"
        mock_user.is_enabled = True

        mock_connection.identity.get_user.return_value = mock_user

        client = InfomaniakIdentityClient(mock_connection)
        result = client.get_current_user()

        assert result["id"] == "user-abc"
        assert result["name"] == "test-user"
        assert result["email"] == "test@example.com"
        assert result["is_enabled"] is True

    def test_list_projects(self, mock_connection):
        """Test listing accessible projects."""
        from codomyrmex.cloud.infomaniak.identity import InfomaniakIdentityClient

        mock_project = MagicMock()
        mock_project.id = "proj-xyz"
        mock_project.name = "my-project"
        mock_project.description = "Test project"
        mock_project.is_enabled = True
        mock_project.domain_id = "domain-1"

        mock_connection.identity.projects.return_value = [mock_project]

        client = InfomaniakIdentityClient(mock_connection)
        projects = client.list_projects()

        assert len(projects) == 1
        assert projects[0]["id"] == "proj-xyz"
        assert projects[0]["name"] == "my-project"

    def test_list_application_credentials(self, mock_connection):
        """Test listing application credentials for the current user."""
        from codomyrmex.cloud.infomaniak.identity import InfomaniakIdentityClient

        mock_cred = MagicMock()
        mock_cred.id = "cred-123"
        mock_cred.name = "my-app-cred"
        mock_cred.description = "For CI/CD"
        mock_cred.expires_at = None
        mock_cred.roles = [{"name": "member"}]

        mock_connection.identity.application_credentials.return_value = [mock_cred]

        client = InfomaniakIdentityClient(mock_connection)
        creds = client.list_application_credentials()

        assert len(creds) == 1
        assert creds[0]["id"] == "cred-123"
        assert creds[0]["name"] == "my-app-cred"
        assert "member" in creds[0]["roles"]

    def test_create_ec2_credentials(self, mock_connection):
        """Test creating EC2-style credentials for S3 access."""
        from codomyrmex.cloud.infomaniak.identity import InfomaniakIdentityClient

        mock_cred = MagicMock()
        mock_cred.id = "ec2-123"
        mock_cred.access = "AKIAEXAMPLE"
        mock_cred.secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        mock_cred.project_id = "proj-xyz"

        mock_connection.identity.create_credential.return_value = mock_cred

        client = InfomaniakIdentityClient(mock_connection)
        result = client.create_ec2_credentials()

        assert result is not None
        assert result["id"] == "ec2-123"
        assert result["access"] == "AKIAEXAMPLE"
        assert result["project_id"] == "proj-xyz"
        mock_connection.identity.create_credential.assert_called_once()

    def test_delete_ec2_credentials(self, mock_connection):
        """Test deleting EC2-style credentials."""
        from codomyrmex.cloud.infomaniak.identity import InfomaniakIdentityClient

        client = InfomaniakIdentityClient(mock_connection)
        result = client.delete_ec2_credentials("ec2-to-delete")

        assert result is True
        mock_connection.identity.delete_credential.assert_called_once_with("ec2-to-delete")


# =========================================================================
# Test DNS Client
# =========================================================================

class TestInfomaniakDNSClient:
    """Tests for InfomaniakDNSClient."""

    @pytest.fixture
    def mock_connection(self):
        return MagicMock()

    def test_list_zones(self, mock_connection):
        """Test listing DNS zones."""
        from codomyrmex.cloud.infomaniak.dns import InfomaniakDNSClient

        mock_zone = MagicMock()
        mock_zone.id = "zone-123"
        mock_zone.name = "example.com."
        mock_zone.email = "admin@example.com"
        mock_zone.status = "ACTIVE"
        mock_zone.type = "PRIMARY"
        mock_zone.ttl = 3600

        mock_connection.dns.zones.return_value = [mock_zone]

        client = InfomaniakDNSClient(mock_connection)
        zones = client.list_zones()

        assert len(zones) == 1
        assert zones[0]["name"] == "example.com."

    # --- Expanded DNS Tests ---

    def test_create_zone(self, mock_connection):
        """Test creating a new DNS zone."""
        from codomyrmex.cloud.infomaniak.dns import InfomaniakDNSClient

        mock_zone = MagicMock()
        mock_zone.id = "zone-new"
        mock_zone.name = "newdomain.com."

        mock_connection.dns.create_zone.return_value = mock_zone

        client = InfomaniakDNSClient(mock_connection)
        result = client.create_zone(
            name="newdomain.com",
            email="admin@newdomain.com",
            ttl=7200,
        )

        assert result is not None
        assert result["id"] == "zone-new"
        # Name should have dot appended
        mock_connection.dns.create_zone.assert_called_once_with(
            name="newdomain.com.",
            email="admin@newdomain.com",
            ttl=7200,
            description=None,
        )

    def test_delete_zone(self, mock_connection):
        """Test deleting a DNS zone."""
        from codomyrmex.cloud.infomaniak.dns import InfomaniakDNSClient

        client = InfomaniakDNSClient(mock_connection)
        result = client.delete_zone("zone-del")

        assert result is True
        mock_connection.dns.delete_zone.assert_called_once_with("zone-del")

    def test_list_records(self, mock_connection):
        """Test listing DNS records in a zone."""
        from codomyrmex.cloud.infomaniak.dns import InfomaniakDNSClient

        mock_record = MagicMock()
        mock_record.id = "rec-123"
        mock_record.name = "www.example.com."
        mock_record.type = "A"
        mock_record.records = ["195.15.220.10"]
        mock_record.ttl = 3600
        mock_record.status = "ACTIVE"

        mock_connection.dns.recordsets.return_value = [mock_record]

        client = InfomaniakDNSClient(mock_connection)
        records = client.list_records("zone-123")

        assert len(records) == 1
        assert records[0]["name"] == "www.example.com."
        assert records[0]["type"] == "A"
        assert "195.15.220.10" in records[0]["records"]

    def test_create_record(self, mock_connection):
        """Test creating a DNS record set."""
        from codomyrmex.cloud.infomaniak.dns import InfomaniakDNSClient

        mock_record = MagicMock()
        mock_record.id = "rec-new"
        mock_record.name = "api.example.com."

        mock_connection.dns.create_recordset.return_value = mock_record

        client = InfomaniakDNSClient(mock_connection)
        result = client.create_record(
            zone_id="zone-123",
            name="api.example.com",
            record_type="A",
            records=["195.15.220.20"],
            ttl=300,
        )

        assert result is not None
        assert result["id"] == "rec-new"
        assert result["type"] == "A"
        # Name should get dot appended
        mock_connection.dns.create_recordset.assert_called_once_with(
            zone="zone-123",
            name="api.example.com.",
            type="A",
            records=["195.15.220.20"],
            ttl=300,
            description=None,
        )

    def test_delete_record(self, mock_connection):
        """Test deleting a DNS record set."""
        from codomyrmex.cloud.infomaniak.dns import InfomaniakDNSClient

        client = InfomaniakDNSClient(mock_connection)
        result = client.delete_record("zone-123", "rec-del")

        assert result is True
        mock_connection.dns.delete_recordset.assert_called_once_with("rec-del", "zone-123")


# =========================================================================
# Test Heat Client
# =========================================================================

class TestInfomaniakHeatClient:
    """Tests for InfomaniakHeatClient."""

    @pytest.fixture
    def mock_connection(self):
        return MagicMock()

    def test_list_stacks(self, mock_connection):
        """Test listing Heat stacks."""
        from codomyrmex.cloud.infomaniak.orchestration import InfomaniakHeatClient

        mock_stack = MagicMock()
        mock_stack.id = "stack-123"
        mock_stack.name = "test-stack"
        mock_stack.status = "CREATE_COMPLETE"
        mock_stack.status_reason = "Stack CREATE completed successfully"
        mock_stack.created_at = None

        mock_connection.orchestration.stacks.return_value = [mock_stack]

        client = InfomaniakHeatClient(mock_connection)
        stacks = client.list_stacks()

        assert len(stacks) == 1
        assert stacks[0]["name"] == "test-stack"

    # --- Expanded Heat Tests ---

    def test_get_stack(self, mock_connection):
        """Test getting a specific Heat stack."""
        from codomyrmex.cloud.infomaniak.orchestration import InfomaniakHeatClient

        mock_stack = MagicMock()
        mock_stack.id = "stack-abc"
        mock_stack.name = "web-stack"
        mock_stack.status = "CREATE_COMPLETE"
        mock_stack.status_reason = "Success"
        mock_stack.description = "Web application stack"
        mock_stack.parameters = {"image": "Ubuntu 22.04"}
        mock_stack.outputs = [{"output_key": "ip", "output_value": "10.0.0.5"}]
        mock_stack.created_at = None
        mock_stack.updated_at = None

        mock_connection.orchestration.find_stack.return_value = mock_stack

        client = InfomaniakHeatClient(mock_connection)
        result = client.get_stack("stack-abc")

        assert result is not None
        assert result["id"] == "stack-abc"
        assert result["name"] == "web-stack"
        assert result["parameters"]["image"] == "Ubuntu 22.04"

    def test_create_stack(self, mock_connection):
        """Test creating a new Heat stack."""
        from codomyrmex.cloud.infomaniak.orchestration import InfomaniakHeatClient

        mock_stack = MagicMock()
        mock_stack.id = "stack-new"

        mock_connection.orchestration.create_stack.return_value = mock_stack

        template_yaml = """
heat_template_version: 2021-04-16
resources:
  my_server:
    type: OS::Nova::Server
    properties:
      flavor: a1-ram2-disk20-perf1
      image: Ubuntu 22.04
"""

        client = InfomaniakHeatClient(mock_connection)
        result = client.create_stack(
            name="new-stack",
            template=template_yaml,
            parameters={"key_name": "my-key"},
            timeout_mins=30,
        )

        assert result is not None
        assert result["id"] == "stack-new"
        assert result["name"] == "new-stack"
        mock_connection.orchestration.create_stack.assert_called_once()

    def test_delete_stack(self, mock_connection):
        """Test deleting a Heat stack."""
        from codomyrmex.cloud.infomaniak.orchestration import InfomaniakHeatClient

        client = InfomaniakHeatClient(mock_connection)
        result = client.delete_stack("stack-del")

        assert result is True
        mock_connection.orchestration.delete_stack.assert_called_once_with("stack-del")

    def test_list_stack_resources(self, mock_connection):
        """Test listing resources in a Heat stack."""
        from codomyrmex.cloud.infomaniak.orchestration import InfomaniakHeatClient

        mock_resource = MagicMock()
        mock_resource.name = "my_server"
        mock_resource.resource_type = "OS::Nova::Server"
        mock_resource.status = "CREATE_COMPLETE"
        mock_resource.status_reason = "state changed"
        mock_resource.physical_resource_id = "srv-physical-123"

        mock_connection.orchestration.resources.return_value = [mock_resource]

        client = InfomaniakHeatClient(mock_connection)
        resources = client.list_stack_resources("stack-123")

        assert len(resources) == 1
        assert resources[0]["name"] == "my_server"
        assert resources[0]["resource_type"] == "OS::Nova::Server"
        assert resources[0]["physical_resource_id"] == "srv-physical-123"

    def test_validate_template(self, mock_connection):
        """Test validating a Heat template."""
        from codomyrmex.cloud.infomaniak.orchestration import InfomaniakHeatClient

        mock_connection.orchestration.validate_template.return_value = {
            "Description": "A simple web server",
            "Parameters": {"image": {"Type": "String", "Default": "Ubuntu 22.04"}},
        }

        client = InfomaniakHeatClient(mock_connection)
        result = client.validate_template(template="heat_template_version: 2021-04-16")

        assert result["valid"] is True
        assert result["description"] == "A simple web server"
        assert "image" in result["parameters"]

    def test_validate_template_invalid(self, mock_connection):
        """Test that invalid template returns valid=False with error message."""
        from codomyrmex.cloud.infomaniak.orchestration import InfomaniakHeatClient

        mock_connection.orchestration.validate_template.side_effect = Exception(
            "Invalid template syntax"
        )

        client = InfomaniakHeatClient(mock_connection)
        result = client.validate_template(template="not valid yaml at all")

        assert result["valid"] is False
        assert "Invalid template syntax" in result["error"]


# =========================================================================
# Test Metering Client
# =========================================================================

class TestInfomaniakMeteringClient:
    """Tests for InfomaniakMeteringClient."""

    @pytest.fixture
    def mock_connection(self):
        conn = MagicMock()
        conn.current_project_id = "proj-xyz"
        return conn

    def _setup_empty_connection(self, conn):
        """Configure connection mocks with empty resource lists."""
        conn.compute.servers.return_value = []
        conn.block_storage.volumes.return_value = []
        conn.network.networks.return_value = []
        conn.network.routers.return_value = []
        conn.network.security_groups.return_value = []
        conn.network.ips.return_value = []
        conn.object_store.containers.return_value = []

    def test_get_all_usage(self, mock_connection):
        """Test getting comprehensive usage."""
        from codomyrmex.cloud.infomaniak.metering import InfomaniakMeteringClient

        self._setup_empty_connection(mock_connection)

        client = InfomaniakMeteringClient(mock_connection)
        usage = client.get_all_usage()

        assert "compute" in usage
        assert "storage" in usage
        assert "network" in usage
        assert "object_storage" in usage
        assert "timestamp" in usage

    # --- Expanded Metering Tests ---

    def test_get_compute_usage(self, mock_connection):
        """Test getting compute usage summary with server data."""
        from codomyrmex.cloud.infomaniak.metering import InfomaniakMeteringClient

        mock_server = MagicMock()
        mock_server.flavor = {"id": "flavor-1"}

        mock_flavor = MagicMock()
        mock_flavor.vcpus = 4
        mock_flavor.ram = 8192
        mock_flavor.disk = 80

        mock_connection.compute.servers.return_value = [mock_server]
        mock_connection.compute.get_flavor.return_value = mock_flavor

        client = InfomaniakMeteringClient(mock_connection)
        usage = client.get_compute_usage()

        assert usage["instance_count"] == 1
        assert usage["total_vcpus"] == 4
        assert usage["total_ram_mb"] == 8192
        assert usage["total_disk_gb"] == 80

    def test_get_storage_usage(self, mock_connection):
        """Test getting block storage usage summary."""
        from codomyrmex.cloud.infomaniak.metering import InfomaniakMeteringClient

        mock_vol1 = MagicMock()
        mock_vol1.size = 100
        mock_vol1.attachments = [{"id": "att-1"}]

        mock_vol2 = MagicMock()
        mock_vol2.size = 50
        mock_vol2.attachments = []

        mock_connection.block_storage.volumes.return_value = [mock_vol1, mock_vol2]

        client = InfomaniakMeteringClient(mock_connection)
        usage = client.get_storage_usage()

        assert usage["volume_count"] == 2
        assert usage["total_size_gb"] == 150
        assert usage["attached_count"] == 1
        assert usage["unattached_count"] == 1

    def test_get_network_usage(self, mock_connection):
        """Test getting network usage summary."""
        from codomyrmex.cloud.infomaniak.metering import InfomaniakMeteringClient

        mock_fip_in_use = MagicMock()
        mock_fip_in_use.port_id = "port-123"
        mock_fip_unused = MagicMock()
        mock_fip_unused.port_id = None

        mock_connection.network.networks.return_value = [MagicMock(), MagicMock()]
        mock_connection.network.routers.return_value = [MagicMock()]
        mock_connection.network.security_groups.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_connection.network.ips.return_value = [mock_fip_in_use, mock_fip_unused]

        client = InfomaniakMeteringClient(mock_connection)
        usage = client.get_network_usage()

        assert usage["network_count"] == 2
        assert usage["router_count"] == 1
        assert usage["security_group_count"] == 3
        assert usage["floating_ip_count"] == 2
        assert usage["floating_ips_in_use"] == 1

    def test_get_compute_quotas(self, mock_connection):
        """Test getting compute quotas for the current project."""
        from codomyrmex.cloud.infomaniak.metering import InfomaniakMeteringClient

        mock_quotas = MagicMock()
        mock_quotas.instances = 10
        mock_quotas.cores = 40
        mock_quotas.ram = 102400
        mock_quotas.key_pairs = 100
        mock_quotas.server_groups = 10

        mock_connection.compute.get_quota_set.return_value = mock_quotas

        client = InfomaniakMeteringClient(mock_connection)
        quotas = client.get_compute_quotas()

        assert quotas["instances"] == 10
        assert quotas["cores"] == 40
        assert quotas["ram_mb"] == 102400

    def test_get_all_usage_timestamp_format(self, mock_connection):
        """Verify get_all_usage uses timezone-aware UTC timestamp (not utcnow)."""
        from codomyrmex.cloud.infomaniak.metering import InfomaniakMeteringClient

        self._setup_empty_connection(mock_connection)

        client = InfomaniakMeteringClient(mock_connection)
        usage = client.get_all_usage()

        # The timestamp should contain timezone info ('+00:00' for UTC)
        timestamp_str = usage["timestamp"]
        assert timestamp_str is not None
        # ISO format with timezone: ends with +00:00 or contains 'Z'
        assert "+00:00" in timestamp_str or "Z" in timestamp_str


# =========================================================================
# Test Module Imports
# =========================================================================

class TestModuleExports:
    """Tests for module-level exports."""

    def test_infomaniak_module_imports(self):
        """Test that Infomaniak module exports the expected clients."""
        from codomyrmex.cloud import infomaniak

        assert hasattr(infomaniak, "InfomaniakComputeClient")
        assert hasattr(infomaniak, "InfomaniakVolumeClient")
        assert hasattr(infomaniak, "InfomaniakNetworkClient")
        assert hasattr(infomaniak, "InfomaniakObjectStorageClient")
        assert hasattr(infomaniak, "InfomaniakS3Client")
        assert hasattr(infomaniak, "InfomaniakIdentityClient")
        assert hasattr(infomaniak, "InfomaniakDNSClient")
        assert hasattr(infomaniak, "InfomaniakHeatClient")
        assert hasattr(infomaniak, "InfomaniakMeteringClient")
        assert hasattr(infomaniak, "InfomaniakNewsletterClient")

    def test_cloud_provider_enum_includes_infomaniak(self):
        """Test that CloudProvider enum includes INFOMANIAK."""
        from codomyrmex.cloud.common import CloudProvider

        assert hasattr(CloudProvider, "INFOMANIAK")
        assert CloudProvider.INFOMANIAK.value == "infomaniak"

    # --- Expanded Module Export Tests ---

    def test_create_s3_client_exported(self):
        """The critical P0 fix: create_s3_client is exported from infomaniak package."""
        from codomyrmex.cloud.infomaniak import create_s3_client

        assert callable(create_s3_client)

    def test_infomaniak_all_contains_create_s3_client(self):
        """Verify __all__ in infomaniak package includes create_s3_client."""
        import codomyrmex.cloud.infomaniak as infomaniak_pkg

        assert "create_s3_client" in infomaniak_pkg.__all__

    def test_cloud_config_from_env_infomaniak(self):
        """CloudConfig.from_env() detects INFOMANIAK_APP_CREDENTIAL_ID and registers provider."""
        from codomyrmex.cloud.common import CloudConfig, CloudProvider

        with patch.dict("os.environ", {
            "INFOMANIAK_APP_CREDENTIAL_ID": "ik-cred-id",
            "INFOMANIAK_APP_CREDENTIAL_SECRET": "ik-cred-secret",
            "INFOMANIAK_REGION": "dc3-b",
        }, clear=True):
            config = CloudConfig.from_env()

            assert config.has_provider(CloudProvider.INFOMANIAK)
            creds = config.get_credentials(CloudProvider.INFOMANIAK)
            assert creds is not None
            assert creds.access_key == "ik-cred-id"
            assert creds.secret_key == "ik-cred-secret"
            assert creds.region == "dc3-b"


# =========================================================================
# Test Newsletter Client
# =========================================================================

class TestInfomaniakNewsletterClient:
    """Tests for InfomaniakNewsletterClient.

    Uses instance-level mocking: creates a real client (exercises __init__,
    URL construction, header setup, payload building), then replaces
    ``_session.get/post/put/delete`` with mocks so only HTTP transport
    is faked.
    """

    BASE = "https://api.infomaniak.com"
    NL_ID = "nl-123"
    URL_PREFIX = f"{BASE}/1/newsletters/{NL_ID}"

    def _make_client(self):
        """Create a newsletter client and replace its session with a mock."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        client = InfomaniakNewsletterClient(
            token="test-token",
            newsletter_id=self.NL_ID,
            base_url=self.BASE,
        )
        client._session = MagicMock()
        return client

    @staticmethod
    def _mock_response(json_data, status_code=200):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = json_data
        resp.raise_for_status = MagicMock()
        return resp

    # ------------------------------------------------------------------
    # Factory methods & construction
    # ------------------------------------------------------------------

    def test_from_credentials(self):
        """from_credentials stores token and newsletter_id."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        client = InfomaniakNewsletterClient.from_credentials(
            token="tok-abc", newsletter_id="nl-456",
        )
        assert client._token == "tok-abc"
        assert client._newsletter_id == "nl-456"

    def test_from_env(self):
        """from_env reads correct environment variables."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        with patch.dict("os.environ", {
            "INFOMANIAK_NEWSLETTER_TOKEN": "env-token",
            "INFOMANIAK_NEWSLETTER_ID": "env-nl-id",
        }):
            client = InfomaniakNewsletterClient.from_env()
            assert client._token == "env-token"
            assert client._newsletter_id == "env-nl-id"

    def test_from_env_missing(self):
        """from_env raises ValueError when env vars are missing."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables"):
                InfomaniakNewsletterClient.from_env()

    def test_auth_header_set(self):
        """__init__ sets Authorization Bearer header on session."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        client = InfomaniakNewsletterClient(
            token="my-secret-token", newsletter_id="nl-1",
        )
        assert client._session.headers["Authorization"] == "Bearer my-secret-token"
        assert client._session.headers["Content-Type"] == "application/json"

    def test_context_manager(self):
        """Context manager protocol calls close on exit."""
        client = self._make_client()
        client.__enter__()
        client.__exit__(None, None, None)
        client._session.close.assert_called_once()

    def test_inherits_rest_base(self):
        """Client inherits from InfomaniakRESTBase."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase
        client = self._make_client()
        assert isinstance(client, InfomaniakRESTBase)

    def test_validate_connection(self):
        """validate_connection calls GET credits endpoint."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"remaining": 100}},
        )
        assert client.validate_connection() is True
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/credits"

    # ------------------------------------------------------------------
    # Campaign operations
    # ------------------------------------------------------------------

    def test_list_campaigns(self):
        """list_campaigns GETs campaigns URL and returns list."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": [{"id": "c-1", "subject": "Hello"}]},
        )
        result = client.list_campaigns()

        assert len(result) == 1
        assert result[0]["id"] == "c-1"
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns"

    def test_get_campaign(self):
        """get_campaign GETs campaign by ID."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"id": "c-99", "subject": "Detail"}},
        )
        result = client.get_campaign("c-99")

        assert result["id"] == "c-99"
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-99"

    def test_create_campaign(self):
        """create_campaign POSTs with all 5 payload fields."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"id": "c-new"}},
        )
        result = client.create_campaign(
            subject="New",
            sender_email="news@test.com",
            sender_name="Tester",
            content_html="<p>Hi</p>",
            mailing_list_id="ml-1",
        )

        assert result["id"] == "c-new"
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns"
        payload = client._session.post.call_args[1]["json"]
        assert payload["subject"] == "New"
        assert payload["sender_email"] == "news@test.com"
        assert payload["sender_name"] == "Tester"
        assert payload["content"] == "<p>Hi</p>"
        assert payload["mailing_list_id"] == "ml-1"

    def test_update_campaign(self):
        """update_campaign PUTs kwargs to campaign URL."""
        client = self._make_client()
        client._session.put.return_value = self._mock_response(
            {"data": {"id": "c-1", "subject": "Updated"}},
        )
        result = client.update_campaign("c-1", subject="Updated")

        assert result["subject"] == "Updated"
        url = client._session.put.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1"
        payload = client._session.put.call_args[1]["json"]
        assert payload == {"subject": "Updated"}

    def test_delete_campaign(self):
        """delete_campaign DELETEs campaign URL and returns True."""
        client = self._make_client()
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        client._session.delete.return_value = resp

        assert client.delete_campaign("c-del") is True
        url = client._session.delete.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-del"

    def test_send_test(self):
        """send_test POSTs email payload to test endpoint."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"status": "sent"}},
        )
        assert client.send_test("c-1", "test@example.com") is True
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1/test"
        payload = client._session.post.call_args[1]["json"]
        assert payload == {"email": "test@example.com"}

    def test_schedule_campaign(self):
        """schedule_campaign POSTs send_at to schedule endpoint."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"scheduled": True}},
        )
        assert client.schedule_campaign("c-1", "2026-03-01T10:00:00Z") is True
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1/schedule"
        payload = client._session.post.call_args[1]["json"]
        assert payload == {"send_at": "2026-03-01T10:00:00Z"}

    def test_unschedule_campaign(self):
        """unschedule_campaign POSTs to unschedule endpoint."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"unscheduled": True}},
        )
        assert client.unschedule_campaign("c-1") is True
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1/unschedule"

    def test_send_campaign(self):
        """send_campaign POSTs to send endpoint."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"status": "sending"}},
        )
        assert client.send_campaign("c-1") is True
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1/send"

    def test_get_campaign_statistics(self):
        """get_campaign_statistics GETs statistics URL."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"sent": 1000, "opened": 450}},
        )
        stats = client.get_campaign_statistics("c-1")

        assert stats["sent"] == 1000
        assert stats["opened"] == 450
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1/statistics"

    # ------------------------------------------------------------------
    # Mailing list operations
    # ------------------------------------------------------------------

    def test_list_mailing_lists(self):
        """list_mailing_lists GETs mailing-lists URL."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": [{"id": "ml-1", "name": "Subs"}, {"id": "ml-2", "name": "VIPs"}]},
        )
        result = client.list_mailing_lists()

        assert len(result) == 2
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists"

    def test_get_mailing_list(self):
        """get_mailing_list GETs specific list by ID."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"id": "ml-1", "name": "Subs"}},
        )
        result = client.get_mailing_list("ml-1")

        assert result["id"] == "ml-1"
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-1"

    def test_create_mailing_list(self):
        """create_mailing_list POSTs name payload."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"id": "ml-new", "name": "New List"}},
        )
        result = client.create_mailing_list("New List")

        assert result["name"] == "New List"
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists"
        payload = client._session.post.call_args[1]["json"]
        assert payload == {"name": "New List"}

    def test_update_mailing_list(self):
        """update_mailing_list PUTs kwargs."""
        client = self._make_client()
        client._session.put.return_value = self._mock_response(
            {"data": {"id": "ml-1", "name": "Renamed"}},
        )
        result = client.update_mailing_list("ml-1", name="Renamed")

        assert result["name"] == "Renamed"
        url = client._session.put.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-1"

    def test_delete_mailing_list(self):
        """delete_mailing_list DELETEs list URL."""
        client = self._make_client()
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        client._session.delete.return_value = resp

        assert client.delete_mailing_list("ml-del") is True
        url = client._session.delete.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-del"

    def test_get_list_contacts(self):
        """get_list_contacts GETs contacts for a list."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": [{"id": "ct-1", "email": "a@test.com"}]},
        )
        result = client.get_list_contacts("ml-1")

        assert len(result) == 1
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-1/contacts"

    def test_import_contacts(self):
        """import_contacts POSTs contacts list."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"task_id": "task-123", "imported": 3}},
        )
        contacts = [{"email": "a@test.com"}, {"email": "b@test.com"}]
        result = client.import_contacts("ml-1", contacts)

        assert result["task_id"] == "task-123"
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-1/contacts/import"
        payload = client._session.post.call_args[1]["json"]
        assert payload == {"contacts": contacts}

    def test_manage_contact(self):
        """manage_contact POSTs to action URL."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"subscribed": True}},
        )
        assert client.manage_contact("ml-1", "ct-5", "subscribe") is True
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-1/contacts/ct-5/subscribe"

    # ------------------------------------------------------------------
    # Contact operations
    # ------------------------------------------------------------------

    def test_get_contact(self):
        """get_contact GETs contact by ID."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"id": "ct-1", "email": "a@test.com"}},
        )
        result = client.get_contact("ct-1")

        assert result["email"] == "a@test.com"
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/contacts/ct-1"

    def test_update_contact(self):
        """update_contact PUTs kwargs."""
        client = self._make_client()
        client._session.put.return_value = self._mock_response(
            {"data": {"id": "ct-1", "name": "Updated"}},
        )
        result = client.update_contact("ct-1", name="Updated")

        assert result["name"] == "Updated"
        url = client._session.put.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/contacts/ct-1"
        payload = client._session.put.call_args[1]["json"]
        assert payload == {"name": "Updated"}

    def test_delete_contact(self):
        """delete_contact DELETEs contact URL."""
        client = self._make_client()
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        client._session.delete.return_value = resp

        assert client.delete_contact("ct-del") is True
        url = client._session.delete.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/contacts/ct-del"

    # ------------------------------------------------------------------
    # Utility operations
    # ------------------------------------------------------------------

    def test_get_task_status(self):
        """get_task_status GETs tasks URL."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"id": "t-1", "status": "completed"}},
        )
        result = client.get_task_status("t-1")

        assert result["status"] == "completed"
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/tasks/t-1"

    def test_get_credits(self):
        """get_credits GETs credits URL."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"remaining": 5000, "used": 1500}},
        )
        credits = client.get_credits()

        assert credits["remaining"] == 5000
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/credits"

    # ------------------------------------------------------------------
    # Error paths
    # ------------------------------------------------------------------

    def test_error_get_returns_none(self):
        """GET error returns None."""
        client = self._make_client()
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("500 Server Error")
        client._session.get.return_value = resp

        assert client.get_campaign("c-1") is None

    def test_error_post_returns_none(self):
        """POST error returns None (bool methods return False)."""
        client = self._make_client()
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("500 Server Error")
        client._session.post.return_value = resp

        assert client.send_campaign("c-1") is False

    def test_error_delete_returns_false(self):
        """DELETE error returns False."""
        client = self._make_client()
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("500 Server Error")
        client._session.delete.return_value = resp

        assert client.delete_campaign("c-1") is False

    def test_list_returns_empty_on_error(self):
        """list_campaigns and list_mailing_lists return [] on error."""
        client = self._make_client()
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("Connection refused")
        client._session.get.return_value = resp

        assert client.list_campaigns() == []
        assert client.list_mailing_lists() == []

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_list_campaigns_dict_response(self):
        """list_campaigns extracts items from dict-wrapped response."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"total": 5, "items": [{"id": "c1"}]}},
        )
        result = client.list_campaigns()
        # Dict-wrapped response: items extracted
        assert isinstance(result, list)
        assert result == [{"id": "c1"}]

    def test_list_campaigns_none_response(self):
        """list_campaigns returns [] when _get returns None."""
        client = self._make_client()
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("error")
        client._session.get.return_value = resp

        assert client.list_campaigns() == []

    def test_get_response_without_data_key(self):
        """_get returns full dict when no 'data' key in response."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"result": "ok", "value": 42},
        )
        result = client.get_credits()
        # dict.get("data", dict) returns dict itself
        assert result["result"] == "ok"
        assert result["value"] == 42

    def test_put_error_returns_none(self):
        """PUT error returns None."""
        client = self._make_client()
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("500 Server Error")
        client._session.put.return_value = resp

        assert client.update_campaign("c-1", subject="X") is None

    def test_base_url_trailing_slash_stripped(self):
        """Trailing slash in base_url is stripped."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(
            token="t", newsletter_id="n", base_url="https://api.test.com/"
        )
        assert client._base_url == "https://api.test.com"

    def test_service_name_is_newsletter(self):
        """Client _service_name is 'newsletter'."""
        client = self._make_client()
        assert client._service_name == "newsletter"

    def test_get_list_contacts_empty(self):
        """get_list_contacts returns [] for empty contact list."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response({"data": []})
        assert client.get_list_contacts("ml-1") == []

    def test_validate_connection_failure(self):
        """validate_connection returns False on error."""
        client = self._make_client()
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("timeout")
        client._session.get.return_value = resp

        assert client.validate_connection() is False


# =========================================================================
# Test Exception Hierarchy
# =========================================================================

class TestInfomaniakExceptionHierarchy:
    """Tests for Infomaniak exception hierarchy and attributes."""

    def test_cloud_error_attributes(self):
        """InfomaniakCloudError stores service, operation, resource_id."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakCloudError

        err = InfomaniakCloudError(
            "test msg", service="compute", operation="create", resource_id="srv-1"
        )
        assert str(err) == "test msg"
        assert err.service == "compute"
        assert err.operation == "create"
        assert err.resource_id == "srv-1"

    def test_cloud_error_default_attributes(self):
        """InfomaniakCloudError defaults to empty strings."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakCloudError

        err = InfomaniakCloudError("msg")
        assert err.service == ""
        assert err.operation == ""
        assert err.resource_id == ""

    def test_all_exceptions_inherit_from_cloud_error(self):
        """All custom exceptions inherit from InfomaniakCloudError."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakAuthError,
            InfomaniakCloudError,
            InfomaniakConflictError,
            InfomaniakConnectionError,
            InfomaniakNotFoundError,
            InfomaniakQuotaExceededError,
            InfomaniakTimeoutError,
        )

        for exc_cls in [
            InfomaniakAuthError,
            InfomaniakNotFoundError,
            InfomaniakConflictError,
            InfomaniakQuotaExceededError,
            InfomaniakConnectionError,
            InfomaniakTimeoutError,
        ]:
            err = exc_cls("test", service="svc")
            assert isinstance(err, InfomaniakCloudError)
            assert isinstance(err, Exception)
            assert err.service == "svc"

    def test_exception_message_propagation(self):
        """Message passes through to Exception base class."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakAuthError

        err = InfomaniakAuthError("auth failed", service="identity")
        assert "auth failed" in str(err)

    def test_exception_kwargs_preserved(self):
        """All kwargs preserved on all subclasses."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakNotFoundError

        err = InfomaniakNotFoundError(
            "not found", service="dns", operation="get_zone", resource_id="zone-42"
        )
        assert err.service == "dns"
        assert err.operation == "get_zone"
        assert err.resource_id == "zone-42"


# =========================================================================
# Test classify_openstack_error
# =========================================================================

class TestClassifyOpenstackError:
    """Tests for classify_openstack_error() string-based classification."""

    def _classify(self, msg, **kwargs):
        from codomyrmex.cloud.infomaniak.exceptions import classify_openstack_error
        return classify_openstack_error(Exception(msg), **kwargs)

    def test_401_returns_auth_error(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakAuthError
        assert isinstance(self._classify("HTTP 401 Unauthorized"), InfomaniakAuthError)

    def test_403_returns_auth_error(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakAuthError
        assert isinstance(self._classify("403 Forbidden"), InfomaniakAuthError)

    def test_authentication_keyword_returns_auth_error(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakAuthError
        assert isinstance(self._classify("Authentication required"), InfomaniakAuthError)

    def test_404_returns_not_found(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakNotFoundError
        assert isinstance(self._classify("HTTP 404"), InfomaniakNotFoundError)

    def test_not_found_keyword(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakNotFoundError
        assert isinstance(self._classify("Resource not found"), InfomaniakNotFoundError)

    def test_409_returns_conflict(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakConflictError
        assert isinstance(self._classify("HTTP 409"), InfomaniakConflictError)

    def test_conflict_keyword(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakConflictError
        assert isinstance(self._classify("State conflict detected"), InfomaniakConflictError)

    def test_413_returns_quota(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakQuotaExceededError
        assert isinstance(self._classify("HTTP 413 Request Entity Too Large"), InfomaniakQuotaExceededError)

    def test_quota_keyword(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakQuotaExceededError
        assert isinstance(self._classify("Quota exceeded"), InfomaniakQuotaExceededError)

    def test_limit_keyword(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakQuotaExceededError
        assert isinstance(self._classify("Rate limit hit"), InfomaniakQuotaExceededError)

    def test_timeout_keyword(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakTimeoutError
        assert isinstance(self._classify("Request timeout"), InfomaniakTimeoutError)

    def test_timed_out_keyword(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakTimeoutError
        assert isinstance(self._classify("Connection timed out"), InfomaniakTimeoutError)

    def test_connection_keyword(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakConnectionError
        assert isinstance(self._classify("Connection refused"), InfomaniakConnectionError)

    def test_refused_keyword(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakConnectionError
        assert isinstance(self._classify("refused by server"), InfomaniakConnectionError)

    def test_unreachable_keyword(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakConnectionError
        assert isinstance(self._classify("Host unreachable"), InfomaniakConnectionError)

    def test_generic_error_fallback(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakCloudError
        result = self._classify("Something unknown went wrong")
        assert type(result) is InfomaniakCloudError

    def test_case_insensitive(self):
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakAuthError
        assert isinstance(self._classify("AUTHENTICATION FAILED"), InfomaniakAuthError)

    def test_kwargs_propagated(self):
        result = self._classify(
            "HTTP 404", service="dns", operation="get_zone", resource_id="z-1"
        )
        assert result.service == "dns"
        assert result.operation == "get_zone"
        assert result.resource_id == "z-1"

    def test_preserves_original_message(self):
        result = self._classify("HTTP 404 zone missing")
        assert "HTTP 404 zone missing" in str(result)


# =========================================================================
# Test classify_http_error
# =========================================================================

class TestClassifyHttpError:
    """Tests for classify_http_error() status-code-based classification."""

    def _make_http_error(self, status_code):
        """Create a requests-like HTTPError with a response object."""
        import requests
        resp = MagicMock()
        resp.status_code = status_code
        err = requests.exceptions.HTTPError(f"HTTP {status_code}")
        err.response = resp
        return err

    def test_connection_error_instance(self):
        """requests.ConnectionError maps to InfomaniakConnectionError."""
        import requests

        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakConnectionError,
            classify_http_error,
        )
        err = requests.exceptions.ConnectionError("refused")
        result = classify_http_error(err, service="newsletter")
        assert isinstance(result, InfomaniakConnectionError)
        assert result.service == "newsletter"

    def test_timeout_instance(self):
        """requests.Timeout maps to InfomaniakTimeoutError."""
        import requests

        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakTimeoutError,
            classify_http_error,
        )
        err = requests.exceptions.Timeout("timed out")
        result = classify_http_error(err, operation="GET credits")
        assert isinstance(result, InfomaniakTimeoutError)
        assert result.operation == "GET credits"

    def test_401_response(self):
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakAuthError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(401))
        assert isinstance(result, InfomaniakAuthError)

    def test_403_response(self):
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakAuthError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(403))
        assert isinstance(result, InfomaniakAuthError)

    def test_404_response(self):
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakNotFoundError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(404))
        assert isinstance(result, InfomaniakNotFoundError)

    def test_409_response(self):
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakConflictError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(409))
        assert isinstance(result, InfomaniakConflictError)

    def test_413_response(self):
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakQuotaExceededError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(413))
        assert isinstance(result, InfomaniakQuotaExceededError)

    def test_429_response(self):
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakQuotaExceededError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(429))
        assert isinstance(result, InfomaniakQuotaExceededError)

    def test_no_response_attribute(self):
        """Error without response falls back to string classification."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakCloudError,
            classify_http_error,
        )
        err = Exception("Something generic happened")
        result = classify_http_error(err)
        assert isinstance(result, InfomaniakCloudError)

    def test_response_without_status_code(self):
        """Response without status_code falls back to string classification."""
        from codomyrmex.cloud.infomaniak.exceptions import classify_http_error
        err = Exception("weird error")
        err.response = MagicMock(spec=[])  # no status_code attr
        result = classify_http_error(err)
        assert result is not None

    def test_500_falls_through_to_string_classification(self):
        """HTTP 500 has no explicit mapping, falls to string classifier."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakCloudError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(500))
        assert isinstance(result, InfomaniakCloudError)

    def test_kwargs_propagated(self):
        from codomyrmex.cloud.infomaniak.exceptions import classify_http_error
        result = classify_http_error(
            self._make_http_error(404),
            service="newsletter",
            operation="GET campaigns/1",
            resource_id="camp-1",
        )
        assert result.service == "newsletter"
        assert result.operation == "GET campaigns/1"
        assert result.resource_id == "camp-1"


# =========================================================================
# Test Base Classes (OpenStack, S3, REST)
# =========================================================================

class TestInfomaniakOpenStackBaseClass:
    """Tests for InfomaniakOpenStackBase protocol methods."""

    def test_context_manager_calls_close(self):
        """__exit__ calls close()."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = MagicMock()
        client = InfomaniakOpenStackBase(mock_conn)
        client.__enter__()
        result = client.__exit__(None, None, None)

        assert result is False
        mock_conn.close.assert_called_once()

    def test_exit_does_not_suppress_exception(self):
        """__exit__ returns False — does not suppress exceptions."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = MagicMock()
        client = InfomaniakOpenStackBase(mock_conn)

        result = client.__exit__(ValueError, ValueError("boom"), None)
        assert result is False

    def test_close_handles_exception(self):
        """close() logs warning when conn.close() raises."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = MagicMock()
        mock_conn.close.side_effect = RuntimeError("close failed")

        client = InfomaniakOpenStackBase(mock_conn)
        # Should not raise
        client.close()

    def test_close_no_close_method(self):
        """close() is safe when connection has no close() method."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = MagicMock(spec=[])  # no close attribute
        client = InfomaniakOpenStackBase(mock_conn)
        client.close()  # Should not raise

    def test_validate_connection_success(self):
        """validate_connection returns True on success."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = MagicMock()
        mock_conn.identity.projects.return_value = []
        client = InfomaniakOpenStackBase(mock_conn)
        assert client.validate_connection() is True

    def test_validate_connection_failure(self):
        """validate_connection returns False on exception."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = MagicMock()
        mock_conn.identity.projects.side_effect = Exception("auth expired")
        client = InfomaniakOpenStackBase(mock_conn)
        assert client.validate_connection() is False

    def test_service_name_default(self):
        """Default _service_name is 'openstack'."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase
        assert InfomaniakOpenStackBase._service_name == "openstack"


class TestInfomaniakS3BaseClass:
    """Tests for InfomaniakS3Base protocol methods."""

    def test_context_manager(self):
        """Context manager protocol enters and exits cleanly."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        mock_client = MagicMock()
        s3 = InfomaniakS3Base(mock_client)
        assert s3.__enter__() is s3
        assert s3.__exit__(None, None, None) is False

    def test_close_is_noop(self):
        """close() is a no-op for S3 (boto3 doesn't need explicit close)."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        mock_client = MagicMock()
        s3 = InfomaniakS3Base(mock_client)
        s3.close()
        # No assertions needed — just verify no exceptions

    def test_validate_connection_success(self):
        """validate_connection returns True when list_buckets succeeds."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        mock_client = MagicMock()
        mock_client.list_buckets.return_value = {"Buckets": []}
        s3 = InfomaniakS3Base(mock_client)
        assert s3.validate_connection() is True

    def test_validate_connection_failure(self):
        """validate_connection returns False on exception."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        mock_client = MagicMock()
        mock_client.list_buckets.side_effect = Exception("invalid creds")
        s3 = InfomaniakS3Base(mock_client)
        assert s3.validate_connection() is False

    def test_default_constants(self):
        """S3Base has correct default endpoint and region."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        assert InfomaniakS3Base.DEFAULT_ENDPOINT == "https://s3.pub1.infomaniak.cloud/"
        assert InfomaniakS3Base.DEFAULT_REGION == "us-east-1"

    def test_exit_does_not_suppress_exception(self):
        """__exit__ returns False — does not suppress exceptions."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        mock_client = MagicMock()
        s3 = InfomaniakS3Base(mock_client)
        result = s3.__exit__(TypeError, TypeError("bad"), None)
        assert result is False


class TestInfomaniakRESTBaseClass:
    """Tests for InfomaniakRESTBase protocol methods."""

    def test_from_env_raises_not_implemented(self):
        """Base from_env() raises NotImplementedError."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        with pytest.raises(NotImplementedError, match="must override from_env"):
            InfomaniakRESTBase.from_env()

    def test_close_handles_exception(self):
        """close() logs warning when session.close() raises."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase(token="t")
        client._session = MagicMock()
        client._session.close.side_effect = RuntimeError("close boom")
        # Should not raise
        client.close()

    def test_close_no_session(self):
        """close() is safe when _session doesn't exist."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase.__new__(InfomaniakRESTBase)
        # _session never set
        client.close()  # Should not raise

    def test_validate_connection_base_returns_true(self):
        """Base validate_connection() returns True (stub)."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase(token="t")
        assert client.validate_connection() is True

    def test_init_strips_trailing_slash(self):
        """base_url trailing slash is stripped."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase(token="t", base_url="https://api.test.com/")
        assert client._base_url == "https://api.test.com"

    def test_init_sets_headers(self):
        """__init__ configures Bearer auth and JSON content type."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase(token="my-token")
        assert client._session.headers["Authorization"] == "Bearer my-token"
        assert client._session.headers["Content-Type"] == "application/json"

    def test_service_name_default(self):
        """Default _service_name is 'rest'."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase
        assert InfomaniakRESTBase._service_name == "rest"

    def test_exit_does_not_suppress_exception(self):
        """__exit__ returns False — does not suppress exceptions."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase(token="t")
        result = client.__exit__(ValueError, ValueError("test"), None)
        assert result is False


# =========================================================================
# Test Auth Module
# =========================================================================

class TestAuthFunctions:
    """Tests for create_openstack_connection and create_s3_client."""

    def test_create_openstack_connection_import_error(self):
        """create_openstack_connection raises ImportError when openstacksdk missing."""
        import sys

        from codomyrmex.cloud.infomaniak.auth import create_openstack_connection

        # Temporarily hide openstack module
        saved = sys.modules.get("openstack")
        sys.modules["openstack"] = None
        try:
            with pytest.raises(ImportError, match="openstacksdk is required"):
                create_openstack_connection(
                    MagicMock()  # credentials arg doesn't matter — import fails first
                )
        finally:
            if saved is not None:
                sys.modules["openstack"] = saved
            else:
                sys.modules.pop("openstack", None)

    def test_create_openstack_connection_auth_failure(self):
        """create_openstack_connection raises InfomaniakAuthError on connection failure."""
        import sys

        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakAuthError,
            InfomaniakCredentials,
            create_openstack_connection,
        )

        mock_openstack = MagicMock()
        mock_openstack.connect.side_effect = Exception("auth failed")
        sys.modules["openstack"] = mock_openstack
        try:
            creds = InfomaniakCredentials(
                application_credential_id="id",
                application_credential_secret="secret",
            )
            with pytest.raises(InfomaniakAuthError, match="Authentication failed"):
                create_openstack_connection(creds)
        finally:
            sys.modules.pop("openstack", None)

    def test_create_openstack_connection_success(self):
        """create_openstack_connection returns Connection on success."""
        import sys

        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakCredentials,
            create_openstack_connection,
        )

        mock_conn = MagicMock()
        mock_openstack = MagicMock()
        mock_openstack.connect.return_value = mock_conn
        sys.modules["openstack"] = mock_openstack
        try:
            creds = InfomaniakCredentials(
                application_credential_id="id",
                application_credential_secret="secret",
            )
            result = create_openstack_connection(creds)
            assert result is mock_conn
            mock_openstack.connect.assert_called_once()
        finally:
            sys.modules.pop("openstack", None)

    def test_create_s3_client_import_error(self):
        """create_s3_client raises ImportError when boto3 missing."""
        import sys

        from codomyrmex.cloud.infomaniak.auth import create_s3_client

        saved = sys.modules.get("boto3")
        sys.modules["boto3"] = None
        try:
            with pytest.raises(ImportError, match="boto3 is required"):
                create_s3_client(MagicMock())
        finally:
            if saved is not None:
                sys.modules["boto3"] = saved
            else:
                sys.modules.pop("boto3", None)

    def test_create_s3_client_success(self):
        """create_s3_client returns boto3 client on success."""
        import sys

        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakS3Credentials,
            create_s3_client,
        )

        mock_s3 = MagicMock()
        mock_boto3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        sys.modules["boto3"] = mock_boto3
        try:
            creds = InfomaniakS3Credentials(
                access_key="ak", secret_key="sk",
            )
            result = create_s3_client(creds)
            assert result is mock_s3
            mock_boto3.client.assert_called_once_with(
                "s3",
                endpoint_url=creds.endpoint_url,
                aws_access_key_id="ak",
                aws_secret_access_key="sk",
                region_name=creds.region,
            )
        finally:
            sys.modules.pop("boto3", None)

    def test_credentials_to_openstack_auth(self):
        """InfomaniakCredentials.to_openstack_auth returns correct dict."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        creds = InfomaniakCredentials(
            application_credential_id="id-123",
            application_credential_secret="secret-456",
            auth_url="https://custom.url/identity/v3/",
        )
        auth = creds.to_openstack_auth()

        assert auth["auth_url"] == "https://custom.url/identity/v3/"
        assert auth["application_credential_id"] == "id-123"
        assert auth["application_credential_secret"] == "secret-456"
        assert len(auth) == 3

    def test_credentials_metadata_field(self):
        """InfomaniakCredentials supports metadata dict."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        creds = InfomaniakCredentials(
            application_credential_id="id",
            application_credential_secret="secret",
            metadata={"env": "prod"},
        )
        assert creds.metadata == {"env": "prod"}

    def test_credentials_default_metadata_empty(self):
        """InfomaniakCredentials metadata defaults to empty dict."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        creds = InfomaniakCredentials(
            application_credential_id="id",
            application_credential_secret="secret",
        )
        assert creds.metadata == {}

    def test_auth_constants(self):
        """Auth module defines correct default constants."""
        from codomyrmex.cloud.infomaniak.auth import (
            DEFAULT_AUTH_URL,
            DEFAULT_S3_ENDPOINT,
            DEFAULT_S3_REGION,
        )
        assert DEFAULT_AUTH_URL == "https://api.pub1.infomaniak.cloud/identity/v3/"
        assert DEFAULT_S3_ENDPOINT == "https://s3.pub1.infomaniak.cloud/"
        assert DEFAULT_S3_REGION == "us-east-1"


# =========================================================================
# Test Module Exports (expanded)
# =========================================================================

class TestExpandedModuleExports:
    """Comprehensive tests for __all__ exports and import paths."""

    def test_classify_http_error_exported(self):
        """classify_http_error is in __all__ and importable."""
        from codomyrmex.cloud.infomaniak import classify_http_error
        assert callable(classify_http_error)

    def test_rest_base_exported(self):
        """InfomaniakRESTBase is in __all__ and importable."""
        from codomyrmex.cloud.infomaniak import InfomaniakRESTBase
        assert InfomaniakRESTBase is not None

    def test_all_exports_importable(self):
        """Every item in __all__ can be imported and is not None."""
        import codomyrmex.cloud.infomaniak as pkg

        for name in pkg.__all__:
            obj = getattr(pkg, name)
            # Client classes may be None if optional deps missing,
            # but base classes and exceptions should always exist
            if name.startswith("Infomaniak") and name.endswith("Client"):
                # Client may be None on systems without openstacksdk/boto3
                continue
            assert obj is not None, f"{name} is None but should be available"

    def test_all_contains_classify_http_error(self):
        """Verify __all__ includes classify_http_error."""
        import codomyrmex.cloud.infomaniak as pkg
        assert "classify_http_error" in pkg.__all__

    def test_all_contains_rest_base(self):
        """Verify __all__ includes InfomaniakRESTBase."""
        import codomyrmex.cloud.infomaniak as pkg
        assert "InfomaniakRESTBase" in pkg.__all__

    def test_newsletter_importable_from_package(self):
        """InfomaniakNewsletterClient importable from package root."""
        from codomyrmex.cloud.infomaniak import InfomaniakNewsletterClient
        assert InfomaniakNewsletterClient is not None

    def test_newsletter_importable_from_submodule(self):
        """InfomaniakNewsletterClient importable from newsletter submodule."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        assert InfomaniakNewsletterClient is not None


# =========================================================================
# ADDITIONAL COMPUTE CLIENT TESTS
# =========================================================================

class TestInfomaniakComputeClientExpanded:
    """Tests for InfomaniakComputeClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient
        mock_conn = MagicMock()
        return InfomaniakComputeClient(connection=mock_conn), mock_conn

    def test_get_image(self):
        """get_image returns dict with image details."""
        client, mc = self._make_client()
        img = MagicMock(id="img-1", status="active",
                        min_disk=10, min_ram=512, size=2048)
        img.name = "Ubuntu"
        mc.image.find_image.return_value = img
        result = client.get_image("img-1")
        mc.image.find_image.assert_called_once_with("img-1")
        assert result["id"] == "img-1"
        assert result["name"] == "Ubuntu"

    def test_get_image_not_found(self):
        """get_image returns None when not found."""
        client, mc = self._make_client()
        mc.image.find_image.return_value = None
        assert client.get_image("nope") is None

    def test_create_keypair(self):
        """create_keypair returns dict with keypair details."""
        client, mc = self._make_client()
        kp = MagicMock(fingerprint="aa:bb", public_key="ssh-rsa AAA")
        kp.name = "mykey"
        kp.private_key = None
        mc.compute.create_keypair.return_value = kp
        result = client.create_keypair("mykey", "ssh-rsa AAA")
        mc.compute.create_keypair.assert_called_once_with(name="mykey", public_key="ssh-rsa AAA")
        assert result["name"] == "mykey"
        assert result["fingerprint"] == "aa:bb"

    def test_delete_keypair(self):
        """delete_keypair calls SDK and returns True."""
        client, mc = self._make_client()
        assert client.delete_keypair("mykey") is True
        mc.compute.delete_keypair.assert_called_once_with("mykey")

    def test_list_availability_zones(self):
        """list_availability_zones returns list of dicts."""
        client, mc = self._make_client()
        az = MagicMock()
        az.name = "dc3-a"
        az.state = {"available": True}
        mc.compute.availability_zones.return_value = [az]
        result = client.list_availability_zones()
        assert len(result) == 1
        assert result[0]["name"] == "dc3-a"

    def test_terminate_instance(self):
        """terminate_instance delegates to delete_instance with force=True."""
        client, mc = self._make_client()
        assert client.terminate_instance("inst-1") is True
        mc.compute.delete_server.assert_called_once_with("inst-1", force=True)

    def test_server_to_dict_flavor_none(self):
        """_server_to_dict handles None flavor safely."""
        client, _ = self._make_client()
        srv = MagicMock(id="s1", name="test", status="ACTIVE",
                        addresses={}, key_name=None, created_at=None,
                        updated_at=None, security_groups=[])
        srv.flavor = None
        srv.image = None
        result = client._server_to_dict(srv)
        assert result["flavor"] is None
        assert result["image"] is None


# =========================================================================
# ADDITIONAL VOLUME CLIENT TESTS
# =========================================================================

class TestInfomaniakVolumeClientExpanded:
    """Tests for InfomaniakVolumeClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.block_storage import InfomaniakVolumeClient
        mock_conn = MagicMock()
        return InfomaniakVolumeClient(connection=mock_conn), mock_conn

    def test_get_volume(self):
        """get_volume returns dict via _volume_to_dict."""
        client, mc = self._make_client()
        vol = MagicMock(id="v1", name="data", status="available", size=50,
                        volume_type="SSD", availability_zone="dc3-a",
                        is_bootable=False, is_encrypted=False,
                        attachments=[], created_at=None)
        mc.block_storage.get_volume.return_value = vol
        result = client.get_volume("v1")
        assert result["id"] == "v1"
        assert result["size"] == 50

    def test_create_backup(self):
        """create_backup returns dict with backup details."""
        client, mc = self._make_client()
        bk = MagicMock(id="bk1", name="mybk", status="creating", volume_id="v1")
        mc.block_storage.create_backup.return_value = bk
        result = client.create_backup("v1", "mybk")
        assert result["id"] == "bk1"
        assert result["volume_id"] == "v1"

    def test_restore_backup(self):
        """restore_backup returns dict with volume_id."""
        client, mc = self._make_client()
        res = MagicMock(volume_id="v-new")
        mc.block_storage.restore_backup.return_value = res
        result = client.restore_backup("bk1")
        assert result["volume_id"] == "v-new"

    def test_delete_backup(self):
        """delete_backup returns True on success."""
        client, mc = self._make_client()
        assert client.delete_backup("bk1") is True
        mc.block_storage.delete_backup.assert_called_once_with("bk1", force=False)

    def test_create_snapshot(self):
        """create_snapshot returns dict with snapshot details."""
        client, mc = self._make_client()
        snap = MagicMock(id="sn1", name="mysnap", status="creating", volume_id="v1")
        mc.block_storage.create_snapshot.return_value = snap
        result = client.create_snapshot("v1", "mysnap")
        assert result["id"] == "sn1"

    def test_delete_snapshot(self):
        """delete_snapshot returns True on success."""
        client, mc = self._make_client()
        assert client.delete_snapshot("sn1") is True
        mc.block_storage.delete_snapshot.assert_called_once_with("sn1", force=False)

    def test_list_volumes_error(self):
        """list_volumes returns [] on error."""
        client, mc = self._make_client()
        mc.block_storage.volumes.side_effect = Exception("fail")
        assert client.list_volumes() == []


# =========================================================================
# ADDITIONAL NETWORK CLIENT TESTS
# =========================================================================

class TestInfomaniakNetworkClientExpanded:
    """Tests for InfomaniakNetworkClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.network import InfomaniakNetworkClient
        mock_conn = MagicMock()
        return InfomaniakNetworkClient(connection=mock_conn), mock_conn

    def test_create_subnet(self):
        client, mc = self._make_client()
        sn = MagicMock(id="sn1", name="sub1", cidr="10.0.0.0/24")
        mc.network.create_subnet.return_value = sn
        result = client.create_subnet("n1", "sub1", "10.0.0.0/24")
        assert result["id"] == "sn1"

    def test_create_router(self):
        client, mc = self._make_client()
        rt = MagicMock(id="rt1", name="router1")
        mc.network.create_router.return_value = rt
        result = client.create_router("router1")
        assert result["id"] == "rt1"

    def test_add_router_interface(self):
        client, mc = self._make_client()
        assert client.add_router_interface("rt1", "sn1") is True
        mc.network.add_interface_to_router.assert_called_once_with("rt1", subnet_id="sn1")

    def test_delete_router(self):
        client, mc = self._make_client()
        assert client.delete_router("rt1") is True
        mc.network.delete_router.assert_called_once_with("rt1")

    def test_create_security_group(self):
        client, mc = self._make_client()
        sg = MagicMock(id="sg1", name="web")
        mc.network.create_security_group.return_value = sg
        result = client.create_security_group("web")
        assert result["id"] == "sg1"

    def test_delete_security_group(self):
        client, mc = self._make_client()
        assert client.delete_security_group("sg1") is True

    def test_allocate_floating_ip(self):
        client, mc = self._make_client()
        ext = MagicMock(id="ext1")
        mc.network.find_network.return_value = ext
        fip = MagicMock(id="fip1", floating_ip_address="1.2.3.4")
        mc.network.create_ip.return_value = fip
        result = client.allocate_floating_ip("external")
        assert result["floating_ip_address"] == "1.2.3.4"

    def test_associate_floating_ip(self):
        client, mc = self._make_client()
        assert client.associate_floating_ip("fip1", "port1") is True
        mc.network.update_ip.assert_called_once_with("fip1", port_id="port1")

    def test_create_loadbalancer(self):
        client, mc = self._make_client()
        lb = MagicMock(id="lb1", name="web-lb", vip_address="10.0.0.5")
        mc.load_balancer.create_load_balancer.return_value = lb
        result = client.create_loadbalancer("web-lb", "sn1")
        assert result["id"] == "lb1"

    def test_delete_loadbalancer(self):
        client, mc = self._make_client()
        assert client.delete_loadbalancer("lb1") is True

    def test_list_subnets(self):
        client, mc = self._make_client()
        sn = MagicMock(id="sn1", name="s", network_id="n1", cidr="10.0.0.0/24",
                       ip_version=4, gateway_ip="10.0.0.1", is_dhcp_enabled=True)
        mc.network.subnets.return_value = [sn]
        result = client.list_subnets()
        assert len(result) == 1
        assert result[0]["id"] == "sn1"

    def test_get_subnet(self):
        client, mc = self._make_client()
        sn = MagicMock(id="sn1", name="s", network_id="n1", cidr="10.0.0.0/24",
                       ip_version=4, gateway_ip="10.0.0.1")
        mc.network.get_subnet.return_value = sn
        result = client.get_subnet("sn1")
        assert result["id"] == "sn1"

    def test_delete_subnet(self):
        client, mc = self._make_client()
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
        li = MagicMock(id="li1", name="http", protocol="HTTP", protocol_port=80)
        mc.load_balancer.listeners.return_value = [li]
        result = client.list_listeners()
        assert len(result) == 1

    def test_create_listener(self):
        client, mc = self._make_client()
        li = MagicMock(id="li1", name="http")
        mc.load_balancer.create_listener.return_value = li
        result = client.create_listener("lb1", "http", "HTTP", 80)
        assert result["id"] == "li1"

    def test_delete_listener(self):
        client, mc = self._make_client()
        assert client.delete_listener("li1") is True

    def test_list_pools(self):
        client, mc = self._make_client()
        p = MagicMock(id="p1", name="pool1", protocol="HTTP", lb_algorithm="ROUND_ROBIN")
        mc.load_balancer.pools.return_value = [p]
        result = client.list_pools()
        assert len(result) == 1

    def test_create_pool(self):
        client, mc = self._make_client()
        p = MagicMock(id="p1", name="pool1")
        mc.load_balancer.create_pool.return_value = p
        result = client.create_pool("pool1", "HTTP", "ROUND_ROBIN")
        assert result["id"] == "p1"

    def test_delete_pool(self):
        client, mc = self._make_client()
        assert client.delete_pool("p1") is True

    def test_list_pool_members(self):
        client, mc = self._make_client()
        m = MagicMock(id="m1", name="srv1", address="10.0.0.2",
                      protocol_port=80, weight=1)
        mc.load_balancer.members.return_value = [m]
        result = client.list_pool_members("p1")
        assert len(result) == 1

    def test_add_pool_member(self):
        client, mc = self._make_client()
        m = MagicMock(id="m1")
        mc.load_balancer.create_member.return_value = m
        result = client.add_pool_member("p1", "10.0.0.2", 80)
        assert result["id"] == "m1"

    def test_remove_pool_member(self):
        client, mc = self._make_client()
        assert client.remove_pool_member("p1", "m1") is True
        mc.load_balancer.delete_member.assert_called_once_with("m1", "p1")

    def test_list_health_monitors(self):
        client, mc = self._make_client()
        hm = MagicMock(id="hm1", name="check", type="HTTP",
                       delay=5, timeout=3, max_retries=3)
        mc.load_balancer.health_monitors.return_value = [hm]
        result = client.list_health_monitors()
        assert len(result) == 1

    def test_create_health_monitor(self):
        """Uses renamed monitor_type parameter."""
        client, mc = self._make_client()
        hm = MagicMock(id="hm1")
        mc.load_balancer.create_health_monitor.return_value = hm
        result = client.create_health_monitor("p1", monitor_type="HTTP", delay=5, timeout=3)
        assert result["id"] == "hm1"
        assert result["type"] == "HTTP"

    def test_delete_health_monitor(self):
        client, mc = self._make_client()
        assert client.delete_health_monitor("hm1") is True

    def test_remove_router_interface(self):
        client, mc = self._make_client()
        assert client.remove_router_interface("rt1", "sn1") is True
        mc.network.remove_interface_from_router.assert_called_once_with("rt1", subnet_id="sn1")

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

class TestInfomaniakSwiftClientExpanded:
    """Tests for InfomaniakObjectStorageClient (Swift) untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.object_storage import (
            InfomaniakObjectStorageClient,
        )
        mock_conn = MagicMock()
        return InfomaniakObjectStorageClient(connection=mock_conn), mock_conn

    def test_delete_container(self):
        client, mc = self._make_client()
        assert client.delete_container("mybucket") is True
        mc.object_store.delete_container.assert_called_once_with("mybucket")

    def test_get_container_metadata(self):
        client, mc = self._make_client()
        meta = MagicMock()
        meta.metadata = {"x-count": "5"}
        mc.object_store.get_container_metadata.return_value = meta
        result = client.get_container_metadata("mybucket")
        assert isinstance(result, dict)

    def test_list_objects(self):
        client, mc = self._make_client()
        obj = MagicMock()
        obj.name = "file.txt"
        mc.object_store.objects.return_value = [obj]
        result = client.list_objects("mybucket")
        assert result == ["file.txt"]

    def test_list_objects_with_prefix(self):
        client, mc = self._make_client()
        mc.object_store.objects.return_value = []
        client.list_objects("mybucket", prefix="logs/")
        mc.object_store.objects.assert_called_once_with("mybucket", prefix="logs/")

    def test_get_object_metadata(self):
        client, mc = self._make_client()
        obj = MagicMock(content_length=1024,
                        content_type="text/plain", etag="abc",
                        last_modified_at=None)
        obj.name = "file.txt"
        mc.object_store.get_object_metadata.return_value = obj
        result = client.get_object_metadata("mybucket", "file.txt")
        assert result["name"] == "file.txt"
        assert result["content_length"] == 1024

    def test_set_container_read_acl(self):
        client, mc = self._make_client()
        assert client.set_container_read_acl("mybucket", ".r:*") is True
        mc.object_store.set_container_metadata.assert_called_once()

    def test_set_container_write_acl(self):
        client, mc = self._make_client()
        assert client.set_container_write_acl("mybucket", "user:admin") is True

    def test_list_containers_error(self):
        client, mc = self._make_client()
        mc.object_store.containers.side_effect = Exception("fail")
        assert client.list_containers() == []


# =========================================================================
# ADDITIONAL S3 CLIENT TESTS
# =========================================================================

class TestInfomaniakS3ClientExpanded:
    """Tests for InfomaniakS3Client untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakS3Client
        mock_s3 = MagicMock()
        return InfomaniakS3Client(client=mock_s3), mock_s3

    def test_create_bucket(self):
        client, s3 = self._make_client()
        assert client.create_bucket("mybucket") is True
        s3.create_bucket.assert_called_once_with(Bucket="mybucket")

    def test_delete_bucket(self):
        client, s3 = self._make_client()
        assert client.delete_bucket("mybucket") is True
        s3.delete_bucket.assert_called_once_with(Bucket="mybucket")

    def test_upload_file(self):
        client, s3 = self._make_client()
        assert client.upload_file("bkt", "key.txt", "/tmp/f.txt") is True
        s3.upload_file.assert_called_once_with("/tmp/f.txt", "bkt", "key.txt", ExtraArgs=None)

    def test_download_file(self):
        client, s3 = self._make_client()
        assert client.download_file("bkt", "key.txt", "/tmp/out.txt") is True
        s3.download_file.assert_called_once_with("bkt", "key.txt", "/tmp/out.txt")

    def test_delete_file_delegates(self):
        client, s3 = self._make_client()
        assert client.delete_file("bkt", "key.txt") is True
        s3.delete_object.assert_called_once_with(Bucket="bkt", Key="key.txt")

    def test_get_metadata(self):
        client, s3 = self._make_client()
        s3.head_object.return_value = {
            "ContentLength": 100, "ContentType": "text/plain",
            "ETag": '"abc"', "LastModified": "2026-01-01",
            "Metadata": {}
        }
        result = client.get_metadata("bkt", "key.txt")
        assert result["content_length"] == 100
        assert result["content_type"] == "text/plain"

    def test_copy_object(self):
        client, s3 = self._make_client()
        assert client.copy_object("src", "sk", "dst", "dk") is True
        s3.copy_object.assert_called_once_with(
            Bucket="dst", Key="dk",
            CopySource={"Bucket": "src", "Key": "sk"}
        )

    def test_list_objects_paginated(self):
        client, s3 = self._make_client()
        paginator = MagicMock()
        paginator.paginate.return_value = [
            {"Contents": [{"Key": "a.txt"}, {"Key": "b.txt"}]}
        ]
        s3.get_paginator.return_value = paginator
        result = client.list_objects_paginated("bkt")
        assert result == ["a.txt", "b.txt"]

    def test_delete_objects_batch(self):
        client, s3 = self._make_client()
        s3.delete_objects.return_value = {
            "Deleted": [{"Key": "a.txt"}, {"Key": "b.txt"}],
            "Errors": []
        }
        result = client.delete_objects_batch("bkt", ["a.txt", "b.txt"])
        assert result["deleted"] == 2
        assert result["errors"] == []

    def test_enable_versioning(self):
        client, s3 = self._make_client()
        assert client.enable_versioning("bkt") is True
        s3.put_bucket_versioning.assert_called_once()

    def test_get_versioning(self):
        client, s3 = self._make_client()
        s3.get_bucket_versioning.return_value = {"Status": "Enabled"}
        assert client.get_versioning("bkt") == "Enabled"

    def test_get_bucket_policy(self):
        client, s3 = self._make_client()
        s3.get_bucket_policy.return_value = {"Policy": '{"Version":"2012"}'}
        assert client.get_bucket_policy("bkt") == '{"Version":"2012"}'

    def test_put_bucket_policy(self):
        client, s3 = self._make_client()
        assert client.put_bucket_policy("bkt", '{"Version":"2012"}') is True
        s3.put_bucket_policy.assert_called_once()

    def test_list_buckets_error(self):
        client, s3 = self._make_client()
        s3.list_buckets.side_effect = Exception("fail")
        assert client.list_buckets() == []


# =========================================================================
# ADDITIONAL IDENTITY CLIENT TESTS
# =========================================================================

class TestInfomaniakIdentityClientExpanded:
    """Tests for InfomaniakIdentityClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.identity import InfomaniakIdentityClient
        mock_conn = MagicMock()
        mock_conn.current_user_id = "uid-1"
        mock_conn.current_project_id = "proj-1"
        return InfomaniakIdentityClient(connection=mock_conn), mock_conn

    def test_get_user(self):
        client, mc = self._make_client()
        u = MagicMock(id="u1", domain_id="d1")
        u.name = "alice"
        mc.identity.get_user.return_value = u
        result = client.get_user("u1")
        assert result["id"] == "u1"
        assert result["name"] == "alice"

    def test_get_current_project(self):
        client, mc = self._make_client()
        p = MagicMock(id="proj-1", name="default", description="desc")
        mc.identity.get_project.return_value = p
        result = client.get_current_project()
        assert result["id"] == "proj-1"

    def test_create_application_credential(self):
        client, mc = self._make_client()
        cred = MagicMock(id="ac1", name="mycred", secret="s3cret", expires_at=None)
        mc.identity.create_application_credential.return_value = cred
        result = client.create_application_credential("mycred")
        assert result["id"] == "ac1"
        assert result["secret"] == "s3cret"

    def test_get_application_credential(self):
        client, mc = self._make_client()
        cred = MagicMock(id="ac1", name="mycred", expires_at=None)
        mc.identity.get_application_credential.return_value = cred
        result = client.get_application_credential("ac1")
        assert result["id"] == "ac1"

    def test_delete_application_credential(self):
        client, mc = self._make_client()
        assert client.delete_application_credential("ac1") is True

    def test_list_roles(self):
        client, mc = self._make_client()
        r = MagicMock(id="r1", description="Full access")
        r.name = "admin"
        mc.identity.roles.return_value = [r]
        result = client.list_roles()
        assert len(result) == 1
        assert result[0]["name"] == "admin"

    def test_list_user_roles(self):
        client, mc = self._make_client()
        ra = MagicMock()
        ra.role = {"id": "r1"}
        role = MagicMock(id="r1")
        role.name = "member"
        mc.identity.role_assignments.return_value = [ra]
        mc.identity.get_role.return_value = role
        result = client.list_user_roles()
        assert len(result) == 1
        assert result[0]["name"] == "member"

    def test_list_ec2_credentials(self):
        client, mc = self._make_client()
        cred = MagicMock(id="ec1", access="AK123", project_id="proj-1", type="ec2")
        mc.identity.credentials.return_value = [cred]
        result = client.list_ec2_credentials()
        assert len(result) == 1
        assert result[0]["access"] == "AK123"

    def test_list_projects_error(self):
        client, mc = self._make_client()
        mc.identity.projects.side_effect = Exception("fail")
        assert client.list_projects() == []


# =========================================================================
# ADDITIONAL DNS CLIENT TESTS
# =========================================================================

class TestInfomaniakDNSClientExpanded:
    """Tests for InfomaniakDNSClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.dns import InfomaniakDNSClient
        mock_conn = MagicMock()
        return InfomaniakDNSClient(connection=mock_conn), mock_conn

    def test_get_zone(self):
        client, mc = self._make_client()
        z = MagicMock(id="z1", email="a@b.com",
                      status="ACTIVE", ttl=3600)
        z.name = "example.com."
        mc.dns.find_zone.return_value = z
        result = client.get_zone("z1")
        assert result["id"] == "z1"
        assert result["name"] == "example.com."

    def test_update_zone(self):
        client, mc = self._make_client()
        assert client.update_zone("z1", email="new@b.com") is True
        mc.dns.update_zone.assert_called_once_with("z1", email="new@b.com")

    def test_get_record(self):
        client, mc = self._make_client()
        r = MagicMock(id="r1", name="www.example.com.", type="A",
                      records=["1.2.3.4"], ttl=300)
        mc.dns.get_recordset.return_value = r
        result = client.get_record("z1", "r1")
        assert result["id"] == "r1"
        assert result["type"] == "A"

    def test_update_record(self):
        client, mc = self._make_client()
        assert client.update_record("z1", "r1", records=["5.6.7.8"]) is True

    def test_list_ptr_records(self):
        client, mc = self._make_client()
        ptr = MagicMock(id="ptr1", ptrdname="host.example.com.",
                        address="1.2.3.4", status="ACTIVE")
        mc.dns.ptr_records.return_value = [ptr]
        result = client.list_ptr_records()
        assert len(result) == 1
        assert result[0]["ptrdname"] == "host.example.com."

    def test_set_reverse_dns(self):
        client, mc = self._make_client()
        fip = MagicMock(id="fip1")
        mc.network.find_ip.return_value = fip
        ptr = MagicMock(id="ptr1")
        mc.dns.create_ptr_record.return_value = ptr
        result = client.set_reverse_dns("1.2.3.4", "host.example.com")
        assert result["address"] == "1.2.3.4"
        assert result["ptrdname"] == "host.example.com."

    def test_get_reverse_dns(self):
        client, mc = self._make_client()
        fip = MagicMock(id="fip1")
        mc.network.find_ip.return_value = fip
        ptr = MagicMock(id="ptr1", ptrdname="host.example.com.", ttl=3600)
        mc.dns.get_ptr_record.return_value = ptr
        result = client.get_reverse_dns("1.2.3.4")
        assert result["ptrdname"] == "host.example.com."

    def test_delete_reverse_dns(self):
        client, mc = self._make_client()
        fip = MagicMock(id="fip1")
        mc.network.find_ip.return_value = fip
        assert client.delete_reverse_dns("1.2.3.4") is True
        mc.dns.delete_ptr_record.assert_called_once_with("fip1")

    def test_list_zones_error(self):
        client, mc = self._make_client()
        mc.dns.zones.side_effect = Exception("fail")
        assert client.list_zones() == []


# =========================================================================
# ADDITIONAL HEAT (ORCHESTRATION) CLIENT TESTS
# =========================================================================

class TestInfomaniakHeatClientExpanded:
    """Tests for InfomaniakHeatClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.orchestration import InfomaniakHeatClient
        mock_conn = MagicMock()
        return InfomaniakHeatClient(connection=mock_conn), mock_conn

    def test_update_stack(self):
        client, mc = self._make_client()
        assert client.update_stack("stk1", template="heat: {}") is True
        mc.orchestration.update_stack.assert_called_once()

    def test_suspend_stack(self):
        client, mc = self._make_client()
        assert client.suspend_stack("stk1") is True
        mc.orchestration.suspend_stack.assert_called_once_with("stk1")

    def test_resume_stack(self):
        client, mc = self._make_client()
        assert client.resume_stack("stk1") is True
        mc.orchestration.resume_stack.assert_called_once_with("stk1")

    def test_get_stack_resource(self):
        client, mc = self._make_client()
        res = MagicMock(name="srv", resource_type="OS::Nova::Server",
                        status="CREATE_COMPLETE", physical_resource_id="inst1",
                        attributes={"ip": "1.2.3.4"})
        mc.orchestration.get_resource.return_value = res
        result = client.get_stack_resource("stk1", "srv")
        assert result["resource_type"] == "OS::Nova::Server"

    def test_list_stack_events(self):
        client, mc = self._make_client()
        ev = MagicMock(id="ev1", resource_name="srv",
                       resource_status="CREATE_COMPLETE",
                       resource_status_reason="OK", event_time=None)
        mc.orchestration.events.return_value = [ev]
        result = client.list_stack_events("stk1")
        assert len(result) == 1
        assert result[0]["resource_name"] == "srv"

    def test_get_stack_template(self):
        client, mc = self._make_client()
        tpl = "heat_template_version: 2021-04-16"
        mc.orchestration.get_stack_template.return_value = tpl
        assert client.get_stack_template("stk1") == tpl

    def test_get_stack_outputs(self):
        client, mc = self._make_client()
        stk = MagicMock()
        stk.outputs = [
            {"output_key": "server_ip", "output_value": "10.0.0.5"}
        ]
        mc.orchestration.find_stack.return_value = stk
        result = client.get_stack_outputs("stk1")
        assert result["server_ip"] == "10.0.0.5"

    def test_list_stacks_error(self):
        client, mc = self._make_client()
        mc.orchestration.stacks.side_effect = Exception("fail")
        assert client.list_stacks() == []


# =========================================================================
# ADDITIONAL METERING CLIENT TESTS
# =========================================================================

class TestInfomaniakMeteringClientExpanded:
    """Tests for InfomaniakMeteringClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.metering import InfomaniakMeteringClient
        mock_conn = MagicMock()
        mock_conn.current_project_id = "proj-1"
        return InfomaniakMeteringClient(connection=mock_conn), mock_conn

    def test_get_object_storage_usage(self):
        client, mc = self._make_client()
        c = MagicMock(count=100, bytes=2048000)
        mc.object_store.containers.return_value = [c]
        result = client.get_object_storage_usage()
        assert result["container_count"] == 1
        assert result["object_count"] == 100
        assert result["total_bytes"] == 2048000

    def test_list_resources_with_usage(self):
        client, mc = self._make_client()
        srv = MagicMock(id="s1", name="web", status="ACTIVE", created_at=None)
        vol = MagicMock(id="v1", name="data", status="in-use", size=50)
        fip = MagicMock(id="f1", floating_ip_address="1.2.3.4", status="ACTIVE", port_id="p1")
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
        q = MagicMock(networks=10, subnets=20, routers=5,
                      floatingips=3, security_groups=10, security_group_rules=50)
        mc.network.get_quota.return_value = q
        result = client.get_network_quotas()
        assert result["networks"] == 10
        assert result["floating_ips"] == 3

    def test_get_storage_quotas(self):
        client, mc = self._make_client()
        q = MagicMock(volumes=20, gigabytes=1000, snapshots=10, backups=5)
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

class TestClientFactoryMethodsExpanded:
    """Factory method tests for clients not previously tested."""

    @patch("codomyrmex.cloud.infomaniak.auth.create_openstack_connection")
    def test_volume_from_credentials(self, mock_create):
        from codomyrmex.cloud.infomaniak.block_storage import InfomaniakVolumeClient
        mock_create.return_value = MagicMock()
        client = InfomaniakVolumeClient.from_credentials("id", "secret")
        assert isinstance(client, InfomaniakVolumeClient)

    @patch("codomyrmex.cloud.infomaniak.auth.create_openstack_connection")
    def test_network_from_credentials(self, mock_create):
        from codomyrmex.cloud.infomaniak.network import InfomaniakNetworkClient
        mock_create.return_value = MagicMock()
        client = InfomaniakNetworkClient.from_credentials("id", "secret")
        assert isinstance(client, InfomaniakNetworkClient)

    @patch("codomyrmex.cloud.infomaniak.auth.create_openstack_connection")
    def test_dns_from_credentials(self, mock_create):
        from codomyrmex.cloud.infomaniak.dns import InfomaniakDNSClient
        mock_create.return_value = MagicMock()
        client = InfomaniakDNSClient.from_credentials("id", "secret")
        assert isinstance(client, InfomaniakDNSClient)

    @patch("codomyrmex.cloud.infomaniak.auth.create_openstack_connection")
    def test_heat_from_credentials(self, mock_create):
        from codomyrmex.cloud.infomaniak.orchestration import InfomaniakHeatClient
        mock_create.return_value = MagicMock()
        client = InfomaniakHeatClient.from_credentials("id", "secret")
        assert isinstance(client, InfomaniakHeatClient)

    @patch("codomyrmex.cloud.infomaniak.auth.create_openstack_connection")
    def test_metering_from_credentials(self, mock_create):
        from codomyrmex.cloud.infomaniak.metering import InfomaniakMeteringClient
        mock_create.return_value = MagicMock()
        client = InfomaniakMeteringClient.from_credentials("id", "secret")
        assert isinstance(client, InfomaniakMeteringClient)


# =========================================================================
# NEWSLETTER VALIDATION TESTS
# =========================================================================

class TestNewsletterValidationExpanded:
    """Tests for newsletter input validation and edge cases."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(
            token="test-token", newsletter_id="nl-1",
            base_url="https://api.infomaniak.com"
        )
        client._session = MagicMock()
        return client

    def test_manage_contact_invalid_action(self):
        """manage_contact raises ValueError for invalid action."""
        client = self._make_client()
        with pytest.raises(ValueError, match="Invalid action"):
            client.manage_contact("list-1", "contact-1", "delete")

    def test_manage_contact_subscribe(self):
        """manage_contact accepts 'subscribe' action."""
        client = self._make_client()
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"data": {"ok": True}}
        resp.raise_for_status = MagicMock()
        client._session.post.return_value = resp
        assert client.manage_contact("list-1", "c1", "subscribe") is True

    def test_manage_contact_unsubscribe(self):
        """manage_contact accepts 'unsubscribe' action."""
        client = self._make_client()
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"data": {"ok": True}}
        resp.raise_for_status = MagicMock()
        client._session.post.return_value = resp
        assert client.manage_contact("list-1", "c1", "unsubscribe") is True

    def test_list_campaigns_dict_with_items_key(self):
        """list_campaigns extracts from dict with 'items' key."""
        client = self._make_client()
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"data": {"items": [{"id": "c1"}], "total": 1}}
        resp.raise_for_status = MagicMock()
        client._session.get.return_value = resp
        result = client.list_campaigns()
        assert result == [{"id": "c1"}]

    def test_list_mailing_lists_dict_with_items_key(self):
        """list_mailing_lists extracts from dict with 'items' key."""
        client = self._make_client()
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"data": {"items": [{"id": "ml1"}], "total": 1}}
        resp.raise_for_status = MagicMock()
        client._session.get.return_value = resp
        result = client.list_mailing_lists()
        assert result == [{"id": "ml1"}]
