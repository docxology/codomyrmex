import pytest

from codomyrmex.languages.java.manager import JavaManager


def test_java_manager_operations():
    """Test Java manager functions."""
    manager = JavaManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = 'public class ZeroMockTest {\n    public static void main(String[] args) {\n        System.out.println("Hello from Java zero-mock test");\n    }\n}\n'
        result = manager.use_script(script)
        assert "Hello from Java zero-mock test" in result
