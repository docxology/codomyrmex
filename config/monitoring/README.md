# config/monitoring

## Signposting
- **Parent**: [config](../README.md)
- **Children**:
    - [examples](examples/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Monitoring and telemetry configuration templates for Codomyrmex. Provides centralized configuration for logging, metrics, alerting, and observability settings used across all modules.

## Directory Contents

- `README.md` – This file
- `SPEC.md` – Functional specification
- `AGENTS.md` – Agent coordination documentation
- `logging.yaml` – Logging configuration templates
- `metrics.yaml` – Metrics collection settings
- `alerts.yaml` – Alerting rules and thresholds
- `telemetry.yaml` – Telemetry configuration
- `examples/` – Example monitoring configs

## Configuration Files

### logging.yaml
Logging configuration templates including log levels, formats, output destinations, and rotation policies.

### metrics.yaml
Metrics collection settings including metric types, collection intervals, and storage configurations.

### alerts.yaml
Alerting rules and thresholds for monitoring system health and performance.

### telemetry.yaml
Telemetry configuration for distributed tracing, performance monitoring, and observability.

## Usage

Monitoring configurations are loaded by the `config_management` module and used by:
- `logging_monitoring/` - Centralized logging system
- `performance/` - Performance monitoring
- `metrics/` - Metrics collection
- All modules for logging

## Best Practices

- Configure appropriate log levels for each environment
- Set up log rotation to manage disk space
- Enable metrics collection for performance monitoring
- Configure alerts for critical system events
- Use structured logging for better analysis

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Examples**: [examples/](examples/README.md)
- **Parent Directory**: [config](../README.md)
- **Project Root**: [README](../../README.md)

