# References {#sec:references}

The bibliography for this manuscript is maintained in `docs/manuscript/references.bib` using BibTeX format. Pandoc processes it during compilation via the `--natbib` flag, which delegates citation rendering to the `natbib` LaTeX package. All entries in `references.bib` must be valid BibTeX; validate before submission using:

```bash
uv run python -m infrastructure.reference.citation.cli validate \
    docs/manuscript/references.bib --strict
```

Citation syntax throughout the manuscript uses the Pandoc-native `[@key]` form (e.g. `[@smith2024]` for a single reference, `[@smith2024; @jones2023]` for multiple). Raw `\cite{}` commands must not appear in Markdown source — they bypass Pandoc's citation pipeline and break non-LaTeX output targets.

## Bibliography Coverage

The bibliography contains 28 entries spanning the five primary citation domains of this manuscript: stigmergy and self-organizing systems, multi-agent trust and reputation, reinforcement learning and consequence memory, capability-based security and least authority, and agentic software engineering frameworks.

**Citation key inventory** (all keys cited in the manuscript body have corresponding entries in `references.bib`):

| Key | Entry | Domain |
|-----|-------|--------|
| `friston2010free` | Friston 2010 — Free Energy Principle | Active Inference |
| `grasse1959reconstruction` | Grassé 1959 — Stigmergy original formulation | Stigmergy |
| `parunak1997pheromones` | Parunak 1997 — Digital pheromones for distributed software agents | Stigmergy |
| `dorigo2004aco` | Dorigo & Stützle 2004 — Ant Colony Optimization | Stigmergy / ACO |
| `bonabeau1999swarm` | Bonabeau et al. 1999 — Swarm Intelligence | Stigmergy |
| `wooldridge1995intelligent` | Wooldridge & Jennings 1995 — Intelligent Agents | MAS |
| `marsh1994trust` | Marsh 1994 — Formalising Trust as a Computational Concept | MAS Trust |
| `huynh2006fire` | Huynh et al. 2006 — FIRE integrated trust and reputation model | MAS Trust |
| `burnett2013bootstrapping` | Burnett et al. 2013 — Bootstrapping trust via stereotypes | MAS Trust |
| `kamvar2003eigentrust` | Kamvar et al. 2003 — EigenTrust reputation management | MAS Trust |
| `sabater2005review` | Sabater & Sierra 2005 — Review of computational trust models | MAS Trust |
| `sutton2018reinforcement` | Sutton & Barto 2018 — Reinforcement Learning: An Introduction | RL |
| `miller2003capabilities` | Miller & Shapiro 2003 — Capability-based security | Security |
| `saltzer1975protection` | Saltzer & Schroeder 1975 — Principle of Least Authority (POLA) | Security |
| `yang2024swebench` | Yang et al. 2024 — SWE-bench: LLM patch generation benchmark | Agentic SE |
| `langgraph2024` | LangChain AI 2024 — LangGraph state machine for agentic pipelines | Agentic SE |
| `wu2023autogen` | Wu et al. 2023 — AutoGen conversational multi-agent framework | Agentic SE |
| `anthropic2024mcp` | Anthropic 2024 — Model Context Protocol specification | MCP |
| `kauffman1993origins` | Kauffman 1993 — Origins of Order | Self-Organization |
| `apt2003principles` | Apt 2003 — Principles of Constraint Programming | Constraint Programming |
| `popper1959logic` | Popper 1959 — Logic of Scientific Discovery | Falsification |
| `peng2011reproducible` | Peng 2011 — Reproducible Research in Computational Science | Reproducibility |
| `dorigo2004ant` | Dorigo & Stützle 2004 — Ant Colony Optimization (alternate key) | Stigmergy / ACO |
| `crewai2024` | CrewAI 2024 — Role-based agent teams and hierarchical task delegation | Agentic SE |
| `bai2022constitutional` | Bai et al. 2022 — Constitutional AI: Harmlessness from AI Feedback | RL / Alignment |
| `christiano2017deep` | Christiano et al. 2017 — Deep Reinforcement Learning from Human Preferences | RL / Alignment |
| `lightman2023let` | Lightman et al. 2023 — Let's Verify Step by Step (Process Reward Models) | RL / PRMs |
| `uesato2022solving` | Uesato et al. 2022 — Solving Math Word Problems with Process- and Outcome-Based Feedback | RL / PRMs |

**Unresolved keys:** none. Every `[@key]` citation in the manuscript body has a corresponding entry in `references.bib`. Run the validation command above before submission to confirm.

**Coverage note:** The 12 trust and stigmergy references represent the theoretical core. The agentic SE trio (SWE-bench, LangGraph, AutoGen) anchors the positioning claim that existing frameworks lack persistent consequence memory — a claim that is empirically grounded by the absence of trust-accumulation primitives in those systems' documented APIs. The Saltzer & Schroeder and Miller capability-security citations connect the ActuationGate design to a 50-year lineage of least-authority engineering, establishing that the gate is not a novel ad hoc mechanism but a concrete instantiation of well-understood security principles applied to a new threat surface.
