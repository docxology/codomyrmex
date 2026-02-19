# Biological & Cognitive Perspectives

**Series**: Codomyrmex Bio Docs | **Status**: Active | **Last Updated**: February 2026

## Introduction

The name *codomyrmex* is a portmanteau of the Latin *codo* (to arrange, to order -- here signifying code) and the Greek *myrmex* (ant). This naming is not decorative. Ant colonies are among the most intensively studied examples of distributed computation in nature, and the architectural decisions embedded in codomyrmex draw repeatedly on principles first characterized in myrmecology, behavioral ecology, and cognitive science.

This document series uses biological and cognitive science as analytical lenses to illuminate the design of codomyrmex. Each essay takes a specific concept from the life sciences -- stigmergy, eusociality, active inference, immune function -- and traces its structural analogues through the platform's module system. The goal is not loose metaphor but precise mapping: identifying where codomyrmex modules implement patterns that biologists have formalized, and where those formalisms suggest design improvements or extensions.

The series assumes familiarity with the codomyrmex module architecture described in the [project README](../../README.md) and with the AI integration patterns documented in [PAI.md](../../PAI.md).

## Document Index

The following table maps each essay to its core biological concept and the codomyrmex modules it primarily examines.

| Document | Core Concept | Primary Modules |
|----------|-------------|-----------------|
| [myrmecology.md](./myrmecology.md) | Study of ants, etymology | bio_simulation, spatial, embodiment, relations, governance |
| [stigmergy.md](./stigmergy.md) | Indirect coordination | events, cache, logging_monitoring, agentic_memory, bio_simulation |
| [eusociality.md](./eusociality.md) | Division of labor | agents, orchestrator, plugin_system, identity, system_discovery |
| [swarm_intelligence.md](./swarm_intelligence.md) | Collective decision-making | meme, concurrency, evolutionary_ai, market, graph_rag |
| [superorganism.md](./superorganism.md) | Colony as organism | system_discovery, telemetry, telemetry, model_context_protocol, bio_simulation |
| [immune_system.md](./immune_system.md) | Digital defense | defense, security, identity, privacy, validation, chaos_engineering |
| [memory_and_forgetting.md](./memory_and_forgetting.md) | Memory models | agentic_memory, cache, cerebrum, vector_store, telemetry |
| [evolution.md](./evolution.md) | Selection and fitness | evolutionary_ai, meme, prompt_engineering, model_ops, vector_store |
| [free_energy.md](./free_energy.md) | Active inference | cerebrum, performance, telemetry, logging_monitoring, model_ops |
| [metabolism.md](./metabolism.md) | Resource flow | performance, performance, rate_limiting, performance, cache, streaming |
| [symbiosis.md](./symbiosis.md) | Mutualism, holobiont | model_context_protocol, plugin_system, agents, llm, wallet |

## Suggested Reading Order

The documents are designed to be read independently, but the following sequence provides the most coherent progression from concrete to abstract.

**Start here:**

1. **[myrmecology.md](./myrmecology.md)** -- The hub document. Introduces the etymological roots of codomyrmex, surveys the science of ants, and provides a navigational overview of the entire series. Every other document is linked and summarized here.

**Foundation trio** (read in order):

2. **[stigmergy.md](./stigmergy.md)** -- The most fundamental coordination mechanism: indirect communication through environmental modification. This concept underpins event systems, caching, and logging throughout the platform.
3. **[eusociality.md](./eusociality.md)** -- How labor divides into specialized roles. Maps directly to the agent framework, orchestrator, and plugin architecture.
4. **[superorganism.md](./superorganism.md)** -- How a distributed system of semi-autonomous components can exhibit organism-level coherence. Connects system discovery, telemetry, and the Model Context Protocol.

**Remaining documents** (any order):

5. **[swarm_intelligence.md](./swarm_intelligence.md)** -- Collective decision-making without centralized control.
6. **[immune_system.md](./immune_system.md)** -- Defense, threat detection, and adaptive security.
7. **[memory_and_forgetting.md](./memory_and_forgetting.md)** -- How information persists, decays, and is selectively retrieved.
8. **[evolution.md](./evolution.md)** -- Selection pressure, fitness landscapes, and iterative improvement.
9. **[free_energy.md](./free_energy.md)** -- Active inference and the minimization of prediction error.
10. **[metabolism.md](./metabolism.md)** -- Resource acquisition, allocation, and expenditure.
11. **[symbiosis.md](./symbiosis.md)** -- Mutualistic partnerships and the holobiont concept.

## Related Resources

- [Project README](../../README.md) -- Platform overview, module architecture, and quick start
- [PAI Integration](../../PAI.md) -- AI agent integration and the PAI Algorithm mapping
