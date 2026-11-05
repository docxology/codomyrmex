"""Real default refusals for URL delegation; positive grants never call backends."""

from __future__ import annotations

import importlib
import json
import os
import queue
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from codomyrmex.model_context_protocol.delegated_url_policy import (
    DELEGATED_URL_TOOLS,
    POLICY_ENV,
    DelegatedURLPolicyError,
    require_delegated_url_tool,
)
from codomyrmex.model_context_protocol.transport.server import (
    MCPServer,
    MCPServerConfig,
)

VIDEO_TOOL = "codomyrmex.video_transcribe_url"
WEBHOOK_TOOL = "codomyrmex.agentmail_create_webhook"


@pytest.mark.parametrize("tool_name", sorted(DELEGATED_URL_TOOLS))
@pytest.mark.parametrize("configured", [None, "", "   "])
def test_missing_or_empty_operator_configuration_denies(
    monkeypatch: pytest.MonkeyPatch, tool_name: str, configured: str | None
) -> None:
    # Given no explicit operator grant.
    if configured is None:
        monkeypatch.delenv(POLICY_ENV, raising=False)
    else:
        monkeypatch.setenv(POLICY_ENV, configured)
    # When authorizing either tool; then require the disabled code.
    with pytest.raises(DelegatedURLPolicyError) as failure:
        require_delegated_url_tool(tool_name)
    assert failure.value.code == "DELEGATED_URL_DISABLED"


@pytest.mark.parametrize("tool_name", sorted(DELEGATED_URL_TOOLS))
@pytest.mark.parametrize(
    "configured",
    [
        "*",
        "video_transcribe_url",
        "codomyrmex.VIDEO_TRANSCRIBE_URL",
        "codomyrmex.unknown_tool",
        VIDEO_TOOL + ",*",
        VIDEO_TOOL + ",",
        "," + VIDEO_TOOL,
        VIDEO_TOOL + "," + VIDEO_TOOL,
        VIDEO_TOOL + ";" + WEBHOOK_TOOL,
        "x" * 1025,
        " " * 1025,
    ],
)
def test_malformed_operator_configuration_fails_closed(
    monkeypatch: pytest.MonkeyPatch, tool_name: str, configured: str
) -> None:
    # Given a malformed or unknown grant, even if one valid name is present.
    monkeypatch.setenv(POLICY_ENV, configured)
    # When authorizing either tool; then invalidate the complete configuration.
    with pytest.raises(DelegatedURLPolicyError) as failure:
        require_delegated_url_tool(tool_name)
    assert failure.value.code == "DELEGATED_URL_POLICY_INVALID"


@pytest.mark.parametrize("tool_name", sorted(DELEGATED_URL_TOOLS))
def test_exact_operator_grant_is_accepted_without_backend_execution(
    monkeypatch: pytest.MonkeyPatch, tool_name: str
) -> None:
    # Given an explicit grant for one known tool.
    monkeypatch.setenv(POLICY_ENV, tool_name)
    # When checking authorization only; then admit the named tool.
    require_delegated_url_tool(tool_name)


@pytest.mark.parametrize("tool_name", sorted(DELEGATED_URL_TOOLS))
def test_explicit_grants_can_enable_both_tools_with_whitespace(
    monkeypatch: pytest.MonkeyPatch, tool_name: str
) -> None:
    # Given both exact names and insignificant surrounding whitespace.
    monkeypatch.setenv(POLICY_ENV, f" {VIDEO_TOOL} , {WEBHOOK_TOOL} ")
    # When checking authorization only; then admit each named tool.
    require_delegated_url_tool(tool_name)


@pytest.mark.parametrize("tool_name", sorted(DELEGATED_URL_TOOLS))
def test_grant_for_one_tool_does_not_enable_the_other(
    monkeypatch: pytest.MonkeyPatch, tool_name: str
) -> None:
    # Given a grant only for the other known tool.
    monkeypatch.setenv(POLICY_ENV, ",".join(DELEGATED_URL_TOOLS - {tool_name}))
    # When checking this tool; then retain default denial.
    with pytest.raises(DelegatedURLPolicyError) as failure:
        require_delegated_url_tool(tool_name)
    assert failure.value.code == "DELEGATED_URL_DISABLED"


def test_unknown_tool_cannot_use_operator_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given grants for every supported tool, with an unsupported caller.
    monkeypatch.setenv(POLICY_ENV, ",".join(sorted(DELEGATED_URL_TOOLS)))
    # When authorizing the unsupported caller; then reject it explicitly.
    with pytest.raises(DelegatedURLPolicyError) as failure:
        require_delegated_url_tool("codomyrmex.arbitrary_tool")
    assert failure.value.code == "DELEGATED_URL_POLICY_INVALID"


def test_revoking_an_environment_grant_takes_effect_on_the_next_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given a previously accepted grant.
    monkeypatch.setenv(POLICY_ENV, VIDEO_TOOL)
    require_delegated_url_tool(VIDEO_TOOL)
    monkeypatch.delenv(POLICY_ENV)
    # When authorizing again; then do not reuse a cached grant.
    with pytest.raises(DelegatedURLPolicyError) as failure:
        require_delegated_url_tool(VIDEO_TOOL)
    assert failure.value.code == "DELEGATED_URL_DISABLED"


@pytest.mark.parametrize("mode", ["auto", "cli", "rest"])
def test_video_tool_refuses_before_backend_setup(
    monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    # Given no grant and any execution backend.
    from codomyrmex.video.mcp_tools import video_transcribe_url

    monkeypatch.delenv(POLICY_ENV, raising=False)
    # When invoking the actual tool; then return policy denial, not a backend error.
    result = video_transcribe_url("http://169.254.169.254/latest", mode=mode)
    assert result["status"] == "error"
    assert result["error_code"] == "DELEGATED_URL_DISABLED"


def test_webhook_tool_refuses_before_provider_credentials_or_sdk_setup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given no grant or API credentials; no webhook operation is authorized.
    from codomyrmex.email.mcp_tools import agentmail_create_webhook

    monkeypatch.delenv(POLICY_ENV, raising=False)
    monkeypatch.delenv("AGENTMAIL_API_KEY", raising=False)
    # When invoking the actual tool; then denial precedes provider auth/setup.
    result = agentmail_create_webhook("http://127.0.0.1/callback", ["message.received"])
    assert result["status"] == "error"
    assert result["error_code"] == "DELEGATED_URL_DISABLED"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("configured", "policy_code"),
    [("", "DELEGATED_URL_DISABLED"), ("*", "DELEGATED_URL_POLICY_INVALID")],
)
@pytest.mark.parametrize(
    ("module_name", "callable_name", "arguments"),
    [
        (
            "codomyrmex.video.mcp_tools",
            "video_transcribe_url",
            {"url": "http://127.0.0.1/source", "mode": "rest"},
        ),
        (
            "codomyrmex.email.mcp_tools",
            "agentmail_create_webhook",
            {"url": "http://127.0.0.1/callback", "event_types": ["message.received"]},
        ),
    ],
)
async def test_raw_mcp_dispatch_cannot_bypass_default_denial(
    monkeypatch: pytest.MonkeyPatch,
    module_name: str,
    callable_name: str,
    arguments: dict[str, str | list[str]],
    configured: str,
    policy_code: str,
) -> None:
    # Given raw registration without the optional PAI trust-gateway wrapper.
    monkeypatch.setenv(POLICY_ENV, configured)
    monkeypatch.delenv("AGENTMAIL_API_KEY", raising=False)
    handler = getattr(importlib.import_module(module_name), callable_name)
    metadata = handler._mcp_tool_meta
    server = MCPServer(config=MCPServerConfig(default_tool_timeout=0, warm_up=False))
    server.register_tool(
        metadata["name"],
        {"name": metadata["name"], "inputSchema": metadata["schema"]},
        handler,
    )
    # When dispatching through the real server; then the tool's own gate applies.
    envelope = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": metadata["name"], "arguments": arguments},
        }
    )
    assert envelope is not None
    response = envelope["result"]
    result = json.loads(response["content"][0]["text"])
    assert response["isError"] is True
    assert result["code"] == "ACCESS_DENIED"
    assert result["module"] == policy_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "error_code"),
    [
        ("codomyrmex.unrelated_failure", "DELEGATED_URL_DISABLED"),
        (VIDEO_TOOL, "UNREVIEWED_POLICY_CODE"),
        (VIDEO_TOOL, ["DELEGATED_URL_DISABLED"]),
    ],
)
async def test_other_logical_failures_keep_existing_wire_classification(
    tool_name: str, error_code: str | list[str]
) -> None:
    # Given a real registered handler with an unrelated or malformed failure.
    def fail() -> dict[str, str | list[str]]:
        return {
            "status": "error",
            "message": "Controlled logical failure",
            "error_code": error_code,
            "opaque_detail": "not-for-wire",
        }

    server = MCPServer(config=MCPServerConfig(default_tool_timeout=0, warm_up=False))
    server.register_tool(tool_name, {"inputSchema": {"type": "object"}}, fail)
    # When dispatching; then retain generic classification without leaking details.
    envelope = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": {}},
        }
    )
    assert envelope is not None
    response = envelope["result"]
    result = json.loads(response["content"][0]["text"])
    assert response["isError"] is True
    assert result["code"] == "EXECUTION_ERROR"
    assert result["module"] == "ToolResultError"
    assert "opaque_detail" not in result
    assert "error_code" not in result


def test_disabled_video_rest_tool_does_not_contact_configured_backend() -> None:
    # Given a real local REST trap and a fresh process with that backend configured.
    received: queue.Queue[str] = queue.Queue()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            received.put(self.path)
            payload = b'{"status":"completed","transcript":"unexpected"}'
            self.send_response(200)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: str) -> None:
            return

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        environment = dict(os.environ)
        environment[POLICY_ENV] = ""
        environment["VIDEO_TRANSCRIPTION_URL"] = (
            f"http://127.0.0.1:{server.server_port}/transcribe"
        )
        environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[3] / "src")
        script = (
            "import json; from codomyrmex.video.mcp_tools import video_transcribe_url; "
            "print(json.dumps(video_transcribe_url("
            "'http://169.254.169.254/latest', mode='rest')))"
        )
        try:
            # When the real entrypoint is invoked; then no backend receives a call.
            completed = subprocess.run(
                [sys.executable, "-c", script],
                env=environment,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=20,
                check=True,
            )
            result = json.loads(completed.stdout.splitlines()[-1])
            assert result["error_code"] == "DELEGATED_URL_DISABLED"
            assert received.empty()
        finally:
            server.shutdown()
            thread.join(timeout=2)
