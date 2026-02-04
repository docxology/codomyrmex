# Infomaniak Examples Specification

## Overview

CLI example scripts demonstrating all Infomaniak Public Cloud service clients.

## Purpose

Provide ready-to-use orchestrator scripts for all Infomaniak OpenStack and S3 operations with:

- Full CLI argument parsing
- Colorful console output
- Error handling with helpful messages
- Environment-based authentication

## Scripts

| Script | Methods Demonstrated |
|--------|---------------------|
| `compute_examples.py` | 13 methods (instances, flavors, images, keypairs, zones) |
| `block_storage_examples.py` | 13 methods (volumes, snapshots, backups) |
| `network_examples.py` | 18 methods (networks, routers, security groups, floating IPs, LBs) |
| `object_storage_examples.py` | 25 methods (Swift + S3 operations) |
| `identity_examples.py` | 14 methods (users, projects, credentials, roles) |
| `dns_examples.py` | 14 methods (zones, records, reverse DNS) |
| `orchestration_examples.py` | 15 methods (Heat stacks, templates) |
| `metering_examples.py` | 10 methods (usage, quotas) |
| `newsletter_examples.py` | 12 methods (campaigns, mailing lists, contacts, credits) |
| `full_workflow.py` | Multi-service deployment workflow |

## Environment Variables

```bash
# OpenStack credentials
INFOMANIAK_APP_CREDENTIAL_ID
INFOMANIAK_APP_CREDENTIAL_SECRET
INFOMANIAK_AUTH_URL
INFOMANIAK_REGION

# S3 credentials
INFOMANIAK_S3_ACCESS_KEY
INFOMANIAK_S3_SECRET_KEY
INFOMANIAK_S3_ENDPOINT

# Newsletter credentials
INFOMANIAK_NEWSLETTER_TOKEN
INFOMANIAK_NEWSLETTER_ID
```

---

**Navigation**: [README](README.md) | [Cloud Scripts](../README.md)
