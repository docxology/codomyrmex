# Plan: Cognitive Perspectives Documentation Suite

## Context

Daniel wants a new `docs/cognitive/` directory with 7 documents covering cognitive science and engineering frameworks applied to codomyrmex. The `docs/bio/` suite (11 essays) already covers biological metaphors (stigmergy as ant trails, FEP as brain theory). The cognitive/ suite takes the **complementary formal theory angle** — not "codomyrmex is like an ant colony" but "codomyrmex implements these cognitive architectures."

The directory exists but is empty. The codebase has deep cognitive implementations: `cerebrum/inference/active_inference.py` (full FEP agent), `crypto/analysis/entropy.py` (Shannon entropy), `security/cognitive/` (threat assessment), `meme/` (12 submodules), `bio_simulation/ant_colony/` (colony simulation).

## Unifying Narrative

**Codomyrmex is a cognitive architecture.** The 7 documents prove this in sequence:

1. **Signal & Information Theory** — The formal language (entropy, channels, coding)
2. **Stigmergy** — How agents coordinate without communication
3. **Cognitive Modeling** — What a mind looks like when built from modules
4. **Active Inference** — How that mind selects actions (FEP implementation)
5. **Cognitive Security** — How that mind fails under attack
6. **Ergonomics** — How human minds couple to the system
7. **Industrialization** — How cognitive systems survive production

Arc: **medium → coordination → architecture → agency → threat → interface → scale**

## Files to Create (8 total)

### 1. `docs/cognitive/README.md` — Suite Index

Structure (following `docs/bio/README.md` pattern):
- Series metadata header: `**Series**: Cognitive Science & Engineering | **Status**: Active | **Last Updated**: February 2026`
- **Theoretical Position** (2 paragraphs): Codomyrmex as cognitive architecture. Reference Newell (1990), ACT-R, Global Workspace Theory. The 7 subsystems.
- **Document Index** table: Document | Theoretical Domain | Primary Modules | Key Formalism
- **Suggested Reading Order**: Foundation → Signal/Info Theory, Stigmergy. Core → Cognitive Modeling, Active Inference. Applied → Cognitive Security, Ergonomics, Industrialization.
- **Relationship to Biological Perspectives**: Complementary lenses on same platform. Bio = analogical, Cognitive = formal identity.
- **Related Resources** footer

### 2. `docs/cognitive/signal_information_theory.md`

**Title**: "Signal, Entropy, and the Channel"
- **The Theory**: Shannon (1948) entropy H = -sum p log p. Channel capacity. Source/channel coding. Kolmogorov complexity.
- **Architectural Mapping** table:
  - Shannon entropy → `crypto/analysis/entropy.py:shannon_entropy()`, `byte_entropy()`
  - Channel capacity → `model_context_protocol/` (MCP as bounded channel)
  - Source coding → `telemetry/` (structured spans as efficient encoding)
  - Noise/redundancy → `meme/cybernetic/engine.py:PIDController`
  - Steganography → `crypto/steganography/`
  - Randomness testing → `crypto/analysis/entropy.py:chi_squared_test()`
- **Design Implications**: Measure entropy of data channels; rate-limit by information rate; channel capacity constrains tool signatures
- Cross-ref: `bio/superorganism.md`, `bio/stigmergy.md`
- **Citations**: Shannon 1948, Cover & Thomas 2006, Kolmogorov 1965, MacKay 2003
- **Docxology**: GLOSSOPETRAE, InsightSpike-AI, QuadMath

### 3. `docs/cognitive/stigmergy.md`

**Title**: "Algorithmic Stigmergy: Marker-Based Coordination"
- **The Theory**: Heylighen (2016) formal definition. Distinguish from message-passing. ACO (Dorigo & Stutzle 2004). GFlowNets (Bengio 2021). Convergence properties. Qualitative vs quantitative stigmergy.
- **Architectural Mapping** table:
  - Marker deposition → `events/event_bus.py:EventBus`
  - Evaporation → `cache/` (TTL-based expiry)
  - ACO simulation → `bio_simulation/ant_colony/colony.py:Colony`
  - Flow network → `orchestrator/parallel_runner.py` (fan-out-fan-in)
  - Reinforcement → `agentic_memory/` (access frequency drives retention)
- **Design Implications**: Convergence guarantees, evaporation rate optimization, GFlowNet-style workflow scheduling
- Cross-ref: `bio/stigmergy.md` (biological treatment → this is the formal theory)
- **Citations**: Heylighen 2016, Dorigo & Stutzle 2004, Bengio et al. 2021
- **Docxology**: gfacs (GFlowNets + ACO)

### 4. `docs/cognitive/cognitive_modeling.md`

**Title**: "Cognitive Architecture: Case-Based Reasoning, Working Memory, and the Cerebrum"
- **The Theory**: Newell (1990) unified cognition. ACT-R (Anderson 2007). CBR 4R cycle (Aamodt & Plaza 1994). Bayesian brain (Tenenbaum et al. 2011). Miller's 7±2.
- **Architectural Mapping** table:
  - Declarative memory → `agentic_memory/memory.py`
  - Working memory → `cerebrum/core/` (bounded short-term state)
  - CBR → `cerebrum/core/` (CaseBase, CaseRetriever)
  - Bayesian inference → `cerebrum/inference/bayesian.py:BayesianNetwork`
  - Episodic memory → `graph_rag/`
  - Production rules → `orchestrator/workflow.py` (condition-action triggers)
- **Design Implications**: CBR for institutional knowledge, explicit WM capacity limits, Bayesian prior engineering
- Cross-ref: `bio/memory_and_forgetting.md`
- **Citations**: Newell 1990, Anderson 2007, Aamodt & Plaza 1994, Miller 1956
- **Docxology**: enactive_inference_model, InsightSpike-AI

### 5. `docs/cognitive/active_inference.md`

**Title**: "Active Inference: The Free Energy Principle in Executable Code"
- **The Theory**: Friston (2006, 2010) variational free energy F = -log P(o|s) + KL[q(s)||p(s)]. Expected free energy (EFE). Policy selection via softmax over -G. Markov blanket (Pearl 1988). Perception-action loop.
- **Architectural Mapping** table (direct code correspondence):
  - Variational free energy → `cerebrum/inference/active_inference.py:VariationalFreeEnergy.compute()`
  - EFE → `VariationalFreeEnergy.compute_expected_free_energy()`
  - Policy selection → `PolicySelector.select_policy()` (softmax with temperature)
  - Belief state → `BeliefState` (dict of state→prob; `entropy()` method)
  - Active inference agent → `ActiveInferenceAgent` (full perception-action loop: `predict()`, `select_action()`, `update_beliefs()`)
  - Markov blanket → MCP tool schemas (module API surface = formal blanket)
  - Amortized inference → `skills/discovery/` (fast lookup as learned recognition model)
- **Design Implications**: F decomposition as engineering handle, EFE's epistemic value = info-seeking, blanket integrity = modularity
- Cross-ref: `bio/free_energy.md` (biology → this traces the implementation)
- **Citations**: Friston 2006, 2010; Parr, Pezzulo & Friston 2022; Pearl 1988
- **Docxology**: active-inference-sim-lab, FEP_RL_VAE, RxInferExamples.jl, enactive_inference_model, Active_Inference_for_Fun

### 6. `docs/cognitive/cognitive_security.md`

**Title**: "Cognitive Security: Epistemic Defense and Information Warfare"
- **The Theory**: Cognitive security = protecting epistemic processes against adversarial manipulation. Kill chain adapted to cognitive attacks (Hutchins 2011). Meme theory (Dawkins 1976, Blackmore 1999) as contagion model. Social engineering as belief-state exploitation. Cialdini's influence principles.
- **Architectural Mapping** table:
  - Threat assessment → `security/cognitive/cognitive_threat_assessment.py:CognitiveThreatAssessor`
  - `CognitiveThreat` dataclass: `threat_id`, `threat_type`, `severity`, `human_factors`, `mitigation`
  - Social engineering → `security/cognitive/social_engineering_detector.py`
  - Phishing → `security/cognitive/phishing_analyzer.py`
  - Epistemic verification → `meme/epistemic/` (truth verification)
  - Contagion modeling → `meme/contagion/` (SIR epidemic models)
  - Framing detection → `meme/neurolinguistic/framing.py`
  - Trust gateway → `agents/pai/trust_gateway.py` (epistemic consent architecture)
- **Design Implications**: human_factors as explicit attack surface modeling, fabrication penalty as formal epistemic prior, trust gateway as cognitive security architecture
- Cross-ref: `bio/immune_system.md`
- **Citations**: Hutchins 2011, Dawkins 1976, Blackmore 1999, Cialdini 2006, Mercier & Sperber 2017
- **Docxology**: p3if, Personal_AI_Infrastructure, GLOSSOPETRAE

### 7. `docs/cognitive/ergonomics.md`

**Title**: "Cognitive Ergonomics: Human Factors and the Operator Interface"
- **The Theory**: GOMS model (Card, Moran & Newell 1983). Fitts's Law. Cognitive load theory (Sweller 1988): intrinsic/extraneous/germane. Mental models (Norman 1988). CLI-first as cognitive ergonomics (Unix philosophy, McIlroy 1978).
- **Architectural Mapping** table:
  - Fitts's Law → `cli/core.py` (command depth minimized)
  - GOMS → CLI noun/verb hierarchy
  - Rich output → `terminal_interface/` (structured, colored output reduces parsing load)
  - Mental model support → `system_discovery/` (`codomyrmex modules` makes system legible)
  - Cognitive load reduction → `documentation/education/curriculum.py` (progressive disclosure)
  - Composability → `cli/` + `orchestrator/` (JSON/YAML shell-composable output)
- **Design Implications**: Command depth predicts Fitts's Law performance, Rich reduces extraneous load, curriculum.py is formal cognitive load management
- Cross-ref: `bio/eusociality.md` (weak parallel — note explicitly)
- **Citations**: Card, Moran & Newell 1983; Fitts 1954; Sweller 1988; Norman 1988
- **Docxology**: Personal_AI_Infrastructure

### 8. `docs/cognitive/industrialization.md`

**Title**: "Industrialization: Process Engineering for Cognitive Systems at Scale"
- **The Theory**: Scientific management (Taylor 1911). Assembly line and quality control (Deming 1982). SRE (Beyer et al. 2016): SLOs, error budgets, toil. CI/CD as continuous quality gate (Humble & Farley 2010). Spiral model (Boehm 1988).
- **Architectural Mapping** table:
  - Quality gates → `ci_cd_automation/pipeline_manager.py`
  - Assembly line → `orchestrator/workflow.py` (DAG stages)
  - Rollback → `ci_cd_automation/` (automated deployment rollback)
  - Performance monitoring → `ci_cd_automation/performance_optimizer.py`
  - Containerization → `containerization/` (standardized execution units)
  - Model versioning → `model_ops/evaluation/metrics.py`
  - SRE metrics → `telemetry/` (alerting, dashboard)
- **Design Implications**: Rollback as designed-in quality control, fan-out-fan-in as assembly line (Little's Law), model registry as product version management
- Cross-ref: `bio/metabolism.md`
- **Citations**: Humble & Farley 2010, Beyer et al. 2016, Deming 1982, Taylor 1911
- **Docxology**: gastown, MetaInformAnt

## Document Pattern (from `docs/bio/`)

Every document follows this exact structure:
1. `**Series**: [Cognitive Perspectives](./README.md) | **Topic**: [topic]`
2. `## The Theory` — Formal framework, academic grounding (replaces bio's "The Biology")
3. `## Architectural Mapping` — Table + prose connecting theory to modules with source paths
4. `## Design Implications` — Engineering consequences of the theory
5. `## Further Reading` — Academic citations, author-year format
6. `## See Also` — Cross-refs within cognitive/ and to bio/ counterparts
7. Navigation footer: `*Return to [series index](./README.md) | [Bio perspectives](../bio/README.md) | [Project README](../../README.md)*`

Target length: 80-120 lines per document. No padding. Substantive throughout.

## Verification

After creating all 8 files:
1. All relative links resolve (spot-check 5+ cross-references)
2. Every source path reference exists in the codebase
3. Pattern matches `docs/bio/` formatting (header style, section order, footer)
4. No overlap/redundancy with `docs/bio/` content (complementary, not duplicative)
5. Academic citations are real (verifiable authors, years, journals)
6. Docxology repo references match actual repos at github.com/docxology
