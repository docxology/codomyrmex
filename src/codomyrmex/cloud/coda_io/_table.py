"""Table, column, and row models for Coda.io."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ._helpers import _parse_datetime
from ._references import ColumnReference, PageReference, TableReference


@dataclass
class Sort:
    """Sort configuration for a table."""

    column: ColumnReference
    direction: str  # "ascending" or "descending"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Sort":

        return cls(
            column=ColumnReference.from_dict(data.get("column"))
            or ColumnReference(id=""),
            direction=data.get("direction", "ascending"),
        )


@dataclass
class Table:
    """A table in a Coda doc."""

    id: str
    type: str
    table_type: str
    href: str
    name: str
    browser_link: str
    row_count: int
    layout: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    parent: PageReference | None = None
    parent_table: TableReference | None = None
    display_column: ColumnReference | None = None
    sorts: list[Sort] | None = None
    filter: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Table":

        sorts_data = data.get("sorts", [])
        sorts = [Sort.from_dict(s) for s in sorts_data] if sorts_data else None

        return cls(
            id=data.get("id", ""),
            type=data.get("type", "table"),
            table_type=data.get("tableType", "table"),
            href=data.get("href", ""),
            name=data.get("name", ""),
            browser_link=data.get("browserLink", ""),
            row_count=data.get("rowCount", 0),
            layout=data.get("layout", "default"),
            created_at=_parse_datetime(data.get("createdAt")),
            updated_at=_parse_datetime(data.get("updatedAt")),
            parent=PageReference.from_dict(data.get("parent")),
            parent_table=TableReference.from_dict(data.get("parentTable")),
            display_column=ColumnReference.from_dict(data.get("displayColumn")),
            sorts=sorts,
            filter=data.get("filter"),
        )


@dataclass
class TableList:
    """list of tables with pagination."""

    items: list[Table]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TableList":

        return cls(
            items=[Table.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


@dataclass
class Column:
    """A column in a Coda table."""

    id: str
    type: str
    href: str
    name: str
    format: dict[str, Any]
    display: bool = False
    calculated: bool = False
    formula: str | None = None
    default_value: str | None = None
    parent: TableReference | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Column":

        return cls(
            id=data.get("id", ""),
            type=data.get("type", "column"),
            href=data.get("href", ""),
            name=data.get("name", ""),
            format=data.get("format", {}),
            display=data.get("display", False),
            calculated=data.get("calculated", False),
            formula=data.get("formula"),
            default_value=data.get("defaultValue"),
            parent=TableReference.from_dict(data.get("parent")),
        )


@dataclass
class ColumnList:
    """list of columns with pagination."""

    items: list[Column]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ColumnList":

        return cls(
            items=[Column.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


@dataclass
class Row:
    """A row in a Coda table."""

    id: str
    type: str
    href: str
    name: str
    index: int
    browser_link: str
    values: dict[str, Any]
    created_at: datetime | None = None
    updated_at: datetime | None = None
    parent: TableReference | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Row":

        return cls(
            id=data.get("id", ""),
            type=data.get("type", "row"),
            href=data.get("href", ""),
            name=data.get("name", ""),
            index=data.get("index", 0),
            browser_link=data.get("browserLink", ""),
            values=data.get("values", {}),
            created_at=_parse_datetime(data.get("createdAt")),
            updated_at=_parse_datetime(data.get("updatedAt")),
            parent=TableReference.from_dict(data.get("parent")),
        )


@dataclass
class RowList:
    """list of rows with pagination."""

    items: list[Row]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None
    next_sync_token: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RowList":

        return cls(
            items=[Row.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
            next_sync_token=data.get("nextSyncToken"),
        )


@dataclass
class CellEdit:
    """A cell value edit."""

    column: str  # Column ID or name
    value: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "column": self.column,
            "value": self.value,
        }


@dataclass
class RowEdit:
    """A row edit with cell values."""

    cells: list[CellEdit]

    def to_dict(self) -> dict[str, Any]:
        return {"cells": [cell.to_dict() for cell in self.cells]}
