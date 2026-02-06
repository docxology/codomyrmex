# Networking Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Network utilities: HTTP clients, sockets, DNS, and network monitoring.

## Key Features

- **HTTP** — Async HTTP client
- **Sockets** — TCP/UDP handling
- **DNS** — DNS resolution
- **Retry** — Connection retries

## Quick Start

```python
from codomyrmex.networking import HTTPClient, DNSResolver

client = HTTPClient(timeout=30, retries=3)
response = await client.get("https://api.example.com")

resolver = DNSResolver()
ips = resolver.resolve("example.com")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/networking/](../../../src/codomyrmex/networking/)
- **Parent**: [Modules](../README.md)
