# Defense Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `defense` module implements "Fiduciary Defense" capabilities. It actively monitors for cognitive exploits (jailbreaks, prompt injections) and responds with active countermeasures like "poisoned context" or "rabbit holes".

## Key Capabilities

- **Exploit Detection**: Heuristic scanning for known attack patterns (`ActiveDefense.detect_exploit`).
- **Active Countermeasures**: Injecting adversarial noise ("poison") to disrupt attacker models.
- **Rabbit Hole Containment**: trapping persistent attackers in simulated loops (`RabbitHole`).

## Core Components

- `ActiveDefense`: Main engine for detection and response.
- `RabbitHole`: Simulation environment for containment.

## Navigation

- **Full Documentation**: [docs/modules/defense/](../../../docs/modules/defense/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
