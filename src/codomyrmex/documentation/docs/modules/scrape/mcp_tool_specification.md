# Scrape - MCP Tool Specification

This document outlines the specification for tools within the Scrape module that are integrated with the Model Context Protocol (MCP).

---

## Tool: `scrape_extract_content`

### 1. Tool Purpose and Description

Extracts structured content (title, headings, links, paragraphs, images) from a raw HTML string. Returns metadata and element counts.

### 2. Invocation Name

`scrape_extract_content`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `html` | `string` | Yes | Raw HTML string to extract content from | `"<html><body><h1>Hello</h1></body></html>"` |
| `base_url` | `string` | No | Base URL for resolving relative links (default: `""`) | `"https://example.com"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` on success, `"error"` on failure | `"ok"` |
| `title` | `string` | Page title extracted from `<title>` or first `<h1>` | `"My Page"` |
| `headings` | `array[object]` | List of `{"level": int, "text": str}` heading objects | `[{"level": 1, "text": "Hello"}]` |
| `paragraph_count` | `integer` | Number of `<p>` elements found | `12` |
| `link_count` | `integer` | Number of `<a href>` links found | `7` |
| `image_count` | `integer` | Number of `<img>` elements found | `3` |
| `word_count` | `integer` | Total word count across all text nodes | `450` |
| `content_hash` | `string` | Hash of the extracted text content | `"a3f2b1..."` |
| `meta` | `object` | Extracted `<meta>` tag key-value pairs | `{"description": "..."}` |
| `error` | `string` | Error message (only present when `status == "error"`) | `"Failed to parse HTML"` |

### 5. Error Handling

- Returns `{"status": "error", "error": "<message>"}` if extraction fails
- Does not raise exceptions — all errors are captured in the return value

### 6. Idempotency

- **Idempotent**: Yes — same HTML input always produces the same output

### 7. Usage Examples

```json
{
  "tool_name": "scrape_extract_content",
  "arguments": {
    "html": "<html><head><title>Test</title></head><body><h1>Hello</h1><p>World</p></body></html>",
    "base_url": "https://example.com"
  }
}
```

**Example response:**
```json
{
  "status": "ok",
  "title": "Test",
  "headings": [{"level": 1, "text": "Hello"}],
  "paragraph_count": 1,
  "link_count": 0,
  "image_count": 0,
  "word_count": 2,
  "content_hash": "...",
  "meta": {}
}
```

### 8. Security Considerations

- **No Network Calls**: Operates entirely on the provided HTML string — no outbound requests
- **Input Size**: Very large HTML strings may increase processing time

---

## Tool: `scrape_text_similarity`

### 1. Tool Purpose and Description

Computes the Jaccard word-level similarity score between two text strings. Returns a float in `[0.0, 1.0]` where `1.0` means identical word sets and `0.0` means no words in common.

### 2. Invocation Name

`scrape_text_similarity`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `text_a` | `string` | Yes | First text string | `"the quick brown fox"` |
| `text_b` | `string` | Yes | Second text string | `"the quick red fox"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` on success, `"error"` on failure | `"ok"` |
| `similarity` | `float` | Jaccard similarity score in range `[0.0, 1.0]` | `0.6` |
| `error` | `string` | Error message (only present when `status == "error"`) | `"..."` |

### 5. Error Handling

- Returns `{"status": "error", "error": "<message>"}` if comparison fails
- Both empty strings produces `similarity: 0.0`

### 6. Idempotency

- **Idempotent**: Yes

### 7. Usage Examples

```json
{
  "tool_name": "scrape_text_similarity",
  "arguments": {
    "text_a": "the quick brown fox",
    "text_b": "the quick red fox"
  }
}
```

**Example response:**
```json
{
  "status": "ok",
  "similarity": 0.6
}
```

### 8. Security Considerations

- **No Network Calls**: Pure text comparison, no I/O

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
