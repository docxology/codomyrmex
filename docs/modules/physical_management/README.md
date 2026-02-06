# Physical Management Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Hardware and physical device integration utilities.

## Key Features

- **Devices** — Device discovery
- **Sensors** — Sensor data reading
- **Control** — Device control
- **Drivers** — Driver management

## Quick Start

```python
from codomyrmex.physical_management import DeviceManager

manager = DeviceManager()
devices = manager.discover()

for device in devices:
    status = device.get_status()
    print(f"{device.name}: {status}")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/physical_management/](../../../src/codomyrmex/physical_management/)
- **Parent**: [Modules](../README.md)
