import json
from pathlib import Path
from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery, default_serializer

def test_default_serializer():
    assert default_serializer(Path("/tmp/test")) == str(Path("/tmp/test"))
    # The serializer handles sets by converting to list then stringifying
    assert default_serializer({1, 2, 3}) == str([1, 2, 3])
    assert default_serializer(123) == "123"
    assert default_serializer("test") == "test"

class TestDiscoveryEngine(SystemDiscovery):
    def scan_system(self):
        return {
            "path_obj": Path("/some/path"),
            "set_obj": {1, 2, 3},
            "custom_obj": object(),
        }

def test_export_inventory(tmp_path):
    engine = TestDiscoveryEngine()
    output_path = tmp_path / "inventory.json"

    success = engine.export_inventory(output_path)

    assert success is True
    assert output_path.exists()

    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["path_obj"] == str(Path("/some/path"))
    assert isinstance(data["set_obj"], str)
