# Languages Module - Programmable AI Interface (PAI)

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Module Identity

- **Name**: languages
- **Category**: Development Tooling
- **Dependencies**: logging_monitoring, environment_setup

## Capabilities

### Primary Functions

1. **Language Environment Detection**
   - Input: Language name (e.g., "python", "rust", "go")
   - Output: Installation status, version, path
   - Supported: Python, JavaScript/Node, TypeScript, Go, Rust, Ruby, Java, C++, C#, PHP, Elixir, Swift, Bash, R

2. **Installation Instructions**
   - Input: Language name + platform
   - Output: Platform-specific installation commands
   - Platforms: macOS, Linux, Windows

3. **Language-Specific Tooling**
   - Per-language subdirectories with helper utilities
   - Formatters, linters, and build tool detection

### Supported Languages

```
bash/       cpp/        csharp/     elixir/
go/         java/       javascript/ php/
python/     r/          ruby/       rust/
swift/      typescript/
```

## Interface Contracts

### MCP Tools

```python
@mcp_tool
def check_language_installed(language: str) -> dict:
    """Check if a programming language is installed and return version info."""

@mcp_tool
def get_installation_instructions(language: str, platform: str = "auto") -> str:
    """Get platform-specific installation instructions for a language."""

@mcp_tool  
def list_supported_languages() -> list[str]:
    """List all supported programming languages."""
```

## Integration Points

### Upstream Dependencies

- `logging_monitoring` — Logging infrastructure
- `environment_setup` — System environment detection

### Downstream Consumers

- `agents` — Language-aware code generation
- `coding` — Multi-language code execution
- `static_analysis` — Language-specific linting

## MCP Tools

This module exposes tools via `mcp_tools.py`:

- `check_language_installed` — Detect if a language runtime is available
- `get_installation_instructions` — Provide setup guidance
- `list_supported_languages` — Enumerate supported languages

## Versioning

- Part of the Core architectural layer
- Language subdirectory additions are minor versions
