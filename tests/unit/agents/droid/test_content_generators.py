"""Tests for droid content_generators — zero-mock.

Covers: generate_physical_init_content, generate_physical_manager_content,
generate_physical_simulation_content, generate_sensor_integration_content.
All functions return large Python source strings.
"""

from codomyrmex.agents.droid.generators.physical_generators.content_generators import (
    generate_physical_init_content,
    generate_physical_manager_content,
    generate_physical_simulation_content,
    generate_sensor_integration_content,
)


class TestGeneratePhysicalInitContent:
    def test_returns_string(self):
        result = generate_physical_init_content()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_python(self):
        result = generate_physical_init_content()
        # Should contain typical __init__.py patterns
        assert (
            "import" in result.lower()
            or "from" in result.lower()
            or "__all__" in result.lower()
        )


class TestGeneratePhysicalManagerContent:
    def test_returns_string(self):
        result = generate_physical_manager_content()
        assert isinstance(result, str)
        assert len(result) > 100  # Should be substantial

    def test_contains_class_or_function(self):
        result = generate_physical_manager_content()
        assert "class " in result or "def " in result


class TestGeneratePhysicalSimulationContent:
    def test_returns_string(self):
        result = generate_physical_simulation_content()
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contains_simulation_keywords(self):
        result = generate_physical_simulation_content()
        lower = result.lower()
        assert (
            "simulation" in lower
            or "simulate" in lower
            or "physics" in lower
            or "class " in result
        )


class TestGenerateSensorIntegrationContent:
    def test_returns_string(self):
        result = generate_sensor_integration_content()
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contains_sensor_keywords(self):
        result = generate_sensor_integration_content()
        lower = result.lower()
        assert "sensor" in lower or "class " in result or "def " in result
