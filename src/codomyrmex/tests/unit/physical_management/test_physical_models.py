"""Tests for physical_management.models."""

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


class TestObjectType:
    def test_all_values(self):
        values = {t.value for t in ObjectType}
        assert "sensor" in values
        assert "actuator" in values
        assert "device" in values
        assert "container" in values
        assert "vehicle" in values
        assert "structure" in values


class TestObjectStatus:
    def test_all_values(self):
        values = {s.value for s in ObjectStatus}
        assert "active" in values
        assert "inactive" in values
        assert "maintenance" in values
        assert "error" in values
        assert "offline" in values

    def test_additional_states(self):
        values = {s.value for s in ObjectStatus}
        assert "initializing" in values
        assert "shutting_down" in values
        assert "calibrating" in values


class TestMaterialType:
    def test_all_values(self):
        values = {m.value for m in MaterialType}
        assert "metal" in values
        assert "plastic" in values
        assert "wood" in values
        assert "unknown" in values

    def test_count(self):
        assert len(MaterialType) >= 9


class TestEventType:
    def test_all_values(self):
        values = {e.value for e in EventType}
        assert "created" in values
        assert "moved" in values
        assert "status_changed" in values
        assert "destroyed" in values


class TestMaterialProperties:
    def test_construction(self):
        mp = MaterialProperties(
            density=7850,
            elasticity=200e9,
            thermal_conductivity=45,
            specific_heat=500,
            melting_point=1811,
        )
        assert mp.density == 7850
        assert mp.friction_coefficient == 0.5
        assert mp.restitution == 0.5

    def test_from_material_type_metal(self):
        mp = MaterialProperties.from_material_type(MaterialType.METAL)
        assert mp.density == 7850
        assert mp.friction_coefficient == 0.4

    def test_from_material_type_plastic(self):
        mp = MaterialProperties.from_material_type(MaterialType.PLASTIC)
        assert mp.density == 1200

    def test_from_material_type_glass(self):
        mp = MaterialProperties.from_material_type(MaterialType.GLASS)
        assert mp.density == 2500

    def test_from_material_type_unknown(self):
        mp = MaterialProperties.from_material_type(MaterialType.UNKNOWN)
        assert mp is not None
        assert mp.density > 0

    def test_from_all_material_types(self):
        for mat_type in MaterialType:
            mp = MaterialProperties.from_material_type(mat_type)
            assert mp is not None
            assert mp.density > 0


class TestObjectEvent:
    def test_construction(self):
        e = ObjectEvent(event_type=EventType.CREATED, object_id="obj-1")
        assert e.event_type == EventType.CREATED
        assert e.object_id == "obj-1"
        assert e.data == {}
        assert e.source is None

    def test_timestamp_auto_set(self):
        e = ObjectEvent(event_type=EventType.MOVED, object_id="obj-2")
        assert e.timestamp > 0

    def test_with_data(self):
        e = ObjectEvent(
            event_type=EventType.PROPERTY_UPDATED,
            object_id="obj-3",
            data={"key": "value"},
            source="system",
        )
        assert e.data["key"] == "value"
        assert e.source == "system"

    def test_independent_default_data(self):
        e1 = ObjectEvent(event_type=EventType.CREATED, object_id="a")
        e2 = ObjectEvent(event_type=EventType.CREATED, object_id="b")
        e1.data["x"] = 1
        assert e2.data == {}


class TestSpatialIndex:
    def test_empty_index(self):
        si = SpatialIndex()
        assert si.grid_size == 10.0

    def test_add_object(self):
        si = SpatialIndex()
        si.add_object("obj-1", 0.0, 0.0, 0.0)
        # Object is within 1 unit of origin
        nearby = si.get_nearby_cells(0.0, 0.0, 0.0, 1.0)
        assert "obj-1" in nearby

    def test_remove_object(self):
        si = SpatialIndex()
        si.add_object("obj-1", 0.0, 0.0, 0.0)
        si.remove_object("obj-1")
        nearby = si.get_nearby_cells(0.0, 0.0, 0.0, 1.0)
        assert "obj-1" not in nearby

    def test_remove_nonexistent_noop(self):
        si = SpatialIndex()
        si.remove_object("nonexistent")  # Should not raise

    def test_get_nearby_cells_within_radius(self):
        si = SpatialIndex()
        si.add_object("near", 1.0, 0.0, 0.0)
        si.add_object("far", 100.0, 0.0, 0.0)
        nearby = si.get_nearby_cells(0.0, 0.0, 0.0, 5.0)
        assert "near" in nearby
        assert "far" not in nearby

    def test_move_object_updates_location(self):
        si = SpatialIndex()
        si.add_object("moving", 0.0, 0.0, 0.0)
        si.add_object("moving", 100.0, 100.0, 100.0)  # Re-add updates location
        # Not in origin anymore
        nearby_origin = si.get_nearby_cells(0.0, 0.0, 0.0, 1.0)
        assert "moving" not in nearby_origin

    def test_multiple_objects_same_cell(self):
        si = SpatialIndex()
        si.add_object("a", 1.0, 0.0, 0.0)
        si.add_object("b", 2.0, 0.0, 0.0)
        nearby = si.get_nearby_cells(0.0, 0.0, 0.0, 5.0)
        assert "a" in nearby
        assert "b" in nearby


class TestPhysicalObject:
    def _make_object(self, **kwargs) -> PhysicalObject:
        defaults = {
            "id": "obj-1",
            "name": "Sensor A",
            "object_type": ObjectType.SENSOR,
            "location": (0.0, 0.0, 0.0),
        }
        defaults.update(kwargs)
        return PhysicalObject(**defaults)

    def test_construction(self):
        obj = self._make_object()
        assert obj.id == "obj-1"
        assert obj.name == "Sensor A"
        assert obj.status == ObjectStatus.ACTIVE

    def test_material_properties_auto_initialized(self):
        obj = self._make_object(material=MaterialType.METAL)
        assert obj.material_properties is not None
        assert obj.material_properties.density == 7850

    def test_density_property(self):
        obj = self._make_object(mass=10.0, volume=2.0)
        assert obj.density == 5.0

    def test_density_zero_volume(self):
        obj = self._make_object(mass=10.0, volume=0.0)
        assert obj.density == 0.0

    def test_update_location(self):
        obj = self._make_object()
        obj.update_location(1.0, 2.0, 3.0)
        assert obj.location == (1.0, 2.0, 3.0)

    def test_update_status(self):
        obj = self._make_object()
        obj.update_status(ObjectStatus.MAINTENANCE)
        assert obj.status == ObjectStatus.MAINTENANCE

    def test_distance_to(self):
        obj1 = self._make_object(id="a", location=(0.0, 0.0, 0.0))
        obj2 = self._make_object(id="b", location=(3.0, 4.0, 0.0))
        assert abs(obj1.distance_to(obj2) - 5.0) < 1e-9

    def test_distance_to_point(self):
        obj = self._make_object(location=(0.0, 0.0, 0.0))
        assert abs(obj.distance_to_point(3.0, 4.0, 0.0) - 5.0) < 1e-9

    def test_is_within_range_true(self):
        obj = self._make_object(location=(0.0, 0.0, 0.0))
        assert obj.is_within_range(3.0, 4.0, 0.0, 10.0) is True

    def test_is_within_range_false(self):
        obj = self._make_object(location=(0.0, 0.0, 0.0))
        assert obj.is_within_range(100.0, 0.0, 0.0, 10.0) is False

    def test_add_property(self):
        obj = self._make_object()
        obj.add_property("serial", "SN-001")
        assert obj.properties["serial"] == "SN-001"

    def test_remove_property_existing(self):
        obj = self._make_object()
        obj.add_property("temp", 25.0)
        val = obj.remove_property("temp")
        assert val == 25.0
        assert "temp" not in obj.properties

    def test_remove_property_missing(self):
        obj = self._make_object()
        result = obj.remove_property("nonexistent")
        assert result is None

    def test_tags(self):
        obj = self._make_object()
        obj.add_tag("outdoor")
        assert obj.has_tag("outdoor") is True
        result = obj.remove_tag("outdoor")
        assert result is True
        assert obj.has_tag("outdoor") is False

    def test_remove_tag_missing(self):
        obj = self._make_object()
        result = obj.remove_tag("nonexistent")
        assert result is False

    def test_connections(self):
        obj = self._make_object()
        obj.connect_to("obj-2")
        assert obj.is_connected_to("obj-2") is True
        result = obj.disconnect_from("obj-2")
        assert result is True
        assert obj.is_connected_to("obj-2") is False

    def test_disconnect_missing(self):
        obj = self._make_object()
        assert obj.disconnect_from("nonexistent") is False

    def test_calculate_thermal_energy(self):
        obj = self._make_object(
            material=MaterialType.METAL, mass=1.0, temperature=373.15
        )
        energy = obj.calculate_thermal_energy()
        assert energy > 0  # 1kg metal, above 0°C

    def test_get_age_positive(self):
        obj = self._make_object()
        age = obj.get_age()
        assert age >= 0.0

    def test_time_since_update_positive(self):
        obj = self._make_object()
        t = obj.time_since_update()
        assert t >= 0.0

    def test_to_dict(self):
        obj = self._make_object(id="obj-99", name="Robot")
        d = obj.to_dict()
        assert d["id"] == "obj-99"
        assert d["name"] == "Robot"
        assert "object_type" in d
        assert "location" in d
        assert "status" in d
        assert "tags" in d
        assert "connections" in d

    def test_to_dict_serializes_enum_values(self):
        obj = self._make_object(
            object_type=ObjectType.VEHICLE, status=ObjectStatus.OFFLINE
        )
        d = obj.to_dict()
        assert d["object_type"] == "vehicle"
        assert d["status"] == "offline"

    def test_to_dict_tags_as_list(self):
        obj = self._make_object()
        obj.add_tag("alpha")
        d = obj.to_dict()
        assert isinstance(d["tags"], list)
        assert "alpha" in d["tags"]

    def test_independent_default_properties(self):
        obj1 = self._make_object(id="a")
        obj2 = self._make_object(id="b")
        obj1.properties["x"] = 1
        assert obj2.properties == {}
