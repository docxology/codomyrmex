# AWS Compute - Agents

**Version**: v0.1.0 | **Status**: Planned | **Last Updated**: February 2026

## Purpose

AWS virtual machine and container compute services. Provides abstracted interfaces for managing EC2 instances, ECS containers, EKS Kubernetes through the Codomyrmex cloud common layer.

## Planned Components

| Component | Type | Status |
|-----------|------|--------|
| `__init__.py` | Module entry point | Planned |

## Operating Contracts

- Implements the abstract base classes defined in `cloud/common/`
- Requires `aws` provider credentials configured via environment variables
- All operations are logged through the `logging_monitoring` module

## Navigation

- **Parent**: [aws/](../README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **Cloud Root**: [cloud/](../../README.md)
