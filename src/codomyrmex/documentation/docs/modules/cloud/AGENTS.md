# Cloud -- Agent Integration Guide

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Agent Capabilities

The Cloud module provides agents with cloud resource management through 3 MCP tools.

## Available MCP Tools

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `list_cloud_instances` | List cloud compute instances | Safe |
| `list_s3_buckets` | List S3 storage buckets | Safe |
| `upload_file_to_s3` | Upload a file to S3 | Destructive (requires trust) |

## Trust Level

`upload_file_to_s3` is a destructive tool requiring TRUSTED trust level. The listing tools are Safe.

## Navigation

- **Source**: [src/codomyrmex/cloud/](../../../../src/codomyrmex/cloud/)
- **Extended README**: [README.md](readme.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Parent**: [All Modules](../README.md)
