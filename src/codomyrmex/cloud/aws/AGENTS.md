# Codomyrmex Agents — cloud/aws

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

AWS service integrations including S3, EC2 (planned), and Lambda (planned).

## Active Components

| Component | Type | Status |
|-----------|------|--------|
| `S3Client` | Class | Active |
| `storage/` | Module | Planned |
| `compute/` | Module | Planned |
| `serverless/` | Module | Planned |

## Operating Contracts

```python
from codomyrmex.cloud import S3Client

# Check availability
if S3Client is None:
    print("boto3 not installed")
else:
    client = S3Client()
```

## Navigation

- **📁 Parent**: [cloud/](../README.md)
- **📖 Specification**: [SPEC.md](SPEC.md)
