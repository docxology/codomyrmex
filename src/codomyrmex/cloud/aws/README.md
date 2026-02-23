# AWS Integration Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Amazon Web Services integration providing S3 object storage, with planned support for EC2 compute and Lambda serverless.

## Components

| Component | Status | Description |
|-----------|--------|-------------|
| `S3Client` | ✅ Active | S3 object storage operations |
| `storage/` | Planned | Extended storage utilities |
| `compute/` | Planned | EC2 instance management |
| `serverless/` | Planned | Lambda function management |

## Quick Start

```python
from codomyrmex.cloud.aws import S3Client

# Uses boto3 default credential chain
client = S3Client(region_name="us-west-2")

# Upload
client.upload_file("local.txt", "my-bucket", "remote.txt")

# List
for obj in client.list_objects("my-bucket"):
    print(obj)

# Download
client.download_file("my-bucket", "remote.txt", "downloaded.txt")
```

## Authentication

Uses boto3 credential chain:

1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS config file (`~/.aws/credentials`)
3. IAM instance role (EC2/ECS/Lambda)

## Dependencies

```bash
uv add boto3
```

## Directory Structure

| Path | Description |
|------|-------------|
| `__init__.py` | S3Client implementation |
| `storage/` | Extended storage operations |
| `compute/` | EC2 operations (planned) |
| `serverless/` | Lambda operations (planned) |

## Navigation

- **Parent**: [cloud/](../README.md)
- **Specification**: [SPEC.md](SPEC.md)
