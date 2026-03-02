# Agent Guidelines - Physical Management

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Physical device and hardware management for IoT and robotics.

## Key Classes

- **DeviceManager** — Manage physical devices
- **SensorHub** — Collect sensor data
- **ActuatorController** — Control actuators
- **ResourceMonitor** — Monitor physical resources

## Agent Instructions

1. **Verify connections** — Check device connectivity
2. **Handle timeouts** — Physical devices may be slow
3. **Safe defaults** — Use safe actuator defaults
4. **Rate limit** — Don't overwhelm hardware
5. **Log all actions** — Audit trail for physical changes

## Common Patterns

```python
from codomyrmex.physical_management import (
    DeviceManager, SensorHub, ActuatorController
)

# Manage devices
devices = DeviceManager()
devices.discover()  # Auto-discover devices

for device in devices.list():
    print(f"{device.id}: {device.status}")

# Collect sensor data
sensors = SensorHub()
temp = sensors.read("temperature_01")
humidity = sensors.read_batch(["humidity_01", "humidity_02"])

# Control actuators
actuator = ActuatorController("motor_01")
actuator.set_position(90)  # degrees
actuator.wait_for_completion()
```

## Testing Patterns

```python
# Verify device discovery (simulation mode)
devices = DeviceManager(simulation=True)
devices.add_simulated_device("test_device")
assert len(devices.list()) == 1

# Verify sensor reading (simulation mode)
sensors = SensorHub(simulation=True)
value = sensors.read("simulated_sensor")
assert value is not None
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Manages physical resources, hardware inventory, and device tracking via `DeviceManager`, `SensorHub`, and `ActuatorController`. Handles device discovery, sensor reads, and actuator commands.

### Architect Agent
**Use Cases**: Designs resource allocation models, reviews hardware abstraction layers, evaluates IoT protocol choices, and analyzes dependency flow between physical management and upstream modules.

### QATester Agent
**Use Cases**: Validates hardware state tracking in simulation mode, verifies sensor read accuracy, confirms actuator position commands, and tests device discovery edge cases.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
