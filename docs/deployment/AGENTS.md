# Codomyrmex Agents — docs/deployment

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Documentation for deploying Codomyrmex to production environments. Covers infrastructure, configuration, monitoring, and operational best practices.

## Active Components

| File | Priority | Description |
|------|----------|-------------|
| [production.md](production.md) | **Critical** | Production deployment guide |
| [README.md](README.md) | High | Directory overview |
| [SPEC.md](SPEC.md) | Medium | Functional specification |
| [PAI.md](PAI.md) | Medium | PAI considerations |

## Agent Guidelines

### Deployment Quality Standards

1. **Infrastructure**: Ensure infrastructure docs match current architecture
2. **Configuration**: Validate all configuration examples are correct
3. **Security**: Verify security recommendations are up-to-date
4. **Monitoring**: Keep monitoring setup docs current

### When Modifying Deployment Docs

- Test all deployment commands before documenting
- Update environment variable lists when configs change
- Verify Docker/K8s configurations are valid
- Update troubleshooting for new failure modes

## Operating Contracts

- Maintain alignment between deployment docs and actual infrastructure
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Navigation Links

- **📁 Parent Directory**: [docs/](../README.md)
- **🏠 Project Root**: [../../README.md](../../README.md)
- **📦 Related**: [Development](../development/) | [Reference](../reference/)
