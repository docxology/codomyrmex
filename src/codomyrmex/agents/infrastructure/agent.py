"""Infrastructure Agent for cloud operations.

Follows the GitAgent pattern — BaseAgent subclass with JSON command dispatch.
"""

import json
import logging
from typing import Any
from collections.abc import Iterator

from codomyrmex.agents.core.base import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)

from .tool_factory import CloudToolFactory, Tool

logger = logging.getLogger(__name__)

# Lazy import for security pipeline
try:
    from codomyrmex.cloud.infomaniak.security import CloudSecurityPipeline
except ImportError:
    CloudSecurityPipeline = None


class InfrastructureAgent(BaseAgent):
    """Agent specialized for cloud infrastructure operations.

    Capabilities:
    - Multi-service cloud management (compute, storage, network, DNS, etc.)
    - Security pipeline integration (exploit detection, identity checks)
    - Auto-generated tool registry from client methods
    """

    def __init__(
        self,
        clients: dict[str, Any] | None = None,
        security_pipeline: Any = None,
        config: dict[str, Any] | None = None,
    ):
        capabilities = [AgentCapabilities.CLOUD_INFRASTRUCTURE]
        if clients and any(
            name in clients for name in ("s3", "object_storage")
        ):
            capabilities.append(AgentCapabilities.CLOUD_STORAGE)

        super().__init__(
            name="InfrastructureAgent",
            capabilities=capabilities,
            config=config,
        )

        self._clients: dict[str, Any] = clients or {}
        self._pipeline = security_pipeline
        if self._pipeline is None and CloudSecurityPipeline is not None:
            self._pipeline = CloudSecurityPipeline()
        self._tool_registry: dict[str, Tool] = {}

    # ------------------------------------------------------------------
    # Class methods
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls) -> "InfrastructureAgent":
        """Create an InfrastructureAgent from environment variables.

        Attempts to create each client type, silently skipping unavailable ones.
        """
        clients: dict[str, Any] = {}

        # Compute
        try:
            from codomyrmex.cloud.infomaniak import InfomaniakComputeClient
            clients["compute"] = InfomaniakComputeClient.from_env()
        except Exception:
            logger.debug("Compute client unavailable")

        # Volume
        try:
            from codomyrmex.cloud.infomaniak import InfomaniakVolumeClient
            clients["volume"] = InfomaniakVolumeClient.from_env()
        except Exception:
            logger.debug("Volume client unavailable")

        # Network
        try:
            from codomyrmex.cloud.infomaniak import InfomaniakNetworkClient
            clients["network"] = InfomaniakNetworkClient.from_env()
        except Exception:
            logger.debug("Network client unavailable")

        # S3
        try:
            from codomyrmex.cloud.infomaniak import InfomaniakS3Client
            clients["s3"] = InfomaniakS3Client.from_env()
        except Exception:
            logger.debug("S3 client unavailable")

        # DNS
        try:
            from codomyrmex.cloud.infomaniak import InfomaniakDNSClient
            clients["dns"] = InfomaniakDNSClient.from_env()
        except Exception:
            logger.debug("DNS client unavailable")

        # Heat
        try:
            from codomyrmex.cloud.infomaniak import InfomaniakHeatClient
            clients["orchestration"] = InfomaniakHeatClient.from_env()
        except Exception:
            logger.debug("Heat client unavailable")

        return cls(clients=clients)

    # ------------------------------------------------------------------
    # Agent interface
    # ------------------------------------------------------------------

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute a cloud infrastructure request.

        Expected prompt format (JSON):
            {"service": "compute", "action": "list_instances", ...params}
        """
        try:
            if not request.prompt.strip().startswith("{"):
                return AgentResponse(
                    content="",
                    error="Expected JSON prompt with 'service' and 'action' keys",
                )

            data = json.loads(request.prompt)
            service = data.get("service")
            action = data.get("action")

            if not service or not action:
                return AgentResponse(
                    content="",
                    error="JSON must contain 'service' and 'action' keys",
                )

            client = self._clients.get(service)
            if client is None:
                available = list(self._clients.keys())
                return AgentResponse(
                    content="",
                    error=f"Service '{service}' not configured. Available: {available}",
                )

            method = getattr(client, action, None)
            if method is None or not callable(method):
                return AgentResponse(
                    content="",
                    error=f"Action '{action}' not found on {service} client",
                )

            # Extract params (everything except service/action)
            params = {
                k: v for k, v in data.items() if k not in ("service", "action")
            }

            # Security pre-check
            if self._pipeline is not None:
                check = self._pipeline.pre_check(action, params)
                if not check.allowed:
                    return AgentResponse(
                        content="",
                        error=f"Security check failed: {check.reason}",
                        metadata={"security_blocked": True},
                    )

            result = method(**params)

            # Security post-process
            if self._pipeline is not None:
                result = self._pipeline.post_process(action, result)

            return AgentResponse(
                content=json.dumps(result, default=str),
                metadata={"service": service, "action": action},
            )

        except json.JSONDecodeError as e:
            return AgentResponse(content="", error=f"Invalid JSON: {e}")
        except TypeError as e:
            return AgentResponse(content="", error=f"Parameter error: {e}")
        except Exception as e:
            logger.exception(f"InfrastructureAgent execution error: {e}")
            return AgentResponse(content="", error=str(e))

    def stream(self, request: AgentRequest) -> Iterator[str]:
        """Streaming not supported — yields execute result."""
        yield self.execute(request).content

    # ------------------------------------------------------------------
    # Tool registry
    # ------------------------------------------------------------------

    def populate_tool_registry(
        self, registry: dict[str, Tool] | None = None
    ) -> dict[str, Tool]:
        """Auto-generate Tool objects from client methods.

        Args:
            registry: External registry to populate. If None, uses internal.

        Returns:
            The populated registry.
        """
        target = registry if registry is not None else self._tool_registry
        CloudToolFactory.register_all_clients(
            target, self._clients, self._pipeline
        )
        return target

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def available_services(self) -> list[str]:
        """Return names of configured services."""
        return list(self._clients.keys())

    def test_connection(self) -> bool:
        """Test connectivity to all configured clients."""
        if not self._clients:
            return False

        for name, client in self._clients.items():
            validate = getattr(client, "validate_connection", None)
            if validate and callable(validate):
                try:
                    if not validate():
                        logger.warning(f"Connection test failed for {name}")
                        return False
                except Exception:
                    logger.warning(f"Connection test error for {name}")
                    return False
        return True
