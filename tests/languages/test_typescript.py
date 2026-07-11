from codomyrmex.languages.typescript.manager import TypeScriptManager


def test_typescript_manager_operations():
    """Test TS manager functions."""
    manager = TypeScriptManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)
    assert len(instructions) > 0

    if is_installed:
        script = (
            'const msg: string = "Hello from TS zero-mock test";\nconsole.log(msg);\n'
        )
        result = manager.use_script(script)
        assert "Hello from TS zero-mock test" in result
