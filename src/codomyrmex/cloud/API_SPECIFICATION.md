# Cloud Module API Specification

**Version**: v0.2.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `cloud` module provides unified APIs for interacting with cloud storage and document services. This specification covers all public interfaces across AWS, GCP, Azure, and Coda.io providers.

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

## 4. Common Abstractions

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

### 4.1 Enums

```python
class CloudProvider(Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
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

### 4.2 StorageClient ABC

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

## 5. Usage Examples

### 5.1 Cross-Provider Storage

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

### 5.2 Coda.io Integration

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

## 6. Error Handling

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
