# System Demos Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Orchestrator for running system demonstrations across multiple modules including defense, identity, market, privacy, and wallet functionality.

## Functional Requirements

- **run_demos.py**: Main orchestrator that discovers and runs registered demos from the demos registry
- **demo_defense.py**: Defense module demonstration script
- **demo_identity.py**: Identity module demonstration script
- **demo_market.py**: Market module demonstration script
- **demo_privacy.py**: Privacy module demonstration script
- **demo_wallet.py**: Wallet module demonstration script


## Execution

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
uv run python scripts/demos/run_demos.py
```

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
