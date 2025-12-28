# Changelog for Code Execution Sandbox

All notable changes to this module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial module structure and comprehensive documentation (README.md, API_SPECIFICATION.md, MCP_TOOL_SPECIFICATION.md, SECURITY.md, USAGE_EXAMPLES.md, CHANGELOG.md).
- Defined `execute_code` function and MCP tool with detailed specifications for secure code execution.
- Outlined support for multiple languages (Python, JavaScript, Bash) via Docker-based sandboxing.
- Specified resource limiting (memory, CPU, processes, network, filesystem) and error handling.
- Enhanced execution capabilities with `execute_with_limits()` function for configurable resource limits
- Added `sandbox_process_isolation()` function for complete subprocess isolation
- Implemented `ExecutionLimits` dataclass for structured resource limit configuration
- Added `ResourceMonitor` class for comprehensive resource usage tracking during execution

### Changed
- 

### Deprecated
- 

### Removed
- 

### Fixed
- 

### Security
- 

## [Version X.Y.Z] - YYYY-MM-DD

### Added
- Feature A.

### Changed
- Enhancement B.

### Fixed
- Bug C. 