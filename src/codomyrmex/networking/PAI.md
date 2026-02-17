# Personal AI Infrastructure — Networking Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Networking module provides a robust, fault-tolerant communication layer for Codomyrmex agents. It wraps standard libraries (`requests`, `websockets`, `paramiko`) with enterprise-grade features like automatic retries, connection backoff, and consistent error handling. This is a **Core Layer** foundation module used by PAI agents to interact with the external world.

## PAI Capabilities

### HTTP Client (Robust Requests)

Wrapper around `requests` with built-in retry logic for 429/5xx errors and timeout management.

```python
from codomyrmex.networking import get_http_client, NetworkingError

client = get_http_client()

try:
    # Automatic retries for transient failures
    response = client.get("https://api.example.com/data", timeout=5)
    data = response.json()
except NetworkingError as e:
    print(f"Network failure: {e}")
```

### WebSocket Client (Persistent Connections)

Async client with automatic reconnection and event-driven message handling.

```python
import asyncio
from codomyrmex.networking import WebSocketClient

async def monitor_stream():
    client = WebSocketClient(
        "wss://stream.example.com/events",
        reconnect_interval=1.0,
        max_reconnect_delay=30.0
    )

    # Register handler
    @client.on
    async def handle_event(data):
        print(f"Received: {data}")

    # Start connection loop
    await client.connect()
```

### SSH & remote Execution

Secure shell access for remote server management.

```python
from codomyrmex.networking import SSHClient

with SSHClient(hostname="remote.host", username="admin") as ssh:
    # Execute commands
    exit_code, stdout, stderr = ssh.execute_command("ls -la /var/log")
    
    # SFTP operations
    sftp = ssh.get_sftp()
    sftp.put("local_file.txt", "remote_file.txt")
```

### Low-Level Socket Operations

Utilities for port scanning and raw TCP/UDP communication.

```python
from codomyrmex.networking import PortScanner, TCPClient

# Check service availability
if PortScanner.is_port_open("db.internal", 5432):
    print("Database is reachable")

# Raw TCP communication
client = TCPClient("localhost", 8080)
client.connect()
client.send(b"PING")
response = client.receive()
```

## Key Exports

| Category | Exports | Purpose |
|----------|---------|---------|
| **HTTP** | `HTTPClient`, `Response`, `get_http_client` | REST API interactions with resilience |
| **Real-time** | `WebSocketClient` | Persistent, event-driven streaming |
| **Remote Access** | `SSHClient` | Secure shell command execution & file transfer |
| **Sockets** | `TCPClient`, `TCPServer`, `UDPClient`, `PortScanner` | Raw network I/O and discovery |
| **Exceptions** | `NetworkError`, `ConnectionError`, `NetworkTimeoutError` | Unified error hierarchy |

## PAI Algorithm Phase Mapping

| Phase | Networking Contribution |
|-------|-------------------------|
| **OBSERVE** | `PortScanner`, `HTTPClient.get` — Discover services and fetch state |
| **CONNECT** | `WebSocketClient.connect`, `SSHClient.connect` — Establish persistent links |
| **EXECUTE** | `HTTPClient.post`, `SSHClient.execute_command` — Trigger remote actions |
| **VERIFY** | `Response.status_code`, `PortScanner.is_port_open` — Validate operation success |

## Architecture Role

**Core Layer** — Foundation for all external communication.

- **Upstream Dependencies**: `exceptions`, `logging_monitoring`
- **Downstream Consumers**: `agents`, `cloud`, `scrape`, `api`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
