# Infomaniak - Personal AI Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## PAI Integration Point

This module enables Personal AI Infrastructure to leverage Swiss-hosted cloud resources via Infomaniak's OpenStack platform.

## Key Capabilities for PAI

| Capability | Service | Use Case |
|------------|---------|----------|
| Compute | Nova | Running AI inference workloads |
| Storage | Swift/S3 | Model artifact storage |
| Network | Neutron | Secure isolated networks |
| DNS | Designate | Service discovery |
| Orchestration | Heat | Infrastructure as Code |
| Newsletter | REST API | Mailing lists and campaigns for activeinference.tech |

## Data Residency

Infomaniak data centers are located in Switzerland, providing:

- GDPR compliance
- Swiss data protection standards
- Low-latency access from European locations

## Authentication for PAI

PAI agents should use Application Credentials with minimal required roles:

- `reader` for monitoring and listing
- `member` for full resource management

## Navigation

- **Parent**: [cloud/PAI.md](../PAI.md)
- **Module README**: [README.md](README.md)
