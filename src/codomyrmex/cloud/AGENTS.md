# Codomyrmex Agents — cloud

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `cloud` module enables agents to interact with distributed object storage. It provides a unified interface for data persistence, artifact management, and dataset orchestration across AWS, GCP, and Azure.

## Active Components

- `aws.S3Client` – High-level wrapper for Amazon S3.
- `gcp.GCSClient` – High-level wrapper for Google Cloud Storage.
- `azure.AzureBlobClient` – High-level wrapper for Azure Blob Storage.
- `coda_io/` – Specialized IO utilities for large-scale data processing in the cloud.

## Operating Contracts

1. **Provider Neutrality**: Agents should use abstract client interfaces where possible to ensure provider portability.
2. **Error Handling**: Gracefully handle provider-specific exceptions (e.g., `ClientError`, `StorageException`).
3. **Resource Lifecycle**: Always check for resource existence before attempting operations.

## Core Interfaces

- `upload_file(...)` / `download_file(...)`: Atomic data transfer.
- `get_metadata(...)`: Retrieve object properties without downloading content.
- `ensure_bucket(...)` / `ensure_container(...)`: idempotent resource creation.

## Navigation Links

- **🏠 Project Root**: ../../../README.md
- **📦 Module README**: ./README.md
- **📜 Functional Spec**: ./SPEC.md
