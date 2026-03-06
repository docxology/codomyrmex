# System Verification Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Phase-based verification scripts that validate the full secure agent system including identity, wallet, defense, market, and privacy modules.

## Functional Requirements

- **verify_phase1.py**: Verifies Identity and Wallet module functionality: persona creation, bio-cognitive metrics, wallet creation, Natural Ritual Recovery
- **verify_phase2.py**: Verifies Defense and Market modules: active defense triggers, exploit detection, reverse auctions, demand aggregation
- **verify_phase3.py**: Verifies Privacy module: crumb scrubbing (metadata removal), mixnet routing simulation
- **verify_secure_agent_system.py**: Master runner that executes all phase verification scripts to ensure full system integrity


## Execution

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
uv run python scripts/verification/verify_secure_agent_system.py
```

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
