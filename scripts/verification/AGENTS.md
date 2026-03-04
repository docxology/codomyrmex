# System Verification -- Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Phase-based verification scripts that validate the full secure agent system including identity, wallet, defense, market, and privacy modules.

## Scripts Available

- **verify_phase1.py**: Verifies Identity and Wallet module functionality: persona creation, bio-cognitive metrics, wallet creation, Natural Ritual Recovery
- **verify_phase2.py**: Verifies Defense and Market modules: active defense triggers, exploit detection, reverse auctions, demand aggregation
- **verify_phase3.py**: Verifies Privacy module: crumb scrubbing (metadata removal), mixnet routing simulation
- **verify_secure_agent_system.py**: Master runner that executes all phase verification scripts to ensure full system integrity


## Agent Instructions

1. Run scripts from the repository root directory using `uv run python scripts/verification/<script>`
2. Ensure prerequisites are installed: `uv sync`
3. Scripts are demonstration/utility tools and do not modify production state

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md)
