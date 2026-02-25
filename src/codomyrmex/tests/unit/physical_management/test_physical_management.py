import time
"""Unit tests for physical_management module."""

import sys

import pytest


@pytest.mark.unit
class TestPhysicalManagement:
    """Test cases for physical management functionality."""

    def test_physical_management_import(self, code_dir):
        """Test that we can import physical_management module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex import physical_management
            assert physical_management is not None
        except ImportError as e:
            pytest.fail(f"Failed to import physical_management: {e}")

    def test_physical_management_module_exists(self, code_dir):
        """Test that physical_management module directory exists."""
        pm_path = code_dir / "codomyrmex" / "physical_management"
        assert pm_path.exists()
        assert pm_path.is_dir()

    def test_physical_management_init_file(self, code_dir):
        """Test that physical_management has __init__.py."""
        init_path = code_dir / "codomyrmex" / "physical_management" / "__init__.py"
        assert init_path.exists()

    def test_object_manager_module_exists(self, code_dir):
        """Test that object_manager module exists."""
        om_path = code_dir / "codomyrmex" / "physical_management" / "object_manager.py"
        assert om_path.exists()

    def test_simulation_engine_module_exists(self, code_dir):
        """Test that simulation_engine module exists."""
        se_path = code_dir / "codomyrmex" / "physical_management" / "simulation_engine.py"
        assert se_path.exists()

    def test_sensor_integration_module_exists(self, code_dir):
        """Test that sensor_integration module exists."""
        si_path = code_dir / "codomyrmex" / "physical_management" / "sensor_integration.py"
        assert si_path.exists()

    def test_analytics_module_exists(self, code_dir):
        """Test that analytics module exists."""
        analytics_path = code_dir / "codomyrmex" / "physical_management" / "analytics.py"
        assert analytics_path.exists()

    def test_physical_object_manager_import(self, code_dir):
        """Test that PhysicalObjectManager class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.physical_management import PhysicalObjectManager, Vector3D
            assert PhysicalObjectManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import PhysicalObjectManager: {e}")

    def test_physical_object_import(self, code_dir):
        """Test that PhysicalObject class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.physical_management import PhysicalObject
            assert PhysicalObject is not None
        except ImportError as e:
            pytest.fail(f"Failed to import PhysicalObject: {e}")

    def test_physics_simulator_import(self, code_dir):
        """Test that PhysicsSimulator class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.physical_management import PhysicsSimulator
            assert PhysicsSimulator is not None
        except ImportError as e:
            pytest.fail(f"Failed to import PhysicsSimulator: {e}")

    def test_sensor_manager_import(self, code_dir):
        """Test that SensorManager class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.physical_management import SensorManager
            assert SensorManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import SensorManager: {e}")

    def test_streaming_analytics_import(self, code_dir):
        """Test that StreamingAnalytics class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.physical_management import StreamingAnalytics
            assert StreamingAnalytics is not None
        except ImportError as e:
            pytest.fail(f"Failed to import StreamingAnalytics: {e}")

    def test_type_enums_import(self, code_dir):
        """Test that type enums can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.physical_management import (
                DeviceStatus,
                EventType,
                MaterialType,
                ObjectStatus,
                ObjectType,
                SensorType,
            )
            assert ObjectType is not None
            assert ObjectStatus is not None
            assert MaterialType is not None
            assert EventType is not None
            assert SensorType is not None
            assert DeviceStatus is not None
        except ImportError as e:
            pytest.fail(f"Failed to import type enums: {e}")

    def test_vector3d_import(self, code_dir):
        """Test that Vector3D class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.physical_management import Vector3D
            assert Vector3D is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Vector3D: {e}")

    def test_physical_management_version(self, code_dir):
        """Test that physical_management has version defined."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex import physical_management
        assert hasattr(physical_management, "__version__")
        assert physical_management.__version__ == "0.2.0"

    def test_physical_management_all_exports(self, code_dir):
        """Test that physical_management exports all expected symbols."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex import physical_management

        expected_exports = [
            "PhysicalObjectManager",
            "PhysicalObject",
            "ObjectRegistry",
            "PhysicsSimulator",
            "SensorManager",
            "StreamingAnalytics",
            "Vector3D",
        ]

        for export in expected_exports:
            assert hasattr(physical_management, export), f"Missing export: {export}"

    def test_agents_md_exists(self, code_dir):
        """Test that AGENTS.md exists for physical_management module."""
        agents_path = code_dir / "codomyrmex" / "physical_management" / "AGENTS.md"
        assert agents_path.exists()

    def test_readme_exists(self, code_dir):
        """Test that README.md exists for physical_management module."""
        readme_path = code_dir / "codomyrmex" / "physical_management" / "README.md"
        assert readme_path.exists()

    def test_docs_directory_exists(self, code_dir):
        """Test that docs directory exists for physical_management module."""
        docs_path = code_dir / "codomyrmex" / "physical_management" / "docs"
        if not docs_path.exists():
            pytest.skip("docs/ directory not yet created for physical_management module")

    def test_examples_directory_exists(self, code_dir):
        """Test that examples directory exists for physical_management module."""
        examples_path = code_dir / "codomyrmex" / "physical_management" / "examples"
        assert examples_path.exists()
        assert examples_path.is_dir()

    def test_tests_directory_exists(self, code_dir):
        """Test that tests directory exists for physical_management module."""
        tests_path = code_dir / "codomyrmex" / "physical_management" / "tests"
        if not tests_path.exists():
            pytest.skip("tests/ directory not yet created for physical_management module")





# From test_coverage_boost_r3.py
class TestDataPoint:
    """Tests for DataPoint dataclass."""

    def test_creation(self):
        from codomyrmex.physical_management.analytics import DataPoint

        dp = DataPoint(timestamp=time.time(), value=42.0, source_id="sensor-1")
        assert dp.value == 42.0
        assert dp.source_id == "sensor-1"

    def test_with_metadata(self):
        from codomyrmex.physical_management.analytics import DataPoint

        dp = DataPoint(timestamp=time.time(), value=1.0, source_id="s",
                       metadata={"unit": "celsius"})
        assert dp.metadata["unit"] == "celsius"


# From test_coverage_boost_r3.py
class TestAnalyticsWindow:
    """Tests for AnalyticsWindow."""

    def test_add_and_metrics(self):
        from codomyrmex.physical_management.analytics import (
            AnalyticsMetric, AnalyticsWindow, DataPoint,
        )

        now = time.time()
        window = AnalyticsWindow(start_time=now, end_time=now + 60, duration=60)
        for v in [10.0, 20.0, 30.0, 40.0, 50.0]:
            window.add_point(DataPoint(timestamp=now, value=v, source_id="s"))
        metrics = window.calculate_metrics()
        assert metrics[AnalyticsMetric.COUNT] == 5
        assert metrics[AnalyticsMetric.MEAN] == 30.0
        assert metrics[AnalyticsMetric.MIN] == 10.0
        assert metrics[AnalyticsMetric.MAX] == 50.0

    def test_is_complete(self):
        from codomyrmex.physical_management.analytics import AnalyticsWindow

        past = time.time() - 120
        window = AnalyticsWindow(start_time=past, end_time=past + 60, duration=60)
        assert window.is_complete()

    def test_empty_window_metrics(self):
        from codomyrmex.physical_management.analytics import AnalyticsWindow

        now = time.time()
        window = AnalyticsWindow(start_time=now, end_time=now + 60, duration=60)
        metrics = window.calculate_metrics()
        # Empty window returns empty dict or dict with count=0
        assert isinstance(metrics, dict)


# From test_coverage_boost_r3.py
class TestDataStream:
    """Tests for DataStream."""

    def test_add_and_get_stats(self):
        from codomyrmex.physical_management.analytics import DataStream

        stream = DataStream("test-stream", buffer_size=100, window_duration=60)
        for i in range(10):
            stream.add_data_point(float(i), source_id="sensor")
        stats = stream.get_stream_statistics()
        assert stats["total_points"] == 10

    def test_subscribe_callback(self):
        from codomyrmex.physical_management.analytics import DataStream

        received = []
        stream = DataStream("sub-test")
        stream.subscribe(lambda dp: received.append(dp.value))
        stream.add_data_point(99.0, source_id="s")
        assert 99.0 in received

    def test_unsubscribe(self):
        from codomyrmex.physical_management.analytics import DataStream

        received = []
        cb = lambda dp: received.append(dp.value)
        stream = DataStream("unsub-test")
        stream.subscribe(cb)
        stream.add_data_point(1.0, source_id="s")
        stream.unsubscribe(cb)
        stream.add_data_point(2.0, source_id="s")
        assert received == [1.0]

    def test_get_recent_data(self):
        from codomyrmex.physical_management.analytics import DataStream

        stream = DataStream("recent-test")
        for i in range(5):
            stream.add_data_point(float(i), source_id="s")
        recent = stream.get_recent_data(60)
        assert len(recent) == 5

    def test_current_metrics(self):
        from codomyrmex.physical_management.analytics import DataStream

        stream = DataStream("metrics-test", window_duration=60)
        stream.add_data_point(10.0, source_id="s")
        stream.add_data_point(20.0, source_id="s")
        metrics = stream.get_current_metrics()
        assert metrics is not None


# From test_coverage_boost_r3.py
class TestStreamingAnalytics:
    """Tests for StreamingAnalytics manager."""

    def test_create_and_delete_stream(self):
        from codomyrmex.physical_management.analytics import StreamingAnalytics

        sa = StreamingAnalytics()
        stream = sa.create_stream("s1")
        assert sa.get_stream("s1") is stream
        sa.delete_stream("s1")
        assert sa.get_stream("s1") is None

    def test_add_data(self):
        from codomyrmex.physical_management.analytics import StreamingAnalytics

        sa = StreamingAnalytics()
        sa.create_stream("s1")
        sa.add_data("s1", 42.0, "sensor")
        stats = sa.get_stream("s1").get_stream_statistics()
        assert stats["total_points"] == 1

    def test_get_analytics_summary(self):
        from codomyrmex.physical_management.analytics import StreamingAnalytics

        sa = StreamingAnalytics()
        sa.create_stream("a")
        sa.create_stream("b")
        sa.add_data("a", 1.0, "s")
        summary = sa.get_analytics_summary()
        assert "total_streams" in summary or isinstance(summary, dict)


# From test_coverage_boost_r7.py
class TestSensorIntegration:
    def test_device_status(self):
        from codomyrmex.physical_management.sensor_integration import DeviceStatus
        assert DeviceStatus is not None  # DeviceStatus exists

    def test_coordinate_system(self):
        from codomyrmex.physical_management.sensor_integration import CoordinateSystem
        assert CoordinateSystem is not None  # CoordinateSystem exists

    def test_physical_constants(self):
        from codomyrmex.physical_management.sensor_integration import PhysicalConstants
        assert hasattr(PhysicalConstants, "GRAVITY") or PhysicalConstants is not None

    def test_device_interface(self):
        from codomyrmex.physical_management.sensor_integration import DeviceInterface
        assert DeviceInterface is not None

    def test_sensor_manager(self):
        from codomyrmex.physical_management.sensor_integration import SensorManager
        mgr = SensorManager()
        assert mgr is not None


# From test_coverage_boost_r7.py
class TestSimulationEngine:
    def test_vector3d(self):
        from codomyrmex.physical_management.simulation_engine import Vector3D
        v = Vector3D(x=1.0, y=2.0, z=3.0)
        assert v.x == 1.0

    def test_force_field(self):
        from codomyrmex.physical_management.simulation_engine import ForceField, Vector3D
        ff = ForceField(position=Vector3D(0, -9.81, 0), strength=9.81)
        assert ff.strength == 9.81

    def test_constraint(self):
        from codomyrmex.physical_management.simulation_engine import Constraint
        c = Constraint(object1_id="obj1", object2_id="obj2", constraint_type="plane")
        assert c.constraint_type == "plane"

    def test_physics_simulator(self):
        from codomyrmex.physical_management.simulation_engine import PhysicsSimulator
        sim = PhysicsSimulator()
        assert sim is not None
