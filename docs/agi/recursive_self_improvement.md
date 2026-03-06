# Recursive Self-Improvement: Gödel Machines, Fitness Landscapes, and Corrigible Growth

**Series**: AGI Perspectives | **Document**: 4 of 10 | **Last Updated**: March 2026

## The Intelligence Explosion

Good's (1965) formulation remains the clearest: an ultraintelligent machine could design a better machine, which could design a still better one — an "intelligence explosion." Schmidhuber (2003) formalized this as the Gödel Machine: a self-referential universal problem solver that rewrites its own code whenever it can prove the rewrite improves expected reward. Bostrom (2014) extended the analysis to existential risk. Solomonoff (1964) provided the information-theoretic foundation: optimal inductive inference via the universal prior implies self-improvement as a natural consequence of compressing observed data.

Codomyrmex implements *bounded* recursive self-improvement. This essay traces the loop through five stages, characterizes the fitness landscape over which improvement operates, and analyzes the safety constraints that prevent unbounded growth.

## The Self-Improvement Loop

```mermaid
graph TB
    subgraph OBSERVE["1. Observe (Perception)"]
        TELEM["telemetry/<br/><i>performance metrics: L(θ)</i>"]
        SA["static_analysis/<br/><i>code quality: Q(c)</i>"]
        TEST["tests/<br/><i>pass rate: P(t)/|T|</i>"]
    end

    subgraph SEARCH["2. Search (Hypothesis Generation)"]
        CEREB["cerebrum/<br/><i>CBR · Bayesian inference</i>"]
        EVOL["evolutionary_ai/<br/><i>population search on F(c)</i>"]
        LLM["llm/<br/><i>conditioned generation P(c'|c,θ)</i>"]
    end

    subgraph MODIFY["3. Modify (Intervention)"]
        CODING["coding/<br/><i>diff generation: Δc</i>"]
        AGENTS_CODE["agents/ai_code_editing<br/><i>structured patching</i>"]
    end

    subgraph VERIFY["4. Verify (Evaluation)"]
        CICD["ci_cd_automation/<br/><i>F(c+Δc) > F(c)?</i>"]
        FORMAL["formal_verification/<br/><i>φ(c+Δc) ⊨ safety</i>"]
        VALID["validation/<br/><i>schema contracts</i>"]
    end

    subgraph DEPLOY["5. Deploy (Selection)"]
        TRUST["trust_gateway<br/><i>human oracle gate</i>"]
        GIT["git_operations/<br/><i>immutable version control</i>"]
    end

    OBSERVE -->|"loss gradient"| SEARCH
    SEARCH -->|"candidate c'"| MODIFY
    MODIFY -->|"diff Δc"| VERIFY
    VERIFY -->|"fitness Δ"| DEPLOY
    DEPLOY -.->|"new baseline"| OBSERVE

    style OBSERVE fill:#1a1a2e,stroke:#e94560,color:#e8e8e8
    style SEARCH fill:#533483,stroke:#e94560,color:#e8e8e8
    style MODIFY fill:#0f3460,stroke:#533483,color:#e8e8e8
    style VERIFY fill:#16213e,stroke:#0f3460,color:#e8e8e8
    style DEPLOY fill:#e94560,stroke:#1a1a2e,color:#fff
```

### Formal Characterization

Define the **system state** as a tuple ⟨C, T, M⟩ where C is the codebase, T is the test suite, and M is the self-model (RASP documentation + `system_discovery` output). The **fitness function** over system states:

$$F(C, T, M) = \alpha \cdot \frac{|T_{pass}|}{|T|} + \beta \cdot Q(C) + \gamma \cdot \text{Perf}(C) - \delta \cdot \text{Regressions}(C, C_{prev})$$

where Q(C) is the static quality metric (ruff violations, type coverage), Perf(C) is runtime performance, and the regression term penalizes capabilities lost during modification. The coefficients (α, β, γ, δ) encode human preferences — the *value function* of the improvement process.

A self-modification Δ is accepted iff:

$$F(C + \Delta C, T, M') > F(C, T, M) + \epsilon$$

where ε is a *noise margin* (prevents accepting trivially small improvements that may be measurement noise), and M' is the updated self-model. This is a **steady-state evolutionary algorithm** with elitist selection.

### The Fitness Landscape

Wright's (1932) fitness landscape metaphor provides geometric intuition. The system state C exists in a high-dimensional space where each coordinate represents a design decision. The fitness function F defines a surface over this space. Self-improvement is a walk on this landscape.

Three landscape properties determine the dynamics of improvement:

| Property | Formal Definition | Codomyrmex Instance |
|:---------|:-----------------|:-------------------|
| **Ruggedness** | # local optima / unit volume | High — many design trade-offs create local peaks |
| **Neutrality** | Fraction of mutations with ΔF ≈ 0 | Moderate — many changes are cosmetic (comments, formatting) |
| **Epistasis** | Non-additivity: F(AB) ≠ F(A) + F(B) - F(∅) | Strong — module interactions create non-linear effects |

Strong epistasis implies that combinatorial improvements (modifying multiple modules simultaneously) can access fitness peaks unreachable by single-module changes. The Jules AI swarm's parallel modification strategy (113+ concurrent sessions) is precisely a *multi-point mutation* strategy that explores the landscape's epistatic structure.

### Developmental Constraints

Kauffman's (1993) NK model predicts that ruggedness increases with epistasis (K), making search harder but potentially placing higher peaks available. Codomyrmex's modular architecture implements what developmental biologists call **developmental constraints** (Maynard Smith et al., 1985): the module boundaries channel modification along specific directions, just as compartmentalized body plans channel evolutionary change.

These constraints are *beneficial*: they reduce the effective dimensionality of the search space. A modification confined to one module (dimension ≤ dim(module)) is far easier to evaluate than a cross-cutting change (dimension ~ dim(codebase)). The 128-module partition creates 127 *quasi-independent* optimization cells.

## The Gödel Machine Connection

Schmidhuber's (2003) Gödel Machine searches for *provably optimal* self-modifications. The search space is the set of all programs expressible in itself (self-referential). When it finds a modification whose improvement can be *formally proved*, it applies the modification.

Codomyrmex approximates this with a weaker verification criterion: modifications must pass *tests and validation*, not *formal proofs*. The 21,000+ tests serve as *empirical evidence* rather than *deductive proof*. The gap between empirical evidence and formal proof is precisely the gap between Σ₁⁰ (testing) and Π₁⁰ (universal correctness) in the arithmetical hierarchy — see [formal_specification.md](./formal_specification.md).

The `evolutionary_ai` module adds a critical capability: **population-based search**. Rather than the Gödel Machine's exhaustive proof search, `evolutionary_ai` maintains a *population* of candidate modifications and applies selection pressure:

$$p(c' \text{ survives}) = \frac{e^{F(c') / T}}{\sum_{c'' \in \text{population}} e^{F(c'') / T}}$$

where T is the selection temperature (high T → exploration; low T → exploitation). This is the **Boltzmann selection** strategy from simulated annealing, adapted to codebase evolution.

## The Halting Problem for Self-Improvement

A subtle issue: self-improvement must *converge*. An improvement loop that never terminates is itself a kind of failure. The convergence condition:

$$\sum_{t=0}^{\infty} [F(C_{t+1}) - F(C_t)] < \infty$$

This sum converging implies that improvements become vanishingly small — the system approaches a fitness peak. The danger is **fitness landscape shifting**: as the system modifies itself, the landscape itself changes (because the evaluation criteria are partly internal). This creates a *Red Queen* dynamic (van Valen, 1973): the system must keep improving just to maintain its relative fitness.

Codomyrmex bounds this through **ratcheting**: the coverage gate (`fail_under=31`) prevents fitness degradation. Each improvement must maintain at least the current fitness — a *monotonic* constraint that guarantees convergence to a local optimum (though not necessarily a global one).

## Five Safety Bounds

| Bound | Mechanism | Formal Property |
|:------|:----------|:---------------|
| **Test constitution** | 21,000+ tests must pass | F(C') ≥ F(C) enforced |
| **Trust governor** | `UNTRUSTED → VERIFIED → TRUSTED` | Rate-limited capability acquisition |
| **Human oracle** | Trust gateway requires human approval | Löbian circuit-breaker (external to proof system) |
| **Formal verification** | Property proofs for critical invariants | Π₁⁰ approximation for selected properties |
| **Containment** | `containerization/` isolates experiments | Resource bounds (CPU, memory, network) |

The combination makes the system *safely autopoietic*: it can maintain and improve itself within constraints, but cannot unilaterally expand those constraints. The constraints themselves are *outside the system's modification scope* — a key architectural decision.

## Lyapunov Stability of the Improvement Loop

A formal stability analysis of the self-improvement loop uses **Lyapunov's direct method**. Define a Lyapunov function:

$$V(C_t) = F^* - F(C_t, T, M_t) \geq 0$$

where F* is the (unknown) global fitness optimum. V(C_t) measures the "distance from optimal" — always non-negative, zero only at the optimum.

For the self-improvement loop to be **Lyapunov stable**, we need:

$$\dot{V}(C_t) = V(C_{t+1}) - V(C_t) = F(C_t) - F(C_{t+1}) \leq 0$$

The ratchet constraint (F(C') ≥ F(C)) ensures exactly this: the fitness can only increase, so V can only decrease. The system converges monotonically to a local optimum.

**Asymptotic stability** requires the stricter condition: V → 0 as t → ∞. This is *not guaranteed* — the system may stall at a local optimum where F < F*. The gap F* - F(C_local) is the **optimality gap** — the price of bounded self-improvement.

The `evolutionary_ai` module's population-based search partially addresses this by maintaining diversity. In Wright's fitness landscape metaphor, a population explores multiple peaks simultaneously, increasing the probability of finding the global optimum.

## Information-Theoretic Speed Limits on Self-Improvement

There are fundamental limits on how fast a system can self-improve, independent of computational resources. Bremermann (1962) derived a limit on the rate of information processing:

$$R_{max} = \frac{mc^2}{h \ln 2} \approx 1.36 \times 10^{50} \text{ bits/s/kg}$$

More practically, the **algorithmic speed limit** for self-improvement is bounded by the mutual information between the system's current state and its potential improvements:

$$\Delta F / \Delta t \leq I(C_t; C^*) \cdot R_{compute}$$

where I(C_t; C*) is the algorithmic mutual information between the current codebase and the optimal one, and R_compute is the computational rate. As the system improves and approaches C*, the mutual information I decreases — improvements become harder to find. This predicts *diminishing returns* on self-improvement, consistent with the empirical observation that the first improvements are largest and subsequent improvements converge.

## Cross-References

- **Biological**: [evolution.md](../bio/evolution.md) — Selection pressure and fitness landscapes
- **Cognitive**: [industrialization.md](../cognitive/industrialization.md) — Quality gates as developmental constraints
- **Previous**: [world_models.md](./world_models.md) — World models enable prediction of modification effects
- **Next**: [alignment_and_safety.md](./alignment_and_safety.md) — Safety constraints on self-improvement

## References

- Bostrom, N. (2014). *Superintelligence*. Oxford University Press.
- Good, I. J. (1965). "Speculations Concerning the First Ultraintelligent Machine." *Advances in Computers*, 6, 31–88.
- Kauffman, S. A. (1993). *The Origins of Order*. Oxford University Press.
- Maynard Smith, J., et al. (1985). "Developmental Constraints and Evolution." *Q. Rev. Biol.*, 60(3), 265–287.
- Schmidhuber, J. (2003). "Gödel Machines." arXiv:cs/0309048.
- Solomonoff, R. J. (1964). "A Formal Theory of Inductive Inference." *Information and Control*, 7(1), 1–22.
- van Valen, L. (1973). "A New Evolutionary Law." *Evolutionary Theory*, 1, 1–30.
- Wright, S. (1932). "The Roles of Mutation, Inbreeding, Crossbreeding and Selection in Evolution." *Proceedings of the 6th International Congress of Genetics*, 1, 356–366.

---

*[← World Models](./world_models.md) | [Next: Alignment & Safety →](./alignment_and_safety.md)*
