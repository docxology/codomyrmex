# privacy

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The privacy module enforces data minimization and network anonymity. It provides a crumb cleaner that recursively strips identifying metadata (timestamps, IP addresses, device IDs, session tokens) from data structures, and a mixnet proxy that simulates anonymous multi-hop routing through overlay network nodes with randomized delays to thwart timing analysis.

## Key Exports

- **`CrumbCleaner`** -- Sanitizes dictionaries and nested structures by recursively removing blacklisted metadata keys (e.g., `ip_address`, `device_id`, `cookie_id`). Supports dynamic blacklist configuration and random noise generation to obscure activity patterns.
- **`MixnetProxy`** -- Manages anonymous payload routing through a simulated 10-node mixnet. Routes data through randomly selected mix nodes with configurable hop counts and processing delays to prevent traffic analysis.

## Directory Contents

- `__init__.py` - Module entry point; exports `CrumbCleaner` and `MixnetProxy`
- `crumbs.py` - `CrumbCleaner` class with recursive scrubbing, noise generation, and configurable blacklist management
- `mixnet.py` - `Packet` dataclass, `MixNode` relay node, and `MixnetProxy` routing manager
- `privacy.py` - Additional privacy utilities
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tool definitions
- `SPEC.md` - Module specification
- `SECURITY.md` - Security considerations
- `CHANGELOG.md` - Version history
- `USAGE_EXAMPLES.md` - Usage examples and patterns
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/privacy/](../../../docs/modules/privacy/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
