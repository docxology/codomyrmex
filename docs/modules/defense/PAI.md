# Personal AI Infrastructure - Defense Module

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

The defense module contributes local active-defense checks to PAI trust gates:
prompt-exploit detection, honeytokens, request screening, threat reporting, and
rabbit-hole containment.

## PAI Phase Mapping

| Phase | Defense Contribution |
| :--- | :--- |
| **OBSERVE** | Detect suspicious prompts and request metadata |
| **PLAN** | Apply blocklists, rate limits, and detection rules |
| **BUILD** | Guard generated actions before execution |
| **VERIFY** | Emit threat reports for safety and release checks |
| **LEARN** | Preserve findings that can tune future defense policy |

## MCP Tools

| Tool | Description |
| :--- | :--- |
| `defense_detect_exploit` | Inspect text for exploit indicators |
| `defense_process_request` | Evaluate request metadata and payload |
| `defense_threat_report` | Return active-defense state summary |
