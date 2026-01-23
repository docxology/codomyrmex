# Personal AI Infrastructure Context: config/cache/

## Purpose

Cache backend configuration for Redis, in-memory, and file-based caching.

## AI Agent Guidance

### Context for Agents

- Configures cache backends (Redis, memory, filesystem)
- TTL and eviction policies
- Namespace isolation for multi-tenant scenarios

### Configuration Patterns

- Redis connection via URL or host/port
- Default TTLs by cache category
- Serialization format (JSON, pickle, msgpack)

### Related Modules

- `src/codomyrmex/cache/` - Cache operations

## Cross-References

- [README.md](README.md) - Configuration overview
- [AGENTS.md](AGENTS.md) - Agent rules
- [SPEC.md](SPEC.md) - Schema specification
