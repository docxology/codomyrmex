
from codomyrmex.languages.elixir.manager import ElixirManager


def test_elixir_manager_operations():
    """Test Elixir manager functions."""
    manager = ElixirManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = 'IO.puts "Hello from Elixir zero-mock test"\n'
        result = manager.use_script(script)
        assert "Hello from Elixir zero-mock test" in result
