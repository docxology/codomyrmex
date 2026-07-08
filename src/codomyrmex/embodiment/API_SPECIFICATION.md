# Embodiment API Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Telemetry

- `SensorPayload(node_id, timestamp, sensor_type, readings, metadata={})`
- `SensorPayload.parse_payload(raw)` parses a JSON string and raises `ValueError` for invalid payloads.
- `TelemetryStream.ingest(payload)` stores a payload.
- `TelemetryStream.get_latest(node_id)` returns the latest payload for a node or `None`.

## Bridge

- `EmbodimentBridge.subscribe(callback)` registers a payload subscriber.
- `EmbodimentBridge.start_server(host, port)` starts a local WebSocket server.
- `EmbodimentBridge.send_command(node_id, command)` sends JSON to a connected node and returns `bool`.

## Sensors And Actuators

- `SensorData(sensor_id, timestamp, data, metadata)`
- `SimulatedSensor.connect()`, `disconnect()`, and `read()`
- `ActuatorCommand(actuator_id, command_type, parameters)`
- `ActuatorStatus(actuator_id, status, feedback)`
- `SimulatedActuator.connect()`, `disconnect()`, `execute(command)`, and `get_status()`

## ROS-Style Bridge

- `ROS2Bridge.connect()` and `disconnect()`
- `ROS2Bridge.create_topic(name, latched=False)`
- `ROS2Bridge.publish(topic, payload)`
- `ROS2Bridge.subscribe(topic, handler, replay_latched=False)`
- `ROS2Bridge.get_history(topic, last_n=None)`
- `ROS2Bridge.clear_history(topic=None)`
- `ROS2Bridge.list_topics()`
- `ROS2Bridge.simulate_message(topic, payload)`

## Transform Math

- `Vec3` supports addition, subtraction, scalar multiplication, length, normalization, dot, cross, tuple, and dict conversion.
- `Transform3D` supports identity, translation, yaw construction, vector rotation, composition, inverse, radian/degree conversion, and dict conversion.
