# Codomyrmex Agents — src/codomyrmex/terminal_interface

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Foundation module providing rich terminal interface capabilities for the Codomyrmex platform. This module enables consistent, interactive command-line experiences with colored output, progress indicators, and user-friendly interactions across all platform components.

The terminal_interface module serves as the user interaction foundation, ensuring consistent and accessible command-line experiences throughout the platform.

## Module Overview

### Key Capabilities
- **Colored Output**: Syntax-highlighted and color-coded terminal output
- **Progress Indicators**: Visual progress bars and status indicators
- **Interactive Prompts**: User input collection with validation
- **Table Formatting**: Structured data display in tabular format
- **Status Messages**: Consistent success, warning, and error message formatting
- **Cross-Platform Support**: Works across different terminal environments

### Key Features
- Rich text formatting with color and style support
- Interactive progress bars for long-running operations
- Structured table output for data presentation
- Input validation and sanitization
- Error message formatting with actionable guidance
- Unicode and emoji support for readability

## Function Signatures

### Terminal Formatter Class

```python
class TerminalFormatter:
    def __init__(self, use_colors: bool = None) -> None
```

Utility class for formatting terminal output with colors and styles. Auto-detects color support if `use_colors` is None.

**Methods:**

```python
def color(self, text: str, color: str, style: Optional[str] = None) -> str
```

Apply color and optional style to text using ANSI escape codes.

**Parameters:**
- `text` (str): Text to format
- `color` (str): Color name (e.g., "RED", "BRIGHT_GREEN", "CYAN")
- `style` (Optional[str]): Style name (e.g., "BOLD", "ITALIC", "UNDERLINE")

**Returns:** `str` - Formatted text with ANSI codes

```python
def success(self, text: str) -> str
def error(self, text: str) -> str
def warning(self, text: str) -> str
def info(self, text: str) -> str
```

Format message with appropriate color and emoji indicator.

**Returns:** `str` - Formatted message (success=green ✅, error=red ❌, warning=yellow ⚠️, info=blue ℹ️)

```python
def header(self, text: str, char: str = "=", width: int = 60) -> str
```

Create a formatted header with border lines.

**Parameters:**
- `text` (str): Header text
- `char` (str): Border character. Defaults to "="
- `width` (int): Total width of header. Defaults to 60

**Returns:** `str` - Formatted header with top and bottom borders

```python
def progress_bar(
    self,
    current: int,
    total: int,
    width: int = 40,
    prefix: str = "",
    suffix: str = ""
) -> str
```

Create a visual progress bar with percentage.

**Parameters:**
- `current` (int): Current progress value
- `total` (int): Total/maximum value
- `width` (int): Width of progress bar in characters. Defaults to 40
- `prefix` (str): Text before progress bar
- `suffix` (str): Text after progress bar

**Returns:** `str` - Formatted progress bar with percentage

```python
def table(
    self,
    headers: list[str],
    rows: list[list[str]],
    max_width: int = 80
) -> str
```

Create a formatted table with borders using Unicode box-drawing characters.

**Parameters:**
- `headers` (list[str]): Column headers
- `rows` (list[list[str]]): Table data rows
- `max_width` (int): Maximum table width. Defaults to 80

**Returns:** `str` - Formatted table with borders

```python
def box(
    self,
    content: str,
    title: Optional[str] = None,
    width: Optional[int] = None
) -> str
```

Create a box around content with optional title.

**Parameters:**
- `content` (str): Content to box (can be multi-line)
- `title` (Optional[str]): Optional box title
- `width` (Optional[int]): Box width (auto-calculated if None)

**Returns:** `str` - Boxed content with Unicode borders

### Command Runner Class

```python
class CommandRunner:
    def __init__(self, formatter: Optional[TerminalFormatter] = None) -> None
```

Utility class for running commands with formatted output.

**Methods:**

```python
def run_command(
    self,
    command: list[str],
    cwd: Optional[Path] = None,
    show_output: bool = True,
    timeout: Optional[int] = None
) -> dict[str, Any]
```

Run a command and return formatted results.

**Parameters:**
- `command` (list[str]): Command and arguments as list
- `cwd` (Optional[Path]): Working directory for command
- `show_output` (bool): Whether to display output in real-time. Defaults to True
- `timeout` (Optional[int]): Timeout in seconds

**Returns:** `dict[str, Any]` with keys:
- `returncode` (int): Exit code
- `stdout` (str): Standard output
- `stderr` (str): Standard error
- `success` (bool): Whether command succeeded
- `command` (str): Original command string

```python
def run_python_module(
    self,
    module: str,
    args: list[str] = None,
    cwd: Optional[Path] = None,
    show_output: bool = True
) -> dict[str, Any]
```

Run a Python module using `python -m module_name`.

**Parameters:**
- `module` (str): Module name to run
- `args` (list[str]): Arguments to pass to module
- `cwd` (Optional[Path]): Working directory
- `show_output` (bool): Whether to display output

**Returns:** Same format as `run_command()`

```python
def check_tool_available(self, tool: str) -> bool
```

Check if a command-line tool is available in PATH.

**Parameters:**
- `tool` (str): Tool name to check

**Returns:** `bool` - True if tool is in PATH

```python
def get_system_info(self) -> dict[str, str]
```

Get system information for diagnostics.

**Returns:** `dict[str, str]` with keys:
- `python_version`: Full Python version string
- `python_executable`: Path to Python interpreter
- `platform`: Platform identifier
- `cwd`: Current working directory
- `{tool}_available`: Availability status for common tools (git, npm, docker, etc.)

```python
def run_diagnostic(self) -> None
```

Run system diagnostic and display formatted results as a table.

**Side Effects**: Prints formatted diagnostic table to stdout

### Interactive Shell Class

```python
class InteractiveShell(cmd.Cmd):
    def __init__(self) -> None
```

Interactive shell for exploring the Codomyrmex ecosystem with command-line interface.

**Attributes:**
- `prompt`: Shell prompt string ("🐜 codomyrmex> ")
- `intro`: Welcome message
- `session_data`: Dictionary tracking session statistics

**Key Commands** (implemented as `do_*` methods):
- `explore [module_name]`: Explore modules
- `capabilities [type]`: Show capabilities
- `demo [module_name]`: Run demonstrations
- `status`: Show system health
- `forage [search_term]`: Search for capabilities
- `dive <module_name>`: Deep dive into module
- `session`: Show session stats
- `quit/exit`: Exit shell

### Utility Functions

```python
def create_ascii_art(text: str, style: str = "simple") -> str
```

Create ASCII art for text.

**Parameters:**
- `text` (str): Text to convert
- `style` (str): Art style ("simple" or "block"). Defaults to "simple"

**Returns:** `str` - ASCII art representation

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `terminal_utils.py` – Terminal formatting and utility functions
- `interactive_shell.py` – Interactive shell capabilities

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for terminal interactions
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies (rich, colorama, etc.)
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite

## Operating Contracts

### Universal Terminal Protocols

All terminal interactions within the Codomyrmex platform must:

1. **Consistent Formatting** - Use unified color schemes and message formats
2. **Accessibility Aware** - Support different terminal capabilities and preferences
3. **User-Friendly** - Provide clear, actionable messages and prompts
4. **Progress Transparency** - Show progress for operations that take time
5. **Error Clarity** - Present errors with specific resolution steps

### Module-Specific Guidelines

#### Output Formatting
- Use consistent color schemes for different message types
- Support both interactive and non-interactive output modes
- Provide options for plain text output when colors aren't available
- Include timestamps for log-style output when appropriate

#### User Interaction
- Validate user input with clear error messages
- Provide default values and help text for prompts
- Support both interactive and automated input modes
- Handle interruption signals gracefully

#### Progress Indication
- Use progress bars for operations expected to take more than a few seconds
- Provide estimated completion times when possible
- Support cancellation of long-running operations
- Update progress indicators frequently for responsiveness

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification

### Related Modules
- **CLI Integration**: Main package CLI components

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **Output Standardization** - Ensure consistent terminal output across modules
2. **Progress Integration** - Coordinate progress indicators for multi-module operations
3. **Error Propagation** - Use consistent error formatting and messaging
4. **User Experience** - Maintain consistent interaction patterns

### Quality Gates

Before terminal interface changes are accepted:

1. **Cross-Platform Tested** - Works on supported operating systems and terminals
2. **Accessibility Verified** - Functions correctly with different terminal settings
3. **Color Compatibility Checked** - Gracefully handles monochrome terminals
4. **Performance Optimized** - Output formatting doesn't significantly impact performance
5. **User Experience Validated** - Interface is intuitive and user-friendly

## Version History

- **v0.1.0** (December 2025) - Initial terminal interface system with rich formatting and interactive capabilities
