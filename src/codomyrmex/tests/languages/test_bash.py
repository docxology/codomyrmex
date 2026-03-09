from codomyrmex.languages.bash.manager import BashManager


def test_bash_manager_operations():
    """Test Bash manager functions."""
    manager = BashManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = 'echo "Hello from Bash zero-mock test"\n'
        result = manager.use_script(script)
        assert "Hello from Bash zero-mock test" in result
