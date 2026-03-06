# Scrape Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

HTML content extraction and text similarity analysis. Provides web scraping with Firecrawl integration, content parsing, and text comparison utilities.

## Quick Configuration

```bash
export FIRECRAWL_API_KEY=""    # API key for Firecrawl scraping service (required)
export FC_API_KEY=""    # Alternative API key for Firecrawl (fallback) (required)
export SCRAPE_BASE_URL="https://api.firecrawl.dev"    # Base URL for scraping service endpoint
export SCRAPE_TIMEOUT="30.0"    # Request timeout in seconds for scraping operations
export SCRAPE_MAX_RETRIES="3"    # Maximum retry attempts for failed scrape requests
export SCRAPE_RETRY_DELAY="1.0"    # Delay in seconds between retry attempts
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `FIRECRAWL_API_KEY` | str | None | API key for Firecrawl scraping service |
| `FC_API_KEY` | str | None | Alternative API key for Firecrawl (fallback) |
| `SCRAPE_BASE_URL` | str | `https://api.firecrawl.dev` | Base URL for scraping service endpoint |
| `SCRAPE_TIMEOUT` | str | `30.0` | Request timeout in seconds for scraping operations |
| `SCRAPE_MAX_RETRIES` | str | `3` | Maximum retry attempts for failed scrape requests |
| `SCRAPE_RETRY_DELAY` | str | `1.0` | Delay in seconds between retry attempts |

## MCP Tools

This module exposes 2 MCP tool(s):

- `scrape_extract_content`
- `scrape_text_similarity`

## PAI Integration

PAI agents invoke scrape tools through the MCP bridge. Firecrawl API key is required for web scraping. URL validation enforces http/https scheme. Retry and timeout settings control resilience.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep scrape

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/scrape/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
