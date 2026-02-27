# Codomyrmex Module Index

**Version**: v1.0.0 | **Modules**: 86 | **Last Updated**: February 2026

> [!TIP]
> This INDEX confirms and catalogs every module directory in `src/codomyrmex/`.
> Cross-reference with [`__init__.py`](__init__.py) for the canonical export list.

## Quick Navigation

| Document | Purpose |
| :--- | :--- |
| [README.md](README.md) | Package overview |
| [AGENTS.md](AGENTS.md) | Agent coordination & module listing |
| [SPEC.md](SPEC.md) | Functional specification & architecture |
| [PAI.md](PAI.md) | Personal AI Infrastructure mapping |
| [**init**.py](__init__.py) | Canonical Python exports (86 modules) |

---

## Foundation Layer

Core infrastructure with zero internal dependencies. Used by all other layers.

| Module | Description | Children |
| :--- | :--- | ---: |
| [config_management/](config_management/) | Configuration loading, validation, secrets | 79 |
| [environment_setup/](environment_setup/) | Environment validation & dependency checking | 29 |
| [logging_monitoring/](logging_monitoring/) | Centralized structured logging (JSON) | 65 |
| [model_context_protocol/](model_context_protocol/) | MCP tool specs & protocol handling | 92 |
| [telemetry/](telemetry/) | Metrics collection, tracing, observability | 113 |
| [terminal_interface/](terminal_interface/) | Interactive CLI & terminal utilities | 68 |

---

## Core Layer

Primary functionality depending only on Foundation.

| Module | Description | Children |
| :--- | :--- | ---: |
| [cache/](cache/) | Caching backends & management | 119 |
| [coding/](coding/) | Secure code execution & sandboxing | 263 |
| [compression/](compression/) | Data compression & archiving | 46 |
| [data_visualization/](data_visualization/) | Charts, plots, visualizations | 274 |
| [documents/](documents/) | Document processing & management | 175 |
| [encryption/](encryption/) | Cryptographic operations | 69 |
| [git_operations/](git_operations/) | Git workflow automation | 345 |
| [llm/](llm/) | LLM infrastructure & model management | 243 |
| [networking/](networking/) | Network utilities & HTTP clients | 38 |
| [performance/](performance/) | Performance monitoring & profiling | 67 |
| [scrape/](scrape/) | Web scraping capabilities | 42 |
| [search/](search/) | Code search & pattern discovery | 24 |
| [security/](security/) | Security scanning & vulnerability detection | 203 |
| [serialization/](serialization/) | Data serialization formats | 25 |
| [static_analysis/](static_analysis/) | Import scanning, layer violations, export auditing | 13 |

---

## Service Layer

Higher-level services orchestrating core modules.

| Module | Description | Children |
| :--- | :--- | ---: |
| [api/](api/) | API infrastructure & OpenAPI generation | 125 |
| [auth/](auth/) | Authentication & authorization | 57 |
| [ci_cd_automation/](ci_cd_automation/) | CI/CD pipeline management | 50 |
| [cloud/](cloud/) | Cloud service integrations | 244 |
| [containerization/](containerization/) | Docker & container orchestration | 82 |
| [database_management/](database_management/) | Database operations & migrations | 94 |
| [deployment/](deployment/) | Deployment automation & releases | 68 |
| [documentation/](documentation/) | Documentation generation tools | 36252 |
| [logistics/](logistics/) | Workflow orchestration & scheduling | 174 |
| [orchestrator/](orchestrator/) | DAG-based workflow execution engine | 148 |

---

## Specialized Layer

Advanced features with flexible dependencies.

| Module | Description | Children |
| :--- | :--- | ---: |
| [agentic_memory/](agentic_memory/) | Long-term memory for AI agents | 57 |
| [agents/](agents/) | AI agent integrations (Claude, Codex, Jules…) | 445 |
| [audio/](audio/) | Audio processing & analysis | 69 |
| [bio_simulation/](bio_simulation/) | Biological simulation models | 37 |
| [calendar/](calendar/) | Event management & calendar providers | 23 |
| [cerebrum/](cerebrum/) | Case-based reasoning & Bayesian inference | 115 |
| [cli/](cli/) | Command-line interface | 83 |
| [collaboration/](collaboration/) | Team collaboration tools | 93 |
| [concurrency/](concurrency/) | Concurrency utilities & async patterns | 46 |
| [crypto/](crypto/) | Cryptographic operations | 132 |
| [dark/](dark/) | Dark mode & theming | 72 |
| [defense/](defense/) | Active countermeasures & containment | 22 |
| [dependency_injection/](dependency_injection/) | DI container & patterns | 19 |
| [edge_computing/](edge_computing/) | Edge deployment & inference | 68 |
| [email/](email/) | Email composition & providers | 31 |
| [embodiment/](embodiment/) | Physical embodiment interfaces | 57 |
| [events/](events/) | Event system & pub/sub | 110 |
| [evolutionary_ai/](evolutionary_ai/) | Evolutionary algorithms & optimization | 69 |
| [examples/](examples/) | Usage examples & reference implementations | 14 |
| [exceptions/](exceptions/) | Unified exception hierarchy | 46 |
| [feature_flags/](feature_flags/) | Feature flag management | 68 |
| [finance/](finance/) | Financial modeling & analysis | 49 |
| [formal_verification/](formal_verification/) | Formal verification tools | 2827 |
| [fpf/](fpf/) | Functional Programming Framework | 117 |
| [graph_rag/](graph_rag/) | Graph-based RAG | 21 |
| [ide/](ide/) | IDE integration (VSCode, Antigravity) | 55 |
| [identity/](identity/) | Multi-persona management | 25 |
| [maintenance/](maintenance/) | Project maintenance & dependency analysis | 31 |
| [market/](market/) | Marketplace & auction mechanics | 21 |
| [meme/](meme/) | Memetics & information dynamics | 225 |
| [model_ops/](model_ops/) | ML model operations & lifecycle | 121 |
| [module_template/](module_template/) | Module creation templates | 20 |
| [networks/](networks/) | Network graph analysis | 15 |
| [physical_management/](physical_management/) | Physical system simulation | 31 |
| [plugin_system/](plugin_system/) | Plugin architecture | 54 |
| [privacy/](privacy/) | Metadata scrubbing & privacy tools | 22 |
| [prompt_engineering/](prompt_engineering/) | Prompt design & optimization | 36 |
| [quantum/](quantum/) | Quantum computing interfaces | 25 |
| [relations/](relations/) | Relationship modeling | 59 |
| [simulation/](simulation/) | General simulation framework | 15 |
| [skills/](skills/) | Skills management & integration | 112 |
| [spatial/](spatial/) | 3D/4D spatial modeling | 88 |
| [system_discovery/](system_discovery/) | System introspection & capability mapping | 68 |
| [templating/](templating/) | Template rendering engine | 57 |
| [testing/](testing/) | Test utilities & runners | 65 |
| [tests/](tests/) | Package test suites | 3003 |
| [tool_use/](tool_use/) | Tool use abstraction layer | 19 |
| [utils/](utils/) | Common utilities | 51 |
| [validation/](validation/) | Data validation & schema checking | 75 |
| [vector_store/](vector_store/) | Vector storage & similarity search | 19 |
| [video/](video/) | Video processing & analysis | 56 |
| [wallet/](wallet/) | Self-custody & key management | 56 |
| [website/](website/) | Website generation & hosting | 77 |

---

## Confirmation

| Check | Status |
| :--- | :--- |
| Directions on disk | **86** |
| Modules in `__init__.py._submodules` | **86** (excl. examples/tests) |
| Modules in `__all__` | **89** (86 modules + 3 utility functions) |
| Foundation Layer | **6** modules |
| Core Layer | **15** modules |
| Service Layer | **10** modules |
| Specialized Layer | **55** modules |
| **Total** | **86** ✅ |

---

## Parent Navigation

- **📁 Source Directory**: [../INDEX.md](../INDEX.md)
- **🏠 Project Root**: [../../INDEX.md](../../INDEX.md)
- **📖 README**: [README.md](README.md)
- **🤖 AGENTS**: [AGENTS.md](AGENTS.md)
- **📋 SPEC**: [SPEC.md](SPEC.md)
