# Codomyrmex Agents — src/codomyrmex/scrape/firecrawl

## Signposting
- **Parent**: [scrape](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Firecrawl scraping provider integration. Provides adapter and client for Firecrawl API, enabling web scraping, crawling, and content extraction through the Firecrawl service.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `adapter.py` – Firecrawl adapter implementation
- `client.py` – Firecrawl API client

## Key Classes and Functions

### FirecrawlClient (`client.py`)
- `FirecrawlClient(api_key: str)` – Firecrawl API client
- `scrape(url: str, **kwargs) -> dict` – Scrape URL
- `crawl(url: str, **kwargs) -> dict` – Crawl website
- `search(query: str, **kwargs) -> dict` – Search web content

### FirecrawlAdapter (`adapter.py`)
- `FirecrawlAdapter()` – Adapter for integrating Firecrawl with scrape module
- Implements scrape module interfaces for Firecrawl provider

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [scrape](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation