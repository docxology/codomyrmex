# Codomyrmex Agents — cloud/infomaniak

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

AI agent integration guide for Infomaniak Public Cloud services.

## Active Components

| Component | Description |
|-----------|-------------|
| `auth.py` | Credential management and connection factories |
| `compute/` | Instance lifecycle and compute resources |
| `block_storage/` | Volume and backup operations |
| `network/` | Networking, security, load balancing |
| `object_storage/` | Swift and S3 object storage |
| `identity/` | Application credentials and EC2 credentials |
| `dns/` | DNS zones and reverse DNS |
| `orchestration/` | Heat stack management |
| `metering/` | Billing and usage data |
| `newsletter/` | Campaign and mailing list management |

## Operating Contracts

- Use Application Credentials (never raw user passwords)
- Handle openstacksdk ImportError gracefully
- Log all operations via module logger
- Return consistent types (List[Dict], bool, Dict)

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `INFOMANIAK_APP_CREDENTIAL_ID` | Application credential ID |
| `INFOMANIAK_APP_CREDENTIAL_SECRET` | Application credential secret |
| `INFOMANIAK_AUTH_URL` | Identity endpoint override |
| `INFOMANIAK_S3_ACCESS_KEY` | S3 access key |
| `INFOMANIAK_S3_SECRET_KEY` | S3 secret key |
| `INFOMANIAK_NEWSLETTER_TOKEN` | OAuth2 bearer token for Newsletter API |
| `INFOMANIAK_NEWSLETTER_ID` | Newsletter product ID |

## Navigation Links

- **📁 Parent Directory**: [cloud/](../AGENTS.md)
- **🏠 Project Root**: ../../../../README.md
