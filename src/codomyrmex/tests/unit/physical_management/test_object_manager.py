"""Unit tests for physical_management.object_manager module.

Covers: enums, dataclasses (MaterialProperties, ObjectEvent, SpatialIndex,
PhysicalObject), ObjectRegistry, and PhysicalObjectManager.
Zero-mock policy: all objects are real instances.
"""

import json
import time

import pytest

from codomyrmex.physical_management.object_manager import (
    EventType,
    MaterialProperties,
    MaterialType,
    ObjectEvent,
    ObjectRegistry,
    ObjectStatus,
    ObjectType,
    PhysicalObject,
    PhysicalObjectManager,
    SpatialIndex,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_obj(
    obj_id: str = "obj-1",
    name: str = "TestSensor",
    obj_type: ObjectType = ObjectType.SENSOR,
    location: tuple = (0.0, 0.0, 0.0),
    status: ObjectStatus = ObjectStatus.ACTIVE,
    material: MaterialType = MaterialType.METAL,
    mass: float = 2.0,
    volume: float = 1.0,
    temperature: float = 300.0,
) -> PhysicalObject:
    return PhysicalObject(
        id=obj_id,
        name=name,
        object_type=obj_type,
        location=location,
        status=status,
        material=material,
        mass=mass,
        volume=volume,
        temperature=temperature,
    )


# ===================================================================
# Enum tests
# ===================================================================


@pytest.mark.unit
class TestEnums:
    """Verify all enum types are well-formed."""

    def test_object_type_values(self):
        assert ObjectType.SENSOR.value == "sensor"
        assert ObjectType.VEHICLE.value == "vehicle"
        assert len(ObjectType) == 6

    def test_object_status_values(self):
        assert ObjectStatus.ACTIVE.value == "active"
        assert ObjectStatus.CALIBRATING.value == "calibrating"
        assert len(ObjectStatus) == 8

    def test_material_type_values(self):
        assert MaterialType.METAL.value == "metal"
        assert MaterialType.UNKNOWN.value == "unknown"
        assert len(MaterialType) == 9

    def test_event_type_values(self):
        assert EventType.CREATED.value == "created"
        assert EventType.DISCONNECTED.value == "disconnected"
        assert len(EventType) == 8


# ===================================================================
# MaterialProperties tests
# ===================================================================


@pytest.mark.unit
class TestMaterialProperties:
    """Tests for MaterialProperties dataclass."""

    def test_direct_construction(self):
        mp = MaterialProperties(
            density=7850, elasticity=200e9, thermal_conductivity=45,
            specific_heat=500, melting_point=1811,
        )
        assert mp.density == 7850
        assert mp.friction_coefficient == 0.5  # default
        assert mp.restitution == 0.5

    def test_from_material_type_metal(self):
        mp = MaterialProperties.from_material_type(MaterialType.METAL)
        assert mp.density == 7850
        assert mp.elasticity == 200e9

    def test_from_material_type_all_variants(self):
        for mt in MaterialType:
            mp = MaterialProperties.from_material_type(mt)
            assert mp.density > 0
            assert mp.melting_point > 0

    def test_from_material_type_unknown_fallback(self):
        mp = MaterialProperties.from_material_type(MaterialType.UNKNOWN)
        assert mp.density == 1000


# ===================================================================
# ObjectEvent tests
# ===================================================================


@pytest.mark.unit
class TestObjectEvent:
    def test_construction_defaults(self):
        before = time.time()
        evt = ObjectEvent(event_type=EventType.CREATED, object_id="x")
        after = time.time()
        assert evt.event_type == EventType.CREATED
        assert evt.object_id == "x"
        assert before <= evt.timestamp <= after
        assert evt.data == {}
        assert evt.source is None

    def test_construction_with_data(self):
        evt = ObjectEvent(
            event_type=EventType.MOVED, object_id="y",
            data={"dx": 1}, source="test",
        )
        assert evt.data == {"dx": 1}
        assert evt.source == "test"


# ===================================================================
# SpatialIndex tests
# ===================================================================


@pytest.mark.unit
class TestSpatialIndex:
    def test_add_and_get_nearby(self):
        si = SpatialIndex(grid_size=10.0)
        si.add_object("a", 0.0, 0.0, 0.0)
        si.add_object("b", 5.0, 0.0, 0.0)
        si.add_object("c", 100.0, 100.0, 100.0)

        nearby = si.get_nearby_cells(0.0, 0.0, 0.0, 10.0)
        assert "a" in nearby
        assert "b" in nearby
        assert "c" not in nearby

    def test_move_object(self):
        si = SpatialIndex(grid_size=10.0)
        si.add_object("a", 0.0, 0.0, 0.0)
        # Move far away
        si.add_object("a", 200.0, 200.0, 200.0)
        nearby_origin = si.get_nearby_cells(0.0, 0.0, 0.0, 5.0)
        assert "a" not in nearby_origin
        nearby_new = si.get_nearby_cells(200.0, 200.0, 200.0, 5.0)
        assert "a" in nearby_new

    def test_remove_object(self):
        si = SpatialIndex(grid_size=10.0)
        si.add_object("a", 0.0, 0.0, 0.0)
        si.remove_object("a")
        nearby = si.get_nearby_cells(0.0, 0.0, 0.0, 50.0)
        assert "a" not in nearby

    def test_remove_nonexistent(self):
        si = SpatialIndex()
        si.remove_object("nope")  # should not raise


# ===================================================================
# PhysicalObject tests
# ===================================================================


@pytest.mark.unit
class TestPhysicalObject:
    def test_construction_defaults(self):
        obj = _make_obj()
        assert obj.id == "obj-1"
        assert obj.material_properties is not None
        assert obj.material_properties.density == 7850  # METAL

    def test_density_property(self):
        obj = _make_obj(mass=10.0, volume=2.0)
        assert obj.density == pytest.approx(5.0)

    def test_density_zero_volume(self):
        obj = _make_obj(volume=0.0)
        assert obj.density == 0.0

    def test_update_location(self):
        obj = _make_obj()
        obj.update_location(10.0, 20.0, 30.0)
        assert obj.location == (10.0, 20.0, 30.0)

    def test_update_status(self):
        obj = _make_obj()
        obj.update_status(ObjectStatus.MAINTENANCE)
        assert obj.status == ObjectStatus.MAINTENANCE

    def test_distance_to(self):
        a = _make_obj(obj_id="a", location=(0.0, 0.0, 0.0))
        b = _make_obj(obj_id="b", location=(3.0, 4.0, 0.0))
        assert a.distance_to(b) == pytest.approx(5.0)

    def test_distance_to_point(self):
        obj = _make_obj(location=(0.0, 0.0, 0.0))
        assert obj.distance_to_point(1.0, 0.0, 0.0) == pytest.approx(1.0)

    def test_is_within_range(self):
        obj = _make_obj(location=(0.0, 0.0, 0.0))
        assert obj.is_within_range(1.0, 0.0, 0.0, 2.0) is True
        assert obj.is_within_range(10.0, 0.0, 0.0, 2.0) is False

    def test_add_and_remove_property(self):
        obj = _make_obj()
        obj.add_property("color", "red")
        assert obj.properties["color"] == "red"
        removed = obj.remove_property("color")
        assert removed == "red"
        assert "color" not in obj.properties

    def test_remove_property_missing(self):
        obj = _make_obj()
        assert obj.remove_property("nope") is None

    def test_tags(self):
        obj = _make_obj()
        obj.add_tag("urgent")
        assert obj.has_tag("urgent")
        assert obj.remove_tag("urgent") is True
        assert obj.has_tag("urgent") is False
        assert obj.remove_tag("urgent") is False

    def test_connections(self):
        obj = _make_obj()
        obj.connect_to("other-1")
        assert obj.is_connected_to("other-1")
        assert obj.disconnect_from("other-1") is True
        assert obj.is_connected_to("other-1") is False
        assert obj.disconnect_from("other-1") is False

    def test_temperature(self):
        obj = _make_obj(temperature=300.0)
        obj.update_temperature(350.0)
        assert obj.temperature == 350.0

    def test_calculate_thermal_energy(self):
        obj = _make_obj(mass=2.0, temperature=373.15, material=MaterialType.METAL)
        energy = obj.calculate_thermal_energy()
        # mass * specific_heat * (T - 273.15) = 2 * 500 * 100 = 100000
        assert energy == pytest.approx(100000.0)

    def test_thermal_energy_no_material_props(self):
        obj = _make_obj()
        obj.material_properties = None
        assert obj.calculate_thermal_energy() == 0.0

    def test_get_age(self):
        obj = _make_obj()
        age = obj.get_age()
        assert age >= 0.0

    def test_time_since_update(self):
        obj = _make_obj()
        t = obj.time_since_update()
        assert t >= 0.0

    def test_to_dict(self):
        obj = _make_obj()
        obj.add_tag("test-tag")
        obj.connect_to("peer")
        d = obj.to_dict()
        assert d["id"] == "obj-1"
        assert d["object_type"] == "sensor"
        assert d["material"] == "metal"
        assert "test-tag" in d["tags"]
        assert "peer" in d["connections"]
        assert isinstance(d["location"], tuple) or isinstance(d["location"], list)


# ===================================================================
# ObjectRegistry tests
# ===================================================================


@pytest.mark.unit
class TestObjectRegistry:
    def _fresh_registry(self) -> ObjectRegistry:
        return ObjectRegistry(spatial_grid_size=10.0)

    def test_register_and_get(self):
        reg = self._fresh_registry()
        obj = _make_obj()
        reg.register_object(obj)
        assert reg.get_object("obj-1") is obj

    def test_unregister(self):
        reg = self._fresh_registry()
        obj = _make_obj()
        reg.register_object(obj)
        removed = reg.unregister_object("obj-1")
        assert removed is obj
        assert reg.get_object("obj-1") is None

    def test_unregister_nonexistent(self):
        reg = self._fresh_registry()
        assert reg.unregister_object("nope") is None

    def test_get_objects_by_type(self):
        reg = self._fresh_registry()
        reg.register_object(_make_obj(obj_id="s1", obj_type=ObjectType.SENSOR))
        reg.register_object(_make_obj(obj_id="d1", obj_type=ObjectType.DEVICE))
        sensors = reg.get_objects_by_type(ObjectType.SENSOR)
        assert len(sensors) == 1
        assert sensors[0].id == "s1"

    def test_get_objects_by_status(self):
        reg = self._fresh_registry()
        reg.register_object(_make_obj(obj_id="a", status=ObjectStatus.ACTIVE))
        reg.register_object(_make_obj(obj_id="b", status=ObjectStatus.INACTIVE))
        active = reg.get_objects_by_status(ObjectStatus.ACTIVE)
        assert len(active) == 1

    def test_get_objects_by_property(self):
        reg = self._fresh_registry()
        obj = _make_obj()
        obj.add_property("color", "blue")
        reg.register_object(obj)
        found = reg.get_objects_by_property("color", "blue")
        assert len(found) == 1

    def test_get_objects_in_area(self):
        reg = self._fresh_registry()
        reg.register_object(_make_obj(obj_id="near", location=(0.5, 0.5, 0.5)))
        reg.register_object(_make_obj(obj_id="far", location=(100.0, 100.0, 100.0)))
        nearby = reg.get_objects_in_area(0.0, 0.0, 0.0, 2.0)
        ids = [o.id for o in nearby]
        assert "near" in ids
        assert "far" not in ids

    def test_find_nearest_object(self):
        reg = self._fresh_registry()
        reg.register_object(_make_obj(obj_id="a", location=(1.0, 0.0, 0.0)))
        reg.register_object(_make_obj(obj_id="b", location=(10.0, 0.0, 0.0)))
        nearest = reg.find_nearest_object(0.0, 0.0, 0.0)
        assert nearest is not None
        assert nearest.id == "a"

    def test_find_nearest_object_by_type(self):
        reg = self._fresh_registry()
        reg.register_object(
            _make_obj(obj_id="s1", location=(5.0, 0.0, 0.0), obj_type=ObjectType.SENSOR)
        )
        reg.register_object(
            _make_obj(obj_id="d1", location=(1.0, 0.0, 0.0), obj_type=ObjectType.DEVICE)
        )
        nearest_sensor = reg.find_nearest_object(0.0, 0.0, 0.0, ObjectType.SENSOR)
        assert nearest_sensor is not None
        assert nearest_sensor.id == "s1"

    def test_find_nearest_object_empty(self):
        reg = self._fresh_registry()
        assert reg.find_nearest_object(0.0, 0.0, 0.0) is None

    def test_check_collisions(self):
        reg = self._fresh_registry()
        reg.register_object(_make_obj(obj_id="a", location=(0.0, 0.0, 0.0)))
        reg.register_object(_make_obj(obj_id="b", location=(0.5, 0.0, 0.0)))
        reg.register_object(_make_obj(obj_id="c", location=(100.0, 0.0, 0.0)))
        collisions = reg.check_collisions(collision_distance=1.0)
        assert len(collisions) == 1
        pair_ids = {collisions[0][0].id, collisions[0][1].id}
        assert pair_ids == {"a", "b"}

    def test_group_objects_by_distance(self):
        reg = self._fresh_registry()
        reg.register_object(_make_obj(obj_id="a", location=(0.0, 0.0, 0.0)))
        reg.register_object(_make_obj(obj_id="b", location=(1.0, 0.0, 0.0)))
        reg.register_object(_make_obj(obj_id="c", location=(100.0, 0.0, 0.0)))
        groups = reg.group_objects_by_distance(max_group_distance=5.0)
        assert len(groups) == 2
        group_sizes = sorted(len(g) for g in groups)
        assert group_sizes == [1, 2]

    def test_event_handler(self):
        reg = self._fresh_registry()
        captured = []
        reg.add_event_handler(EventType.CREATED, lambda e: captured.append(e))
        reg.register_object(_make_obj())
        assert len(captured) == 1
        assert captured[0].event_type == EventType.CREATED

    def test_remove_event_handler(self):
        reg = self._fresh_registry()
        handler = lambda e: None  # noqa: E731
        reg.add_event_handler(EventType.CREATED, handler)
        assert reg.remove_event_handler(EventType.CREATED, handler) is True
        assert reg.remove_event_handler(EventType.CREATED, handler) is False

    def test_event_history_limit(self):
        reg = self._fresh_registry()
        reg.max_event_history = 5
        for i in range(10):
            reg.register_object(_make_obj(obj_id=f"obj-{i}"))
        assert len(reg.event_history) <= 5

    def test_get_events_filters(self):
        reg = self._fresh_registry()
        reg.register_object(_make_obj(obj_id="a"))
        reg.register_object(_make_obj(obj_id="b"))
        # Filter by type
        created = reg.get_events(event_type=EventType.CREATED)
        assert len(created) == 2
        # Filter by object_id
        a_events = reg.get_events(object_id="a")
        assert len(a_events) == 1
        # Filter by since (future timestamp)
        future_events = reg.get_events(since=time.time() + 1000)
        assert len(future_events) == 0

    def test_get_objects_by_tags_match_all(self):
        reg = self._fresh_registry()
        obj = _make_obj()
        obj.add_tag("urgent")
        obj.add_tag("outdoor")
        reg.register_object(obj)
        found = reg.get_objects_by_tags({"urgent", "outdoor"}, match_all=True)
        assert len(found) == 1
        not_found = reg.get_objects_by_tags({"urgent", "missing"}, match_all=True)
        assert len(not_found) == 0

    def test_get_objects_by_tags_match_any(self):
        reg = self._fresh_registry()
        obj = _make_obj()
        obj.add_tag("urgent")
        reg.register_object(obj)
        found = reg.get_objects_by_tags({"urgent", "missing"}, match_all=False)
        assert len(found) == 1

    def test_get_network_topology(self):
        reg = self._fresh_registry()
        obj_a = _make_obj(obj_id="a")
        obj_b = _make_obj(obj_id="b")
        obj_a.connect_to("b")
        reg.register_object(obj_a)
        reg.register_object(obj_b)
        topo = reg.get_network_topology()
        assert "b" in topo["a"]
        assert topo["b"] == []

    def test_find_path_through_network(self):
        reg = self._fresh_registry()
        obj_a = _make_obj(obj_id="a")
        obj_b = _make_obj(obj_id="b")
        obj_c = _make_obj(obj_id="c")
        obj_a.connect_to("b")
        obj_b.connect_to("c")
        reg.register_object(obj_a)
        reg.register_object(obj_b)
        reg.register_object(obj_c)
        path = reg.find_path_through_network("a", "c")
        assert path is not None
        assert path[0] == "a"
        assert path[-1] == "c"

    def test_find_path_same_start_end(self):
        reg = self._fresh_registry()
        reg.register_object(_make_obj(obj_id="a"))
        path = reg.find_path_through_network("a", "a")
        assert path == ["a"]

    def test_find_path_no_route(self):
        reg = self._fresh_registry()
        reg.register_object(_make_obj(obj_id="a"))
        reg.register_object(_make_obj(obj_id="b"))
        # no connections
        path = reg.find_path_through_network("a", "b")
        assert path is None

    def test_find_path_missing_object(self):
        reg = self._fresh_registry()
        assert reg.find_path_through_network("nope", "also-nope") is None

    def test_analyze_network_metrics_empty(self):
        reg = self._fresh_registry()
        metrics = reg.analyze_network_metrics()
        assert metrics["total_objects"] == 0
        assert metrics["average_degree"] == 0

    def test_analyze_network_metrics_with_objects(self):
        reg = self._fresh_registry()
        a = _make_obj(obj_id="a")
        b = _make_obj(obj_id="b")
        c = _make_obj(obj_id="c")
        a.connect_to("b")
        a.connect_to("c")
        b.connect_to("a")
        b.connect_to("c")
        c.connect_to("a")
        c.connect_to("b")
        reg.register_object(a)
        reg.register_object(b)
        reg.register_object(c)
        metrics = reg.analyze_network_metrics()
        assert metrics["total_objects"] == 3
        assert metrics["max_degree"] == 2
        assert metrics["average_clustering"] > 0

    def test_save_and_load(self, tmp_path):
        reg = self._fresh_registry()
        reg.register_object(_make_obj(obj_id="s1", location=(1.0, 2.0, 3.0)))
        file_path = tmp_path / "registry.json"
        reg.save_to_file(file_path)

        reg2 = ObjectRegistry()
        reg2.load_from_file(file_path)
        loaded = reg2.get_object("s1")
        assert loaded is not None
        assert loaded.name == "TestSensor"
        assert loaded.location == (1.0, 2.0, 3.0)

    def test_load_nonexistent_file(self, tmp_path):
        reg = self._fresh_registry()
        reg.load_from_file(tmp_path / "does_not_exist.json")
        assert len(reg.objects) == 0

    def test_save_file_content(self, tmp_path):
        reg = self._fresh_registry()
        reg.register_object(_make_obj())
        fp = tmp_path / "out.json"
        reg.save_to_file(fp)
        data = json.loads(fp.read_text())
        assert "objects" in data
        assert "metadata" in data
        assert data["metadata"]["total_objects"] == 1

    def test_event_handler_exception_does_not_crash(self):
        reg = self._fresh_registry()

        def bad_handler(event):
            raise RuntimeError("boom")

        reg.add_event_handler(EventType.CREATED, bad_handler)
        # Should not raise
        reg.register_object(_make_obj())
        assert len(reg.objects) == 1


# ===================================================================
# PhysicalObjectManager tests
# ===================================================================


@pytest.mark.unit
class TestPhysicalObjectManager:
    def _fresh_manager(self) -> PhysicalObjectManager:
        return PhysicalObjectManager()

    def test_init(self):
        mgr = self._fresh_manager()
        assert mgr.registry is not None
        assert len(mgr._active_simulations) == 0

    def test_create_object(self):
        mgr = self._fresh_manager()
        obj = mgr.create_object(
            "t1", "Thermometer", ObjectType.SENSOR, 1.0, 2.0, 3.0,
            material=MaterialType.GLASS, mass=0.5,
        )
        assert obj.id == "t1"
        assert obj.location == (1.0, 2.0, 3.0)
        assert obj.material == MaterialType.GLASS
        assert mgr.registry.get_object("t1") is obj

    def test_get_object_status(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.DEVICE, 0, 0, 0)
        assert mgr.get_object_status("a") == ObjectStatus.ACTIVE
        assert mgr.get_object_status("missing") is None

    def test_update_object_location(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.DEVICE, 0, 0, 0)
        assert mgr.update_object_location("a", 5.0, 6.0, 7.0) is True
        obj = mgr.registry.get_object("a")
        assert obj.location == (5.0, 6.0, 7.0)

    def test_update_location_nonexistent(self):
        mgr = self._fresh_manager()
        assert mgr.update_object_location("nope", 1, 2, 3) is False

    def test_get_nearby_objects(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.SENSOR, 0.0, 0.0, 0.0)
        mgr.create_object("b", "B", ObjectType.SENSOR, 0.5, 0.0, 0.0)
        mgr.create_object("c", "C", ObjectType.SENSOR, 50.0, 50.0, 50.0)
        nearby = mgr.get_nearby_objects(0.0, 0.0, 0.0, 2.0)
        ids = [o.id for o in nearby]
        assert "a" in ids
        assert "b" in ids

    def test_get_objects_by_type(self):
        mgr = self._fresh_manager()
        mgr.create_object("s1", "S1", ObjectType.SENSOR, 0, 0, 0)
        mgr.create_object("d1", "D1", ObjectType.DEVICE, 0, 0, 0)
        sensors = mgr.get_objects_by_type(ObjectType.SENSOR)
        assert len(sensors) == 1

    def test_save_and_load_state(self, tmp_path):
        mgr = self._fresh_manager()
        mgr.create_object("x", "X", ObjectType.VEHICLE, 10, 20, 30)
        fp = tmp_path / "state.json"
        mgr.save_state(fp)

        mgr2 = PhysicalObjectManager()
        mgr2.load_state(fp)
        obj = mgr2.registry.get_object("x")
        assert obj is not None
        assert obj.object_type == ObjectType.VEHICLE

    def test_get_statistics(self):
        mgr = self._fresh_manager()
        mgr.create_object("s1", "S", ObjectType.SENSOR, 0, 0, 0)
        mgr.create_object("d1", "D", ObjectType.DEVICE, 0, 0, 0)
        stats = mgr.get_statistics()
        assert stats["total_objects"] == 2
        assert stats["objects_by_type"]["sensor"] == 1
        assert stats["objects_by_type"]["device"] == 1
        assert stats["active_simulations"] == 0
        assert stats["objects_by_status"]["active"] == 2

    def test_batch_update_status(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.SENSOR, 0, 0, 0)
        mgr.create_object("b", "B", ObjectType.SENSOR, 0, 0, 0)
        count = mgr.batch_update_status(["a", "b", "missing"], ObjectStatus.MAINTENANCE)
        assert count == 2
        assert mgr.get_object_status("a") == ObjectStatus.MAINTENANCE
        assert mgr.get_object_status("b") == ObjectStatus.MAINTENANCE

    def test_batch_move_objects(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.SENSOR, 0, 0, 0)
        mgr.create_object("b", "B", ObjectType.SENSOR, 0, 0, 0)
        moves = {"a": (1.0, 2.0, 3.0), "b": (4.0, 5.0, 6.0), "missing": (0, 0, 0)}
        count = mgr.batch_move_objects(moves)
        assert count == 2
        assert mgr.registry.get_object("a").location == (1.0, 2.0, 3.0)

    def test_calculate_center_of_mass_all(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.SENSOR, 0, 0, 0)
        mgr.create_object("b", "B", ObjectType.SENSOR, 10, 0, 0)
        cx, cy, cz = mgr.calculate_center_of_mass()
        assert cx == pytest.approx(5.0)
        assert cy == pytest.approx(0.0)

    def test_calculate_center_of_mass_subset(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.SENSOR, 0, 0, 0)
        mgr.create_object("b", "B", ObjectType.SENSOR, 10, 0, 0)
        mgr.create_object("c", "C", ObjectType.SENSOR, 100, 0, 0)
        cx, _, _ = mgr.calculate_center_of_mass(["a", "b"])
        assert cx == pytest.approx(5.0)

    def test_calculate_center_of_mass_empty(self):
        mgr = self._fresh_manager()
        assert mgr.calculate_center_of_mass() == (0.0, 0.0, 0.0)

    def test_calculate_center_of_mass_missing_ids(self):
        mgr = self._fresh_manager()
        assert mgr.calculate_center_of_mass(["nope"]) == (0.0, 0.0, 0.0)

    def test_detect_object_clusters(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.SENSOR, 0, 0, 0)
        mgr.create_object("b", "B", ObjectType.SENSOR, 1, 0, 0)
        mgr.create_object("c", "C", ObjectType.SENSOR, 100, 0, 0)
        clusters = mgr.detect_object_clusters(cluster_radius=3.0, min_cluster_size=2)
        assert len(clusters) == 1
        assert len(clusters[0]) == 2

    def test_get_boundary_box(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.SENSOR, -5, 0, 10)
        mgr.create_object("b", "B", ObjectType.SENSOR, 5, 20, -10)
        bb = mgr.get_boundary_box()
        assert bb["x"] == (-5.0, 5.0)
        assert bb["y"] == (0.0, 20.0)
        assert bb["z"] == (-10.0, 10.0)

    def test_get_boundary_box_empty(self):
        mgr = self._fresh_manager()
        bb = mgr.get_boundary_box()
        assert bb == {"x": (0.0, 0.0), "y": (0.0, 0.0), "z": (0.0, 0.0)}

    def test_get_boundary_box_subset(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.SENSOR, 0, 0, 0)
        mgr.create_object("b", "B", ObjectType.SENSOR, 10, 10, 10)
        mgr.create_object("c", "C", ObjectType.SENSOR, 100, 100, 100)
        bb = mgr.get_boundary_box(["a", "b"])
        assert bb["x"] == (0.0, 10.0)

    def test_find_path_between_close_objects(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.SENSOR, 0, 0, 0)
        mgr.create_object("b", "B", ObjectType.SENSOR, 0.5, 0, 0)
        path = mgr.find_path_between_objects("a", "b")
        assert path is not None
        assert path[0].id == "a"
        assert path[-1].id == "b"

    def test_find_path_missing_objects(self):
        mgr = self._fresh_manager()
        assert mgr.find_path_between_objects("x", "y") is None

    def test_find_path_no_route(self):
        mgr = self._fresh_manager()
        mgr.create_object("a", "A", ObjectType.SENSOR, 0, 0, 0)
        mgr.create_object("b", "B", ObjectType.SENSOR, 1000, 1000, 1000)
        path = mgr.find_path_between_objects("a", "b", max_steps=2)
        # Objects too far apart with no waypoints
        assert path is None
