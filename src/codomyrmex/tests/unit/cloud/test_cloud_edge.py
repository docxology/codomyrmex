"""Tests for cloud.edge module."""

import pytest

try:
    from codomyrmex.cloud.edge import (
        CloudflareWorkersClient,
        EdgeDeployment,
        EdgeFunctionConfig,
        EdgeManager,
        EdgeProvider,
        EdgeRegion,
        FastlyComputeClient,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("cloud.edge module not available", allow_module_level=True)


@pytest.mark.unit
class TestEdgeProvider:
    """Test suite for EdgeProvider."""
    def test_cloudflare(self):
        """Test functionality: cloudflare."""
        assert EdgeProvider.CLOUDFLARE_WORKERS is not None

    def test_fastly(self):
        """Test functionality: fastly."""
        assert EdgeProvider.FASTLY_COMPUTE is not None

    def test_aws_lambda_edge(self):
        """Test functionality: aws lambda edge."""
        assert EdgeProvider.AWS_LAMBDA_EDGE is not None

    def test_vercel(self):
        """Test functionality: vercel."""
        assert EdgeProvider.VERCEL_EDGE is not None

    def test_deno(self):
        """Test functionality: deno."""
        assert EdgeProvider.DENO_DEPLOY is not None


@pytest.mark.unit
class TestEdgeRegion:
    """Test suite for EdgeRegion."""
    def test_global(self):
        """Test functionality: global."""
        assert EdgeRegion.GLOBAL is not None

    def test_us_east(self):
        """Test functionality: us east."""
        assert EdgeRegion.US_EAST is not None

    def test_europe(self):
        """Test functionality: europe."""
        assert EdgeRegion.EUROPE is not None


@pytest.mark.unit
class TestEdgeFunctionConfig:
    """Test suite for EdgeFunctionConfig."""
    def test_create_config(self):
        """Test functionality: create config."""
        config = EdgeFunctionConfig(
            name="worker",
            provider=EdgeProvider.CLOUDFLARE_WORKERS,
        )
        assert config.name == "worker"
        assert config.entry_point == "handler"
        assert config.runtime == "javascript"
        assert config.memory_mb == 128
        assert config.timeout_seconds == 30

    def test_config_with_routes(self):
        """Test functionality: config with routes."""
        config = EdgeFunctionConfig(
            name="api",
            provider=EdgeProvider.VERCEL_EDGE,
            routes=["/api/*"],
        )
        assert len(config.routes) == 1


@pytest.mark.unit
class TestEdgeDeployment:
    """Test suite for EdgeDeployment."""
    def test_create_deployment(self):
        """Test functionality: create deployment."""
        deployment = EdgeDeployment(
            id="deploy-1",
            function_name="worker",
            provider=EdgeProvider.CLOUDFLARE_WORKERS,
            version="1.0.0",
        )
        assert deployment.id == "deploy-1"
        assert deployment.status == "active"
        assert deployment.url == ""


@pytest.mark.unit
class TestCloudflareWorkersClient:
    """Test suite for CloudflareWorkersClient."""
    def test_create_client(self):
        """Test functionality: create client."""
        client = CloudflareWorkersClient(account_id="acc-123", api_token="token-123")
        assert client is not None
        assert client.provider == EdgeProvider.CLOUDFLARE_WORKERS


@pytest.mark.unit
class TestFastlyComputeClient:
    """Test suite for FastlyComputeClient."""
    def test_create_client(self):
        """Test functionality: create client."""
        client = FastlyComputeClient(api_key="key-123")
        assert client is not None
        assert client.provider == EdgeProvider.FASTLY_COMPUTE


@pytest.mark.unit
class TestEdgeManager:
    """Test suite for EdgeManager."""
    def test_create_manager(self):
        """Test functionality: create manager."""
        manager = EdgeManager()
        assert manager is not None

    def test_register_client(self):
        """Test functionality: register client."""
        manager = EdgeManager()
        client = CloudflareWorkersClient(account_id="acc", api_token="tok")
        manager.register_client(client)
        retrieved = manager.get_client(EdgeProvider.CLOUDFLARE_WORKERS)
        assert retrieved is not None
