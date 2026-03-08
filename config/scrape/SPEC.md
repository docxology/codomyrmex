# Scrape Configuration Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

HTML content extraction and text similarity analysis. Provides web scraping with Firecrawl integration, content parsing, and text comparison utilities. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `FIRECRAWL_API_KEY` | string | Yes | None | API key for Firecrawl scraping service |
| `FC_API_KEY` | string | Yes | None | Alternative API key for Firecrawl (fallback) |
| `SCRAPE_BASE_URL` | string | No | `https://api.firecrawl.dev` | Base URL for scraping service endpoint |
| `SCRAPE_TIMEOUT` | string | No | `30.0` | Request timeout in seconds for scraping operations |
| `SCRAPE_MAX_RETRIES` | string | No | `3` | Maximum retry attempts for failed scrape requests |
| `SCRAPE_RETRY_DELAY` | string | No | `1.0` | Delay in seconds between retry attempts |

## Environment Variables

```bash
# Required
export FIRECRAWL_API_KEY=""    # API key for Firecrawl scraping service
export FC_API_KEY=""    # Alternative API key for Firecrawl (fallback)

# Optional (defaults shown)
export SCRAPE_BASE_URL="https://api.firecrawl.dev"    # Base URL for scraping service endpoint
export SCRAPE_TIMEOUT="30.0"    # Request timeout in seconds for scraping operations
export SCRAPE_MAX_RETRIES="3"    # Maximum retry attempts for failed scrape requests
export SCRAPE_RETRY_DELAY="1.0"    # Delay in seconds between retry attempts
```

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- `FIRECRAWL_API_KEY` must be set before module initialization
- `FC_API_KEY` must be set before module initialization
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/scrape/SPEC.md)
