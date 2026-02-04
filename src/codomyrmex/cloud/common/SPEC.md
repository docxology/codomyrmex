# Cloud Common - Functional Specification

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Define abstract interfaces and shared utilities for cloud provider implementations. All provider-specific clients should adhere to these contracts for consistency.

## Interface Contracts

### StorageClient ABC

All object storage implementations must provide:

```python
class StorageClient(ABC):
    @abstractmethod
    def list_buckets(self) -> List[str]:
        """Return names of all accessible buckets."""
    
    @abstractmethod
    def create_bucket(self, name: str) -> bool:
        """Create a new bucket. Returns success status."""
    
    @abstractmethod
    def upload_file(self, bucket: str, key: str, data: bytes,
                    content_type: Optional[str] = None) -> str:
        """Upload data to bucket. Returns object URL/path."""
    
    @abstractmethod
    def download_file(self, bucket: str, key: str) -> bytes:
        """Download object contents as bytes."""
    
    @abstractmethod
    def delete_file(self, bucket: str, key: str) -> bool:
        """Delete object. Returns success status."""
    
    @abstractmethod
    def generate_presigned_url(self, bucket: str, key: str,
                               expires_in: int = 3600) -> str:
        """Generate temporary access URL."""
```

### ComputeClient ABC

```python
class ComputeClient(ABC):
    @abstractmethod
    def list_instances(self) -> List[Dict[str, Any]]:
        """List all compute instances."""
    
    @abstractmethod
    def start_instance(self, instance_id: str) -> bool:
        """Start stopped instance."""
    
    @abstractmethod
    def stop_instance(self, instance_id: str) -> bool:
        """Stop running instance."""
    
    @abstractmethod
    def terminate_instance(self, instance_id: str) -> bool:
        """Permanently terminate instance."""
    
    @abstractmethod
    def create_instance(self, name: str, instance_type: str,
                        image_id: str, **kwargs) -> Dict[str, Any]:
        """Create new compute instance."""
```

### ServerlessClient ABC

```python
class ServerlessClient(ABC):
    @abstractmethod
    def list_functions(self) -> List[Dict[str, Any]]:
        """List all serverless functions."""
    
    @abstractmethod
    def invoke_function(self, function_name: str,
                        payload: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke function with payload."""
    
    @abstractmethod
    def create_function(self, name: str, runtime: str, handler: str,
                        code_path: str, **kwargs) -> Dict[str, Any]:
        """Deploy new function."""
    
    @abstractmethod
    def delete_function(self, function_name: str) -> bool:
        """Delete function."""
```

## Data Models

### CloudCredentials

```python
@dataclass
class CloudCredentials:
    provider: CloudProvider      # Required: target platform
    access_key: Optional[str]    # AWS access key / API key
    secret_key: Optional[str]    # AWS secret key
    region: str = "us-east-1"    # Default region
    project_id: Optional[str]    # GCP project ID
    profile: Optional[str]       # AWS profile name
    metadata: Dict[str, str]     # Additional provider-specific data
```

### CloudResource

```python
@dataclass
class CloudResource:
    id: str                      # Unique resource identifier
    name: str                    # Human-readable name
    resource_type: ResourceType  # Category (COMPUTE, STORAGE, etc.)
    provider: CloudProvider      # Source platform
    region: str                  # Geographic region
    status: str = "active"       # Current state
    created_at: Optional[datetime]
    tags: Dict[str, str]         # Resource tags
    metadata: Dict[str, Any]     # Additional data
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
```

## Error Handling Requirements

1. All methods should handle provider-specific exceptions internally
2. Return `False` or empty collections on non-critical failures
3. Log errors using `logging` module
4. Raise exceptions only for critical/unrecoverable errors

## Navigation

- **README**: [README.md](README.md)
- **Parent**: [cloud/](../README.md)
