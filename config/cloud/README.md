# Cloud Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Cloud service integrations including Coda.io, AWS S3, GCP Storage, Azure Blob, and Infomaniak OpenStack. Provides unified cloud resource management.

## Quick Configuration

```bash
export AZURE_STORAGE_ACCOUNT_URL=""    # Azure Storage account URL (required)
export INFOMANIAK_APP_CREDENTIAL_ID=""    # Infomaniak API credential ID (required)
export INFOMANIAK_APP_CREDENTIAL_SECRET=""    # Infomaniak API credential secret (required)
export INFOMANIAK_AUTH_URL="https://api.infomaniak.com/1/auth"    # Infomaniak authentication endpoint
export INFOMANIAK_PROJECT_ID=""    # Infomaniak project identifier (required)
export INFOMANIAK_S3_ACCESS_KEY=""    # Infomaniak S3 access key (required)
export INFOMANIAK_S3_SECRET_KEY=""    # Infomaniak S3 secret key (required)
export INFOMANIAK_S3_ENDPOINT=""    # Infomaniak S3 endpoint URL (required)
export INFOMANIAK_S3_REGION=""    # Infomaniak S3 region (required)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `AZURE_STORAGE_ACCOUNT_URL` | str | None | Azure Storage account URL |
| `INFOMANIAK_APP_CREDENTIAL_ID` | str | None | Infomaniak API credential ID |
| `INFOMANIAK_APP_CREDENTIAL_SECRET` | str | None | Infomaniak API credential secret |
| `INFOMANIAK_AUTH_URL` | str | `https://api.infomaniak.com/1/auth` | Infomaniak authentication endpoint |
| `INFOMANIAK_PROJECT_ID` | str | None | Infomaniak project identifier |
| `INFOMANIAK_S3_ACCESS_KEY` | str | None | Infomaniak S3 access key |
| `INFOMANIAK_S3_SECRET_KEY` | str | None | Infomaniak S3 secret key |
| `INFOMANIAK_S3_ENDPOINT` | str | None | Infomaniak S3 endpoint URL |
| `INFOMANIAK_S3_REGION` | str | None | Infomaniak S3 region |

## MCP Tools

This module exposes 3 MCP tool(s):

- `list_cloud_instances`
- `list_s3_buckets`
- `upload_file_to_s3`

## PAI Integration

PAI agents invoke cloud tools through the MCP bridge. Each cloud provider requires its own credentials. AWS uses standard boto3 credential chain. Infomaniak uses OpenStack Keystone authentication.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep cloud

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/cloud/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
