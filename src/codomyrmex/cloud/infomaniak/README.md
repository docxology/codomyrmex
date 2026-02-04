# Infomaniak Public Cloud Integration

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive integration with Infomaniak's OpenStack-based public cloud platform. Provides modular clients for all major cloud services.

| Service | Client | OpenStack API |
|---------|--------|---------------|
| Compute | `InfomaniakComputeClient` | Nova |
| Block Storage | `InfomaniakVolumeClient` | Cinder |
| Network | `InfomaniakNetworkClient` | Neutron/Octavia |
| Object Storage | `InfomaniakObjectStorageClient` | Swift |
| S3 Storage | `InfomaniakS3Client` | S3-compatible |
| Identity / EC2 | `InfomaniakIdentityClient` | Keystone |
| DNS | `InfomaniakDNSClient` | Designate |
| Orchestration | `InfomaniakHeatClient` | Heat |
| Metering | `InfomaniakMeteringClient` | Ceilometer |
| Newsletter | `InfomaniakNewsletterClient` | Infomaniak REST API |

## Quick Start

### Installation

```bash
# OpenStack SDK (for most services)
pip install openstacksdk

# boto3 (for S3-compatible storage)
pip install boto3
```

### Authentication

Create Application Credentials in the Infomaniak dashboard, then:

```python
import os
os.environ["INFOMANIAK_APP_CREDENTIAL_ID"] = "your-credential-id"
os.environ["INFOMANIAK_APP_CREDENTIAL_SECRET"] = "your-secret"

from codomyrmex.cloud.infomaniak import InfomaniakComputeClient

client = InfomaniakComputeClient.from_env()
instances = client.list_instances()
```

### S3 Object Storage

```python
os.environ["INFOMANIAK_S3_ACCESS_KEY"] = "your-s3-key"
os.environ["INFOMANIAK_S3_SECRET_KEY"] = "your-s3-secret"

from codomyrmex.cloud.infomaniak import InfomaniakS3Client

s3 = InfomaniakS3Client.from_env()
s3.upload_file("my-bucket", "key.txt", "local-file.txt")
```

## Endpoints

| Service | Endpoint |
|---------|----------|
| Identity (Keystone) | `https://api.pub1.infomaniak.cloud/identity/v3/` |
| S3 Object Storage | `https://s3.pub1.infomaniak.cloud/` |
| S3 (alternate) | `https://s3.pub2.infomaniak.cloud/` |

## Directory Structure

| Path | Description |
|------|-------------|
| `auth.py` | Authentication utilities and credentials |
| `compute/` | Instance, image, keypair, availability zone operations |
| `block_storage/` | Volume and backup operations |
| `network/` | Networks, routers, security groups, load balancers |
| `object_storage/` | Swift and S3-compatible storage clients |
| `identity/` | Application credentials, EC2 credentials, user info |
| `dns/` | DNS zones and reverse DNS (PTR records) |
| `orchestration/` | Heat stack operations |
| `metering/` | Billing and usage metrics |
| `newsletter/` | Newsletter campaign and mailing list management |

### Newsletter API

```python
os.environ["INFOMANIAK_NEWSLETTER_TOKEN"] = "your-oauth2-token"
os.environ["INFOMANIAK_NEWSLETTER_ID"] = "your-newsletter-product-id"

from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

client = InfomaniakNewsletterClient.from_env()
campaigns = client.list_campaigns()
client.send_test(campaign_id="123", email="test@activeinference.tech")
```

## Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | This file - overview and quick start |
| [SPEC.md](SPEC.md) | Functional specification |
| [AGENTS.md](AGENTS.md) | AI agent integration guide |
| [PAI.md](PAI.md) | Personal AI context |

## Navigation

- **Parent Module**: [cloud/](../README.md)
- **Full Documentation**: [docs/modules/cloud/](../../../../docs/modules/cloud/)
- **Project Root**: [../../../../README.md](../../../../README.md)
