# Cloud -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Coda.io Integration
- Full REST API v1 client covering docs, pages, tables, columns, rows, formulas, controls, permissions.
- Authentication via API token.

### FR-2: Multi-Cloud Storage
- S3Client, GCSClient, AzureBlobClient shall provide unified file upload/download/list operations.
- Providers shall be lazy-loaded; unavailable SDKs set exports to None.

### FR-3: Infomaniak
- OpenStack-based clients for compute, volumes, networking, object storage, DNS, orchestration.
- S3-compatible storage via InfomaniakS3Client.

## Navigation

- **Source**: [src/codomyrmex/cloud/](../../../../cloud/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
