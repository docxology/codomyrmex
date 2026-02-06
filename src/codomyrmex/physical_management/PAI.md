# Personal AI Infrastructure — Physical Management Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Physical Management module provides PAI integration for hardware and IoT devices.

## PAI Capabilities

### Device Discovery

Find connected devices:

```python
from codomyrmex.physical_management import DeviceManager

manager = DeviceManager()
devices = manager.discover()

for device in devices:
    print(f"{device.name}: {device.type}")
```

### Device Control

Control devices:

```python
from codomyrmex.physical_management import DeviceManager

manager = DeviceManager()
device = manager.get("sensor_1")
data = device.read()
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `DeviceManager` | Device management |
| `discover` | Find devices |
| `control` | Control hardware |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
