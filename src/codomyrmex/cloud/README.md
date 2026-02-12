# Cloud Services Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Cloud Services module provides unified, provider-agnostic interfaces for interacting with cloud platforms:

| Provider | Component | Description |
|----------|-----------|-------------|
| **AWS** | `S3Client` | Amazon S3 object storage |
| **GCP** | `GCSClient` | Google Cloud Storage |
| **Azure** | `AzureBlobClient` | Azure Blob Storage |
| **Coda.io** | `CodaClient` | Document and database API |
| **Infomaniak** | `InfomaniakComputeClient`, `InfomaniakVolumeClient`, `InfomaniakNetworkClient`, `InfomaniakObjectStorageClient`, `InfomaniakS3Client`, `InfomaniakIdentityClient`, `InfomaniakDNSClient`, `InfomaniakHeatClient`, `InfomaniakMeteringClient`, `InfomaniakNewsletterClient` | Swiss-hosted OpenStack cloud (9 services) + Newsletter API |

All storage clients share a consistent interface pattern with operations for upload, download, list, metadata retrieval, and bucket/container management. Infomaniak clients provide compute, storage, networking, DNS, orchestration, metering, and newsletter services via OpenStack and Infomaniak REST APIs.

## Key Exports

### Clients
- **`CodaClient`** — Coda.io REST API v1 client with pagination and rate limiting
- **`S3Client`** — Amazon S3 object storage client (lazy-loaded, requires boto3)
- **`GCSClient`** — Google Cloud Storage client (lazy-loaded, requires google-cloud-storage)
- **`AzureBlobClient`** — Azure Blob Storage client (lazy-loaded, requires azure-storage-blob)
- **`InfomaniakComputeClient`** / **`InfomaniakVolumeClient`** / **`InfomaniakNetworkClient`** — Infomaniak compute, volume, and network clients
- **`InfomaniakObjectStorageClient`** / **`InfomaniakS3Client`** — Infomaniak Swift and S3-compatible storage clients
- **`InfomaniakIdentityClient`** / **`InfomaniakDNSClient`** / **`InfomaniakHeatClient`** / **`InfomaniakMeteringClient`** — Infomaniak identity, DNS, orchestration, and metering clients
- **`InfomaniakNewsletterClient`** — Infomaniak Newsletter REST API client

### Coda.io Data Models
- **`Doc`** — A Coda document
- **`DocList`** — Paginated list of Coda documents
- **`Page`** — A page in a Coda doc
- **`PageList`** — Paginated list of pages
- **`PageReference`** — Reference to a page (id, name, href)
- **`Table`** — A table in a Coda doc
- **`TableList`** — Paginated list of tables
- **`TableReference`** — Reference to a table (id, name, href)
- **`Column`** — A column in a Coda table
- **`ColumnList`** — Paginated list of columns
- **`Row`** — A row in a Coda table
- **`RowList`** — Paginated list of rows
- **`RowEdit`** — A row edit with cell values for upsert operations
- **`CellEdit`** — A cell value edit (column + value)
- **`Formula`** — A named formula in a Coda doc
- **`FormulaList`** — Paginated list of formulas
- **`Control`** — A control widget in a Coda doc
- **`ControlList`** — Paginated list of controls
- **`Permission`** — A permission on a doc
- **`PermissionList`** — Paginated list of permissions
- **`SharingMetadata`** — Sharing metadata for a doc (can_share, can_copy)
- **`ACLSettings`** — Access control list settings for a doc
- **`User`** — Current user information from the whoami endpoint
- **`WorkspaceReference`** — Reference to a Coda workspace
- **`FolderReference`** — Reference to a Coda folder
- **`Icon`** — Icon information (name, type, browser URL)
- **`DocSize`** — Size information for a doc (row counts, table/page counts)

### Coda.io Exceptions
- **`CodaAPIError`** — Base exception for all Coda API errors
- **`CodaAuthenticationError`** — Raised when the API token is invalid or missing (HTTP 401)
- **`CodaForbiddenError`** — Raised when the API token lacks access to a resource (HTTP 403)
- **`CodaNotFoundError`** — Raised when the requested resource could not be found (HTTP 404)
- **`CodaRateLimitError`** — Raised when the API rate limit has been exceeded (HTTP 429)
- **`CodaValidationError`** — Raised when request parameters did not conform to expectations (HTTP 400)
- **`CodaGoneError`** — Raised when the requested resource has been deleted (HTTP 410)

### Infomaniak Authentication
- **`InfomaniakCredentials`** — Credentials dataclass for Infomaniak OpenStack services
- **`InfomaniakS3Credentials`** — Credentials dataclass for Infomaniak S3-compatible Object Storage
- **`create_openstack_connection`** — Factory function to create an authenticated OpenStack connection

## Architecture

```mermaid
graph TB
    subgraph "Cloud Module"
        Init[cloud/__init__.py]
        
        subgraph "Common Abstractions"
            ABC[CloudClient ABC]
            Storage[StorageClient ABC]
            Compute[ComputeClient ABC]
            Serverless[ServerlessClient ABC]
        end
        
        subgraph "AWS Provider"
            S3[S3Client]
            EC2[EC2Client - planned]
            Lambda[LambdaClient - planned]
        end
        
        subgraph "GCP Provider"
            GCS[GCSClient]
            GCE[GCEClient - planned]
            Functions[CloudFunctions - planned]
        end
        
        subgraph "Azure Provider"
            Blob[AzureBlobClient]
            VM[VMClient - planned]
            AzFunc[AzureFunctions - planned]
        end
        
        subgraph "Coda.io"
            Coda[CodaClient]
            Models[Data Models]
        end

        subgraph "Infomaniak"
            IKCompute[InfomaniakComputeClient]
            IKVolume[InfomaniakVolumeClient]
            IKNetwork[InfomaniakNetworkClient]
            IKObjStore[InfomaniakObjectStorageClient]
            IKS3[InfomaniakS3Client]
            IKIdentity[InfomaniakIdentityClient]
            IKDNS[InfomaniakDNSClient]
            IKHeat[InfomaniakHeatClient]
            IKMeter[InfomaniakMeteringClient]
            IKNewsletter[InfomaniakNewsletterClient]
        end
    end

    Init --> S3 & GCS & Blob & Coda & IKCompute
    Storage -.-> S3 & GCS & Blob
    Compute -.-> IKCompute
    IKS3 -.-> Storage
```

## Quick Start

### Installation

```bash
# Core (Coda.io only)
uv uv add requests

# AWS support
uv uv add boto3

# GCP support
uv uv add google-cloud-storage

# Azure support
uv uv add azure-storage-blob azure-identity

# Infomaniak support (OpenStack services)
uv uv add openstacksdk

# Infomaniak S3-compatible storage
uv uv add boto3
```

### Usage Examples

#### AWS S3

```python
from codomyrmex.cloud import S3Client

# Initialize client (uses default AWS credentials)
s3 = S3Client(region_name="us-west-2")

# Upload a file
s3.upload_file("local/file.txt", "my-bucket", "remote/file.txt")

# List objects
objects = s3.list_objects("my-bucket")
for obj in objects:
    print(obj)

# Download a file
s3.download_file("my-bucket", "remote/file.txt", "local/downloaded.txt")

# Get object metadata
metadata = s3.get_metadata("my-bucket", "remote/file.txt")
```

#### GCP Cloud Storage

```python
from codomyrmex.cloud import GCSClient

# Initialize client
gcs = GCSClient(project="my-project")

# Upload a blob
gcs.upload_blob("my-bucket", "local/file.txt", "remote/file.txt")

# List blobs
blobs = gcs.list_blobs("my-bucket")
for blob in blobs:
    print(blob)

# Download a blob
gcs.download_blob("my-bucket", "remote/file.txt", "local/downloaded.txt")
```

#### Azure Blob Storage

```python
from codomyrmex.cloud import AzureBlobClient

# Initialize (uses DefaultAzureCredential)
azure = AzureBlobClient(account_url="https://myaccount.blob.core.windows.net")

# Upload a blob
azure.upload_blob("my-container", "remote/file.txt", "local/file.txt")

# List blobs
blobs = azure.list_blobs("my-container")
for blob in blobs:
    print(blob)
```

#### Coda.io

```python
from codomyrmex.cloud import CodaClient

# Initialize with API token
client = CodaClient(api_token="your-api-token")

# List documents
docs = client.list_docs()
for doc in docs.items:
    print(f"{doc.name} ({doc.id})")

# Get table rows
rows = client.list_rows(doc_id="doc-id", table_id_or_name="Tasks")
for row in rows.items:
    print(row.values)
```

## Directory Structure

| Path | Description |
|------|-------------|
| [`aws/`](aws/README.md) | Amazon Web Services integration |
| [`gcp/`](gcp/README.md) | Google Cloud Platform integration |
| [`azure/`](azure/README.md) | Microsoft Azure integration |
| [`coda_io/`](coda_io/README.md) | Coda.io document/database API |
| [`infomaniak/`](infomaniak/README.md) | Infomaniak OpenStack cloud + Newsletter API |
| [`common/`](common/README.md) | Shared abstractions and utilities |

#### Infomaniak

```python
from codomyrmex.cloud.infomaniak import InfomaniakComputeClient, InfomaniakS3Client

# Compute (from environment variables)
compute = InfomaniakComputeClient.from_env()
instances = compute.list_instances()

# S3-compatible storage
s3 = InfomaniakS3Client.from_env()
s3.upload_data("my-bucket", "data.csv", open("data.csv", "rb").read())
```

#### Infomaniak Newsletter

```python
from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

client = InfomaniakNewsletterClient.from_env()
campaigns = client.list_campaigns()
client.send_test(campaign_id="123", email="test@activeinference.tech")
```

## Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | This file - overview and quick start |
| [SPEC.md](SPEC.md) | Functional specification and requirements |
| [AGENTS.md](AGENTS.md) | AI agent integration guide |
| [PAI.md](PAI.md) | Personal AI infrastructure context |
| [API_SPECIFICATION.md](API_SPECIFICATION.md) | Complete API reference |

## Navigation

- **Full Documentation**: [docs/modules/cloud/](../../../docs/modules/cloud/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [../../../README.md](../../../README.md)
