# Scrape - MCP Tool Specification

This document outlines the specification for tools within the Scrape module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Scrape module provides web scraping capabilities with support for multiple scraping providers (currently Firecrawl), including page scraping, crawling, site mapping, search, and structured extraction in multiple output formats (Markdown, HTML, raw text) for internal use by other Codomyrmex modules. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal web scraping and content extraction mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., scraping a URL and returning structured content on demand, or crawling a site and returning a sitemap), this document will be updated accordingly.

For details on how to use the scrape functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
