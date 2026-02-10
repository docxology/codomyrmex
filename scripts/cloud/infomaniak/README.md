# Infomaniak Cloud Examples

Comprehensive example scripts demonstrating all Infomaniak Public Cloud service clients.

## Prerequisites

```bash
uv pip install openstacksdk boto3
```

## Environment Setup

```bash
export INFOMANIAK_APP_CREDENTIAL_ID="your-app-credential-id"
export INFOMANIAK_APP_CREDENTIAL_SECRET="your-app-credential-secret"
export INFOMANIAK_AUTH_URL="https://api.pub1.infomaniak.cloud/identity/v3/"
export INFOMANIAK_REGION="dc3-a"

# For S3-compatible storage
export INFOMANIAK_S3_ACCESS_KEY="your-s3-access-key"
export INFOMANIAK_S3_SECRET_KEY="your-s3-secret-key"
export INFOMANIAK_S3_ENDPOINT="https://s3.pub1.infomaniak.cloud/"
```

## Scripts

| Script | Service | Description |
|--------|---------|-------------|
| `compute_examples.py` | Compute (Nova) | Instances, flavors, keypairs |
| `block_storage_examples.py` | Block Storage (Cinder) | Volumes, snapshots |
| `network_examples.py` | Network (Neutron) | Networks, routers, security groups |
| `object_storage_examples.py` | Object Storage | Swift and S3 operations |
| `identity_examples.py` | Identity (Keystone) | Users, credentials |
| `dns_examples.py` | DNS (Designate) | Zones, records |
| `orchestration_examples.py` | Orchestration (Heat) | Stack management |
| `metering_examples.py` | Metering | Usage and quotas |
| `newsletter_examples.py` | Newsletter API | Campaigns, mailing lists, contacts |
| `full_workflow.py` | All Services | Complete deployment workflow |

## Quick Start

```bash
# Check status
python compute_examples.py --list-instances

# S3 example
python object_storage_examples.py --s3 --list-buckets

# Newsletter example
export INFOMANIAK_NEWSLETTER_TOKEN="your-oauth2-token"
export INFOMANIAK_NEWSLETTER_ID="your-newsletter-id"
python newsletter_examples.py --list-campaigns
python newsletter_examples.py --send-test --campaign 123 --email test@activeinference.tech
```

---

**Navigation**: [Parent README](../README.md) | [Cloud Module](../../../src/codomyrmex/cloud/infomaniak/README.md)
