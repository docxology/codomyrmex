# Personal AI Infrastructure — Networking Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Networking module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.networking import HTTPClient, WebSocketClient, SSHClient, get_http_client
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `HTTPClient` | Class | Httpclient |
| `WebSocketClient` | Class | Websocketclient |
| `SSHClient` | Class | Sshclient |
| `TCPClient` | Class | Tcpclient |
| `TCPServer` | Class | Tcpserver |
| `UDPClient` | Class | Udpclient |
| `PortScanner` | Class | Portscanner |
| `Response` | Class | Response |
| `get_http_client` | Function/Constant | Get http client |
| `NetworkError` | Class | Networkerror |
| `ConnectionError` | Class | Connectionerror |
| `NetworkTimeoutError` | Class | Networktimeouterror |
| `SSLError` | Class | Sslerror |
| `HTTPError` | Class | Httperror |
| `DNSResolutionError` | Class | Dnsresolutionerror |

*Plus 5 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Networking Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |
| **VERIFY** | Validation and quality checks |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
