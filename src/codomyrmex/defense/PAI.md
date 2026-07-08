# Personal AI Infrastructure - Defense Module

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

The defense module provides local active-defense primitives for PAI trust gates:
prompt-exploit detection, honeytokens, context poisoning, rate limiting, threat
rules, and rabbit-hole containment. It is used by demos, security workflows, MCP
tools, and the AI-safety facade when agent actions need deterministic safety
screening.

## PAI Capabilities

| Capability | Purpose |
| :--- | :--- |
| Exploit detection | Identify prompt-injection and override attempts before action execution |
| Honeytokens | Emit traceable decoy markers for suspicious interactions |
| Request defense | Combine blocklist, rate-limit, and rule checks for inbound requests |
| Threat reporting | Produce local reports that can feed trust and telemetry surfaces |
| Rabbit-hole containment | Divert contained sources to bounded decoy responses |

## Key Exports

| Export | Type | Purpose |
| :--- | :--- | :--- |
| `ActiveDefense` | Class | Prompt-exploit and honeytoken primitives |
| `Defense` | Class | Request-processing defense orchestrator |
| `RateLimiter` | Class | Sliding-window rate limiting |
| `ThreatDetector` | Class | Detection-rule evaluation |
| `RabbitHole` | Class | Containment and decoy response tracking |
| `defense_detect_exploit` | Function | MCP wrapper for exploit detection |
| `defense_process_request` | Function | MCP wrapper for request checks |
| `defense_threat_report` | Function | MCP wrapper for threat reports |

## PAI Algorithm Phase Mapping

| Phase | Defense Contribution |
| :--- | :--- |
| **OBSERVE** | Detect exploit markers and suspicious request metadata |
| **PLAN** | Flag high-risk sources and rate-limit repeated attempts |
| **BUILD** | Provide deterministic guard checks for generated actions |
| **VERIFY** | Emit threat reports for release and safety gates |
| **LEARN** | Preserve findings that can tune future rules and containment policy |

## MCP Integration

Three safe MCP tools expose bounded defense checks for agent workflows:

| Tool | Description |
| :--- | :--- |
| `defense_detect_exploit` | Inspect text for prompt-exploit indicators |
| `defense_process_request` | Evaluate a request through blocklist, rate-limit, rule, and prompt checks |
| `defense_threat_report` | Summarize recorded active-defense state |

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Module README**: [README.md](README.md)
- **Specification**: [SPEC.md](SPEC.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Tool Specification**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
