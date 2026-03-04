# Cloud Configuration Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Cloud service integrations including Coda.io, AWS S3, GCP Storage, Azure Blob, and Infomaniak OpenStack. Provides unified cloud resource management. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `AZURE_STORAGE_ACCOUNT_URL` | string | Yes | None | Azure Storage account URL |
| `INFOMANIAK_APP_CREDENTIAL_ID` | string | Yes | None | Infomaniak API credential ID |
| `INFOMANIAK_APP_CREDENTIAL_SECRET` | string | Yes | None | Infomaniak API credential secret |
| `INFOMANIAK_AUTH_URL` | string | No | `https://api.infomaniak.com/1/auth` | Infomaniak authentication endpoint |
| `INFOMANIAK_PROJECT_ID` | string | Yes | None | Infomaniak project identifier |
| `INFOMANIAK_S3_ACCESS_KEY` | string | Yes | None | Infomaniak S3 access key |
| `INFOMANIAK_S3_SECRET_KEY` | string | Yes | None | Infomaniak S3 secret key |
| `INFOMANIAK_S3_ENDPOINT` | string | Yes | None | Infomaniak S3 endpoint URL |
| `INFOMANIAK_S3_REGION` | string | Yes | None | Infomaniak S3 region |

## Environment Variables

```bash
# Required
export AZURE_STORAGE_ACCOUNT_URL=""    # Azure Storage account URL
export INFOMANIAK_APP_CREDENTIAL_ID=""    # Infomaniak API credential ID
export INFOMANIAK_APP_CREDENTIAL_SECRET=""    # Infomaniak API credential secret
export INFOMANIAK_PROJECT_ID=""    # Infomaniak project identifier
export INFOMANIAK_S3_ACCESS_KEY=""    # Infomaniak S3 access key
export INFOMANIAK_S3_SECRET_KEY=""    # Infomaniak S3 secret key
export INFOMANIAK_S3_ENDPOINT=""    # Infomaniak S3 endpoint URL
export INFOMANIAK_S3_REGION=""    # Infomaniak S3 region

# Optional (defaults shown)
export INFOMANIAK_AUTH_URL="https://api.infomaniak.com/1/auth"    # Infomaniak authentication endpoint
```

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- `AZURE_STORAGE_ACCOUNT_URL` must be set before module initialization
- `INFOMANIAK_APP_CREDENTIAL_ID` must be set before module initialization
- `INFOMANIAK_APP_CREDENTIAL_SECRET` must be set before module initialization
- `INFOMANIAK_PROJECT_ID` must be set before module initialization
- `INFOMANIAK_S3_ACCESS_KEY` must be set before module initialization
- `INFOMANIAK_S3_SECRET_KEY` must be set before module initialization
- `INFOMANIAK_S3_ENDPOINT` must be set before module initialization
- `INFOMANIAK_S3_REGION` must be set before module initialization
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/cloud/SPEC.md)
