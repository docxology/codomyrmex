# Codomyrmex Agents — config/security

## Signposting
- **Parent**: [config](../AGENTS.md)
- **Self**: [security Agents](AGENTS.md)
- **Children**:
    - [examples](examples/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Security and authentication configuration templates for API keys, authentication providers, authorization policies, encryption settings, and security policies. Used across `auth/`, `security/`, `api/`, `config_management/`, and `project_orchestration/` modules.

## Active Components

- `README.md` – Security configuration documentation
- `SPEC.md` – Functional specification
- `api-keys.yaml` – API key templates and validation rules
- `authentication.yaml` – Authentication provider configurations
- `authorization.yaml` – Permission and role definitions
- `encryption.yaml` – Encryption key management templates
- `security-policies.yaml` – Security policy configurations
- `examples/` – Example security configurations

## Operating Contracts

- Maintain alignment between code, documentation, and security configurations.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Never commit actual secrets or API keys to version control.
- Use environment variable references for all sensitive values.

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Examples**: [examples/](examples/README.md)
- **Parent**: [config](../AGENTS.md)
- **Project Root**: [README](../../README.md)

