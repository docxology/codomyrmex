from codomyrmex.languages.python.manager import PythonManager


def test_python_manager_operations():
    """Test Python manager functions."""
    manager = PythonManager()

    # Check installation status
    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    # Check instructions type
    instructions = manager.install_instructions()
    assert isinstance(instructions, str)
    assert len(instructions) > 0

    # Run a real test script if python is installed
    if is_installed:
        # Simple print test
        script = 'print("Hello from Python zero-mock test")\n'
        result = manager.use_script(script)
        assert "Hello from Python zero-mock test" in result

        # Test error capturing
        error_script = 'import sys; sys.stderr.write("Stderr test\\n"); sys.exit(1)\n'
        result_err = manager.use_script(error_script)
        assert "Stderr test" in result_err
