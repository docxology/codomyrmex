# reports/ - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Reports layer with templates and output directories for analysis documentation.

## Functional Requirements

### FR-1: Report Generation

- Support multiple output formats (HTML, JSON, Markdown)
- Include summary metrics and file details
- Professional styling for HTML reports

### FR-2: Dashboard Generation

- Interactive HTML dashboards
- Metric cards and charts
- File analysis tables

## Output Formats

### HTML Report Structure

- Header with title and metadata
- Summary metrics grid
- Pattern distribution chart
- File analysis table
- Issues summary

### JSON Report Structure

```json
{
  "metadata": { "title", "author", "generated_at" },
  "target": "string",
  "summary": { ... },
  "files": [ ... ]
}
```

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Agent Coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [../README.md](../README.md)
