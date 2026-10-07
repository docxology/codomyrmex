"""Infrastructure Agent for cloud operations.

Follows the GitAgent pattern — BaseAgent subclass with JSON command dispatch.
"""

import contextlib
import json
from collections.abc import Iterator
from typing import Any

from codomyrmex.agents.core.base import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.logging_monitoring import get_logger

from .tool_factory import CloudToolFactory, Tool

logger = get_logger(__name__)

# Lazy import for security pipeline
with contextlib.suppress(ImportError):
    from codomyrmex.cloud.infomaniak.security import CloudSecurityPipeline


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
        if clients and any(name in clients for name in ("s3", "object_storage")):
            capabilities.append(AgentCapabilities.CLOUD_STORAGE)

        super().__init__(
            name="InfrastructureAgent",
            capabilities=capabilities,
            config=config,
        )
        #: Services left out by :meth:`from_env`, mapped to the reason.
        self.skipped_clients: dict[str, str] = {}

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

        Each Infomaniak client is created from its own environment variables.
        A client whose credentials are missing or invalid, or whose SDK is not
        installed, is left out; which ones were skipped, and why, is logged at
        INFO level and listed in ``skipped_clients``.
        """
        from codomyrmex.cloud import infomaniak
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakCloudError

        factories = {
            "compute": "InfomaniakComputeClient",
            "volume": "InfomaniakVolumeClient",
            "network": "InfomaniakNetworkClient",
            "s3": "InfomaniakS3Client",
            "dns": "InfomaniakDNSClient",
            "orchestration": "InfomaniakHeatClient",
        }
        clients: dict[str, Any] = {}
        skipped: dict[str, str] = {}
        for service, class_name in factories.items():
            try:
                clients[service] = getattr(infomaniak, class_name).from_env()
            except (
                ImportError,
                OSError,
                ValueError,
                AttributeError,
                InfomaniakCloudError,
            ) as exc:
                skipped[service] = f"{type(exc).__name__}: {exc}"
                logger.info("Infomaniak %s client unavailable: %s", service, exc)

        agent = cls(clients=clients)
        agent.skipped_clients = skipped
        return agent

    # ------------------------------------------------------------------
    # Agent interface
    # ------------------------------------------------------------------

    def _execute_impl(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
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
            params = {k: v for k, v in data.items() if k not in ("service", "action")}

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
            logger.exception("InfrastructureAgent execution error: %s", e)
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
        CloudToolFactory.register_all_clients(target, self._clients, self._pipeline)
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
                        logger.warning("Connection test failed for %s", name)
                        return False
                except (AttributeError, TypeError, OSError, ConnectionError):
                    logger.warning("Connection test error for %s", name)
                    return False
        return True
