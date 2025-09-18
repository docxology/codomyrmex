# Terminal Interface

## Overview

The Terminal Interface module provides rich command-line interfaces and interactive terminal utilities for the Codomyrmex ecosystem. It offers both programmatic interfaces for building CLI applications and interactive shells for exploring the system.

## Key Components

- **Interactive Shell**: Full-featured interactive exploration environment
- **Terminal Utilities**: Rich terminal output, progress bars, and formatting
- **CLI Framework**: Command-line interface building blocks and utilities

## Integration Points

This module serves as the primary user interface layer for Codomyrmex:

**Provides:**
- **Interactive Exploration**: Rich shell environment for system exploration
- **Terminal Utilities**: Enhanced terminal output and user interaction
- **CLI Integration**: Command-line access to all Codomyrmex functionality
- **Progress Reporting**: Visual progress indicators for long-running operations

**Consumes:**
- **All Modules**: Provides CLI access to every Codomyrmex module
- **Logging Monitoring**: Terminal logging and output formatting
- **System Discovery**: Integration with system exploration capabilities

## Getting Started

### Interactive Shell
```bash
# Launch the interactive shell
python -c "from codomyrmex.terminal_interface import InteractiveShell; InteractiveShell().run()"

# Or use the orchestrator script
./start_here.sh
```

### Programmatic Usage
```python
from codomyrmex.terminal_interface import InteractiveShell, TerminalUtils

# Create interactive shell instance
shell = InteractiveShell()
shell.run()

# Use terminal utilities
utils = TerminalUtils()
utils.print_success("Operation completed!")
utils.show_progress("Processing", 50, 100)
```

## Key Features

### Rich Interactive Experience
- **Command Completion**: Intelligent command and argument completion
- **Context Help**: Dynamic help system based on current context
- **History**: Command history and recall functionality
- **Multi-line Input**: Support for complex multi-line commands

### Enhanced Terminal Output
- **Colored Output**: Syntax-highlighted and color-coded terminal output
- **Progress Bars**: Visual progress indicators for long operations
- **Status Messages**: Success, warning, and error message formatting
- **Table Display**: Formatted tabular data presentation

### CLI Framework
- **Command Registration**: Easy registration of new commands
- **Argument Parsing**: Flexible command argument handling
- **Help Generation**: Automatic help text generation
- **Error Handling**: Graceful error handling and user feedback

## Usage Examples

### Interactive Commands
```bash
🐜 codomyrmex> explore                    # Overview of all modules
🐜 codomyrmex> forage visualization       # Find visualization capabilities
🐜 codomyrmex> demo data_visualization    # Run live demo
🐜 codomyrmex> dive ai_code_editing       # Deep dive into AI module
🐜 codomyrmex> status                     # System health check
🐜 codomyrmex> export                     # Generate system inventory
```

### Programmatic Interface
```python
from codomyrmex.terminal_interface import TerminalUtils

# Enhanced output formatting
utils = TerminalUtils()
utils.print_header("Codomyrmex System Status")
utils.print_success("All modules loaded successfully")
utils.print_warning("Some optional dependencies missing")
utils.print_error("Critical module failed to load")

# Progress tracking
with utils.progress_context("Processing modules", total=100) as progress:
    for i in range(100):
        # Do work
        progress.update(1)
```

### Custom CLI Commands
```python
from codomyrmex.terminal_interface import CLIFramework

cli = CLIFramework()

@cli.command('analyze', help='Analyze code with AI assistance')
def analyze_command(file_path, analysis_type='comprehensive'):
    """Analyze a file using AI assistance."""
    from codomyrmex.ai_code_editing import analyze_code

    result = analyze_code(file_path, analysis_type)
    print(f"Analysis complete: {len(result['issues'])} issues found")

if __name__ == '__main__':
    cli.run()
```

## API Reference

See [API_SPECIFICATION.md](API_SPECIFICATION.md) for detailed programmatic interfaces.

## MCP Tools

This module provides the following MCP tools:
- `terminal_interface.run_interactive`: Launch interactive shell
- `terminal_interface.execute_command`: Execute CLI commands
- `terminal_interface.get_system_info`: Get formatted system information

See [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) for complete tool specifications.

## Security Considerations

See [SECURITY.md](SECURITY.md) for security implications and best practices.

## Dependencies

- `rich`: For enhanced terminal output and formatting
- `prompt_toolkit`: For interactive shell functionality
- `click`: For CLI framework (optional)
- `logging_monitoring`: For terminal logging integration
