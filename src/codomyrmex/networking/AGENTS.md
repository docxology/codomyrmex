# Codomyrmex Agents — networking

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `networking` module enables agents to communicate across process, host, and network boundaries. It provides the connectivity layer for distributed agent swarms and remote resource access.

## Active Components

- `http_client.py` – Orchestrates RESTful and generic HTTP/2 interactions.
- `websocket_client.py` – Manages persistent, bidirectional event streams.
- `ssh_sftp.py` – Enables remote command execution and secure file orchestration.
- `raw_sockets.py` – Low-level TCP/UDP primitives and network diagnostics (`PortScanner`).

## Operating Contracts

1. **Protocol Awareness**: Select the most efficient protocol for the task (e.g., WebSockets for streaming, HTTP for RPC).
2. **Timeout Enforcements**: All network operations must have explicit timeouts to prevent agent hangs.
3. **Security First**: Use encrypted protocols (HTTPS, WSS, SSH) by default for sensitive data.

## Core Interfaces

- `HTTPClient` / `WebSocketClient`: High-level application clients.
- `SSHClient`: Remote orchestration interface.
- `PortScanner`: Diagnostic tool for checking port availability.
- `TCPClient` / `UDPClient`: Primitive socket wrappers.

## Navigation Links

- **🏠 Project Root**: ../../../README.md
- **📦 Module README**: ./README.md
- **📜 Functional Spec**: ./SPEC.md
