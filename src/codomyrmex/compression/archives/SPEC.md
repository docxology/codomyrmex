# Archives -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides multi-format archive creation and extraction using Python standard library modules (`zipfile`, `tarfile`). Supports ZIP, TAR, and TAR.GZ formats for bundling and unbundling collections of files.

## Architecture

Single-class design centered on `ArchiveManager`, which delegates to `zipfile.ZipFile` for ZIP archives and `tarfile.open` for TAR/TAR.GZ archives. Format selection is explicit on creation and inferred from extension on extraction.

## Key Classes

### `ArchiveManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_archive` | `files: list[Path], output: Path, format: str = "zip"` | `bool` | Creates an archive containing the listed files. Supported formats: `zip`, `tar`, `tar.gz`. |
| `extract_archive` | `archive: Path, output: Path` | `bool` | Extracts archive contents to `output` directory. Format inferred from extension. |

### `CompressionError`

Inherits from `CodomyrmexError`. Raised when archive creation or extraction fails. Always logged before raising.

## Dependencies

- **Internal**: `codomyrmex.exceptions.CodomyrmexError`, `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `zipfile` (stdlib), `tarfile` (stdlib), `pathlib` (stdlib)

## Constraints

- Only existing files are added to archives; missing paths are silently skipped during creation.
- The output directory for extraction is auto-created via `mkdir(parents=True, exist_ok=True)`.
- Unknown archive formats raise `ValueError` (creation) or `CompressionError` (extraction).
- ZIP archives use `ZIP_DEFLATED` compression.
- Zero-mock: real filesystem operations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- All exceptions during archive operations are caught, logged via `logger.error`, and re-raised as `CompressionError` with the original exception chained (`from e`).
