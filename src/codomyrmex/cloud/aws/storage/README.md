# AWS Storage Submodule

**Version**: v0.2.0 | **Status**: Planned | **Last Updated**: February 2026

## Overview

Extended AWS S3 storage utilities including multipart uploads, transfer acceleration, and lifecycle management.

## Planned Features

- Multipart upload for large files
- Transfer acceleration configuration
- Lifecycle policy management
- Cross-region replication setup
- Versioning and object lock

## Current Implementation

The `S3Client` in `aws/__init__.py` provides core operations:

- `upload_file`, `download_file`, `list_objects`, `get_metadata`, `ensure_bucket`

## Navigation

- **Parent**: [aws/](../README.md)
- **Cloud Root**: [cloud/](../../README.md)
