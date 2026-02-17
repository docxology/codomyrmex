# Cognitive Architecture: Case-Based Reasoning, Working Memory, and the Cerebrum

**Series**: [Cognitive Perspectives](./README.md) | **Topic**: Cognitive Architecture Theory

## The Theory

Allen Newell (1990) argued that a complete theory of cognition must unify perception, memory, reasoning, and action within a single architectural framework -- a *unified theory of cognition*. The resulting cognitive architectures (ACT-R, Soar, LIDA) are not models of specific cognitive phenomena but specifications of the machinery that produces cognition. They define what kinds of memory exist, how knowledge is retrieved, and how action is selected.

ACT-R (Anderson, 2007) distinguishes declarative memory (facts, retrievable by spreading activation) from procedural memory (production rules, condition-action pairs). Retrieval is competitive: chunks with higher activation -- a function of recency, frequency, and contextual relevance -- are retrieved faster and more reliably. Working memory is a bounded buffer that holds the currently active chunks; Miller's (1956) observation that short-term memory capacity is roughly 7 plus or minus 2 items remains one of the most robust findings in cognitive science.

Case-Based Reasoning (Aamodt & Plaza, 1994) offers an alternative to rule-based systems: instead of deriving solutions from first principles, retrieve a similar past case and adapt it. The CBR cycle has four steps -- Retrieve, Reuse, Revise, Retain -- forming a learning loop where each solved problem becomes a new case for future retrieval. CBR is most effective when the problem space is large, formal rules are hard to articulate, and examples are abundant -- conditions that describe AI-assisted development precisely.

The Bayesian brain hypothesis (Tenenbaum et al., 2011) reframes cognition as probabilistic inference: the brain maintains probability distributions over hypotheses and updates them via Bayes' theorem as evidence arrives. Perception is inference (what caused this sensory input?), learning is prior update (how should I weight hypotheses?), and action is expected utility maximization (which action minimizes expected loss?). This framework connects to active inference, treated in detail in [active_inference.md](./active_inference.md).

## Architectural Mapping

| Cognitive Architecture Component | Module | Source Path | Implementation |
|---------------------------------|--------|-------------|----------------|
| Declarative memory (semantic) | agentic_memory | [`memory.py`](../../src/codomyrmex/agentic_memory/) | Persistent stores; retrieval by similarity and activation |
| Working memory buffer | cerebrum/core | [`core/`](../../src/codomyrmex/cerebrum/core/) | Bounded short-term state for active reasoning context |
| Case-Based Reasoning | cerebrum/core | [`core/`](../../src/codomyrmex/cerebrum/core/) | CaseBase, CaseRetriever with similarity metrics; 4R cycle |
| Bayesian inference | cerebrum/inference | [`inference/bayesian.py`](../../src/codomyrmex/cerebrum/inference/) | BayesianNetwork with conditional probability tables, belief propagation |
| Production rules | orchestrator | [`workflow.py`](../../src/codomyrmex/orchestrator/) | Condition-action triggers in workflow DAG; step/pipe/condition primitives |
| Episodic memory (graph-structured) | graph_rag | [`graph_rag/`](../../src/codomyrmex/graph_rag/) | Graph-based retrieval augmented generation for episode retrieval |
| Memory consolidation | agentic_memory | [`compression.py`](../../src/codomyrmex/agentic_memory/) | Lossy compression of memory traces; gist extraction |
| Spreading activation | vector_store | [`vector_store/`](../../src/codomyrmex/vector_store/) | Embedding-based similarity search as continuous activation |

**The cerebrum module** is the cognitive engine. Its `core/` subdirectory implements case-based reasoning with `CaseBase` (the case library), `CaseRetriever` (similarity-driven retrieval using Euclidean and cosine metrics), and `SimilarityMetrics` (the distance functions that determine what counts as "similar"). The four-step CBR cycle is realized as: Retrieve (query CaseBase by similarity), Reuse (apply retrieved solution to current problem), Revise (modify solution based on outcome), Retain (add the new case to CaseBase for future use). This loop is exactly Aamodt and Plaza's formalization.

**The `BayesianNetwork`** in `cerebrum/inference/bayesian.py` implements belief propagation over conditional probability tables. Priors are an engineering decision: flat priors maximize entropy and produce conservative behavior (maximum uncertainty); informative priors encode domain expertise and produce faster but less robust inference. The choice of prior is the cognitive architecture's expression of how much the system "knows" before seeing data.

**Working memory** is bounded by design. Cognitive architectures set this bound deliberately because unbounded working memory would make cognitive overload impossible -- and cognitive overload is a real failure mode in complex agent chains. The cerebrum module's working memory buffer enforces capacity limits, preventing downstream reasoning from being overwhelmed by upstream context.

**`agentic_memory/compression.py`** implements memory consolidation -- the process by which detailed episodic traces are compressed into gist representations. This parallels hippocampal consolidation in neuroscience: detailed but fragile recent memories are gradually compressed into robust but lossy long-term representations. The compression is not information-theoretically lossless; it is designed to preserve the aspects of experience most useful for future retrieval while discarding details.

## Design Implications

**Use CBR when formal rules are expensive to articulate.** AI-assisted development generates abundant cases (solved problems, successful patterns, debugging sessions) but resists formalization as exhaustive rule sets. The cerebrum module's CaseBase should be the primary mechanism for capturing institutional knowledge -- not as documentation but as structured (problem, solution) pairs available for similarity retrieval.

**Enforce working memory capacity limits.** Removing capacity limits does not make the system smarter; it makes cognitive overload impossible to detect. Explicit bounds on working memory force the architecture to prioritize -- which is what cognitive architectures do.

**Engineer priors deliberately.** A BayesianNetwork with uniform priors treats all hypotheses as equally likely and requires maximum evidence to converge. A network with informative priors converges faster but is brittle to prior misspecification. The choice is not neutral; it encodes assumptions about the problem domain.

**Design for the CBR Retain step.** Most CBR implementations focus on Retrieve and Reuse but underinvest in Retain. A CaseBase that does not grow from solved problems cannot improve over time. The Retain step is the learning mechanism of the cognitive architecture.

## Further Reading

- Newell, A. (1990). *Unified Theories of Cognition*. Harvard University Press.
- Anderson, J.R. (2007). *How Can the Human Mind Occur in the Physical Universe?* Oxford University Press.
- Aamodt, A. & Plaza, E. (1994). Case-based reasoning: foundational issues, methodological variations, and system approaches. *AI Communications*, 7(1), 39--59.
- Tenenbaum, J.B., Kemp, C., Griffiths, T.L. & Goodman, N.D. (2011). How to grow a mind: statistics, structure, and abstraction. *Science*, 331(6022), 1279--1285.
- Miller, G.A. (1956). The magical number seven, plus or minus two: some limits on our capacity for processing information. *Psychological Review*, 63(2), 81--97.

## See Also

- [Active Inference](./active_inference.md) -- Action selection within the cognitive architecture via free energy minimization
- [Signal and Information Theory](./signal_information_theory.md) -- Entropy as the formal language of belief uncertainty
- [Stigmergy](./stigmergy.md) -- Case retrieval as a form of marker-following in the problem space
- [Memory and Forgetting](../bio/memory_and_forgetting.md) -- The biological perspective on memory architecture
- [Free Energy Principle](../bio/free_energy.md) -- The biological framing of Bayesian brain theory

*Docxology references*: [enactive_inference_model](https://github.com/docxology/enactive_inference_model) (hierarchical cognitive model with Thoughtseeds framework), [InsightSpike-AI](https://github.com/docxology/InsightSpike-AI) (computational model of cognitive insight via structural isomorphism), [cogames](https://github.com/docxology/cogames) (multi-agent cooperative cognition)

---

*Return to [series index](./README.md) | [Bio perspectives](../bio/README.md) | [Project README](../../README.md)*
