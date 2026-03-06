# Embodiment Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Robotics integration with ROS2, sensors, actuators, and 3D transforms. Provides ROS2Bridge for robot communication and Transform3D for spatial calculations. This specification documents the configuration schema and constraints.

## Configuration Schema

The embodiment module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | ROS2 integration requires ROS2 installed and sourced. Transform3D operates independently without external configuration. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- ROS2 integration requires ROS2 installed and sourced. Transform3D operates independently without external configuration.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/embodiment/SPEC.md)
