
from codomyrmex.languages.ruby.manager import RubyManager


def test_ruby_manager_operations():
    """Test Ruby manager functions."""
    manager = RubyManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = 'puts "Hello from Ruby zero-mock test"\n'
        result = manager.use_script(script)
        assert "Hello from Ruby zero-mock test" in result
