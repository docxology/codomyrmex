# Personal AI Infrastructure Context: config/security/

## Purpose

Security configuration including encryption, authentication, and access control settings.

## AI Agent Guidance

### Context for Agents

- Encryption keys and algorithms
- Authentication providers
- Access control policies
- Secret management configuration

### Security Patterns

- Never commit secrets to version control
- Use environment variables or secret managers
- Follow principle of least privilege

### Related Modules

- `src/codomyrmex/security/` - Security operations
- `src/codomyrmex/auth/` - Authentication
- `src/codomyrmex/encryption/` - Encryption

## Cross-References

- [README.md](README.md) - Configuration overview
- [AGENTS.md](AGENTS.md) - Agent rules
- [SPEC.md](SPEC.md) - Schema specification
