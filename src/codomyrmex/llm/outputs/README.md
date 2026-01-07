# outputs

## Signposting
- **Parent**: [outputs](../README.md)
- **Children**:
    - [integration](integration/README.md)
    - [llm_outputs](llm_outputs/README.md)
    - [performance](performance/README.md)
    - [reports](reports/README.md)
    - [test_results](test_results/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Persistence layer for LLM interactions. Stores traces, generation logs, and performance metrics. Provides structured way to debug and analyze LLM interactions with timestamped or ID-based filenames to prevent collisions. Outputs are categorized by type (raw llm_outputs, structured reports, performance metrics).

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `config.json` – File
- `integration/` – Subdirectory
- `llm_outputs/` – Subdirectory
- `model_listing.json` – File
- `ollama_connection.json` – File
- `performance/` – Subdirectory
- `reports/` – Subdirectory
- `test_results/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [llm](../README.md)
- **Project Root**: [README](../../../../README.md)