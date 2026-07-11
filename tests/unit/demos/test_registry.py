"""Unit tests for the DemoRegistry."""

import tempfile
from pathlib import Path

from codomyrmex.demos.registry import DemoRegistry


def test_registry_register_and_list():
    registry = DemoRegistry()

    def my_demo():
        return True

    registry.register(
        "test_demo", "A test demo", my_demo, module="test", category="unit"
    )

    demos = registry.list_demos()
    assert len(demos) == 1
    assert demos[0].name == "test_demo"
    assert demos[0].module == "test"
    assert demos[0].category == "unit"

    # Filter by module
    assert len(registry.list_demos(module="test")) == 1
    assert len(registry.list_demos(module="other")) == 0


def test_run_callable_demo():
    registry = DemoRegistry()

    def success_demo():
        return "All good"

    def fail_demo():
        return False

    registry.register("success", "Success", success_demo)
    registry.register("fail", "Fail", fail_demo)

    res1 = registry.run_demo("success")
    assert res1.success is True
    assert res1.output == "All good"

    res2 = registry.run_demo("fail")
    assert res2.success is False


def test_discover_and_run_script_demo():
    registry = DemoRegistry()

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "demo_test_script.py"
        script_path.write_text('"""Test Script Demo"""\nprint("Hello from script")\n')

        registry.discover_scripts(tmpdir)

        demos = registry.list_demos(category="script")
        assert len(demos) == 1
        assert demos[0].name == "demo_test_script"
        assert demos[0].description == "Test Script Demo"

        # Run it
        # Note: In a real test environment, we'd need to ensure PYTHONPATH is set,
        # but here we're just checking that the script runs.
        # Since it doesn't import codomyrmex, it should be fine.
        result = registry.run_demo("demo_test_script")
        assert result.success is True
        assert "Hello from script" in result.output


def test_run_nonexistent_demo():
    registry = DemoRegistry()
    result = registry.run_demo("ghost")
    assert result.success is False
    assert "not found" in (result.error or "")
