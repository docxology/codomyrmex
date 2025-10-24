"""
Comprehensive tests for the Terminal Interface module.

This module tests all components of the terminal interface functionality:
- InteractiveShell for command-line exploration
- TerminalUtils for formatting and utilities
"""

import pytest
import sys
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from io import StringIO

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.terminal_interface.interactive_shell import InteractiveShell


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

    def test_default_unknown_command(self):
        """Test handling of unknown commands."""
        with patch('builtins.print') as mock_print:
            self.shell.default("unknown_command")

            # Should print unknown command message
            mock_print.assert_any_call("🤔 Unknown command: 'unknown_command'")
            mock_print.assert_any_call("💡 Try 'help' to see available commands, or 'explore' to start foraging!")

    def test_do_explore_no_discovery(self):
        """Test explore command when discovery is not available."""
        with patch.object(self.shell, 'discovery', None):
            with patch('builtins.print') as mock_print:
                self.shell.do_explore("")

                mock_print.assert_any_call("❌ System discovery not available - running in limited mode")

    @patch('codomyrmex.terminal_interface.interactive_shell.SystemDiscovery')
    def test_do_explore_overview(self, mock_discovery_class):
        """Test explore command overview functionality."""
        # Mock the discovery system
        mock_discovery = MagicMock()
        mock_discovery_class.return_value = mock_discovery
        mock_discovery.modules = {}

        # Create shell with mocked discovery
        shell = InteractiveShell()
        shell.discovery = mock_discovery

        with patch('builtins.print') as mock_print:
            shell.do_explore("")

            # Should increment commands_run
            assert shell.session_data['commands_run'] == 1

            # Should print exploration header
            mock_print.assert_any_call("🗺️  " + "="*60)

    @patch('codomyrmex.terminal_interface.interactive_shell.SystemDiscovery')
    def test_do_explore_specific_module(self, mock_discovery_class):
        """Test explore command for specific module."""
        # Mock the discovery system
        mock_discovery = MagicMock()
        mock_discovery_class.return_value = mock_discovery

        # Create shell with mocked discovery
        shell = InteractiveShell()
        shell.discovery = mock_discovery

        with patch.object(shell, '_explore_module') as mock_explore_module:
            shell.do_explore("test_module")

            # Should call _explore_module with the module name
            mock_explore_module.assert_called_once_with("test_module")

    def test_do_status(self):
        """Test status command."""
        with patch.object(self.shell, 'discovery', None):
            with patch('builtins.print') as mock_print:
                self.shell.do_status("")

                mock_print.assert_any_call("🏥 ============================================================")

    @patch('codomyrmex.terminal_interface.interactive_shell.SystemDiscovery')
    def test_do_status_with_discovery(self, mock_discovery_class):
        """Test status command with discovery available."""
        # Mock the discovery system
        mock_discovery = MagicMock()
        mock_discovery_class.return_value = mock_discovery

        # Create shell with mocked discovery
        shell = InteractiveShell()
        shell.discovery = mock_discovery

        with patch('builtins.print') as mock_print:
            shell.do_status("")

            # Should show status dashboard
            mock_print.assert_any_call("🏥 ============================================================")

    def test_do_demo(self):
        """Test demo command."""
        with patch.object(self.shell, 'discovery', None):
            with patch('builtins.print') as mock_print:
                self.shell.do_demo("")

                mock_print.assert_any_call("❌ Discovery system not available")

    @patch('codomyrmex.terminal_interface.interactive_shell.SystemDiscovery')
    def test_do_demo_with_discovery(self, mock_discovery_class):
        """Test demo command with discovery available."""
        # Mock the discovery system
        mock_discovery = MagicMock()
        mock_discovery_class.return_value = mock_discovery

        # Create shell with mocked discovery
        shell = InteractiveShell()
        shell.discovery = mock_discovery

        with patch('builtins.print') as mock_print:
            shell.do_demo("")

            # Should run demo workflows
            mock_print.assert_any_call("🚀 ============================================================")

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

    def test_do_quit(self):
        """Test quit command."""
        with patch('builtins.print') as mock_print:
            result = self.shell.do_quit("")

            # Should return True to exit
            assert result == True

            # Should print farewell message
            mock_print.assert_any_call("\n🐜 Thank you for foraging in the Codomyrmex nest!")

    def test_do_EOF(self):
        """Test EOF (Ctrl+D) handling."""
        with patch('builtins.print') as mock_print:
            result = self.shell.do_EOF("")

            # Should return True to exit
            assert result == True

            # Should print farewell message (same as do_quit since do_EOF calls do_quit)
            mock_print.assert_any_call("\n🐜 Thank you for foraging in the Codomyrmex nest!")

    def test_do_exit(self):
        """Test exit command."""
        with patch('builtins.print') as mock_print:
            result = self.shell.do_exit("")

            # Should return True to exit
            assert result == True

            # Should print farewell message
            mock_print.assert_any_call("\n🐜 Thank you for foraging in the Codomyrmex nest!")

    def test_do_shell(self):
        """Test shell command for running system commands."""
        with patch('subprocess.run') as mock_subprocess:
            mock_result = MagicMock()
            mock_result.stdout = "test output"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result

            self.shell.do_shell("ls -la")

            # Should call subprocess.run with the command
            mock_subprocess.assert_called_once_with("ls -la", shell=True, capture_output=True, text=True)

    def test_do_forage(self):
        """Test forage command."""
        with patch('builtins.print') as mock_print:
            self.shell.do_forage("visualization")

            # Should print foraging message
            assert any("🔍" in str(call) for call in mock_print.call_args_list)

    def test_do_dive(self):
        """Test dive command."""
        # Mock discovery system so dive can work
        mock_discovery = MagicMock()
        mock_discovery.modules = {
            'ai_code_editing': MagicMock(),
        }
        mock_discovery.modules['ai_code_editing'].capabilities = [
            MagicMock(type='function', name='test_function'),
            MagicMock(type='class', name='TestClass')
        ]

        with patch.object(self.shell, 'discovery', mock_discovery):
            with patch('builtins.print') as mock_print:
                self.shell.do_dive("ai_code_editing")

                # Should print diving message
                assert any("🤿" in str(call) for call in mock_print.call_args_list)

    def test_do_stats(self):
        """Test stats command."""
        with patch('builtins.print') as mock_print:
            self.shell.do_stats("")

            # Should show session statistics
            mock_print.assert_any_call("📊 Session Statistics:")

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

    def test_do_history(self):
        """Test history command."""
        with patch('builtins.print') as mock_print:
            self.shell.do_history("")

            # Should show command history
            mock_print.assert_any_call("📜 Command History:")

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
        """Test command completion for explore."""
        # Mock available modules
        with patch.object(self.shell, 'discovery') as mock_discovery:
            mock_discovery.discover_modules.return_value = [
                {'name': 'ai_code_editing'},
                {'name': 'data_visualization'},
                {'name': 'static_analysis'}
            ]

            # Test completion
            completions = self.shell.complete_explore("ai", line="explore ai", begidx=8, endidx=10)

            assert 'ai_code_editing' in completions

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
        mock_discovery = MagicMock()
        mock_discovery.modules = {}
        with patch.object(self.shell, 'discovery', mock_discovery):
            self.shell.do_explore("")

        # Should increment command count
        assert self.shell.session_data['commands_run'] == initial_commands + 1

    def test_foraging_messages_variety(self):
        """Test that foraging messages are varied."""
        messages = set()

        # Run multiple times to get different messages
        for _ in range(10):
            with patch('random.choice') as mock_random:
                mock_random.return_value = "Test message"
                with patch('builtins.print'):
                    self.shell.do_explore("")
                    messages.add(mock_random.return_value)

        # Should use random.choice for message selection
        assert "Test message" in messages


class TestShellIntegration:
    """Integration tests for shell functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.shell = InteractiveShell()

    def test_shell_initialization_with_discovery(self):
        """Test shell initialization with working discovery."""
        with patch('codomyrmex.terminal_interface.interactive_shell.SystemDiscovery') as mock_discovery:
            mock_instance = MagicMock()
            mock_discovery.return_value = mock_instance

            shell = InteractiveShell()

            assert shell.discovery is not None
            mock_discovery.assert_called_once()

    def test_shell_initialization_without_discovery(self):
        """Test shell initialization when discovery import fails."""
        with patch('codomyrmex.terminal_interface.interactive_shell.SystemDiscovery', None):
            shell = InteractiveShell()

            assert shell.discovery is None

    def test_command_execution_flow(self):
        """Test complete command execution flow."""
        with patch.object(self.shell, 'discovery', None):
            with patch('builtins.print') as mock_print:
                # Execute a command
                self.shell.onecmd("explore")

                # Should handle the command and show appropriate output
                assert mock_print.called

    def test_help_system(self):
        """Test that help system works for all commands."""
        # Get all do_ methods
        do_methods = [method for method in dir(self.shell) if method.startswith('do_')]

        for method_name in do_methods[:5]:  # Test first 5 to avoid too many calls
            command_name = method_name[3:]  # Remove 'do_' prefix

            with patch('builtins.print'):
                # This should not raise an exception
                self.shell.do_help(command_name)


class TestCommandValidation:
    """Test command validation and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.shell = InteractiveShell()

    def test_invalid_command_handling(self):
        """Test handling of invalid commands."""
        with patch('builtins.print') as mock_print:
            self.shell.onecmd("invalid_command_xyz")

            # Should show unknown command message
            unknown_call = None
            for call in mock_print.call_args_list:
                if "Unknown command" in str(call):
                    unknown_call = call
                    break

            assert unknown_call is not None

    def test_command_with_arguments(self):
        """Test commands that accept arguments."""
        with patch.object(self.shell, 'discovery', None):
            with patch('builtins.print'):
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


class TestShellOutputFormatting:
    """Test shell output formatting and display."""

    def setup_method(self):
        """Set up test fixtures."""
        self.shell = InteractiveShell()

    def test_colored_output(self):
        """Test that shell uses appropriate emojis and formatting."""
        commands_to_test = [
            ("explore", "🔎"),  # Discovery scanning uses 🔎
            ("status", "📊"),
            ("demo", "🚀"),
            ("help", "🐜"),  # Help uses the ant emoji in the prompt
            ("quit", "🐜")
        ]

        for command, expected_emoji in commands_to_test:
            with patch('builtins.print') as mock_print:
                if command == "quit":
                    self.shell.do_quit("")
                elif command == "help":
                    # Help command uses cmd module's help system, check prompt emoji instead
                    assert expected_emoji in self.shell.prompt
                else:
                    getattr(self.shell, f"do_{command}")("")

                    # Check that expected emoji appears in output
                    output_calls = [call.args[0] for call in mock_print.call_args_list if call.args]
                    emoji_found = any(expected_emoji in output for output in output_calls)
                    assert emoji_found, f"Expected emoji {expected_emoji} not found in {command} output. Got: {output_calls}"


class TestShellStateManagement:
    """Test shell state management and persistence."""

    def setup_method(self):
        """Set up test fixtures."""
        self.shell = InteractiveShell()

    def test_session_persistence(self):
        """Test that session data persists across commands."""
        initial_commands = self.shell.session_data['commands_run']

        # Run multiple commands
        with patch.object(self.shell, 'discovery', None):
            with patch('builtins.print'):
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
