# Embodiment - API Specification

## Introduction

The Embodiment module provides tools for connecting AI agents to physical or simulated robots, including ROS2 integration and 3D transformation utilities.

## Endpoints / Functions / Interfaces

### Class: `ROS2Bridge`

- **Description**: Bridge for communicating with ROS2 (Robot Operating System 2).
- **Constructor**:
    - `node_name` (str): ROS2 node name. Default: "codomyrmex_bridge".
    - `namespace` (str, optional): ROS2 namespace.
    - `spin_thread` (bool, optional): Whether to spin in separate thread. Default: True.
- **Methods**:

#### `connect() -> bool`

- **Description**: Initialize ROS2 connection.
- **Returns**:
    - `bool`: True if connection successful.

#### `disconnect() -> None`

- **Description**: Disconnect from ROS2.

#### `publish(topic: str, message: Any, msg_type: str) -> bool`

- **Description**: Publish a message to a topic.
- **Parameters/Arguments**:
    - `topic` (str): Topic name.
    - `message` (Any): Message data.
    - `msg_type` (str): ROS2 message type.
- **Returns**:
    - `bool`: True if publish successful.

#### `subscribe(topic: str, msg_type: str, callback: Callable) -> Subscription`

- **Description**: Subscribe to a topic.
- **Parameters/Arguments**:
    - `topic` (str): Topic name.
    - `msg_type` (str): ROS2 message type.
    - `callback` (Callable): Callback for received messages.
- **Returns**:
    - `Subscription`: Subscription handle.

#### `call_service(service: str, request: Any, srv_type: str) -> Any`

- **Description**: Call a ROS2 service.
- **Parameters/Arguments**:
    - `service` (str): Service name.
    - `request` (Any): Service request.
    - `srv_type` (str): Service type.
- **Returns**:
    - `Any`: Service response.

#### `send_action(action: str, goal: Any, action_type: str) -> ActionHandle`

- **Description**: Send an action goal.
- **Parameters/Arguments**:
    - `action` (str): Action server name.
    - `goal` (Any): Action goal.
    - `action_type` (str): Action type.
- **Returns**:
    - `ActionHandle`: Handle for tracking action progress.

#### `get_parameter(name: str) -> Any`

- **Description**: Get a ROS2 parameter value.
- **Parameters/Arguments**:
    - `name` (str): Parameter name.
- **Returns**:
    - `Any`: Parameter value.

#### `set_parameter(name: str, value: Any) -> bool`

- **Description**: Set a ROS2 parameter value.
- **Parameters/Arguments**:
    - `name` (str): Parameter name.
    - `value` (Any): Parameter value.
- **Returns**:
    - `bool`: True if successful.

### Class: `Transform3D`

- **Description**: Represents a 3D transformation (position + orientation).
- **Constructor**:
    - `position` (tuple[float, float, float], optional): XYZ position. Default: (0, 0, 0).
    - `orientation` (tuple[float, float, float, float], optional): Quaternion (x, y, z, w). Default: (0, 0, 0, 1).
- **Methods**:

#### `from_matrix(matrix: np.ndarray) -> Transform3D` (classmethod)

- **Description**: Create transform from 4x4 transformation matrix.
- **Parameters/Arguments**:
    - `matrix` (np.ndarray): 4x4 transformation matrix.
- **Returns**:
    - `Transform3D`: Transform instance.

#### `to_matrix() -> np.ndarray`

- **Description**: Convert to 4x4 transformation matrix.
- **Returns**:
    - `np.ndarray`: 4x4 transformation matrix.

#### `from_euler(roll: float, pitch: float, yaw: float, position: tuple) -> Transform3D` (classmethod)

- **Description**: Create transform from Euler angles.
- **Parameters/Arguments**:
    - `roll` (float): Roll angle in radians.
    - `pitch` (float): Pitch angle in radians.
    - `yaw` (float): Yaw angle in radians.
    - `position` (tuple): XYZ position.
- **Returns**:
    - `Transform3D`: Transform instance.

#### `to_euler() -> tuple[float, float, float]`

- **Description**: Convert orientation to Euler angles.
- **Returns**:
    - `tuple[float, float, float]`: Roll, pitch, yaw in radians.

#### `inverse() -> Transform3D`

- **Description**: Compute inverse transform.
- **Returns**:
    - `Transform3D`: Inverted transform.

#### `compose(other: Transform3D) -> Transform3D`

- **Description**: Compose with another transform.
- **Parameters/Arguments**:
    - `other` (Transform3D): Transform to compose with.
- **Returns**:
    - `Transform3D`: Composed transform.

#### `transform_point(point: tuple[float, float, float]) -> tuple[float, float, float]`

- **Description**: Transform a 3D point.
- **Parameters/Arguments**:
    - `point` (tuple): XYZ point.
- **Returns**:
    - `tuple`: Transformed XYZ point.

## Data Models

### Model: `Subscription`
- `topic` (str): Subscribed topic.
- `msg_type` (str): Message type.
- `active` (bool): Whether subscription is active.

### Model: `ActionHandle`
- `action` (str): Action name.
- `goal_id` (str): Goal identifier.
- `status` (str): Status (pending, accepted, running, succeeded, failed, cancelled).
- `result` (Any | None): Action result when completed.

## Authentication & Authorization

ROS2 security can be configured via DDS security settings. Refer to ROS2 DDS security documentation.

## Rate Limiting

Message publishing rates may be subject to ROS2 QoS (Quality of Service) settings.

## Versioning

This API follows semantic versioning. Breaking changes will be documented in the changelog.
