# Privacy Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `privacy` module enforces data minimization and network anonymity. It systematically removes metadata ("crumbs") from all agent communications and simulates onion routing transport.

## Key Capabilities

- **Crumb Scrubbing**: Recursive removal of timestamps, location data, device IDs, and headers (`CrumbCleaner`).
- **Mixnet Proxy**: Simulation of multi-hop encrypted routing (`MixnetProxy`).
- **Dynamic Configuration**: Runtime update of blacklisted metadata keys.

## Core Components

- `CrumbCleaner`: The primary sanitation engine.
- `MixnetProxy`: Transport layer simulation.

## Navigation

- **Full Documentation**: [docs/modules/privacy/](../../../docs/modules/privacy/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
