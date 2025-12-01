"""Unit tests for physical_management module."""

import sys
import pytest
from pathlib import Path


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
            from codomyrmex.physical_management import PhysicalObjectManager
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
                ObjectType,
                ObjectStatus,
                MaterialType,
                EventType,
                SensorType,
                DeviceStatus,
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
        assert docs_path.exists()
        assert docs_path.is_dir()

    def test_examples_directory_exists(self, code_dir):
        """Test that examples directory exists for physical_management module."""
        examples_path = code_dir / "codomyrmex" / "physical_management" / "examples"
        assert examples_path.exists()
        assert examples_path.is_dir()

    def test_tests_directory_exists(self, code_dir):
        """Test that tests directory exists for physical_management module."""
        tests_path = code_dir / "codomyrmex" / "physical_management" / "tests"
        assert tests_path.exists()
        assert tests_path.is_dir()

