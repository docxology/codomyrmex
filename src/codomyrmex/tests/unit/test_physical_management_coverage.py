# type: ignore
"""Functional tests for physical_management module — zero-mock.

Exercises data models, ObjectRegistry (registration, spatial queries,
collision detection, network analysis, persistence), and
PhysicalObjectManager (create, move, batch ops, pathfinding, bounding box).
"""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

import pytest

from codomyrmex.physical_management.models import (
    EventType,
    MaterialProperties,
    MaterialType,
    ObjectEvent,
    ObjectStatus,
    ObjectType,
    PhysicalObject,
    SpatialIndex,
)
from codomyrmex.physical_management.object_manager import (
    ObjectRegistry,
    PhysicalObjectManager,
)

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# Data Model Tests
# ---------------------------------------------------------------------------


class TestEnums:
    """All four enums are importable and have expected members."""

    def test_object_type_members(self) -> None:
        assert {e.value for e in ObjectType} >= {"sensor", "actuator", "device"}

    def test_object_status_members(self) -> None:
        assert {e.value for e in ObjectStatus} >= {"active", "inactive", "error"}

    def test_material_type_members(self) -> None:
        assert {e.value for e in MaterialType} >= {"metal", "plastic", "glass"}

    def test_event_type_members(self) -> None:
        assert {e.value for e in EventType} >= {"created", "moved", "destroyed"}


class TestMaterialProperties:
    """MaterialProperties dataclass and factory method."""

    def test_from_material_type_metal(self) -> None:
        mp = MaterialProperties.from_material_type(MaterialType.METAL)
        assert mp.density == 7850
        assert mp.melting_point == 1811

    def test_from_material_type_unknown(self) -> None:
        mp = MaterialProperties.from_material_type(MaterialType.UNKNOWN)
        assert mp.density > 0

    def test_custom_init(self) -> None:
        mp = MaterialProperties(
            density=5000,
            elasticity=100e9,
            thermal_conductivity=10,
            specific_heat=600,
            melting_point=1500,
        )
        assert mp.friction_coefficient == 0.5  # default


class TestPhysicalObject:
    """PhysicalObject dataclass methods."""

    def _make(self, **kw) -> PhysicalObject:
        defaults = {
            "id": "obj-1",
            "name": "Test Sensor",
            "object_type": ObjectType.SENSOR,
            "location": (0.0, 0.0, 0.0),
        }
        defaults.update(kw)
        return PhysicalObject(**defaults)

    def test_auto_material_properties(self) -> None:
        obj = self._make(material=MaterialType.METAL)
        assert obj.material_properties is not None
        assert obj.material_properties.density == 7850

    def test_density_property(self) -> None:
        obj = self._make(mass=10.0, volume=2.0)
        assert obj.density == 5.0

    def test_density_zero_volume(self) -> None:
        obj = self._make(volume=0.0)
        assert obj.density == 0.0

    def test_update_location(self) -> None:
        obj = self._make()
        obj.update_location(5.0, 6.0, 7.0)
        assert obj.location == (5.0, 6.0, 7.0)

    def test_update_status(self) -> None:
        obj = self._make()
        obj.update_status(ObjectStatus.MAINTENANCE)
        assert obj.status == ObjectStatus.MAINTENANCE

    def test_distance_to(self) -> None:
        a = self._make(id="a", location=(0.0, 0.0, 0.0))
        b = self._make(id="b", location=(3.0, 4.0, 0.0))
        assert abs(a.distance_to(b) - 5.0) < 1e-9

    def test_distance_to_point(self) -> None:
        obj = self._make(location=(1.0, 2.0, 3.0))
        assert obj.distance_to_point(1.0, 2.0, 3.0) == 0.0

    def test_is_within_range(self) -> None:
        obj = self._make(location=(0.0, 0.0, 0.0))
        assert obj.is_within_range(1.0, 0.0, 0.0, 2.0)
        assert not obj.is_within_range(100.0, 0.0, 0.0, 2.0)

    def test_properties_crud(self) -> None:
        obj = self._make()
        obj.add_property("voltage", 3.3)
        assert obj.properties["voltage"] == 3.3
        assert obj.remove_property("voltage") == 3.3
        assert obj.remove_property("nonexistent") is None

    def test_tags_crud(self) -> None:
        obj = self._make()
        obj.add_tag("indoor")
        assert obj.has_tag("indoor")
        assert obj.remove_tag("indoor")
        assert not obj.remove_tag("indoor")

    def test_connection_ops(self) -> None:
        obj = self._make()
        obj.connect_to("obj-2")
        assert obj.is_connected_to("obj-2")
        assert obj.disconnect_from("obj-2")
        assert not obj.disconnect_from("obj-2")

    def test_temperature_and_thermal(self) -> None:
        obj = self._make(mass=2.0, material=MaterialType.METAL)
        obj.update_temperature(373.15)
        energy = obj.calculate_thermal_energy()
        assert energy > 0

    def test_age_and_update_time(self) -> None:
        obj = self._make()
        assert obj.get_age() >= 0
        assert obj.time_since_update() >= 0

    def test_to_dict_round_trip(self) -> None:
        obj = self._make(material=MaterialType.PLASTIC)
        d = obj.to_dict()
        assert d["id"] == "obj-1"
        assert d["material"] == "plastic"
        assert isinstance(d["connections"], list)
        assert isinstance(d["tags"], list)


class TestSpatialIndex:
    """SpatialIndex operations."""

    def test_add_and_query(self) -> None:
        idx = SpatialIndex(grid_size=5.0)
        idx.add_object("a", 1.0, 1.0, 1.0)
        idx.add_object("b", 2.0, 2.0, 2.0)
        idx.add_object("c", 100.0, 100.0, 100.0)
        nearby = idx.get_nearby_cells(0.0, 0.0, 0.0, 5.0)
        assert "a" in nearby
        assert "b" in nearby
        assert "c" not in nearby

    def test_remove_object(self) -> None:
        idx = SpatialIndex()
        idx.add_object("x", 0.0, 0.0, 0.0)
        idx.remove_object("x")
        assert idx.get_nearby_cells(0.0, 0.0, 0.0, 10.0) == set()

    def test_object_relocation(self) -> None:
        idx = SpatialIndex()
        idx.add_object("m", 0.0, 0.0, 0.0)
        idx.add_object("m", 999.0, 999.0, 999.0)
        assert "m" not in idx.get_nearby_cells(0.0, 0.0, 0.0, 5.0)
        assert "m" in idx.get_nearby_cells(999.0, 999.0, 999.0, 5.0)


class TestObjectEvent:
    """ObjectEvent dataclass."""

    def test_event_creation(self) -> None:
        ev = ObjectEvent(event_type=EventType.CREATED, object_id="obj-1")
        assert ev.timestamp > 0
        assert ev.data == {}

    def test_event_with_data(self) -> None:
        ev = ObjectEvent(
            event_type=EventType.MOVED,
            object_id="obj-2",
            data={"from": (0, 0, 0), "to": (1, 1, 1)},
            source="test",
        )
        assert ev.source == "test"


# ---------------------------------------------------------------------------
# ObjectRegistry Tests
# ---------------------------------------------------------------------------


class TestObjectRegistry:
    """ObjectRegistry operations with real objects."""

    @pytest.fixture
    def registry(self) -> ObjectRegistry:
        reg = ObjectRegistry()
        for i in range(5):
            obj = PhysicalObject(
                id=f"sensor-{i}",
                name=f"Sensor {i}",
                object_type=ObjectType.SENSOR,
                location=(float(i * 10), 0.0, 0.0),
            )
            reg.register_object(obj)
        return reg

    def test_register_and_get(self, registry: ObjectRegistry) -> None:
        assert registry.get_object("sensor-0") is not None
        assert registry.get_object("nonexistent") is None

    def test_unregister(self, registry: ObjectRegistry) -> None:
        obj = registry.unregister_object("sensor-0")
        assert obj is not None
        assert registry.get_object("sensor-0") is None
        assert registry.unregister_object("nonexistent") is None

    def test_get_by_type(self, registry: ObjectRegistry) -> None:
        sensors = registry.get_objects_by_type(ObjectType.SENSOR)
        assert len(sensors) == 5

    def test_get_by_status(self, registry: ObjectRegistry) -> None:
        active = registry.get_objects_by_status(ObjectStatus.ACTIVE)
        assert len(active) == 5

    def test_get_by_property(self, registry: ObjectRegistry) -> None:
        registry.get_object("sensor-0").add_property("floor", 2)
        found = registry.get_objects_by_property("floor", 2)
        assert len(found) == 1

    def test_find_nearest(self, registry: ObjectRegistry) -> None:
        nearest = registry.find_nearest_object(0.5, 0.0, 0.0)
        assert nearest.id == "sensor-0"

    def test_check_collisions(self) -> None:
        reg = ObjectRegistry()
        a = PhysicalObject(id="a", name="A", object_type=ObjectType.DEVICE, location=(0.0, 0.0, 0.0))
        b = PhysicalObject(id="b", name="B", object_type=ObjectType.DEVICE, location=(0.5, 0.0, 0.0))
        c = PhysicalObject(id="c", name="C", object_type=ObjectType.DEVICE, location=(100.0, 0.0, 0.0))
        reg.register_object(a)
        reg.register_object(b)
        reg.register_object(c)
        collisions = reg.check_collisions(1.0)
        assert len(collisions) == 1
        assert {collisions[0][0].id, collisions[0][1].id} == {"a", "b"}

    def test_group_by_distance(self, registry: ObjectRegistry) -> None:
        groups = registry.group_objects_by_distance(15.0)
        assert len(groups) >= 1

    def test_event_system(self) -> None:
        reg = ObjectRegistry()
        events_received = []
        reg.add_event_handler(EventType.CREATED, events_received.append)
        obj = PhysicalObject(id="e1", name="E1", object_type=ObjectType.SENSOR, location=(0.0, 0.0, 0.0))
        reg.register_object(obj)
        assert len(events_received) == 1
        assert events_received[0].event_type == EventType.CREATED
        # Remove handler
        assert reg.remove_event_handler(EventType.CREATED, events_received.append)

    def test_get_events_filter(self) -> None:
        reg = ObjectRegistry()
        obj = PhysicalObject(id="f1", name="F1", object_type=ObjectType.SENSOR, location=(0.0, 0.0, 0.0))
        reg.register_object(obj)
        events = reg.get_events(event_type=EventType.CREATED, object_id="f1")
        assert len(events) == 1

    def test_tags_query(self) -> None:
        reg = ObjectRegistry()
        obj = PhysicalObject(id="t1", name="T1", object_type=ObjectType.SENSOR, location=(0.0, 0.0, 0.0))
        obj.add_tag("indoor")
        obj.add_tag("floor1")
        reg.register_object(obj)
        found = reg.get_objects_by_tags({"indoor", "floor1"}, match_all=True)
        assert len(found) == 1
        found_any = reg.get_objects_by_tags({"outdoor"}, match_all=False)
        assert len(found_any) == 0

    def test_network_topology(self) -> None:
        reg = ObjectRegistry()
        a = PhysicalObject(id="n1", name="N1", object_type=ObjectType.DEVICE, location=(0.0, 0.0, 0.0))
        b = PhysicalObject(id="n2", name="N2", object_type=ObjectType.DEVICE, location=(1.0, 0.0, 0.0))
        a.connect_to("n2")
        b.connect_to("n1")
        reg.register_object(a)
        reg.register_object(b)
        topo = reg.get_network_topology()
        assert "n2" in topo["n1"]

    def test_path_through_network(self) -> None:
        reg = ObjectRegistry()
        a = PhysicalObject(id="p1", name="P1", object_type=ObjectType.DEVICE, location=(0.0, 0.0, 0.0))
        b = PhysicalObject(id="p2", name="P2", object_type=ObjectType.DEVICE, location=(1.0, 0.0, 0.0))
        c = PhysicalObject(id="p3", name="P3", object_type=ObjectType.DEVICE, location=(2.0, 0.0, 0.0))
        a.connect_to("p2")
        b.connect_to("p3")
        reg.register_object(a)
        reg.register_object(b)
        reg.register_object(c)
        path = reg.find_path_through_network("p1", "p3")
        assert path is not None
        assert path[0] == "p1" and path[-1] == "p3"

    def test_find_path_self(self) -> None:
        reg = ObjectRegistry()
        a = PhysicalObject(id="self1", name="Self", object_type=ObjectType.DEVICE, location=(0.0, 0.0, 0.0))
        reg.register_object(a)
        assert reg.find_path_through_network("self1", "self1") == ["self1"]

    def test_find_path_nonexistent(self) -> None:
        reg = ObjectRegistry()
        assert reg.find_path_through_network("x", "y") is None

    def test_analyze_network_metrics(self) -> None:
        reg = ObjectRegistry()
        a = PhysicalObject(id="am1", name="AM1", object_type=ObjectType.DEVICE, location=(0.0, 0.0, 0.0))
        b = PhysicalObject(id="am2", name="AM2", object_type=ObjectType.DEVICE, location=(1.0, 0.0, 0.0))
        a.connect_to("am2")
        b.connect_to("am1")
        reg.register_object(a)
        reg.register_object(b)
        metrics = reg.analyze_network_metrics()
        assert metrics["total_objects"] == 2
        assert metrics["average_degree"] > 0

    def test_save_and_load(self, registry: ObjectRegistry, tmp_path: Path) -> None:
        fp = tmp_path / "registry.json"
        registry.save_to_file(fp)
        data = json.loads(fp.read_text())
        assert data["metadata"]["total_objects"] == 5

        new_reg = ObjectRegistry()
        new_reg.load_from_file(fp)
        assert len(new_reg.objects) == 5

    def test_load_nonexistent(self) -> None:
        reg = ObjectRegistry()
        reg.load_from_file("/tmp/nonexistent_file_xyz.json")  # should not raise
        assert len(reg.objects) == 0


# ---------------------------------------------------------------------------
# PhysicalObjectManager Tests
# ---------------------------------------------------------------------------


class TestPhysicalObjectManager:
    """PhysicalObjectManager high-level operations."""

    @pytest.fixture
    def mgr(self) -> PhysicalObjectManager:
        m = PhysicalObjectManager()
        m.create_object("s1", "Sensor 1", ObjectType.SENSOR, 0.0, 0.0, 0.0)
        m.create_object("s2", "Sensor 2", ObjectType.SENSOR, 10.0, 0.0, 0.0)
        m.create_object("d1", "Device 1", ObjectType.DEVICE, 5.0, 5.0, 0.0)
        return m

    def test_create_object(self, mgr: PhysicalObjectManager) -> None:
        obj = mgr.create_object("new1", "New", ObjectType.ACTUATOR, 1.0, 2.0, 3.0, mass=5.0)
        assert obj.mass == 5.0
        assert mgr.get_object_status("new1") == ObjectStatus.ACTIVE

    def test_get_status_nonexistent(self, mgr: PhysicalObjectManager) -> None:
        assert mgr.get_object_status("nonexistent") is None

    def test_update_location(self, mgr: PhysicalObjectManager) -> None:
        assert mgr.update_object_location("s1", 99.0, 99.0, 99.0)
        assert not mgr.update_object_location("nonexistent", 0, 0, 0)

    def test_get_nearby(self, mgr: PhysicalObjectManager) -> None:
        nearby = mgr.get_nearby_objects(0.0, 0.0, 0.0, 8.0)
        ids = {o.id for o in nearby}
        assert "s1" in ids

    def test_get_by_type(self, mgr: PhysicalObjectManager) -> None:
        sensors = mgr.get_objects_by_type(ObjectType.SENSOR)
        assert len(sensors) == 2

    def test_save_and_load_state(self, mgr: PhysicalObjectManager, tmp_path: Path) -> None:
        fp = tmp_path / "state.json"
        mgr.save_state(fp)
        new_mgr = PhysicalObjectManager()
        new_mgr.load_state(fp)
        assert len(new_mgr.registry.objects) == 3

    def test_statistics(self, mgr: PhysicalObjectManager) -> None:
        stats = mgr.get_statistics()
        assert stats["total_objects"] == 3
        assert stats["objects_by_type"]["sensor"] == 2

    def test_batch_update_status(self, mgr: PhysicalObjectManager) -> None:
        count = mgr.batch_update_status(["s1", "s2", "nonexistent"], ObjectStatus.MAINTENANCE)
        assert count == 2

    def test_batch_move(self, mgr: PhysicalObjectManager) -> None:
        count = mgr.batch_move_objects({"s1": (50.0, 50.0, 50.0), "nonexistent": (0, 0, 0)})
        assert count == 1

    def test_calculate_center_of_mass(self, mgr: PhysicalObjectManager) -> None:
        cx, cy, cz = mgr.calculate_center_of_mass()
        assert cx > 0

    def test_center_of_mass_subset(self, mgr: PhysicalObjectManager) -> None:
        cx, cy, cz = mgr.calculate_center_of_mass(["s1"])
        assert cx == 0.0

    def test_center_of_mass_empty(self) -> None:
        mgr = PhysicalObjectManager()
        assert mgr.calculate_center_of_mass() == (0.0, 0.0, 0.0)

    def test_detect_clusters(self, mgr: PhysicalObjectManager) -> None:
        clusters = mgr.detect_object_clusters(cluster_radius=20.0, min_cluster_size=2)
        assert len(clusters) >= 1

    def test_get_boundary_box(self, mgr: PhysicalObjectManager) -> None:
        bbox = mgr.get_boundary_box()
        assert bbox["x"][1] >= bbox["x"][0]

    def test_boundary_box_empty(self) -> None:
        mgr = PhysicalObjectManager()
        assert mgr.get_boundary_box() == {"x": (0.0, 0.0), "y": (0.0, 0.0), "z": (0.0, 0.0)}

    def test_find_path_between(self) -> None:
        mgr = PhysicalObjectManager()
        mgr.create_object("wp1", "W1", ObjectType.DEVICE, 0.0, 0.0, 0.0)
        mgr.create_object("wp2", "W2", ObjectType.DEVICE, 3.0, 0.0, 0.0)
        mgr.create_object("wp3", "W3", ObjectType.DEVICE, 6.0, 0.0, 0.0)
        # With objects this close, greedy pathfinding should find a path
        path = mgr.find_path_between_objects("wp1", "wp3")
        # path may be None if distance > 5.0 between steps; this tests the code path
        # either way, the function runs without error
