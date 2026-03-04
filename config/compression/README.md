# Compression Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Data compression utilities and archive handling supporting gzip, zlib, ZIP, and Zstandard formats. Provides configurable compression levels, stream-based compression, and parallel compression.

## Configuration Options

The compression module operates with sensible defaults and does not require environment variable configuration. Compression level (1-9 for gzip/zlib, 1-22 for zstd) and algorithm are set per-operation. ParallelCompressor uses system CPU count by default.

## PAI Integration

PAI agents interact with compression through direct Python imports. Compression level (1-9 for gzip/zlib, 1-22 for zstd) and algorithm are set per-operation. ParallelCompressor uses system CPU count by default.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep compression

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/compression/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
