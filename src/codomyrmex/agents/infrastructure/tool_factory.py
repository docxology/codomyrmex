"""Cloud Tool Factory.

Auto-generates Tool objects from Infomaniak client methods via introspection.
"""

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class Tool:
    """Lightweight tool descriptor for agent registries."""
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    handler: Callable | None = None


def _method_to_args_schema(method: Callable) -> dict[str, Any]:
    """Extract a JSON-schema-like parameter dict from a method signature."""
    sig = inspect.signature(method)
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        if param_name.startswith("_"):
            continue

        prop: dict[str, Any] = {}
        annotation = param.annotation

        if annotation is inspect.Parameter.empty:
            prop["type"] = "string"
        elif annotation is str:
            prop["type"] = "string"
        elif annotation is int:
            prop["type"] = "integer"
        elif annotation is float:
            prop["type"] = "number"
        elif annotation is bool:
            prop["type"] = "boolean"
        else:
            prop["type"] = "string"

        if param.default is inspect.Parameter.empty:
            required.append(param_name)
        else:
            prop["default"] = (
                param.default if not isinstance(param.default, type) else None
            )

        properties[param_name] = prop

    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required
    return schema


def _is_public_method(name: str, obj: Any) -> bool:
    """Check if name refers to a public, callable method."""
    return (
        callable(obj)
        and not name.startswith("_")
        and not isinstance(obj, type)
    )


class CloudToolFactory:
    """Generates Tool objects from cloud client methods."""

    @staticmethod
    def register_client(
        client: Any,
        service_name: str,
        registry: dict[str, Tool],
        security_pipeline: Any = None,
    ) -> list[str]:
        """Register all public methods of a client as tools.

        Args:
            client: An Infomaniak client instance.
            service_name: Service label (e.g., "compute", "s3").
            registry: Dict to populate with tool_name -> Tool.
            security_pipeline: Optional CloudSecurityPipeline for wrapping.

        Returns:
            List of registered tool names.
        """
        registered = []

        for method_name in dir(client):
            method = getattr(client, method_name, None)
            if not _is_public_method(method_name, method):
                continue

            tool_name = f"infomaniak_{service_name}_{method_name}"
            schema = _method_to_args_schema(method)

            handler = method
            if security_pipeline is not None:
                handler = CloudToolFactory._wrap_with_security(
                    method, method_name, security_pipeline
                )

            tool = Tool(
                name=tool_name,
                description=f"{service_name}.{method_name}",
                parameters=schema,
                handler=handler,
            )
            registry[tool_name] = tool
            registered.append(tool_name)

        logger.info(
            f"Registered {len(registered)} tools for service '{service_name}'"
        )
        return registered

    @staticmethod
    def register_all_clients(
        registry: dict[str, Tool],
        clients: dict[str, Any],
        security_pipeline: Any = None,
    ) -> dict[str, list[str]]:
        """Register tools from multiple clients.

        Args:
            registry: Shared tool registry.
            clients: Mapping of service_name -> client instance.
            security_pipeline: Optional security pipeline.

        Returns:
            Mapping of service_name -> list of tool names.
        """
        result: dict[str, list[str]] = {}
        for service_name, client in clients.items():
            names = CloudToolFactory.register_client(
                client, service_name, registry, security_pipeline
            )
            result[service_name] = names
        return result

    @staticmethod
    def _wrap_with_security(
        method: Callable,
        method_name: str,
        pipeline: Any,
    ) -> Callable:
        """Wrap a client method with pre/post security checks."""

        def secured(*args: Any, **kwargs: Any) -> Any:
            """secured ."""
            check = pipeline.pre_check(method_name, kwargs)
            if not check.allowed:
                raise PermissionError(
                    f"Security check failed: {check.reason}"
                )
            result = method(*args, **kwargs)
            return pipeline.post_process(method_name, result)

        secured.__name__ = method_name
        secured.__doc__ = method.__doc__
        return secured
