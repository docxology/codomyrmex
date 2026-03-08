# Model Ops Configuration

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

ML model operations including versioning, deployment, monitoring, and feature store integration. Provides model lifecycle management and experiment tracking.

## Configuration Options

The model_ops module operates with sensible defaults and does not require environment variable configuration. Model registry storage path and experiment tracking backend are configurable. Feature store integration requires feature_store module.

## PAI Integration

PAI agents interact with model_ops through direct Python imports. Model registry storage path and experiment tracking backend are configurable. Feature store integration requires feature_store module.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep model_ops

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/model_ops/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
