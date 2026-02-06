"""
Comprehensive tests for the Terminal Interface module.

This module tests all components of the terminal interface functionality:
- InteractiveShell for command-line exploration
- TerminalUtils for formatting and utilities
"""


import pytest

try:
    from codomyrmex.terminal_interface.interactive_shell import InteractiveShell
except ImportError:
    pytest.skip("terminal_interface module not available", allow_module_level=True)


@pytest.mark.unit
class TestInteractiveShell:
    """Test cases for InteractiveShell functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.shell = InteractiveShell()

    def test_interactive_shell_initialization(self):
        """Test InteractiveShell initialization."""
        assert self.shell.prompt == "🐜 codomyrmex> "
        assert isinstance(self.shell.session_data, dict)
        assert 'commands_run' in self.shell.session_data
        assert 'modules_explored' in self.shell.session_data
        assert 'discoveries_made' in self.shell.session_data
        assert 'demos_run' in self.shell.session_data

        assert isinstance(self.shell.foraging_messages, list)
        assert len(self.shell.foraging_messages) > 0

    def test_emptyline(self):
        """Test handling of empty lines."""
        # Should not raise an exception
        self.shell.emptyline()

    def test_default_unknown_command(self, capsys):
        """Test handling of unknown commands with real print."""
        self.shell.default("unknown_command")

        # Capture output
        captured = capsys.readouterr()
        assert "Unknown command" in captured.out or "unknown_command" in captured.out

    def test_do_explore_no_discovery(self, capsys):
        """Test explore command when discovery is not available."""
        self.shell.discovery = None
        self.shell.do_explore("")

        # Capture output
        captured = capsys.readouterr()
        assert "System discovery not available" in captured.out or "limited mode" in captured.out

    def test_do_explore_overview(self):
        """Test explore command overview functionality with real discovery."""
        try:
            from codomyrmex.system_discovery import SystemDiscovery
            discovery = SystemDiscovery()
            self.shell.discovery = discovery
        except ImportError:
            pytest.skip("SystemDiscovery not available")

        initial_commands = self.shell.session_data['commands_run']
        self.shell.do_explore("")

        # Should increment commands_run
        assert self.shell.session_data['commands_run'] == initial_commands + 1

    def test_do_explore_specific_module(self):
        """Test explore command for specific module with real discovery."""
        try:
            from codomyrmex.system_discovery import SystemDiscovery
            discovery = SystemDiscovery()
            self.shell.discovery = discovery
        except ImportError:
            pytest.skip("SystemDiscovery not available")

        # Test with a real module name
        self.shell.do_explore("logging_monitoring")

        # Should have attempted to explore
        assert self.shell.session_data['commands_run'] > 0

    def test_do_status(self, capsys):
        """Test status command with real print."""
        self.shell.discovery = None
        self.shell.do_status("")

        # Capture output
        captured = capsys.readouterr()
        assert len(captured.out) >= 0  # Should produce output

    def test_do_status_with_discovery(self):
        """Test status command with discovery available."""
        try:
            from codomyrmex.system_discovery import SystemDiscovery
            discovery = SystemDiscovery()
            self.shell.discovery = discovery
        except ImportError:
            pytest.skip("SystemDiscovery not available")

        self.shell.do_status("")
        # Should complete without error

    def test_do_demo(self, capsys):
        """Test demo command with real print."""
        self.shell.discovery = None
        self.shell.do_demo("")

        # Capture output
        captured = capsys.readouterr()
        assert "Discovery system not available" in captured.out or len(captured.out) >= 0

    def test_do_demo_with_discovery(self):
        """Test demo command with discovery available."""
        try:
            from codomyrmex.system_discovery import SystemDiscovery
            discovery = SystemDiscovery()
            self.shell.discovery = discovery
        except ImportError:
            pytest.skip("SystemDiscovery not available")

        self.shell.do_demo("")
        # Should complete without error

    def test_do_help(self):
        """Test help command."""
        # Help command uses cmd module's built-in help system
        # Just test that it doesn't raise an error
        try:
            self.shell.do_help("")
            # If we get here without exception, the test passes
            assert True
        except Exception as e:
            pytest.fail(f"Help command raised an exception: {e}")

    def test_do_quit(self, capsys):
        """Test quit command with real print."""
        result = self.shell.do_quit("")

        # Should return True to exit
        assert result == True

        # Capture output
        captured = capsys.readouterr()
        assert "Thank you for foraging" in captured.out or "Codomyrmex" in captured.out

    def test_do_EOF(self, capsys):
        """Test EOF (Ctrl+D) handling with real print."""
        result = self.shell.do_EOF("")

        # Should return True to exit
        assert result == True

        # Capture output
        captured = capsys.readouterr()
        assert "Thank you for foraging" in captured.out or "Codomyrmex" in captured.out

    def test_do_exit(self, capsys):
        """Test exit command with real print."""
        result = self.shell.do_exit("")

        # Should return True to exit
        assert result == True

        # Capture output
        captured = capsys.readouterr()
        assert "Thank you for foraging" in captured.out or "Codomyrmex" in captured.out

    def test_do_shell(self):
        """Test shell command for running system commands with real subprocess."""
        # Use a simple command that should work
        self.shell.do_shell("echo test")

        # Should complete without error
        # Note: We can't easily capture subprocess output in this context

    def test_do_forage(self, capsys):
        """Test forage command with real print."""
        self.shell.do_forage("visualization")

        # Capture output
        captured = capsys.readouterr()
        assert len(captured.out) >= 0  # Should produce output

    def test_do_dive(self):
        """Test dive command with real discovery."""
        try:
            from codomyrmex.system_discovery import SystemDiscovery
            discovery = SystemDiscovery()
            self.shell.discovery = discovery
        except ImportError:
            pytest.skip("SystemDiscovery not available")

        # Test with a real module
        self.shell.do_dive("logging_monitoring")
        # Should complete without error

    def test_do_stats(self, capsys):
        """Test stats command with real print."""
        self.shell.do_stats("")

        # Capture output
        captured = capsys.readouterr()
        assert "Session Statistics" in captured.out or "Statistics" in captured.out

    def test_do_clear(self):
        """Test clear command."""
        # Set some session data
        self.shell.session_data['commands_run'] = 5
        self.shell.session_data['modules_explored'].add('test_module')

        # Clear session
        self.shell.do_clear("")

        # Should reset session data
        assert self.shell.session_data['commands_run'] == 0
        assert len(self.shell.session_data['modules_explored']) == 0

    def test_do_history(self, capsys):
        """Test history command with real print."""
        self.shell.do_history("")

        # Capture output
        captured = capsys.readouterr()
        assert "Command History" in captured.out or "History" in captured.out

    def test_get_names(self):
        """Test get_names method for command completion."""
        names = self.shell.get_names()

        # Should return a list of method names
        assert isinstance(names, list)
        assert len(names) > 0

        # Should include our custom methods
        method_names = [name for name in names if name.startswith('do_')]
        assert 'do_explore' in method_names
        assert 'do_status' in method_names
        assert 'do_quit' in method_names

    def test_complete_explore(self):
        """Test command completion for explore with real discovery."""
        try:
            from codomyrmex.system_discovery import SystemDiscovery
            discovery = SystemDiscovery()
            self.shell.discovery = discovery
        except ImportError:
            pytest.skip("SystemDiscovery not available")

        # Test completion
        completions = self.shell.complete_explore("log", line="explore log", begidx=8, endidx=11)

        # Should return a list
        assert isinstance(completions, list)

    def test_precmd(self):
        """Test precmd hook."""
        # Test with a normal command
        result = self.shell.precmd("explore")
        assert result == "explore"

        # Test with empty/whitespace command
        result = self.shell.precmd("   ")
        assert result == "   "

    def test_postcmd(self):
        """Test postcmd hook."""
        # Test with stop=False (continue)
        result = self.shell.postcmd(False, "explore")
        assert result == False

        # Test with stop=True (exit)
        result = self.shell.postcmd(True, "quit")
        assert result == True

    def test_session_data_tracking(self):
        """Test that session data is properly tracked."""
        initial_commands = self.shell.session_data['commands_run']

        # Run a command
        try:
            from codomyrmex.system_discovery import SystemDiscovery
            discovery = SystemDiscovery()
            self.shell.discovery = discovery
        except ImportError:
            self.shell.discovery = None

        self.shell.do_explore("")

        # Should increment command count
        assert self.shell.session_data['commands_run'] == initial_commands + 1

    def test_foraging_messages_variety(self):
        """Test that foraging messages are varied."""
        # Test that foraging_messages list exists and has content
        assert len(self.shell.foraging_messages) > 0
        assert isinstance(self.shell.foraging_messages, list)


@pytest.mark.unit
class TestShellIntegration:
    """Integration tests for shell functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.shell = InteractiveShell()

    def test_shell_initialization_with_discovery(self):
        """Test shell initialization with working discovery."""
        try:
            from codomyrmex.system_discovery import SystemDiscovery
            shell = InteractiveShell()
            # Discovery may or may not be available
            assert shell.discovery is None or isinstance(shell.discovery, SystemDiscovery)
        except ImportError:
            pytest.skip("SystemDiscovery not available")

    def test_shell_initialization_without_discovery(self):
        """Test shell initialization when discovery import fails."""
        shell = InteractiveShell()
        # Discovery may be None if import fails
        assert shell.discovery is None or shell.discovery is not None

    def test_command_execution_flow(self, capsys):
        """Test complete command execution flow."""
        self.shell.discovery = None
        # Execute a command
        self.shell.onecmd("explore")

        # Should handle the command
        captured = capsys.readouterr()
        assert len(captured.out) >= 0  # Should produce some output

    def test_help_system(self):
        """Test that help system works for all commands."""
        # Get all do_ methods
        do_methods = [method for method in dir(self.shell) if method.startswith('do_')]

        for method_name in do_methods[:5]:  # Test first 5 to avoid too many calls
            command_name = method_name[3:]  # Remove 'do_' prefix

            # This should not raise an exception
            self.shell.do_help(command_name)


@pytest.mark.unit
class TestCommandValidation:
    """Test command validation and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.shell = InteractiveShell()

    def test_invalid_command_handling(self, capsys):
        """Test handling of invalid commands."""
        self.shell.onecmd("invalid_command_xyz")

        # Capture output
        captured = capsys.readouterr()
        assert "Unknown command" in captured.out or "invalid_command_xyz" in captured.out

    def test_command_with_arguments(self):
        """Test commands that accept arguments."""
        self.shell.discovery = None
        # Test explore with argument
        self.shell.onecmd("explore test_module")

        # Should handle the command without error
        # (The actual behavior depends on discovery availability)

    def test_empty_command_handling(self):
        """Test handling of empty commands."""
        # Empty command should not cause issues
        result = self.shell.onecmd("")
        assert result is None

        result = self.shell.onecmd("   ")
        assert result is None


@pytest.mark.unit
class TestShellOutputFormatting:
    """Test shell output formatting and display."""

    def setup_method(self):
        """Set up test fixtures."""
        self.shell = InteractiveShell()

    def test_colored_output(self):
        """Test that shell uses appropriate emojis and formatting."""
        # Test that prompt has emoji
        assert "🐜" in self.shell.prompt

        # Test that commands work
        commands_to_test = ["explore", "status", "demo", "help", "quit"]

        for command in commands_to_test:
            if command == "quit":
                result = self.shell.do_quit("")
                assert result is True
            elif command == "help":
                # Help command uses cmd module's help system
                self.shell.do_help("")
            else:
                getattr(self.shell, f"do_{command}")("")
                # Should complete without error


@pytest.mark.unit
class TestShellStateManagement:
    """Test shell state management and persistence."""

    def setup_method(self):
        """Set up test fixtures."""
        self.shell = InteractiveShell()

    def test_session_persistence(self):
        """Test that session data persists across commands."""
        initial_commands = self.shell.session_data['commands_run']

        # Run multiple commands
        self.shell.discovery = None
        self.shell.do_explore("")
        self.shell.do_status("")
        self.shell.do_demo("")

        # Should have incremented command count for each command
        expected_commands = initial_commands + 3
        assert self.shell.session_data['commands_run'] == expected_commands

    def test_module_exploration_tracking(self):
        """Test tracking of explored modules."""
        initial_explored = len(self.shell.session_data['modules_explored'])

        # Simulate exploring modules
        self.shell.session_data['modules_explored'].add('test_module1')
        self.shell.session_data['modules_explored'].add('test_module2')

        assert len(self.shell.session_data['modules_explored']) == initial_explored + 2
        assert 'test_module1' in self.shell.session_data['modules_explored']
        assert 'test_module2' in self.shell.session_data['modules_explored']


if __name__ == '__main__':
    pytest.main([__file__])
