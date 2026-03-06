# Jules Mega-Swarm v2 — 260 Targeted Tasks

# Each non-empty, non-comment line is a standalone Jules agent prompt

# Dispatched via: ./mega_swarm_v2_dispatcher.py or ./jules_batch_dispatch.sh swarm_tasks_v2.md

# Date: 2026-03-05 | Repository: docxology/codomyrmex

# ============================================================================

# WAVE 1: FOUNDATION LAYER — Zero-Mock Test Backfill & Module Hardening (40 agents)

# ============================================================================

# --- concurrency ---

In src/codomyrmex/concurrency/, review and improve all methods in core.py and pool.py. Add comprehensive zero-mock tests in src/codomyrmex/tests/unit/concurrency/ covering thread pool creation, async task submission, parallel execution, and edge cases (empty task list, exception propagation). Use 'uv run pytest' to verify. No mocking allowed.
In src/codomyrmex/concurrency/, review README.md, SPEC.md, and AGENTS.md for accuracy. Update all docstrings in every .py file to include Args, Returns, Raises, and Example sections. Ensure SPEC.md documents the complete public API surface.

# --- events ---

In src/codomyrmex/events/, review and improve all event emission, subscription, and handler methods. Add zero-mock tests covering event registration, emission ordering, wildcard subscriptions, handler exceptions, and event filtering. Use 'uv run pytest' to verify. No mocking allowed.
In src/codomyrmex/events/, audit mcp_tools.py for correct @mcp_tool decorator usage. Ensure each tool has proper type hints, docstrings, and a corresponding zero-mock test. Add any missing MCP tools for event replay and event history querying.

# --- logging_monitoring ---

In src/codomyrmex/logging_monitoring/, review and improve the JSON-structured logging infrastructure. Add zero-mock tests for log formatting, log level filtering, file rotation, and structured field injection. Verify all tests pass with 'uv run pytest'. No mocking allowed.
In src/codomyrmex/logging_monitoring/, update README.md with usage examples for all public functions. Add SPEC.md entries for any undocumented public APIs. Ensure AGENTS.md accurately describes how agents should interact with this module.

# --- performance ---

In src/codomyrmex/performance/, review and improve caching, lazy loading, and benchmarking methods. Add zero-mock tests for resource manager lifecycle, cache eviction policies, lazy initialization, and benchmark timing accuracy. Use 'uv run pytest' to verify.
In src/codomyrmex/performance/, audit mcp_tools.py and ensure all performance profiling tools have proper type hints and zero-mock test coverage. Add any missing MCP tools for memory profiling and CPU profiling.

# --- system_discovery ---

In src/codomyrmex/system_discovery/, review and improve system introspection and environment scanning. Add zero-mock tests for OS detection, Python version checking, dependency validation, GPU detection, and capability reporting. Use 'uv run pytest' to verify.

# --- telemetry ---

In src/codomyrmex/telemetry/, review and improve the OpenTelemetry-compatible tracing framework. Add zero-mock tests for span creation, context propagation, metric recording, and trace export formatting. Use 'uv run pytest' to verify.
In src/codomyrmex/telemetry/, add agent-specific telemetry hooks as described in TODO.md v1.1.7 — implement granular performance tracking for agent execution flows to provide exact latency visibility. Add zero-mock tests.

# --- terminal_interface ---

In src/codomyrmex/terminal_interface/, review and improve the Rich CLI implementation. Add zero-mock tests for colored output rendering, interactive prompts, progress bars, table formatting, and status spinners. Use 'uv run pytest' to verify.

# --- utils ---

In src/codomyrmex/utils/, review and improve all shared utility functions. Add zero-mock tests for every public function including file I/O helpers, data processing utilities, string manipulation, and path normalization. Use 'uv run pytest' to verify.

# --- environment_setup ---

In src/codomyrmex/environment_setup/, review and improve Python version validation and dependency checking. Add zero-mock tests for version constraint checking, missing dependency detection, and environment report generation. Use 'uv run pytest' to verify.

# --- exceptions ---

In src/codomyrmex/exceptions/, review and improve the exception hierarchy. Ensure every custom exception has proper docstrings, is tested with zero-mock tests covering instantiation, message formatting, and exception chaining. Use 'uv run pytest' to verify.

# --- validation ---

In src/codomyrmex/validation/, review and improve all validation logic. Add zero-mock tests for input validation, schema validation, type coercion, and error message formatting. Use 'uv run pytest' to verify.

# --- config_management ---

In src/codomyrmex/config_management/, review and improve configuration loading, merging, and environment variable resolution. Add zero-mock tests for config precedence, env var substitution, YAML/JSON loading, and default value handling. Use 'uv run pytest' to verify.

# ============================================================================

# WAVE 2: CORE SERVICES LAYER — Comprehensive Review & Enhancement (35 agents)

# ============================================================================

# --- agents ---

In src/codomyrmex/agents/, review and improve the multi-model AI agent framework. Focus on the LLM client factory, structured response dataclasses, and provider abstraction. Add zero-mock tests for agent lifecycle, response parsing, and error handling. Use 'uv run pytest' to verify.
In src/codomyrmex/agents/, review the Claude, Gemini, Qwen, and Jules provider integrations. Ensure each provider has consistent error handling, retry logic, and zero-mock tests. Fix any type hint issues flagged by ty.
In src/codomyrmex/agents/, update AGENTS.md and SPEC.md to accurately reflect the current provider-specific folder organization and the unified LLM client factory pattern. Ensure README.md has working code examples.

# --- llm ---

In src/codomyrmex/llm/, review and improve the language model provider integration. Add zero-mock tests for prompt templating, token counting, streaming response handling, and provider fallback logic. Use 'uv run pytest' to verify.
In src/codomyrmex/llm/, review the RAG subsystem and chain implementations. Ensure retrieval, augmentation, and generation steps have zero-mock tests. Fix any import errors or type issues.
In src/codomyrmex/llm/, review the OpenRouter provider including the FREE_MODELS list. Ensure all provider methods have zero-mock tests and proper error handling for rate limits and API failures.

# --- git_operations ---

In src/codomyrmex/git_operations/, review and improve the programmatic Git interface. Add zero-mock tests for commit, branch, merge, diff, log, status, and stash operations using real temporary git repos. Use 'uv run pytest' to verify.
In src/codomyrmex/git_operations/, update documentation (README.md, SPEC.md) with complete API reference. Ensure mcp_tools.py exposes all key Git operations as MCP tools with proper type hints.

# --- model_context_protocol ---

In src/codomyrmex/model_context_protocol/, review and improve the MCP standard schemas and tool decorator. Add zero-mock tests for @mcp_tool decorator, schema validation, tool registration, tool discovery, and request/response serialization. Use 'uv run pytest' to verify.
In src/codomyrmex/model_context_protocol/, ensure all tool schemas are JSON Schema compliant. Add tests for schema generation from Python type hints and validate against the MCP specification.

# --- pattern_matching ---

In src/codomyrmex/pattern_matching/, review and improve AST parsing, pattern recognition, and semantic search. Add zero-mock tests for regex matching, AST node querying, fuzzy matching, and structural pattern detection. Use 'uv run pytest' to verify.

# --- static_analysis ---

In src/codomyrmex/static_analysis/, review and improve code quality assessment, linting integration, and security scanning. Add zero-mock tests for lint rule application, violation detection, auto-fix generation, and severity classification. Use 'uv run pytest' to verify.

# --- tree_sitter ---

In src/codomyrmex/tree_sitter/, review and improve multi-language source code parsing. Add zero-mock tests for Python, JavaScript, TypeScript, and Rust parsing including AST traversal, node extraction, and code transformation. Use 'uv run pytest' to verify.
In src/codomyrmex/tree_sitter/, ensure proper grammar loading, error recovery, and incremental parsing. Add zero-mock tests for large file parsing and editing operations.

# --- auth ---

In src/codomyrmex/auth/, review and improve multi-provider authentication (OAuth, JWT, API Keys). Add zero-mock tests for token generation, validation, expiry, refresh, and revocation. Use 'uv run pytest' to verify.
In src/codomyrmex/auth/, review mcp_tools.py for security best practices. Ensure no secrets are logged, tokens have proper scoping, and all auth flows have zero-mock test coverage.

# --- serialization ---

In src/codomyrmex/serialization/, review and improve multi-format data conversion (JSON, YAML, MsgPack). Add property-based tests using hypothesis for schema validators and data round-trips (encode→decode identity). Use 'uv run pytest' to verify. This is a v1.1.7 priority.

# --- api ---

In src/codomyrmex/api/, review and improve the API layer. Add zero-mock tests for route handling, request validation, response formatting, error responses, and middleware. Use 'uv run pytest' to verify.

# --- cli ---

In src/codomyrmex/cli/, review and improve the CLI interface. Add zero-mock tests for argument parsing, subcommand dispatch, help text generation, and error output. Use 'uv run pytest' to verify.

# ============================================================================

# WAVE 3: DATA & KNOWLEDGE LAYER (25 agents)

# ============================================================================

# --- cache ---

In src/codomyrmex/cache/, review and improve the unified caching framework (Memory, File, Redis). Add zero-mock tests for cache get/set, TTL expiry, eviction policies (LRU, LFU), cache invalidation, and backend switching. Use 'uv run pytest' to verify.
In src/codomyrmex/cache/core.py, this is a v1.1.7 mutation testing target. Ensure every branch and edge case is covered by tests. Add boundary condition tests for cache size limits and concurrent access patterns.

# --- database_management ---

In src/codomyrmex/database_management/, review and improve DB operations, connection pooling, and migration support. Add zero-mock tests using SQLite for connection lifecycle, query execution, transaction handling, and schema migration. Use 'uv run pytest' to verify.

# --- documents ---

In src/codomyrmex/documents/, review and improve document parsing and transformation (PDF, Markdown, etc.). Add zero-mock tests for Markdown parsing, text extraction, document chunking, and format conversion. Use 'uv run pytest' to verify.

# --- data_visualization ---

In src/codomyrmex/data_visualization/, review and improve multi-engine plotting capabilities. Add zero-mock tests for chart generation, theme application, data binding, and Mermaid diagram rendering. Use 'uv run pytest' to verify.
In src/codomyrmex/data_visualization/, add test-run history timeline and module health heatmap logic as specified in TODO.md v1.1.9. Write zero-mock tests for the new visualization logic.

# --- feature_store ---

In src/codomyrmex/feature_store/, review and improve ML feature management and versioning. Add zero-mock tests for feature registration, retrieval, versioning, and metadata management. Use 'uv run pytest' to verify.

# --- graph_rag ---

In src/codomyrmex/graph_rag/, review and improve the knowledge graph + RAG integration. Add zero-mock tests for entity extraction, relationship mapping, graph traversal, and RAG query generation. This is a v1.1.7 coverage target. Use 'uv run pytest' to verify.

# --- vector_store ---

In src/codomyrmex/vector_store/, review and improve vector storage and similarity search. Add zero-mock tests for embedding storage, cosine similarity search, index management, and batch operations. Use 'uv run pytest' to verify.

# --- search ---

In src/codomyrmex/search/, review and improve search functionality. Add zero-mock tests for full-text search, fuzzy matching, result ranking, and search index management. Use 'uv run pytest' to verify.

# --- data_lineage ---

In src/codomyrmex/data_lineage/, review and improve provenance and transformation audit trails. Add zero-mock tests for lineage tracking, transformation logging, dependency graph construction, and audit report generation. Use 'uv run pytest' to verify.

# --- agentic_memory ---

In src/codomyrmex/agentic_memory/, review and improve long-term stateful agent memory systems. Add zero-mock tests for memory store CRUD operations, TTL expiry, tag indexing, and cross-session retrieval. This is a v1.1.8 priority. Use 'uv run pytest' to verify.

# ============================================================================

# WAVE 4: AUTOMATION & TOOLING LAYER (25 agents)

# ============================================================================

# --- orchestrator ---

In src/codomyrmex/orchestrator/, review and improve workflow DAG execution, pipelines, and triggers. Add zero-mock tests for DAG construction, topological sorting, pipeline execution, trigger conditions, and state persistence. Use 'uv run pytest' to verify.
In src/codomyrmex/orchestrator/, review template and state management. Ensure zero-mock tests cover workflow resumption, error recovery, and partial execution rollback.

# --- logistics ---

In src/codomyrmex/logistics/, review and improve task management, scheduling, and resource optimization. Add zero-mock tests for task creation, priority queuing, scheduling algorithms, and resource allocation. Use 'uv run pytest' to verify.

# --- ci_cd_automation ---

In src/codomyrmex/ci_cd_automation/, review and improve CI/CD pipeline orchestration. Add zero-mock tests for pipeline definition, stage execution, artifact collection, and deployment triggering. Use 'uv run pytest' to verify.

# --- coding ---

In src/codomyrmex/coding/, review and improve sandboxed execution and AI-assisted code editing. Add zero-mock tests for code execution isolation, refactoring operations, code generation, and test running. Use 'uv run pytest' to verify.
In src/codomyrmex/coding/, review the formal verification spike (v1.1.8 target). Ensure the z3-solver integration path is documented and initial invariant checking scaffolding has tests.

# --- deployment ---

In src/codomyrmex/deployment/, review and improve infrastructure-as-code and rollout management. Add zero-mock tests for deployment plan generation, rollback procedures, health check verification, and canary deployment logic. Use 'uv run pytest' to verify.

# --- plugin_system ---

In src/codomyrmex/plugin_system/, review and improve dynamic capability extension. Add zero-mock tests for plugin discovery, loading, unloading, version checking, dependency resolution, and sandboxed execution. Use 'uv run pytest' to verify.

# --- build_synthesis ---

In src/codomyrmex/build_synthesis/, review and improve build automation and artifact synthesis. Add zero-mock tests for build plan generation, artifact packaging, checksum verification, and build caching. Use 'uv run pytest' to verify.

# --- containerization ---

In src/codomyrmex/containerization/, review and improve Docker, Kubernetes, and container registry operations. Add zero-mock tests for Dockerfile generation, image building simulation, K8s manifest templating, and registry interaction. Use 'uv run pytest' to verify.

# --- tool_use ---

In src/codomyrmex/tool_use/, review and improve tool invocation and registration. Add zero-mock tests for tool registration, discovery, invocation, parameter validation, and result handling. Use 'uv run pytest' to verify.

# ============================================================================

# WAVE 5: SPECIALIZED ENGINE LAYER — Part A: AI/ML Modules (30 agents)

# ============================================================================

# --- cerebrum ---

In src/codomyrmex/cerebrum/, review and improve the Bayesian reasoning engine and cognitive architecture. Add zero-mock tests for belief updating, probabilistic inference, uncertainty quantification, and belief revision. This is a v1.1.7 coverage target. Use 'uv run pytest' to verify.

# --- spatial ---

In src/codomyrmex/spatial/, review and improve 3D/4D modeling and world model representations. Add zero-mock tests for coordinate transformations, geodesic calculations, icosahedral mesh generation, and 4D rotation matrices. This is a v1.1.7 coverage target. Use 'uv run pytest' to verify.

# --- embodiment ---

In src/codomyrmex/embodiment/, review and improve the ROS2 bridge and physical system integration. Add zero-mock tests for sensor data processing, actuator command generation, and coordinate frame transformations. Use 'uv run pytest' to verify.

# --- evolutionary_ai ---

In src/codomyrmex/evolutionary_ai/, review and improve genetic algorithms and neural architecture search. Add zero-mock tests for population initialization, crossover, mutation, selection, and fitness evaluation. Use 'uv run pytest' to verify.

# --- prompt_engineering ---

In src/codomyrmex/prompt_engineering/, review and improve prompt construction and template management. Add zero-mock tests for prompt templating, variable substitution, chain-of-thought formatting, and few-shot example management. Use 'uv run pytest' to verify.

# --- prompt_testing ---

In src/codomyrmex/prompt_testing/, review and improve systematic evaluation and A/B testing for prompts. Add zero-mock tests for test case generation, metric collection, comparison analysis, and regression detection. Use 'uv run pytest' to verify.

# --- inference_optimization ---

In src/codomyrmex/quantization/, review and improve INT8/INT4 quantization wrappers. Add zero-mock tests for weight quantization, calibration, accuracy validation, and memory reduction calculations. Use 'uv run pytest' to verify.

# --- distillation ---

In src/codomyrmex/distillation/, review and improve knowledge distillation and student-teacher pipelines. Add zero-mock tests for distillation loss computation, temperature scaling, soft label generation, and student model evaluation. Use 'uv run pytest' to verify.

# --- lora ---

In src/codomyrmex/lora/, review and improve Low-Rank Adaptation training and adapter management. Add zero-mock tests for LoRA initialization, rank selection, adapter merging, and weight decomposition. Use 'uv run pytest' to verify.

# --- peft ---

In src/codomyrmex/peft/, review and improve Parameter-Efficient Fine-Tuning methods. Add zero-mock tests for adapter creation, prefix tuning, prompt tuning, and method comparison utilities. Use 'uv run pytest' to verify.

# --- dpo ---

In src/codomyrmex/dpo/, review and improve Direct Preference Optimization for alignment. Add zero-mock tests for preference pair construction, DPO loss computation, reward model integration, and training loop logic. Use 'uv run pytest' to verify.

# --- rlhf ---

In src/codomyrmex/rlhf/, review and improve PPO reinforcement learning pipelines. Add zero-mock tests for PPO loss computation, advantage estimation, reward normalization, and policy update steps. Use 'uv run pytest' to verify.

# --- eval_harness ---

In src/codomyrmex/eval_harness/, review and improve systematic LLM benchmark and custom eval suites. Add zero-mock tests for benchmark registration, metric computation, result aggregation, and leaderboard generation. Use 'uv run pytest' to verify.

# --- interpretability ---

In src/codomyrmex/interpretability/, review and improve Sparse Autoencoder (SAE) and mechanistic analysis. Add zero-mock tests for feature extraction, activation analysis, neuron importance scoring, and attribution methods. Use 'uv run pytest' to verify.

# --- model_merger ---

In src/codomyrmex/model_merger/, review and improve TIES, SLERP, and average merging for model weights. Add zero-mock tests for weight interpolation, merge strategy selection, and merged model validation. Use 'uv run pytest' to verify.

# --- synthetic_data ---

In src/codomyrmex/synthetic_data/, review and improve multi-agent synthetic dataset generation. Add zero-mock tests for data template creation, quality filtering, deduplication, and format conversion. Use 'uv run pytest' to verify.

# --- model_registry ---

In src/codomyrmex/model_ops/, review and improve ML model storage and lifecycle tracking. Add zero-mock tests for model registration, version comparison, metadata management, and artifact linking. Use 'uv run pytest' to verify.

# --- semantic_router ---

In src/codomyrmex/semantic_router/, review and improve vector-based intent routing and semantic load-balancing. Add zero-mock tests for intent classification, route matching, fallback handling, and load distribution. Use 'uv run pytest' to verify.

# --- ai_gateway ---

In src/codomyrmex/ai_gateway/, review and improve unified AI provider routing and optimization. Add zero-mock tests for provider selection, request routing, failover, budget-aware routing, and response normalization. Use 'uv run pytest' to verify.

# --- data_curation ---

In src/codomyrmex/data_curation/, review and improve MinHash-based deduplication and quality filtering. Add zero-mock tests for MinHash computation, dedup detection, quality scoring, and batch processing. Use 'uv run pytest' to verify.

# ============================================================================

# WAVE 6: SPECIALIZED ENGINE LAYER — Part B: Systems & Infrastructure (25 agents)

# ============================================================================

# --- neural ---

In src/codomyrmex/neural/, review and improve neural network components and architectures. Add zero-mock tests for layer construction, forward pass computation, gradient flow, and architecture serialization. Use 'uv run pytest' to verify.

# --- autograd ---

In src/codomyrmex/autograd/, review and improve the automatic differentiation engine. Add zero-mock tests for gradient computation, backpropagation, computational graph construction, and gradient accumulation. Use 'uv run pytest' to verify.

# --- logit_processor ---

In src/codomyrmex/logit_processor/, review and improve logit modification and sampling control. Add zero-mock tests for temperature scaling, top-k filtering, top-p (nucleus) sampling, repetition penalty, and logit bias application. Use 'uv run pytest' to verify.

# --- softmax_opt ---

In src/codomyrmex/softmax_opt/, review and improve optimized softmax implementations. Add zero-mock tests for numerical stability, flash attention compatibility, overflow handling, and performance benchmarks. Use 'uv run pytest' to verify.

# --- matmul_kernel ---

In src/codomyrmex/matmul_kernel/, review and improve low-level matrix multiplication kernels. Add zero-mock tests for matrix multiplication correctness, tiling strategies, and numerical precision. Use 'uv run pytest' to verify.

# --- nas ---

In src/codomyrmex/nas/, review and improve Neural Architecture Search. Add zero-mock tests for search space definition, architecture sampling, performance prediction, and Pareto frontier computation. Use 'uv run pytest' to verify.

# --- ssm ---

In src/codomyrmex/ssm/, review and improve State Space Models implementation. Add zero-mock tests for state transition, observation generation, parameter estimation, and sequence modeling. Use 'uv run pytest' to verify.

# --- slm ---

In src/codomyrmex/slm/, review and improve Small Language Model management and fine-tuning. Add zero-mock tests for model loading, configuration, training loop, and evaluation metrics. Use 'uv run pytest' to verify.

# --- tokenizer ---

In src/codomyrmex/tokenizer/, review and improve tokenization utilities. Add zero-mock tests for BPE encoding/decoding, vocabulary management, special token handling, and token count estimation. Use 'uv run pytest' to verify.

# --- text_to_sql ---

In src/codomyrmex/text_to_sql/, review and improve natural language to SQL translation. Add zero-mock tests for query parsing, SQL generation, dialect handling, and query validation. Use 'uv run pytest' to verify.

# --- multimodal ---

In src/codomyrmex/multimodal/, review and improve unified vision/audio/image processing. Add zero-mock tests for modality detection, embedding alignment, cross-modal retrieval, and format conversion. Use 'uv run pytest' to verify.

# --- cost_management ---

In src/codomyrmex/cost_management/, review and improve cloud and API spend tracking. Add zero-mock tests for cost calculation, budget threshold detection, spend aggregation by provider, and alert generation. Use 'uv run pytest' to verify.

# --- observability_dashboard ---

In src/codomyrmex/observability_dashboard/ (or relevant module), review and improve unified monitoring dashboards. Add zero-mock tests for metric aggregation, dashboard configuration, and alert rule evaluation. Use 'uv run pytest' to verify.

# --- file_system ---

In src/codomyrmex/file_system/, review and improve file operations and directory management. Add zero-mock tests for file read/write, directory traversal, glob matching, and atomic file operations. Use 'uv run pytest' to verify.

# --- operating_system ---

In src/codomyrmex/operating_system/, review and improve platform-specific OS interactions. Add zero-mock tests for process management, signal handling, environment variable manipulation, and platform detection. Use 'uv run pytest' to verify.

# --- image ---

In src/codomyrmex/image/, review and improve image processing and generation. Add zero-mock tests for image loading, resizing, format conversion, and metadata extraction. Use 'uv run pytest' to verify.

# ============================================================================

# WAVE 7: SECURE COGNITIVE & SPECIALIZED LAYERS (20 agents)

# ============================================================================

# --- identity ---

In src/codomyrmex/identity/, review and improve 3-Tier persona management (Blue/Grey/Black) and bio-cognitive verification. Add zero-mock tests for persona creation, tier switching, verification challenges, and access control. Use 'uv run pytest' to verify.

# --- wallet ---

In src/codomyrmex/wallet/, review and improve self-custody key management and Natural Ritual Recovery. Add zero-mock tests for key generation, secure storage, recovery phrase validation, and transaction signing. Use 'uv run pytest' to verify.

# --- defense ---

In src/codomyrmex/defense/, review and improve active defense against cognitive attacks, context poisoning, and rabbit holes. Add zero-mock tests for attack detection, content filtering, and defense response generation. Use 'uv run pytest' to verify.

# --- market ---

In src/codomyrmex/market/, review and improve anonymous marketplace transactions and reverse auctions. Add zero-mock tests for order creation, price matching, auction lifecycle, and transaction verification. Use 'uv run pytest' to verify.

# --- privacy ---

In src/codomyrmex/privacy/, review and improve digital trace minimization and anonymous routing. Add zero-mock tests for crumb scrubbing, data anonymization, and routing path selection. Use 'uv run pytest' to verify.

# --- crypto ---

In src/codomyrmex/crypto/, review and improve cryptographic operations. Add zero-mock tests for hashing, symmetric encryption, asymmetric encryption, key derivation, digital signatures, and certificate validation. Use 'uv run pytest' to verify.

# --- encryption ---

In src/codomyrmex/encryption/, review and improve encryption implementations. Add zero-mock tests for AES encryption/decryption, key management, IV generation, and padding schemes. Use 'uv run pytest' to verify.

# --- security ---

In src/codomyrmex/security/, review and improve security scanning and vulnerability detection. Add zero-mock tests for SAST rule evaluation, dependency vulnerability checking, and security report generation. Use 'uv run pytest' to verify.
In src/codomyrmex/security/, review the STRIDE threat model analysis capabilities. Ensure comprehensive zero-mock tests for threat identification, risk scoring, and mitigation recommendation. Use 'uv run pytest' to verify.

# --- formal_verification ---

In src/codomyrmex/formal_verification/, review and improve formal verification methods. Add zero-mock tests for property specification, invariant checking, and counterexample generation. Use 'uv run pytest' to verify.

# --- dark ---

In src/codomyrmex/dark/, review and improve all methods. Ensure comprehensive zero-mock tests, proper documentation (README.md, SPEC.md, AGENTS.md), and correct type hints. Use 'uv run pytest' to verify.

# --- soul ---

In src/codomyrmex/soul/, review and improve all methods. Ensure comprehensive zero-mock tests, proper documentation (README.md, SPEC.md, AGENTS.md), and correct type hints. Use 'uv run pytest' to verify.

# ============================================================================

# WAVE 8: COMMUNICATION & INTEGRATION MODULES (20 agents)

# ============================================================================

# --- notification ---

In src/codomyrmex/networking/ and related notification logic, review and improve multi-channel dispatch (Email, Slack, SMS). Add zero-mock tests for message formatting, channel routing, delivery confirmation, and retry logic. Use 'uv run pytest' to verify.

# --- email ---

In src/codomyrmex/email/, review and improve email integration. Add zero-mock tests for email composition, template rendering, MIME handling, and address validation. Use 'uv run pytest' to verify.

# --- calendar_integration ---

In src/codomyrmex/calendar_integration/, review and improve calendar integration. Add zero-mock tests for event creation, recurrence rules, timezone conversion, and conflict detection. Use 'uv run pytest' to verify.

# --- collaboration ---

In src/codomyrmex/collaboration/, review and improve team collaboration features (agents, communication, coordination, protocols). Add zero-mock tests for message passing, coordination protocols, and consensus mechanisms. Use 'uv run pytest' to verify.

# --- networking ---

In src/codomyrmex/networking/, review and improve networking operations. Add zero-mock tests for HTTP client operations, connection pooling, retry logic, and timeout handling. Use 'uv run pytest' to verify.

# --- audio ---

In src/codomyrmex/audio/, review and improve audio processing capabilities. Add zero-mock tests for audio format detection, waveform analysis, transcription pipeline, and TTS integration. Use 'uv run pytest' to verify.

# --- video ---

In src/codomyrmex/video/, review and improve video processing capabilities. Add zero-mock tests for frame extraction, codec detection, metadata parsing, and thumbnail generation. Use 'uv run pytest' to verify.

# --- scrape ---

In src/codomyrmex/scrape/, review and improve web scraping capabilities. Add zero-mock tests for HTML parsing, data extraction, rate limiting, and content cleaning. Use 'uv run pytest' to verify.

# --- compression ---

In src/codomyrmex/compression/, review and improve compression operations. Add zero-mock tests for gzip/zlib/brotli compression and decompression, compression ratio calculation, and streaming compression. Use 'uv run pytest' to verify.

# --- edge_computing ---

In src/codomyrmex/edge_computing/, review and improve edge computing capabilities. Add zero-mock tests for edge deployment configuration, model optimization for edge, and resource constraint handling. Use 'uv run pytest' to verify.

# --- cloud ---

In src/codomyrmex/cloud/, review and improve cloud provider integrations. Add zero-mock tests for provider abstraction, resource management, and cloud API client operations. Use 'uv run pytest' to verify.

# --- ide ---

In src/codomyrmex/ide/, review and improve IDE integration capabilities. Add zero-mock tests for LSP communication, code action generation, and workspace management. Use 'uv run pytest' to verify.

# ============================================================================

# WAVE 9: DOMAIN-SPECIFIC & EMERGING MODULES (20 agents)

# ============================================================================

# --- bio_simulation ---

In src/codomyrmex/bio_simulation/, review and improve biological simulation capabilities. Add zero-mock tests for simulation setup, parameter configuration, result parsing, and visualization hooks. Use 'uv run pytest' to verify.

# --- finance ---

In src/codomyrmex/finance/, review and improve financial analysis capabilities. Add zero-mock tests for portfolio calculations, risk metrics, price analysis, and financial data formatting. Use 'uv run pytest' to verify.

# --- quantum ---

In src/codomyrmex/quantum/, review and improve quantum computing capabilities. Add zero-mock tests for qubit simulation, gate operations, circuit construction, and measurement simulation. Use 'uv run pytest' to verify.

# --- simulation ---

In src/codomyrmex/simulation/, review and improve general simulation frameworks. Add zero-mock tests for simulation lifecycle, step execution, metric collection, and state management. Use 'uv run pytest' to verify.

# --- meme ---

In src/codomyrmex/meme/, review and improve meme generation and processing capabilities. Add zero-mock tests covering all public methods with proper type hints. Use 'uv run pytest' to verify.

# --- relations ---

In src/codomyrmex/relations/, review and improve relationship management. Add zero-mock tests for entity relationship creation, graph traversal, and relationship querying. Use 'uv run pytest' to verify.

# --- fpf ---

In src/codomyrmex/fpf/, review and improve all methods. Ensure comprehensive zero-mock tests, proper documentation (README.md, SPEC.md, AGENTS.md), and correct type hints throughout. Use 'uv run pytest' to verify.

# --- dependency_injection ---

In src/codomyrmex/dependency_injection/, review and improve the DI container and registration. Add zero-mock tests for dependency registration, resolution, scope management, and circular dependency detection. Use 'uv run pytest' to verify.

# --- feature_flags ---

In src/codomyrmex/feature_flags/, review and improve the feature flag system (core, strategies, storage, evaluation, rollout). Add zero-mock tests for flag evaluation, percentage rollout, targeting rules, and A/B test assignment. Use 'uv run pytest' to verify.

# --- templating ---

In src/codomyrmex/templating/, review and improve template rendering. Add zero-mock tests for template loading, variable substitution, conditional rendering, loop constructs, and template inheritance. Use 'uv run pytest' to verify.

# --- languages ---

In src/codomyrmex/languages/, review and improve the multi-language support module. Ensure all language submodules (Python, JavaScript, TypeScript, Rust, Go, R, Elixir, Swift, PHP, C#) have comprehensive zero-mock tests and proper SPEC.md coverage. Use 'uv run pytest' to verify.

# ============================================================================

# WAVE 10: CROSS-CUTTING DOCUMENTATION IMPROVEMENTS (20 agents)

# ============================================================================

In docs/getting-started/, review and improve all getting started guides. Ensure installation instructions work on macOS, Linux, and WSL. Update code examples to use the current API. Fix any broken links.
In docs/agents/, review and improve all agent documentation. Ensure the multi-agent orchestration guide is accurate. Update examples to reflect the current Jules, Claude, Gemini, and Qwen integrations.
In docs/pai/, review and improve all PAI documentation. Ensure the architecture diagram matches the current thin-script orchestration pattern. Update the Trust Gateway and MCP integration documentation.
In docs/security/, review and improve all security documentation. Ensure STRIDE threat model, penetration testing guides, and key management audit docs are current and accurate.
In docs/deployment/, review and improve deployment documentation. Ensure cloud deployment guides, Docker workflows, and CI/CD pipeline docs are accurate and contain working examples.
In docs/reference/, review and improve all API reference documentation. Ensure every public module has an entry. Cross-reference with the actual module SPEC.md files for accuracy.
In docs/modules/, systematically verify that every one of the 127 source modules has a corresponding documentation page. Identify gaps and create stub entries for any missing module documentation.
In docs/integration/, review and improve all integration guides. Ensure third-party integration docs (MCP servers, LLM providers, Git services) are accurate and tested.
In docs/cognitive/, review and improve cognitive architecture documentation. Ensure the Cerebrum, defense, and identity module docs accurately reflect the current implementation.
In docs/development/, review and improve development workflow documentation. Ensure contribution guidelines, testing standards, and code review processes are documented and current.
In docs/bio/, review and improve biological simulation documentation. Ensure all bio-simulation modules have proper usage examples and API references.
In docs/agi/, review and improve AGI-related documentation. Ensure the evolutionary AI, neural architecture search, and multi-agent collaboration docs are current.
In docs/compliance/, review and improve compliance documentation. Ensure SBOM generation, license compliance, and audit trail documentation are accurate.
In docs/project/, review and improve project management documentation. Ensure roadmap, changelog, and versioning docs are current with v1.1.7.
In docs/project_orchestration/, review and improve project orchestration documentation. Ensure orchestrator, pipeline, and workflow management docs are accurate.
In docs/skills/, review and improve skills system documentation. Ensure all 15 Skill Domains are documented with correct module mappings.
In docs/examples/, review and improve example code and tutorials. Ensure all examples run successfully, use current APIs, and demonstrate best practices.
In docs/plans/, review and improve planning documentation. Ensure architecture decision records and implementation plans are current.

# ============================================================================

# WAVE 11: MCP TOOLS AUDIT & EXPANSION (15 agents)

# ============================================================================

Audit all mcp_tools.py files across src/codomyrmex/. List every module that is missing an mcp_tools.py file. For the first 5 missing modules alphabetically, create proper mcp_tools.py files with @mcp_tool decorators following the pattern in src/codomyrmex/auth/mcp_tools.py. Add zero-mock tests for each.
For modules ai_gateway, autograd, bio_simulation, build_synthesis, and calendar_integration: create mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules cloud, coding, collaboration, compression, and containerization: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules cost_management, crypto, dark, data_curation, and data_lineage: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules defense, deployment, distillation, distributed_training, and dpo: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules edge_computing, embodiment, encryption, evolutionary_ai, and feature_flags: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules feature_store, file_system, finance, formal_verification, and fpf: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules graph_rag, identity, ide, image, and interpretability: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules logit_processor, lora, market, matmul_kernel, and meme: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules model_merger, multimodal, nas, neural, and operating_system: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules peft, privacy, prompt_testing, quantization, and quantum: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules relations, rlhf, semantic_router, slm, and softmax_opt: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules soul, ssm, synthetic_data, text_to_sql, and tokenizer: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.
For modules tool_use, vector_store, video, and wallet: create or improve mcp_tools.py with 2-3 relevant MCP tools each. Follow the @mcp_tool decorator pattern. Add zero-mock tests. Use 'uv run pytest' to verify.

# ============================================================================

# WAVE 12: TYPE SAFETY & LINTING (10 agents)

# ============================================================================

Run 'uv run ty check src/codomyrmex/agents/' and fix any type errors. Add missing type annotations to all function signatures. Ensure all return types are annotated. Do not break any existing tests. Run 'uv run pytest src/codomyrmex/tests/unit/agents/' to verify.
Run 'uv run ty check src/codomyrmex/llm/' and fix any type errors. Add missing type annotations to all function signatures. Ensure all return types are annotated. Do not break any existing tests. Run 'uv run pytest' to verify.
Run 'uv run ty check src/codomyrmex/orchestrator/' and fix any type errors. Add missing type annotations to all function signatures. Ensure all return types are annotated. Do not break any existing tests. Run 'uv run pytest' to verify.
Run 'uv run ty check src/codomyrmex/model_context_protocol/' and fix any type errors. Add missing type annotations to all function signatures. Ensure all return types are annotated. Do not break any existing tests. Run 'uv run pytest' to verify.
Run 'uv run ty check src/codomyrmex/security/' and fix any type errors. Add missing type annotations to all function signatures. Ensure all return types are annotated. Do not break any existing tests. Run 'uv run pytest' to verify.
Run 'uv run ty check src/codomyrmex/cache/ src/codomyrmex/concurrency/ src/codomyrmex/events/' and fix any type errors in these three modules. Run 'uv run pytest' to verify.
Run 'uv run ty check src/codomyrmex/crypto/ src/codomyrmex/encryption/ src/codomyrmex/auth/' and fix any type errors in these three modules. Run 'uv run pytest' to verify.
Run 'uv run ty check src/codomyrmex/git_operations/ src/codomyrmex/tree_sitter/ src/codomyrmex/pattern_matching/' and fix any type errors in these three modules. Run 'uv run pytest' to verify.
Run 'uv run ty check src/codomyrmex/data_visualization/ src/codomyrmex/documents/ src/codomyrmex/serialization/' and fix any type errors in these three modules. Run 'uv run pytest' to verify.
Run 'uv run ty check src/codomyrmex/coding/ src/codomyrmex/api/ src/codomyrmex/cli/' and fix any type errors in these three modules. Run 'uv run pytest' to verify.

# ============================================================================

# WAVE 13: SCRIPTS DIRECTORY — Thin Orchestrator Verification (15 agents)

# ============================================================================

In scripts/agents/, review all agent scripts. Ensure every script follows the thin orchestrator pattern (delegating to src/codomyrmex). Fix any that contain business logic — move it to the proper module. Add missing docstrings and usage comments.
In scripts/agents/jules/, review and improve the mega_swarm_dispatcher.py and mega_swarm_harvester.py. Ensure proper error handling, progress reporting, and batch management. Add docstrings and usage examples.
In scripts/agents/qwen/, review and improve all Qwen agent scripts. Ensure they follow the thin orchestrator pattern and have proper error handling. Run 'uv run pytest' on any associated tests to verify.
In scripts/agents/claude/, review and improve all Claude agent scripts. Ensure they follow the thin orchestrator pattern and have proper error handling.
In scripts/agents/gemini/, review and improve all Gemini agent scripts. Ensure they follow the thin orchestrator pattern and have proper error handling.
In scripts/agents/deepseek/, review and improve all DeepSeek agent scripts. Ensure they follow the thin orchestrator pattern and have proper error handling.
In scripts/agents/evaluation/, review and improve all agent evaluation scripts. Ensure evaluation metrics are properly computed and results are formatted for comparison.
In scripts/agents/pooling/, review and improve all agent pooling scripts. Ensure connection pooling and resource management are robust.
In scripts/collaboration/, review all collaboration scripts. Ensure they follow the thin orchestrator pattern and properly delegate to src/codomyrmex/collaboration/.
In scripts/demos/, review and improve all demo scripts. Ensure every demo runs successfully, produces meaningful output, and demonstrates real module functionality.
Review all top-level scripts in the scripts/ directory (not in subdirectories). Ensure each follows the thin orchestrator pattern, has proper docstrings, and delegates to src/codomyrmex/ modules.
In scripts/agents/pai/, review and improve all PAI agent scripts. Ensure they follow the thin orchestrator pattern and properly integrate with the PAI PM server.
In scripts/agents/o1/, review and improve all O1 agent scripts. Ensure they follow the thin orchestrator pattern and have proper error handling.
In scripts/agents/history/, review and improve all agent history scripts. Ensure they properly track and report agent session history.

# ============================================================================

# WAVE 14: TEST INFRASTRUCTURE & COVERAGE (15 agents)

# ============================================================================

In src/codomyrmex/tests/, audit the test directory structure. Ensure every module in src/codomyrmex/ has a corresponding test directory under src/codomyrmex/tests/unit/. Create missing test directories and add __init__.py files.
In src/codomyrmex/testing/, review and improve the testing utilities module. Ensure test fixtures, helpers, and assertions are well-documented and have their own zero-mock tests. Use 'uv run pytest' to verify.
Review src/codomyrmex/conftest.py and all conftest.py files throughout the test directories. Ensure fixtures are properly scoped, documented, and not duplicated. Remove any unused fixtures.
Run 'uv run pytest --collect-only src/codomyrmex/tests/unit/cache/' and verify that cache tests are comprehensive. Add missing tests for cache eviction, concurrent access, and serialization. Aim for mutation testing readiness (v1.1.7 target).
Run 'uv run pytest --collect-only src/codomyrmex/tests/unit/concurrency/' and verify that concurrency tests are comprehensive. Add missing tests for thread safety, deadlock detection, and pool exhaustion. Aim for mutation testing readiness (v1.1.7 target).
Run 'uv run pytest --collect-only src/codomyrmex/tests/unit/events/' and verify that events tests are comprehensive. Add missing tests for event ordering, handler priority, and event cancellation. Aim for mutation testing readiness (v1.1.7 target).
Run 'uv run pytest --collect-only' across the entire test suite. Identify the 10 module test directories with the fewest tests relative to the module size. For the top 3, add at least 5 new zero-mock tests each.
Review all conftest.py files in the repository. Ensure none contain mock objects or mock fixtures. Replace any remaining mock-based fixtures with real InMemory or Test implementations per the Zero-Mock policy.
Audit the repository for any remaining uses of unittest.mock, MagicMock, or patch() in test files. List all occurrences. Replace each with a real functional alternative following the Zero-Mock policy. Use 'uv run pytest' to verify.
In pyproject.toml, review the [tool.pytest] and [tool.coverage] configuration. Ensure coverage source includes all 128 modules. Verify the fail_under gate is set correctly. Audit the mutmut configuration for the v1.1.7 expansion targets.
Review the pytest markers defined in pyproject.toml. Ensure all custom markers (slow, integration, flaky, etc.) are properly registered and used consistently across the test suite.
In src/codomyrmex/tests/integration/, review and improve all integration tests. Ensure they test real cross-module interactions without mocking. Add missing integration tests for critical module boundaries.
Run 'uv run pytest -x --tb=short' to identify and fix the first failing test. Then run the full suite with 'uv run pytest --tb=short' and report the results (pass/fail/skip counts).
Review the GitHub Actions CI workflow (.github/workflows/ci.yml). Ensure the test matrix covers Python 3.11 and 3.12. Verify cacheing, timeouts, and artifact upload are properly configured.
Add pytest-rerunfailures configuration as specified in TODO.md v1.1.7. Apply @pytest.mark.flaky(reruns=2) to any tests identified as flaky in CI. Document which tests are marked flaky and why.

# ============================================================================

# WAVE 15: RELEASE & PROJECT HEALTH (10 agents)

# ============================================================================

Review pyproject.toml for overall project health. Ensure all dependencies are up to date, extras are properly defined, version is correct (1.1.7), and build backend configuration is optimal for uv_build.
Review all AGENTS.md files across the repository (root and module-level). Ensure each accurately describes how AI agents should interact with that module. Fix any outdated references or missing capability descriptions.
Review the root README.md. Ensure badges are current, installation instructions work, and the project description accurately reflects the v1.1.7 state with 128 modules and 21,000+ tests.
Review CLAUDE.md and ensure it accurately describes the repository structure, development commands (uv run pytest, uv run ruff, uv run ty), and the Zero-Mock policy for Claude Code integration.
Review .github/workflows/ for all workflow files. Ensure security scanning (Semgrep), CI testing, dependency management, and release automation are all properly configured and reference correct versions.
Review and improve the CHANGELOG.md or release documentation. Ensure all changes from v1.1.5 through v1.1.7 are properly documented with categorized entries (Added, Changed, Fixed, Removed).
In src/codomyrmex/__init__.py, review the package initialization. Ensure __version__ matches pyproject.toml, all public APIs are properly exported, and lazy imports are configured for performance.
Review all .gitignore, .dockerignore, and similar filter files. Ensure they properly exclude build artifacts, caches, and sensitive files while including necessary configuration files.
Review the justfile (or Makefile) at the repository root. Ensure all common development commands (test, lint, format, type-check, build, docs) are defined and work correctly.
Review start_here.sh and ensure it properly orchestrates all entry points. Verify it handles error cases, provides helpful output, and correctly delegates to the scripts directory.

# ============================================================================

# WAVE 16: DEEPER MODULE INTERNALS — Docstrings, __init__.py, SKILL.md (20 agents)

# ============================================================================

In src/codomyrmex/website/, review and improve the full-stack dashboard including data_provider.py, WebSocket server, and frontend assets. Add zero-mock tests for data aggregation, endpoint handlers, and WebSocket message formatting. Use 'uv run pytest' to verify.
In src/codomyrmex/website/, audit the frontend JavaScript for the 15-tab SPA dashboard. Ensure all tabs load correctly, WebSocket reconnection logic works, and all API endpoints return valid JSON. Document any issues found.
In src/codomyrmex/git_analysis/, review and improve the git analysis capabilities. Add zero-mock tests for commit history analysis, contributor statistics, code churn metrics, and file change frequency tracking. Use 'uv run pytest' to verify.
In src/codomyrmex/git_analysis/, review submodule organization and ensure proper SPEC.md, README.md, AGENTS.md documentation. Fix any import issues and ensure all public APIs are properly exported.
In src/codomyrmex/release/, review and improve the release automation module. Add zero-mock tests for version bumping, changelog generation, release note formatting, and GitHub release API interaction. Use 'uv run pytest' to verify.
In src/codomyrmex/maintenance/, review and improve the maintenance module. Add zero-mock tests for dependency checking, stale code detection, migration planning, and health report generation. Use 'uv run pytest' to verify.
In src/codomyrmex/docs_gen/, review and improve the documentation generation module. Add zero-mock tests for API doc generation, markdown rendering, and cross-reference validation. Use 'uv run pytest' to verify.
In src/codomyrmex/documentation/, review and improve the documentation module. Ensure all documentation templates, generators, and validators have zero-mock tests. Use 'uv run pytest' to verify.
In src/codomyrmex/examples/, review all example scripts. Ensure each example runs independently, demonstrates real functionality, and follows the thin orchestrator pattern. Fix any broken imports.
In src/codomyrmex/demos/, review all demo scripts. Ensure each demo produces meaningful output and uses real module functionality, not placeholder logic. Fix any broken imports.
In src/codomyrmex/aider/, review and improve the Aider integration module. Add zero-mock tests for code editing commands, diff generation, and session management. Use 'uv run pytest' to verify.
In src/codomyrmex/ml_pipeline/, review and improve the ML pipeline module. Add zero-mock tests for pipeline construction, step execution, and result collection. Use 'uv run pytest' to verify.
In src/codomyrmex/networks/, review and improve the networks module. Add zero-mock tests for network topology construction, node communication, and message routing. Use 'uv run pytest' to verify.
In src/codomyrmex/config_audits/, review and improve the configuration audit module. Add zero-mock tests for config validation rules, compliance checking, and audit report generation. Use 'uv run pytest' to verify.
In src/codomyrmex/config_monitoring/, review and improve the configuration monitoring module. Add zero-mock tests for config change detection, drift alerting, and configuration snapshot comparison. Use 'uv run pytest' to verify.
In src/codomyrmex/container_optimization/, review and improve the container optimization module. Add zero-mock tests for image size analysis, layer optimization suggestions, and build cache improvement. Use 'uv run pytest' to verify.
In src/codomyrmex/distributed_training/, review and improve the distributed training module. Add zero-mock tests for FSDP configuration, gradient synchronization, and shard management. Use 'uv run pytest' to verify.
In src/codomyrmex/migration/, review and add a migration module if not present, for cross-provider data and service transitions. Add zero-mock tests for migration plan generation and data transformation validation. Use 'uv run pytest' to verify.
In src/codomyrmex/physical_management/, review and improve the physical management module. Add zero-mock tests for device inventory, hardware monitoring, and physical resource allocation. Use 'uv run pytest' to verify.
In src/codomyrmex/workflow_testing/ (or relevant test module), review and improve end-to-end multi-step validation. Add zero-mock tests for workflow scenario execution, step assertion, and failure recovery. Use 'uv run pytest' to verify.

# ============================================================================

# WAVE 17: __init__.py EXPORTS & SKILL.md VERIFICATION (15 agents)

# ============================================================================

Audit all __init__.py files in src/codomyrmex/*/. Ensure each module's __init__.py exports all public classes, functions, and constants listed in its SPEC.md. Add __all__ lists where missing. Fix any circular import issues.
For modules concurrency, events, logging_monitoring, performance, and system_discovery: verify that SKILL.md exists and accurately maps to the correct Skill Domain. Fix any incorrect domain assignments.
For modules agents, llm, git_operations, model_context_protocol, and pattern_matching: verify that SKILL.md exists and accurately maps to the correct Skill Domain. Fix any incorrect domain assignments.
For modules cache, database_management, documents, data_visualization, and serialization: verify that SKILL.md exists and accurately maps to the correct Skill Domain. Fix any incorrect domain assignments.
For modules orchestrator, logistics, ci_cd_automation, coding, and deployment: verify that SKILL.md exists and accurately maps to the correct Skill Domain. Fix any incorrect domain assignments.
For modules cerebrum, spatial, embodiment, evolutionary_ai, and graph_rag: verify that SKILL.md exists and accurately maps to the correct Skill Domain. Fix any incorrect domain assignments.
For modules identity, wallet, defense, market, and privacy: verify that SKILL.md exists and accurately maps to the correct Skill Domain. Fix any incorrect domain assignments.
For modules crypto, encryption, security, auth, and formal_verification: verify that SKILL.md exists and accurately maps to the correct Skill Domain. Fix any incorrect domain assignments.
Audit all py.typed marker files across src/codomyrmex/*/. Ensure every module directory contains a py.typed file for PEP 561 compliance. Create any missing markers with the standard content.
Review src/codomyrmex/SPEC.md for accuracy. Ensure all 128 modules are listed with correct purpose statements, dependency maps, and public API summaries. Cross-reference against the actual module contents.
Review src/codomyrmex/INDEX.md for accuracy. Ensure the module index is complete, alphabetically sorted, and links to each module's README.md. Fix any broken links or missing entries.
Review src/codomyrmex/README.md for accuracy. Ensure it provides a clear overview of the package, installation instructions, and quick-start examples that work with the current API.
Review src/codomyrmex/AGENTS.md for accuracy. Ensure it provides comprehensive guidance for AI agents on how to interact with the package, including available MCP tools, testing commands, and coding standards.
In src/codomyrmex/pai_pm/, review and improve the PAI PM server module. Add zero-mock tests for API endpoint handlers, WebSocket management, and data aggregation. Use 'uv run pytest' to verify.
In src/codomyrmex/skills/, audit the skills module structure. Ensure all 127+ module skill files are present, properly formatted, and map to the correct Skill Domains. Report any gaps.

# ============================================================================

# WAVE 18: ADVANCED v1.1.7 TARGETS & EDGE CASES (14 agents)

# ============================================================================

Add hypothesis-based property tests to src/codomyrmex/serialization/. Write @given decorators testing JSON encode/decode round-trips, YAML serialization invariants, and schema validation with random data. This is a v1.1.7 priority. Use 'uv run pytest' to verify.
In pyproject.toml, expand the [tool.mutmut] targets list from 6 to 12 modules: add cache/core.py, concurrency/core.py, events/core.py, serialization/core.py, validation/core.py, and auth/core.py. Verify mutmut runs correctly on each target.
Review and improve the GitHub Actions security workflow (.github/workflows/security.yml). Ensure Semgrep SARIF upload works, CodeQL scanning is configured, and dependency review actions are current.
Audit all .github/ configuration files (dependabot.yml, CODEOWNERS, FUNDING.yml, issue templates, PR templates). Ensure they are current, properly configured, and follow best practices.
Run 'uv run ruff check src/ --statistics' and identify the top 10 remaining violation categories. For the top 3 most common, determine if they are auto-fixable and apply fixes where safe. Report results.
Run 'uv run ruff format --check src/' and identify any files that are not properly formatted. Apply formatting fixes. Ensure no test failures result from the formatting changes.
Review mkdocs.yml for documentation site configuration. Ensure all navigation entries point to existing files, plugins are properly configured, and the build succeeds without warnings.
In src/codomyrmex/model_context_protocol/, review the tool_decorator module. Ensure the @mcp_tool decorator properly generates JSON Schema from type hints, handles Optional parameters, and supports docstring-based descriptions. Add edge case tests.
Audit cross-module imports throughout src/codomyrmex/. Identify any circular dependencies and refactor to resolve them. Ensure lazy imports are used for heavy dependencies. Document the dependency graph.
Review the uv.lock file and pyproject.toml dependency specifications. Ensure all pinned versions are recent, security-patched, and compatible. Flag any dependencies that haven't been updated in 6+ months.
In src/codomyrmex/model_context_protocol/server.py, review the MCP server implementation. Ensure proper error handling, connection management, and tool dispatch. Add zero-mock tests for server lifecycle.
Create a comprehensive test for the thin orchestrator pattern compliance. Write a script that scans all files in scripts/ and verifies each is under 50 lines of business logic, delegates to src/codomyrmex, and has a proper docstring.
Review and improve the project's CONTRIBUTING.md. Ensure it documents the development setup, testing requirements (zero-mock policy), code review process, and PR checklist.
Audit all README.md files across docs/ subdirectories. Ensure each provides navigation, purpose description, and links to related documentation. Fix any broken links or outdated references.
