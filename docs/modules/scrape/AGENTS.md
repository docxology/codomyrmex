# Scrape Module — Agent Coordination

## Purpose

Scrape Module for Codomyrmex.

## Key Capabilities

- Scrape operations and management

## Agent Usage Patterns

```python
from codomyrmex.scrape import *

# Agent uses scrape capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/scrape/](../../../src/codomyrmex/scrape/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`ScrapeConfig`** — Configuration for scraping operations.
- **`ScrapeFormat`** — Supported output formats for scraping operations.
- **`ScrapeResult`** — Standard result structure for scraping operations.
- **`ScrapeOptions`** — Configuration options for scraping operations.
- **`CrawlResult`** — Result structure for crawl operations.
- **`get_config()`** — Get the global configuration instance.
- **`set_config()`** — Set the global configuration instance.
- **`reset_config()`** — Reset the global configuration to None.

### Submodules

- `firecrawl` — Firecrawl

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k scrape -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
