import pytest

try:
    from codomyrmex.terminal_interface.interactive_shell import InteractiveShell
    from codomyrmex.terminal_interface.terminal_utils import TerminalFormatter, CommandRunner
except ImportError:
    pytest.skip("terminal_interface module not importable", allow_module_level=True)

class TestTerminalInterface:
    
    @pytest.fixture
    def terminal_formatter(self):
        return TerminalFormatter(use_colors=False)

    def test_formatter_instantiation(self, terminal_formatter):
        assert terminal_formatter is not None
        assert hasattr(terminal_formatter, "success")
        assert hasattr(terminal_formatter, "error")

    def test_shell_instantiation(self):
        """Test shell instantiation with real SystemDiscovery."""
        shell = InteractiveShell()
        assert shell is not None
        assert hasattr(shell, "do_explore")
        # SystemDiscovery may or may not be available, but shell should still instantiate
        # SystemDiscovery has run_full_discovery method, not discover_modules
        assert shell.discovery is None or hasattr(shell.discovery, "run_full_discovery")

    def test_formatter_methods(self, terminal_formatter):
        msg = terminal_formatter.success("test")
        assert "test" in msg
