# Personal AI Infrastructure — Auth Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Auth module provides authentication, authorization, and token management for Codomyrmex services. It implements credential verification, role-based access control (RBAC), and token lifecycle management — essential for securing PAI agent actions and MCP tool access.

## PAI Capabilities

### Authentication

```python
from codomyrmex.auth import authenticate, get_authenticator, Token

# Authenticate with credentials
token = authenticate({"api_key": "sk-...", "provider": "openai"})

# Get the authenticator instance
auth = get_authenticator()
```

### Authorization (RBAC)

```python
from codomyrmex.auth import authorize, Token

# Check if a token grants access to a resource
allowed = authorize(token, resource="mcp_tools", permission="execute")
```

### Token Management

```python
from codomyrmex.auth import TokenManager, TokenValidator

manager = TokenManager()
token = manager.issue(subject="pai_agent", scopes=["read", "write"])

validator = TokenValidator()
is_valid = validator.validate(token)
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Authenticator` | Class | Core authentication engine |
| `APIKeyManager` | Class | API key storage and validation |
| `PermissionRegistry` | Class | RBAC permission definitions |
| `Token` | Class | Token data model |
| `TokenManager` | Class | Token issuance and revocation |
| `TokenValidator` | Class | Token verification |
| `authenticate` | Function | Convenience authentication entry point |
| `authorize` | Function | Convenience authorization check |
| `get_authenticator` | Function | Singleton authenticator accessor |

## PAI Algorithm Phase Mapping

| Phase | Auth Contribution |
|-------|-------------------|
| **OBSERVE** | Validate agent identity and credentials before codebase access |
| **EXECUTE** | Gate MCP tool execution with token-based authorization |
| **VERIFY** | Verify that all agent actions were properly authenticated |
| **LEARN** | Audit log of auth events for security review |

## Architecture Role

**Service Layer** — Consumed by `model_context_protocol/` for MCP auth, `agents/pai/` trust gateway, and `security/` governance.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
