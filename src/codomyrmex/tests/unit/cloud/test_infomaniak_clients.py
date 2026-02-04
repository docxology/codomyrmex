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
- InfomaniakNewsletterClient
- Authentication utilities and error paths
- Factory methods (from_credentials)
- Module-level exports and CloudConfig integration

Total: ~100 tests across 14 test classes.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from dataclasses import asdict
from datetime import datetime, timezone


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
            InfomaniakCredentials,
            InfomaniakAuthError,
        )

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(InfomaniakAuthError, match="Missing required environment variables"):
                InfomaniakCredentials.from_env()

    def test_s3_credentials_missing_env_vars(self):
        """Missing INFOMANIAK_S3_ACCESS_KEY/SECRET raises InfomaniakAuthError."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakS3Credentials,
            InfomaniakAuthError,
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

            from codomyrmex.cloud.infomaniak.object_storage import InfomaniakObjectStorageClient

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
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakObjectStorageClient

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
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakObjectStorageClient

        client = InfomaniakObjectStorageClient(mock_connection)
        result = client.create_container("my-container")

        assert result is True
        mock_connection.object_store.create_container.assert_called_once_with("my-container")

    def test_upload_object(self, mock_connection):
        """Test uploading an object to a Swift container."""
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakObjectStorageClient

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
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakObjectStorageClient

        mock_connection.object_store.download_object.return_value = b"swift data"

        client = InfomaniakObjectStorageClient(mock_connection)
        data = client.download_object("my-container", "test.txt")

        assert data == b"swift data"
        mock_connection.object_store.download_object.assert_called_once_with(
            "my-container", "test.txt"
        )

    def test_delete_object(self, mock_connection):
        """Test deleting an object from a Swift container."""
        from codomyrmex.cloud.infomaniak.object_storage import InfomaniakObjectStorageClient

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
    """Tests for InfomaniakNewsletterClient."""

    def _make_client(self):
        """Create a newsletter client with test credentials."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        return InfomaniakNewsletterClient(
            token="test-token",
            newsletter_id="nl-123",
            base_url="https://api.infomaniak.com",
        )

    def test_newsletter_from_credentials(self):
        """Test creating client with explicit credentials."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        client = InfomaniakNewsletterClient.from_credentials(
            token="tok-abc",
            newsletter_id="nl-456",
        )
        assert client._token == "tok-abc"
        assert client._newsletter_id == "nl-456"

    def test_newsletter_from_env(self):
        """Test creating client from environment variables."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        with patch.dict("os.environ", {
            "INFOMANIAK_NEWSLETTER_TOKEN": "env-token",
            "INFOMANIAK_NEWSLETTER_ID": "env-nl-id",
        }):
            client = InfomaniakNewsletterClient.from_env()
            assert client._token == "env-token"
            assert client._newsletter_id == "env-nl-id"

    def test_newsletter_from_env_missing(self):
        """Test that missing env vars raises ValueError."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables"):
                InfomaniakNewsletterClient.from_env()

    @patch("codomyrmex.cloud.infomaniak.newsletter.client.requests.Session")
    def test_list_campaigns(self, MockSession):
        """Test listing campaigns."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": [
            {"id": "camp-1", "subject": "Test Campaign", "status": "draft"},
        ]}
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_resp
        MockSession.return_value = mock_session

        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(token="t", newsletter_id="n")
        campaigns = client.list_campaigns()

        assert len(campaigns) == 1
        assert campaigns[0]["id"] == "camp-1"
        assert campaigns[0]["subject"] == "Test Campaign"

    @patch("codomyrmex.cloud.infomaniak.newsletter.client.requests.Session")
    def test_create_campaign(self, MockSession):
        """Test creating a campaign."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {"id": "camp-new", "subject": "New"}}
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.post.return_value = mock_resp
        MockSession.return_value = mock_session

        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(token="t", newsletter_id="n")
        result = client.create_campaign(
            subject="New",
            sender_email="news@activeinference.tech",
            sender_name="AI Institute",
            content_html="<h1>Hello</h1>",
            mailing_list_id="ml-1",
        )

        assert result is not None
        assert result["id"] == "camp-new"
        mock_session.post.assert_called_once()

    @patch("codomyrmex.cloud.infomaniak.newsletter.client.requests.Session")
    def test_send_campaign(self, MockSession):
        """Test sending a campaign."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {"status": "sending"}}
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.post.return_value = mock_resp
        MockSession.return_value = mock_session

        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(token="t", newsletter_id="n")
        result = client.send_campaign("camp-1")

        assert result is True

    @patch("codomyrmex.cloud.infomaniak.newsletter.client.requests.Session")
    def test_list_mailing_lists(self, MockSession):
        """Test listing mailing lists."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": [
            {"id": "ml-1", "name": "Subscribers"},
            {"id": "ml-2", "name": "VIPs"},
        ]}
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_resp
        MockSession.return_value = mock_session

        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(token="t", newsletter_id="n")
        lists = client.list_mailing_lists()

        assert len(lists) == 2
        assert lists[0]["name"] == "Subscribers"

    @patch("codomyrmex.cloud.infomaniak.newsletter.client.requests.Session")
    def test_create_mailing_list(self, MockSession):
        """Test creating a mailing list."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {"id": "ml-new", "name": "New List"}}
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.post.return_value = mock_resp
        MockSession.return_value = mock_session

        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(token="t", newsletter_id="n")
        result = client.create_mailing_list("New List")

        assert result is not None
        assert result["name"] == "New List"

    @patch("codomyrmex.cloud.infomaniak.newsletter.client.requests.Session")
    def test_import_contacts(self, MockSession):
        """Test importing contacts to a mailing list."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {"task_id": "task-123", "imported": 3}}
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.post.return_value = mock_resp
        MockSession.return_value = mock_session

        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(token="t", newsletter_id="n")
        result = client.import_contacts("ml-1", [
            {"email": "a@example.com"},
            {"email": "b@example.com"},
            {"email": "c@example.com"},
        ])

        assert result is not None
        assert result["task_id"] == "task-123"

    @patch("codomyrmex.cloud.infomaniak.newsletter.client.requests.Session")
    def test_get_campaign_statistics(self, MockSession):
        """Test getting campaign statistics."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {
            "sent": 1000, "opened": 450, "clicked": 120, "bounced": 5,
        }}
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_resp
        MockSession.return_value = mock_session

        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(token="t", newsletter_id="n")
        stats = client.get_campaign_statistics("camp-1")

        assert stats is not None
        assert stats["sent"] == 1000
        assert stats["opened"] == 450

    @patch("codomyrmex.cloud.infomaniak.newsletter.client.requests.Session")
    def test_get_credits(self, MockSession):
        """Test getting newsletter credits."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {"remaining": 5000, "used": 1500}}
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get.return_value = mock_resp
        MockSession.return_value = mock_session

        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(token="t", newsletter_id="n")
        credits = client.get_credits()

        assert credits is not None
        assert credits["remaining"] == 5000

    @patch("codomyrmex.cloud.infomaniak.newsletter.client.requests.Session")
    def test_error_handling(self, MockSession):
        """Test that API errors return None/False/[] instead of raising."""
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("500 Server Error")
        mock_session.get.return_value = mock_resp
        mock_session.post.return_value = mock_resp
        mock_session.delete.return_value = mock_resp
        MockSession.return_value = mock_session

        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(token="t", newsletter_id="n")

        # GET operations return None or empty list
        assert client.list_campaigns() == []
        assert client.get_campaign("123") is None
        assert client.get_credits() is None

        # POST operations return None or False
        assert client.send_campaign("123") is False

        # DELETE operations return False
        assert client.delete_campaign("123") is False
