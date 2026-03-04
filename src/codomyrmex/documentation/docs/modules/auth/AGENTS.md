# Auth -- Agent Integration Guide

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Agent Capabilities

The Auth module provides authentication and authorization primitives. Agents interact with it via direct Python import; no MCP tools are exposed by this module.

## Agent Interaction Patterns

Agents use the auth module internally when accessing secured resources. The `authenticate()` function verifies credentials, and `authorize()` checks permissions against the RBAC registry.

## Trust Level

No MCP tools exposed. Access via direct Python import only.

## Navigation

- **Source**: [src/codomyrmex/auth/](../../../../src/codomyrmex/auth/)
- **Extended README**: [README.md](readme.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Parent**: [All Modules](../README.md)
