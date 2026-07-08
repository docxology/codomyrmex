# embodiment - API Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Public API

| Symbol | Type | Purpose |
| :--- | :--- | :--- |
| `SensorPayload` | Class | Structured sensor reading |
| `TelemetryStream` | Class | Latest-reading registry |
| `EmbodimentBridge` | Class | WebSocket telemetry and actuator command bridge |
| `SensorData` | Class | Sensor reading value object |
| `SimulatedSensor` | Class | Deterministic sensor source |
| `MockSensor` | Class | Compatibility alias for simulated sensors |
| `ActuatorCommand` | Class | Actuator command value object |
| `ActuatorStatus` | Class | Actuator status enum |
| `SimulatedActuator` | Class | Deterministic actuator sink |
| `MockActuator` | Class | Compatibility alias for simulated actuators |
| `ROS2Bridge` | Class | In-process topic bridge |
| `TopicMessage` | Class | Topic message value object |
| `TopicInfo` | Class | Topic metadata value object |
| `Vec3` | Class | 3D vector value |
| `Transform3D` | Class | Euler transform composition and inversion |

## Example

```python
from codomyrmex.embodiment import ROS2Bridge, SimulatedActuator

bridge = ROS2Bridge()
bridge.create_topic("/events")
bridge.publish("/events", {"status": "ok"})

actuator = SimulatedActuator("arm")
result = actuator.execute({"target": "home"})
```
