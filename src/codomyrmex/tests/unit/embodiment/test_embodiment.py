"""Unit tests for embodiment module."""

import math
import pytest
import asyncio
from codomyrmex.embodiment import ROS2Bridge, Transform3D
from codomyrmex.embodiment.sensors import MockSensor
from codomyrmex.embodiment.actuators import MockActuator, ActuatorCommand


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ros_bridge_pub_sub():
    """Test the basic pub/sub orchestration of the bridge."""
    bridge = ROS2Bridge("test_node")
    await bridge.connect()

    # Track messages received
    received = []
    def callback(msg):
        received.append(msg)

    await bridge.subscribe("/sensor/data", callback)

    # Simulate an incoming message
    test_msg = {"value": 42}
    bridge.simulate_message("/sensor/data", test_msg)
    
    # Wait for async delivery if needed (though simulate_message is currently sync or async-tasked)
    await asyncio.sleep(0.01)

    assert len(received) == 1
    assert received[0].payload == test_msg

@pytest.mark.asyncio
@pytest.mark.unit
async def test_bridge_publishing():
    """Test publishing interface."""
    bridge = ROS2Bridge("test_node")
    await bridge.connect()
    msg = await bridge.publish("/cmd_vel", {"speed": 1.0})
    assert msg is not None
    assert msg.topic == "/cmd_vel"
    assert msg.payload == {"speed": 1.0}

@pytest.mark.unit
def test_transform_3d():
    """Test 3D transformation logic."""
    tf = Transform3D(translation=(1, 2, 3))
    point = (0, 0, 0)
    transformed = tf.transform_point(point)
    assert transformed == (1, 2, 3)

    # Test apply (alias)
    assert tf.apply(point) == (1, 2, 3)

    # Rotation test (90 deg yaw)
    tf_yaw = Transform3D.from_rotation(0, 0, math.pi / 2)
    p = (1, 0, 0)
    p_trans = tf_yaw.apply(p)
    assert abs(p_trans[0]) < 1e-9
    assert abs(p_trans[1] - 1.0) < 1e-9
    assert abs(p_trans[2]) < 1e-9

    assert Transform3D.deg_to_rad(180) == math.pi

@pytest.mark.unit
def test_sensors():
    """Test sensor interface and mock sensor."""
    sensor = MockSensor("temp_1", default_value=25.0)
    assert not sensor.is_connected
    
    with pytest.raises(RuntimeError):
        sensor.read()
        
    sensor.connect()
    assert sensor.is_connected
    
    data = sensor.read()
    assert data.sensor_id == "temp_1"
    assert data.data["value"] == 25.0
    
    sensor.disconnect()
    assert not sensor.is_connected

@pytest.mark.unit
def test_actuators():
    """Test actuator interface and mock actuator."""
    actuator = MockActuator("motor_1")
    assert not actuator.is_connected
    
    cmd = ActuatorCommand("motor_1", "move", {"target": 10.0})
    assert not actuator.execute(cmd)
    
    actuator.connect()
    assert actuator.is_connected
    
    assert actuator.execute(cmd)
    status = actuator.get_status()
    assert status.feedback["position"] == 10.0
    
    actuator.disconnect()
    assert not actuator.is_connected
