from codomyrmex.languages.go.manager import GoManager


def test_go_manager_operations():
    """Test Go manager functions."""
    manager = GoManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = 'package main\nimport "fmt"\nfunc main() {\n\tfmt.Println("Hello from Go zero-mock test")\n}\n'
        result = manager.use_script(script)
        assert "Hello from Go zero-mock test" in result
