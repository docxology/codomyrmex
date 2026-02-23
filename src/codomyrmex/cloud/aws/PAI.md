# Personal AI Infrastructure - cloud/aws

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: cloud/aws  
**Status**: Active

## Context

AWS integration using boto3 for S3, EC2, and Lambda operations.

## AI Agent Strategy

1. **Credential Check**: Verify `S3Client is not None` before use
2. **Region Selection**: Pass `region_name` for cross-region operations
3. **Error Handling**: All methods return `False` on failure; check return values

## Key Patterns

```python
from codomyrmex.cloud import S3Client

client = S3Client(region_name="us-east-1")

# Always check success
if client.upload_file("data.csv", "bucket", "data.csv"):
    print("Upload successful")
else:
    print("Upload failed - check logs")
```

## Navigation

- **Specification**: [SPEC.md](SPEC.md)
- **Parent**: [cloud/](../README.md)
