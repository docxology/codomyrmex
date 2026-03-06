# Scrape -- Configuration Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the scrape module. HTML content extraction and text similarity analysis.

## Configuration Requirements

Before using scrape in any PAI workflow, ensure:

1. `FIRECRAWL_API_KEY` is set -- API key for Firecrawl scraping service
2. `FC_API_KEY` is set -- Alternative API key for Firecrawl (fallback)
3. `SCRAPE_BASE_URL` is set (default: `https://api.firecrawl.dev`) -- Base URL for scraping service endpoint
4. `SCRAPE_TIMEOUT` is set (default: `30.0`) -- Request timeout in seconds for scraping operations
5. `SCRAPE_MAX_RETRIES` is set (default: `3`) -- Maximum retry attempts for failed scrape requests
6. `SCRAPE_RETRY_DELAY` is set (default: `1.0`) -- Delay in seconds between retry attempts

## Agent Instructions

1. Verify required environment variables are set before invoking scrape tools
2. Use `get_config("scrape.<key>")` from config_management to read module settings
3. Available MCP tools: `scrape_extract_content`, `scrape_text_similarity`
4. Firecrawl API key is required for web scraping. URL validation enforces http/https scheme. Retry and timeout settings control resilience.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("scrape.setting")

# Update configuration
set_config("scrape.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/scrape/AGENTS.md)
