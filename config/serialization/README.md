# Serialization Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Data serialization and deserialization supporting JSON, YAML, TOML, MessagePack, and pickle formats with validation and type safety.

## Configuration Options

The serialization module operates with sensible defaults and does not require environment variable configuration. Serialization format is selected per-operation. Pickle validation is enforced for security. Custom serializers can be registered.

## PAI Integration

PAI agents interact with serialization through direct Python imports. Serialization format is selected per-operation. Pickle validation is enforced for security. Custom serializers can be registered.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep serialization

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/serialization/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
