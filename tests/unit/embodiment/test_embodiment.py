"""Unit tests for the Physical Embodiment Bridge and Telemetry.

Zero-Mock Policy: Uses `websockets` package to instantiate real
local network ingress servers and genuine payload parsers to
validate agent-to-hardware communication natively.
"""

import asyncio
import json

import pytest

try:
    import websockets
except ImportError:
    websockets = None  # type: ignore

from codomyrmex.embodiment.bridge import EmbodimentBridge
from codomyrmex.embodiment.telemetry import SensorPayload, TelemetryStream


@pytest.mark.unit
def test_parse_valid_sensor_payload():
    """Test standard hardware sensor payload parses cleanly."""
    raw = json.dumps(
        {
            "node_id": "rover-01",
            "timestamp": 12345.6,
            "sensor_type": "lidar",
            "readings": {"distance": 5.4, "angle": 45.0},
            "metadata": {"battery": "good"},
        }
    )
    payload = SensorPayload.parse_payload(raw)
    assert payload.node_id == "rover-01"
    assert payload.timestamp == 12345.6
    assert payload.sensor_type == "lidar"
    assert payload.readings["distance"] == 5.4
    assert payload.readings["angle"] == 45.0
    assert payload.metadata["battery"] == "good"


@pytest.mark.unit
def test_parse_invalid_payload_raises_value_error():
    """Test malformed hardware payload throws predictable error."""
    raw = json.dumps({"missing": "required_keys"})
    with pytest.raises(ValueError, match="Invalid sensor payload"):
        SensorPayload.parse_payload(raw)


@pytest.mark.unit
def test_telemetry_stream_aggregation():
    """Test telemetry stream correctly scopes payloads by node."""
    stream = TelemetryStream()
    p1 = SensorPayload("node1", 1.0, "temp", {"c": 20}, {})
    p2 = SensorPayload("node2", 2.0, "temp", {"c": 21}, {})
    p3 = SensorPayload("node1", 3.0, "temp", {"c": 22}, {})

    stream.ingest(p1)
    stream.ingest(p2)
    stream.ingest(p3)

    latest1 = stream.get_latest("node1")
    assert latest1 is not None and latest1.timestamp == 3.0

    latest2 = stream.get_latest("node2")
    assert latest2 is not None and latest2.timestamp == 2.0

    assert stream.get_latest("unknown") is None


@pytest.mark.asyncio
@pytest.mark.skipif(
    websockets is None, reason="websockets library required for real async testing"
)
async def test_embodiment_bridge_telemetry_flow():
    """Test full async lifecycle of hardware connecting and streaming telemetry."""
    bridge = EmbodimentBridge()

    # Capture outputs via subscriber
    received = []
    bridge.subscribe(received.append)

    # Start the real server
    server = await bridge.start_server(host="127.0.0.1", port=8766)

    try:
        # Simulate local hardware connecting natively over WS
        async with websockets.connect("ws://127.0.0.1:8766") as ws:
            # 1. Handshake
            await ws.send(json.dumps({"node_id": "drone-99"}))

            # Allow brief asyncio context switch for server to register connection
            await asyncio.sleep(0.1)

            assert "drone-99" in bridge._connected_nodes

            # 2. Transmit real telemetry
            telemetry = {
                "node_id": "drone-99",
                "timestamp": 100.0,
                "sensor_type": "altimeter",
                "readings": {"z": 10.5},
            }
            await ws.send(json.dumps(telemetry))

            # Allow processing
            await asyncio.sleep(0.1)

            # Verification
            assert len(received) == 1
            assert received[0].node_id == "drone-99"
            assert received[0].readings["z"] == 10.5

            # 3. Server sends actuator command back to node
            success = await bridge.send_command("drone-99", {"action": "ascend"})
            assert success is True

            response = await ws.recv()
            assert json.loads(response)["action"] == "ascend"

    finally:
        server.close()
        await server.wait_closed()
