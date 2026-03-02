"""
CLI Output Formatters.

Provides formatters for consistent CLI output across different formats.
"""

import json
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from io import StringIO
from typing import Any, Dict, List, Optional, Union


@dataclass
class Column:
    """Definition of a table column."""
    name: str
    key: str
    width: int | None = None
    align: str = "left"    # Optional formatting function
    formatter: Callable | None = None

    def format_value(self, value: Any) -> str:
        """Format a value for this column."""
        if self.formatter:
            value = self.formatter(value)
        text = str(value) if value is not None else ""

        if self.width:
            if self.align == "right":
                return text.rjust(self.width)
            elif self.align == "center":
                return text.center(self.width)
            else:
                return text.ljust(self.width)
        return text


class OutputFormatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def format_data(self, data: Any) -> str:
        """Format data for output."""
        pass

    @abstractmethod
    def format_table(self, data: list[dict], columns: list[Column] | None = None) -> str:
        """Format tabular data."""
        pass

    @abstractmethod
    def format_list(self, items: list[Any]) -> str:
        """Format a list of items."""
        pass

    @abstractmethod
    def format_key_value(self, data: dict[str, Any]) -> str:
        """Format key-value pairs."""
        pass


class PlainFormatter(OutputFormatter):
    """Plain text formatter."""

    def format_data(self, data: Any) -> str:
        if isinstance(data, (dict, list)):
            return json.dumps(data, indent=2)
        return str(data)

    def format_table(self, data: list[dict], columns: list[Column] | None = None) -> str:
        if not data:
            return "No data"

        if columns is None:
            # Auto-detect columns from first row
            columns = [Column(name=k, key=k) for k in data[0].keys()]

        # Calculate column widths
        for col in columns:
            if col.width is None:
                col.width = max(
                    len(col.name),
                    max(len(str(row.get(col.key, ""))) for row in data)
                )

        # Build table
        lines = []

        # Header
        header = " | ".join(col.format_value(col.name) for col in columns)
        lines.append(header)
        lines.append("-" * len(header))

        # Rows
        for row in data:
            line = " | ".join(
                col.format_value(row.get(col.key, ""))
                for col in columns
            )
            lines.append(line)

        return "\n".join(lines)

    def format_list(self, items: list[Any]) -> str:
        return "\n".join(f"  - {item}" for item in items)

    def format_key_value(self, data: dict[str, Any]) -> str:
        max_key_len = max(len(k) for k in data.keys()) if data else 0
        lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            lines.append(f"{key.ljust(max_key_len)}: {value}")
        return "\n".join(lines)


class JSONFormatter(OutputFormatter):
    """JSON formatter for machine-readable output."""

    def __init__(self, indent: int = 2, compact: bool = False):
        self.indent = None if compact else indent

    def format_data(self, data: Any) -> str:
        return json.dumps(data, indent=self.indent, default=str)

    def format_table(self, data: list[dict], columns: list[Column] | None = None) -> str:
        return self.format_data(data)

    def format_list(self, items: list[Any]) -> str:
        return self.format_data(items)

    def format_key_value(self, data: dict[str, Any]) -> str:
        return self.format_data(data)


class TableFormatter(OutputFormatter):
    """Rich table formatter with borders."""

    def __init__(
        self,
        border_style: str = "single",  # single, double, ascii, none
        show_header: bool = True,
        row_separator: bool = False,
    ):
        self.border_style = border_style
        self.show_header = show_header
        self.row_separator = row_separator
        self._borders = self._get_borders()

    def _get_borders(self) -> dict[str, str]:
        """Get border characters based on style."""
        styles = {
            "single": {
                "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
                "h": "─", "v": "│",
                "ml": "├", "mr": "┤", "mt": "┬", "mb": "┴",
                "c": "┼"
            },
            "double": {
                "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
                "h": "═", "v": "║",
                "ml": "╠", "mr": "╣", "mt": "╦", "mb": "╩",
                "c": "╬"
            },
            "ascii": {
                "tl": "+", "tr": "+", "bl": "+", "br": "+",
                "h": "-", "v": "|",
                "ml": "+", "mr": "+", "mt": "+", "mb": "+",
                "c": "+"
            },
            "none": {
                "tl": " ", "tr": " ", "bl": " ", "br": " ",
                "h": " ", "v": " ",
                "ml": " ", "mr": " ", "mt": " ", "mb": " ",
                "c": " "
            }
        }
        return styles.get(self.border_style, styles["single"])

    def format_data(self, data: Any) -> str:
        if isinstance(data, list) and all(isinstance(d, dict) for d in data):
            return self.format_table(data)
        elif isinstance(data, dict):
            return self.format_key_value(data)
        return str(data)

    def format_table(self, data: list[dict], columns: list[Column] | None = None) -> str:
        if not data:
            return "No data"

        if columns is None:
            columns = [Column(name=k, key=k) for k in data[0].keys()]

        # Calculate widths
        for col in columns:
            if col.width is None:
                col.width = max(
                    len(col.name),
                    max(len(str(row.get(col.key, ""))) for row in data)
                )

        b = self._borders
        lines = []

        # Top border
        top = b["tl"] + b["mt"].join(b["h"] * (col.width + 2) for col in columns) + b["tr"]
        lines.append(top)

        # Header
        if self.show_header:
            header = b["v"] + b["v"].join(
                f" {col.name.ljust(col.width)} " for col in columns
            ) + b["v"]
            lines.append(header)

            # Header separator
            sep = b["ml"] + b["c"].join(b["h"] * (col.width + 2) for col in columns) + b["mr"]
            lines.append(sep)

        # Rows
        for i, row in enumerate(data):
            line = b["v"] + b["v"].join(
                f" {col.format_value(row.get(col.key, ''))} "
                for col in columns
            ) + b["v"]
            lines.append(line)

            if self.row_separator and i < len(data) - 1:
                sep = b["ml"] + b["c"].join(b["h"] * (col.width + 2) for col in columns) + b["mr"]
                lines.append(sep)

        # Bottom border
        bottom = b["bl"] + b["mb"].join(b["h"] * (col.width + 2) for col in columns) + b["br"]
        lines.append(bottom)

        return "\n".join(lines)

    def format_list(self, items: list[Any]) -> str:
        data = [{"item": item} for item in items]
        return self.format_table(data, [Column(name="Item", key="item")])

    def format_key_value(self, data: dict[str, Any]) -> str:
        table_data = [{"key": k, "value": v} for k, v in data.items()]
        return self.format_table(
            table_data,
            [Column(name="Key", key="key"), Column(name="Value", key="value")]
        )


class YAMLFormatter(OutputFormatter):
    """YAML-like formatter for readable output."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def _format_value(self, value: Any, level: int = 0) -> str:
        """Recursively format a value."""
        prefix = " " * (self.indent * level)

        if isinstance(value, dict):
            if not value:
                return "{}"
            lines = []
            for k, v in value.items():
                formatted = self._format_value(v, level + 1)
                if "\n" in formatted:
                    lines.append(f"{prefix}{k}:")
                    lines.append(formatted)
                else:
                    lines.append(f"{prefix}{k}: {formatted}")
            return "\n".join(lines)
        elif isinstance(value, list):
            if not value:
                return "[]"
            lines = []
            for item in value:
                formatted = self._format_value(item, level + 1)
                if isinstance(item, dict):
                    lines.append(f"{prefix}-")
                    lines.append(formatted)
                else:
                    lines.append(f"{prefix}- {formatted}")
            return "\n".join(lines)
        elif value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            if "\n" in value or ":" in value:
                return f'"{value}"'
            return value
        else:
            return str(value)

    def format_data(self, data: Any) -> str:
        return self._format_value(data)

    def format_table(self, data: list[dict], columns: list[Column] | None = None) -> str:
        return self.format_data(data)

    def format_list(self, items: list[Any]) -> str:
        return self.format_data(items)

    def format_key_value(self, data: dict[str, Any]) -> str:
        return self.format_data(data)


def create_formatter(format_type: str, **kwargs) -> OutputFormatter:
    """Factory function to create formatters."""
    formatters = {
        "plain": PlainFormatter,
        "json": JSONFormatter,
        "table": TableFormatter,
        "yaml": YAMLFormatter,
    }

    formatter_class = formatters.get(format_type)
    if not formatter_class:
        raise ValueError(f"Unknown format type: {format_type}")

    return formatter_class(**kwargs)


__all__ = [
    "Column",
    "OutputFormatter",
    "PlainFormatter",
    "JSONFormatter",
    "TableFormatter",
    "YAMLFormatter",
    "create_formatter",
]
