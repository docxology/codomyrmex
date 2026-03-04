# Embodiment Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Robotics integration with ROS2, sensors, actuators, and 3D transforms. Provides ROS2Bridge for robot communication and Transform3D for spatial calculations.

## Configuration Options

The embodiment module operates with sensible defaults and does not require environment variable configuration. ROS2 integration requires ROS2 installed and sourced. Transform3D operates independently without external configuration.

## PAI Integration

PAI agents interact with embodiment through direct Python imports. ROS2 integration requires ROS2 installed and sourced. Transform3D operates independently without external configuration.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep embodiment

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/embodiment/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
