"""Enums for Coda.io data models."""

from enum import Enum


class TableType(Enum):
    """Type of table in Coda."""

    TABLE = "table"
    VIEW = "view"


class PageType(Enum):
    """Type of page content."""

    CANVAS = "canvas"
    EMBED = "embed"
    SYNC_PAGE = "syncPage"


class ControlType(Enum):
    """Type of control widget."""

    AI_BLOCK = "aiBlock"
    BUTTON = "button"
    CHECKBOX = "checkbox"
    DATE_PICKER = "datePicker"
    DATE_RANGE_PICKER = "dateRangePicker"
    DATE_TIME_PICKER = "dateTimePicker"
    LOOKUP = "lookup"
    MULTISELECT = "multiselect"
    SELECT = "select"
    SCALE = "scale"
    SLIDER = "slider"
    REACTION = "reaction"
    TEXTBOX = "textbox"
    TIME_PICKER = "timePicker"


class AccessType(Enum):
    """Permission access level."""

    NONE = "none"
    READONLY = "readonly"
    WRITE = "write"
    COMMENT = "comment"


class DocPublishMode(Enum):
    """Publishing mode for docs."""

    VIEW = "view"
    PLAY = "play"
    EDIT = "edit"


class ValueFormat(Enum):
    """Format for cell values."""

    SIMPLE = "simple"
    SIMPLE_WITH_ARRAYS = "simpleWithArrays"
    RICH = "rich"
