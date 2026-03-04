# Cloud -- Configuration Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the cloud module. Cloud service integrations including Coda.

## Configuration Requirements

Before using cloud in any PAI workflow, ensure:

1. `AZURE_STORAGE_ACCOUNT_URL` is set -- Azure Storage account URL
2. `INFOMANIAK_APP_CREDENTIAL_ID` is set -- Infomaniak API credential ID
3. `INFOMANIAK_APP_CREDENTIAL_SECRET` is set -- Infomaniak API credential secret
4. `INFOMANIAK_AUTH_URL` is set (default: `https://api.infomaniak.com/1/auth`) -- Infomaniak authentication endpoint
5. `INFOMANIAK_PROJECT_ID` is set -- Infomaniak project identifier
6. `INFOMANIAK_S3_ACCESS_KEY` is set -- Infomaniak S3 access key
7. `INFOMANIAK_S3_SECRET_KEY` is set -- Infomaniak S3 secret key
8. `INFOMANIAK_S3_ENDPOINT` is set -- Infomaniak S3 endpoint URL
9. `INFOMANIAK_S3_REGION` is set -- Infomaniak S3 region

## Agent Instructions

1. Verify required environment variables are set before invoking cloud tools
2. Use `get_config("cloud.<key>")` from config_management to read module settings
3. Available MCP tools: `list_cloud_instances`, `list_s3_buckets`, `upload_file_to_s3`
4. Each cloud provider requires its own credentials. AWS uses standard boto3 credential chain. Infomaniak uses OpenStack Keystone authentication.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("cloud.setting")

# Update configuration
set_config("cloud.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/cloud/AGENTS.md)
