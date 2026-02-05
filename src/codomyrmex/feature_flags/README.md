# feature_flags

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Runtime feature flag system for controlling functional and operational aspects of Codomyrmex. Organized into submodules for flag evaluation strategies, persistent storage backends, evaluation logic, and gradual rollout management. The optional `FeatureManager` class in the `core` submodule provides a unified interface for flag lifecycle operations. Enables gradual releases, A/B testing, and rapid incident response through feature toggles.

## Key Exports

### Submodules

- **`strategies`** -- Flag evaluation strategies (percentage-based, user targeting, environment-based, etc.)
- **`storage`** -- Persistent storage backends for flag state (file, database, remote)
- **`evaluation`** -- Flag evaluation engine that resolves flag values against context
- **`rollout`** -- Gradual rollout management with percentage ramps and scheduling

### Core

- **`FeatureManager`** -- Unified feature flag manager for creating, evaluating, and managing flags (available when `core` submodule is installed)

## Directory Contents

- `__init__.py` - Module entry point with submodule exports and optional FeatureManager
- `core/` - Core feature flag manager and flag definitions
- `strategies/` - Evaluation strategies (percentage, user segment, environment)
- `storage/` - Flag state persistence backends
- `evaluation/` - Flag evaluation engine and context resolution
- `rollout/` - Gradual rollout orchestration and scheduling

## Navigation

- **Full Documentation**: [docs/modules/feature_flags/](../../../docs/modules/feature_flags/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
