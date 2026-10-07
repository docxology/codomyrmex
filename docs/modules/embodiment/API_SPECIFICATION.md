# embodiment - API Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Public API

`codomyrmex.embodiment` exports `SensorPayload`, `TelemetryStream`, and `EmbodimentBridge`; the other symbols are imported from the `sensors`, `actuators`, `ros`, and `transformation` subpackages (for example `from codomyrmex.embodiment.ros import ROS2Bridge`).

| Symbol | Type | Purpose |
| :--- | :--- | :--- |
| `SensorPayload` | Class | Structured sensor reading |
| `TelemetryStream` | Class | Latest-reading registry |
| `EmbodimentBridge` | Class | WebSocket telemetry and actuator command bridge |
| `SensorData` | Class | Sensor reading value object |
| `SimulatedSensor` | Class | Deterministic sensor source |
| `ActuatorCommand` | Class | Actuator command value object |
| `ActuatorStatus` | Class | Actuator status enum |
| `SimulatedActuator` | Class | Deterministic actuator sink |
| `ROS2Bridge` | Class | In-process topic bridge |
| `TopicMessage` | Class | Topic message value object |
| `TopicInfo` | Class | Topic metadata value object |
| `Vec3` | Class | 3D vector value |
| `Transform3D` | Class | Euler transform composition and inversion |

## Example

```python
import asyncio

from codomyrmex.embodiment.actuators import ActuatorCommand, SimulatedActuator
from codomyrmex.embodiment.ros import ROS2Bridge

bridge = ROS2Bridge()
bridge.create_topic("/events")
message = asyncio.run(bridge.publish("/events", {"status": "ok"}))  # publish is async

actuator = SimulatedActuator("arm")
actuator.connect()
accepted = actuator.execute(
    ActuatorCommand(actuator_id="arm", command_type="move", parameters={"target": "home"})
)
```
