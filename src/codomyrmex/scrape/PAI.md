# Personal AI Infrastructure — Scrape Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Scrape module provides PAI integration for web scraping and data extraction.

## PAI Capabilities

### Web Scraping

Scrape web pages:

```python
from codomyrmex.scrape import Scraper

scraper = Scraper(rate_limit=1.0)
page = await scraper.get("https://example.com")

title = page.select("h1").text
links = page.select_all("a.link").attrs("href")
```

### Data Extraction

Extract structured data:

```python
from codomyrmex.scrape import DataExtractor

extractor = DataExtractor()
data = extractor.extract_tables(page)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Scraper` | Web requests |
| `DataExtractor` | Extract data |
| `Selector` | CSS/XPath selection |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
