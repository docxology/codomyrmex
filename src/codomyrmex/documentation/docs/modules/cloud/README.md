<!-- readme: generated -->

# cloud

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/cloud/`

## Overview

Cloud Services Module for Codomyrmex.

This module provides integrations with various cloud service APIs including:
- Coda.io: Document and database API for Coda docs
- AWS: Amazon Web Services (S3)
- GCP: Google Cloud Platform (GCS)
- Azure: Microsoft Azure (Blob Storage)
- Infomaniak: OpenStack-based public cloud (Compute, Storage, Network, DNS, etc.)

The module is organized into submodules for each cloud service:
- coda_io: Coda.io REST API v1 client
- aws: AWS S3 client
- gcp: GCP Storage client
- azure: Azure Blob client
- infomaniak: Infomaniak Public Cloud clients (Nova, Cinder, Neutron, Swift, S3, Keystone, Designate, Heat)
- common: Shared cloud utilities

Usage:
    from codomyrmex.cloud import CodaClient

    client = CodaClient(api_token="your-api-token")
    docs = client.list_docs()

## Submodules

| Submodule | Description |
|-----------|-------------|
| `common:` | Shared cloud utilities. |

## Public Exports

`cloud` exports 54 public symbols via `__all__`:

`ACLSettings`, `AzureBlobClient`, `CellEdit`, `CodaAPIError`, `CodaAuthenticationError`, `CodaClient`, `CodaForbiddenError`, `CodaGoneError`, `CodaNotFoundError`, `CodaRateLimitError`, `CodaValidationError`, `Column`, `ColumnList`, `Control`, `ControlList`, `Doc`, `DocList`, `DocSize`, `FolderReference`, `Formula`, `FormulaList`, `GCSClient`, `Icon`, `InfomaniakComputeClient` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../cloud/](../../../../cloud/)
