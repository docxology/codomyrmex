# Data Lineage Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Data lineage tracking through transformations with graph-based analysis. Provides LineageGraph for dependency visualization and ImpactAnalyzer for change impact assessment.

## Configuration Options

The data_lineage module operates with sensible defaults and does not require environment variable configuration. Lineage graphs are built incrementally as data flows through transformations. Storage is in-memory by default.

## PAI Integration

PAI agents interact with data_lineage through direct Python imports. Lineage graphs are built incrementally as data flows through transformations. Storage is in-memory by default.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep data_lineage

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/data_lineage/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
