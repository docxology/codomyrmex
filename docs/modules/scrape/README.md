# Scrape Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Web scraping with selectors, pagination, and rate limiting.

## Key Features

- **Selectors** — CSS and XPath
- **Pagination** — Multi-page scraping
- **Rate Limit** — Respect rate limits
- **Async** — Async scraping

## Quick Start

```python
from codomyrmex.scrape import Scraper, Selector

scraper = Scraper(rate_limit=1.0)
page = await scraper.get("https://example.com")

title = page.select("h1").text
links = page.select_all("a").attrs("href")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/scrape/](../../../src/codomyrmex/scrape/)
- **Parent**: [Modules](../README.md)
