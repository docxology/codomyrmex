# identity

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The identity module provides multi-persona management and bio-cognitive verification. It enables agents to maintain distinct, verifiable identities with graduated trust levels (unverified, anonymous verified, verified anonymous with reputation, and full KYC) while supporting behavioral biometric authentication through keystroke dynamics and decision latency analysis.

## Key Exports

- **`Persona`** -- Dataclass representing a distinct identity persona with an ID, name, verification level, timestamps, key-value attributes, and siloed interaction crumbs (tracking data). Supports `add_attribute()` and `add_crumb()` methods.
- **`VerificationLevel`** -- Enum defining four trust tiers: `UNVERIFIED`, `ANON` (anonymous verified via bio-cognitive metrics), `VERIFIED_ANON` (anonymous with persistent reputation), and `KYC` (full legal identity link).
- **`IdentityManager`** -- Orchestrates multiple personas with lifecycle operations: `create_persona()`, `get_persona()`, `set_active_persona()`, `list_personas()`, `revoke_persona()`, and `export_persona()` for portable identity claims.
- **`BioCognitiveVerifier`** -- Statistical verification engine that authenticates users by comparing current behavioral metrics (e.g., keystroke flight time, decision latency) against stored baselines using Z-score analysis with a 2.5-sigma threshold. Maintains a rolling window of 100 samples per metric.

## Directory Contents

- `__init__.py` - Module entry point; exports all identity classes
- `persona.py` - `Persona` dataclass and `VerificationLevel` enum
- `manager.py` - `IdentityManager` for persona lifecycle orchestration
- `biocognitive.py` - `BioCognitiveVerifier` for behavioral biometric authentication using numpy-based statistics
- `identity.py` - Additional identity utilities
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tool definitions
- `SPEC.md` - Module specification
- `SECURITY.md` - Security considerations
- `CHANGELOG.md` - Version history
- `USAGE_EXAMPLES.md` - Usage examples and patterns
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/identity/](../../../docs/modules/identity/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
