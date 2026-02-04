# Cloud Module API Specification

**Version**: v0.2.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `cloud` module provides unified APIs for interacting with cloud storage, document, and infrastructure services. This specification covers all public interfaces across AWS, GCP, Azure, Coda.io, and Infomaniak providers.

---

## 2. Storage APIs

### 2.1 AWS S3 (`S3Client`)

```python
from codomyrmex.cloud import S3Client
```

#### Constructor

```python
S3Client(region_name: Optional[str] = None)
```

- Uses boto3 default credential chain

#### Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `upload_file` | `(file_path: str, bucket: str, object_name: Optional[str] = None) -> bool` | Success flag | Upload local file to S3 |
| `download_file` | `(bucket: str, object_name: str, file_path: str) -> bool` | Success flag | Download S3 object to local file |
| `list_objects` | `(bucket: str) -> list[str]` | Object keys | List all objects in bucket |
| `get_metadata` | `(bucket: str, object_name: str) -> Dict[str, Any]` | Metadata dict | Get object metadata |
| `ensure_bucket` | `(bucket: str, region: Optional[str] = None) -> bool` | Success flag | Create bucket if not exists |

---

### 2.2 GCP Cloud Storage (`GCSClient`)

```python
from codomyrmex.cloud import GCSClient
```

#### Constructor

```python
GCSClient(project: Optional[str] = None)
```

- Uses Application Default Credentials

#### Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `upload_blob` | `(bucket_name: str, source_file_name: str, destination_blob_name: str) -> bool` | Success flag | Upload file to GCS |
| `download_blob` | `(bucket_name: str, source_blob_name: str, destination_file_name: str) -> bool` | Success flag | Download blob to local file |
| `list_blobs` | `(bucket_name: str) -> list[str]` | Blob names | List all blobs in bucket |
| `get_metadata` | `(bucket_name: str, blob_name: str) -> dict` | Metadata dict | Get blob metadata |
| `ensure_bucket` | `(bucket_name: str, location: str = "US") -> bool` | Success flag | Create bucket if not exists |

---

### 2.3 Azure Blob Storage (`AzureBlobClient`)

```python
from codomyrmex.cloud import AzureBlobClient
```

#### Constructor

```python
AzureBlobClient(account_url: Optional[str] = None)
```

- Falls back to `AZURE_STORAGE_ACCOUNT_URL` environment variable
- Uses `DefaultAzureCredential` for authentication

#### Methods

| Method | Signature | Returns | Description |
|--------|-----------|---------|-------------|
| `upload_blob` | `(container_name: str, blob_name: str, file_path: str) -> bool` | Success flag | Upload file to container |
| `download_blob` | `(container_name: str, blob_name: str, file_path: str) -> bool` | Success flag | Download blob to local file |
| `list_blobs` | `(container_name: str) -> list[str]` | Blob names | List blobs in container |
| `get_metadata` | `(container_name: str, blob_name: str) -> dict` | Metadata dict | Get blob properties/metadata |
| `ensure_container` | `(container_name: str) -> bool` | Success flag | Create container if not exists |

---

## 3. Coda.io API (`CodaClient`)

```python
from codomyrmex.cloud import CodaClient
```

### 3.1 Constructor

```python
CodaClient(
    api_token: str,
    base_url: str = "https://coda.io/apis/v1",
    timeout: int = 30
)
```

### 3.2 Documents API

| Method | Signature | Description |
|--------|-----------|-------------|
| `list_docs` | `(**filters) -> DocList` | List accessible documents |
| `create_doc` | `(title, **kwargs) -> Doc` | Create new document |
| `get_doc` | `(doc_id: str) -> Doc` | Get document metadata |
| `update_doc` | `(doc_id: str, **kwargs) -> dict` | Update document |
| `delete_doc` | `(doc_id: str) -> dict` | Delete document |

### 3.3 Pages API

| Method | Signature | Description |
|--------|-----------|-------------|
| `list_pages` | `(doc_id: str, **params) -> PageList` | List pages in doc |
| `create_page` | `(doc_id: str, **kwargs) -> dict` | Create new page |
| `get_page` | `(doc_id: str, page_id: str) -> Page` | Get page details |
| `update_page` | `(doc_id: str, page_id: str, **kwargs) -> dict` | Update page |
| `delete_page` | `(doc_id: str, page_id: str) -> dict` | Delete page |

### 3.4 Tables & Rows API

| Method | Signature | Description |
|--------|-----------|-------------|
| `list_tables` | `(doc_id: str, **params) -> TableList` | List tables in doc |
| `get_table` | `(doc_id: str, table_id: str) -> Table` | Get table details |
| `list_columns` | `(doc_id: str, table_id: str) -> ColumnList` | List table columns |
| `list_rows` | `(doc_id: str, table_id: str, **params) -> RowList` | List table rows |
| `insert_rows` | `(doc_id: str, table_id: str, rows: List) -> InsertRowsResult` | Insert/upsert rows |
| `get_row` | `(doc_id: str, table_id: str, row_id: str) -> Row` | Get single row |
| `update_row` | `(doc_id: str, table_id: str, row_id: str, **kwargs) -> dict` | Update row |
| `delete_row` | `(doc_id: str, table_id: str, row_id: str) -> dict` | Delete row |

### 3.5 Exceptions

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `CodaAPIError` | Various | Base exception for API errors |
| `CodaAuthenticationError` | 401 | Invalid or missing API token |
| `CodaForbiddenError` | 403 | Permission denied |
| `CodaNotFoundError` | 404 | Resource not found |
| `CodaRateLimitError` | 429 | Rate limit exceeded |
| `CodaValidationError` | 400 | Invalid request parameters |
| `CodaGoneError` | 410 | Resource deleted |

---

## 4. Infomaniak Cloud APIs

### 4.1 Overview

```python
from codomyrmex.cloud.infomaniak import (
    InfomaniakComputeClient,
    InfomaniakVolumeClient,
    InfomaniakNetworkClient,
    InfomaniakObjectStorageClient,
    InfomaniakS3Client,
    InfomaniakIdentityClient,
    InfomaniakDNSClient,
    InfomaniakHeatClient,
    InfomaniakMeteringClient,
)
from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
```

All Infomaniak OpenStack clients support `from_env()` and `from_credentials()` factory methods.

### 4.2 Compute (`InfomaniakComputeClient`)

| Method | Returns | Description |
|--------|---------|-------------|
| `list_instances()` | `List[Dict]` | List all compute instances |
| `get_instance(server_id)` | `Optional[Dict]` | Get instance details |
| `create_instance(name, flavor, image, network, ...)` | `Optional[Dict]` | Create a new instance |
| `start_instance(server_id)` | `bool` | Start a stopped instance |
| `stop_instance(server_id)` | `bool` | Stop a running instance |
| `reboot_instance(server_id, reboot_type)` | `bool` | Reboot an instance |
| `delete_instance(server_id)` | `bool` | Delete an instance |
| `list_flavors()` | `List[Dict]` | List available flavors |
| `list_images()` | `List[Dict]` | List available images |
| `list_keypairs()` | `List[Dict]` | List SSH key pairs |

### 4.3 Volume (`InfomaniakVolumeClient`)

| Method | Returns | Description |
|--------|---------|-------------|
| `list_volumes()` | `List[Dict]` | List block storage volumes |
| `create_volume(size, name, ...)` | `Optional[Dict]` | Create a volume |
| `delete_volume(volume_id)` | `bool` | Delete a volume |
| `extend_volume(volume_id, new_size)` | `bool` | Extend a volume |
| `attach_volume(volume_id, server_id)` | `bool` | Attach volume to instance |
| `detach_volume(volume_id, server_id)` | `bool` | Detach volume from instance |
| `list_snapshots()` | `List[Dict]` | List volume snapshots |
| `list_backups()` | `List[Dict]` | List volume backups |

### 4.4 Network (`InfomaniakNetworkClient`)

| Method | Returns | Description |
|--------|---------|-------------|
| `list_networks()` | `List[Dict]` | List networks |
| `create_network(name, ...)` | `Optional[Dict]` | Create a network |
| `delete_network(network_id)` | `bool` | Delete a network |
| `list_routers()` | `List[Dict]` | List routers |
| `list_security_groups()` | `List[Dict]` | List security groups |
| `add_security_group_rule(...)` | `Optional[Dict]` | Add a security group rule |
| `list_floating_ips()` | `List[Dict]` | List floating IPs |
| `list_loadbalancers()` | `List[Dict]` | List load balancers |

### 4.5 Object Storage (`InfomaniakObjectStorageClient` / `InfomaniakS3Client`)

**Swift API:**

| Method | Returns | Description |
|--------|---------|-------------|
| `list_containers()` | `List[str]` | List Swift containers |
| `create_container(name)` | `bool` | Create a container |
| `upload_object(container, name, data)` | `bool` | Upload an object |
| `download_object(container, name)` | `bytes` | Download an object |
| `delete_object(container, name)` | `bool` | Delete an object |

**S3-compatible API:**

| Method | Returns | Description |
|--------|---------|-------------|
| `list_buckets()` | `List[str]` | List S3 buckets |
| `list_objects(bucket)` | `List[str]` | List objects in bucket |
| `upload_data(bucket, key, data)` | `bool` | Upload data |
| `download_data(bucket, key)` | `bytes` | Download data |
| `delete_object(bucket, key)` | `bool` | Delete an object |
| `generate_presigned_url(bucket, key, ...)` | `Optional[str]` | Generate presigned URL |
| `bucket_exists(bucket)` | `bool` | Check if bucket exists |

### 4.6 Identity (`InfomaniakIdentityClient`)

| Method | Returns | Description |
|--------|---------|-------------|
| `get_current_user()` | `Optional[Dict]` | Get authenticated user info |
| `list_projects()` | `List[Dict]` | List accessible projects |
| `list_application_credentials()` | `List[Dict]` | List app credentials |
| `create_ec2_credentials()` | `Optional[Dict]` | Create EC2-style credentials |
| `delete_ec2_credentials(cred_id)` | `bool` | Delete EC2 credentials |

### 4.7 DNS (`InfomaniakDNSClient`)

| Method | Returns | Description |
|--------|---------|-------------|
| `list_zones()` | `List[Dict]` | List DNS zones |
| `create_zone(name, email, ...)` | `Optional[Dict]` | Create a zone |
| `delete_zone(zone_id)` | `bool` | Delete a zone |
| `list_records(zone_id)` | `List[Dict]` | List records in zone |
| `create_record(zone_id, name, type, records, ...)` | `Optional[Dict]` | Create a record |
| `delete_record(zone_id, record_id)` | `bool` | Delete a record |

### 4.8 Orchestration (`InfomaniakHeatClient`)

| Method | Returns | Description |
|--------|---------|-------------|
| `list_stacks()` | `List[Dict]` | List Heat stacks |
| `get_stack(stack_id)` | `Optional[Dict]` | Get stack details |
| `create_stack(name, template, ...)` | `Optional[Dict]` | Create a stack |
| `delete_stack(stack_id)` | `bool` | Delete a stack |
| `list_stack_resources(stack_id)` | `List[Dict]` | List stack resources |
| `validate_template(template)` | `Dict` | Validate a Heat template |

### 4.9 Metering (`InfomaniakMeteringClient`)

| Method | Returns | Description |
|--------|---------|-------------|
| `get_all_usage()` | `Dict` | Comprehensive usage summary |
| `get_compute_usage()` | `Dict` | Compute usage (vCPUs, RAM, disk) |
| `get_storage_usage()` | `Dict` | Block storage usage |
| `get_network_usage()` | `Dict` | Network resource usage |
| `get_compute_quotas()` | `Dict` | Compute quota limits |

### 4.10 Newsletter (`InfomaniakNewsletterClient`)

```python
from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
client = InfomaniakNewsletterClient.from_env()  # uses INFOMANIAK_NEWSLETTER_TOKEN, INFOMANIAK_NEWSLETTER_ID
```

**Campaigns:**

| Method | Returns | Description |
|--------|---------|-------------|
| `list_campaigns()` | `List[Dict]` | List all campaigns |
| `get_campaign(campaign_id)` | `Optional[Dict]` | Get campaign details |
| `create_campaign(subject, sender_email, sender_name, content_html, mailing_list_id)` | `Optional[Dict]` | Create a campaign |
| `update_campaign(campaign_id, **kwargs)` | `Optional[Dict]` | Update a campaign |
| `delete_campaign(campaign_id)` | `bool` | Delete a campaign |
| `send_test(campaign_id, email)` | `bool` | Send test email |
| `schedule_campaign(campaign_id, send_at)` | `bool` | Schedule campaign |
| `unschedule_campaign(campaign_id)` | `bool` | Unschedule campaign |
| `send_campaign(campaign_id)` | `bool` | Send campaign immediately |
| `get_campaign_statistics(campaign_id)` | `Optional[Dict]` | Get campaign stats |

**Mailing Lists:**

| Method | Returns | Description |
|--------|---------|-------------|
| `list_mailing_lists()` | `List[Dict]` | List mailing lists |
| `get_mailing_list(list_id)` | `Optional[Dict]` | Get mailing list details |
| `create_mailing_list(name)` | `Optional[Dict]` | Create a mailing list |
| `update_mailing_list(list_id, **kwargs)` | `Optional[Dict]` | Update a mailing list |
| `delete_mailing_list(list_id)` | `bool` | Delete a mailing list |
| `get_list_contacts(list_id)` | `List[Dict]` | Get contacts in list |
| `import_contacts(list_id, contacts)` | `Optional[Dict]` | Import contacts to list |
| `manage_contact(list_id, contact_id, action)` | `bool` | Subscribe/unsubscribe contact |

**Contacts:**

| Method | Returns | Description |
|--------|---------|-------------|
| `get_contact(contact_id)` | `Optional[Dict]` | Get contact details |
| `update_contact(contact_id, **kwargs)` | `Optional[Dict]` | Update contact |
| `delete_contact(contact_id)` | `bool` | Delete contact |

**Utility:**

| Method | Returns | Description |
|--------|---------|-------------|
| `get_task_status(task_id)` | `Optional[Dict]` | Check async task status |
| `get_credits()` | `Optional[Dict]` | Get newsletter credits |

---

## 6. Common Abstractions

```python
from codomyrmex.cloud.common import (
    CloudProvider,
    ResourceType,
    CloudCredentials,
    CloudResource,
    StorageClient,
    ComputeClient,
    ServerlessClient,
)
```

### 6.1 Enums

```python
class CloudProvider(Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    INFOMANIAK = "infomaniak"
    LOCAL = "local"

class ResourceType(Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    SERVERLESS = "serverless"
    CONTAINER = "container"
    QUEUE = "queue"
```

### 6.2 StorageClient ABC

```python
class StorageClient(ABC):
    @abstractmethod
    def list_buckets(self) -> List[str]: ...
    
    @abstractmethod
    def create_bucket(self, name: str) -> bool: ...
    
    @abstractmethod
    def upload_file(self, bucket: str, key: str, data: bytes, 
                    content_type: Optional[str] = None) -> str: ...
    
    @abstractmethod
    def download_file(self, bucket: str, key: str) -> bytes: ...
    
    @abstractmethod
    def delete_file(self, bucket: str, key: str) -> bool: ...
    
    @abstractmethod
    def generate_presigned_url(self, bucket: str, key: str, 
                               expires_in: int = 3600) -> str: ...
```

---

## 7. Usage Examples

### 7.1 Cross-Provider Storage

```python
from codomyrmex.cloud import S3Client, GCSClient, AzureBlobClient

# Choose provider based on environment
import os
provider = os.environ.get("CLOUD_PROVIDER", "aws")

if provider == "aws":
    client = S3Client()
    client.upload_file("data.csv", "my-bucket", "uploads/data.csv")
elif provider == "gcp":
    client = GCSClient()
    client.upload_blob("my-bucket", "data.csv", "uploads/data.csv")
elif provider == "azure":
    client = AzureBlobClient()
    client.upload_blob("my-container", "uploads/data.csv", "data.csv")
```

### 7.2 Coda.io Integration

```python
from codomyrmex.cloud import CodaClient, CodaRateLimitError
import time

client = CodaClient(api_token="your-token")

# Handle rate limiting
def safe_list_rows(doc_id, table_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.list_rows(doc_id, table_id)
        except CodaRateLimitError:
            if attempt < max_retries - 1:
                time.sleep(6)  # Wait for rate limit window
            else:
                raise
```

---

## 8. Error Handling

All storage clients log errors internally and return `False` or empty results on failure. For detailed error handling:

```python
import logging
logging.getLogger("codomyrmex.cloud.aws").setLevel(logging.DEBUG)

from codomyrmex.cloud import S3Client
client = S3Client()

# Check return values
if not client.upload_file("local.txt", "bucket", "remote.txt"):
    print("Upload failed - check logs for details")
```
