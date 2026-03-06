"""Tests for embodiment sensors, actuators, and ROS base classes."""

import asyncio
import pytest
from codomyrmex.embodiment.actuators.base import ActuatorCommand, ActuatorStatus
from codomyrmex.embodiment.sensors.base import SensorData
from codomyrmex.embodiment.ros.ros_bridge import ROS2Bridge, Message

@pytest.mark.unit
class TestDataclasses:
    def test_sensor_data_defaults(self):
        sd = SensorData(sensor_id="s1")
        assert sd.sensor_id == "s1"
        assert sd.timestamp > 0
        assert sd.metadata == {}
        assert sd.data is None

    def test_actuator_status_defaults(self):
        as_ = ActuatorStatus(actuator_id="a1", status="ok", feedback={"pos": 1})
        assert as_.actuator_id == "a1"
        assert as_.status == "ok"
        assert as_.feedback == {"pos": 1}
        assert as_.timestamp > 0

    def test_actuator_command(self):
        ac = ActuatorCommand(actuator_id="a1", command_type="move", parameters={"p": 1})
        assert ac.actuator_id == "a1"
        assert ac.command_type == "move"
        assert ac.parameters == {"p": 1}

@pytest.mark.asyncio
@pytest.mark.unit
class TestROS2BridgeAdvanced:
    async def test_history(self):
        bridge = ROS2Bridge("test_history", history_depth=5)
        await bridge.connect()
        for i in range(10):
            await bridge.publish("/topic", {"i": i})
        
        hist = bridge.get_history("/topic")
        assert len(hist) == 5
        assert hist[0].payload["i"] == 5
        assert hist[-1].payload["i"] == 9

        last_2 = bridge.get_history("/topic", last_n=2)
        assert len(last_2) == 2
        assert last_2[0].payload["i"] == 8

        bridge.clear_history("/topic")
        assert len(bridge.get_history("/topic")) == 0

        bridge.clear_history()  # Clear all test
        assert len(bridge.get_history("/topic")) == 0

    async def test_latched_subscribe(self):
        bridge = ROS2Bridge("test_latch")
        await bridge.connect()
        bridge.create_topic("/latched", latched=True)
        await bridge.publish("/latched", {"status": "ready"})

        received = []
        def handler(msg):
            received.append(msg)
            
        await bridge.subscribe("/latched", handler, replay_latched=True)
        assert len(received) == 1
        assert received[0].payload["status"] == "ready"

    async def test_list_topics_and_status(self):
        bridge = ROS2Bridge("test_meta")
        await bridge.connect()
        bridge.create_topic("/t1", latched=False)
        await bridge.publish("/t1", {"a": 1})
        await bridge.publish("/t1", {"a": 2})

        topics = bridge.list_topics()
        assert len(topics) == 1
        assert topics[0].name == "/t1"
        assert topics[0].total_published == 2
        assert topics[0].subscriber_count == 0

        assert bridge.total_messages == 2
        bridge.disconnect()
        
    async def test_simulate_message_async(self):
        bridge = ROS2Bridge("test_sim")
        await bridge.connect()
        
        received = []
        async def async_handler(msg):
            received.append(msg)
            
        await bridge.subscribe("/sim", async_handler)
        
        # simulated message is delivered without storing in history
        bridge.simulate_message("/sim", {"fake": True})
        
        # let async task complete
        await asyncio.sleep(0.01)
        
        assert len(received) == 1
        assert len(bridge.get_history("/sim")) == 0
