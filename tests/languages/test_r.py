from codomyrmex.languages.r.manager import RManager


def test_r_manager_operations():
    """Test R manager functions."""
    manager = RManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = 'cat("Hello from R zero-mock test\\n")\n'
        result = manager.use_script(script)
        assert "Hello from R zero-mock test" in result
