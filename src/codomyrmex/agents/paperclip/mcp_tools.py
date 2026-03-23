"""MCP tool definitions for the Paperclip agent module.

Exposes Paperclip CLI and API operations as MCP tools.
All tools lazy-import the underlying clients to avoid circular dependencies.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="paperclip",
    description=(
        "Execute a single heartbeat run against a Paperclip agent. "
        "Triggers the agent to wake up, check work, and act."
    ),
)
def paperclip_execute(
    prompt: str,
    agent_id: str | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    """Submit a heartbeat run to Paperclip.

    Args:
        prompt: Natural-language directive for the heartbeat context.
        agent_id: Agent ID to invoke. If None, falls back to default run.
        timeout: CLI timeout in seconds (default 120).

    Returns:
        dict with keys: status, content, error, metadata
    """
    try:
        from codomyrmex.agents.core import AgentRequest
        from codomyrmex.agents.paperclip.paperclip_client import PaperclipClient

        config: dict[str, Any] = {"paperclip_timeout": timeout}
        if agent_id:
            config["paperclip_agent_id"] = agent_id
        client = PaperclipClient(config=config)
        request = AgentRequest(prompt=prompt)
        response = client.execute(request)
        return {
            "status": "success" if response.is_success() else "error",
            "content": response.content,
            "error": response.error,
            "metadata": response.metadata,
        }
    except Exception as exc:
        return {"status": "error", "content": "", "error": str(exc), "metadata": {}}


@mcp_tool(
    category="paperclip",
    description=(
        "list all companies managed by the Paperclip instance via the REST API."
    ),
)
def paperclip_list_companies(
    base_url: str = "http://localhost:3100",
    api_key: str | None = None,
) -> dict[str, Any]:
    """list companies from the Paperclip API.

    Args:
        base_url: Paperclip server URL.
        api_key: Optional bearer token.

    Returns:
        dict with company data or error info.
    """
    try:
        from codomyrmex.agents.paperclip.paperclip_api_client import (
            PaperclipAPIClient,
        )

        client = PaperclipAPIClient(base_url=base_url, api_key=api_key)
        return {"status": "success", "data": client.list_companies()}
    except Exception as exc:
        return {"status": "error", "data": None, "error": str(exc)}


@mcp_tool(
    category="paperclip",
    description=("Create a new issue/ticket in a Paperclip company via the REST API."),
)
def paperclip_create_issue(
    company_id: str,
    title: str,
    description: str | None = None,
    base_url: str = "http://localhost:3100",
    api_key: str | None = None,
) -> dict[str, Any]:
    """Create an issue in a Paperclip company.

    Args:
        company_id: Company identifier.
        title: Issue title.
        description: Optional issue description.
        base_url: Paperclip server URL.
        api_key: Optional bearer token.

    Returns:
        dict with issue data or error info.
    """
    try:
        from codomyrmex.agents.paperclip.paperclip_api_client import (
            PaperclipAPIClient,
        )

        client = PaperclipAPIClient(base_url=base_url, api_key=api_key)
        result = client.create_issue(
            company_id=company_id,
            title=title,
            description=description,
        )
        return {"status": "success", "data": result}
    except Exception as exc:
        return {"status": "error", "data": None, "error": str(exc)}


@mcp_tool(
    category="paperclip",
    description=(
        "Trigger a heartbeat run for a specific agent via the Paperclip REST API."
    ),
)
def paperclip_trigger_heartbeat(
    agent_id: str,
    base_url: str = "http://localhost:3100",
    api_key: str | None = None,
) -> dict[str, Any]:
    """Trigger a heartbeat via the Paperclip API.

    Args:
        agent_id: Agent identifier.
        base_url: Paperclip server URL.
        api_key: Optional bearer token.

    Returns:
        dict with heartbeat result or error info.
    """
    try:
        from codomyrmex.agents.paperclip.paperclip_api_client import (
            PaperclipAPIClient,
        )

        client = PaperclipAPIClient(base_url=base_url, api_key=api_key)
        result = client.trigger_heartbeat(agent_id=agent_id)
        return {"status": "success", "data": result}
    except Exception as exc:
        return {"status": "error", "data": None, "error": str(exc)}


@mcp_tool(
    category="paperclip",
    description=("Run Paperclip doctor diagnostics to check CLI and server health."),
)
def paperclip_doctor(
    repair: bool = False,
) -> dict[str, Any]:
    """Run Paperclip doctor health check.

    Args:
        repair: Attempt automatic repair of issues.

    Returns:
        dict with diagnostic results.
    """
    try:
        from codomyrmex.agents.paperclip.paperclip_client import PaperclipClient

        client = PaperclipClient()
        result = client.run_doctor(repair=repair)
        return {
            "status": "success" if result.get("success") else "error",
            "data": result,
        }
    except Exception as exc:
        return {"status": "error", "data": None, "error": str(exc)}
