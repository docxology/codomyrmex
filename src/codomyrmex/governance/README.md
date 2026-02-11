# Governance Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Legal and policy framework for decentralized agent operations. Handles contract generation, policy-as-code enforcement, and dispute resolution.

## Installation

```bash
uv pip install codomyrmex
```

## Key Exports

### Legal

- **`Contract`** — Smart and legal contract wrapper
- **`Policy`** — Executable governance rule
- **`Arbitrator`** — Dispute resolution engine

### Submodules

- `contracts/` — Agreements and terms
- `policy/` — Rule enforcement
- `dispute_resolution/` — Arbitration logic

## Quick Start

```python
from codomyrmex.governance import Contract, Policy

policy = Policy(rule="No spending > $500 without approval")
policy.enforce(transaction)
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [Parent](../README.md)
