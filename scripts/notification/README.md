# Notification Scripts

**Version**: v1.1.4 | **Status**: Placeholder | **Last Updated**: March 2026

## Overview

Placeholder scripts for the `notification` module, which will provide multi-channel notification delivery (email, Slack, webhooks) with template support and delivery tracking.

## Purpose

These scripts will demonstrate notification workflows once the underlying module is implemented. Currently the demo raises `NotImplementedError`.

## Contents

| File | Description |
|------|-------------|
| `notification_demo.py` | Placeholder demo (raises `NotImplementedError` -- module not yet implemented) |

## Usage

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
# Will raise NotImplementedError until module is implemented
uv run python scripts/notification/notification_demo.py
```

## Status

The `codomyrmex.notification` source module is not yet implemented. Create `src/codomyrmex/notification/` with real functionality before using this demo.

## Agent Usage

Agents should not attempt to use this module until the source implementation exists. Check `src/codomyrmex/notification/` for availability.

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
