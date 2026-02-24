"""Antigravity ToolRegistry Bridge.

Bridges the 18 Antigravity IDE tools into the agents ``ToolRegistry`` so
that any ``BaseAgent`` or ``AgentOrchestrator`` can discover, schema-inspect,
and invoke them.

Example::

    >>> from codomyrmex.ide.antigravity import AntigravityClient
    >>> from codomyrmex.ide.antigravity.tool_provider import AntigravityToolProvider
    >>> client = AntigravityClient()
    >>> client.connect()
    >>> provider = AntigravityToolProvider(client)
    >>> registry = provider.get_tool_registry()
    >>> registry.list_tools()  # 18 Tool objects
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from codomyrmex.agents.core.registry import Tool, ToolRegistry
except ImportError:
    Tool = None
    ToolRegistry = None

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


# Classification of Antigravity tools by safety level
SAFE_TOOLS: frozenset[str] = frozenset({
    "view_file",
    "view_file_outline",
    "view_code_item",
    "find_by_name",
    "grep_search",
    "list_dir",
    "command_status",
    "search_web",
    "read_url_content",
})

DESTRUCTIVE_TOOLS: frozenset[str] = frozenset({
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
    "run_command",
    "send_command_input",
    "browser_subagent",
    "generate_image",
})

CONTROL_TOOLS: frozenset[str] = frozenset({
    "task_boundary",
    "notify_user",
})


# Full schema definitions for all 18 tools
_TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "task_boundary": {
        "description": "Manage task state and progress tracking",
        "parameters": {
            "type": "object",
            "properties": {
                "TaskName": {"type": "string", "description": "Name of the task boundary"},
                "Mode": {"type": "string", "enum": ["PLANNING", "EXECUTION", "VERIFICATION"]},
                "TaskSummary": {"type": "string", "description": "Summary of progress"},
                "TaskStatus": {"type": "string", "description": "Current activity"},
                "PredictedTaskSize": {"type": "integer", "description": "Estimated tool calls"},
            },
            "required": ["TaskName", "Mode", "TaskSummary", "TaskStatus", "PredictedTaskSize"],
        },
    },
    "notify_user": {
        "description": "Send a notification or question to the user",
        "parameters": {
            "type": "object",
            "properties": {
                "Message": {"type": "string", "description": "Message content"},
                "PathsToReview": {"type": "array", "items": {"type": "string"}},
                "BlockedOnUser": {"type": "boolean"},
                "ShouldAutoProceed": {"type": "boolean"},
            },
            "required": ["Message", "PathsToReview", "BlockedOnUser", "ShouldAutoProceed"],
        },
    },
    "write_to_file": {
        "description": "Create or overwrite a file with given content",
        "parameters": {
            "type": "object",
            "properties": {
                "TargetFile": {"type": "string", "description": "Absolute path to file"},
                "CodeContent": {"type": "string", "description": "Content to write"},
                "Overwrite": {"type": "boolean"},
                "EmptyFile": {"type": "boolean"},
                "IsArtifact": {"type": "boolean"},
                "Description": {"type": "string"},
                "Complexity": {"type": "integer"},
            },
            "required": ["TargetFile", "CodeContent"],
        },
    },
    "replace_file_content": {
        "description": "Replace a single contiguous block of content in a file",
        "parameters": {
            "type": "object",
            "properties": {
                "TargetFile": {"type": "string"},
                "TargetContent": {"type": "string"},
                "ReplacementContent": {"type": "string"},
                "StartLine": {"type": "integer"},
                "EndLine": {"type": "integer"},
            },
            "required": ["TargetFile", "TargetContent", "ReplacementContent", "StartLine", "EndLine"],
        },
    },
    "multi_replace_file_content": {
        "description": "Make multiple non-contiguous replacements in a file",
        "parameters": {
            "type": "object",
            "properties": {
                "TargetFile": {"type": "string"},
                "ReplacementChunks": {"type": "array", "items": {"type": "object"}},
            },
            "required": ["TargetFile", "ReplacementChunks"],
        },
    },
    "view_file": {
        "description": "View the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "AbsolutePath": {"type": "string", "description": "Absolute path to file"},
                "StartLine": {"type": "integer"},
                "EndLine": {"type": "integer"},
            },
            "required": ["AbsolutePath"],
        },
    },
    "view_file_outline": {
        "description": "View the structural outline of a file (classes, functions)",
        "parameters": {
            "type": "object",
            "properties": {
                "AbsolutePath": {"type": "string"},
                "ItemOffset": {"type": "integer"},
            },
            "required": ["AbsolutePath"],
        },
    },
    "view_code_item": {
        "description": "View specific code items (classes/functions) by node path",
        "parameters": {
            "type": "object",
            "properties": {
                "File": {"type": "string"},
                "NodePaths": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["File", "NodePaths"],
        },
    },
    "run_command": {
        "description": "Execute a terminal command",
        "parameters": {
            "type": "object",
            "properties": {
                "CommandLine": {"type": "string", "description": "Command to execute"},
                "Cwd": {"type": "string", "description": "Working directory"},
                "SafeToAutoRun": {"type": "boolean"},
                "WaitMsBeforeAsync": {"type": "integer"},
            },
            "required": ["CommandLine", "Cwd", "SafeToAutoRun", "WaitMsBeforeAsync"],
        },
    },
    "command_status": {
        "description": "Get status of a running background command",
        "parameters": {
            "type": "object",
            "properties": {
                "CommandId": {"type": "string"},
                "WaitDurationSeconds": {"type": "integer"},
                "OutputCharacterCount": {"type": "integer"},
            },
            "required": ["CommandId", "WaitDurationSeconds"],
        },
    },
    "send_command_input": {
        "description": "Send stdin input to a running command",
        "parameters": {
            "type": "object",
            "properties": {
                "CommandId": {"type": "string"},
                "Input": {"type": "string"},
                "Terminate": {"type": "boolean"},
                "WaitMs": {"type": "integer"},
                "SafeToAutoRun": {"type": "boolean"},
            },
            "required": ["CommandId", "WaitMs", "SafeToAutoRun"],
        },
    },
    "find_by_name": {
        "description": "Search for files and directories by name pattern",
        "parameters": {
            "type": "object",
            "properties": {
                "SearchDirectory": {"type": "string"},
                "Pattern": {"type": "string"},
                "Extensions": {"type": "array", "items": {"type": "string"}},
                "MaxDepth": {"type": "integer"},
                "Type": {"type": "string", "enum": ["file", "directory", "any"]},
            },
            "required": ["SearchDirectory", "Pattern"],
        },
    },
    "grep_search": {
        "description": "Search file contents with ripgrep",
        "parameters": {
            "type": "object",
            "properties": {
                "SearchPath": {"type": "string"},
                "Query": {"type": "string"},
                "MatchPerLine": {"type": "boolean"},
                "IsRegex": {"type": "boolean"},
                "CaseInsensitive": {"type": "boolean"},
                "Includes": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["SearchPath", "Query"],
        },
    },
    "list_dir": {
        "description": "List contents of a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "DirectoryPath": {"type": "string"},
            },
            "required": ["DirectoryPath"],
        },
    },
    "browser_subagent": {
        "description": "Launch a browser subagent to perform web interactions",
        "parameters": {
            "type": "object",
            "properties": {
                "TaskName": {"type": "string"},
                "Task": {"type": "string"},
                "RecordingName": {"type": "string"},
            },
            "required": ["TaskName", "Task", "RecordingName"],
        },
    },
    "generate_image": {
        "description": "Generate an image from a text prompt",
        "parameters": {
            "type": "object",
            "properties": {
                "Prompt": {"type": "string"},
                "ImageName": {"type": "string"},
                "ImagePaths": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["Prompt", "ImageName"],
        },
    },
    "search_web": {
        "description": "Perform a web search and return summarized results",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "domain": {"type": "string"},
            },
            "required": ["query"],
        },
    },
    "read_url_content": {
        "description": "Fetch and read content from a URL",
        "parameters": {
            "type": "object",
            "properties": {
                "Url": {"type": "string"},
            },
            "required": ["Url"],
        },
    },
}


class AntigravityToolProvider:
    """Bridges Antigravity IDE tools into the agents ToolRegistry.

    Converts the 18 Antigravity tool definitions into ``Tool`` instances
    that the ``ToolRegistry`` can manage, enabling any ``BaseAgent`` or
    ``AgentOrchestrator`` to discover and invoke them.

    Attributes:
        client: The AntigravityClient instance providing tool execution.
        prefix: Optional prefix for tool names (default: ``"antigravity."``).
    """

    def __init__(self, client: Any, *, prefix: str = "antigravity.") -> None:
        """Initialize the tool provider.

        Args:
            client: An ``AntigravityClient`` instance.
            prefix: Prefix for registered tool names.
        """
        self.client = client
        self.prefix = prefix
        logger.info(f"AntigravityToolProvider initialized with prefix '{prefix}'")

    def _make_tool_func(self, tool_name: str):
        """Create a closure that invokes the given tool via the client.

        Args:
            tool_name: Name of the Antigravity tool.

        Returns:
            A callable that invokes the tool.
        """
        def _invoke(**kwargs: Any) -> Any:
            """Execute  Invoke operations natively."""
            return self.client.invoke_tool(tool_name, kwargs)
        _invoke.__name__ = tool_name
        _invoke.__doc__ = _TOOL_SCHEMAS.get(tool_name, {}).get(
            "description", f"Invoke Antigravity tool: {tool_name}"
        )
        return _invoke

    def get_tool_registry(
        self,
        *,
        include_destructive: bool = True,
        include_control: bool = False,
    ) -> ToolRegistry:
        """Build a ``ToolRegistry`` populated with Antigravity tools.

        Args:
            include_destructive: Include write/execute tools (default True).
            include_control: Include task_boundary/notify_user (default False).

        Returns:
            A ``ToolRegistry`` with bridged Antigravity tools.

        Raises:
            RuntimeError: If ``ToolRegistry`` is not available.
        """
        if ToolRegistry is None:
            raise RuntimeError(
                "agents.core.registry not available; install codomyrmex[agents]"
            )

        registry = ToolRegistry()
        registered = 0

        for tool_name, schema in _TOOL_SCHEMAS.items():
            # Filter by category
            if tool_name in CONTROL_TOOLS and not include_control:
                continue
            if tool_name in DESTRUCTIVE_TOOLS and not include_destructive:
                continue

            tool = Tool(
                name=f"{self.prefix}{tool_name}",
                func=self._make_tool_func(tool_name),
                description=schema["description"],
                args_schema=schema["parameters"],
            )
            registry.register(tool)
            registered += 1

        logger.info(f"Registered {registered} Antigravity tools in ToolRegistry")
        return registry

    def get_safe_registry(self) -> ToolRegistry:
        """Build a ToolRegistry with only safe (read-only) tools.

        Returns:
            A ``ToolRegistry`` containing only non-destructive tools.
        """
        return self.get_tool_registry(
            include_destructive=False,
            include_control=False,
        )

    @staticmethod
    def classify_tool(tool_name: str) -> str:
        """Classify a tool by safety level.

        Args:
            tool_name: Tool name (without prefix).

        Returns:
            One of ``"safe"``, ``"destructive"``, or ``"control"``.
        """
        if tool_name in SAFE_TOOLS:
            return "safe"
        if tool_name in DESTRUCTIVE_TOOLS:
            return "destructive"
        if tool_name in CONTROL_TOOLS:
            return "control"
        return "unknown"

    @staticmethod
    def get_tool_schema(tool_name: str) -> dict[str, Any] | None:
        """Get the JSON schema for a tool.

        Args:
            tool_name: Tool name (without prefix).

        Returns:
            Schema dict or None if not found.
        """
        return _TOOL_SCHEMAS.get(tool_name)

    @staticmethod
    def list_all_tools() -> list[str]:
        """List all known Antigravity tool names.

        Returns:
            Sorted list of tool names.
        """
        return sorted(_TOOL_SCHEMAS.keys())


__all__ = [
    "AntigravityToolProvider",
    "SAFE_TOOLS",
    "DESTRUCTIVE_TOOLS",
    "CONTROL_TOOLS",
]
