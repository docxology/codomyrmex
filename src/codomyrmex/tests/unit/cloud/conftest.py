"""
Shared test fixtures for Infomaniak cloud client tests.

Provides mock OpenStack connections, S3 clients, and factory helpers
used across all per-client test files.
"""

import pytest
from unittest.mock import MagicMock


# =========================================================================
# Connection Fixtures
# =========================================================================

@pytest.fixture
def mock_openstack_connection():
    """Create a fully-mocked OpenStack connection with all service subsystems."""
    conn = MagicMock()
    conn.current_user_id = "user-test-123"
    conn.current_project_id = "proj-test-456"
    return conn


@pytest.fixture
def mock_s3_client():
    """Create a mock boto3 S3 client."""
    return MagicMock()


# =========================================================================
# Environment Variable Fixtures
# =========================================================================

@pytest.fixture
def infomaniak_openstack_env():
    """Standard env vars for OpenStack connections."""
    return {
        "INFOMANIAK_APP_CREDENTIAL_ID": "test-cred-id",
        "INFOMANIAK_APP_CREDENTIAL_SECRET": "test-cred-secret",
        "INFOMANIAK_AUTH_URL": "https://api.pub1.infomaniak.cloud/identity/v3/",
        "INFOMANIAK_REGION": "dc3-a",
    }


@pytest.fixture
def infomaniak_s3_env():
    """Standard env vars for S3 connections."""
    return {
        "INFOMANIAK_S3_ACCESS_KEY": "test-s3-access",
        "INFOMANIAK_S3_SECRET_KEY": "test-s3-secret",
        "INFOMANIAK_S3_ENDPOINT": "https://s3.pub1.infomaniak.cloud/",
    }


# =========================================================================
# Mock Object Factories
# =========================================================================

def make_mock_server(
    server_id="server-123",
    name="test-server",
    status="ACTIVE",
    flavor_id="flavor-1",
    image_id="image-1",
):
    """Create a mock OpenStack server object."""
    server = MagicMock()
    server.id = server_id
    server.name = name
    server.status = status
    server.flavor = {"id": flavor_id}
    server.image = {"id": image_id}
    server.addresses = {"network1": [{"addr": "10.0.0.1"}]}
    server.key_name = "my-key"
    server.created_at = None
    server.updated_at = None
    server.availability_zone = "dc3-a"
    server.security_groups = [{"name": "default"}]
    return server


def make_mock_volume(
    volume_id="vol-123",
    name="test-volume",
    status="available",
    size=100,
):
    """Create a mock OpenStack volume object."""
    volume = MagicMock()
    volume.id = volume_id
    volume.name = name
    volume.status = status
    volume.size = size
    volume.volume_type = "ssd"
    volume.availability_zone = "dc3-a"
    volume.is_bootable = False
    volume.is_encrypted = False
    volume.attachments = []
    volume.created_at = None
    return volume


def make_mock_network(
    network_id="net-123",
    name="test-network",
    status="ACTIVE",
):
    """Create a mock OpenStack network object."""
    network = MagicMock()
    network.id = network_id
    network.name = name
    network.status = status
    network.is_shared = False
    network.is_router_external = False
    network.subnet_ids = ["subnet-1"]
    return network


def make_mock_zone(
    zone_id="zone-123",
    name="example.com.",
    email="admin@example.com",
):
    """Create a mock DNS zone object."""
    zone = MagicMock()
    zone.id = zone_id
    zone.name = name
    zone.email = email
    zone.status = "ACTIVE"
    zone.type = "PRIMARY"
    zone.ttl = 3600
    return zone


def make_mock_stack(
    stack_id="stack-123",
    name="test-stack",
    status="CREATE_COMPLETE",
):
    """Create a mock Heat stack object."""
    stack = MagicMock()
    stack.id = stack_id
    stack.name = name
    stack.status = status
    stack.status_reason = f"Stack {status}"
    stack.description = "Test stack"
    stack.parameters = {"key": "value"}
    stack.outputs = [{"output_key": "ip", "output_value": "10.0.0.1"}]
    stack.created_at = None
    stack.updated_at = None
    return stack


def make_mock_image(
    image_id="img-123",
    name="Ubuntu 22.04",
    status="active",
):
    """Create a mock Glance image object."""
    image = MagicMock()
    image.id = image_id
    image.name = name
    image.status = status
    image.min_disk = 10
    image.min_ram = 512
    image.size = 2147483648
    image.created_at = None
    return image


def make_mock_floating_ip(
    fip_id="fip-123",
    address="195.15.220.10",
    status="ACTIVE",
    port_id="port-abc",
):
    """Create a mock floating IP object."""
    fip = MagicMock()
    fip.id = fip_id
    fip.floating_ip_address = address
    fip.fixed_ip_address = "10.0.0.5"
    fip.status = status
    fip.port_id = port_id
    return fip


def make_mock_container(
    name="test-container",
    count=10,
    bytes_used=1024000,
):
    """Create a mock Swift container object."""
    container = MagicMock()
    container.name = name
    container.count = count
    container.bytes = bytes_used
    return container
