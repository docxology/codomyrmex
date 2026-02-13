"""
Shared pytest fixtures for cloud tests.

The ``Stub`` class and factory helpers live in ``_stubs.py`` so they
can be imported explicitly by test modules.  This file re-exports
fixtures that inject them.
"""

import sys
from pathlib import Path

import pytest

# Ensure _stubs.py is importable from test modules
sys.path.insert(0, str(Path(__file__).parent))

from _stubs import (  # noqa: F401, E402  – re-exported for fixture use
    Stub,
    make_stub_container,
    make_stub_floating_ip,
    make_stub_image,
    make_stub_network,
    make_stub_server,
    make_stub_stack,
    make_stub_volume,
    make_stub_zone,
)


# =========================================================================
# Connection Fixtures
# =========================================================================

@pytest.fixture
def mock_openstack_connection():
    """Create a fully-stubbed OpenStack connection with all service subsystems."""
    conn = Stub()
    conn.current_user_id = "user-test-123"
    conn.current_project_id = "proj-test-456"
    return conn


@pytest.fixture
def mock_s3_client():
    """Create a stub boto3 S3 client."""
    return Stub()


# =========================================================================
# Environment Variable Fixtures
# =========================================================================

@pytest.fixture
def infomaniak_openstack_env(monkeypatch):
    """Set standard env vars for OpenStack connections."""
    monkeypatch.setenv("INFOMANIAK_APP_CREDENTIAL_ID", "test-cred-id")
    monkeypatch.setenv("INFOMANIAK_APP_CREDENTIAL_SECRET", "test-cred-secret")
    monkeypatch.setenv("INFOMANIAK_AUTH_URL", "https://api.pub1.infomaniak.cloud/identity/v3/")
    monkeypatch.setenv("INFOMANIAK_REGION", "dc3-a")


@pytest.fixture
def infomaniak_s3_env(monkeypatch):
    """Set standard env vars for S3 connections."""
    monkeypatch.setenv("INFOMANIAK_S3_ACCESS_KEY", "test-s3-access")
    monkeypatch.setenv("INFOMANIAK_S3_SECRET_KEY", "test-s3-secret")
    monkeypatch.setenv("INFOMANIAK_S3_ENDPOINT", "https://s3.pub1.infomaniak.cloud/")
