# Accessibility - API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Accessibility module provides WCAG compliance checking, color contrast calculation, and heading hierarchy validation. All checks are configurable by WCAG conformance level (A, AA, AAA).

## Enums

### `WCAGLevel`

WCAG conformance levels.

- `WCAGLevel.A` - Level A (minimum)
- `WCAGLevel.AA` - Level AA (recommended)
- `WCAGLevel.AAA` - Level AAA (enhanced)

### `IssueType`

Accessibility issue severity.

- `IssueType.ERROR` - Failure that must be fixed
- `IssueType.WARNING` - Potential issue to review
- `IssueType.NOTICE` - Informational finding

## Data Classes

### `AccessibilityIssue`

Represents a single accessibility finding.

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `code` | `str` | required | Rule code (e.g., `"img-alt"`) |
| `message` | `str` | required | Human-readable description |
| `selector` | `str` | `""` | CSS selector of the element |
| `issue_type` | `IssueType` | `IssueType.ERROR` | Severity level |
| `wcag_criterion` | `str` | `""` | WCAG criterion (e.g., `"1.1.1"`) |
| `wcag_level` | `WCAGLevel` | `WCAGLevel.A` | Required conformance level |
| `suggestion` | `str` | `""` | Remediation guidance |

### `AccessibilityReport`

Aggregated audit results.

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `url` | `str` | `""` | Audited URL or identifier |
| `issues` | `list[AccessibilityIssue]` | `[]` | All findings |
| `passed` | `int` | `0` | Number of passed checks |
| `warnings` | `int` | `0` | Number of warnings |
| `errors` | `int` | `0` | Number of errors |

#### Property: `score -> float`

Returns a percentage score: `(passed / (passed + errors)) * 100`. Returns `100.0` when no checks were run.

## Classes

### `WCAGRule`

#### `WCAGRule.__init__(code, criterion, level, check_fn, message, suggestion="")`

- **Parameters**:
    - `code` (str): Rule identifier.
    - `criterion` (str): WCAG success criterion number.
    - `level` (WCAGLevel): Required conformance level.
    - `check_fn` (Callable[[dict], bool]): Returns True if element passes.
    - `message` (str): Failure description.
    - `suggestion` (str): Remediation advice.

#### `WCAGRule.check(element) -> AccessibilityIssue | None`

- **Description**: Run the rule against an element dict. Returns an `AccessibilityIssue` on failure, `None` on pass.
- **Parameters**:
    - `element` (dict[str, Any]): Element attributes. Expected keys vary by rule (e.g., `tag`, `alt`, `text`, `contrast_ratio`, `focusable`, `has_focus_style`, `selector`).

### `A11yChecker`

Primary checker that aggregates rules and runs audits.

#### `A11yChecker.__init__(level=WCAGLevel.AA)`

- **Description**: Initialize checker with target conformance level. Loads five default rules: `img-alt` (1.1.1/A), `form-label` (1.3.1/A), `link-text` (2.4.4/A), `color-contrast` (1.4.3/AA), `focus-visible` (2.4.7/AA).

#### `A11yChecker.add_rule(rule) -> None`

- **Description**: Register an additional `WCAGRule`.

#### `A11yChecker.check_elements(elements) -> AccessibilityReport`

- **Description**: Run all applicable rules against a list of element dicts. Rules above the checker's target level are skipped.
- **Parameters**:
    - `elements` (list[dict[str, Any]]): Element attribute dicts.
- **Returns**: `AccessibilityReport` with aggregated results.

## Functions

### `calculate_contrast_ratio(fg, bg) -> float`

- **Description**: Calculate the WCAG 2.x luminance contrast ratio between two hex colors.
- **Parameters**:
    - `fg` (str): Foreground hex color (e.g., `"#000000"`).
    - `bg` (str): Background hex color (e.g., `"#FFFFFF"`).
- **Returns**: `float` - Contrast ratio from 1.0 to 21.0. Returns `0.0` on invalid input.

### `check_heading_hierarchy(headings) -> list[str]`

- **Description**: Validate heading level order. Detects skipped levels and missing h1.
- **Parameters**:
    - `headings` (list[int]): Sequence of heading levels (1-6).
- **Returns**: `list[str]` - List of issue descriptions. Empty list means valid hierarchy.

### `AccessibilityReporter`

Formats an `AccessibilityReport` for various output targets.

#### `AccessibilityReporter.__init__(report)`

- **Parameters**:
    - `report` (AccessibilityReport): The report to format.

#### `AccessibilityReporter.to_summary() -> str`

- **Description**: One-line summary string: `"Score: 85.0% | 17 passed, 2 errors, 1 warning"`.

#### `AccessibilityReporter.to_dict() -> dict[str, Any]`

- **Description**: Full report as a serializable dictionary with `url`, `score`, `passed`, `errors`, `warnings`, and `issues` list.

#### `AccessibilityReporter.to_json(indent=2) -> str`

- **Description**: JSON string of the report (calls `to_dict()` internally).

#### `AccessibilityReporter.to_markdown() -> str`

- **Description**: Markdown formatted report with heading, score summary, and an issues table with columns: Code, Level, Type, Message, Suggestion.

## Error Handling

Functions return empty/zero values on invalid input rather than raising exceptions. `calculate_contrast_ratio` returns `0.0` for malformed hex strings. `check_heading_hierarchy` handles empty lists gracefully.

## Configuration

The `A11yChecker` target level is set at construction time. No external configuration files are required. Custom rules are added via `add_rule()`.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
