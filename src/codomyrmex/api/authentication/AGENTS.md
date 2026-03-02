# AI Agent Guidelines — api/authentication

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides pluggable authentication strategies for API requests, supporting six auth types through a common `Authenticator` interface with factory-based instantiation.

## Key Components

| Component | Role |
|-----------|------|
| `AuthType` | Enum of supported auth types: `API_KEY`, `BEARER_TOKEN`, `BASIC_AUTH`, `OAUTH2`, `HMAC`, `JWT` |
| `AuthCredentials` | Dataclass holding auth type, credential value, and optional metadata |
| `AuthResult` | Dataclass with `authenticated` bool, `user_id`, `roles`, and `error` |
| `Authenticator` | ABC defining `authenticate(credentials) -> AuthResult` contract |
| `APIKeyAuthenticator` | Validates API keys against a key store dict |
| `BearerTokenAuthenticator` | Validates bearer tokens via a verification callable |
| `BasicAuthenticator` | Username/password authentication against a user store |
| `HMACAuthenticator` | HMAC signature verification with shared secret |
| `create_authenticator` | Factory function returning the correct `Authenticator` for a given `AuthType` |

## Operating Contracts

- All authenticators implement the `Authenticator` ABC (`authenticate` method).
- `AuthResult.authenticated` is always set; `error` is populated on failure.
- `create_authenticator(auth_type, **kwargs)` selects the implementation by `AuthType` enum value.
- No external dependencies beyond the Python standard library.

## Integration Points

- **Parent**: `api` module uses authenticators as middleware in request pipelines.
- **Consumers**: Any module requiring request-level authentication (REST API, webhooks, MCP server).
- **Pattern**: Instantiate via `create_authenticator`, then call `authenticate(credentials)`.

## Navigation

- **Parent**: [api/README.md](../README.md)
- **Sibling**: [SPEC.md](SPEC.md) | [README.md](README.md)
- **Root**: [../../../../README.md](../../../../README.md)
