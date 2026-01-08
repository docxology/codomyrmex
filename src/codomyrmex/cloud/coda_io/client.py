from codomyrmex.logging_monitoring import get_logger
"""Core functionality module

This module provides client functionality including:
- 53 functions: __init__, _request, _get...
- 1 classes: CodaClient

Usage:
    from client import FunctionName, ClassName
    # Example usage here
"""
logger = get_logger(__name__)
"""
Coda.io REST API v1 Client.

This module provides a comprehensive Python client for the Coda.io API,
enabling programmatic access to Coda docs, pages, tables, rows, and more.

API Documentation: https://coda.io/developers/apis/v1
"""

import json
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode, quote

try:
    import requests
except ImportError:
    requests = None  # type: ignore

from .models import (
    Doc,
    DocList,
    Page,
    PageList,
    PageContentItem,
    Table,
    TableList,
    Column,
    ColumnList,
    Row,
    RowList,
    RowEdit,
    CellEdit,
    Formula,
    FormulaList,
    Control,
    ControlList,
    Permission,
    PermissionList,
    SharingMetadata,
    ACLSettings,
    Principal,
    User,
    MutationStatus,
    InsertRowsResult,
)
from .exceptions import raise_for_status, CodaAPIError


class CodaClient:
    """
    Coda.io REST API v1 client.
    
    This client provides methods for all Coda API v1 endpoints including:
    - Docs: List, create, get, update, delete documents
    - Pages: Manage pages and their content
    - Tables: Access tables and views
    - Columns: Read column definitions
    - Rows: CRUD operations on table rows
    - Permissions: Manage doc sharing
    - Publishing: Publish/unpublish docs
    - Formulas: Access named formulas
    - Controls: Read control values
    - Automations: Trigger webhooks
    - Analytics: Usage analytics
    
    Example:
        >>> client = CodaClient(api_token="your-api-token")
        >>> docs = client.list_docs()
        >>> for doc in docs.items:
        ...     print(doc.name)
    
    Attributes:
        api_token: The Coda API token for authentication
        base_url: The base URL for the Coda API (default: https://coda.io/apis/v1)
        session: The requests session used for HTTP calls
    """
    
    DEFAULT_BASE_URL = "https://coda.io/apis/v1"
    
    def __init__(
        self,
        api_token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30,
    ):
        """
        Initialize the Coda API client.
        
        Args:
            api_token: Your Coda API token. Get one from https://coda.io/account
            base_url: Base URL for the API. Defaults to the production API.
            timeout: Default timeout for requests in seconds.
            
        Raises:
            ImportError: If the requests library is not installed.
        """
        if requests is None:
            raise ImportError(
                "The 'requests' library is required. "
                "Install it with: pip install requests"
            )
        
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        })
    
    # =========================================================================
    # HTTP Helpers
    # =========================================================================
    
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Coda API.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path: API endpoint path (e.g., "/docs")
            params: Query parameters
            json_data: JSON body for POST/PUT/PATCH requests
            headers: Additional headers
            
        Returns:
            Parsed JSON response
            
        Raises:
            CodaAPIError: On API errors
        """
        url = f"{self.base_url}{path}"
        
        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=request_headers,
            timeout=self.timeout,
        )
        
        # Parse response body
        try:
            response_body = response.json() if response.content else {}
        except json.JSONDecodeError:
            response_body = {}
        
        # Raise exception for error status codes
        raise_for_status(response.status_code, response_body)
        
        return response_body
    
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", path, params=params, **kwargs)
    
    def _post(self, path: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", path, json_data=json_data, **kwargs)
    
    def _put(self, path: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._request("PUT", path, json_data=json_data, **kwargs)
    
    def _patch(self, path: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self._request("PATCH", path, json_data=json_data, **kwargs)
    
    def _delete(self, path: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._request("DELETE", path, json_data=json_data, **kwargs)
    
    @staticmethod
    def _encode_id(id_or_name: str) -> str:
        """URL-encode an ID or name for use in paths."""
        return quote(id_or_name, safe="")
    
    # =========================================================================
    # Docs API
    # =========================================================================
    
    def list_docs(
        self,
        is_owner: Optional[bool] = None,
        is_published: Optional[bool] = None,
        query: Optional[str] = None,
        source_doc: Optional[str] = None,
        is_starred: Optional[bool] = None,
        in_gallery: Optional[bool] = None,
        workspace_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        limit: int = 25,
        page_token: Optional[str] = None,
    ) -> DocList:
        """
        List accessible docs.
        
        Returns docs in reverse chronological order by last relevant event.
        
        Args:
            is_owner: Show only docs owned by the user
            is_published: Show only published docs
            query: Search term to filter results
            source_doc: Show only docs copied from this doc ID
            is_starred: Filter by starred status
            in_gallery: Show only docs visible in gallery
            workspace_id: Filter by workspace
            folder_id: Filter by folder
            limit: Maximum results (default 25)
            page_token: Pagination token
            
        Returns:
            DocList with items and pagination info
        """
        params = {
            "isOwner": is_owner,
            "isPublished": is_published,
            "query": query,
            "sourceDoc": source_doc,
            "isStarred": is_starred,
            "inGallery": in_gallery,
            "workspaceId": workspace_id,
            "folderId": folder_id,
            "limit": limit,
            "pageToken": page_token,
        }
        data = self._get("/docs", params=params)
        return DocList.from_dict(data)
    
    def create_doc(
        self,
        title: Optional[str] = None,
        source_doc: Optional[str] = None,
        timezone: Optional[str] = None,
        folder_id: Optional[str] = None,
        initial_page: Optional[Dict[str, Any]] = None,
    ) -> Doc:
        """
        Create a new doc.
        
        Note: Creating a doc requires Doc Maker role in the workspace.
        
        Args:
            title: Title of the new doc (defaults to "Untitled")
            source_doc: Doc ID to copy from
            timezone: Timezone for the doc
            folder_id: Folder to create doc in
            initial_page: Initial page content
            
        Returns:
            The created Doc
        """
        body = {}
        if title:
            body["title"] = title
        if source_doc:
            body["sourceDoc"] = source_doc
        if timezone:
            body["timezone"] = timezone
        if folder_id:
            body["folderId"] = folder_id
        if initial_page:
            body["initialPage"] = initial_page
        
        data = self._post("/docs", json_data=body)
        return Doc.from_dict(data)
    
    def get_doc(self, doc_id: str) -> Doc:
        """
        Get metadata for a specific doc.
        
        Args:
            doc_id: The doc ID
            
        Returns:
            Doc metadata
        """
        data = self._get(f"/docs/{self._encode_id(doc_id)}")
        return Doc.from_dict(data)
    
    def delete_doc(self, doc_id: str) -> Dict[str, Any]:
        """
        Delete a doc.
        
        Args:
            doc_id: The doc ID to delete
            
        Returns:
            Deletion result
        """
        return self._delete(f"/docs/{self._encode_id(doc_id)}")
    
    def update_doc(
        self,
        doc_id: str,
        title: Optional[str] = None,
        icon_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update doc metadata.
        
        Note: Updating title requires Doc Maker role.
        
        Args:
            doc_id: The doc ID
            title: New title
            icon_name: New icon name
            
        Returns:
            Update result
        """
        body = {}
        if title:
            body["title"] = title
        if icon_name:
            body["iconName"] = icon_name
        
        return self._patch(f"/docs/{self._encode_id(doc_id)}", json_data=body)
    
    # =========================================================================
    # Pages API
    # =========================================================================
    
    def list_pages(
        self,
        doc_id: str,
        limit: int = 25,
        page_token: Optional[str] = None,
    ) -> PageList:
        """
        List pages in a doc.
        
        Args:
            doc_id: The doc ID
            limit: Maximum results
            page_token: Pagination token
            
        Returns:
            PageList with items and pagination info
        """
        params = {"limit": limit, "pageToken": page_token}
        data = self._get(f"/docs/{self._encode_id(doc_id)}/pages", params=params)
        return PageList.from_dict(data)
    
    def create_page(
        self,
        doc_id: str,
        name: Optional[str] = None,
        subtitle: Optional[str] = None,
        icon_name: Optional[str] = None,
        image_url: Optional[str] = None,
        parent_page_id: Optional[str] = None,
        page_content: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new page in a doc.
        
        Note: Requires Doc Maker role.
        
        Args:
            doc_id: The doc ID
            name: Page name
            subtitle: Page subtitle
            icon_name: Icon name
            image_url: Cover image URL
            parent_page_id: Parent page ID for subpages
            page_content: Initial page content
            
        Returns:
            Creation result with request_id and page id
        """
        body = {}
        if name:
            body["name"] = name
        if subtitle:
            body["subtitle"] = subtitle
        if icon_name:
            body["iconName"] = icon_name
        if image_url:
            body["imageUrl"] = image_url
        if parent_page_id:
            body["parentPageId"] = parent_page_id
        if page_content:
            body["pageContent"] = page_content
        
        return self._post(f"/docs/{self._encode_id(doc_id)}/pages", json_data=body)
    
    def get_page(self, doc_id: str, page_id_or_name: str) -> Page:
        """
        Get details about a page.
        
        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name (names are discouraged)
            
        Returns:
            Page details
        """
        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}"
        data = self._get(path)
        return Page.from_dict(data)
    
    def update_page(
        self,
        doc_id: str,
        page_id_or_name: str,
        name: Optional[str] = None,
        subtitle: Optional[str] = None,
        icon_name: Optional[str] = None,
        image_url: Optional[str] = None,
        is_hidden: Optional[bool] = None,
        content_update: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a page.
        
        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name
            name: New name
            subtitle: New subtitle
            icon_name: New icon
            image_url: New cover image URL
            is_hidden: Whether to hide the page
            content_update: Content to update
            
        Returns:
            Update result
        """
        body = {}
        if name is not None:
            body["name"] = name
        if subtitle is not None:
            body["subtitle"] = subtitle
        if icon_name is not None:
            body["iconName"] = icon_name
        if image_url is not None:
            body["imageUrl"] = image_url
        if is_hidden is not None:
            body["isHidden"] = is_hidden
        if content_update is not None:
            body["contentUpdate"] = content_update
        
        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}"
        return self._put(path, json_data=body)
    
    def delete_page(self, doc_id: str, page_id_or_name: str) -> Dict[str, Any]:
        """
        Delete a page.
        
        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name
            
        Returns:
            Deletion result
        """
        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}"
        return self._delete(path)
    
    def list_page_content(
        self,
        doc_id: str,
        page_id_or_name: str,
        limit: int = 50,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List content elements in a page.
        
        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name
            limit: Maximum results (1-500, default 50)
            page_token: Pagination token
            
        Returns:
            Page content with items
        """
        params = {"limit": limit, "pageToken": page_token}
        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}/content"
        return self._get(path, params=params)
    
    def export_page(
        self,
        doc_id: str,
        page_id_or_name: str,
        output_format: str = "html",
    ) -> Dict[str, Any]:
        """
        Begin exporting page content.
        
        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name
            output_format: "html" or "markdown"
            
        Returns:
            Export status with request ID and href to poll
        """
        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}/export"
        return self._post(path, json_data={"outputFormat": output_format})
    
    def get_page_export_status(
        self,
        doc_id: str,
        page_id_or_name: str,
        request_id: str,
    ) -> Dict[str, Any]:
        """
        Check page export status.
        
        Args:
            doc_id: The doc ID
            page_id_or_name: Page ID or name
            request_id: Export request ID
            
        Returns:
            Export status with download link when complete
        """
        path = f"/docs/{self._encode_id(doc_id)}/pages/{self._encode_id(page_id_or_name)}/export/{request_id}"
        return self._get(path)
    
    # =========================================================================
    # Tables API
    # =========================================================================
    
    def list_tables(
        self,
        doc_id: str,
        limit: int = 25,
        page_token: Optional[str] = None,
        sort_by: Optional[str] = None,
        table_types: Optional[List[str]] = None,
    ) -> TableList:
        """
        List tables and views in a doc.
        
        Args:
            doc_id: The doc ID
            limit: Maximum results
            page_token: Pagination token
            sort_by: Sort order ("name")
            table_types: Filter by type (["table", "view"])
            
        Returns:
            TableList with items
        """
        params = {
            "limit": limit,
            "pageToken": page_token,
            "sortBy": sort_by,
        }
        if table_types:
            params["tableTypes"] = ",".join(table_types)
        
        data = self._get(f"/docs/{self._encode_id(doc_id)}/tables", params=params)
        return TableList.from_dict(data)
    
    def get_table(
        self,
        doc_id: str,
        table_id_or_name: str,
        use_updated_table_layouts: bool = False,
    ) -> Table:
        """
        Get details about a table or view.
        
        Args:
            doc_id: The doc ID
            table_id_or_name: Table ID or name
            use_updated_table_layouts: Return updated layout field values
            
        Returns:
            Table details
        """
        params = {}
        if use_updated_table_layouts:
            params["useUpdatedTableLayouts"] = True
        
        path = f"/docs/{self._encode_id(doc_id)}/tables/{self._encode_id(table_id_or_name)}"
        data = self._get(path, params=params if params else None)
        return Table.from_dict(data)
    
    # =========================================================================
    # Columns API
    # =========================================================================
    
    def list_columns(
        self,
        doc_id: str,
        table_id_or_name: str,
        limit: int = 25,
        page_token: Optional[str] = None,
        visible_only: bool = False,
    ) -> ColumnList:
        """
        List columns in a table.
        
        Args:
            doc_id: The doc ID
            table_id_or_name: Table ID or name
            limit: Maximum results (1-100, default 25)
            page_token: Pagination token
            visible_only: Only return visible columns (base tables only)
            
        Returns:
            ColumnList with items
        """
        params = {
            "limit": limit,
            "pageToken": page_token,
        }
        if visible_only:
            params["visibleOnly"] = True
        
        path = f"/docs/{self._encode_id(doc_id)}/tables/{self._encode_id(table_id_or_name)}/columns"
        data = self._get(path, params=params)
        return ColumnList.from_dict(data)
    
    def get_column(
        self,
        doc_id: str,
        table_id_or_name: str,
        column_id_or_name: str,
    ) -> Column:
        """
        Get details about a column.
        
        Args:
            doc_id: The doc ID
            table_id_or_name: Table ID or name
            column_id_or_name: Column ID or name
            
        Returns:
            Column details
        """
        path = (
            f"/docs/{self._encode_id(doc_id)}"
            f"/tables/{self._encode_id(table_id_or_name)}"
            f"/columns/{self._encode_id(column_id_or_name)}"
        )
        data = self._get(path)
        return Column.from_dict(data)
    
    # =========================================================================
    # Rows API
    # =========================================================================
    
    def list_rows(
        self,
        doc_id: str,
        table_id_or_name: str,
        query: Optional[str] = None,
        sort_by: Optional[str] = None,
        use_column_names: bool = False,
        value_format: str = "simple",
        visible_only: bool = False,
        limit: int = 25,
        page_token: Optional[str] = None,
        sync_token: Optional[str] = None,
    ) -> RowList:
        """
        List rows in a table.
        
        Args:
            doc_id: The doc ID
            table_id_or_name: Table ID or name
            query: Filter query (e.g., 'column_id:"value"')
            sort_by: Sort order ("createdAt", "natural", "updatedAt")
            use_column_names: Use column names instead of IDs in values
            value_format: Value format ("simple", "simpleWithArrays", "rich")
            visible_only: Only visible rows/columns
            limit: Maximum results
            page_token: Pagination token
            sync_token: Sync token for incremental updates
            
        Returns:
            RowList with items
        """
        params = {
            "query": query,
            "sortBy": sort_by,
            "useColumnNames": use_column_names if use_column_names else None,
            "valueFormat": value_format,
            "visibleOnly": visible_only if visible_only else None,
            "limit": limit,
            "pageToken": page_token,
            "syncToken": sync_token,
        }
        
        path = f"/docs/{self._encode_id(doc_id)}/tables/{self._encode_id(table_id_or_name)}/rows"
        data = self._get(path, params=params)
        return RowList.from_dict(data)
    
    def insert_rows(
        self,
        doc_id: str,
        table_id_or_name: str,
        rows: List[Union[RowEdit, Dict[str, Any]]],
        key_columns: Optional[List[str]] = None,
        disable_parsing: bool = False,
    ) -> InsertRowsResult:
        """
        Insert rows into a table.
        
        If key_columns are provided, this becomes an upsert operation.
        Note: Only works for base tables, not views.
        
        Args:
            doc_id: The doc ID
            table_id_or_name: Table ID or name
            rows: List of rows to insert (RowEdit or dict with "cells")
            key_columns: Columns for upsert matching
            disable_parsing: Don't parse values
            
        Returns:
            InsertRowsResult with request_id and added_row_ids
        """
        # Convert RowEdit objects to dicts
        row_dicts = []
        for row in rows:
            if isinstance(row, RowEdit):
                row_dicts.append(row.to_dict())
            else:
                row_dicts.append(row)
        
        body: Dict[str, Any] = {"rows": row_dicts}
        if key_columns:
            body["keyColumns"] = key_columns
        
        params = {}
        if disable_parsing:
            params["disableParsing"] = True
        
        path = f"/docs/{self._encode_id(doc_id)}/tables/{self._encode_id(table_id_or_name)}/rows"
        data = self._post(path, json_data=body, params=params if params else None)
        return InsertRowsResult.from_dict(data)
    
    def get_row(
        self,
        doc_id: str,
        table_id_or_name: str,
        row_id_or_name: str,
        use_column_names: bool = False,
        value_format: str = "simple",
    ) -> Row:
        """
        Get a specific row.
        
        Args:
            doc_id: The doc ID
            table_id_or_name: Table ID or name
            row_id_or_name: Row ID or name
            use_column_names: Use column names in values
            value_format: Value format
            
        Returns:
            Row details
        """
        params = {
            "valueFormat": value_format,
        }
        if use_column_names:
            params["useColumnNames"] = True
        
        path = (
            f"/docs/{self._encode_id(doc_id)}"
            f"/tables/{self._encode_id(table_id_or_name)}"
            f"/rows/{self._encode_id(row_id_or_name)}"
        )
        data = self._get(path, params=params)
        return Row.from_dict(data)
    
    def update_row(
        self,
        doc_id: str,
        table_id_or_name: str,
        row_id_or_name: str,
        row: Union[RowEdit, Dict[str, Any]],
        disable_parsing: bool = False,
    ) -> Dict[str, Any]:
        """
        Update a row.
        
        Args:
            doc_id: The doc ID
            table_id_or_name: Table ID or name
            row_id_or_name: Row ID or name
            row: Row data to update
            disable_parsing: Don't parse values
            
        Returns:
            Update result with request_id
        """
        if isinstance(row, RowEdit):
            row_dict = row.to_dict()
        else:
            row_dict = row
        
        params = {}
        if disable_parsing:
            params["disableParsing"] = True
        
        path = (
            f"/docs/{self._encode_id(doc_id)}"
            f"/tables/{self._encode_id(table_id_or_name)}"
            f"/rows/{self._encode_id(row_id_or_name)}"
        )
        return self._put(path, json_data={"row": row_dict}, params=params if params else None)
    
    def delete_row(
        self,
        doc_id: str,
        table_id_or_name: str,
        row_id_or_name: str,
    ) -> Dict[str, Any]:
        """
        Delete a row.
        
        Args:
            doc_id: The doc ID
            table_id_or_name: Table ID or name
            row_id_or_name: Row ID or name
            
        Returns:
            Deletion result
        """
        path = (
            f"/docs/{self._encode_id(doc_id)}"
            f"/tables/{self._encode_id(table_id_or_name)}"
            f"/rows/{self._encode_id(row_id_or_name)}"
        )
        return self._delete(path)
    
    def delete_rows(
        self,
        doc_id: str,
        table_id_or_name: str,
        row_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Delete multiple rows.
        
        Args:
            doc_id: The doc ID
            table_id_or_name: Table ID or name
            row_ids: List of row IDs to delete
            
        Returns:
            Deletion result
        """
        path = f"/docs/{self._encode_id(doc_id)}/tables/{self._encode_id(table_id_or_name)}/rows"
        return self._delete(path, json_data={"rowIds": row_ids})
    
    def push_button(
        self,
        doc_id: str,
        table_id_or_name: str,
        row_id_or_name: str,
        column_id_or_name: str,
    ) -> Dict[str, Any]:
        """
        Push a button in a table.
        
        The button can perform any action on the document.
        
        Args:
            doc_id: The doc ID
            table_id_or_name: Table ID or name
            row_id_or_name: Row ID or name
            column_id_or_name: Column ID or name of the button
            
        Returns:
            Result with request_id
        """
        path = (
            f"/docs/{self._encode_id(doc_id)}"
            f"/tables/{self._encode_id(table_id_or_name)}"
            f"/rows/{self._encode_id(row_id_or_name)}"
            f"/buttons/{self._encode_id(column_id_or_name)}"
        )
        return self._post(path)
    
    # =========================================================================
    # Permissions API
    # =========================================================================
    
    def get_sharing_metadata(self, doc_id: str) -> SharingMetadata:
        """
        Get sharing metadata for a doc.
        
        Args:
            doc_id: The doc ID
            
        Returns:
            SharingMetadata with sharing permissions
        """
        path = f"/docs/{self._encode_id(doc_id)}/acl/metadata"
        data = self._get(path)
        return SharingMetadata.from_dict(data)
    
    def list_permissions(
        self,
        doc_id: str,
        limit: int = 25,
        page_token: Optional[str] = None,
    ) -> PermissionList:
        """
        List permissions for a doc.
        
        Args:
            doc_id: The doc ID
            limit: Maximum results
            page_token: Pagination token
            
        Returns:
            PermissionList with items
        """
        params = {"limit": limit, "pageToken": page_token}
        path = f"/docs/{self._encode_id(doc_id)}/acl/permissions"
        data = self._get(path, params=params)
        return PermissionList.from_dict(data)
    
    def add_permission(
        self,
        doc_id: str,
        access: str,
        principal: Union[Principal, Dict[str, Any]],
        suppress_email: bool = False,
    ) -> Dict[str, Any]:
        """
        Add a permission to a doc.
        
        Args:
            doc_id: The doc ID
            access: Access level ("readonly", "write", "comment")
            principal: Principal to add (email, domain, or anyone)
            suppress_email: Don't send notification email
            
        Returns:
            Result
        """
        if isinstance(principal, Principal):
            principal_dict = principal.to_dict()
        else:
            principal_dict = principal
        
        body = {
            "access": access,
            "principal": principal_dict,
            "suppressEmail": suppress_email,
        }
        
        path = f"/docs/{self._encode_id(doc_id)}/acl/permissions"
        return self._post(path, json_data=body)
    
    def delete_permission(self, doc_id: str, permission_id: str) -> Dict[str, Any]:
        """
        Delete a permission.
        
        Args:
            doc_id: The doc ID
            permission_id: The permission ID to delete
            
        Returns:
            Deletion result
        """
        path = f"/docs/{self._encode_id(doc_id)}/acl/permissions/{self._encode_id(permission_id)}"
        return self._delete(path)
    
    def search_principals(
        self,
        doc_id: str,
        query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for principals that the doc can be shared with.
        
        Args:
            doc_id: The doc ID
            query: Search query (if empty, returns no results)
            
        Returns:
            Dict with users and groups lists
        """
        params = {"query": query} if query else {}
        path = f"/docs/{self._encode_id(doc_id)}/acl/principals/search"
        return self._get(path, params=params if params else None)
    
    def get_acl_settings(self, doc_id: str) -> ACLSettings:
        """
        Get ACL settings for a doc.
        
        Args:
            doc_id: The doc ID
            
        Returns:
            ACLSettings
        """
        path = f"/docs/{self._encode_id(doc_id)}/acl/settings"
        data = self._get(path)
        return ACLSettings.from_dict(data)
    
    def update_acl_settings(
        self,
        doc_id: str,
        allow_editors_to_change_permissions: Optional[bool] = None,
        allow_copying: Optional[bool] = None,
        allow_viewers_to_request_editing: Optional[bool] = None,
    ) -> ACLSettings:
        """
        Update ACL settings for a doc.
        
        Args:
            doc_id: The doc ID
            allow_editors_to_change_permissions: Allow editors to change permissions
            allow_copying: Allow viewers to copy the doc
            allow_viewers_to_request_editing: Allow viewers to request edit access
            
        Returns:
            Updated ACLSettings
        """
        body = {}
        if allow_editors_to_change_permissions is not None:
            body["allowEditorsToChangePermissions"] = allow_editors_to_change_permissions
        if allow_copying is not None:
            body["allowCopying"] = allow_copying
        if allow_viewers_to_request_editing is not None:
            body["allowViewersToRequestEditing"] = allow_viewers_to_request_editing
        
        path = f"/docs/{self._encode_id(doc_id)}/acl/settings"
        data = self._patch(path, json_data=body)
        return ACLSettings.from_dict(data)
    
    # =========================================================================
    # Publishing API
    # =========================================================================
    
    def get_categories(self) -> Dict[str, Any]:
        """
        Get all available doc categories.
        
        Returns:
            Dict with items list of categories
        """
        return self._get("/categories")
    
    def publish_doc(
        self,
        doc_id: str,
        slug: Optional[str] = None,
        discoverable: Optional[bool] = None,
        earn_credit: Optional[bool] = None,
        category_names: Optional[List[str]] = None,
        mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Publish a doc.
        
        Args:
            doc_id: The doc ID
            slug: URL slug for the published doc
            discoverable: Make doc discoverable
            earn_credit: Earn credit for signups via doc
            category_names: Categories to apply
            mode: Publish mode ("view", "play", "edit")
            
        Returns:
            Result with request_id
        """
        body = {}
        if slug is not None:
            body["slug"] = slug
        if discoverable is not None:
            body["discoverable"] = discoverable
        if earn_credit is not None:
            body["earnCredit"] = earn_credit
        if category_names is not None:
            body["categoryNames"] = category_names
        if mode is not None:
            body["mode"] = mode
        
        path = f"/docs/{self._encode_id(doc_id)}/publish"
        return self._put(path, json_data=body)
    
    def unpublish_doc(self, doc_id: str) -> Dict[str, Any]:
        """
        Unpublish a doc.
        
        Args:
            doc_id: The doc ID
            
        Returns:
            Result
        """
        path = f"/docs/{self._encode_id(doc_id)}/publish"
        return self._delete(path)
    
    # =========================================================================
    # Formulas API
    # =========================================================================
    
    def list_formulas(
        self,
        doc_id: str,
        limit: int = 25,
        page_token: Optional[str] = None,
        sort_by: Optional[str] = None,
    ) -> FormulaList:
        """
        List named formulas in a doc.
        
        Args:
            doc_id: The doc ID
            limit: Maximum results
            page_token: Pagination token
            sort_by: Sort order ("name")
            
        Returns:
            FormulaList with items
        """
        params = {"limit": limit, "pageToken": page_token, "sortBy": sort_by}
        path = f"/docs/{self._encode_id(doc_id)}/formulas"
        data = self._get(path, params=params)
        return FormulaList.from_dict(data)
    
    def get_formula(self, doc_id: str, formula_id_or_name: str) -> Formula:
        """
        Get a formula's current value.
        
        Args:
            doc_id: The doc ID
            formula_id_or_name: Formula ID or name
            
        Returns:
            Formula with computed value
        """
        path = f"/docs/{self._encode_id(doc_id)}/formulas/{self._encode_id(formula_id_or_name)}"
        data = self._get(path)
        return Formula.from_dict(data)
    
    # =========================================================================
    # Controls API
    # =========================================================================
    
    def list_controls(
        self,
        doc_id: str,
        limit: int = 25,
        page_token: Optional[str] = None,
        sort_by: Optional[str] = None,
    ) -> ControlList:
        """
        List controls in a doc.
        
        Args:
            doc_id: The doc ID
            limit: Maximum results
            page_token: Pagination token
            sort_by: Sort order ("name")
            
        Returns:
            ControlList with items
        """
        params = {"limit": limit, "pageToken": page_token, "sortBy": sort_by}
        path = f"/docs/{self._encode_id(doc_id)}/controls"
        data = self._get(path, params=params)
        return ControlList.from_dict(data)
    
    def get_control(self, doc_id: str, control_id_or_name: str) -> Control:
        """
        Get a control's current value.
        
        Args:
            doc_id: The doc ID
            control_id_or_name: Control ID or name
            
        Returns:
            Control with current value
        """
        path = f"/docs/{self._encode_id(doc_id)}/controls/{self._encode_id(control_id_or_name)}"
        data = self._get(path)
        return Control.from_dict(data)
    
    # =========================================================================
    # Automations API
    # =========================================================================
    
    def trigger_automation(
        self,
        doc_id: str,
        rule_id: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Trigger a webhook automation.
        
        Args:
            doc_id: The doc ID
            rule_id: The automation rule ID
            payload: Payload to send to the webhook
            
        Returns:
            Result with request_id
        """
        path = f"/docs/{self._encode_id(doc_id)}/hooks/automation/{self._encode_id(rule_id)}"
        return self._post(path, json_data=payload or {})
    
    # =========================================================================
    # Analytics API
    # =========================================================================
    
    def list_doc_analytics(
        self,
        doc_ids: Optional[List[str]] = None,
        workspace_id: Optional[str] = None,
        query: Optional[str] = None,
        is_published: Optional[bool] = None,
        since_date: Optional[str] = None,
        until_date: Optional[str] = None,
        scale: str = "daily",
        limit: int = 1000,
        page_token: Optional[str] = None,
        order_by: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get doc analytics data.
        
        Args:
            doc_ids: Filter by doc IDs
            workspace_id: Filter by workspace
            query: Search query
            is_published: Filter by published status
            since_date: Start date (YYYY-MM-DD)
            until_date: End date (YYYY-MM-DD)
            scale: "daily" or "cumulative"
            limit: Maximum results (1-5000)
            page_token: Pagination token
            order_by: Sort field
            direction: "ascending" or "descending"
            
        Returns:
            Analytics data with items
        """
        params = {
            "workspaceId": workspace_id,
            "query": query,
            "isPublished": is_published,
            "sinceDate": since_date,
            "untilDate": until_date,
            "scale": scale,
            "limit": limit,
            "pageToken": page_token,
            "orderBy": order_by,
            "direction": direction,
        }
        if doc_ids:
            params["docIds"] = ",".join(doc_ids)
        
        return self._get("/analytics/docs", params=params)
    
    def get_doc_analytics_summary(
        self,
        is_published: Optional[bool] = None,
        since_date: Optional[str] = None,
        until_date: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get summarized doc analytics.
        
        Args:
            is_published: Filter by published status
            since_date: Start date (YYYY-MM-DD)
            until_date: End date (YYYY-MM-DD)
            workspace_id: Filter by workspace
            
        Returns:
            Summary with totalSessions
        """
        params = {
            "isPublished": is_published,
            "sinceDate": since_date,
            "untilDate": until_date,
            "workspaceId": workspace_id,
        }
        return self._get("/analytics/docs/summary", params=params)
    
    def list_page_analytics(
        self,
        doc_id: str,
        since_date: Optional[str] = None,
        until_date: Optional[str] = None,
        limit: int = 1000,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get page analytics for a doc (Enterprise workspaces only).
        
        Args:
            doc_id: The doc ID
            since_date: Start date (YYYY-MM-DD)
            until_date: End date (YYYY-MM-DD)
            limit: Maximum results (1-5000)
            page_token: Pagination token
            
        Returns:
            Page analytics data
        """
        params = {
            "sinceDate": since_date,
            "untilDate": until_date,
            "limit": limit,
            "pageToken": page_token,
        }
        path = f"/analytics/docs/{self._encode_id(doc_id)}/pages"
        return self._get(path, params=params)
    
    # =========================================================================
    # Miscellaneous API
    # =========================================================================
    
    def whoami(self) -> User:
        """
        Get info about the current user.
        
        Returns:
            User info
        """
        data = self._get("/whoami")
        return User.from_dict(data)
    
    def resolve_browser_link(
        self,
        url: str,
        degrade_gracefully: bool = False,
    ) -> Dict[str, Any]:
        """
        Resolve a Coda browser URL to API metadata.
        
        Args:
            url: The browser URL to resolve
            degrade_gracefully: Return parent if resource deleted
            
        Returns:
            Resolved resource info with API href
        """
        params = {"url": url}
        if degrade_gracefully:
            params["degradeGracefully"] = True
        
        return self._get("/resolveBrowserLink", params=params)
    
    def get_mutation_status(self, request_id: str) -> MutationStatus:
        """
        Get status of an async mutation.
        
        Args:
            request_id: The mutation request ID
            
        Returns:
            MutationStatus with completed flag
        """
        path = f"/mutationStatus/{request_id}"
        data = self._get(path)
        return MutationStatus.from_dict(data)
