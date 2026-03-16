# SAIR PAI Bridge

**Module**: scripts/sair  
**Status**: 🟢 Active (v0.1.0)  
**Last Review**: March 2026

## Core Objectives

1. **Bridge to SAIR Foundation**: Enable seamless participation in the Mathematics Distillation challenge.
2. **Local Distortion Engine**: Provide high-fidelity local replication of the official evaluation environment.
3. **Data Parity**: Maintain synchronized access to the 22M Equational Theories Project implication graph.

## Capability Map

| Capability | Script | Status | Verification |
| :--- | :--- | :--- | :--- |
| **Data Download** | `download_data.py` | 🟢 Active | Verified with `normal.jsonl` |
| **Playground Eval** | `evaluate.py` | 🟢 Active | Accuracy parity check (Gemini 2.5) |
| **Prompt Gen** | `generate_cheatsheet.py` | 🟢 Active | Size enforcement check |

## Knowledge Anchors

- [Equational Theories Project](https://github.com/teorth/equational_theories)
- [SAIR Challenge](https://competition.sair.foundation)
- [Jinja2 Prompt Template](./SPEC.md#evaluation-template)

## Telemetry & Maintenance

- All evaluation runs should be logged to `output/logs/` in structured JSON format.
- Performance metrics (accuracy, cost, latency) to be aggregated daily.
