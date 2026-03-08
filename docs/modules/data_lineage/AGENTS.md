# Data Lineage -- Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Tracks data lineage through transformations with graph-based analysis. Models data assets, transformations, and dependencies as a directed graph for impact analysis and provenance tracking.

## MCP Tools

No MCP tools defined for this module.

## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| OBSERVE | Monitoring Agent | Trace data provenance and transformation history |
| PLAN | Architect Agent | Analyze impact of data pipeline changes |


## Agent Instructions

1. Use LineageTracker to record data transformations as graph edges
2. Use ImpactAnalyzer to determine downstream effects of upstream data changes


## Navigation

- [Source README](../../src/codomyrmex/data_lineage/README.md) | [SPEC.md](SPEC.md)
