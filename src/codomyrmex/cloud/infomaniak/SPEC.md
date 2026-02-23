# infomaniak - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Integration with Infomaniak Public Cloud, an OpenStack-based infrastructure providing compute, storage, networking, and supporting services in Swiss data centers.

## Design Principles

### 1. OpenStack Native

- Uses standard OpenStack APIs (Nova, Cinder, Neutron, Swift, Keystone, Designate, Heat)
- Compatible with upstream OpenStack tooling and Terraform providers
- Application Credentials for secure, scoped authentication

### 2. Three Auth Base Classes

- `InfomaniakOpenStackBase`: OpenStack SDK with Application Credentials (compute, network, storage, DNS, orchestration, metering, identity)
- `InfomaniakS3Base`: boto3 S3 with access key / secret key (S3-compatible storage)
- `InfomaniakRESTBase`: REST API with OAuth2 Bearer token (Newsletter API)

### 3. Dual Object Storage

- Swift API via openstacksdk for native OpenStack operations
- S3-compatible API via boto3 for broad tooling compatibility

### 4. Consistency

- Follows existing cloud module patterns (AWS, GCP, Azure)
- Uniform error handling and logging
- Optional dependency handling with graceful degradation

## Architecture

```mermaid
graph TD
    subgraph "Infomaniak Module"
        Init[__init__.py]
        Auth[auth.py]
        
        Compute[compute/] --> Nova[Nova API]
        BlockStorage[block_storage/] --> Cinder[Cinder API]
        Network[network/] --> Neutron[Neutron API]
        ObjStorage[object_storage/] --> Swift[Swift API]
        ObjStorage --> S3[S3 API]
        Identity[identity/] --> Keystone[Keystone API]
        DNS[dns/] --> Designate[Designate API]
        Orch[orchestration/] --> Heat[Heat API]
        Meter[metering/] --> Aggregation[Resource Aggregation]
    end
    
    Auth --> Init
    openstack[openstacksdk] -.-> Compute & BlockStorage & Network & ObjStorage & Identity & DNS & Orch & Meter
    boto3[boto3] -.-> S3
```

## Functional Requirements

### FR-1: Compute Operations

- List, create, start, stop, reboot, delete, terminate instances
- Get instance details
- List images, get image by ID, list flavors, list availability zones
- Key pair management (create, delete, list)

### FR-2: Block Storage

- Volume CRUD operations (list, create, get, delete)
- Attach/detach volumes to instances
- Extend volume size
- List, create, delete snapshots
- Backup and restore

### FR-3: Networking

- Network and subnet management (CRUD)
- Router operations with external gateway (create, delete, add/remove interface)
- Security groups and rules (create, delete, add rules)
- Floating IP operations (allocate, release, associate, disassociate)
- Load balancer (Octavia) operations:
  - Load balancer CRUD
  - Listener CRUD
  - Pool CRUD
  - Pool member add/remove/list
  - Health monitor CRUD

### FR-4: Object Storage

- Swift container and object management
- S3-compatible bucket and object operations
- ACL management
- Presigned URL generation

### FR-5: Identity

- Application credential management
- EC2 credential management (for S3 access)
- User and project info retrieval

### FR-6: DNS

- Zone management (Designate) — CRUD
- Record set CRUD (list, create, update, delete)
- Reverse DNS (PTR record) management (list, set, delete)

### FR-7: Orchestration

- Heat stack CRUD (create, get, update, delete, list)
- Template validation
- Stack event and resource listing
- Stack suspend and resume
- Stack outputs retrieval

### FR-8: Metering

- Usage data retrieval
- Billing summary

### FR-9: Newsletter Operations

- Campaign CRUD (create, read, update, delete)
- Send test emails and live campaigns
- Schedule and unschedule campaigns
- Campaign statistics (opens, clicks, bounces)
- Mailing list management (CRUD)
- Contact import, subscribe/unsubscribe
- Credit balance retrieval
- Async task status checking

## Technical Constraints

### Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| `openstacksdk` | OpenStack services | Optional |
| `boto3` | S3-compatible storage | Optional |
| `requests` | Newsletter REST API (InfomaniakRESTBase) | Required for RESTBase |

### Endpoints

| Service | URL |
|---------|-----|
| Identity | `https://api.pub1.infomaniak.cloud/identity/v3/` |
| S3 | `https://s3.pub1.infomaniak.cloud/` |

### Python Version

- Python 3.10+ for modern type hints
- Full typing with `py.typed` marker

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [cloud/](../README.md)
