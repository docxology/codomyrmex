# Templating Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Template engines for code and document generation. Provides Jinja2-based templating with custom filters, template inheritance, and dynamic template resolution.

## Configuration Options

The templating module operates with sensible defaults and does not require environment variable configuration. Template directories and Jinja2 environment settings are configurable. Custom filters and extensions can be registered per-environment.

## PAI Integration

PAI agents interact with templating through direct Python imports. Template directories and Jinja2 environment settings are configurable. Custom filters and extensions can be registered per-environment.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep templating

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/templating/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
