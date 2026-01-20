# networking

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

The `networking` module provides high-level and low-level communication primitives for the Codomyrmex ecosystem. It supports HTTP, WebSockets, SSH/SFTP, and raw socket operations including network diagnostics.

## Key Features

- **Multi-Protocol Support**: Unified clients for HTTP, WebSockets, and SSH.
- **Network Diagnostics**: Built-in `PortScanner` for service discovery and health checks.
- **Raw Socket Primitives**: TCP/UDP clients and servers for custom protocol implementation.
- **Secure Communication**: Integrated SSH/SFTP support with key-based authentication.

## Module Structure

- `http_client.py` – Advanced HTTP/1.1 and HTTP/2 client.
- `websocket_client.py` – Real-time bidirectional communication.
- `ssh_sftp.py` – Secure shell and file transfer protocol.
- `raw_sockets.py` – TCP/UDP primitives and `PortScanner`.

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
