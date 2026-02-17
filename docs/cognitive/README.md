# Cognitive Perspectives on Codomyrmex

**Series**: Cognitive Science & Engineering | **Status**: Active | **Last Updated**: February 2026

## Theoretical Position

Codomyrmex is a cognitive architecture -- not merely a software platform that borrows biological metaphors, but a system that implements the structural requirements cognitive scientists have identified for unified problem-solving systems. Newell (1990) argued that a cognitive architecture must integrate perception, memory, reasoning, action selection, and learning within a single framework. Codomyrmex satisfies these criteria: `telemetry` provides perception, `agentic_memory` and `cerebrum` provide multi-tier memory and reasoning, `orchestrator` and `skills` handle action selection, and `evolutionary_ai` closes the learning loop. The seven documents in this series trace these implementations against the formal theoretical literature.

Where the [Biological Perspectives](../bio/README.md) series maps ant biology to codomyrmex modules by analogy -- "the EventBus is *like* a pheromone trail" -- this series maps formal theoretical frameworks to module implementations by identity: `shannon_entropy()` in `crypto/analysis/entropy.py` *is* Shannon's H, not an analogy for it. The `ActiveInferenceAgent` in `cerebrum/inference/active_inference.py` *implements* Friston's variational free energy, not a metaphor for it. Both perspectives illuminate the same platform; the biological metaphor makes the theory intuitive, the formal framework makes the metaphor precise.

## Document Index

| Document | Theoretical Domain | Primary Modules | Key Formalism |
|----------|-------------------|-----------------|---------------|
| [signal_information_theory.md](./signal_information_theory.md) | Information Theory | crypto/analysis, telemetry, MCP | Shannon entropy, channel capacity |
| [stigmergy.md](./stigmergy.md) | Multi-Agent Coordination | orchestrator, events, bio_simulation | Algorithmic stigmergy, GFlowNets |
| [cognitive_modeling.md](./cognitive_modeling.md) | Cognitive Architecture | cerebrum/core, agentic_memory, graph_rag | CBR, Bayesian networks, working memory |
| [active_inference.md](./active_inference.md) | Computational Neuroscience | cerebrum/inference, skills, fpf | Free energy principle, EFE, policy selection |
| [cognitive_security.md](./cognitive_security.md) | Security Epistemics | security/cognitive, meme/epistemic | Cognitive threat modeling, social engineering |
| [ergonomics.md](./ergonomics.md) | Human Factors | terminal_interface, cli, documentation | Cognitive load, Fitts's Law, mental models |
| [industrialization.md](./industrialization.md) | Process Engineering | ci_cd_automation, orchestrator, containerization | Quality gates, SRE, assembly line |

## Suggested Reading Order

The documents are designed to be read independently, but the following sequence provides the most coherent progression from foundational to applied.

**Foundation:**

1. **[signal_information_theory.md](./signal_information_theory.md)** -- Information theory is the universal language. Entropy, channel capacity, and coding theory appear in every subsequent document. Start here.
2. **[stigmergy.md](./stigmergy.md)** -- How independent agents coordinate through shared environmental state, grounded in the information-theoretic substrate established above.

**Core architecture:**

3. **[cognitive_modeling.md](./cognitive_modeling.md)** -- What a mind looks like when implemented as software: case-based reasoning, working memory, Bayesian inference.
4. **[active_inference.md](./active_inference.md)** -- How the system selects actions by minimizing expected free energy. Requires cognitive modeling as background.

**Applied perspectives:**

5. **[cognitive_security.md](./cognitive_security.md)** -- How adversaries exploit cognitive architectures. Requires knowing the architecture to understand how it fails.
6. **[ergonomics.md](./ergonomics.md)** -- The human-machine cognitive coupling. Where theory meets real interface design.
7. **[industrialization.md](./industrialization.md)** -- Taking cognitive systems to production scale. The capstone: all prior theory applied to engineering at scale.

## Relationship to Biological Perspectives

The [Biological Perspectives](../bio/README.md) series and this Cognitive Perspectives series analyze the same platform from complementary angles. The biological series uses ant colonies, immune systems, and metabolic networks as analogical models -- grounding software architecture in well-characterized natural systems. This series uses formal theoretical frameworks from information theory, cognitive science, and engineering as the primary language -- grounding the same architecture in mathematical formalisms with testable predictions.

Points of explicit overlap are cross-referenced within each document. Stigmergy appears in both suites: `bio/stigmergy.md` explains the ant pheromone trail; `cognitive/stigmergy.md` addresses convergence guarantees and algorithmic complexity. Active inference likewise spans both: `bio/free_energy.md` surveys the free energy principle as brain theory; `cognitive/active_inference.md` traces the `ActiveInferenceAgent` implementation class by class. Neither series presupposes the other; both reward cross-reading.

## Related Resources

- [Biological Perspectives](../bio/README.md) -- Biological and myrmecological lenses on codomyrmex
- [Project README](../../README.md) -- Platform overview and module architecture
- [PAI Integration](../../PAI.md) -- AI agent integration and the PAI Algorithm mapping
- [PAI Documentation](../pai/README.md) -- Architecture, tools, API, and workflows

---

*Return to [docs index](../README.md) | [Bio perspectives](../bio/README.md) | [Project README](../../README.md)*
