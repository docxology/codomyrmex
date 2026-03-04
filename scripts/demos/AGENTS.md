# System Demos -- Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Orchestrator for running system demonstrations across multiple modules including defense, identity, market, privacy, and wallet functionality.

## Scripts Available

- **run_demos.py**: Main orchestrator that discovers and runs registered demos from the demos registry
- **demo_defense.py**: Defense module demonstration script
- **demo_identity.py**: Identity module demonstration script
- **demo_market.py**: Market module demonstration script
- **demo_privacy.py**: Privacy module demonstration script
- **demo_wallet.py**: Wallet module demonstration script


## Agent Instructions

1. Run scripts from the repository root directory using `uv run python scripts/demos/<script>`
2. Ensure prerequisites are installed: `uv sync`
3. Scripts are demonstration/utility tools and do not modify production state

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md)
