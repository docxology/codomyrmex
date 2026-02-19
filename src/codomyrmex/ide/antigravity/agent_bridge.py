"""Antigravity AgentInterface Adapter.

Wraps ``AntigravityClient`` as a ``BaseAgent`` so it can participate in
``AgentOrchestrator`` workflows alongside Claude, Codex, Gemini, and other
agent providers.

The adapter routes ``AgentRequest`` instances to the appropriate Antigravity
tool based on requested capabilities and prompt analysis.

Example::

    >>> from codomyrmex.ide.antigravity.agent_bridge import AntigravityAgent
    >>> agent = AntigravityAgent()
    >>> agent.connect()
    >>> from codomyrmex.agents.core import AgentRequest
    >>> resp = agent.execute(AgentRequest(
    ...     prompt="Find all TODO comments",
    ...     context={"path": "/src"},
    ...     capabilities=["code_analysis"],
    ... ))
    >>> print(resp.content)
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from typing import Any

try:
    from codomyrmex.agents.core import (
        AgentCapabilities,
        AgentRequest,
        AgentResponse,
        BaseAgent,
    )
    from codomyrmex.agents.core.registry import ToolRegistry
except ImportError:
    BaseAgent = None
    AgentCapabilities = None
    AgentRequest = None
    AgentResponse = None
    ToolRegistry = None

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


# Keywords that map prompt intent → Antigravity tool
_INTENT_ROUTES: dict[str, str] = {
    # File reading
    "view": "view_file",
    "read": "view_file",
    "show": "view_file",
    "cat": "view_file",
    "outline": "view_file_outline",
    "structure": "view_file_outline",
    # Search
    "search": "grep_search",
    "find": "find_by_name",
    "grep": "grep_search",
    "locate": "find_by_name",
    # Directory
    "list": "list_dir",
    "ls": "list_dir",
    "directory": "list_dir",
    # Writing
    "write": "write_to_file",
    "create": "write_to_file",
    "edit": "replace_file_content",
    "replace": "replace_file_content",
    "modify": "replace_file_content",
    # Execution
    "run": "run_command",
    "execute": "run_command",
    "command": "run_command",
    "shell": "run_command",
    # Web
    "browse": "search_web",
    "fetch": "read_url_content",
    "url": "read_url_content",
}


def _route_prompt(prompt: str) -> str | None:
    """Determine the best Antigravity tool for a prompt.

    Args:
        prompt: The natural-language prompt to route.

    Returns:
        Tool name or None if no clear match.
    """
    prompt_lower = prompt.lower()
    for keyword, tool in _INTENT_ROUTES.items():
        if keyword in prompt_lower:
            return tool
    return None


def _extract_context_args(request: AgentRequest) -> dict[str, Any]:
    """Extract tool arguments from request context/metadata.

    Args:
        request: The agent request.

    Returns:
        Dictionary of keyword arguments for the tool.
    """
    args: dict[str, Any] = {}
    ctx = request.context or {}
    meta = request.metadata or {}

    # Common context keys → tool params
    if "path" in ctx:
        args["AbsolutePath"] = ctx["path"]
        args["SearchPath"] = ctx["path"]
        args["DirectoryPath"] = ctx["path"]
        args["SearchDirectory"] = ctx["path"]
    if "query" in ctx:
        args["Query"] = ctx["query"]
        args["query"] = ctx["query"]
    if "pattern" in ctx:
        args["Pattern"] = ctx["pattern"]
    if "command" in ctx:
        args["CommandLine"] = ctx["command"]
    if "cwd" in ctx:
        args["Cwd"] = ctx["cwd"]
    if "content" in ctx:
        args["CodeContent"] = ctx["content"]
    if "target_file" in ctx:
        args["TargetFile"] = ctx["target_file"]
    if "url" in ctx:
        args["Url"] = ctx["url"]

    # Merge metadata overrides
    args.update(meta)
    return args


if BaseAgent is not None:

    class AntigravityAgent(BaseAgent):
        """Wraps AntigravityClient as a full AgentInterface participant.

        This adapter enables the ``AgentOrchestrator`` to include Antigravity
        in parallel, sequential, and fallback execution strategies alongside
        other agent providers.

        Attributes:
            client: The underlying ``AntigravityClient``.
        """

        def __init__(
            self,
            client: Any | None = None,
            config: dict[str, Any] | None = None,
        ) -> None:
            """Initialize the Antigravity agent adapter.

            Args:
                client: An ``AntigravityClient`` instance (lazy-created if None).
                config: Optional configuration dict.
            """
            super().__init__(
                name="antigravity",
                capabilities=[
                    AgentCapabilities.CODE_GENERATION,
                    AgentCapabilities.CODE_EDITING,
                    AgentCapabilities.CODE_ANALYSIS,
                    AgentCapabilities.FILE_OPERATIONS,
                    AgentCapabilities.TOOL_USE,
                ],
                config=config,
            )
            self._client = client
            self._tool_registry: ToolRegistry | None = None

        @property
        def client(self) -> Any:
            """Lazy-initialize the AntigravityClient.

            Returns:
                The AntigravityClient instance.
            """
            if self._client is None:
                from codomyrmex.ide.antigravity import AntigravityClient
                self._client = AntigravityClient()
            return self._client

        def connect(self) -> None:
            """Connect the underlying client."""
            self.client.connect()

        def _execute_impl(self, request: AgentRequest) -> AgentResponse:
            """Execute a request by routing to the appropriate Antigravity tool.

            Args:
                request: The agent request to execute.

            Returns:
                Agent response with tool output.
            """
            start = time.monotonic()
            tool_name = _route_prompt(request.prompt)

            if tool_name is None:
                # Default to grep_search for analysis, view_file for viewing
                if request.capabilities and AgentCapabilities.CODE_ANALYSIS in request.capabilities:
                    tool_name = "grep_search"
                elif request.capabilities and AgentCapabilities.FILE_OPERATIONS in request.capabilities:
                    tool_name = "view_file"
                else:
                    tool_name = "grep_search"
                logger.info(f"No intent match, defaulting to {tool_name}")

            args = _extract_context_args(request)

            # Use prompt as query/pattern if not in context
            if tool_name == "grep_search" and "Query" not in args:
                args["Query"] = request.prompt
            if tool_name == "find_by_name" and "Pattern" not in args:
                args["Pattern"] = request.prompt

            logger.info(f"Routing to tool: {tool_name}")

            try:
                result = self.client.invoke_tool(tool_name, args)
                elapsed = time.monotonic() - start
                return AgentResponse(
                    content=str(result),
                    metadata={"tool": tool_name, "args": args},
                    execution_time=elapsed,
                    request_id=request.id,
                )
            except Exception as e:
                elapsed = time.monotonic() - start
                logger.error(f"Tool {tool_name} failed: {e}")
                return AgentResponse(
                    content="",
                    error=str(e),
                    metadata={"tool": tool_name, "args": args},
                    execution_time=elapsed,
                    request_id=request.id,
                )

        def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
            """Stream is not supported — yields single response.

            Args:
                request: The agent request.

            Yields:
                Single response chunk.
            """
            response = self.execute(request)
            yield response.content

        def setup(self) -> None:
            """Interactive setup — connects to the IDE."""
            self.connect()

        def test_connection(self) -> bool:
            """Test if the client is connected.

            Returns:
                True if connected.
            """
            try:
                return self.client.is_connected()
            except Exception:
                return False

        def get_tool_registry(self) -> ToolRegistry:
            """Get a ToolRegistry with all Antigravity tools.

            Returns:
                ``ToolRegistry`` with bridged tools.
            """
            if self._tool_registry is None:
                from codomyrmex.ide.antigravity.tool_provider import AntigravityToolProvider
                provider = AntigravityToolProvider(self.client)
                self._tool_registry = provider.get_tool_registry()
            return self._tool_registry

else:
    # Stub when agents.core is not available
    class AntigravityAgent:  # type: ignore[no-redef]
        """Stub for when agents.core is not installed."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError(
                "codomyrmex.agents.core is required for AntigravityAgent. "
                "Install with: pip install codomyrmex[agents]"
            )


__all__ = ["AntigravityAgent"]
