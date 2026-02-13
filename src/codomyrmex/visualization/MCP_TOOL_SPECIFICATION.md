# Visualization - MCP Tool Specification

This document outlines the specification for tools within the Visualization module that are intended to be integrated with the Model Context Protocol (MCP).

## Current Status: No MCP Tools Defined

The Visualization module provides a unified dashboard and plotting system including 20+ plot types (scatter, heatmap, bar, line, histogram, pie, box, area, violin, radar, candlestick, Gantt, funnel, Sankey, word cloud, confusion matrix, treemap, network graph, Mermaid diagrams), UI components (cards, tables, alerts, progress bars, timelines), and report generation (general, finance, marketing, logistics) for internal use by other Codomyrmex modules. These functions are primarily for programmatic integration within the application lifecycle and are not suited for exposure as Model Context Protocol (MCP) tools.

MCP tools are typically designed for discrete, invocable actions or queries that an external agent (like an LLM) would trigger. The internal visualization rendering, dashboard composition, and report generation mechanisms do not fit this paradigm.

If future enhancements to this module introduce features that are appropriate for MCP (e.g., generating a chart from structured data and returning an image or HTML snippet, or creating a dashboard report on demand), this document will be updated accordingly.

For details on how to use the visualization functionalities within your Python code, please refer to the module's `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
