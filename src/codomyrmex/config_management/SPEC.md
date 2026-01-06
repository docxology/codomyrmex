# config_management - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Centralized management of application configuration and secrets. It loads, validates, and serves config to other modules.

## Design Principles
- **Environment Aware**: Different values for Dev/Staging/Prod.
- **Secret Safety**: Secrets must never be logged or stored in plain text (`SecretManager`).

## Functional Requirements
1.  **Loading**: Read from YAML/JSON/Env vars.
2.  **Validation**: Ensure config meets schema requirements.

## Interface Contracts
- `ConfigLoader`: API for retrieving values.
- `SecretManager`: API for encryption/decryption.

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)
