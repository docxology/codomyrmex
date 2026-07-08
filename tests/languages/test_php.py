from codomyrmex.languages.php.manager import PhpManager


def test_php_manager_operations():
    """Test PHP manager functions."""
    manager = PhpManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = '<?php\necho "Hello from PHP zero-mock test";\n?>\n'
        result = manager.use_script(script)
        assert "Hello from PHP zero-mock test" in result
