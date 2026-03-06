import pytest

from codomyrmex.languages.swift.manager import SwiftManager


def test_swift_manager_operations():
    """Test Swift manager functions."""
    manager = SwiftManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = 'print("Hello from Swift zero-mock test")\n'
        result = manager.use_script(script)
        assert "Hello from Swift zero-mock test" in result
