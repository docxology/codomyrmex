# Personal AI Infrastructure - Cloud Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: cloud  
**Status**: Active

## Context

Cloud provider integrations for AWS, GCP, Azure, Coda.io, and Infomaniak with unified abstractions for storage, compute, serverless, DNS, orchestration, metering, and newsletter operations. Infomaniak provides Swiss-hosted, GDPR-compliant cloud infrastructure.

## AI Agent Strategy

When working with this module as an AI agent:

### 1. Provider Selection

```python
# Evaluate available providers
from codomyrmex.cloud import S3Client, GCSClient, AzureBlobClient

available = []
if S3Client: available.append("aws")
if GCSClient: available.append("gcp")
if AzureBlobClient: available.append("azure")

from codomyrmex.cloud import InfomaniakComputeClient
if InfomaniakComputeClient: available.append("infomaniak")

# Choose based on context or preference
```

### 2. Unified Operations

All storage clients share common patterns:

| Operation | AWS | GCP | Azure |
|-----------|-----|-----|-------|
| Upload | `upload_file()` | `upload_blob()` | `upload_blob()` |
| Download | `download_file()` | `download_blob()` | `download_blob()` |
| List | `list_objects()` | `list_blobs()` | `list_blobs()` |
| Metadata | `get_metadata()` | `get_metadata()` | `get_metadata()` |
| Ensure | `ensure_bucket()` | `ensure_bucket()` | `ensure_container()` |

### 3. Error Handling Strategy

```python
# Wrap all cloud operations in try/except
try:
    client.upload_file(local, bucket, remote)
except Exception as e:
    # Log error, notify user, or retry
    logger.error(f"Cloud upload failed: {e}")
    return fallback_action()
```

### 4. Credential Management

- **AWS**: Use environment variables or IAM roles
- **GCP**: Use application default credentials or service account
- **Azure**: Use DefaultAzureCredential for automatic chain
- **Coda.io**: Pass API token to CodaClient constructor
- **Infomaniak**: Application Credentials for OpenStack; OAuth2 Bearer token for Newsletter

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public API exports |
| `common/__init__.py` | Abstract base classes |
| `coda_io/client.py` | Full Coda.io REST API client |
| `SPEC.md` | Technical specification |

## Best Practices

1. **Check Dependencies**: Verify client availability before use
2. **Use Logging**: Integrate with `logging_monitoring` module
3. **Handle Pagination**: List operations may return partial results
4. **Respect Rate Limits**: Especially for Coda.io API calls
5. **Clean Up**: Delete temporary cloud resources when done

## Future Considerations

- **Serverless**: Lambda, Cloud Functions, Azure Functions
- **Databases**: RDS, Cloud SQL, Azure SQL
- **Telemetry**: Emit metrics for cloud operations

## Navigation

- **Specification**: [SPEC.md](SPEC.md)
- **Agent Guide**: [AGENTS.md](AGENTS.md)
- **Parent**: [codomyrmex](../README.md)
