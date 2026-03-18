"""Category → Skill group mapping constants and description text.

Split from ``skill_generator.py`` to keep the parent file under 800 LOC.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Category → Skill group mapping
# Maps @mcp_tool(category=...) values to the skill directory name.
# New categories not in this map are auto-named Codomyrmex{Category.title()}.
# ---------------------------------------------------------------------------
CATEGORY_GROUP_MAP: dict[str, str] = {
    # ── Git ──────────────────────────────────────────────────────────────
    "git_operations": "CodomyrmexGit",
    "git_analysis": "CodomyrmexGit",
    "git": "CodomyrmexGit",
    "git_status": "CodomyrmexGit",
    "apply_stash": "CodomyrmexGit",
    "clone_repository": "CodomyrmexGit",
    "commit_changes": "CodomyrmexGit",
    "create_branch": "CodomyrmexGit",
    "create_tag": "CodomyrmexGit",
    "create_commit_timeline_diagram": "CodomyrmexGit",
    "create_git_branch_diagram": "CodomyrmexGit",
    "create_git_workflow_diagram": "CodomyrmexGit",
    "create_repository_structure_diagram": "CodomyrmexGit",
    "get_commit_history": "CodomyrmexGit",
    "get_current_branch": "CodomyrmexGit",
    "get_status": "CodomyrmexGit",
    "initialize_git_repository": "CodomyrmexGit",
    "list_stashes": "CodomyrmexGit",
    "list_tags": "CodomyrmexGit",
    "merge_branch": "CodomyrmexGit",
    "pull_changes": "CodomyrmexGit",
    "push_changes": "CodomyrmexGit",
    "rebase_branch": "CodomyrmexGit",
    "stash_changes": "CodomyrmexGit",
    "switch_branch": "CodomyrmexGit",
    # ── Security ─────────────────────────────────────────────────────────
    "security": "CodomyrmexSecurity",
    "crypto": "CodomyrmexSecurity",
    "formal_verification": "CodomyrmexSecurity",
    # ── AI / LLM / Reasoning ─────────────────────────────────────────────
    "agents": "CodomyrmexAI",
    "agents.core": "CodomyrmexAI",
    "cerebrum": "CodomyrmexAI",
    "llm": "CodomyrmexAI",
    "orchestrator": "CodomyrmexAI",
    "collaboration": "CodomyrmexAI",
    "email": "CodomyrmexAI",
    "calendar": "CodomyrmexAI",
    "list_workflows": "CodomyrmexAI",
    # ── Code execution / analysis ─────────────────────────────────────────
    "coding": "CodomyrmexCode",
    "analyze_file": "CodomyrmexCode",
    "analyze_project": "CodomyrmexCode",
    "analyze_python": "CodomyrmexCode",
    "execute_code": "CodomyrmexCode",
    # ── Data / Visualization / Scraping ───────────────────────────────────
    "data_visualization": "CodomyrmexData",
    "scrape": "CodomyrmexData",
    "relations": "CodomyrmexData",
    "create_bar_chart": "CodomyrmexData",
    "create_line_plot": "CodomyrmexData",
    "create_pie_chart": "CodomyrmexData",
    "checksum_file": "CodomyrmexData",
    "json_query": "CodomyrmexData",
    # ── Deploy / Infrastructure ───────────────────────────────────────────
    "containerization": "CodomyrmexDeploy",
    "cloud": "CodomyrmexDeploy",
    # ── Test / Quality ────────────────────────────────────────────────────
    "performance": "CodomyrmexTest",
    "maintenance": "CodomyrmexTest",
    "validation": "CodomyrmexTest",
    "run_tests": "CodomyrmexTest",
    # ── Memory ────────────────────────────────────────────────────────────
    "agentic_memory": "codomyrmexMemory",
    # ── Search ────────────────────────────────────────────────────────────
    "search": "codomyrmexSearch",
    "search_codebase": "codomyrmexSearch",
    # ── Docs ──────────────────────────────────────────────────────────────
    "documentation": "codomyrmexDocs",
    "generate_documentation": "codomyrmexDocs",
    "get_module_readme": "codomyrmexDocs",
    # ── Status / Discovery ────────────────────────────────────────────────
    "system_discovery": "codomyrmexStatus",
    "logging": "codomyrmexStatus",
    "model_context_protocol": "codomyrmexStatus",
    "plugins": "codomyrmexStatus",
    "list_directory": "codomyrmexStatus",
    "list_module_functions": "codomyrmexStatus",
    "list_modules": "codomyrmexStatus",
    "module_info": "codomyrmexStatus",
    "pai_awareness": "codomyrmexStatus",
    "pai_status": "codomyrmexStatus",
    "read_file": "codomyrmexStatus",
    # ── Events ────────────────────────────────────────────────────────────
    "events": "CodomyrmexEvents",
    # ── Config ────────────────────────────────────────────────────────────
    "config_management": "CodomyrmexConfig",
    # ── Meta / General (main umbrella skill) ──────────────────────────────
    "general": "Codomyrmex",
    "call_module_function": "Codomyrmex",
    "invalidate_cache": "Codomyrmex",
    "run_command": "Codomyrmex",
    "write_file": "Codomyrmex",
    # ── New explicit overrides ───────────────────────────────────────────
    "NetworkGraph": "CodomyrmexData",
    "Simulator": "Codomyrmex",
    "ai_gateway": "CodomyrmexAI",
    "aider": "CodomyrmexAI",
    "api": "Codomyrmex",
    "audio": "CodomyrmexData",
    "auth": "CodomyrmexSecurity",
    "autograd": "CodomyrmexCode",
    "bio_simulation": "Codomyrmex",
    "cache": "Codomyrmex",
    "ci_cd_automation": "CodomyrmexDeploy",
    "compression": "Codomyrmex",
    "concurrency": "Codomyrmex",
    "config_audits": "CodomyrmexConfig",
    "config_monitoring": "CodomyrmexTest",
    "container_optimization": "CodomyrmexAI",
    "create_ascii_art": "Codomyrmex",
    "dark": "Codomyrmex",
    "data_curation": "CodomyrmexData",
    "data_lineage": "CodomyrmexData",
    "database_management": "CodomyrmexData",
    "defense": "CodomyrmexSecurity",
    "dependency_injection": "Codomyrmex",
    "deployment": "CodomyrmexDeploy",
    "distillation": "Codomyrmex",
    "distributed_training": "CodomyrmexAI",
    "docs_gen": "codomyrmexDocs",
    "documents": "codomyrmexDocs",
    "dpo": "CodomyrmexAI",
    "edge_computing": "CodomyrmexDeploy",
    "encryption": "CodomyrmexSecurity",
    "environment_setup": "Codomyrmex",
    "eval_harness": "CodomyrmexTest",
    "evolutionary_ai": "CodomyrmexAI",
    "feature_flags": "Codomyrmex",
    "feature_store": "Codomyrmex",
    "file_system": "Codomyrmex",
    "finance": "Codomyrmex",
    "get_config": "CodomyrmexConfig",
    "git_add": "CodomyrmexGit",
    "git_clone": "CodomyrmexGit",
    "git_diff_files": "CodomyrmexGit",
    "git_fetch_changes": "CodomyrmexGit",
    "git_is_repo": "CodomyrmexGit",
    "git_log_filtered": "CodomyrmexGit",
    "git_prune_remote": "CodomyrmexGit",
    "git_pull": "CodomyrmexGit",
    "google_workspace": "Codomyrmex",
    "graph_rag": "CodomyrmexData",
    "ide": "CodomyrmexCode",
    "identity": "CodomyrmexSecurity",
    "image": "CodomyrmexData",
    "init_submodules": "CodomyrmexGit",
    "interpretability": "Codomyrmex",
    "jules": "CodomyrmexAI",
    "logistics": "Codomyrmex",
    "logit_processor": "CodomyrmexGit",
    "lora": "CodomyrmexAI",
    "market": "Codomyrmex",
    "matmul_kernel": "Codomyrmex",
    "meme": "Codomyrmex",
    "ml_pipeline_create": "Codomyrmex",
    "ml_pipeline_execute": "Codomyrmex",
    "model_merger": "CodomyrmexAI",
    "model_ops": "CodomyrmexAI",
    "multimodal": "Codomyrmex",
    "nas": "Codomyrmex",
    "networking": "CodomyrmexDeploy",
    "networks": "CodomyrmexDeploy",
    "neural": "CodomyrmexAI",
    "operating_system": "CodomyrmexDeploy",
    "pai_pm": "CodomyrmexAI",
    "pattern_matching": "Codomyrmex",
    "peft": "Codomyrmex",
    "physical_management": "Codomyrmex",
    "privacy": "CodomyrmexSecurity",
    "prompt_engineering": "CodomyrmexAI",
    "quantization": "CodomyrmexAI",
    "quantum_bell_state_demo": "Codomyrmex",
    "quantum_circuit_stats": "Codomyrmex",
    "quantum_run_circuit": "Codomyrmex",
    "relations_crm": "Codomyrmex",
    "relations_network_analysis": "CodomyrmexDeploy",
    "relations_social_media": "Codomyrmex",
    "relations_uor": "Codomyrmex",
    "release": "CodomyrmexDeploy",
    "rlhf": "CodomyrmexAI",
    "semantic_router": "Codomyrmex",
    "serialization": "Codomyrmex",
    "set_config": "CodomyrmexConfig",
    "simulation": "Codomyrmex",
    "skills": "Codomyrmex",
    "slm": "CodomyrmexAI",
    "softmax_opt": "Codomyrmex",
    "soul": "CodomyrmexAI",
    "spatial": "Codomyrmex",
    "ssm": "Codomyrmex",
    "static_analysis": "CodomyrmexCode",
    "synthetic_data": "CodomyrmexData",
    "telemetry": "CodomyrmexTest",
    "templating": "Codomyrmex",
    "terminal_interface": "Codomyrmex",
    "testing": "CodomyrmexTest",
    "text_to_sql": "Codomyrmex",
    "tokenizer": "Codomyrmex",
    "tool_use": "Codomyrmex",
    "tree_sitter": "CodomyrmexCode",
    "update_submodules": "CodomyrmexGit",
    "utils": "Codomyrmex",
    "vector_store": "Codomyrmex",
    "video": "CodomyrmexCode",
    "wallet": "Codomyrmex",
}

# ---------------------------------------------------------------------------
# Per-skill description text (USE WHEN triggers for frontmatter)
# ---------------------------------------------------------------------------
SKILL_DESCRIPTIONS: dict[str, str] = {
    "CodomyrmexGit": (
        "Git operations and history analysis via Codomyrmex modules. "
        "USE WHEN user wants git analysis, commit timeline, contributor stats, "
        "branch diagrams, git log, push/pull/clone operations, repository history "
        "insights, git status, git diff, create branch, switch branch, commit, tag, "
        "stash, rebase, merge, compare branches, find commit, contributor analysis, "
        "git history, git blame, or cherry-pick."
    ),
    "CodomyrmexSecurity": (
        "Security scanning, crypto operations, and formal verification via Codomyrmex. "
        "USE WHEN user wants security scan, scan secrets, audit code security, "
        "scan vulnerabilities, crypto key generation, hash data, verify hash, "
        "z3 constraint, formal verify, check for leaked secrets, security audit, "
        "cryptographic operations, formal proof, find vulnerabilities, check secrets, "
        "certificate validation, key generation, hashing, prove invariant, or check "
        "satisfiability."
    ),
    "CodomyrmexAI": (
        "AI agents, reasoning, orchestration, and LLM operations via Codomyrmex. "
        "USE WHEN user wants reasoning trace, thinking agent, cerebrum knowledge, "
        "orchestrate workflow, llm provider, ask llm, generate text, execute agent, "
        "get agent memory, workflow dependencies, agentic memory, store intelligence, "
        "query knowledge base, set reasoning depth, retrieve reasoning trace, knowledge "
        "retrieval, run agent, ask question, generate response, or run thought process."
    ),
    "CodomyrmexCode": (
        "Code execution, analysis, and static analysis via Codomyrmex. "
        "USE WHEN user wants execute code, sandbox code, run python, run javascript, "
        "static analysis, code debug, analyze code error, code quality, pattern matching, "
        "find code pattern, code complexity, code review, pylint, bandit, security lint, "
        "run code in sandbox, code review, linting check, check code quality, run "
        "snippet, or debug error."
    ),
    "CodomyrmexData": (
        "Data search, scraping, and visualization via Codomyrmex. "
        "USE WHEN user wants full text search, fuzzy search, scrape html, extract content "
        "from webpage, text similarity, bar chart, pie chart, line plot, data "
        "visualization, generate chart, export dashboard, create visualization, HTML "
        "dashboard, data analysis charts, create chart, plot data, html report, "
        "visualize data, chart comparison, or data similarity."
    ),
    "CodomyrmexDeploy": (
        "Infrastructure and deployment operations via Codomyrmex. "
        "USE WHEN user wants docker build, container scan, list containers, list cloud "
        "instances, s3 bucket, upload to s3, ci pipeline, build automation, container "
        "runtime, container security scan, cloud vm, deploy, infrastructure, "
        "containerization, CI/CD, deploy code, build image, scan dockerfile, push to "
        "cloud, list running containers, or cloud storage."
    ),
    "CodomyrmexTest": (
        "Testing and performance benchmarking via Codomyrmex. "
        "USE WHEN user wants run tests, benchmark, performance regression, compare "
        "benchmarks, run pytest, test a module, check performance, benchmark comparison, "
        "detect regression, run codomyrmex tests, test suite, performance analysis, "
        "measure performance, coverage report, run unit tests, check performance, "
        "regression check, or test module."
    ),
    "codomyrmexMemory": (
        "Agentic long-term memory storage and retrieval via Codomyrmex. "
        "USE WHEN user says 'add to memory', 'store memory', 'remember this', "
        "'save to memory', 'retrieve memory', 'search memory', 'what do I remember "
        "about', 'store this for later', 'recall from memory', 'list memories', "
        "'what have you stored', 'delete memory', 'forget this', 'tagged memory', or "
        "'recall from earlier'."
    ),
    "codomyrmexSearch": (
        "High-performance codebase and document search via Codomyrmex. "
        "USE WHEN user says 'search codebase', 'find in code', 'grep pattern', "
        "'search for pattern', 'find all occurrences', 'full text search', 'fuzzy "
        "search', 'search documents', 'find files matching', 'find all uses of', "
        "'locate pattern', 'where is function', 'grep recursively', 'find definition', "
        "or wants regex/pattern search across code or text."
    ),
    "codomyrmexDocs": (
        "Retrieve and generate Codomyrmex module documentation. "
        "USE WHEN user says 'get module docs', 'module documentation', 'show me the "
        "readme for', 'what does module X do', 'generate docs', 'audit RASP "
        "compliance', 'module readme', 'module spec', 'show me the api', 'module "
        "capabilities', 'read the spec', 'what is in module', 'module exports', or "
        "wants documentation for any Codomyrmex module."
    ),
    "codomyrmexStatus": (
        "System health check and PAI awareness report for Codomyrmex. "
        "USE WHEN user says 'system status', 'health check', 'pai status', 'codomyrmex "
        "health', 'is codomyrmex working', 'check pai awareness', 'list modules', "
        "'module inventory', 'how many tools', 'system overview', 'check health', "
        "'module count', 'what modules exist', 'codomyrmex inventory', or wants a "
        "status dashboard."
    ),
    "CodomyrmexEvents": (
        "Event bus operations via Codomyrmex events module. "
        "USE WHEN user wants emit event, publish event, subscribe to events, listen for "
        "events, event history, event bus, trigger event, event type registry, "
        "event-driven, or async event handling."
    ),
    "CodomyrmexConfig": (
        "Configuration management via Codomyrmex config_management module. "
        "USE WHEN user wants get config, set config, validate config, config management, "
        "app configuration, config key, configuration store, settings management, "
        "read settings, or update settings."
    ),
    "Codomyrmex": (
        "Full-spectrum coding workspace skill providing 171 MCP tools across 33 modules. "
        "USE WHEN user says 'verify codomyrmex', 'codomyrmexVerify', 'audit codomyrmex', "
        "'trust codomyrmex', 'codomyrmexTrust', 'trust tools', 'enable destructive tools', "
        "'check pai status', 'codomyrmex tools', 'codomyrmex analyze', 'codomyrmex search', "
        "'codomyrmex memory', 'codomyrmex docs', 'codomyrmex status', 'codomyrmex git', "
        "'codomyrmex security', 'codomyrmex ai', 'codomyrmex code', 'codomyrmex data', "
        "'codomyrmex deploy', 'codomyrmex test', 'list capabilities', 'codomyrmex help', "
        "'what can codomyrmex do', 'codomyrmex capabilities', or uses any 'codomyrmex' "
        "automation tools."
    ),
    "CodomyrmexGemini": (
        "Gemini LLM operations and executions via Codomyrmex. "
        "USE WHEN user wants gemini operations, wants to run a prompt through Gemini, "
        "or uses any codomyrmex gemini tools."
    ),
    "CodomyrmexO1": (
        "O1 LLM operations and reasoning traces via Codomyrmex. "
        "USE WHEN user wants o1 operations, advanced mathematical or coding reasoning, "
        "or uses any codomyrmex o1 tools."
    ),
    "CodomyrmexOpenclaw": (
        "Openclaw orchestration and agentic tool operations via Codomyrmex. "
        "USE WHEN user wants openclaw operations, or uses any codomyrmex openclaw tools."
    ),
    "CodomyrmexDeepseek": (
        "Deepseek programmatic coding and reasoning operations via Codomyrmex. "
        "USE WHEN user wants deepseek operations, deepseek coder executions, "
        "or uses any codomyrmex deepseek tools."
    ),
    "CodomyrmexCli": (
        "Direct Command Line Interface (CLI) execution environment via Codomyrmex. "
        "USE WHEN user wants cli operations, terminal execution, shell commands, "
        "or uses any codomyrmex cli tools."
    ),
    "CodomyrmexMistralVibe": (
        "Mistral Vibe specific model operations and processing via Codomyrmex. "
        "USE WHEN user wants mistralvibe operations, Mistral large parameter execution, "
        "or uses any codomyrmex mistralvibe tools."
    ),
    "CodomyrmexEveryCode": (
        "EveryCode language-agnostic code transformation and translation via Codomyrmex. "
        "USE WHEN user wants everycode operations, code interpretation, "
        "or uses any codomyrmex everycode tools."
    ),
    "CodomyrmexPi": (
        "Inflection Pi style conversational and pedagogical assistance via Codomyrmex. "
        "USE WHEN user wants pi operations, or uses any codomyrmex pi tools."
    ),
    "CodomyrmexPaperclip": (
        "Paperclip resource extraction and unbounded capability agent via Codomyrmex. "
        "USE WHEN user wants paperclip operations, objective maximization loops, "
        "or uses any codomyrmex paperclip tools."
    ),
    "CodomyrmexOpenfang": (
        "Openfang specialized LLM capability interface via Codomyrmex. "
        "USE WHEN user wants openfang operations, or uses any codomyrmex openfang tools."
    ),
    "CodomyrmexHermes": (
        "Hermes model family integration (NousResearch) via Codomyrmex. "
        "USE WHEN user wants hermes operations, tool-calling optimizations, "
        "fine-tuned agentic models, or uses any codomyrmex hermes tools."
    ),
    "CodomyrmexCodex": (
        "Codex execution for autocompletion and rapid drafting via Codomyrmex. "
        "USE WHEN user wants codex operations, code completion tasks, "
        "or uses any codomyrmex codex tools."
    ),
}

# ---------------------------------------------------------------------------
# Algorithm phase mapping defaults
# ---------------------------------------------------------------------------
DEFAULT_PHASE_MAPS: dict[str, dict[str, list[str]]] = {
    "CodomyrmexGit": {
        "OBSERVE": ["git_repo_status", "git_log", "git_current_branch", "git_is_repo"],
        "THINK": [
            "git_diff",
            "create_commit_timeline_diagram",
            "create_git_branch_diagram",
        ],
        "BUILD": ["git_create_branch", "git_switch_branch", "stash_changes"],
        "EXECUTE": ["git_commit", "git_push", "git_pull", "git_clone"],
        "VERIFY": ["git_repo_status", "git_diff", "list_tags"],
        "LEARN": ["create_git_workflow_diagram", "create_repository_structure_diagram"],
    },
    "CodomyrmexSecurity": {
        "OBSERVE": ["audit_code_security", "scan_vulnerabilities", "scan_secrets"],
        "THINK": ["get_model", "add_item", "solve_model"],
        "VERIFY": ["scan_secrets", "verify_hash", "audit_code_security"],
        "LEARN": ["hash_data", "generate_key"],
    },
    "CodomyrmexAI": {
        "OBSERVE": ["execute_agent", "get_case_reference", "ask"],
        "THINK": ["set_reasoning_depth", "add_case_reference", "ask"],
        "PLAN": ["analyze_workflow_dependencies", "list_workflows"],
        "BUILD": ["execute_agent", "generate_text"],
        "EXECUTE": ["execute_agent", "execute_workflow", "ask"],
        "VERIFY": ["get_agent_memory", "retrieve_reasoning_trace"],
        "LEARN": ["store_reasoning_trace", "add_case_reference"],
    },
    "CodomyrmexCode": {
        "OBSERVE": ["code_review_file", "code_review_project", "analyze_python"],
        "THINK": ["code_review_file"],
        "BUILD": ["code_execute", "code_debug"],
        "EXECUTE": ["code_execute"],
        "VERIFY": ["code_review_file", "code_list_languages"],
    },
    "CodomyrmexData": {
        "OBSERVE": ["full_text_search", "fuzzy_search", "scrape_html"],
        "BUILD": ["generate_chart", "create_bar_chart", "create_pie_chart"],
        "EXECUTE": ["export_dashboard"],
        "VERIFY": ["full_text_search"],
    },
    "CodomyrmexDeploy": {
        "OBSERVE": [
            "container_list",
            "container_runtime_status",
            "list_cloud_instances",
        ],
        "BUILD": ["container_build"],
        "EXECUTE": ["container_build", "upload_to_s3"],
        "VERIFY": ["container_security_scan", "container_list"],
    },
    "CodomyrmexTest": {
        "OBSERVE": ["health_check", "run_benchmark"],
        "EXECUTE": ["run_benchmark", "compare_benchmarks"],
        "VERIFY": ["detect_regression", "validate_schema", "health_check"],
    },
    "codomyrmexMemory": {
        "OBSERVE": ["search_memories", "list_memories"],
        "EXECUTE": ["store_memory"],
        "VERIFY": ["search_memories"],
        "LEARN": ["store_memory", "add_memory_tag"],
    },
    "codomyrmexSearch": {
        "OBSERVE": ["full_text_search", "fuzzy_search", "indexed_search"],
        "THINK": ["full_text_search"],
        "VERIFY": ["full_text_search"],
    },
    "codomyrmexDocs": {
        "OBSERVE": ["audit_rasp_compliance"],
        "BUILD": ["generate_module_docs"],
        "VERIFY": ["audit_rasp_compliance"],
    },
    "codomyrmexStatus": {
        "OBSERVE": ["pai_status", "list_modules", "dependency_tree", "health_check"],
        "VERIFY": ["pai_status", "health_check"],
    },
    "CodomyrmexEvents": {
        "EXECUTE": ["emit_event"],
        "OBSERVE": ["get_event_history", "list_event_types"],
        "VERIFY": ["get_event_history"],
    },
    "CodomyrmexConfig": {
        "OBSERVE": ["get_config"],
        "BUILD": ["set_config"],
        "VERIFY": ["validate_config", "get_config"],
    },
}
