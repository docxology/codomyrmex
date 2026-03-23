"""Formula and control elements for Coda.io."""

from dataclasses import dataclass
from typing import Any

from ._references import PageReference


@dataclass
class Formula:
    """A named formula in a Coda doc."""

    id: str
    type: str
    href: str
    name: str
    value: Any
    parent: PageReference | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Formula":
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "formula"),
            href=data.get("href", ""),
            name=data.get("name", ""),
            value=data.get("value"),
            parent=PageReference.from_dict(data.get("parent")),
        )


@dataclass
class FormulaList:
    """list of formulas with pagination."""

    items: list[Formula]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormulaList":

        return cls(
            items=[Formula.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )


@dataclass
class Control:
    """A control in a Coda doc."""

    id: str
    type: str
    href: str
    name: str
    control_type: str
    value: Any
    parent: PageReference | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Control":

        return cls(
            id=data.get("id", ""),
            type=data.get("type", "control"),
            href=data.get("href", ""),
            name=data.get("name", ""),
            control_type=data.get("controlType", ""),
            value=data.get("value"),
            parent=PageReference.from_dict(data.get("parent")),
        )


@dataclass
class ControlList:
    """list of controls with pagination."""

    items: list[Control]
    href: str | None = None
    next_page_token: str | None = None
    next_page_link: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ControlList":

        return cls(
            items=[Control.from_dict(item) for item in data.get("items", [])],
            href=data.get("href"),
            next_page_token=data.get("nextPageToken"),
            next_page_link=data.get("nextPageLink"),
        )
