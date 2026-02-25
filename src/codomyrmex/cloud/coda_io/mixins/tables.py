"""TablesMixin functionality."""

from typing import Any

from codomyrmex.cloud.coda_io.models import (
    Column,
    ColumnList,
    InsertRowsResult,
    Row,
    RowEdit,
    RowList,
    Table,
    TableList,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class TablesMixin:
    """TablesMixin class."""

    def list_tables(
        self,
        doc_id: str,
        limit: int = 25,
        page_token: str | None = None,
        sort_by: str | None = None,
        table_types: list[str] | None = None,
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

    def list_columns(
        self,
        doc_id: str,
        table_id_or_name: str,
        limit: int = 25,
        page_token: str | None = None,
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

    def list_rows(
        self,
        doc_id: str,
        table_id_or_name: str,
        query: str | None = None,
        sort_by: str | None = None,
        use_column_names: bool = False,
        value_format: str = "simple",
        visible_only: bool = False,
        limit: int = 25,
        page_token: str | None = None,
        sync_token: str | None = None,
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
        rows: list[RowEdit | dict[str, Any]],
        key_columns: list[str] | None = None,
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

        body: dict[str, Any] = {"rows": row_dicts}
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
        row: RowEdit | dict[str, Any],
        disable_parsing: bool = False,
    ) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
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
        row_ids: list[str],
    ) -> dict[str, Any]:
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

