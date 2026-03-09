from codomyrmex.languages.javascript.manager import JavaScriptManager


def test_javascript_manager_operations():
    """Test JS manager functions."""
    manager = JavaScriptManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)
    assert len(instructions) > 0

    if is_installed:
        script = 'console.log("Hello from JS zero-mock test");\n'
        result = manager.use_script(script)
        assert "Hello from JS zero-mock test" in result

        error_script = 'console.error("Stderr test JS"); process.exit(1);\n'
        result_err = manager.use_script(error_script)
        assert "Stderr test JS" in result_err
