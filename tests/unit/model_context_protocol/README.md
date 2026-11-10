# model_context_protocol

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Validation coverage, fixtures, and regression checks for Model Context Protocol.

## Directory Contents

- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `integration/` – Subdirectory
- `test_decorators.py` – File
- `test_discovery.py` – File
- `test_mcp_server.py` – File
- `test_mcp_tools.py` – File
- `test_model_context_protocol.py` – File
- `test_schemas.py` – File
- `test_server_coverage.py` – File
- `test_tools_extended.py` – File
- `test_transport.py` – File
- `unit/` – Subdirectory

## Navigation

- **Parent Directory**: [unit](../README.md)
- **Project Root**: ../../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## Delegated URL admission

`test_delegated_url_policy.py` exercises strict per-tool operator grants, actual
handler refusal before backend setup, and raw MCP dispatch without a PAI wrapper.
A fresh Python process points video REST configuration at a real loopback trap and
checks that a denied call never contacts it. Positive tests check authorization
only; they do not transcribe media, send email, or create webhooks. No external
service, credential, or patched network method is used.
