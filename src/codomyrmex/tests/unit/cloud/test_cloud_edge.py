"""Tests for cloud.edge module."""

import pytest

try:
    from codomyrmex.cloud.edge import (
        CloudflareWorkersClient,
        EdgeClient,
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
    def test_cloudflare(self):
        assert EdgeProvider.CLOUDFLARE_WORKERS is not None

    def test_fastly(self):
        assert EdgeProvider.FASTLY_COMPUTE is not None

    def test_aws_lambda_edge(self):
        assert EdgeProvider.AWS_LAMBDA_EDGE is not None

    def test_vercel(self):
        assert EdgeProvider.VERCEL_EDGE is not None

    def test_deno(self):
        assert EdgeProvider.DENO_DEPLOY is not None


@pytest.mark.unit
class TestEdgeRegion:
    def test_global(self):
        assert EdgeRegion.GLOBAL is not None

    def test_us_east(self):
        assert EdgeRegion.US_EAST is not None

    def test_europe(self):
        assert EdgeRegion.EUROPE is not None


@pytest.mark.unit
class TestEdgeFunctionConfig:
    def test_create_config(self):
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
        config = EdgeFunctionConfig(
            name="api",
            provider=EdgeProvider.VERCEL_EDGE,
            routes=["/api/*"],
        )
        assert len(config.routes) == 1


@pytest.mark.unit
class TestEdgeDeployment:
    def test_create_deployment(self):
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
    def test_create_client(self):
        client = CloudflareWorkersClient(account_id="acc-123", api_token="token-123")
        assert client is not None
        assert client.provider == EdgeProvider.CLOUDFLARE_WORKERS


@pytest.mark.unit
class TestFastlyComputeClient:
    def test_create_client(self):
        client = FastlyComputeClient(api_key="key-123")
        assert client is not None
        assert client.provider == EdgeProvider.FASTLY_COMPUTE


@pytest.mark.unit
class TestEdgeManager:
    def test_create_manager(self):
        manager = EdgeManager()
        assert manager is not None

    def test_register_client(self):
        manager = EdgeManager()
        client = CloudflareWorkersClient(account_id="acc", api_token="tok")
        manager.register_client(client)
        retrieved = manager.get_client(EdgeProvider.CLOUDFLARE_WORKERS)
        assert retrieved is not None
