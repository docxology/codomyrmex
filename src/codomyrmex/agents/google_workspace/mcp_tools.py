"""MCP tool definitions for the agents/google_workspace module.

Exposes Google Workspace CLI (gws) operations as MCP tools for agent consumption.
All tools use subprocess execution via GoogleWorkspaceRunner.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

if TYPE_CHECKING:
    from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner


def _get_runner(account: str = "", timeout: int = 60) -> GoogleWorkspaceRunner:  # type: ignore[name-defined]
    """Lazy import of GoogleWorkspaceRunner."""
    from codomyrmex.agents.google_workspace.core import GoogleWorkspaceRunner

    return GoogleWorkspaceRunner(account=account, timeout=timeout)


def _get_version() -> str:
    """Lazy import of get_gws_version."""
    from codomyrmex.agents.google_workspace.core import get_gws_version

    return get_gws_version()


def _get_config():
    """Lazy import of get_config."""
    from codomyrmex.agents.google_workspace.config import get_config

    return get_config


@mcp_tool(
    category="google_workspace",
    description="Check if the gws CLI is installed and return version + auth status.",
)
def gws_check() -> dict[str, Any]:
    """Check gws installation status and current authentication configuration.

    Returns:
        dict with keys: status, installed, version, has_auth, account, install_hint
    """
    try:
        import shutil

        installed = shutil.which("gws") is not None
        version = _get_version() if installed else ""
        cfg_fn = _get_config()
        cfg = cfg_fn()
        result: dict[str, Any] = {
            "status": "success",
            "installed": installed,
            "version": version,
            "has_auth": cfg.has_auth,
            "account": cfg.account,
        }
        if not installed:
            result["install_hint"] = "npm install -g @googleworkspace/cli"
        return result
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="google_workspace",
    description=(
        "Run any gws CLI command by specifying service, resource, and method. "
        "Supports all 40+ Google Workspace services."
    ),
)
def gws_run(
    service: str,
    resource: str,
    method: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    page_all: bool = False,
    account: str = "",
    timeout: int = 60,
) -> dict[str, Any]:
    """Run a gws CLI command against any Google Workspace service.

    Args:
        service: Google service name (e.g., 'drive', 'gmail', 'calendar').
        resource: Resource name within the service (e.g., 'files', 'messages').
        method: Method to call (e.g., 'list', 'get', 'create').
        params: Query parameters as dict (passed as --params JSON).
        body: Request body as dict (passed as --json JSON).
        page_all: If True, fetch all pages automatically (--page-all flag).
        account: Override account (empty uses GOOGLE_WORKSPACE_CLI_ACCOUNT env var).
        timeout: Subprocess timeout in seconds.

    Returns:
        dict with keys: status, output, stderr, returncode
    """
    try:
        runner = _get_runner(account=account, timeout=timeout)
        result = runner.run(
            service,
            resource,
            method,
            params=params,
            body=body,
            page_all=page_all,
        )
        parsed = runner._parse_output(result["stdout"])
        return {
            "status": "success",
            "output": parsed,
            "stderr": result["stderr"],
            "returncode": result["returncode"],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="google_workspace",
    description="Fetch the JSON schema for a gws tool path (e.g., 'drive.files.list').",
)
def gws_schema(tool_path: str) -> dict[str, Any]:
    """Fetch the JSON schema for a specific gws tool.

    Args:
        tool_path: Dot-separated path to the tool (e.g., 'drive.files.list').

    Returns:
        dict with keys: status, schema, tool_path
    """
    try:
        runner = _get_runner()
        result = runner.schema(tool_path)
        schema = runner._parse_output(result["stdout"])
        return {
            "status": "success",
            "schema": schema,
            "tool_path": tool_path,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="google_workspace",
    description="List Google Drive files matching an optional query.",
)
def gws_drive_list_files(
    query: str = "",
    page_size: int = 20,
    fields: str = "files(id,name,mimeType,modifiedTime,size)",
    account: str = "",
    timeout: int = 60,
) -> dict[str, Any]:
    """List files in Google Drive.

    Args:
        query: Drive search query (e.g., "name contains 'report'").
        page_size: Maximum number of files to return.
        fields: Comma-separated fields to include in the response.
        account: Account override (empty uses env var).
        timeout: Subprocess timeout in seconds.

    Returns:
        dict with keys: status, files, count
    """
    try:
        runner = _get_runner(account=account, timeout=timeout)
        params: dict[str, Any] = {"pageSize": page_size, "fields": fields}
        if query:
            params["q"] = query
        result = runner.run("drive", "files", "list", params=params)
        parsed = runner._parse_output(result["stdout"])
        files = parsed.get("files", []) if isinstance(parsed, dict) else []
        return {"status": "success", "files": files, "count": len(files)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="google_workspace",
    description="List Gmail messages matching an optional query.",
)
def gws_gmail_list_messages(
    query: str = "",
    max_results: int = 20,
    account: str = "",
    timeout: int = 60,
) -> dict[str, Any]:
    """List Gmail messages.

    Args:
        query: Gmail search query (e.g., "from:boss@company.com is:unread").
        max_results: Maximum number of messages to return.
        account: Account override (empty uses env var).
        timeout: Subprocess timeout in seconds.

    Returns:
        dict with keys: status, messages, count
    """
    try:
        runner = _get_runner(account=account, timeout=timeout)
        params: dict[str, Any] = {"maxResults": max_results}
        if query:
            params["q"] = query
        result = runner.run("gmail", "users", "messages", "list", params=params)
        parsed = runner._parse_output(result["stdout"])
        messages = parsed.get("messages", []) if isinstance(parsed, dict) else []
        return {"status": "success", "messages": messages, "count": len(messages)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="google_workspace",
    description="List Google Calendar events in a date range.",
)
def gws_calendar_list_events(
    calendar_id: str = "primary",
    time_min: str = "",
    time_max: str = "",
    max_results: int = 20,
    account: str = "",
    timeout: int = 60,
) -> dict[str, Any]:
    """List Google Calendar events.

    Args:
        calendar_id: Calendar ID (default: 'primary').
        time_min: RFC3339 lower bound for event start time.
        time_max: RFC3339 upper bound for event start time.
        max_results: Maximum number of events to return.
        account: Account override (empty uses env var).
        timeout: Subprocess timeout in seconds.

    Returns:
        dict with keys: status, events, count
    """
    try:
        runner = _get_runner(account=account, timeout=timeout)
        params: dict[str, Any] = {
            "calendarId": calendar_id,
            "maxResults": max_results,
        }
        if time_min:
            params["timeMin"] = time_min
        if time_max:
            params["timeMax"] = time_max
        result = runner.run("calendar", "events", "list", params=params)
        parsed = runner._parse_output(result["stdout"])
        events = parsed.get("items", []) if isinstance(parsed, dict) else []
        return {"status": "success", "events": events, "count": len(events)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="google_workspace",
    description="Get values from a Google Sheets range.",
)
def gws_sheets_get_values(
    spreadsheet_id: str,
    range_: str,
    account: str = "",
    timeout: int = 60,
) -> dict[str, Any]:
    """Read values from a Google Sheets spreadsheet range.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_: A1 notation range (e.g., 'Sheet1!A1:D10').
        account: Account override (empty uses env var).
        timeout: Subprocess timeout in seconds.

    Returns:
        dict with keys: status, values, range
    """
    try:
        runner = _get_runner(account=account, timeout=timeout)
        params: dict[str, Any] = {
            "spreadsheetId": spreadsheet_id,
            "range": range_,
        }
        result = runner.run("sheets", "spreadsheets", "values", "get", params=params)
        parsed = runner._parse_output(result["stdout"])
        values = parsed.get("values", []) if isinstance(parsed, dict) else []
        rng = parsed.get("range", range_) if isinstance(parsed, dict) else range_
        return {"status": "success", "values": values, "range": rng}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="google_workspace",
    description="List tasks from a Google Tasks tasklist.",
)
def gws_tasks_list(
    tasklist_id: str = "@default",
    show_completed: bool = False,
    account: str = "",
    timeout: int = 60,
) -> dict[str, Any]:
    """List tasks from Google Tasks.

    Args:
        tasklist_id: ID of the tasklist (default: '@default').
        show_completed: If True, include completed tasks.
        account: Account override (empty uses env var).
        timeout: Subprocess timeout in seconds.

    Returns:
        dict with keys: status, tasks, count
    """
    try:
        runner = _get_runner(account=account, timeout=timeout)
        params: dict[str, Any] = {
            "tasklist": tasklist_id,
            "showCompleted": show_completed,
        }
        result = runner.run("tasks", "tasks", "list", params=params)
        parsed = runner._parse_output(result["stdout"])
        tasks = parsed.get("items", []) if isinstance(parsed, dict) else []
        return {"status": "success", "tasks": tasks, "count": len(tasks)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="google_workspace",
    description=(
        "Return the gws MCP server start command for the specified services. "
        "Does NOT spawn a process — returns the command string for manual use."
    ),
)
def gws_mcp_start(
    services: list[str] | None = None,
    account: str = "",
) -> dict[str, Any]:
    """Return the gws MCP server start command (does NOT spawn a process).

    Args:
        services: List of service names to enable (empty = all services).
        account: Account to use for the MCP server session.

    Returns:
        dict with keys: status, command, message
    """
    try:
        import shutil

        gws_path = shutil.which("gws")
        if not gws_path:
            return {
                "status": "error",
                "message": "gws not installed. Run: npm install -g @googleworkspace/cli",
            }
        cmd_parts = [gws_path, "mcp"]
        if services:
            cmd_parts.extend(["--services", ",".join(services)])
        if account:
            cmd_parts.extend(["--account", account])
        return {
            "status": "success",
            "command": " ".join(cmd_parts),
            "message": "MCP server command ready. Run manually or add to MCP config.",
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="google_workspace",
    description="Return full gws CLI configuration and authentication status.",
)
def gws_config() -> dict[str, Any]:
    """Return current gws CLI configuration from environment.

    Returns:
        dict with keys: status, installed, version, has_token, has_credentials,
        has_auth, account, timeout, page_all
    """
    try:
        import shutil

        cfg_fn = _get_config()
        cfg = cfg_fn()
        installed = shutil.which("gws") is not None
        version = _get_version() if installed else ""
        return {
            "status": "success",
            "installed": installed,
            "version": version,
            "has_token": cfg.has_token,
            "has_credentials": cfg.has_credentials,
            "has_auth": cfg.has_auth,
            "account": cfg.account,
            "timeout": cfg.timeout,
            "page_all": cfg.page_all,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
