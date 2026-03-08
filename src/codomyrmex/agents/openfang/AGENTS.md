# agents/openfang — Agent Capabilities

## Module Purpose

Wraps the openfang Agent Operating System via subprocess for use as a codomyrmex agent provider.

## Capabilities

```
CODE_GENERATION
TEXT_COMPLETION
STREAMING
MULTI_TURN
TOOL_USE
AUTONOMOUS_SCHEDULING
MULTI_CHANNEL_MESSAGING
WEBSOCKET_GATEWAY
```

## Constraints

- Requires the openfang binary on PATH (or configured via `OPENFANG_COMMAND`)
- Binary installation is external to Python — `uv sync` does not install it
- Build from source requires Rust toolchain (`cargo`) and the vendor submodule initialized
- Streaming via `OpenFangRunner.stream()` yields lines; no structured streaming protocol
- WebSocket gateway requires openfang daemon running locally

## Navigation

```
agents/openfang/
├── __init__.py        HAS_OPENFANG flag, all public exports
├── core.py            OpenFangRunner subprocess wrapper
├── config.py          OpenFangConfig env-var dataclass
├── exceptions.py      OpenFangError hierarchy (5 classes)
├── hands.py           HandsManager and Hand dataclass
├── update.py          Submodule sync + build pipeline
├── mcp_tools.py       7 @mcp_tool functions (auto-discovered)
└── vendor/openfang/   git submodule → github.com/RightNow-AI/openfang
```

## Agent Providers

`OpenFangRunner` (aliased as `OpenFangClient`) is registered in `agents/__init__.py`
and can be used wherever a CLI agent client is expected.

## MCP Auto-Discovery

The 7 tools in `mcp_tools.py` are auto-discovered via the `@mcp_tool` decorator
and surfaced through the PAI MCP bridge without manual registration.

## Zero-Mock Policy

All tests use real filesystem state and real subprocess calls.
Binary-dependent tests use `@pytest.mark.skipif(not HAS_OPENFANG, ...)`.
