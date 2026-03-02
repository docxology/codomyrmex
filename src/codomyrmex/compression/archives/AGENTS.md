# Codomyrmex Agents -- src/codomyrmex/compression/archives

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides multi-format archive creation and extraction supporting ZIP, TAR, and TAR.GZ formats. The `ArchiveManager` class bundles files into compressed archives and extracts them, with automatic format detection based on file extension.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `archive_manager.py` | `ArchiveManager` | Creates and extracts ZIP, TAR, and TAR.GZ archives |
| `archive_manager.py` | `ArchiveManager.create_archive` | Bundles a list of `Path` objects into an archive with a specified format |
| `archive_manager.py` | `ArchiveManager.extract_archive` | Extracts archive contents to a target directory |
| `archive_manager.py` | `CompressionError` | Domain-specific error raised when archive operations fail |

## Operating Contracts

- Archives are created using `zipfile.ZipFile` (ZIP) or `tarfile.open` (TAR/TAR.GZ) from the Python standard library.
- Only files that exist on disk are included when creating archives; missing files are silently skipped.
- Format detection during extraction is based on the archive file extension (`.zip`, `.tar`, `.gz`, `.tar.gz`).
- All errors are logged via `logging_monitoring` before being re-raised as `CompressionError`.
- The output directory for extraction is created automatically via `mkdir(parents=True, exist_ok=True)`.

## Integration Points

- **Depends on**: `codomyrmex.exceptions.CodomyrmexError`, `codomyrmex.logging_monitoring.core.logger_config`
- **Used by**: Higher-level compression utilities, CI/CD artifact packaging, backup workflows

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
