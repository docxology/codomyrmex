"""
Unit tests for Infomaniak Compute Client (Nova).

Tests cover:
- Base class inheritance and service name
- Context manager protocol
- from_env factory delegation
- Instance CRUD operations (list, get, create, start, stop, reboot, delete, terminate)
- Image operations (list, get, get returns None)
- Flavor operations (list)
- Keypair operations (list, create with public_key, create generates private_key, delete)
- Availability zone operations (list)
- Error paths (graceful degradation returning [] / None / False)

Total: ~24 tests across 7 test classes.
"""

import os
from _stubs import Stub


from codomyrmex.cloud.common import ComputeClient
from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase
from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient
from _stubs import make_stub_image, make_stub_server

import pytest
try:
    import openstack
    HAS_OPENSTACK = True
except ImportError:
    HAS_OPENSTACK = False

# =========================================================================
# Base Class & Construction
# =========================================================================


class TestComputeClientBase:
    """Tests for InfomaniakComputeClient class hierarchy and construction."""

    def test_inherits_from_openstack_base(self):
        """InfomaniakComputeClient inherits from InfomaniakOpenStackBase."""
        assert issubclass(InfomaniakComputeClient, InfomaniakOpenStackBase)

    def test_inherits_from_compute_client_abc(self):
        """InfomaniakComputeClient also inherits from ComputeClient ABC."""
        assert issubclass(InfomaniakComputeClient, ComputeClient)

    def test_service_name_is_compute(self, mock_openstack_connection):
        """The _service_name class attribute is set to 'compute'."""
        client = InfomaniakComputeClient(mock_openstack_connection)
        assert client._service_name == "compute"

    def test_context_manager_enter_returns_self(self, mock_openstack_connection):
        """Using the client as a context manager returns itself on __enter__."""
        client = InfomaniakComputeClient(mock_openstack_connection)

        with client as ctx:
            assert ctx is client

    def test_context_manager_calls_close(self, mock_openstack_connection):
        """Exiting the context manager calls close() on the connection."""
        client = InfomaniakComputeClient(mock_openstack_connection)

        with client:
            pass

        mock_openstack_connection.close.assert_called_once()


# =========================================================================
# Instance Operations
# =========================================================================


class TestComputeInstanceOps:
    """Tests for instance lifecycle operations."""

    def test_list_instances(self, mock_openstack_connection):
        """list_instances returns a list of dicts from OpenStack servers."""
        server = make_stub_server()
        mock_openstack_connection.compute.servers.return_value = [server]

        client = InfomaniakComputeClient(mock_openstack_connection)
        instances = client.list_instances()

        assert len(instances) == 1
        assert instances[0]["id"] == "server-123"
        assert instances[0]["name"] == "test-server"
        assert instances[0]["status"] == "ACTIVE"
        assert instances[0]["key_name"] == "my-key"
        assert instances[0]["availability_zone"] == "dc3-a"
        assert "default" in instances[0]["security_groups"]

    def test_get_instance(self, mock_openstack_connection):
        """get_instance returns a dict for a specific server ID."""
        server = make_stub_server(server_id="srv-abc", name="specific-server")
        mock_openstack_connection.compute.get_server.return_value = server

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.get_instance("srv-abc")

        assert result is not None
        assert result["id"] == "srv-abc"
        assert result["name"] == "specific-server"
        mock_openstack_connection.compute.get_server.assert_called_once_with("srv-abc")

    def test_create_instance_happy_path(self, mock_openstack_connection):
        """create_instance resolves flavor/image/network and returns created server."""
        # Set up resolved objects
        mock_flavor = Stub()
        mock_flavor.id = "flavor-a1"
        mock_image = Stub()
        mock_image.id = "img-ubuntu"
        mock_network = Stub()
        mock_network.id = "net-main"

        mock_openstack_connection.compute.find_flavor.return_value = mock_flavor
        mock_openstack_connection.image.find_image.return_value = mock_image
        mock_openstack_connection.network.find_network.return_value = mock_network

        created = make_stub_server(server_id="srv-new", name="new-instance")
        mock_openstack_connection.compute.create_server.return_value = created
        mock_openstack_connection.compute.wait_for_server.return_value = created

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.create_instance(
            name="new-instance",
            flavor="a1-ram2-disk20-perf1",
            image="Ubuntu 22.04",
            network="my-network",
            key_name="my-key",
        )

        assert result is not None
        assert result["id"] == "srv-new"
        mock_openstack_connection.compute.create_server.assert_called_once()
        mock_openstack_connection.compute.wait_for_server.assert_called_once_with(
            created
        )

    def test_create_instance_flavor_not_found(self, mock_openstack_connection):
        """create_instance returns None when the flavor is not found."""
        mock_openstack_connection.compute.find_flavor.return_value = None

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.create_instance(
            name="bad-flavor",
            flavor="nonexistent-flavor",
            image="Ubuntu 22.04",
            network="net-1",
        )

        assert result is None
        mock_openstack_connection.compute.create_server.assert_not_called()

    def test_create_instance_image_not_found(self, mock_openstack_connection):
        """create_instance returns None when the image is not found."""
        mock_flavor = Stub()
        mock_flavor.id = "flavor-1"
        mock_openstack_connection.compute.find_flavor.return_value = mock_flavor
        mock_openstack_connection.image.find_image.return_value = None

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.create_instance(
            name="bad-image",
            flavor="a1-ram2-disk20-perf1",
            image="nonexistent-image",
            network="net-1",
        )

        assert result is None
        mock_openstack_connection.compute.create_server.assert_not_called()

    def test_create_instance_network_not_found(self, mock_openstack_connection):
        """create_instance returns None when the network is not found."""
        mock_flavor = Stub()
        mock_flavor.id = "flavor-1"
        mock_image = Stub()
        mock_image.id = "image-1"
        mock_openstack_connection.compute.find_flavor.return_value = mock_flavor
        mock_openstack_connection.image.find_image.return_value = mock_image
        mock_openstack_connection.network.find_network.return_value = None

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.create_instance(
            name="bad-network",
            flavor="a1-ram2-disk20-perf1",
            image="Ubuntu 22.04",
            network="nonexistent-network",
        )

        assert result is None
        mock_openstack_connection.compute.create_server.assert_not_called()

    def test_start_instance(self, mock_openstack_connection):
        """start_instance calls start_server and returns True."""
        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.start_instance("srv-stopped")

        assert result is True
        mock_openstack_connection.compute.start_server.assert_called_once_with(
            "srv-stopped"
        )

    def test_stop_instance(self, mock_openstack_connection):
        """stop_instance calls stop_server and returns True."""
        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.stop_instance("srv-running")

        assert result is True
        mock_openstack_connection.compute.stop_server.assert_called_once_with(
            "srv-running"
        )

    def test_reboot_instance(self, mock_openstack_connection):
        """reboot_instance calls reboot_server with the requested reboot type."""
        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.reboot_instance("srv-123", reboot_type="HARD")

        assert result is True
        mock_openstack_connection.compute.reboot_server.assert_called_once_with(
            "srv-123", "HARD"
        )

    def test_delete_instance(self, mock_openstack_connection):
        """delete_instance calls delete_server with force=False by default."""
        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.delete_instance("srv-del")

        assert result is True
        mock_openstack_connection.compute.delete_server.assert_called_once_with(
            "srv-del", force=False
        )

    def test_terminate_instance_delegates_to_delete(self, mock_openstack_connection):
        """terminate_instance is an alias that calls delete_instance with force=True."""
        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.terminate_instance("srv-term")

        assert result is True
        mock_openstack_connection.compute.delete_server.assert_called_once_with(
            "srv-term", force=True
        )


# =========================================================================
# Image Operations
# =========================================================================


class TestComputeImageOps:
    """Tests for image listing and retrieval."""

    def test_list_images(self, mock_openstack_connection):
        """list_images returns a list of image dicts from Glance."""
        img = make_stub_image(image_id="img-ubuntu", name="Ubuntu 22.04")
        mock_openstack_connection.image.images.return_value = [img]

        client = InfomaniakComputeClient(mock_openstack_connection)
        images = client.list_images()

        assert len(images) == 1
        assert images[0]["id"] == "img-ubuntu"
        assert images[0]["name"] == "Ubuntu 22.04"
        assert images[0]["min_disk"] == 10
        assert images[0]["min_ram"] == 512

    def test_get_image(self, mock_openstack_connection):
        """get_image returns a dict for a found image."""
        img = make_stub_image(image_id="img-found", name="Debian 12")
        mock_openstack_connection.image.find_image.return_value = img

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.get_image("img-found")

        assert result is not None
        assert result["id"] == "img-found"
        assert result["name"] == "Debian 12"
        mock_openstack_connection.image.find_image.assert_called_once_with("img-found")

    def test_get_image_returns_none_when_not_found(self, mock_openstack_connection):
        """get_image returns None when the image does not exist."""
        mock_openstack_connection.image.find_image.return_value = None

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.get_image("img-missing")

        assert result is None


# =========================================================================
# Flavor Operations
# =========================================================================


class TestComputeFlavorOps:
    """Tests for flavor listing."""

    def test_list_flavors(self, mock_openstack_connection):
        """list_flavors returns flavor dicts with vcpus, ram, disk."""
        mock_flavor = Stub()
        mock_flavor.id = "a1-ram2-disk20-perf1"
        mock_flavor.name = "a1-ram2-disk20-perf1"
        mock_flavor.vcpus = 1
        mock_flavor.ram = 2048
        mock_flavor.disk = 20
        mock_flavor.is_public = True

        mock_openstack_connection.compute.flavors.return_value = [mock_flavor]

        client = InfomaniakComputeClient(mock_openstack_connection)
        flavors = client.list_flavors()

        assert len(flavors) == 1
        assert flavors[0]["id"] == "a1-ram2-disk20-perf1"
        assert flavors[0]["vcpus"] == 1
        assert flavors[0]["ram"] == 2048
        assert flavors[0]["disk"] == 20
        assert flavors[0]["is_public"] is True


# =========================================================================
# Keypair Operations
# =========================================================================


class TestComputeKeypairOps:
    """Tests for SSH keypair management."""

    def test_list_keypairs(self, mock_openstack_connection):
        """list_keypairs returns keypair dicts with name and fingerprint."""
        mock_kp = Stub()
        mock_kp.name = "deploy-key"
        mock_kp.fingerprint = "aa:bb:cc:dd:ee:ff"
        mock_kp.type = "ssh"

        mock_openstack_connection.compute.keypairs.return_value = [mock_kp]

        client = InfomaniakComputeClient(mock_openstack_connection)
        keypairs = client.list_keypairs()

        assert len(keypairs) == 1
        assert keypairs[0]["name"] == "deploy-key"
        assert keypairs[0]["fingerprint"] == "aa:bb:cc:dd:ee:ff"
        assert keypairs[0]["type"] == "ssh"

    def test_create_keypair_with_public_key(self, mock_openstack_connection):
        """create_keypair imports an existing public key and returns the result."""
        mock_kp = Stub()
        mock_kp.name = "imported-key"
        mock_kp.fingerprint = "11:22:33:44"
        mock_kp.public_key = "ssh-rsa AAAA..."
        mock_kp.private_key = None

        mock_openstack_connection.compute.create_keypair.return_value = mock_kp

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.create_keypair(
            name="imported-key", public_key="ssh-rsa AAAA..."
        )

        assert result is not None
        assert result["name"] == "imported-key"
        assert result["public_key"] == "ssh-rsa AAAA..."
        assert "private_key" not in result
        mock_openstack_connection.compute.create_keypair.assert_called_once_with(
            name="imported-key", public_key="ssh-rsa AAAA..."
        )

    def test_create_keypair_generates_private_key(self, mock_openstack_connection):
        """create_keypair without public_key generates a new pair with private_key."""
        mock_kp = Stub()
        mock_kp.name = "generated-key"
        mock_kp.fingerprint = "55:66:77:88"
        mock_kp.public_key = "ssh-rsa BBBB..."
        mock_kp.private_key = "-----BEGIN RSA PRIVATE KEY-----\nMIIE..."

        mock_openstack_connection.compute.create_keypair.return_value = mock_kp

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.create_keypair(name="generated-key")

        assert result is not None
        assert result["name"] == "generated-key"
        assert result["public_key"] == "ssh-rsa BBBB..."
        assert "private_key" in result
        assert result["private_key"].startswith("-----BEGIN RSA PRIVATE KEY-----")
        mock_openstack_connection.compute.create_keypair.assert_called_once_with(
            name="generated-key", public_key=None
        )

    def test_delete_keypair(self, mock_openstack_connection):
        """delete_keypair calls delete_keypair on the connection and returns True."""
        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.delete_keypair("old-key")

        assert result is True
        mock_openstack_connection.compute.delete_keypair.assert_called_once_with(
            "old-key"
        )


# =========================================================================
# Availability Zone Operations
# =========================================================================


class TestComputeAZOps:
    """Tests for availability zone listing."""

    def test_list_availability_zones(self, mock_openstack_connection):
        """list_availability_zones returns zone dicts with name and state."""
        mock_zone = Stub()
        mock_zone.name = "dc3-a"
        mock_zone.state = {"available": True}

        mock_openstack_connection.compute.availability_zones.return_value = [mock_zone]

        client = InfomaniakComputeClient(mock_openstack_connection)
        zones = client.list_availability_zones()

        assert len(zones) == 1
        assert zones[0]["name"] == "dc3-a"
        assert zones[0]["state"] is True


# =========================================================================
# Error Paths
# =========================================================================


class TestComputeErrorPaths:
    """Tests verifying graceful error handling returns safe defaults."""

    def test_list_instances_error_returns_empty_list(self, mock_openstack_connection):
        """Connection error during list_instances returns [] instead of raising."""
        mock_openstack_connection.compute.servers.side_effect = Exception(
            "Connection refused"
        )

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.list_instances()

        assert result == []

    def test_get_instance_error_returns_none(self, mock_openstack_connection):
        """Exception during get_instance returns None instead of raising."""
        mock_openstack_connection.compute.get_server.side_effect = Exception(
            "Server error"
        )

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.get_instance("srv-bad")

        assert result is None

    def test_create_instance_error_returns_none(self, mock_openstack_connection):
        """Exception during create_instance returns None instead of raising."""
        mock_openstack_connection.compute.find_flavor.side_effect = Exception(
            "API timeout"
        )

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.create_instance(
            name="fail-server",
            flavor="a1-ram2",
            image="Ubuntu",
            network="net-1",
        )

        assert result is None

    def test_list_flavors_error_returns_empty_list(self, mock_openstack_connection):
        """Exception during list_flavors returns [] instead of raising."""
        mock_openstack_connection.compute.flavors.side_effect = Exception(
            "Service unavailable"
        )

        client = InfomaniakComputeClient(mock_openstack_connection)
        result = client.list_flavors()

        assert result == []


# =========================================================================

class TestInfomaniakComputeClientExpanded:
    """Tests for InfomaniakComputeClient untested methods."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.compute import InfomaniakComputeClient
        mock_conn = Stub()
        return InfomaniakComputeClient(connection=mock_conn), mock_conn

    def test_get_image(self):
        """get_image returns dict with image details."""
        client, mc = self._make_client()
        img = Stub(id="img-1", status="active",
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
        kp = Stub(fingerprint="aa:bb", public_key="ssh-rsa AAA")
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
        az = Stub()
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
        srv = Stub(id="s1", name="test", status="ACTIVE",
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
