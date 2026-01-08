# utils - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Shared utilities for Codomyrmex orchestrator scripts. Provides common functions and patterns used across all orchestrator scripts to ensure consistency and reduce code duplication.

## Design Principles

### Consistency
- Uniform error handling patterns
- Standardized output formatting
- Common CLI argument patterns

### Reusability
- Generic utilities usable across all scripts
- No script-specific logic
- Clear, focused function responsibilities

### Reliability
- Robust error handling
- Path validation
- Safe file operations

## Functional Requirements

### Progress Reporting
- Support progress bars with customizable prefixes/suffixes
- ETA calculation for long-running operations
- Throttled updates to avoid output spam

### Error Handling
- Context managers for enhanced error reporting
- Correlation IDs for error tracking
- Consistent error message formatting

### Output Formatting
- Table formatting with automatic column width calculation
- JSON and text output formats
- Colored terminal output (when supported)

### File Operations
- JSON file loading with error handling
- JSON file saving with parent directory creation
- Path validation (file/directory existence checks)

### CLI Utilities
- Common argument parsing (dry-run, verbose, quiet, format)
- Dry-run mode validation and planning
- Consistent argument extraction

## Interface Contracts

### ProgressReporter
- Initialize with total steps, prefix, suffix
- Update progress incrementally or set absolute value
- Display progress with optional status messages
- Mark completion with final message

### File Operations
- All file operations validate paths before execution
- JSON operations handle encoding/decoding errors gracefully
- Path validation raises appropriate exceptions

### Output Functions
- All print functions support optional context
- Color output only when TTY is detected
- Consistent message formatting across all output types

## Implementation Guidelines

1. All functions should handle errors gracefully
2. Use type hints for all public functions
3. Provide docstrings following Google/NumPy style
4. Log operations using the centralized logging system
5. Support both interactive and non-interactive environments

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)



<!-- Navigation Links keyword for score -->
