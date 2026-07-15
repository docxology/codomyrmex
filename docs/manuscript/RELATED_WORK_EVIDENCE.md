# Related-work and evidence register

This register keeps the manuscript's external grounding separate from evidence about
Codomyrmex. Each source is primary scholarly or official material. A source can justify a
definition, protocol choice, or comparison target; it cannot validate the Colony Kernel
without an executed, provider-backed study.

| Domain | Source | What it supports here | Boundary retained |
|---|---|---|---|
| Stigmergy | Grassé (1959), [doi:10.1007/BF02223791](https://doi.org/10.1007/BF02223791) | Historical definition of coordination mediated by environmental changes | The kernel's trace field is a deterministic engineering analogy, not biological stigmergy or ant-colony optimization |
| Active inference | Friston (2010), [doi:10.1038/nrn2787](https://doi.org/10.1038/nrn2787) | Primary source for the free-energy framing used in the conceptual crosswalk | The kernel does not implement a generative model, posterior inference, or expected-free-energy policy selection |
| Agent evaluation | Jimenez et al. (2023), [SWE-bench](https://arxiv.org/abs/2310.06770) | Primary repository-level software-engineering evaluation precedent and task-family rationale | SWE-bench results are not results for this control plane; the planned study must release its own traces and pins |
| Broad agent evaluation | Liang et al. (2022), [HELM](https://arxiv.org/abs/2211.09110) | Primary evaluation-framework precedent for reporting multiple dimensions and releasing raw completions | A broad metric surface does not remove the need for provider identity, denominators, partitions, and provenance |
| Paired binary statistics | McNemar (1947), [doi:10.1007/BF02295996](https://doi.org/10.1007/BF02295996) | Primary basis for the exact conditional paired nominal-data test used by the analysis layer | The test addresses paired binary outcomes; it does not establish causal attribution or external validity |
| Reproducibility | ACM SIGSIM PADS, [artifact evaluation guidance](https://sigsim.acm.org/conf/pads/2024/blog/artifact-evaluation/) | Official artifact-evaluation expectations for documented, functional, reusable, reproducible artifacts | A clean replay is evidence about artifact reproducibility, not proof of production safety |
| Safety-case provenance | ISO/IEC 15026-2, [assurance-case standard](https://www.iso.org/standard/52926.html) | Official structured-argument model linking claims, assumptions, and evidence | The repository's release manifest is a provenance aid, not certification or an assurance case by itself |

## Use in the manuscript

The related-work section uses these sources only for positioning and protocol design. The
claim-status table remains the authority for what this release supports. In particular,
the benchmark remains `not evaluated` while the checked-in executor registry is empty and
no provider-backed raw result, trusted receipt bundle, and clean-clone replay are present.
