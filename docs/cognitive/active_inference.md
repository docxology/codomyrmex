# Active Inference: The Free Energy Principle in Executable Code

**Series**: [Cognitive Perspectives](./README.md) | **Topic**: Computational Neuroscience

## The Theory

Karl Friston's free energy principle (2006, 2010) proposes that biological systems maintain their integrity by minimizing variational free energy -- an information-theoretic quantity that upper-bounds surprise. The variational free energy of a system is:

    F = -log P(o|s) + KL[q(s) || p(s)]

where P(o|s) is the likelihood of observations given hidden states, q(s) is the agent's approximate posterior (beliefs about states), and p(s) is the prior. The first term is *accuracy* (how well beliefs predict observations); the second is *complexity* (how far beliefs diverge from priors). Perception minimizes F by updating q(s) -- making beliefs more accurate. Action minimizes F by changing observations o -- making the world conform to predictions.

Expected free energy (EFE) extends this to planning. For a policy pi, EFE decomposes as:

    G(pi) = expected_complexity + expected_ambiguity

Expected complexity is the anticipated divergence between future beliefs and priors. Expected ambiguity is the anticipated uncertainty about observations given future states. Policies are selected via softmax over negative EFE: lower expected free energy means higher probability of selection. Critically, the ambiguity term operationalizes *epistemic value* -- the system preferentially selects policies that will reduce future uncertainty. This is information-seeking behavior, not mere reward maximization.

The Markov blanket (Pearl, 1988) formalizes the boundary between agent and environment. States internal to the blanket are conditionally independent of external states given blanket states. In biological systems the blanket is the cell membrane; in software, it is the module's public API. Every function signature, type constraint, and schema validation is a blanket state mediating interaction between internal implementation and external consumers.

## Architectural Mapping

| FEP Construct | Module | Source Path | Direct Correspondence |
|--------------|--------|-------------|----------------------|
| Belief state | cerebrum/inference | [`active_inference.py:BeliefState`](../../src/codomyrmex/cerebrum/inference/active_inference.py) | `states: dict[str, float]` with `normalize()` and `entropy()` |
| Variational free energy | cerebrum/inference | [`active_inference.py:VariationalFreeEnergy.compute()`](../../src/codomyrmex/cerebrum/inference/active_inference.py) | F = accuracy + complexity/precision |
| Expected free energy | cerebrum/inference | [`active_inference.py:VariationalFreeEnergy.compute_expected_free_energy()`](../../src/codomyrmex/cerebrum/inference/active_inference.py) | EFE = expected_complexity + expected_ambiguity |
| Policy selection | cerebrum/inference | [`active_inference.py:PolicySelector.select_policy()`](../../src/codomyrmex/cerebrum/inference/active_inference.py) | Softmax over -EFE with temperature parameter |
| Active inference agent | cerebrum/inference | [`active_inference.py:ActiveInferenceAgent`](../../src/codomyrmex/cerebrum/inference/active_inference.py) | Full perception-action loop: `predict()`, `select_action()`, `update_beliefs()` |
| Generative model | cerebrum/inference | [`bayesian.py:BayesianNetwork`](../../src/codomyrmex/cerebrum/inference/) | Transition model P(s'|s,a) and observation model P(o|s) |
| Markov blanket | model_context_protocol | [`server.py`](../../src/codomyrmex/model_context_protocol/) | MCP tool schemas as formal blanket; internal state conditionally independent given API |
| Amortized inference | skills/discovery | [`skill_registry.py`](../../src/codomyrmex/skills/) | Fast skill lookup as learned recognition model bypassing iterative search |

**`BeliefState`** is a dataclass holding a probability distribution over states as `dict[str, float]`. Its `entropy()` method computes Shannon entropy: H = -sum(p * ln(p)) -- the uncertainty of the agent's beliefs. Higher entropy means the agent is less certain about which state obtains. This is the quantity that perception works to reduce.

**`VariationalFreeEnergy.compute()`** implements F directly. The accuracy term iterates over belief states, computing -prob * log(obs_prob) for each state-observation pair. The complexity term is `beliefs.entropy() / self.precision`, where precision is a temperature-like parameter controlling the accuracy-complexity tradeoff. High precision weights accuracy heavily (confident, potentially brittle inference); low precision tolerates more complexity (uncertain, robust inference).

**`compute_expected_free_energy()`** evaluates EFE for a candidate policy. Expected complexity is the entropy of the predicted next-state distribution under the transition model. Expected ambiguity is the expected entropy of observations given predicted next states under the observation model. The sum gives the total EFE for that policy.

**`PolicySelector.select_policy()`** converts EFE values to utilities (negate, since lower EFE is better), applies softmax with a temperature parameter, and samples. The temperature is 1/precision, connecting the agent's precision parameter to its exploration-exploitation tradeoff. High precision (low temperature) means greedy exploitation of the best-known policy; low precision (high temperature) means exploratory sampling across policies.

**`ActiveInferenceAgent`** composes all components into a complete agent. The perception-action loop is: observe → `update_beliefs()` (Bayesian update using observation model) → `select_action()` (EFE-based policy selection) → act → repeat. The `predict()` method implements Bayesian state estimation: prior * likelihood, normalized. The `reset()` method returns beliefs to uniform priors -- maximum entropy, maximum uncertainty.

## Design Implications

**The F decomposition is an engineering handle.** Accuracy and complexity can be tuned independently via the precision parameter. A system that prioritizes accuracy over complexity will make confident predictions but break when the generative model is wrong. A system that tolerates complexity will be robust but slow to converge. The precision parameter is where this tradeoff is controlled.

**EFE's ambiguity term produces information-seeking behavior.** Policies that reduce future uncertainty are preferred even when they offer no immediate reward. This is why active inference agents explore: they are not random, they are epistemic -- they seek observations that will sharpen their beliefs. This property is valuable for diagnostic workflows where the system should actively probe for information rather than passively waiting.

**Markov blanket integrity is modularity.** A module whose internal state leaks through non-API paths (global variables, shared mutable state, file-system side effects) violates its Markov blanket. The formal consequence: external systems can no longer be conditionally independent of internal state, and inference about the module's behavior becomes intractable. Design for blanket integrity is design for modularity.

**Skill discovery is amortized inference.** The `SkillRegistry.search_by_pattern()` in `skills/discovery/` functions as a learned recognition model: instead of iteratively evaluating which skill best fits a task (expensive posterior inference), the registry maps patterns directly to skills (amortized recognition). This is the computational shortcut that perception learns in predictive processing frameworks.

## Further Reading

- Friston, K. (2006). A free energy principle for the brain. *Journal of Physiology--Paris*, 100(1--3), 70--87.
- Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11, 127--138.
- Parr, T., Pezzulo, G. & Friston, K. (2022). *Active Inference: The Free Energy Principle in Mind, Brain, and Behavior*. MIT Press.
- Pearl, J. (1988). *Probabilistic Reasoning in Intelligent Systems: Networks of Plausible Inference*. Morgan Kaufmann.
- Friston, K. et al. (2017). Active inference and epistemic value. *Cognitive Neuroscience*, 8(4), 218--228.

## See Also

- [Cognitive Modeling](./cognitive_modeling.md) -- The architectural substrate on which active inference operates
- [Signal and Information Theory](./signal_information_theory.md) -- Free energy is an information-theoretic quantity
- [The Free Energy Principle](../bio/free_energy.md) -- The biological perspective on FEP as brain theory
- [Memory and Forgetting](../bio/memory_and_forgetting.md) -- Belief updating as memory formation and revision

*Docxology references*: [active-inference-sim-lab](https://github.com/docxology/active-inference-sim-lab) (FEP toolkit with C++ core), [FEP_RL_VAE](https://github.com/docxology/FEP_RL_VAE) (variational autoencoder integrating FEP with RL), [RxInferExamples.jl](https://github.com/docxology/RxInferExamples.jl) (reactive message passing for probabilistic inference), [enactive_inference_model](https://github.com/docxology/enactive_inference_model) (hierarchical enactive inference model of mental action), [Active_Inference_for_Fun](https://github.com/docxology/Active_Inference_for_Fun) (educational sandbox with PyMDP)

---

*Return to [series index](./README.md) | [Bio perspectives](../bio/README.md) | [Project README](../../README.md)*
