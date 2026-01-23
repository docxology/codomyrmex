# Personal AI Infrastructure Context: config/database/

## Purpose

Database configuration files for Codomyrmex database connections and settings.

## AI Agent Guidance

### Context for Agents

- Contains database connection configurations
- Supports PostgreSQL, SQLite, and other backends
- Example configurations in `examples/` subdirectory

### Configuration Patterns

- Connection strings follow standard URI format
- Sensitive values should use environment variables
- Production configs should never contain plaintext credentials

### Related Modules

- `src/codomyrmex/database_management/` - Database operations
- `config/security/` - Security configuration

## Cross-References

- [README.md](README.md) - Configuration overview
- [AGENTS.md](AGENTS.md) - Agent rules
- [SPEC.md](SPEC.md) - Schema specification
