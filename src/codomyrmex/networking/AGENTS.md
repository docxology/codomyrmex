# Agent Guidelines - Networking

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Network utilities: HTTP clients, sockets, protocols, and DNS.

## Key Classes

- **HTTPClient** — Async HTTP client with retries
- **SocketManager** — TCP/UDP socket handling
- **DNSResolver** — DNS lookups and caching
- **NetworkMonitor** — Network health checks

## Agent Instructions

1. **Use async** — Prefer async for concurrent requests
2. **Set timeouts** — Always configure timeouts
3. **Retry transients** — Retry on network errors
4. **Pool connections** — Reuse HTTP connections
5. **Cache DNS** — Cache DNS lookups

## Common Patterns

```python
from codomyrmex.networking import (
    HTTPClient, SocketManager, DNSResolver
)

# HTTP client with retry
client = HTTPClient(
    timeout=30,
    retries=3,
    backoff_factor=1.5
)

response = await client.get("https://api.example.com/data")
print(response.json())

# Socket communication
socket = SocketManager()
socket.connect("server.example.com", 8080)
socket.send(b"Hello")
data = socket.receive()

# DNS resolution
resolver = DNSResolver(cache_ttl=300)
ips = resolver.resolve("example.com")
```

## Testing Patterns

```python
# Verify HTTP client with real endpoint
client = HTTPClient()
response = await client.get("http://httpbin.org/get")
assert response.status_code == 200

# Verify DNS resolver
resolver = DNSResolver()
ips = resolver.resolve("localhost")
assert "127.0.0.1" in ips
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
