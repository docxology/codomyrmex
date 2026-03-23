"""MCP tools for the cloud module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="cloud")
def list_cloud_instances() -> dict:
    """list virtual machine instances currently running in the Infomaniak OpenStack cloud.

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
            results.append(
                {
                    "id": instance.id,
                    "name": instance.name,
                    "status": instance.status,
                    "flavor": instance.flavor.get("original_name")
                    if hasattr(instance.flavor, "get")
                    else str(instance.flavor),
                }
            )

        return {"status": "success", "instances": results, "count": len(results)}
    except Exception as e:
        return {"status": "error", "message": f"Failed to list instances: {e}"}


@mcp_tool(category="cloud")
def list_s3_buckets() -> dict:
    """list S3 buckets available in the Infomaniak storage.

    Returns:
        A list of available S3 buckets.
    """
    from codomyrmex.cloud.infomaniak import InfomaniakS3Client

    try:
        # Requires INFOMANIAK_S3_ACCESS_KEY and INFOMANIAK_S3_SECRET_KEY
        client = InfomaniakS3Client.from_env()
        buckets = client.list_buckets()

        return {
            "status": "success",
            "buckets": [b.get("Name") for b in buckets],
            "count": len(buckets),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to list buckets: {e}"}


@mcp_tool(category="cloud")
def upload_file_to_s3(
    file_path: str, bucket: str, object_name: str | None = None
) -> dict:
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
            "message": f"Successfully uploaded {file_path} to {bucket}",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to upload file: {e}"}


@mcp_tool(category="google_workspace", description="list Google Drive files via SDK.")
def gws_sdk_drive_list_files(query: str = "", page_size: int = 20) -> dict:
    """list files in Google Drive using the Python SDK.

    Args:
        query: Drive search query (e.g., "name contains 'report'").
        page_size: Maximum number of files to return.

    Returns:
        dict with keys: status, files, count
    """
    try:
        from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient

        client = GoogleDriveClient.from_env()
        files = client.list_files(query=query, page_size=page_size)
        return {"status": "success", "files": files, "count": len(files)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(category="google_workspace", description="list Gmail messages via SDK.")
def gws_sdk_gmail_list_messages(query: str = "", max_results: int = 20) -> dict:
    """list Gmail messages using the Python SDK.

    Args:
        query: Gmail search query (e.g., "is:unread").
        max_results: Maximum number of messages to return.

    Returns:
        dict with keys: status, messages, count
    """
    try:
        from codomyrmex.cloud.google_workspace.gmail import GoogleGmailClient

        client = GoogleGmailClient.from_env()
        messages = client.list_messages(query=query, max_results=max_results)
        return {"status": "success", "messages": messages, "count": len(messages)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="google_workspace",
    description="list Google Calendar events via SDK.",
)
def gws_sdk_calendar_list_events(
    calendar_id: str = "primary",
    time_min: str = "",
    time_max: str = "",
) -> dict:
    """list Google Calendar events using the Python SDK.

    Args:
        calendar_id: Calendar ID (default: 'primary').
        time_min: RFC3339 lower bound for event start time.
        time_max: RFC3339 upper bound for event start time.

    Returns:
        dict with keys: status, events, count
    """
    try:
        from codomyrmex.cloud.google_workspace.calendar import GoogleCalendarClient

        client = GoogleCalendarClient.from_env()
        events = client.list_events(
            calendar_id=calendar_id, time_min=time_min, time_max=time_max
        )
        return {"status": "success", "events": events, "count": len(events)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="google_workspace",
    description="Get Google Sheets values via SDK.",
)
def gws_sdk_sheets_get_values(spreadsheet_id: str, range_notation: str) -> dict:
    """Read values from a Google Sheets range using the Python SDK.

    Args:
        spreadsheet_id: The spreadsheet ID.
        range_notation: A1 notation range (e.g., 'Sheet1!A1:D10').

    Returns:
        dict with keys: status, values, range
    """
    try:
        from codomyrmex.cloud.google_workspace.sheets import GoogleSheetsClient

        client = GoogleSheetsClient.from_env()
        values = client.get_values(spreadsheet_id, range_notation)
        return {"status": "success", "values": values, "range": range_notation}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
