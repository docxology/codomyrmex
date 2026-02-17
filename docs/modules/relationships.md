# 🔗 Codomyrmex Module Relationships & Interdependencies

**Version**: v0.1.1 | **Last Updated**: February 2026

This document provides a comprehensive overview of how Codomyrmex modules interact with each other, their dependencies, and data flow patterns.

## 📋 Module Overview

| Module | Primary Role | Key Dependencies | Consumes From | Provides To |
|--------|-------------|------------------|---------------|-------------|
| **`environment_setup`** | Environment validation & dependency management | System packages | None | All modules |
| **`logging_monitoring`** | Centralized logging framework | None | All modules | All modules |
| **`model_context_protocol`** | AI communication standard, auto-discovery | JSON Schema | AI modules | AI modules |
| **`terminal_interface`** | Rich terminal interactions | Rich, prompt-toolkit | None | Application modules |
| **`config_management`** | Configuration management | PyYAML, configparser | logging_monitoring | All modules |
| **`database_management`** | Data persistence, **migration**, **backup**, **lineage** | SQLAlchemy, asyncpg | logging_monitoring | All modules |
| **`llm`** | LLM infrastructure, **multimodal**, **safety filtering** | OpenAI, Anthropic, Ollama | logging_monitoring, model_context_protocol | AI modules |
| **`performance`** | Performance monitoring | psutil, cProfile | logging_monitoring | All modules |
| **`coding`** | Code execution, review, **static analysis**, **pattern matching** | subprocess, security | logging_monitoring | All modules |
| **`data_visualization`** | Charts, plots, **multi-format export** | matplotlib, seaborn | logging_monitoring | All modules |
| **`security`** | Security scanning, threat modeling, **vulnerability scanner**, **governance** | bandit, semgrep, cryptography | logging_monitoring | All modules |
| **`scrape`** | Web scraping and content extraction | BeautifulSoup, requests | logging_monitoring | All modules |
| **`documents`** | Document processing, **RAG chunking** | parsers, extractors | logging_monitoring | All modules |
| **`cache`** | Caching infrastructure, **multi-strategy invalidation** | redis, memory | logging_monitoring | All modules |
| **`compression`** | Data compression | zlib, gzip, lz4 | None | All modules |
| **`encryption`** | Encryption utilities, **digital signing** | cryptography | logging_monitoring | All modules |
| **`networking`** | Network utilities, **service mesh** | aiohttp, requests | logging_monitoring | All modules |
| **`serialization`** | Data serialization, **streaming I/O** | json, yaml, msgpack | None | All modules |
| **`validation`** | Data validation, **shared schema registry** | pydantic, jsonschema | logging_monitoring | All modules |
| **`git_operations`** | Git workflow automation, **merge resolution** | GitPython | logging_monitoring | All modules |
| **`documentation`** | Documentation generation, **education** | Docusaurus | All modules | All modules |
| **`api`** | API infrastructure, **rate limiting** | OpenAPI, FastAPI | logging_monitoring | All modules |
| **`ci_cd_automation`** | CI/CD pipeline management, **build automation** | Docker, Kubernetes | logging_monitoring, containerization | All modules |
| **`containerization`** | Container management | Docker, Kubernetes | logging_monitoring | ci_cd_automation |
| **`logistics`** | Orchestration and scheduling | schedulers | logging_monitoring | Application modules |
| **`cloud`** | Cloud integrations, **cost management** | cloud SDKs | logging_monitoring, config_management | All modules |
| **`auth`** | Authentication | OAuth, JWT | logging_monitoring | All modules |
| **`system_discovery`** | System exploration | introspection | logging_monitoring | Application modules |
| **`cli`** | Command-line interface, **shell completion** | click, argparse | logging_monitoring | Users |
| **`website`** | Website generation, **accessibility** | Jinja2, Flask | logging_monitoring | Users |
| **`module_template`** | Module creation template | None | None | Developers |
| **`events`** | Event system, pub/sub, **replay**, **dead letter**, **streaming**, **notifications** | asyncio | logging_monitoring | All modules |
| **`plugin_system`** | Plugin architecture | importlib | logging_monitoring | All modules |
| **`agents`** | Agentic framework integrations, **benchmarks** | AI providers | logging_monitoring, llm | All modules |
| **`ide`** | IDE integrations | IDE APIs | logging_monitoring, agents | Developers |
| **`cerebrum`** | Case-based reasoning | numpy, scipy | logging_monitoring | AI modules |
| **`fpf`** | Functional Programming Framework | None | logging_monitoring | All modules |
| **`skills`** | Skills framework | None | logging_monitoring, agents | All modules |
| **`spatial`** | 3D/4D modeling and visualization | Open3D, Trimesh | logging_monitoring | Specialized use cases |
| **`physical_management`** | Physical system simulation | Physics engines | logging_monitoring | Specialized use cases |
| **`utils`** | Common utilities, **hashing**, **retry**, **i18n** | None | None | All modules |
| **`templating`** | Template engine | Jinja2 | None | All modules |
| **`tests`** | Test infrastructure | pytest | All modules | Developers |
| **`agentic_memory`** | Long-term agent memory, **compression** | vector stores | logging_monitoring, llm | agents, cerebrum |
| **`audio`** | Audio processing & transcription | whisper, pydub | logging_monitoring | llm |
| **`bio_simulation`** | Ant colony simulation | numpy | logging_monitoring | data_visualization, examples |
| **`collaboration`** | Multi-agent collaboration | events, agents | logging_monitoring, agents, events | agents, orchestrator |
| **`concurrency`** | Distributed synchronization, **channels**, **rate limiting** | threading, asyncio | logging_monitoring | All modules |
| **`dark`** | Dark mode & PDF processing | PyMuPDF, Pillow | logging_monitoring | documents |
| **`defense`** | Active defense systems | security, encryption | logging_monitoring, security, encryption | identity, privacy |
| **`dependency_injection`** | IoC container & lifecycle | None | None | All modules |
| **`deployment`** | Deployment strategies | cloud SDKs | logging_monitoring, containerization, cloud | ci_cd_automation |
| **`edge_computing`** | Edge deployment & IoT | MQTT, gRPC | logging_monitoring, networking | deployment, cloud |
| **`embodiment`** | Physical/robotic integration | hardware drivers | logging_monitoring, spatial | physical_management |
| **`evolutionary_ai`** | Genetic algorithms | numpy, scipy | logging_monitoring | bio_simulation, model_ops |
| **`examples`** | Code examples & templates | All modules | All modules | Developers |
| **`exceptions`** | Centralized exception hierarchy | None | None | All modules |
| **`feature_flags`** | Feature toggle management | config_management | logging_monitoring, config_management | All modules |
| **`finance`** | Financial operations | decimal, pandas | logging_monitoring, database_management | data_visualization, examples |
| **`graph_rag`** | Knowledge graph RAG | networkx, llm | logging_monitoring, llm, vector_store | agents, cerebrum |
| **`identity`** | 3-Tier personas & verification | encryption, auth | logging_monitoring, encryption, auth | defense, wallet, privacy |
| **`market`** | Anonymous markets | privacy | logging_monitoring, privacy | wallet |
| **`meme`** | Information dynamics | networkx, llm | logging_monitoring, llm | data_visualization, examples |
| **`model_ops`** | ML operations, **evaluation**, **registry**, **optimization**, **feature store** | mlflow | logging_monitoring | llm |
| **`orchestrator`** | Workflow execution, **scheduling** | events, concurrency | logging_monitoring, events, concurrency | All modules |
| **`privacy`** | Crumb scrubbing & mixnets | encryption | logging_monitoring, encryption | identity, defense |
| **`prompt_engineering`** | Prompt management, **A/B testing** | llm, templating | logging_monitoring, llm, templating | agents |
| **`quantum`** | Quantum algorithm primitives | numpy, cirq | logging_monitoring | examples, evolutionary_ai |
| **`relations`** | CRM & social graphs | networkx | logging_monitoring, database_management | data_visualization, examples |
| **`search`** | Full-text search, **hybrid BM25+semantic** | TF-IDF, fuzzy | logging_monitoring | documents, database_management |
| **`telemetry`** | OpenTelemetry tracing, **metrics**, **dashboards** | opentelemetry | logging_monitoring | performance |
| **`testing`** | Test fixtures, generators, **workflow testing**, **chaos engineering** | pytest, factory | logging_monitoring | tests, Developers |
| **`tool_use`** | Tool registry & composition | validation | logging_monitoring, validation | agents, orchestrator |
| **`tree_sitter`** | AST parsing & analysis | tree-sitter | logging_monitoring | coding |
| **`vector_store`** | Embeddings storage | faiss, chromadb | logging_monitoring, llm | graph_rag, agentic_memory |
| **`video`** | Video processing | ffmpeg, opencv | logging_monitoring | llm, documents |
| **`wallet`** | Self-custody, recovery, **smart contracts** | encryption | logging_monitoring, encryption | identity, market |

## 🔄 Core Data Flow Patterns

### **1. Development Workflow Integration**

```mermaid
graph LR
    subgraph "Primary Workflow"
        UserCode["User Code"]
        CodingAnalysis["Coding Module<br/>(static analysis + patterns)"]
        CICD["CI/CD Automation<br/>(incl. build)"]

        UserCode --> CodingAnalysis
        CodingAnalysis --> CICD
    end

    subgraph "Supporting Services"
        AICode["AI Agents<br/>& Benchmarks"]
        GitOps["Git Operations<br/>& Merge Resolution"]

        UserCode --> AICode
        CICD --> GitOps
    end
```

### **2. AI-Powered Development Cycle**

```mermaid
graph TD
    CodeInput["Code Input"]

    Coding["Coding Module<br/>(static analysis + pattern matching)"]
    AICode["AI Agents<br/>Enhancement"]
    CodeExec["Code Execution<br/>Validation"]
    DataViz["Data Visualization<br/>& Export"]

    CodeInput --> Coding
    Coding --> AICode
    AICode --> CodeExec
    AICode --> DataViz
```

**Related Documentation**:

- **[System Architecture](../project/architecture.md)**: Overall system design
- **[Module Overview](./overview.md)**: Module architecture principles
- **[API Reference](../reference/api.md)**: Module APIs and integration patterns

## 🔗 Detailed Module Relationships

### **🔧 Foundation Modules (Used by All)**

#### **`environment_setup` → All Modules**

- **Provides**: Dependency validation, environment variables, API key management
- **Integration Points**:

  ```python
  # Every module imports this for setup validation
  from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

  # Called at module initialization
  ensure_dependencies_installed()
  ```

#### **`logging_monitoring` → All Modules**

- **Provides**: Standardized logging interface, structured logging
- **Integration Points**:

  ```python
  # Universal logging interface across all modules
  from codomyrmex.logging_monitoring.logger_config import get_logger
  logger = get_logger(__name__)

  # Consistent log format across entire project
  logger.info("Module operation completed")
  ```

#### **`model_context_protocol` → AI Modules**

- **Provides**: Standardized communication with AI agents
- **Integration Points**:

  ```python
  # AI modules implement MCP tools
  from codomyrmex.model_context_protocol.mcp_schemas import MCPToolCall, MCPToolResult

  # Standardized request/response format
  tool_call = MCPToolCall(tool_name="agents.generate_code", arguments={...})
  ```

### **🤖 AI & Intelligence Modules**

#### **`agents` Integration Points**

- **Consumes**: `logging_monitoring`, `environment_setup`, `model_context_protocol`
- **Provides**: Code generation, refactoring, summarization
- **Cross-Module Usage**:

  ```python
  # Used by pattern_matching for code understanding
  from codomyrmex.agents.ai_code_helpers import generate_code

  # Used by documentation for example generation
  result = generate_code("Create a hello world function", "python")
  ```

#### **`coding.pattern_matching` Integration Points**

- **Consumes**: `logging_monitoring`, `environment_setup`, `agents`
- **Provides**: Code analysis, pattern recognition, dependency mapping
- **Now a sub-module of `coding`**
- **Cross-Module Usage**:

  ```python
  # Pattern matching is now part of the coding module
  from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import analyze_repository_path

  # Comprehensive analysis workflow
  analysis_results = analyze_repository_path(repo_path="./src", output_dir="./analysis")
  ```

### **🔍 Analysis & Quality Modules**

#### **`coding.static_analysis` Integration Points**

- **Consumes**: `logging_monitoring`
- **Provides**: Code quality metrics, security scanning, linting
- **Now a sub-module of `coding`**
- **Cross-Module Usage**:

  ```python
  # Static analysis is now part of the coding module
  from codomyrmex.coding.static_analysis.pyrefly_runner import run_pyrefly_analysis

  # Quality check before build
  issues = run_pyrefly_analysis(target_paths=["src/"], project_root=".")
  ```

#### **`code` Integration Points**

- **Consumes**: `logging_monitoring`
- **Provides**: Code execution, sandboxing, review, and monitoring
- **Submodules**: `execution`, `sandbox`, `review`, `monitoring`
- **Cross-Module Usage**:

  ```python
  # Used by agents for code validation
  from codomyrmex.coding import execute_code

  # Test generated code before applying
  result = execute_code(language="python", code="print('test')")
  
  # Code review integration
  from codomyrmex.coding.review import CodeReviewer, analyze_file
  reviewer = CodeReviewer()
  results = analyze_file("path/to/file.py")
  ```

### **🏗️ Build & Deployment Modules**

#### **`ci_cd_automation.build` Integration Points**

- **Consumes**: `coding.static_analysis`, `logging_monitoring`, `git_operations`
- **Provides**: Automated building, code scaffolding, deployment
- **Now a sub-module of `ci_cd_automation`**
- **Cross-Module Usage**:

  ```python
  # Build automation is now part of ci_cd_automation
  from codomyrmex.ci_cd_automation.build.build_orchestrator import orchestrate_build_pipeline
  from codomyrmex.coding.static_analysis.pyrefly_runner import run_pyrefly_analysis

  # Complete build workflow
  build_config = {"target": "python_wheel", "clean": True}
  result = orchestrate_build_pipeline(build_config)

  # Quality-gated build process
  analysis = run_pyrefly_analysis(paths, root)
  if not analysis["issues"]:
      build_result = trigger_build("production")
  ```

#### **`git_operations` Integration Points**

- **Consumes**: `logging_monitoring`
- **Provides**: Git workflow automation, repository management
- **Cross-Module Usage**:

  ```python
  # Used by ci_cd_automation.build for version control integration
  from codomyrmex.git_operations.git_wrapper import create_branch, commit_changes

  # Automated release workflow
  create_branch("release/v1.0.0")
  commit_changes("Release version 1.0.0")
  ```

### **📊 Visualization & Reporting Modules**

#### **`data_visualization` Integration Points**

- **Consumes**: `logging_monitoring`
- **Provides**: Charts, plots, data visualization
- **Cross-Module Usage**:

  ```python
  # Used by coding.pattern_matching for analysis visualization
  from codomyrmex.data_visualization.plotter import create_heatmap
  from codomyrmex.coding.pattern_matching.run_codomyrmex_analysis import analyze_repository_path

  # Visualize analysis results
  analysis = analyze_repository_path(path, config)
  create_heatmap(analysis["dependency_matrix"], title="Code Dependencies")
  ```

#### **`documentation` Integration Points**

- **Consumes**: All modules (meta-module)
- **Provides**: Comprehensive documentation website, API references
- **Cross-Module Usage**:

  ```python
  # Generates documentation from all modules
  from codomyrmex.documentation.documentation_website import build_static_site

  # Auto-generate docs from module APIs
  build_static_site()
  ```

### **🧠 Advanced AI & ML Modules**

#### **`cerebrum` Integration Points**

- **Consumes**: `logging_monitoring`, `llm`
- **Provides**: Case-based reasoning, cognitive architecture
- **Cross-Module Usage**:

  ```python
  from codomyrmex.cerebrum import CaseLibrary, CBREngine

  # Build reasoning engine from prior cases
  library = CaseLibrary()
  engine = CBREngine(library)
  solution = engine.retrieve_and_adapt(problem_description)
  ```

#### **`graph_rag` Integration Points**

- **Consumes**: `logging_monitoring`, `llm`, `vector_store`
- **Provides**: Knowledge graph construction, graph-based RAG retrieval
- **Cross-Module Usage**:

  ```python
  from codomyrmex.graph_rag import KnowledgeGraph, GraphRAGRetriever
  from codomyrmex.vector_store import VectorStore

  # Build knowledge graph from documents, then query with RAG
  kg = KnowledgeGraph()
  retriever = GraphRAGRetriever(kg, vector_store=VectorStore())
  context = retriever.query("How do modules interact?")
  ```

#### **`agentic_memory` Integration Points**

- **Consumes**: `logging_monitoring`, `llm`, `vector_store`
- **Provides**: Long-term agent memory, episodic recall
- **Cross-Module Usage**:

  ```python
  from codomyrmex.agentic_memory import MemoryStore, EpisodicMemory

  # Agents persist and recall information across sessions
  memory = MemoryStore()
  memory.store(episode="Resolved merge conflict in auth module")
  relevant = memory.recall("authentication issues")
  ```

#### **`prompt_engineering` Integration Points**

- **Consumes**: `logging_monitoring`, `llm`, `templating`
- **Provides**: Prompt templates, chain-of-thought patterns, few-shot construction
- **Cross-Module Usage**:

  ```python
  from codomyrmex.prompt_engineering import PromptTemplate, PromptChain

  # Build reusable prompt templates for agents
  template = PromptTemplate("Analyze {code} for {language} best practices")
  result = template.render(code=source, language="python")
  ```

#### **`model_ops.evaluation` Integration Points**

- **Consumes**: `logging_monitoring`, `llm`, `telemetry.metrics`
- **Provides**: LLM output scoring, benchmark suites, A/B comparison
- **Now a sub-module of `model_ops`**
- **Cross-Module Usage**:

  ```python
  from codomyrmex.model_ops.evaluation import Evaluator, BenchmarkSuite

  # Score LLM outputs against reference answers
  evaluator = Evaluator(metrics=["bleu", "rouge", "semantic_similarity"])
  scores = evaluator.evaluate(predictions, references)
  ```

#### **`model_ops.optimization` Integration Points**

- **Consumes**: `logging_monitoring`, `llm`
- **Provides**: Model quantization, ONNX export, inference acceleration
- **Now a sub-module of `model_ops`**
- **Cross-Module Usage**:

  ```python
  from codomyrmex.model_ops.optimization import optimize_model, quantize

  # Optimize model for production inference
  optimized = optimize_model(model_path, target="onnx")
  quantized = quantize(optimized, precision="int8")
  ```

### **⚙️ Infrastructure & Runtime Modules**

#### **`concurrency` Integration Points**

- **Consumes**: `logging_monitoring`
- **Provides**: Thread pools, async coordination, distributed locks
- **Cross-Module Usage**:

  ```python
  from codomyrmex.concurrency import TaskPool, DistributedLock

  # Parallel execution with coordination
  pool = TaskPool(max_workers=8)
  results = pool.map(process_item, items)
  ```

#### **`cache` Integration Points**

- **Consumes**: `logging_monitoring`
- **Provides**: In-memory and distributed caching, TTL policies
- **Cross-Module Usage**:

  ```python
  from codomyrmex.cache import CacheManager, cache_result

  # Cache expensive computations
  @cache_result(ttl=3600)
  def expensive_analysis(repo_path):
      return analyze_repository(repo_path)
  ```

#### **`events` Integration Points**

- **Consumes**: `logging_monitoring`
- **Provides**: Event bus, pub/sub, async event handling
- **Cross-Module Usage**:

  ```python
  from codomyrmex.events import EventBus, subscribe

  # Cross-module event communication
  bus = EventBus()
  bus.subscribe("build.completed", on_build_complete)
  bus.publish("build.completed", {"status": "success"})
  ```

#### **`orchestrator` Integration Points** (includes scheduler)

- **Consumes**: `logging_monitoring`, `events`, `concurrency`
- **Provides**: Workflow definition, step sequencing, error recovery, **cron-like scheduling**
- **Cross-Module Usage**:

  ```python
  from codomyrmex.orchestrator import Workflow, Step
  from codomyrmex.orchestrator.scheduler import Scheduler, CronTrigger

  # Define multi-step workflows
  workflow = Workflow("deploy_pipeline")
  workflow.add_step(Step("test", run_tests))
  workflow.add_step(Step("build", build_artifacts, depends_on="test"))
  workflow.add_step(Step("deploy", deploy, depends_on="build"))
  workflow.execute()

  # Schedule recurring analysis
  scheduler = Scheduler()
  scheduler.add_job(run_analysis, CronTrigger(hour=2))
  scheduler.start()
  ```

#### **`networking` Integration Points** (includes service_mesh)

- **Consumes**: `logging_monitoring`
- **Provides**: HTTP clients, WebSocket support, diagnostics, **circuit breakers, load balancing**
- **Cross-Module Usage**:

  ```python
  from codomyrmex.networking.service_mesh import CircuitBreaker, RetryPolicy

  # Resilient external service calls
  breaker = CircuitBreaker(failure_threshold=5, reset_timeout=30)
  result = breaker.call(external_api, request_data)
  ```

### **🔐 Security & Identity Modules**

#### **`security` Integration Points**

- **Consumes**: `logging_monitoring`, `coding.static_analysis`
- **Provides**: Vulnerability scanning, threat modeling, secrets detection, **governance**
- **Cross-Module Usage**:

  ```python
  from codomyrmex.security import scan_for_vulnerabilities, ThreatModel

  # Security scanning in CI/CD
  vulnerabilities = scan_for_vulnerabilities(repo_path=".")
  model = ThreatModel(application="web_api")
  threats = model.analyze()
  ```

#### **`identity` / `privacy` / `defense` Integration Points**

- **identity** → `encryption`, `auth` → provides persona management, verification
- **privacy** → `encryption` → provides data scrubbing, anonymization
- **defense** → `security`, `encryption` → provides active defense, intrusion detection
- **Cross-Module Usage**:

  ```python
  from codomyrmex.identity import PersonaManager
  from codomyrmex.privacy import DataScrubber
  from codomyrmex.defense import IntrusionDetector

  # Layered security architecture
  persona = PersonaManager().get_active_persona()
  scrubbed = DataScrubber().scrub(sensitive_data)
  detector = IntrusionDetector(alert_callback=notify_admin)
  ```

#### **`encryption` Integration Points**

- **Consumes**: `logging_monitoring`
- **Provides**: Symmetric/asymmetric encryption, key management, hashing
- **Cross-Module Usage**:

  ```python
  from codomyrmex.encryption import encrypt, decrypt, KeyManager

  # Used by identity, privacy, defense, wallet modules
  key_mgr = KeyManager()
  encrypted = encrypt(data, key_mgr.get_key("primary"))
  ```

### **☁️ Cloud & Deployment Modules**

#### **`cloud` Integration Points**

- **Consumes**: `logging_monitoring`, `config_management`
- **Provides**: Multi-cloud abstractions, storage, compute
- **Cross-Module Usage**:

  ```python
  from codomyrmex.cloud import CloudProvider, StorageClient

  # Cloud-agnostic resource management
  provider = CloudProvider.from_config()
  storage = StorageClient(provider)
  storage.upload("artifacts/build.tar.gz", bucket="releases")
  ```

#### **`containerization` Integration Points**

- **Consumes**: `logging_monitoring`
- **Provides**: Docker/K8s management, image building
- **Cross-Module Usage**:

  ```python
  from codomyrmex.containerization import DockerManager, K8sClient

  # Build and deploy containers
  docker = DockerManager()
  image = docker.build(".", tag="codomyrmex:latest")
  K8sClient().deploy(image, namespace="production")
  ```

#### **`deployment` Integration Points**

- **Consumes**: `logging_monitoring`, `containerization`, `cloud`
- **Provides**: Blue-green, canary, rolling deployment strategies
- **Cross-Module Usage**:

  ```python
  from codomyrmex.deployment import DeploymentStrategy, CanaryDeploy

  # Canary deployment with automatic rollback
  strategy = CanaryDeploy(initial_percent=5, step_percent=10)
  strategy.execute(image="codomyrmex:latest", health_check=check_health)
  ```

## 🔄 Common Integration Patterns

### **1. Initialization Sequence**

```python
# Standard module initialization pattern used across all modules
from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed
from codomyrmex.logging_monitoring import get_logger

# 1. Validate environment
ensure_dependencies_installed()

# 2. Setup logging
logger = get_logger(__name__)

# 3. Module-specific initialization
# ... module specific setup ...
```

### **2. Error Handling Chain**

```python
# Consistent error handling across modules
try:
    result = perform_operation()
    logger.info(f"Operation completed: {result}")
except ModuleSpecificError as e:
    logger.error(f"Module error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

### **3. Configuration Sharing**

```python
# Environment variables shared across modules
import os
from codomyrmex.environment_setup.env_checker import check_and_setup_env_vars

# Ensure .env is loaded
check_and_setup_env_vars("/path/to/project")

# Shared configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

## 📋 Module Compatibility Matrix

```mermaid
graph LR
    subgraph "Module Compatibility & Dependencies"
        subgraph "Foundation Layer (Required by All)"
            ENV["environment_setup"]
            LOG["logging_monitoring"]
            MCP["model_context_protocol"]
        end

        subgraph "AI & Intelligence Layer"
            AI["agents"]
            MOPS["model_ops"]
        end

        subgraph "Analysis & Quality Layer"
            CODE["coding (static_analysis, patterns)"]
            SEC["security (governance)"]
        end

        subgraph "Build & Deploy Layer"
            CICD["ci_cd_automation (build)"]
            GIT["git_operations"]
            DOCS["documentation (education)"]
        end

        subgraph "Visualization Layer"
            VIZ["data_visualization"]
        end
    end

    %% Foundation dependencies (dotted lines)
    AI -.-> ENV
    AI -.-> LOG
    AI -.-> MCP

    MOPS -.-> LOG

    CODE -.-> LOG
    SEC -.-> LOG

    CICD -.-> LOG
    GIT -.-> LOG
    DOCS -.-> LOG

    VIZ -.-> LOG

    %% Functional dependencies (solid lines)
    AI --> CODE
    SEC --> CODE
    CICD --> GIT
    CICD --> DOCS
```

### **Dependency Matrix Table**

**Key Modules Dependency Matrix** (showing core module dependencies, post-consolidation):

| Consumer Module | environment_setup | logging_monitoring | model_context_protocol | agents | data_visualization | coding | security | git_operations | ci_cd_automation | documentation |
|-----------------|-------------------|-------------------|-------------------------|----------------|-------------------|--------|----------|---------------|-----------------|---------------|
| **environment_setup** | ✅ Self | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **logging_monitoring** | ❌ | ✅ Self | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **model_context_protocol** | ❌ | ❌ | ✅ Self | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **config_management** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **database_management** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **llm** | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **agents** | ✅ | ✅ | ✅ | ✅ Self | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| **data_visualization** | ❌ | ✅ | ❌ | ❌ | ✅ Self | ✅ | ❌ | ❌ | ❌ | ✅ |
| **coding** | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ Self | ❌ | ❌ | ❌ | ✅ |
| **security** | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ Self | ❌ | ❌ | ✅ |
| **ci_cd_automation** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Self | ✅ |
| **orchestrator** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **documentation** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ Self |
| **model_ops** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **testing** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Legend:**

- ✅ **Required**: Module cannot function without this dependency
- 🔄 **Optional**: Module can use this for enhanced functionality
- ❌ **None**: No direct dependency

**Related Documentation:**

- **[System Architecture](../project/architecture.md)**: Overall system design and principles
- **[Module Overview](./overview.md)**: Module architecture and organization
- **[API Reference](../reference/api.md)**: Module APIs and programmatic interfaces
- **[Contributing Guide](../project/contributing.md)**: Adding new modules and maintaining dependencies

## 🚀 Quick Integration Examples

### **Adding AI Enhancement to Any Module**

```python
from codomyrmex.agents.ai_code_helpers import generate_code_snippet
from codomyrmex.model_context_protocol.mcp_schemas import MCPToolCall

def enhance_code_with_ai(code_snippet, enhancement_request):
    """Add AI enhancement capability to any module"""
    result = generate_code_snippet(
        prompt=f"Enhance this code: {enhancement_request}",
        language="python",
        context_code=code_snippet
    )
    return result
```

### **Adding Visualization to Analysis Results**

```python
from codomyrmex.data_visualization.plotter import create_bar_chart
from codomyrmex.coding.static_analysis.pyrefly_runner import run_pyrefly_analysis

def visualize_analysis_results(target_paths, project_root):
    """Create visual representation of analysis results"""
    analysis = run_pyrefly_analysis(target_paths, project_root)

    # Extract issue counts by severity
    severity_counts = {}
    for issue in analysis["issues"]:
        severity = issue.get("severity", "unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    # Create visualization
    create_bar_chart(
        categories=list(severity_counts.keys()),
        values=list(severity_counts.values()),
        title="Code Analysis Issues by Severity",
        x_label="Severity Level",
        y_label="Issue Count",
        output_path="analysis_report.png"
    )
```

### **Creating a Complete Workflow**

```python
from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed
from codomyrmex.logging_monitoring import get_logger
from codomyrmex.agents.ai_code_helpers import generate_code_snippet
from codomyrmex.coding.code_executor import execute_code
from codomyrmex.data_visualization.plotter import create_line_plot

def complete_development_workflow():
    """Complete workflow using multiple modules"""
    # 1. Setup
    ensure_dependencies_installed()
    logger = get_logger(__name__)

    # 2. Generate code with AI
    code_result = generate_code_snippet(
        "Create a function to calculate fibonacci numbers",
        "python"
    )

    # 3. Test the generated code
    if code_result["status"] == "success":
        exec_result = execute_code(
            "python",
            code_result["generated_code"],
            stdin="10"
        )

        # 4. Visualize results
        create_line_plot(
            x_data=list(range(10)),
            y_data=[int(x) for x in exec_result["output"].split()],
            title="Fibonacci Sequence",
            output_path="fibonacci_plot.png"
        )

        logger.info("Complete workflow executed successfully")
    else:
        logger.error("Code generation failed")
```

This comprehensive integration guide shows how Codomyrmex modules work together to create powerful, interconnected development workflows.

## Navigation Links

- **Parent**: [docs](../README.md)
- **Module Index**: [AGENTS.md](../AGENTS.md)
- **Home**: [Repository Root](../../README.md)
