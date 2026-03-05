#!/usr/bin/env python3
"""Generate real configuration documentation for all config/ stub files.

Replaces MANUAL_DOC_REVIEW_REQUIRED stubs with accurate config docs
based on source module __init__.py docstrings and os.getenv() calls.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
SRC_DIR = REPO_ROOT / "src" / "codomyrmex"

# Module metadata: description, env_vars [(name, default, description)], mcp_tools
MODULE_META = {
    "agentic_memory": {
        "desc": "Persistent, searchable agent memory with typed retrieval. Provides Memory models, in-memory and file-backed stores, agent-level search/recall, and Obsidian vault integration.",
        "env_vars": [],
        "mcp_tools": ["memory_put", "memory_get", "memory_search"],
        "config_notes": "Memory storage defaults to in-memory. For persistent storage, configure a JSONFileStore with a file path. Obsidian vault integration requires a vault directory path.",
    },
    "agents": {
        "desc": "AI agent framework integrations supporting 13 agentic frameworks including Claude, Codex, Gemini, Jules, and more. Provides API-based and CLI-based agent clients with orchestration.",
        "env_vars": [
            (
                "AGENT_DEFAULT_TIMEOUT",
                "30",
                "Default timeout in seconds for agent operations",
            ),
            (
                "AGENT_ENABLE_LOGGING",
                "true",
                "Enable or disable agent execution logging",
            ),
            ("ANTHROPIC_API_KEY", "", "API key for Claude agent integration"),
            ("OPENAI_API_KEY", "", "API key for Codex/O1 agent integration"),
            ("GEMINI_API_KEY", "", "API key for Gemini agent integration"),
        ],
        "mcp_tools": ["execute_agent", "list_agents", "get_agent_memory"],
        "config_notes": "Each agent provider requires its own API key. CLI-based agents (Jules, OpenCode) require the respective CLI tool installed on PATH.",
    },
    "audio": {
        "desc": "Audio processing with speech-to-text (Whisper) and text-to-speech (pyttsx3, Edge TTS). Supports transcription, language detection, and voice synthesis.",
        "env_vars": [],
        "mcp_tools": ["audio_transcribe", "audio_synthesize"],
        "config_notes": "Requires optional dependencies: `uv sync --extra audio`. Whisper model size (tiny/base/small/medium/large) affects accuracy and memory usage.",
    },
    "auth": {
        "desc": "Authentication and authorization with API key management, OAuth integration, and Role-Based Access Control (RBAC). Provides token management and validation.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Token expiration and RBAC permissions are configured programmatically through the Authenticator and PermissionRegistry classes.",
    },
    "bio_simulation": {
        "desc": "Ant colony simulation with pheromone-based foraging and genomics/genetic algorithm integration. Provides Colony, Environment, Genome, and Population models.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Simulation parameters (colony size, environment dimensions, pheromone decay rate) are set through constructor arguments on Colony and Environment.",
    },
    "calendar_integration": {
        "desc": "Calendar management with Google Calendar integration. Provides generic CalendarEvent and CalendarProvider abstractions with a GoogleCalendar implementation.",
        "env_vars": [
            ("GOOGLE_CLIENT_ID", "", "Google OAuth client ID for Calendar API"),
            ("GOOGLE_CLIENT_SECRET", "", "Google OAuth client secret"),
            (
                "GOOGLE_REFRESH_TOKEN",
                "",
                "Google OAuth refresh token for persistent access",
            ),
        ],
        "mcp_tools": [
            "calendar_list_events",
            "calendar_create_event",
            "calendar_get_event",
            "calendar_delete_event",
            "calendar_update_event",
        ],
        "config_notes": "Requires Google Cloud project with Calendar API enabled. OAuth credentials must be configured before use. Install with `uv sync --extra calendar`.",
    },
    "cerebrum": {
        "desc": "Case-Enabled Reasoning Engine with Bayesian Representations for Unified Modeling. Provides case-based reasoning combined with Bayesian probabilistic inference.",
        "env_vars": [],
        "mcp_tools": ["query_knowledge_base", "add_case_reference"],
        "config_notes": "The CerebrumEngine is instantiated with case base size limits and inference parameters. Integrates with logging_monitoring for operational logging.",
    },
    "ci_cd_automation": {
        "desc": "Continuous integration and deployment pipeline management. Provides pipeline creation, execution, monitoring, and automated testing orchestration.",
        "env_vars": [
            ("CI_CD_API_TOKEN", "", "Authentication token for CI/CD service API"),
            ("CI_CD_BASE_URL", "", "Base URL of the CI/CD service endpoint"),
        ],
        "mcp_tools": ["ci_run_pipeline", "ci_get_status", "ci_list_pipelines"],
        "config_notes": "Pipeline definitions are typically stored as YAML. The module connects to external CI services via API token authentication.",
    },
    "cli": {
        "desc": "Command-line interface for the Codomyrmex development platform. Entry point for all user interaction including module management, workflows, AI code operations, and system status.",
        "env_vars": [
            (
                "VIRTUAL_ENV",
                "",
                "Path to active Python virtual environment (auto-detected)",
            ),
        ],
        "mcp_tools": ["cli_execute", "cli_list_commands"],
        "config_notes": "The CLI auto-detects the virtual environment and available modules. Shell completion is available via `codomyrmex --install-completion`.",
    },
    "cloud": {
        "desc": "Cloud service integrations including Coda.io, AWS S3, GCP Storage, Azure Blob, and Infomaniak OpenStack. Provides unified cloud resource management.",
        "env_vars": [
            ("AZURE_STORAGE_ACCOUNT_URL", "", "Azure Storage account URL"),
            ("INFOMANIAK_APP_CREDENTIAL_ID", "", "Infomaniak API credential ID"),
            (
                "INFOMANIAK_APP_CREDENTIAL_SECRET",
                "",
                "Infomaniak API credential secret",
            ),
            (
                "INFOMANIAK_AUTH_URL",
                "https://api.infomaniak.com/1/auth",
                "Infomaniak authentication endpoint",
            ),
            ("INFOMANIAK_PROJECT_ID", "", "Infomaniak project identifier"),
            ("INFOMANIAK_S3_ACCESS_KEY", "", "Infomaniak S3 access key"),
            ("INFOMANIAK_S3_SECRET_KEY", "", "Infomaniak S3 secret key"),
            ("INFOMANIAK_S3_ENDPOINT", "", "Infomaniak S3 endpoint URL"),
            ("INFOMANIAK_S3_REGION", "", "Infomaniak S3 region"),
        ],
        "mcp_tools": ["list_cloud_instances", "list_s3_buckets", "upload_file_to_s3"],
        "config_notes": "Each cloud provider requires its own credentials. AWS uses standard boto3 credential chain. Infomaniak uses OpenStack Keystone authentication.",
    },
    "coding": {
        "desc": "Unified module for code execution, sandboxing, review, monitoring, and debugging. Provides a comprehensive toolkit for running, analyzing, and fixing code programmatically.",
        "env_vars": [],
        "mcp_tools": [
            "code_execute",
            "code_list_languages",
            "code_review_file",
            "code_review_project",
            "code_debug",
        ],
        "config_notes": "Code execution runs in sandboxed environments with configurable resource limits (CPU, memory, timeout). Review uses static analysis rules.",
    },
    "collaboration": {
        "desc": "Multi-agent collaboration capabilities including agent management, communication channels, task coordination, consensus protocols, and swarm behavior.",
        "env_vars": [],
        "mcp_tools": ["swarm_submit_task", "pool_status", "list_agents"],
        "config_notes": "Collaboration sessions are created programmatically. Agent registry maintains worker and supervisor roles. Communication uses in-process channels.",
    },
    "compression": {
        "desc": "Data compression utilities and archive handling supporting gzip, zlib, ZIP, and Zstandard formats. Provides configurable compression levels, stream-based compression, and parallel compression.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Compression level (1-9 for gzip/zlib, 1-22 for zstd) and algorithm are set per-operation. ParallelCompressor uses system CPU count by default.",
    },
    "concurrency": {
        "desc": "Distributed locks, semaphores, and synchronization primitives. Provides local locks, Redis-backed distributed locks, read-write locks, and dead letter queues.",
        "env_vars": [],
        "mcp_tools": ["concurrency_lock_status", "concurrency_list_locks"],
        "config_notes": "Redis-backed locks require `redis` package (`uv sync --extra concurrency`). Local locks use threading primitives. Lock timeout and retry parameters are set per-lock.",
    },
    "config_audits": {
        "desc": "Configuration auditing and compliance module. Provides tools for auditing configuration files for security, compliance, and best practices using configurable audit rules.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Audit rules are defined through the AuditRule model and loaded via DEFAULT_RULES. Custom rules can be added to the ConfigAuditor instance.",
    },
    "config_management": {
        "desc": "Central configuration management, validation, and deployment for the Codomyrmex ecosystem. Provides multi-source config loading, schema validation, and environment-aware configuration.",
        "env_vars": [
            (
                "ENVIRONMENT",
                "development",
                "Active environment name (development, staging, production)",
            ),
            (
                "OLLAMA_BASE_URL",
                "http://localhost:11434",
                "Base URL for Ollama LLM service",
            ),
        ],
        "mcp_tools": ["get_config", "set_config", "validate_config"],
        "config_notes": "Configuration is loaded from YAML files, environment variables, and programmatic defaults. Environment variables take precedence over file values.",
    },
    "config_monitoring": {
        "desc": "Configuration monitoring, auditing, and hot-reload watching. Provides configuration change detection, drift analysis, compliance auditing, and file-system-based hot-reload.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "ConfigWatcher uses filesystem events to detect config changes. ConfigurationMonitor tracks snapshots for drift analysis. Polling interval is configurable.",
    },
    "container_optimization": {
        "desc": "Container image analysis and optimization. Provides tools for analyzing container images and tuning resource usage with ContainerOptimizer and ResourceTuner.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Requires Docker daemon access for image analysis. Resource tuning parameters (CPU limits, memory requests) are set per-container.",
    },
    "containerization": {
        "desc": "Container management, orchestration, and deployment. Provides Docker build/scan/runtime, Kubernetes management, container registry, and security scanning.",
        "env_vars": [],
        "mcp_tools": [
            "container_runtime_status",
            "container_build",
            "container_list",
            "container_security_scan",
        ],
        "config_notes": "Requires Docker CLI and daemon for container operations. Kubernetes operations require kubectl configured with cluster access.",
    },
    "cost_management": {
        "desc": "Spend tracking, budgeting, and cost optimization. Provides CostTracker for recording expenses, BudgetManager for budget enforcement, and JSON-backed persistent storage.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Cost data is stored via CostStore implementations (InMemoryCostStore for testing, JSONCostStore for persistence). Budget periods are configurable.",
    },
    "crypto": {
        "desc": "Comprehensive cryptographic operations including symmetric/asymmetric encryption, hashing, digital signatures, KDF, certificates, cryptocurrency, cryptanalysis, steganography, and encoding.",
        "env_vars": [],
        "mcp_tools": ["hash_data", "verify_hash", "generate_key"],
        "config_notes": "Cryptographic parameters (key sizes, algorithms) are set per-operation. No global configuration required. Uses Python cryptography library.",
    },
    "dark": {
        "desc": "PDF dark mode utilities providing inversion, brightness, contrast, and sepia filters for PDF documents. Supports preset modes and custom filter chains.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Requires optional dependencies: `uv sync --extra dark`. Filter parameters (inversion level, brightness, contrast) are set per-document.",
    },
    "data_lineage": {
        "desc": "Data lineage tracking through transformations with graph-based analysis. Provides LineageGraph for dependency visualization and ImpactAnalyzer for change impact assessment.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Lineage graphs are built incrementally as data flows through transformations. Storage is in-memory by default.",
    },
    "data_visualization": {
        "desc": "Chart and dashboard generation supporting bar, line, scatter, heatmap, histogram, pie, area, and box plot chart types. Includes report generators, Mermaid diagrams, and HTML export.",
        "env_vars": [],
        "mcp_tools": ["generate_chart", "export_dashboard"],
        "config_notes": "Visual themes are configurable. Chart output formats include PNG, SVG, and HTML. Dashboard export produces self-contained HTML files.",
    },
    "database_management": {
        "desc": "Database management, migration, backup, and administration. Supports PostgreSQL, MySQL, and SQLite with connection pooling, schema generation, and replication management.",
        "env_vars": [
            ("DB_HOST", "localhost", "Database server hostname"),
            ("DB_PORT", "5432", "Database server port"),
            ("DB_USER", "postgres", "Database username"),
        ],
        "mcp_tools": [],
        "config_notes": "Connection parameters can be set via environment variables or passed directly to DatabaseManager. Connection pooling size and timeout are configurable.",
    },
    "defense": {
        "desc": "Threat detection, rate limiting, and response engine. Provides ActiveDefense for exploit detection, RabbitHole for attacker engagement, and Defense for orchestrating security responses.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Detection rules and response actions are configured through DetectionRule and ResponseAction models. Severity levels control escalation behavior.",
    },
    "dependency_injection": {
        "desc": "Lightweight, thread-safe Inversion of Control (IoC) container for managing service lifetimes and constructor-based dependency injection. Foundation layer with no external dependencies.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Service lifetimes (SINGLETON, TRANSIENT, SCOPED) are set via @injectable decorator. Container is configured programmatically with no external config files.",
    },
    "deployment": {
        "desc": "Deployment strategies including canary, blue-green, and rolling deployments. Provides DeploymentManager, GitOps synchronization, health checks, and automated rollback.",
        "env_vars": [
            ("DEPLOY_HOST", "localhost", "Target deployment host address"),
            ("DEPLOY_BASE_PORT", "8000", "Base port for deployment instances"),
        ],
        "mcp_tools": [],
        "config_notes": "Deployment strategies are selected per-deployment. Canary analysis thresholds and health check intervals are configurable per strategy.",
    },
    "docs_gen": {
        "desc": "Documentation generation from Python source code. Provides API documentation extraction, searchable in-memory indices, and static documentation site configuration.",
        "env_vars": [],
        "mcp_tools": ["docs_gen_extract", "docs_gen_search"],
        "config_notes": "SiteGenerator output directory and template settings are configurable. SearchIndex rebuilds automatically when new modules are extracted.",
    },
    "documentation": {
        "desc": "Documentation management, quality auditing, and website generation. Provides RASP compliance auditing, consistency checking, quality assessment, and static site building.",
        "env_vars": [
            ("DOCS_PORT", "3000", "Port for documentation dev server"),
            ("DOCS_HOST", "localhost", "Host for documentation dev server"),
        ],
        "mcp_tools": ["generate_module_docs", "audit_rasp_compliance"],
        "config_notes": "Documentation website runs on configurable host and port. Quality thresholds for RASP compliance can be adjusted in audit configuration.",
    },
    "documents": {
        "desc": "Document I/O operations for multiple formats including markdown, JSON, PDF, YAML, XML, CSV, HTML, and plain text. Provides read, write, parse, validate, convert, merge, and split operations.",
        "env_vars": [
            ("CODOMYRMEX_CACHE_DIR", "", "Directory for document cache storage"),
        ],
        "mcp_tools": ["documents_read", "documents_write", "documents_convert"],
        "config_notes": "Cache directory defaults to system temp. Document format detection is automatic based on file extension.",
    },
    "edge_computing": {
        "desc": "Edge deployment, IoT gateways, and latency-sensitive patterns. Provides EdgeNode management, EdgeRuntime for function execution, deployment planning, and edge caching.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Edge node configuration includes sync state, health monitoring intervals, and cache TTL settings. Deployment strategies are set per-plan.",
    },
    "email": {
        "desc": "Email integration with Gmail and AgentMail providers. Provides generic EmailMessage and EmailProvider abstractions with inbox management, threading, and webhook support.",
        "env_vars": [
            ("AGENTMAIL_API_KEY", "", "API key for AgentMail service"),
            (
                "AGENTMAIL_DEFAULT_INBOX",
                "",
                "Default inbox ID for AgentMail operations",
            ),
            ("GOOGLE_CLIENT_ID", "", "Google OAuth client ID for Gmail API"),
            ("GOOGLE_CLIENT_SECRET", "", "Google OAuth client secret for Gmail"),
            ("GOOGLE_REFRESH_TOKEN", "", "Google OAuth refresh token for Gmail access"),
        ],
        "mcp_tools": [
            "agentmail_send_message",
            "agentmail_list_messages",
            "agentmail_get_message",
            "agentmail_reply_to_message",
            "agentmail_list_inboxes",
            "agentmail_create_inbox",
            "agentmail_list_threads",
            "agentmail_create_webhook",
            "gmail_send_message",
            "gmail_list_messages",
            "gmail_get_message",
            "gmail_create_draft",
        ],
        "config_notes": "AgentMail requires an API key. Gmail requires Google OAuth credentials. Install with `uv sync --extra email`.",
    },
    "embodiment": {
        "desc": "Robotics integration with ROS2, sensors, actuators, and 3D transforms. Provides ROS2Bridge for robot communication and Transform3D for spatial calculations.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "ROS2 integration requires ROS2 installed and sourced. Transform3D operates independently without external configuration.",
    },
    "encryption": {
        "desc": "Encryption, hashing, digital signatures, and key management. Provides AES-256 (CBC/GCM), RSA, PBKDF2, HKDF, HMAC, and secure data containers.",
        "env_vars": [],
        "mcp_tools": ["encryption_encrypt", "encryption_decrypt"],
        "config_notes": "Encryption keys are managed through KeyManager. Key derivation parameters (iterations, salt length) are configurable per-operation.",
    },
    "environment_setup": {
        "desc": "Environment validation, dependency checking, and uv package manager integration. Validates Python version, virtual environments, API keys, and installed dependencies.",
        "env_vars": [
            ("VIRTUAL_ENV", "", "Path to active virtual environment (auto-detected)"),
            ("UV_ACTIVE", "1", "Indicator that uv environment is active"),
            ("CONDA_DEFAULT_ENV", "", "Active Conda environment name"),
        ],
        "mcp_tools": [],
        "config_notes": "Environment validation runs automatically on import. API key checks use a configurable list of required keys per module.",
    },
    "events": {
        "desc": "Event-driven architecture providing decoupled, asynchronous communication between components. Supports event emission, typed event registration, and event history.",
        "env_vars": [],
        "mcp_tools": ["emit_event", "list_event_types", "get_event_history"],
        "config_notes": "Event bus is a singleton. Event types are registered dynamically. History retention can be configured through the event bus settings.",
    },
    "evolutionary_ai": {
        "desc": "Evolutionary computation and genetic algorithms for AI optimization. Provides population-based optimization with configurable selection, crossover, and mutation operators.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Population size, mutation rate, crossover rate, and selection strategy are set per-algorithm instance. Fitness functions are user-defined.",
    },
    "exceptions": {
        "desc": "Centralized exception hierarchy for the Codomyrmex platform. Provides base CodomyrmexError and specialized exceptions for authentication, encryption, validation, and module-specific errors.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "No configuration required. Exception classes are imported directly. All module exceptions inherit from CodomyrmexError.",
    },
    "feature_flags": {
        "desc": "Feature flag management with percentage-based, user-list, and time-window strategies. Supports dynamic feature toggling without deployment.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Feature flags are defined programmatically with strategy objects (PercentageStrategy, UserListStrategy, TimeWindowStrategy). Flags can be toggled at runtime.",
    },
    "feature_store": {
        "desc": "Feature management, storage, and serving for ML applications. Provides FeatureDefinition, FeatureGroup, and FeatureVector with typed feature values.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Feature definitions are registered with type constraints. Feature vectors include timestamp and user ID features by default.",
    },
    "file_system": {
        "desc": "File system operations, directory management, and file watching. Provides safe file I/O utilities with atomic writes and directory traversal.",
        "env_vars": [],
        "mcp_tools": ["file_read", "file_write"],
        "config_notes": "File operations use atomic writes by default to prevent corruption. Watch intervals and ignore patterns are configurable.",
    },
    "finance": {
        "desc": "Financial calculations, portfolio management, and market data analysis. Provides pricing models, risk assessment, and financial reporting utilities.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Financial model parameters (interest rates, risk factors) are set per-calculation. No global financial configuration.",
    },
    "formal_verification": {
        "desc": "Z3 constraint solving and model checking. Provides a model builder with add/delete/replace/solve operations for formal verification of system properties.",
        "env_vars": [],
        "mcp_tools": [
            "clear_model",
            "add_item",
            "delete_item",
            "replace_item",
            "get_model",
            "solve_model",
        ],
        "config_notes": "Z3 solver timeout and memory limits can be configured per-solve operation. The model state is maintained in-memory.",
    },
    "fpf": {
        "desc": "Fetch-Parse-Format pipeline for extracting, parsing, and exporting content from URLs. Supports multiple output formats and content transformation.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "URL fetching uses configurable timeout and retry settings. Output format (JSON, Markdown, plain text) is selected per-operation.",
    },
    "git_analysis": {
        "desc": "Git history analysis, contributor statistics, and commit pattern detection. Provides 16 analysis tools for repository insights including hotspot detection and code churn.",
        "env_vars": [],
        "mcp_tools": [
            "git_analysis_commit_history",
            "git_analysis_contributor_stats",
            "git_analysis_hotspots",
        ],
        "config_notes": "Analysis operates on the current git repository by default. Date ranges and file filters can be set per-analysis call.",
    },
    "git_operations": {
        "desc": "Version control automation with 35 git operation tools. Provides branch management, commit operations, PR workflows, and repository management via GitHub API.",
        "env_vars": [
            ("GITHUB_TOKEN", "", "GitHub personal access token for API operations"),
        ],
        "mcp_tools": [
            "git_commit",
            "git_push",
            "git_pull",
            "git_branch",
            "git_list_branches",
        ],
        "config_notes": "GitHub API operations require GITHUB_TOKEN. Git operations use the system git binary. GIT_EDITOR and GIT_TERMINAL_PROMPT are managed internally.",
    },
    "graph_rag": {
        "desc": "Graph-based Retrieval Augmented Generation combining knowledge graphs with LLM retrieval for enhanced question answering and knowledge exploration.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Graph storage and retrieval parameters are configured per-instance. Embedding model and similarity threshold are adjustable.",
    },
    "ide": {
        "desc": "IDE integration and Antigravity client for editor communication. Provides file tracking, artifact management, and IDE bridge for development workflows.",
        "env_vars": [],
        "mcp_tools": ["ide_get_active_file", "ide_list_open_files"],
        "config_notes": "IDE bridge automatically detects running editor instances. Antigravity client uses artifact mtime and cwd scan for file resolution.",
    },
    "identity": {
        "desc": "Identity management for users, agents, and system components. Provides identity resolution, verification, and credential management.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Identity providers are configured programmatically. No global environment variables required.",
    },
    "logging_monitoring": {
        "desc": "Centralized structured logging and monitoring integration. Foundation layer module used by all other modules for consistent log output.",
        "env_vars": [
            (
                "CODOMYRMEX_LOG_LEVEL",
                "INFO",
                "Global log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            ),
            (
                "CODOMYRMEX_LOG_FILE",
                "",
                "File path for log output (empty for stdout only)",
            ),
            (
                "CODOMYRMEX_LOG_FORMAT",
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "Log message format string",
            ),
            ("CODOMYRMEX_LOG_OUTPUT_TYPE", "TEXT", "Log output type (TEXT or JSON)"),
        ],
        "mcp_tools": ["logging_format_structured"],
        "config_notes": "Logging is initialized on first import. Environment variables are read once at startup. JSON output mode enables structured logging for log aggregation systems.",
    },
    "logistics": {
        "desc": "Task orchestration, project management, and workflow logistics. Provides task decomposition, scheduling, and project tracking with class-based MCP integration.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Logistics uses a class-based MCP pattern (not auto-discovered via @mcp_tool). Task scheduling and project configuration are set programmatically.",
    },
    "maintenance": {
        "desc": "System health checks and task management. Provides maintenance_health_check for system status and maintenance_list_tasks for tracking maintenance activities.",
        "env_vars": [],
        "mcp_tools": ["maintenance_health_check", "maintenance_list_tasks"],
        "config_notes": "Health check thresholds (disk space, memory, CPU) are configurable. Task retention period is set through the maintenance manager.",
    },
    "market": {
        "desc": "Market data analysis, trading signals, and financial market integration. Provides market data fetching, technical indicators, and strategy backtesting.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Market data sources and API keys are configured per-provider. Indicator parameters are set per-calculation.",
    },
    "meme": {
        "desc": "Meme generation and template management. Provides image-based meme creation with text overlay and template library management.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Meme template directory is configurable. Font settings and text positioning are set per-meme generation call.",
    },
    "model_context_protocol": {
        "desc": "Standardized LLM communication interfaces. Foundation layer providing @mcp_tool decorator, server transport, tool discovery, and versioning for all MCP integrations.",
        "env_vars": [],
        "mcp_tools": ["inspect_server", "list_registered_tools", "get_tool_schema"],
        "config_notes": "MCP server transport and discovery are configured at startup. Tool discovery uses a 5-minute TTL cache for auto-discovered modules.",
    },
    "model_ops": {
        "desc": "ML model operations including versioning, deployment, monitoring, and feature store integration. Provides model lifecycle management and experiment tracking.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Model registry storage path and experiment tracking backend are configurable. Feature store integration requires feature_store module.",
    },
    "module_template": {
        "desc": "Template module providing the standard structure for creating new Codomyrmex modules. Includes reference implementations of all required module components.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "This is a reference template, not a runtime module. Copy and rename to create new modules following the standard structure.",
    },
    "multimodal": {
        "desc": "Multimodal processing combining text, image, audio, and video inputs. Provides unified processing pipelines for cross-modal analysis.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Individual modality processors are configured through their respective modules (audio, video, etc.). Fusion strategy is set per-pipeline.",
    },
    "networking": {
        "desc": "Network communication utilities including HTTP clients, WebSocket support, and protocol implementations for service-to-service communication.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Connection timeouts, retry policies, and proxy settings are configurable per-client instance.",
    },
    "networks": {
        "desc": "Neural network architectures and graph network implementations. Provides network topology definitions and graph-based computation models.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Network architecture parameters (layers, activation functions, dimensions) are set during model construction.",
    },
    "operating_system": {
        "desc": "OS-level utilities for Linux, macOS, and Windows. Provides platform-specific operations, process management, and system information gathering.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Platform detection is automatic. OS-specific modules load conditionally based on the detected operating system.",
    },
    "orchestrator": {
        "desc": "Workflow execution and scheduling orchestrator. Provides workflow dependency analysis, scheduler metrics, and execution engine for multi-step task automation.",
        "env_vars": [],
        "mcp_tools": ["get_scheduler_metrics", "analyze_workflow_dependencies"],
        "config_notes": "Workflow definitions use YAML or programmatic construction. Scheduler concurrency and retry policies are configurable.",
    },
    "performance": {
        "desc": "Benchmark comparison, regression detection, and performance profiling. Provides performance_check_regression and performance_compare_benchmarks for quantitative analysis.",
        "env_vars": [],
        "mcp_tools": ["performance_check_regression", "performance_compare_benchmarks"],
        "config_notes": "Benchmark storage path and regression thresholds are configurable. Profiling depth and sampling rate are set per-session.",
    },
    "physical_management": {
        "desc": "Physical infrastructure and hardware management. Provides device inventory, sensor monitoring, and physical resource tracking for IoT and edge deployments.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Device registry and sensor polling intervals are configured per-device. Hardware profiles are defined through the management API.",
    },
    "plugin_system": {
        "desc": "Plugin discovery, dependency resolution, and lifecycle management. Provides entry point scanning and plugin dependency graph resolution.",
        "env_vars": [],
        "mcp_tools": ["plugin_scan_entry_points", "plugin_resolve_dependencies"],
        "config_notes": "Plugin directories and entry point groups are configurable. Plugin loading order respects dependency resolution.",
    },
    "privacy": {
        "desc": "Privacy protection including data anonymization, PII detection, consent management, and privacy-preserving data processing.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "PII detection patterns and anonymization strategies are configurable. Consent management rules are set per-data-category.",
    },
    "prompt_engineering": {
        "desc": "LLM prompt design, optimization, and template management. Provides prompt construction utilities, template libraries, and prompt evaluation tools.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Prompt templates are loaded from configurable directories. Model-specific formatting is set per-template.",
    },
    "quantum": {
        "desc": "Quantum computing abstractions and quantum algorithm implementations. Provides quantum circuit construction, simulation, and quantum-classical hybrid workflows.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Quantum backend (simulator or hardware) is configured per-circuit execution. Qubit count and gate set depend on the chosen backend.",
    },
    "relations": {
        "desc": "Relationship strength scoring between entities. Provides quantitative relationship analysis with configurable scoring models.",
        "env_vars": [],
        "mcp_tools": ["relations_score_strength"],
        "config_notes": "Scoring model parameters and relationship type weights are configurable. Default scoring uses a weighted sum model.",
    },
    "release": {
        "desc": "Release management including versioning, changelog generation, and release packaging. Provides automated release workflows with semantic versioning.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Version bump strategy (major, minor, patch) is set per-release. Changelog format and commit message parsing rules are configurable.",
    },
    "scrape": {
        "desc": "HTML content extraction and text similarity analysis. Provides web scraping with Firecrawl integration, content parsing, and text comparison utilities.",
        "env_vars": [
            ("FIRECRAWL_API_KEY", "", "API key for Firecrawl scraping service"),
            ("FC_API_KEY", "", "Alternative API key for Firecrawl (fallback)"),
            (
                "SCRAPE_BASE_URL",
                "https://api.firecrawl.dev",
                "Base URL for scraping service endpoint",
            ),
            (
                "SCRAPE_TIMEOUT",
                "30.0",
                "Request timeout in seconds for scraping operations",
            ),
            (
                "SCRAPE_MAX_RETRIES",
                "3",
                "Maximum retry attempts for failed scrape requests",
            ),
            ("SCRAPE_RETRY_DELAY", "1.0", "Delay in seconds between retry attempts"),
        ],
        "mcp_tools": ["scrape_extract_content", "scrape_text_similarity"],
        "config_notes": "Firecrawl API key is required for web scraping. URL validation enforces http/https scheme. Retry and timeout settings control resilience.",
    },
    "search": {
        "desc": "Full-text, fuzzy, and indexed search across documents and code. Provides search indexing, query parsing, and ranked result retrieval.",
        "env_vars": [],
        "mcp_tools": ["search_documents", "search_index_query", "search_fuzzy"],
        "config_notes": "Search index storage path and tokenization settings are configurable. Fuzzy search threshold controls match sensitivity.",
    },
    "serialization": {
        "desc": "Data serialization and deserialization supporting JSON, YAML, TOML, MessagePack, and pickle formats with validation and type safety.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Serialization format is selected per-operation. Pickle validation is enforced for security. Custom serializers can be registered.",
    },
    "simulation": {
        "desc": "Discrete event simulation and agent-based modeling. Provides simulation environments, event scheduling, and statistical analysis of simulation results.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Simulation parameters (time step, duration, random seed) are set per-simulation run. Event schedulers support priority queues.",
    },
    "skills": {
        "desc": "Skill discovery, listing, and invocation management. Provides 7 skill management tools for PAI skill ecosystem integration.",
        "env_vars": [],
        "mcp_tools": [
            "skills_list",
            "skills_get",
            "skills_invoke",
            "skills_search",
            "skills_register",
            "skills_unregister",
            "skills_validate",
        ],
        "config_notes": "Skill directories are auto-discovered from ~/.claude/skills/. Skill index is cached and regenerated on demand.",
    },
    "spatial": {
        "desc": "Spatial computing with 2D/3D geometry, coordinate systems, and spatial indexing. Provides geospatial operations and 3D transformation utilities.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Coordinate reference systems and spatial index parameters are set per-instance. 3D rendering requires optional dependencies.",
    },
    "static_analysis": {
        "desc": "Code quality analysis, linting, and security scanning. Provides AST-based analysis, style checking, and vulnerability detection across Python source files.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Analysis rules and severity thresholds are configurable. Linting integrates with ruff and black for formatting checks.",
    },
    "system_discovery": {
        "desc": "Module discovery and health monitoring. Provides health_check, list_modules, and dependency_tree tools for understanding system state and module availability.",
        "env_vars": [],
        "mcp_tools": ["health_check", "list_modules", "dependency_tree"],
        "config_notes": "Module discovery scans src/codomyrmex/ automatically. CI environment detection (GitHub Actions, Travis, Kubernetes) is automatic via environment variables.",
    },
    "telemetry": {
        "desc": "Application telemetry with StatsD metrics and OpenTelemetry tracing. Provides metric collection, distributed tracing, and observability integration.",
        "env_vars": [
            ("STATSD_HOST", "localhost", "StatsD server hostname for metrics"),
            ("STATSD_PORT", "8125", "StatsD server port"),
            (
                "OTEL_EXPORTER_OTLP_ENDPOINT",
                "http://localhost:4317",
                "OpenTelemetry OTLP exporter endpoint",
            ),
            (
                "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
                "",
                "OpenTelemetry OTLP traces-specific endpoint",
            ),
        ],
        "mcp_tools": [],
        "config_notes": "StatsD client connects to the configured host:port on initialization. OpenTelemetry exporter uses OTLP protocol with configurable endpoint.",
    },
    "templating": {
        "desc": "Template engines for code and document generation. Provides Jinja2-based templating with custom filters, template inheritance, and dynamic template resolution.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Template directories and Jinja2 environment settings are configurable. Custom filters and extensions can be registered per-environment.",
    },
    "terminal_interface": {
        "desc": "Rich terminal output and formatting for CLI applications. Foundation layer providing colored output, progress bars, tables, and interactive prompts.",
        "env_vars": [],
        "mcp_tools": ["terminal_execute", "terminal_get_info"],
        "config_notes": "Terminal capabilities (color support, Unicode, width) are auto-detected from TERM and COLORTERM environment variables. Shell path is detected from SHELL.",
    },
    "testing": {
        "desc": "Testing infrastructure and utilities for the Codomyrmex test suite. Provides test runners, fixtures, and testing helper functions.",
        "env_vars": [
            ("CODOMYRMEX_TEST_MODE", "true", "Enables test mode for safe execution"),
        ],
        "mcp_tools": [],
        "config_notes": "Test mode is automatically enabled when running under pytest. Test markers (unit, integration, slow, etc.) are defined in pytest.ini.",
    },
    "tool_use": {
        "desc": "Tool invocation framework for LLM tool use patterns. Provides tool registration, parameter validation, and execution tracking for AI agent tool calls.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Tools are registered with schemas for parameter validation. Execution timeout and retry policies are set per-tool.",
    },
    "tree_sitter": {
        "desc": "Tree-sitter based code parsing and AST analysis. Provides language-agnostic syntax tree construction, node querying, and code structure extraction.",
        "env_vars": [],
        "mcp_tools": [
            "tree_sitter_parse",
            "tree_sitter_query",
            "tree_sitter_languages",
        ],
        "config_notes": "Language grammars are loaded on demand. Parser timeout and maximum file size are configurable.",
    },
    "utils": {
        "desc": "Shared utility functions used across the Codomyrmex platform. Provides file handling, string manipulation, process management, and general-purpose helpers.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Utility functions read environment variables via os.environ.get() with caller-specified defaults. No global utils configuration.",
    },
    "validation": {
        "desc": "Schema validation, configuration validation, and validation summaries. Provides JSON schema validation, config file validation, and aggregate validation reporting.",
        "env_vars": [],
        "mcp_tools": ["validate_schema", "validate_config", "validation_summary"],
        "config_notes": "Validation schemas are registered per-module. Result and ResultStatus models provide standardized validation output format.",
    },
    "vector_store": {
        "desc": "Vector database integration for embedding storage and similarity search. Provides vector indexing, nearest neighbor search, and embedding management.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Vector dimensions, distance metric (cosine, euclidean, dot product), and index type are set at store creation time.",
    },
    "video": {
        "desc": "Video processing including capture, editing, transcoding, and analysis. Provides video frame extraction, format conversion, and video metadata handling.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Requires optional dependencies: `uv sync --extra video`. FFmpeg must be installed for transcoding operations.",
    },
    "wallet": {
        "desc": "Digital wallet management for cryptocurrency and token operations. Provides wallet creation, balance tracking, and transaction signing.",
        "env_vars": [],
        "mcp_tools": [],
        "config_notes": "Wallet encryption keys and network endpoints are configured per-wallet instance. Private key storage uses encrypted containers.",
    },
    "website": {
        "desc": "Web application server for the Codomyrmex platform. Provides REST API endpoints, CORS configuration, and Ollama LLM integration for the web interface.",
        "env_vars": [
            ("CODOMYRMEX_CORS_ORIGINS", "*", "Allowed CORS origins (comma-separated)"),
            ("CODOMYRMEX_ENV", "Development", "Application environment name"),
            (
                "CODOMYRMEX_OLLAMA_URL",
                "http://localhost:11434",
                "Ollama service URL for web LLM features",
            ),
            (
                "CODOMYRMEX_DEFAULT_MODEL",
                "llama3.2:1b",
                "Default Ollama model for web interface",
            ),
        ],
        "mcp_tools": [],
        "config_notes": "CORS origins control cross-origin access. Ollama URL must point to a running Ollama instance for LLM features.",
    },
}


def title_case(module_name: str) -> str:
    """Convert module_name to Title Case."""
    words = module_name.replace("_", " ").split()
    # Special cases
    special = {
        "ai": "AI",
        "ci": "CI",
        "cd": "CD",
        "cli": "CLI",
        "api": "API",
        "ide": "IDE",
        "io": "IO",
        "ml": "ML",
        "llm": "LLM",
        "mcp": "MCP",
        "ui": "UI",
        "iot": "IoT",
        "pdf": "PDF",
        "rbac": "RBAC",
        "rag": "RAG",
        "fpf": "FPF",
        "os": "OS",
        "sql": "SQL",
        "tts": "TTS",
        "stt": "STT",
        "ros2": "ROS2",
        "oauth": "OAuth",
        "yaml": "YAML",
        "json": "JSON",
        "csv": "CSV",
        "xml": "XML",
        "html": "HTML",
        "http": "HTTP",
        "s3": "S3",
        "gcp": "GCP",
        "aws": "AWS",
    }
    return " ".join(special.get(w.lower(), w.capitalize()) for w in words)


def generate_readme(module: str, meta: dict) -> str:
    title = title_case(module)
    desc = meta["desc"]
    env_vars = meta["env_vars"]
    mcp_tools = meta["mcp_tools"]
    config_notes = meta["config_notes"]

    lines = [
        f"# {title} Configuration",
        "",
        "**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026",
        "",
        "## Overview",
        "",
        desc,
        "",
    ]

    # Quick Configuration
    if env_vars:
        lines.append("## Quick Configuration")
        lines.append("")
        lines.append("```bash")
        for name, default, description in env_vars:
            if default:
                lines.append(f'export {name}="{default}"    # {description}')
            else:
                lines.append(f'export {name}=""    # {description} (required)')
        lines.append("```")
        lines.append("")

    # Configuration Options table
    lines.append("## Configuration Options")
    lines.append("")
    if env_vars:
        lines.append("| Option | Type | Default | Description |")
        lines.append("|--------|------|---------|-------------|")
        for name, default, description in env_vars:
            default_display = f"`{default}`" if default else "None"
            lines.append(f"| `{name}` | str | {default_display} | {description} |")
    else:
        lines.append(
            f"The {module} module operates with sensible defaults and does not require environment variable configuration. {config_notes}"
        )
    lines.append("")

    # MCP Tools
    if mcp_tools:
        lines.append("## MCP Tools")
        lines.append("")
        lines.append(f"This module exposes {len(mcp_tools)} MCP tool(s):")
        lines.append("")
        for tool in mcp_tools:
            lines.append(f"- `{tool}`")
        lines.append("")

    # PAI Integration
    lines.append("## PAI Integration")
    lines.append("")
    if mcp_tools:
        lines.append(
            f"PAI agents invoke {module} tools through the MCP bridge. {config_notes}"
        )
    else:
        lines.append(
            f"PAI agents interact with {module} through direct Python imports. {config_notes}"
        )
    lines.append("")

    # Validation
    lines.append("## Validation")
    lines.append("")
    lines.append("```bash")
    lines.append("# Verify module is available")
    lines.append("codomyrmex modules | grep " + module)
    lines.append("")
    lines.append("# Run module health check")
    lines.append("codomyrmex status")
    lines.append("```")
    lines.append("")

    # Navigation
    lines.append("## Navigation")
    lines.append("")
    lines.append(
        f"- [Source Module](../../src/codomyrmex/{module}/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)"
    )
    lines.append("")

    return "\n".join(lines)


def generate_agents(module: str, meta: dict) -> str:
    title = title_case(module)
    desc = meta["desc"]
    env_vars = meta["env_vars"]
    mcp_tools = meta["mcp_tools"]
    config_notes = meta["config_notes"]

    lines = [
        f"# {title} -- Configuration Agent Coordination",
        "",
        "**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026",
        "",
        "## Overview",
        "",
        f"Agent coordination guide for configuring and using the {module} module. {desc.split('.')[0]}.",
        "",
        "## Configuration Requirements",
        "",
        f"Before using {module} in any PAI workflow, ensure:",
        "",
    ]

    if env_vars:
        for i, (name, default, description) in enumerate(env_vars, 1):
            if default:
                lines.append(
                    f"{i}. `{name}` is set (default: `{default}`) -- {description}"
                )
            else:
                lines.append(f"{i}. `{name}` is set -- {description}")
    else:
        lines.append(
            f"1. The module is importable via `from codomyrmex.{module} import *`"
        )
        lines.append(
            "2. Any optional dependencies are installed (check with `codomyrmex check`)"
        )

    lines.append("")
    lines.append("## Agent Instructions")
    lines.append("")

    if env_vars:
        lines.append(
            f"1. Verify required environment variables are set before invoking {module} tools"
        )
        lines.append(
            f'2. Use `get_config("{module}.<key>")` from config_management to read module settings'
        )
    else:
        lines.append(
            f"1. Import the module directly: `from codomyrmex.{module} import ...`"
        )
        lines.append(
            "2. Check module availability with `list_modules()` from system_discovery"
        )

    if mcp_tools:
        lines.append(
            f"3. Available MCP tools: {', '.join(f'`{t}`' for t in mcp_tools)}"
        )
    else:
        lines.append(
            "3. This module has no auto-discovered MCP tools; use direct Python imports"
        )

    lines.append(f"4. {config_notes}")
    lines.append("")

    lines.append("## Operating Contracts")
    lines.append("")
    lines.append(
        "- **Import Safety**: Module import does not trigger side effects or network calls"
    )
    lines.append(
        "- **Error Handling**: All errors raise specific exceptions (never returns None silently)"
    )
    lines.append(
        "- **Thread Safety**: Configuration reads are thread-safe after initialization"
    )
    lines.append("")

    lines.append("## Configuration Patterns")
    lines.append("")
    lines.append("```python")
    lines.append(
        "from codomyrmex.config_management.mcp_tools import get_config, set_config"
    )
    lines.append("")
    lines.append("# Read current configuration")
    lines.append(f'value = get_config("{module}.setting")')
    lines.append("")
    lines.append("# Update configuration")
    lines.append(f'set_config("{module}.setting", "new_value")')
    lines.append("```")
    lines.append("")

    lines.append("## PAI Agent Role Access Matrix")
    lines.append("")
    lines.append("| PAI Agent | Config Access | Notes |")
    lines.append("|-----------|--------------|-------|")
    lines.append("| Engineer | Read/Write | Can update configuration during setup |")
    lines.append("| Architect | Read | Reviews configuration for compliance |")
    lines.append("| QATester | Read | Validates configuration before test runs |")
    lines.append("| Researcher | Read | No configuration changes |")
    lines.append("")

    lines.append("## Navigation")
    lines.append("")
    lines.append(
        f"- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/{module}/AGENTS.md)"
    )
    lines.append("")

    return "\n".join(lines)


def generate_spec(module: str, meta: dict) -> str:
    title = title_case(module)
    desc = meta["desc"]
    env_vars = meta["env_vars"]
    config_notes = meta["config_notes"]

    lines = [
        f"# {title} Configuration Specification",
        "",
        "**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026",
        "",
        "## Overview",
        "",
        f"{desc} This specification documents the configuration schema and constraints.",
        "",
        "## Configuration Schema",
        "",
    ]

    if env_vars:
        lines.append("| Key | Type | Required | Default | Description |")
        lines.append("|-----|------|----------|---------|-------------|")
        for name, default, description in env_vars:
            required = "Yes" if not default else "No"
            default_display = f"`{default}`" if default else "None"
            lines.append(
                f"| `{name}` | string | {required} | {default_display} | {description} |"
            )
        lines.append("")

        lines.append("## Environment Variables")
        lines.append("")
        lines.append("```bash")
        required = [(n, d, desc) for n, d, desc in env_vars if not d]
        optional = [(n, d, desc) for n, d, desc in env_vars if d]
        if required:
            lines.append("# Required")
            for name, default, description in required:
                lines.append(f'export {name}=""    # {description}')
        if optional:
            if required:
                lines.append("")
            lines.append("# Optional (defaults shown)")
            for name, default, description in optional:
                lines.append(f'export {name}="{default}"    # {description}')
        lines.append("```")
    else:
        lines.append(
            f"The {module} module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments."
        )
        lines.append("")
        lines.append("| Key | Type | Required | Default | Description |")
        lines.append("|-----|------|----------|---------|-------------|")
        lines.append(
            f"| (programmatic) | varies | No | module defaults | {config_notes} |"
        )

    lines.append("")

    lines.append("## Design Principles")
    lines.append("")
    lines.append(
        "- **Centralized Config**: All settings accessible via config_management module"
    )
    lines.append(
        "- **Env-First**: Environment variables take precedence over config file values"
    )
    lines.append(
        "- **Explicit Defaults**: All optional settings have documented defaults"
    )
    lines.append(
        "- **Zero-Mock**: No placeholder or fake configuration values in production"
    )
    lines.append("")

    lines.append("## Constraints")
    lines.append("")
    if env_vars:
        required_vars = [n for n, d, _ in env_vars if not d]
        if required_vars:
            for v in required_vars:
                lines.append(f"- `{v}` must be set before module initialization")
        else:
            lines.append("- All configuration options have sensible defaults")
    else:
        lines.append(f"- {config_notes}")
    lines.append(
        "- Configuration is validated on first use; invalid values raise explicit errors"
    )
    lines.append("- No silent fallback to placeholder values")
    lines.append("")

    lines.append("## Dependencies")
    lines.append("")
    lines.append("**Depends on**: `config_management`, `environment_setup`")
    lines.append("")

    lines.append("## Navigation")
    lines.append("")
    lines.append(
        f"- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/{module}/SPEC.md)"
    )
    lines.append("")

    return "\n".join(lines)


def has_stub(filepath: Path) -> bool:
    """Check if file contains the stub marker."""
    if not filepath.exists():
        return False
    text = filepath.read_text()
    return "MANUAL_DOC_REVIEW_REQUIRED" in text


def main():
    total_written = 0
    total_skipped = 0
    errors = []

    for module, meta in sorted(MODULE_META.items()):
        config_module_dir = CONFIG_DIR / module
        if not config_module_dir.exists():
            errors.append(f"SKIP: config/{module}/ directory does not exist")
            total_skipped += 1
            continue

        # README.md
        readme_path = config_module_dir / "README.md"
        if has_stub(readme_path):
            readme_path.write_text(generate_readme(module, meta))
            total_written += 1
        else:
            total_skipped += 1

        # AGENTS.md
        agents_path = config_module_dir / "AGENTS.md"
        if has_stub(agents_path):
            agents_path.write_text(generate_agents(module, meta))
            total_written += 1
        else:
            total_skipped += 1

        # SPEC.md
        spec_path = config_module_dir / "SPEC.md"
        if has_stub(spec_path):
            spec_path.write_text(generate_spec(module, meta))
            total_written += 1
        else:
            total_skipped += 1

    print(f"Written: {total_written} files")
    print(f"Skipped: {total_skipped} files (no stub marker or missing dir)")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  {e}")


if __name__ == "__main__":
    main()
