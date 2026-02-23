# AWS Compute - Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Specification for AWS virtual machine and container compute services.

## Planned API

Implements the `cloud/common` abstract interface for compute operations:

- Resource provisioning and lifecycle management
- Configuration and scaling
- Monitoring and metrics integration
- Cost tracking via the `performance` module

## Provider-Specific Services

- EC2 instances, ECS containers, EKS Kubernetes

## Dependencies

- `cloud/common` - Abstract base classes and shared interfaces
- `logging_monitoring` - Structured logging
- `config_management` - Credential and configuration management

## Navigation

- **Parent**: [aws/](../README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Cloud Root**: [cloud/](../../README.md)
