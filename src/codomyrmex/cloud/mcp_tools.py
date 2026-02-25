"""MCP tools for the cloud module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="cloud")
def list_cloud_instances() -> dict:
    """List virtual machine instances currently running in the Infomaniak OpenStack cloud.
    
    Returns:
        A list of active instances or an error if authentication fails.
    """
    from codomyrmex.cloud.infomaniak import InfomaniakComputeClient

    try:
        # Requires INFOMANIAK_APP_CREDENTIAL_ID and INFOMANIAK_APP_CREDENTIAL_SECRET
        client = InfomaniakComputeClient.from_env()
        instances = client.list_instances()

        results = []
        for instance in instances:
            results.append({
                "id": instance.id,
                "name": instance.name,
                "status": instance.status,
                "flavor": instance.flavor.get("original_name") if hasattr(instance.flavor, "get") else str(instance.flavor)
            })

        return {"status": "success", "instances": results, "count": len(results)}
    except Exception as e:
        return {"status": "error", "message": f"Failed to list instances: {e}"}


@mcp_tool(category="cloud")
def list_s3_buckets() -> dict:
    """List S3 buckets available in the Infomaniak storage.
    
    Returns:
        A list of available S3 buckets.
    """
    from codomyrmex.cloud.infomaniak import InfomaniakS3Client

    try:
        # Requires INFOMANIAK_S3_ACCESS_KEY and INFOMANIAK_S3_SECRET_KEY
        client = InfomaniakS3Client.from_env()
        buckets = client.list_buckets()

        return {"status": "success", "buckets": [b.get("Name") for b in buckets], "count": len(buckets)}
    except Exception as e:
        return {"status": "error", "message": f"Failed to list buckets: {e}"}


@mcp_tool(category="cloud")
def upload_file_to_s3(file_path: str, bucket: str, object_name: str | None = None) -> dict:
    """Upload a local file to Infomaniak S3 storage.
    
    Args:
        file_path: The local path to the file to upload
        bucket: The destination S3 bucket name
        object_name: The target S3 object key (defaults to the file name)
        
    Returns:
        Status of the upload operation.
    """
    from codomyrmex.cloud.infomaniak import InfomaniakS3Client

    try:
        client = InfomaniakS3Client.from_env()
        client.upload_file(file_path=file_path, bucket=bucket, object_name=object_name)

        return {
            "status": "success",
            "message": f"Successfully uploaded {file_path} to {bucket}"
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to upload file: {e}"}
