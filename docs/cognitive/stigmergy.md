# Algorithmic Stigmergy: Marker-Based Coordination

**Series**: [Cognitive Perspectives](./README.md) | **Topic**: Multi-Agent Coordination Theory

## The Theory

Stigmergy -- coordination through persistent environmental modification -- was formalized by Heylighen (2016) as a universal coordination mechanism appearing in insect societies, human collaboration, and artificial multi-agent systems. The formal definition distinguishes stigmergy from both direct communication (message-passing between identified agents) and blackboard architectures (centralized shared memory with explicit read/write protocols). In stigmergic coordination, an agent modifies the shared environment as a side effect of work; other agents respond to the modified environment without knowing which agent produced the modification. The signal is in the medium, not in a message.

Dorigo and Stutzle (2004) formalized ant colony optimization (ACO) as a metaheuristic: artificial ants deposit pheromone on graph edges proportional to solution quality, and subsequent ants probabilistically follow stronger trails. Evaporation decays all trails at a constant rate, preventing lock-in to early suboptimal solutions. Under appropriate evaporation schedules, ACO provably converges to optimal solutions on shortest-path problems in polynomial time -- a result that transforms biological intuition into algorithmic guarantee.

Bengio et al. (2021) introduced GFlowNets, which learn to sample from complex distributions by flowing probability through directed acyclic graphs. While not stigmergic in the biological sense, GFlowNets share the structural property: the "flow" deposited on edges during training serves as a marker that guides subsequent sampling. The distinction between ACO's explicit pheromone and GFlowNet's learned flow is the distinction between constructive and amortized stigmergy -- one builds markers incrementally during search, the other learns a generative model of where markers should be.

Theraulaz and Bonabeau (1999) distinguished *quantitative* stigmergy (stimulus modulates the intensity of the same behavior) from *qualitative* stigmergy (stimulus triggers a different behavior). Both forms appear in codomyrmex: cache TTL reinforcement is quantitative (more access = longer retention), while event-driven workflow triggers are qualitative (an event of type A triggers behavior B).

## Architectural Mapping

| Stigmergic Construct | Module | Source Path | Implementation |
|---------------------|--------|-------------|----------------|
| Marker deposition | events | [`event_bus.py:EventBus`](../../src/codomyrmex/events/) | Publish to shared medium without addressing any receiver |
| Marker evaporation | cache | [`cache/`](../../src/codomyrmex/cache/) | TTL-based entries expire unless reinforced by access |
| Pheromone simulation | bio_simulation | [`ant_colony/colony.py:Colony`](../../src/codomyrmex/bio_simulation/ant_colony/colony.py) | PheromoneGrid with deposition rates, evaporation constants, diffusion |
| Flow network (DAG) | orchestrator | [`parallel_runner.py`](../../src/codomyrmex/orchestrator/) | Fan-out-fan-in as flow network topology |
| Trail reinforcement | agentic_memory | [`memory.py`](../../src/codomyrmex/agentic_memory/) | Access frequency drives retention priority |
| Colony convergence | agents | [`agents/`](../../src/codomyrmex/agents/) | Multi-agent pool coordination via shared state, not direct messaging |

**The EventBus** is the most direct software implementation of stigmergy. A module publishes an event to a shared medium without addressing or even knowing which subscribers exist. Subscribers detect events according to their own logic. The publisher modifies the shared environment; the subscriber responds to that modification. No point-to-point channel is established. This is Heylighen's definition instantiated as a publish-subscribe pattern.

**Cache eviction** implements pheromone evaporation. A cached value persists for a defined TTL, then expires. Repeated access refreshes the TTL -- quantitative stigmergic reinforcement. LRU and LFU policies map to different biological evaporation and reinforcement schedules. The key insight from ACO convergence theory is that evaporation rates are not arbitrary defaults but hyperparameters with theoretical optima: too fast and useful markers vanish, too slow and outdated markers persist.

**The `Colony` class** in `bio_simulation/ant_colony/` implements literal ant colony simulation with a `PheromoneGrid`, configurable evaporation constants, and ant agents that deposit and follow pheromone trails. This is the reference implementation -- the biological system modeled in code -- against which the abstract stigmergic patterns in `events/`, `cache/`, and `orchestrator/` can be validated.

## Design Implications

**Prefer indirect coordination over direct messaging.** When modules communicate through shared environmental state (events, caches, logs) rather than point-to-point calls, new consumers can be added without modifying producers. The formal advantage: stigmergic systems scale as O(n) in the number of agents, while fully-connected message-passing scales as O(n^2).

**Treat evaporation rates as convergence parameters.** ACO theory provides formal guidance: the evaporation rate rho should satisfy 0 < rho < 1, with smaller values favoring exploitation of known solutions and larger values favoring exploration. TTL values in caching should be set with this tradeoff in mind, not as arbitrary round numbers.

**Distinguish quantitative from qualitative stigmergy in design.** Cache reinforcement (quantitative) and event-triggered workflows (qualitative) serve different coordination purposes. Conflating them -- using the same mechanism for both -- loses the design vocabulary that Theraulaz and Bonabeau identified.

## Further Reading

- Heylighen, F. (2016). Stigmergy as a universal coordination mechanism I: Definition and components. *Cognitive Systems Research*, 38, 4--13.
- Dorigo, M. & Stutzle, T. (2004). *Ant Colony Optimization*. MIT Press.
- Bengio, E., Jain, M., Korablyov, M., Precup, D. & Bengio, Y. (2021). Flow network based generative models for non-iterative diverse candidate generation. *NeurIPS 2021*.
- Theraulaz, G. & Bonabeau, E. (1999). A brief history of stigmergy. *Artificial Life*, 5(2), 97--116.
- Grassé, P.-P. (1959). La reconstruction du nid et les coordinations interindividuelles. *Insectes Sociaux*, 6, 41--80.

## See Also

- [Signal and Information Theory](./signal_information_theory.md) -- Pheromone trails as signal channels with evaporation as noise
- [Cognitive Modeling](./cognitive_modeling.md) -- Case-based reasoning retrieval as a form of marker-following
- [Stigmergy and the Pheromone Trail](../bio/stigmergy.md) -- The biological treatment of the same concept
- [Swarm Intelligence](../bio/swarm_intelligence.md) -- Collective decision-making that depends on stigmergic coordination

*Docxology references*: [gfacs](https://github.com/docxology/gfacs) (GFlowNets with Ant Colony Sampling -- the direct combination of ACO and GFlowNet approaches)

---

*Return to [series index](./README.md) | [Bio perspectives](../bio/README.md) | [Project README](../../README.md)*
