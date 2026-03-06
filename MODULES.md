# Codomyrmex Module Index

128 modules grouped by domain. Install extras with `uv sync --extra <group>`.

## AI / ML Core

| Module | Description |
|--------|-------------|
| `llm` | LLM provider abstraction (Ollama, OpenAI, Anthropic, Gemini) |
| `model_ops` | Model evaluation, benchmarking, registry, fine-tuning |
| `agents` | AI agent framework integrations and orchestration |
| `agentic_memory` | Persistent agent memory: store, retrieve, semantic search |
| `prompt_engineering` | Prompt templates, evaluation, optimization, versioning |
| `cerebrum` | Case-based reasoning, knowledge retrieval, FPF orchestration |
| `neural` | Transformer, attention, and neural building blocks |
| `autograd` | Automatic differentiation engine |
| `quantization` | INT8 and model quantization utilities |
| `peft` | Parameter-efficient fine-tuning adapters (LoRA, etc.) |
| `rlhf` | Reinforcement learning from human feedback (PPO) |
| `dpo` | Direct preference optimization |
| `distillation` | Model distillation pipelines |
| `nas` | Neural architecture search |
| `slm` | Small language model wrappers |
| `lora` | LoRA adapter utilities |
| `logit_processor` | Custom logit processors for sampling |
| `ssm` | State space model components |
| `matmul_kernel` | Optimized matrix multiply kernels |
| `softmax_opt` | Optimized softmax implementations |
| `distributed_training` | Multi-GPU and distributed training (FSDP) |
| `model_merger` | Model merging strategies (TIES, SLERP, DARE) |
| `tokenizer` | Custom tokenizer training and management |
| `multimodal` | Imagen 3 image generation, multi-modal AI pipelines |

## Agents & Automation

| Module | Description |
|--------|-------------|
| `aider` | AI pair programmer (aider-chat subprocess wrapper) — install via `uv tool install aider-chat` |
| `soul` | Markdown-based persistent LLM memory (soul-agent wrapper) |
| `orchestrator` | Workflow execution, scheduling, retry policies |
| `logistics` | Project/task management, scheduling, timezone utilities |
| `collaboration` | Multi-agent swarm, worker pool, broadcaster |
| `ai_gateway` | Unified AI model gateway with routing |
| `demos` | Demo registry and showcase scripts |
| `email` | Gmail, AgentMail providers, SMTP, IMAP |
| `calendar_integration` | Google Calendar CRUD, event management, scheduling |
| `pai_pm` | PAI Project Manager server (Bun/TypeScript) |

## Data & Storage

| Module | Description |
|--------|-------------|
| `data_visualization` | Chart and dashboard generation, HTML export |
| `database_management` | DB migrations and query utilities |
| `documents` | Document models, formats, transformation, merging |
| `serialization` | Format-agnostic serialization (JSON, YAML, msgpack, Avro, Parquet) |
| `cache` | Redis and in-memory cache backends with warmers |
| `vector_store` | Vector embedding storage and similarity search |
| `feature_store` | ML feature definitions and retrieval |
| `data_curation` | Dataset curation pipelines |
| `data_lineage` | Data provenance and lineage tracking |
| `ml_pipeline` | End-to-end ML pipeline utilities |
| `synthetic_data` | Synthetic dataset generation |

## Security & Privacy

| Module | Description |
|--------|-------------|
| `security` | Vulnerability scanning, secret detection, code security audit |
| `encryption` | Symmetric/asymmetric encryption utilities |
| `crypto` | Key generation, hashing, hash verification |
| `auth` | Google OAuth and authentication helpers |
| `privacy` | PII detection and anonymization |
| `defense` | Defensive security patterns |
| `formal_verification` | Z3 constraint solving and model checking |

## Infrastructure & Cloud

| Module | Description |
|--------|-------------|
| `ci_cd_automation` | Pipeline generation, build orchestration, deployment |
| `containerization` | Docker build/scan/run, Kubernetes orchestration |
| `cloud` | Cloud instance management, S3, Infomaniak, Coda |
| `deployment` | Deployment manager and strategy patterns |
| `edge_computing` | Edge node management |
| `networking` | Service mesh, network utilities |
| `environment_setup` | Environment validation and dependency checking |
| `container_optimization` | Docker image optimization |
| `cost_management` | Cloud cost tracking and alerting |
| `networks` | Network topology and graph analysis |

## Code & Development Tools

| Module | Description |
|--------|-------------|
| `coding` | Code execution sandbox, review, debugging, static analysis |
| `static_analysis` | Linting and security scanning wrappers |
| `git_operations` | Version control automation (35+ MCP tools) |
| `git_analysis` | Git history analysis, contributor stats, commit patterns |
| `documentation` | Doc generation, RASP compliance audit |
| `docs_gen` | Automated documentation generation |
| `testing` | Test fixtures, chaos scenarios, workflow test runners |
| `tree_sitter` | Tree-sitter parsing for 20+ languages |
| `languages` | Language detection and analysis |
| `ide` | IDE integration (Antigravity agent bridge, relay endpoint) |
| `release` | Release management utilities |
| `config_audits` | Configuration auditing tools |
| `config_monitoring` | Runtime configuration change monitoring |
| `module_template` | Module creation templates and scaffolding |
| `file_system` | File operations, directory walker, permissions |
| `operating_system` | OS interaction (macOS/Linux/Windows), filesystem |
| `examples` | Reference implementation examples and demos |

## API & Web

| Module | Description |
|--------|-------------|
| `api` | REST API framework, circuit breaker, pagination, mocking |
| `model_context_protocol` | MCP server transport, decorators, discovery |
| `scrape` | HTML content extraction, text similarity (Firecrawl) |
| `search` | Full-text, fuzzy, and indexed search |
| `website` | Web server, health endpoint, PAI awareness mixin |
| `templating` | Jinja2 template loading and management |
| `text_to_sql` | Natural language to SQL engine |
| `semantic_router` | Semantic request routing |
| `tool_use` | Tool registry and validation |

## Knowledge & Intelligence

| Module | Description |
|--------|-------------|
| `skills` | Skill discovery, listing, invocation |
| `plugin_system` | Plugin discovery and dependency resolution |
| `validation` | Schema validation, config validation, summaries |
| `relations` | Relationship strength scoring |
| `graph_rag` | Graph-based retrieval-augmented generation |
| `eval_harness` | Evaluation harness for model benchmarking |
| `evolutionary_ai` | Evolutionary algorithms and population management |

## Media & Sensors

| Module | Description |
|--------|-------------|
| `audio` | Speech-to-text (Whisper), text-to-speech (pyttsx3, edge-tts) |
| `video` | Video analysis, frame extraction, processing |
| `image` | Image processing utilities |
| `spatial` | 3D spatial computation, coordinates |
| `simulation` | Agent-based simulation engine |
| `physical_management` | Physical object simulation and management |
| `embodiment` | Embodied agent interfaces |

## Observability & Platform

| Module | Description |
|--------|-------------|
| `logging_monitoring` | Centralized structured logging and monitoring |
| `telemetry` | Metrics, spans, SLO tracking, alerting |
| `performance` | Benchmark comparison, regression detection |
| `events` | Event bus: emit, history, type registry |
| `maintenance` | Health checks and scheduled tasks |
| `system_discovery` | Module health monitoring, dependency tree |
| `config_management` | Get/set/validate configuration |
| `feature_flags` | Feature flag management with strategies |
| `terminal_interface` | Rich terminal output and formatting |
| `cli` | Command-line interface entry point |
| `utils` | Shared utilities, retry logic, i18n |
| `exceptions` | Shared exception hierarchy |
| `concurrency` | Distributed locks, semaphores, Redis locking |
| `compression` | gzip, zstd, brotli compression algorithms |
| `dependency_injection` | IoC container, service locator, scoped lifetimes |

## Research & Experimental

| Module | Description |
|--------|-------------|
| `quantum` | Quantum computing interfaces |
| `bio_simulation` | Biological simulation models |
| `interpretability` | Model interpretability tools |
| `meme` | Meme analysis (experimental) |
| `market` | Market data interfaces |
| `finance` | Financial computation utilities |
| `dark` | Dark data processing (PDF extraction) |
| `fpf` | Feed-Parse-Format pipeline (fetch, parse, section export) |
| `wallet` | Crypto wallet and contract registry |
| `identity` | Digital identity management |

---

> For API boundaries between adjacent modules, see each module's `README.md`.
> For MCP tool listings, see each module's `MCP_TOOL_SPECIFICATION.md`.
> For PAI integration, see each module's `PAI.md`.
