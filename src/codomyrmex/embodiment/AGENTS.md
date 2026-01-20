# embodiment - Technical Documentation

## Operating Contract

- Use asynchronous messaging for all robot communications.
- Validate all motion commands against safety constraints before execution.
- Maintain a history of sensor data for temporal reasoning.
- Provide a clean abstraction over specific ROS2 message types.

## Directory Structure

- `__init__.py`: Module entry point and exports.
- `ros_bridge.py`: Core ROS2 communication logic.
- `sensors.py`: Sensor data wrappers (Camera, Lidar, etc.).
- `actuators.py`: Motion control and action dispatching.
- `safety.py`: Safety monitoring and collision avoidance logic.

## Communication Pattern

1. **Discovery**: Identify available ROS2 topics and services.
2. **Subscription**: Attach callbacks to relevant sensor streams.
3. **Processing**: Transform raw sensor data into high-level features.
4. **Command**: Dispatch control messages back to the robot.

## Testing Strategy

- Unit tests for data transformation logic (e.g., coordinate system shifts).
- Mocked ROS2 environment to verify publish/subscribe cycles.
- Simulation-based integration tests for safety constraint enforcement.
