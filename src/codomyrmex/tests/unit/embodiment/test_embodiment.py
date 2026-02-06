"""Unit tests for embodiment module."""
import pytest

from codomyrmex.embodiment import ROS2Bridge, Transform3D


@pytest.mark.unit
def test_ros_bridge_pub_sub():
    """Test the basic pub/sub orchestration of the bridge."""
    bridge = ROS2Bridge("test_node")

    # Track messages received
    received = []
    def callback(msg):
        received.append(msg)

    bridge.subscribe("/sensor/data", callback)

    # Simulate an incoming message
    test_msg = {"value": 42}
    bridge.simulate_message("/sensor/data", test_msg)

    assert len(received) == 1
    assert received[0] == test_msg

@pytest.mark.unit
def test_bridge_publishing():
    """Test publishing interface."""
    bridge = ROS2Bridge("test_node")
    assert bridge.publish("/cmd_vel", {"speed": 1.0}) is True

@pytest.mark.unit
def test_transform_3d():
    """Test 3D transformation logic."""
    tf = Transform3D(translation=(1, 2, 3))
    point = (0, 0, 0)
    transformed = tf.transform_point(point)
    assert transformed == (1, 2, 3)

    assert Transform3D.deg_to_rad(180) > 3.14
