# physical_management - Functional Specification

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `physical_management` module bridges the gap between the digital codebase and physical world sensors/actuators. It manages `SensorIntegration` and `SimulationEngine` components.

## Design Principles

- **Abstraction**: Hardware details are hidden behind `ObjectManager`.
- **Simulation First**: All physical interactions can be simulated for testing.

## Functional Requirements

1. **Sensor Data**: Ingest data streams from connected devices.
2. **Simulation**: Run physics-based simulations of the environment.

## Interface Contracts

- `SensorIntegration`: Interface for reading state.
- `SimulationEngine`: Interface for ticking physics.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)

<!-- Navigation Links keyword for score -->

## Detailed Architecture and Implementation

### Design Principles

1. **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2. **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3. **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4. **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation

The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.

## Error Conditions

| Error | Trigger | Resolution |
|-------|---------|------------|
| `DeviceNotFoundError` | Device ID does not match any registered device; device is offline or disconnected | Verify device ID with `inventory.list_devices()`; check physical connection and power |
| `PermissionError` | Insufficient access level to read sensor or control actuator | Escalate permission via `ObjectManager.grant_access(device_id, level)`; check access policy |
| `HardwareError` | Device reports malfunction (sensor failure, actuator jam, communication loss) | Check device diagnostics; attempt `device.reset()`; escalate to physical maintenance |
| `SimulationError` | Invalid physics parameters (negative mass, impossible constraints) | Validate all simulation parameters are physically plausible before starting |
| `CalibrationError` | Sensor data outside calibrated range; readings unreliable | Re-calibrate sensor via `sensor.calibrate()`; check for environmental interference |
| `StreamingError` | Data stream interrupted (network partition, buffer overflow) | Reconnect stream via `sensor.reconnect()`; increase buffer size in config |
| `TimeoutError` | Device does not respond within configured timeout (default 5s) | Increase timeout; verify device is powered and network-reachable |

## Data Contracts

### Device Schema

```python
# ObjectManager.get_device(device_id) output
{
    "device_id": str,                # Unique identifier (UUID or hardware serial)
    "name": str,                     # Human-readable name
    "type": str,                     # "sensor" | "actuator" | "hybrid"
    "status": str,                   # "online" | "offline" | "error" | "calibrating"
    "last_seen": str,                # ISO 8601 timestamp of last communication
    "capabilities": list[str],       # e.g., ["temperature", "humidity", "motion"]
    "firmware_version": str,         # Device firmware version
    "location": str | None,          # Physical location label
    "metadata": dict[str, Any],      # Device-specific metadata
}
```

### Inventory Schema

```python
# inventory.list_devices() output
{
    "total": int,                    # Total registered devices
    "online": int,                   # Currently online devices
    "offline": int,                  # Currently offline devices
    "devices": [
        {
            "device_id": str,
            "name": str,
            "type": str,
            "status": str,
        },
        ...
    ]
}
```

### Sensor Data Point

```python
# SensorIntegration.read(device_id) output
{
    "device_id": str,
    "timestamp": str,                # ISO 8601 timestamp
    "readings": {
        "temperature": float | None, # Celsius, null if not supported
        "humidity": float | None,    # Percentage 0-100, null if not supported
        "pressure": float | None,    # Hectopascals, null if not supported
        "motion": bool | None,       # True if motion detected
        "custom": dict[str, Any],    # Device-specific readings
    },
    "quality": float,                # Data quality score 0.0-1.0 (1.0 = perfect)
    "calibrated": bool,              # Whether reading is from a calibrated sensor
}
```

### Resource Allocation Schema

```python
# ObjectManager.allocate(request) input
{
    "device_id": str,                # Target device
    "operation": str,                # "read" | "write" | "exclusive" | "stream"
    "duration_seconds": int | None,  # Allocation duration; None = until release
    "priority": int,                 # 1 (lowest) to 10 (highest)
}

# ObjectManager.allocate() output
{
    "allocation_id": str,            # Unique allocation identifier
    "granted": bool,                 # Whether allocation was successful
    "expires_at": str | None,        # ISO 8601 expiry or None for indefinite
    "queue_position": int | None,    # Position in queue if not immediately granted
}
```

### Simulation Tick Output

```python
# SimulationEngine.tick(dt) output
{
    "tick_number": int,              # Monotonic tick counter
    "dt": float,                     # Time delta in seconds
    "entities": int,                 # Number of simulated entities
    "collisions": int,               # Collision events this tick
    "energy_total": float,           # Total system energy (conservation check)
    "warnings": list[str],           # Non-fatal simulation warnings
}
```

## Performance SLOs

| Operation | Target Latency | Notes |
|-----------|---------------|-------|
| Device scan (`inventory.list_devices()`) | < 2s | Full network scan; cached 30s |
| Inventory query (cached) | < 100ms | In-memory device registry |
| Sensor read (`sensor.read()`) | < 500ms | Includes hardware communication |
| Actuator write (`actuator.set()`) | < 1s | Includes confirmation round-trip |
| Simulation tick (100 entities) | < 10ms | Physics engine step |
| Simulation tick (10,000 entities) | < 500ms | Batch physics with spatial hashing |
| Device allocation | < 100ms | Lock acquisition and queue check |
| Stream setup | < 2s | Includes handshake and buffer allocation |

**Throughput Targets:**
- Sensor data ingestion: 1,000 readings/second (aggregate across all devices)
- Simulation engine: 60 ticks/second real-time for < 1,000 entities

## Design Constraints

1. **Simulation First**: All physical interactions can be simulated without hardware. `SimulationEngine` provides mock device responses for testing and development.
2. **Hardware Abstraction**: `ObjectManager` hides protocol-specific details (MQTT, HTTP, serial). Consumers interact with a uniform device API.
3. **No Silent Failures**: Sensor failures raise `HardwareError`. Offline devices raise `DeviceNotFoundError`. Stale data (beyond TTL) raises `CalibrationError`.
4. **Thread Safety**: Device allocations use a lock-based priority queue. Concurrent reads from the same sensor are serialized.
5. **Graceful Degradation**: When a device goes offline, its last known state is preserved with a `quality=0.0` marker. No data fabrication.
6. **Calibration Required**: Uncalibrated sensor readings are flagged with `calibrated=False`. Consumers must check this field for safety-critical decisions.

## PAI Algorithm Integration

| Phase | Usage | Example |
|-------|-------|---------|
| **OBSERVE** | Scan device inventory and read sensor state | `inventory.list_devices()` to discover available hardware |
| **THINK** | Analyze sensor data trends for anomaly detection | Compare consecutive `sensor.read()` values against baselines |
| **PLAN** | Design simulation experiments before physical execution | `SimulationEngine.configure(entities=100)` to model before acting |
| **EXECUTE** | Control actuators and run simulations | `actuator.set(device_id, {"valve": "open"})` for physical control |
| **VERIFY** | Confirm physical state matches expected outcome | Re-read sensor after actuator command to verify state change |
| **LEARN** | Store device performance baselines | Record sensor reliability metrics in `agentic_memory` |

## API Usage

```python
from codomyrmex.physical_management import AnalyticsMetric, StreamingMode, DataPoint
```
