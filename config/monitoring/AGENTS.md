# Codomyrmex Agents — config/monitoring

## Signposting
- **Parent**: [config](../AGENTS.md)
- **Self**: [monitoring Agents](AGENTS.md)
- **Children**:
    - [examples](examples/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Monitoring and telemetry configuration templates for logging, metrics, alerting, and observability settings. Used across `logging_monitoring/`, `performance/`, `metrics/`, and all modules for logging.

## Active Components

- `README.md` – Monitoring configuration documentation
- `SPEC.md` – Functional specification
- `logging.yaml` – Logging configuration templates
- `metrics.yaml` – Metrics collection settings
- `alerts.yaml` – Alerting rules and thresholds
- `telemetry.yaml` – Telemetry configuration
- `examples/` – Example monitoring configs

## Operating Contracts

- Maintain alignment between code, documentation, and monitoring configurations.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Support multiple logging formats and output destinations.
- Enable consistent observability across all modules.

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Examples**: [examples/](examples/README.md)
- **Parent**: [config](../AGENTS.md)
- **Project Root**: [README](../../README.md)

