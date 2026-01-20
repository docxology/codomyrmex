# cloud

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

The `cloud` module provides a unified interface for interacting with major cloud providers (AWS, GCP, Azure). It abstracts object storage operations across providers, enabling portable cloud-agnostic workflows.

## Key Features

- **Multi-Cloud Support**: Unified clients for AWS S3, Google Cloud Storage, and Azure Blob Storage.
- **Atomic Operations**: Simplified upload, download, and metadata retrieval.
- **Resource Orchestration**: Automatic container/bucket existence checks and creation.
- **Provider Agnostic**: Consistent API signatures across different cloud SDKs.

## Module Structure

- `aws/` – AWS S3 client implementation.
- `gcp/` – Google Cloud Storage client implementation.
- `azure/` – Azure Blob Storage client implementation.
- `coda_io/` – Data ingestion and IO utilities for cloud datasets.

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
