# Deployment Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Guides for deploying Codomyrmex to production environments. Covers infrastructure requirements, deployment strategies, monitoring, and operational best practices.

## Contents

| File | Description |
|------|-------------|
| [**production.md**](production.md) | Comprehensive production deployment guide |
| [AGENTS.md](AGENTS.md) | Agent coordination for deployment docs |
| [SPEC.md](SPEC.md) | Deployment documentation specification |
| [PAI.md](PAI.md) | Personal AI deployment considerations |

## Key Topics

### Production Deployment

- **Infrastructure Requirements**: Hardware, Docker, Kubernetes
- **Configuration Management**: Environment variables, secrets
- **Scaling Strategies**: Horizontal scaling, load balancing
- **Monitoring & Observability**: Logging, metrics, alerting

### Security Considerations

- API key management
- Network security
- Access control

## Quick Start

For immediate production deployment:

```bash
# See production.md for full guide
./scripts/deploy.sh production
```

## Related Documentation

- [Environment Setup](../development/environment-setup.md) - Development setup
- [Security Guide](../reference/security.md) - Security best practices
- [Architecture](../project/architecture.md) - System design

## Navigation

- **Parent**: [docs/](../README.md)
- **Root**: [Project Root](../../README.md)
