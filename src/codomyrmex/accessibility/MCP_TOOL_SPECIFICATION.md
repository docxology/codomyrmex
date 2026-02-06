# Accessibility - MCP Tool Specification

## General Considerations for Accessibility Tools

- **Dependencies**: No external dependencies. Pure Python implementation.
- **Initialization**: `A11yChecker` is instantiated per-request with the specified WCAG level.
- **Error Handling**: Tools return `{"error": "description"}` on failure. Invalid hex colors return a ratio of `0.0`.
- **Colors**: All color parameters use 6-digit hex format with `#` prefix.

---

## Tool: `a11y_check`

### 1. Tool Purpose and Description

Runs a full accessibility audit against a list of HTML element descriptors. Applies all WCAG rules up to the specified conformance level and returns a scored report.

### 2. Invocation Name

`a11y_check`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `elements` | `array[object]` | Yes | Element attribute dicts with keys like `tag`, `alt`, `text`, `label`, `contrast_ratio`, `focusable`, `has_focus_style`, `selector` | `[{"tag": "img", "alt": "", "selector": "#logo"}]` |
| `level` | `string` | No | WCAG target level: `"A"`, `"AA"`, or `"AAA"`. Default: `"AA"` | `"AA"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `score` | `number` | Percentage of passed checks | `85.0` |
| `passed` | `integer` | Number of passed checks | `17` |
| `errors` | `integer` | Number of errors | `3` |
| `warnings` | `integer` | Number of warnings | `0` |
| `issues` | `array[object]` | List of `{code, message, selector, wcag_criterion, wcag_level, suggestion}` | See below |

### 5. Error Handling

- `INVALID_LEVEL`: Unrecognized WCAG level string.
- `INVALID_ELEMENTS`: Elements parameter is not a valid array.

### 6. Idempotency

- **Idempotent**: Yes. Same elements and level always produce the same report.

### 7. Usage Examples

```json
{
  "tool_name": "a11y_check",
  "arguments": {
    "elements": [
      {"tag": "img", "alt": "", "selector": "header img"},
      {"tag": "a", "text": "", "selector": "nav a.icon"},
      {"tag": "input", "label": "Email", "selector": "#email"}
    ],
    "level": "AA"
  }
}
```

### 8. Security Considerations

- **Input Validation**: Element dicts are read-only; unknown keys are ignored.
- **Data Handling**: No file system access. Pure computation.

---

## Tool: `a11y_contrast_check`

### 1. Tool Purpose and Description

Checks the WCAG luminance contrast ratio between a foreground and background color pair. Reports whether the combination meets the specified level's requirements (4.5:1 for AA normal text, 3:1 for AA large text, 7:1 for AAA).

### 2. Invocation Name

`a11y_contrast_check`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `foreground` | `string` | Yes | Foreground hex color | `"#333333"` |
| `background` | `string` | Yes | Background hex color | `"#FFFFFF"` |
| `level` | `string` | No | Target WCAG level. Default: `"AA"` | `"AA"` |
| `large_text` | `boolean` | No | Whether text is large (>=18pt or 14pt bold). Default: `false` | `false` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `ratio` | `number` | Computed contrast ratio | `12.63` |
| `passes` | `boolean` | Whether ratio meets the target | `true` |
| `required_ratio` | `number` | Minimum ratio for the target | `4.5` |
| `foreground` | `string` | Input foreground color | `"#333333"` |
| `background` | `string` | Input background color | `"#FFFFFF"` |

### 5. Error Handling

- `INVALID_COLOR`: Hex color string could not be parsed. Returns ratio `0.0`.

### 6. Idempotency

- **Idempotent**: Yes. Pure mathematical computation.

### 7. Usage Examples

```json
{
  "tool_name": "a11y_contrast_check",
  "arguments": {
    "foreground": "#767676",
    "background": "#FFFFFF",
    "level": "AA",
    "large_text": false
  }
}
```

### 8. Security Considerations

- **Input Validation**: Colors are validated as 6-digit hex strings.
- **Data Handling**: No state, no side effects.

---

## Tool: `a11y_heading_check`

### 1. Tool Purpose and Description

Validates the heading level hierarchy of a document. Detects skipped heading levels (e.g., h1 to h3) and verifies the document starts with h1.

### 2. Invocation Name

`a11y_heading_check`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `headings` | `array[integer]` | Yes | Ordered list of heading levels (1-6) as they appear in the document | `[1, 2, 2, 4, 2]` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `valid` | `boolean` | True if no issues found | `false` |
| `issues` | `array[string]` | List of issue descriptions | `["Skipped heading level: h2 to h4"]` |
| `heading_count` | `integer` | Total headings analyzed | `5` |

### 5. Error Handling

- `INVALID_HEADINGS`: Parameter is not an array of integers.

### 6. Idempotency

- **Idempotent**: Yes. Pure validation.

### 7. Usage Examples

```json
{
  "tool_name": "a11y_heading_check",
  "arguments": {
    "headings": [1, 2, 3, 3, 2, 3]
  }
}
```

### 8. Security Considerations

- **Input Validation**: Values outside 1-6 are accepted but produce meaningless results.
- **Data Handling**: No state, no side effects.

---

## Navigation Links

- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Human Documentation**: [README.md](README.md)
- **Parent Directory**: [codomyrmex](../README.md)
