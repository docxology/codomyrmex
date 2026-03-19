"""Bidirectional MCP validation: same JSON-RPC / newline stdio flow Cursor uses.

Exercises the full PAI-assembled server (static + discovered tools) over a real
subprocess with stdin/stdout pipes — request out, response back — plus an
in-process protocol sequence for fast CI signal when subprocess is skipped.

Zero mocks: temp workspace on disk, real ``uv run`` child, real handlers.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path

import pytest

# Repo root: .../src/codomyrmex/tests/integration/pai/this_file.py
_REPO_ROOT = Path(__file__).resolve().parents[5]
_STDIO_RUNNER = _REPO_ROOT / "scripts" / "model_context_protocol" / "run_pai_mcp_stdio.py"


def _readline_timeout(proc: subprocess.Popen[str], timeout: float) -> str:
    """Read one line from *proc.stdout* or fail if *timeout* seconds elapse."""
    out: list[str] = []

    def _read() -> None:
        assert proc.stdout is not None
        line = proc.stdout.readline()
        out.append(line)

    t = threading.Thread(target=_read, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        proc.kill()
        proc.wait(timeout=5)
        pytest.fail(f"No stdout line within {timeout}s (server hung or crashed)")
    return out[0]


def _read_jsonrpc_response(proc: subprocess.Popen[str], total_timeout: float) -> dict:
    """Read lines until a JSON-RPC object appears (logs may precede MCP on stdout)."""
    deadline = time.monotonic() + total_timeout
    while time.monotonic() < deadline:
        remain = max(5.0, deadline - time.monotonic())
        line = _readline_timeout(proc, min(30.0, remain)).strip()
        if not line.startswith("{"):
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    proc.kill()
    proc.wait(timeout=5)
    pytest.fail(f"No JSON-RPC object on stdout within {total_timeout}s")


def _send(proc: subprocess.Popen[str], obj: dict) -> None:
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(obj) + "\n")
    proc.stdin.flush()


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(shutil.which("uv") is None, reason="uv not on PATH")
@pytest.mark.skipif(not _STDIO_RUNNER.is_file(), reason="run_pai_mcp_stdio.py missing")
def test_pai_mcp_stdio_subprocess_bidirectional_roundtrip(tmp_path: Path) -> None:
    """Cursor-style newline-delimited JSON-RPC over stdio (full PAI server)."""
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "probe.py").write_text("# probe\n", encoding="utf-8")

    proc = subprocess.Popen(
        [
            "uv",
            "run",
            "python",
            str(_STDIO_RUNNER.relative_to(_REPO_ROOT)),
        ],
        cwd=str(_REPO_ROOT),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        env={
            **os.environ,
            "CODOMYRMEX_CURSOR_WORKSPACE": str(workspace),
        },
    )
    try:
        # 1) initialize → result
        _send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {"name": "pytest-cursor-mcp", "version": "1.0"},
                },
            },
        )
        r1 = _read_jsonrpc_response(proc, 180.0)
        assert r1.get("jsonrpc") == "2.0" and r1.get("id") == 1, r1
        assert "result" in r1, r1
        assert r1["result"].get("protocolVersion") == "2025-06-18"
        caps = r1["result"].get("capabilities", {})
        assert "tools" in caps and "resources" in caps and "prompts" in caps

        # 2) client initialized (notification — no response body)
        _send(
            proc,
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            },
        )

        # 3) tools/list
        _send(
            proc,
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        r2 = _read_jsonrpc_response(proc, 60.0)
        assert r2.get("id") == 2, r2
        tools = r2["result"]["tools"]
        names = {t["name"] for t in tools}
        assert "codomyrmex.ide_cursor_workspace_info" in names
        assert "codomyrmex.ide_cursor_get_active_file" in names

        # 4) tools/call (Cursor ↔ codomyrmex ide bridge)
        _send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "codomyrmex.ide_cursor_workspace_info",
                    "arguments": {"workspace_path": str(workspace)},
                },
            },
        )
        r3 = _read_jsonrpc_response(proc, 60.0)
        assert r3.get("id") == 3 and "result" in r3, r3
        content = r3["result"]["content"]
        assert content and content[0].get("type") == "text"
        payload = json.loads(content[0]["text"])
        inner = payload.get("result", payload)
        assert inner.get("status") == "success"
        assert inner.get("backend") == "cursor"
        assert inner.get("workspace") == str(workspace.resolve())

        # 5) resources/list + resources/read (server → client content)
        _send(
            proc,
            {"jsonrpc": "2.0", "id": 4, "method": "resources/list", "params": {}},
        )
        r4 = _read_jsonrpc_response(proc, 60.0)
        assert r4.get("id") == 4, r4
        uris = {x["uri"] for x in r4["result"]["resources"]}
        assert "codomyrmex://status" in uris

        _send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "resources/read",
                "params": {"uri": "codomyrmex://status"},
            },
        )
        r5 = _read_jsonrpc_response(proc, 60.0)
        assert r5.get("id") == 5, r5
        text = r5["result"]["contents"][0]["text"]
        status_blob = json.loads(text)
        assert isinstance(status_blob, dict)

        # 6) prompts/list + prompts/get
        _send(
            proc,
            {"jsonrpc": "2.0", "id": 6, "method": "prompts/list", "params": {}},
        )
        r6 = _read_jsonrpc_response(proc, 60.0)
        assert r6.get("id") == 6, r6
        plist = r6["result"]["prompts"]
        assert plist
        pname = next(
            (p["name"] for p in plist if "analyze_module" in p["name"]),
            plist[0]["name"],
        )
        pargs = (
            {"module_name": "logging_monitoring"} if "analyze_module" in pname else {}
        )

        _send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "prompts/get",
                "params": {"name": pname, "arguments": pargs},
            },
        )
        r7 = _read_jsonrpc_response(proc, 60.0)
        assert r7.get("id") == 7 and "result" in r7, r7
        assert "messages" in r7["result"]
    finally:
        proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=30)


@pytest.mark.integration
def test_pai_mcp_inprocess_jsonrpc_bidirectional(tmp_path: Path) -> None:
    """Same RPC sequence in-process (no subprocess). Still loads full tool registry."""
    import asyncio

    from codomyrmex.agents.pai.mcp.server import create_codomyrmex_mcp_server

    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "probe.py").write_text("x", encoding="utf-8")

    server = create_codomyrmex_mcp_server(transport="stdio")
    assert server.tool_count > 100

    async def _run() -> None:
        r1 = await server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "clientInfo": {"name": "pytest", "version": "1"},
                },
            }
        )
        assert r1 and "result" in r1

        await server.handle_request(
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            }
        )

        r2 = await server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }
        )
        names = {t["name"] for t in r2["result"]["tools"]}
        assert "codomyrmex.ide_cursor_workspace_info" in names

        r3 = await server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "codomyrmex.ide_cursor_workspace_info",
                    "arguments": {"workspace_path": str(workspace)},
                },
            }
        )
        assert r3 and "result" in r3
        payload = json.loads(r3["result"]["content"][0]["text"])
        inner = payload.get("result", payload)
        assert inner["status"] == "success"
        assert inner["backend"] == "cursor"

    asyncio.run(_run())
