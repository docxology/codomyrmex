# Swarm Intelligence and Collective Decision-Making

Swarm intelligence describes the collective behavior of decentralized, self-organized systems composed of simple agents following local rules that produce globally coherent and often near-optimal behavior. This document examines the biological foundations of swarm intelligence and maps its principles to codomyrmex architecture.

## The Biology

The term "swarm intelligence" was introduced by Beni and Wang (1993) in cellular robotics, but the phenomena have deep roots in entomology. The core insight is that insect colonies solve complex computational problems -- shortest-path routing, optimal site selection, efficient allocation -- without any individual possessing a global representation of the problem.

Ant Colony Optimization (ACO), formalized by Dorigo (1992), abstracts foraging behavior into a metaheuristic. Ants deposit pheromone on paths to food sources; shorter paths accumulate pheromone faster, creating positive feedback. Pheromone evaporation provides negative feedback, preventing lock-in on suboptimal solutions. This combination produces robust convergence toward near-optimal solutions across graph problems (Dorigo & Stutzle, 2004).

Quorum sensing represents a different mechanism. Pratt et al. (2002) showed that *Temnothorax albipennis* ants use quorum thresholds during nest emigration: scouts independently assess candidate sites, and when a scout encounters sufficient other scouts at a site, she switches from slow tandem-running recruitment to fast carrying. This produces accurate collective decisions from individually noisy assessments -- a biological "wisdom of crowds" (Surowiecki, 2004).

The honeybee waggle dance (von Frisch, 1967) demonstrates distributed information sharing: returning foragers encode direction and distance to food sources through dance, and observing bees integrate information from multiple dancers, producing a colony-level probability distribution over foraging sites. The critical feature across all these mechanisms is that simple local rules produce globally adaptive behavior without any agent representing the global state.

## Architectural Mapping

- **[`meme`](../../src/codomyrmex/meme/)** -- The swarm submodule implements digital flocking and memetic evolution. Flocking (Reynolds, 1987) shows how three local rules -- separation, alignment, cohesion -- produce coordinated motion. Memetic swarm algorithms apply analogous update rules to candidate solutions, evolving shared structures through imitation and recombination.

- **[`concurrency`](../../src/codomyrmex/concurrency/)** -- Concurrent resource access parallels foraging competition. When multiple foragers exploit the same source, depletion creates implicit competition requiring distributed arbitration. The concurrency module manages locks, semaphores, and scheduling -- the computational equivalents of forager interference and trail congestion.

- **[`evolutionary_ai`](../../src/codomyrmex/evolutionary_ai/)** -- Population-based optimization shares swarm intelligence's core structure: many agents interact through a shared fitness landscape, and optima emerge from local selection without centralized direction.

- **[`market`](../../src/codomyrmex/market/)** -- Auction mechanisms implement competitive foraging computationally. Biological foragers compete for sources with varying profitability, influenced by crowding and pheromone cues. The market module provides analogous bidding, with allocation emerging from distributed competition.

- **[`graph_rag`](../../src/codomyrmex/graph_rag/)** -- Graph-based retrieval distributes knowledge across a structure, with paths determined by query relevance. This mirrors how scouts distribute spatial knowledge through dance: no single bee holds a complete map, but the colony maintains a distributed representation any forager can query.

## Design Implications

**Choose swarm approaches for decomposable, dynamic problems.** Swarm algorithms excel when the solution space is large, the environment changes (invalidating cached solutions), and agents have limited sensing. Hierarchical approaches suit problems with strict global constraints or strong sequential dependencies.

**Calibrate quorum thresholds.** Pratt et al. (2002) showed that quorum thresholds control a speed-accuracy tradeoff. In codomyrmex, consensus mechanisms should expose the threshold as a tunable parameter, letting operators adjust based on error cost versus delay cost.

**Guard against premature convergence.** ACO's evaporation prevents lock-in, but artificial systems often converge too quickly. Design diversity-maintenance mechanisms -- analogous to scouts that continue exploring after quorum -- to avoid locally optimal but globally suboptimal commitment.

## Further Reading

- Dorigo, M. (1992). *Optimization, Learning and Natural Algorithms*. PhD thesis, Politecnico di Milano.
- Bonabeau, E., Dorigo, M. & Theraulaz, G. (1999). *Swarm Intelligence: From Natural to Artificial Systems*. Oxford University Press.
- Pratt, S.C., Mallon, E.B., Sumpter, D.J.T. & Franks, N.R. (2002). Quorum sensing, recruitment, and collective decision-making during colony emigration by the ant *Temnothorax albipennis*. *Behavioral Ecology and Sociobiology*, 52(2), 117--127.

## See Also

- [Myrmecology and Software Architecture](./myrmecology.md)
- [Stigmergy and Indirect Coordination](./stigmergy.md)
- [Eusociality and the Division of Labor](./eusociality.md)
- [Evolutionary Computation](./evolution.md)
- [Project README](../../README.md)
