# Defense Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Threat detection, rate limiting, and response engine. Provides ActiveDefense for exploit detection, RabbitHole for attacker engagement, and Defense for orchestrating security responses.

## Configuration Options

The defense module operates with sensible defaults and does not require environment variable configuration. Detection rules and response actions are configured through DetectionRule and ResponseAction models. Severity levels control escalation behavior.

## PAI Integration

PAI agents interact with defense through direct Python imports. Detection rules and response actions are configured through DetectionRule and ResponseAction models. Severity levels control escalation behavior.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep defense

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/defense/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
