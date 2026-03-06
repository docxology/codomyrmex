
from codomyrmex.languages.cpp.manager import CppManager


def test_cpp_manager_operations():
    """Test C++ manager functions."""
    manager = CppManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = '#include <iostream>\n\nint main() {\n    std::cout << "Hello from C++ zero-mock test" << std::endl;\n    return 0;\n}\n'
        result = manager.use_script(script)
        assert "Hello from C++ zero-mock test" in result
