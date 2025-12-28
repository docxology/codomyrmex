# Changelog for Logging Monitoring

All notable changes to this module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Option for structured JSON log output via `CODOMYRMEX_LOG_OUTPUT_TYPE` environment variable. Includes a `JsonFormatter`.
- Enhanced logging capabilities with `log_with_context()` function for structured context logging
- `create_correlation_id()` function for generating unique correlation IDs for request tracing
- `LogContext` class - context manager for automatic correlation ID injection in logs
- `PerformanceLogger` class - specialized logger for performance metrics and operation timing with timer functionality

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