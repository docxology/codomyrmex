# Codomyrmex

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-≥3.10-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/codomyrmex/codomyrmex)

**Version**: 0.1.0 | **License**: MIT | **Python**: ≥3.10

A modular, extensible coding workspace designed for AI development workflows. Codomyrmex integrates tools for building, documenting, analyzing, executing, and visualizing code across multiple languages.

## Overview

Codomyrmex provides a suite of development tools organized as independent, composable modules. Each module offers specific functionality while maintaining clear interfaces and minimal coupling, enabling flexible composition and easy extensibility.

**Key Design Principles**:
- **Modularity First**: Self-contained modules with clear boundaries
- **AI Integration**: Built-in support for Large Language Models via Model Context Protocol (MCP)
- **Polyglot Support**: Language-agnostic interfaces with pluggable implementations
- **Professional Quality**: Testing, documentation, and security practices

<details>
<summary><strong>Table of Contents</strong></summary>

- [Quick Navigation](#quick-navigation)
- [System Architecture](#system-architecture)
  - [Module Dependency Graph](#module-dependency-graph)
  - [Workflow Execution Architecture](#workflow-execution-architecture)
  - [Multi-Stage Build Architecture](#multi-stage-build-architecture)
- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
  - [Getting Started Workflow](#getting-started-workflow)
- [Architecture](#architecture)
  - [Layered Design Principles](#layered-design-principles)
- [Core Modules](#core-modules)
  - [Foundation Layer](#foundation-layer)
  - [Core Functional Modules](#core-functional-modules)
  - [Service Modules](#service-modules)
  - [Specialized Modules](#specialized-modules)
- [Explore Modules](#explore-modules)
- [Module Quick Reference](#module-quick-reference)
- [Common Use Cases](#common-use-cases)
- [Project Structure](#project-structure)
- [Key Concepts](#key-concepts)
- [Documentation](#documentation)
- [Development](#development)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)
- [Data Flow Architecture](#data-flow-architecture)
- [Module Interaction Workflow](#module-interaction-workflow)
- [Development Workflow Architecture](#development-workflow-architecture)
- [Dependencies Overview](#dependencies-overview)
- [Module Maturity Levels](#module-maturity-levels)
- [Key Metrics](#key-metrics)
- [Links](#links)

</details>

## Quick Navigation

**Get Started Quickly:**
- 📚 **[Source Code](src/README.md)** - Browse all modules and implementations
- 📖 **[Documentation Hub](docs/README.md)** - User guides and developer documentation
- 🚀 **[Quick Start Guide](docs/getting-started/quickstart.md)** - Get up and running in 5 minutes
- 🏗️ **[Module Overview](docs/modules/overview.md)** - Understand the module system
- 🎯 **[Architecture Guide](docs/project/architecture.md)** - System design and principles

## System Architecture

```mermaid
graph TB
    subgraph userInterfaces ["User Interfaces"]
        CLI["CLI (codomyrmex)"]
        Shell["Interactive Shell"]
        API["API Endpoints (FastAPI)"]
    end

    subgraph coreServices ["Core Services Layer"]
        Discovery["System Discovery"]
        Status["Status Reporting"]
        Terminal["Interactive Terminal"]
    end

    subgraph aiIntelligence ["Module Layer - AI & Intelligence"]
        AICode["AI Code Editing"]
        MCP["Model Context Protocol"]
        LLM["LLM Infrastructure"]
    end

    subgraph analysisQuality ["Module Layer - Analysis & Quality"]
        StaticAnalysis["Static Analysis"]
        PatternMatch["Pattern Matching"]
        Coding["Coding & Review"]
        Security["Security"]
        Perf["Performance Monitoring"]
    end

    subgraph buildDeploy ["Module Layer - Build & Deploy"]
        Build["Build Synthesis"]
        Git["Git Operations"]
        Docs["Documentation Generation"]
        APIDocs["API Documentation"]
        APIStd["API Standardization"]
        CICDAuto["CI/CD Automation"]
        Container["Container Management"]
    end

    subgraph visualizationData ["Module Layer - Visualization & Data"]
        DataViz["Data Visualization"]
        Spatial["Spatial (3D/4D)"]
    end

    subgraph infrastructure ["Module Layer - Infrastructure"]
        Database["Database Management"]
        ConfigMgmt["Config Management"]
        PhysMgmt["Physical Management"]
        Events["Event System"]
        PluginSys["Plugin System"]
    end

    subgraph extensions ["Module Layer - Extensions"]
        ModTemplate["Module Template"]
        Tools["Utility Tools"]
        SysDiscovery["System Discovery"]
    end

    subgraph foundation ["Foundation Layer"]
        Logging["Logging & Monitoring"]
        Environment["Environment Setup"]
        TerminalInterface["Terminal Interface"]
    end

    %% User Interface connections
    CLI --> Discovery
    Shell --> Terminal
    API --> Status

    %% Service Layer connections
    Discovery --> AICode
    Discovery --> StaticAnalysis
    Discovery --> Build
    Status --> DataViz
    Terminal --> Shell

    %% Module interconnections
    AICode --> Coding
    AICode --> MCP
    AICode --> Ollama
    AICode --> LLM
    StaticAnalysis --> Build
    StaticAnalysis --> PatternMatch
    StaticAnalysis --> Coding
    StaticAnalysis --> Security
    PatternMatch --> AICode
    PatternMatch --> Coding
    Perf --> Coding
    Perf --> Build
    Perf --> CICDAuto
    Build --> Git
    Build --> Docs
    Build --> APIDocs
    Build --> APIStd
    Build --> CICDAuto
    Build --> Container
    Docs --> StaticAnalysis
    APIDocs --> APIStd
    CICDAuto --> Build
    CICDAuto --> Security
    Container --> PhysMgmt
    Container --> Events
    DataViz --> Spatial
    Database --> Build
    Database --> Events
    ConfigMgmt --> Environment
    Events --> PluginSys
    PluginSys --> ModTemplate
    SysDiscovery --> ModTemplate
    SysDiscovery --> Tools
    DataViz --> Spatial
    DataViz --> Spatial
    DataViz --> Spatial
    DataViz --> Spatial
    DataViz --> Spatial

    %% Foundation connections (all modules depend on foundation)
    AICode -.-> Logging
    StaticAnalysis -.-> Logging
    Coding -.-> Logging
    Coding -.-> Logging
    Security -.-> Logging
    Perf -.-> Logging
    Build -.-> Logging
    Git -.-> Logging
    Docs -.-> Logging
    APIDocs -.-> Logging
    APIStd -.-> Logging
    CICDAuto -.-> Logging
    Container -.-> Logging
    DataViz -.-> Logging
    Spatial -.-> Logging
    Database -.-> Logging
    ConfigMgmt -.-> Logging
    PhysMgmt -.-> Logging
    Events -.-> Logging
    PluginSys -.-> Logging
    ModTemplate -.-> Logging
    Tools -.-> Logging
    SysDiscovery -.-> Logging
    Discovery -.-> Logging
    Status -.-> Logging
    Terminal -.-> Logging

    AICode -.-> Environment
    StaticAnalysis -.-> Environment
    Coding -.-> Environment
    Coding -.-> Environment
    Security -.-> Environment
    Perf -.-> Environment
    Build -.-> Environment
    Git -.-> Environment
    Docs -.-> Environment
    APIDocs -.-> Environment
    APIStd -.-> Environment
    CICDAuto -.-> Environment
    Container -.-> Environment
    DataViz -.-> Environment
    Spatial -.-> Environment
    Database -.-> Environment
    ConfigMgmt -.-> Environment
    PhysMgmt -.-> Environment
    Events -.-> Environment
    PluginSys -.-> Environment
    ModTemplate -.-> Environment
    Tools -.-> Environment
    SysDiscovery -.-> Environment
    Discovery -.-> Environment
    Status -.-> Environment
    Terminal -.-> Environment

    AICode -.-> TerminalInterface
    MCP -.-> TerminalInterface
    Ollama -.-> TerminalInterface
    LLM -.-> TerminalInterface
    Discovery -.-> TerminalInterface
    Status -.-> TerminalInterface
    Terminal -.-> TerminalInterface
    Events -.-> TerminalInterface
    PluginSys -.-> TerminalInterface
    SysDiscovery -.-> TerminalInterface
```

### Module Dependency Graph

```mermaid
graph TD
    subgraph foundation ["Foundation Layer"]
        Logging["logging_monitoring"]
        Env["environment_setup"]
        MCP["model_context_protocol"]
        Terminal["terminal_interface"]
    end

    subgraph core ["Core Layer"]
        Agents["agents"]
        StaticAnalysis["static_analysis"]
        Coding["coding"]
        DataViz["data_visualization"]
        PatternMatch["pattern_matching"]
        GitOps["git_operations"]
        Security["security"]
        LLM["llm"]
        Performance["performance"]
    end

    subgraph service ["Service Layer"]
        BuildSynth["build_synthesis"]
        Documentation["documentation"]
        API["api"]
        CICD["ci_cd_automation"]
        Container["containerization"]
        ConfigMgmt["config_management"]
        Database["database_management"]
        ProjectOrch["project_orchestration"]
        PhysMgmt["physical_management"]
    end

    subgraph specialized ["Specialized Layer"]
        SysDiscovery["system_discovery"]
        ModuleTemplate["module_template"]
        Spatial["spatial"]
        Events["events"]
        PluginSys["plugin_system"]
        Tools["tools"]
    end

    %% Foundation dependencies (minimal)
    Env --> Logging

    %% Core layer dependencies
    Logging --> Agents
    Logging --> StaticAnalysis
    Logging --> Coding
    Logging --> DataViz
    Logging --> PatternMatch
    Logging --> GitOps
    Logging --> Security
    Logging --> LLM
    Logging --> Performance

    Env --> Agents
    Env --> Coding
    Env --> Security
    Env --> Performance

    MCP --> Agents
    MCP --> LLM

    Terminal --> Agents
    Terminal --> Coding

    StaticAnalysis --> Coding
    PatternMatch --> Coding
    Security --> Coding

    %% Service layer dependencies
    Logging --> BuildSynth
    Logging --> Documentation
    Logging --> API
    Logging --> CICD
    Logging --> Container
    Logging --> ConfigMgmt
    Logging --> Database
    Logging --> ProjectOrch
    Logging --> PhysMgmt

    Env --> BuildSynth
    Env --> CICD
    Env --> Container
    Env --> ConfigMgmt
    Env --> Database
    Env --> PhysMgmt

    Agents --> BuildSynth
    Agents --> Documentation
    Agents --> ProjectOrch

    StaticAnalysis --> BuildSynth
    StaticAnalysis --> CICD

    Code --> BuildSynth
    Coding --> BuildSynth
    Coding --> CICD

    DataViz --> Documentation
    DataViz --> API

    GitOps --> BuildSynth
    GitOps --> CICD
    GitOps --> ProjectOrch

    Security --> CICD
    Security --> Container

    Performance --> CICD
    Performance --> Container

    BuildSynth --> ProjectOrch
    Documentation --> ProjectOrch
    CICD --> ProjectOrch
    Container --> ProjectOrch
    ConfigMgmt --> ProjectOrch
    Database --> ProjectOrch

    %% Specialized layer dependencies
    Logging --> SysDiscovery
    Logging --> ModuleTemplate
    Logging --> Spatial
    Logging --> Events
    Logging --> PluginSys
    Logging --> Tools

    Env --> SysDiscovery
    Env --> ModuleTemplate
    Env --> Events
    Env --> PluginSys

    SysDiscovery --> ModuleTemplate
    SysDiscovery --> Tools
    DataViz --> Spatial
    Events --> PluginSys
    PluginSys --> ModuleTemplate
```

### Workflow Execution Architecture

```mermaid
graph TD
    User[👤 User Request] --> Orchestrator[🎯 Project Orchestrator]

    Orchestrator --> DAGBuilder[DAG Builder]
    DAGBuilder --> WorkflowDAG[Workflow DAG]

    WorkflowDAG --> ParallelExecutor[Parallel Executor]
    ParallelExecutor --> TaskRunner1[Task Runner 1]
    ParallelExecutor --> TaskRunner2[Task Runner 2]
    ParallelExecutor --> TaskRunner3[Task Runner 3]

    TaskRunner1 --> Module1[Codomyrmex Module]
    TaskRunner2 --> Module2[Codomyrmex Module]
    TaskRunner3 --> Module3[Codomyrmex Module]

    Module1 --> Results1{Results}
    Module2 --> Results2{Results}
    Module3 --> Results3{Results}

    Results1 --> Aggregator[Result Aggregator]
    Results2 --> Aggregator
    Results3 --> Aggregator

    Aggregator --> Reporter[📊 Status Reporter]
    Reporter --> User

    %% Feedback loop for iterative workflows
    Reporter --> Orchestrator
```

### Multi-Stage Build Architecture

```mermaid
graph TD
    subgraph "Source Code"
        AppCode[📁 Application Code]
        Dependencies[📦 Dependencies]
        ConfigFiles[⚙️ Configuration]
    end

    subgraph "Build Stages"
        Builder["🏗️ Builder Stage<br/>- Install dependencies<br/>- Compile code<br/>- Run tests<br/>- Create artifacts"]
        Runtime["🚀 Runtime Stage<br/>- Copy artifacts<br/>- Configure runtime<br/>- Set permissions<br/>- Define entrypoint"]
    end

    subgraph "Output"
        OptimizedImage["📦 Optimized Image<br/>- Minimal layers<br/>- Security hardened<br/>- Cached efficiently"]
    end

    AppCode --> Builder
    Dependencies --> Builder
    ConfigFiles --> Builder
    ConfigFiles --> Runtime

    Builder --> Runtime
    Runtime --> OptimizedImage

    Builder -.->|"Remove build tools<br/>Clean cache"| OptimizedImage
    Runtime -.->|"Add runtime deps<br/>Configure app"| OptimizedImage
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex

# Install with uv (recommended)
uv sync
```

### Basic Usage

```bash
# Launch interactive shell
./start_here.sh

# Or use the CLI directly
codomyrmex --help

# Discover available modules
uv run python -c "from codomyrmex.system_discovery import SystemDiscovery; SystemDiscovery().discover_modules()"
```

## Getting Started Workflow

Typical user journey with Codomyrmex:

```mermaid
flowchart TD
    Start([Start]) --> Install{Install<br/>Codomyrmex}

    Install -->|uv sync| Config[Configure<br/>Environment]
    Install -->|pip install| Config

    Config --> Setup[Environment<br/>Setup]
    Setup --> Discover[Discover<br/>Modules]

    Discover --> Choose{Choose<br/>Workflow}

    Choose -->|CLI Usage| CLI[Use CLI<br/>Commands]
    Choose -->|Interactive| Interactive[Launch<br/>Interactive Shell]
    Choose -->|API| API[Use REST<br/>API]

    CLI --> Modules[Work with<br/>Modules]
    Interactive --> Modules
    API --> Modules

    Modules --> Dev{Development<br/>Tasks}

    Dev -->|Code Analysis| Analysis[Static Analysis<br/>Code Review]
    Dev -->|Build & Deploy| Build[Build Synthesis<br/>CI/CD Automation]
    Dev -->|AI Assistance| AI[AI Code Editing<br/>Pattern Matching]
    Dev -->|Visualization| Viz[Data Visualization<br/>3D Modeling]
    Dev -->|Infrastructure| Infra[Container Management<br/>Database Operations]

    Analysis --> Extend[Extend &<br/>Customize]
    Build --> Extend
    AI --> Extend
    Viz --> Extend
    Infra --> Extend

    Extend --> Contrib{Contribute<br/>Back}

    Contrib -->|Bug Reports| Issues[File Issues<br/>in GitHub]
    Contrib -->|Features| PR[Create Pull<br/>Requests]
    Contrib -->|Documentation| Docs[Improve<br/>Documentation]

    Issues --> End([End])
    PR --> End
    Docs --> End

    Modules --> End
```

## Architecture

### Layered Design Principles

Codomyrmex follows a **layered architecture** that ensures clean separation of concerns and prevents circular dependencies. Each layer builds upon the layers below it, creating a stable foundation for complex workflows.

**Key Architectural Decisions**:
- **Upward Dependencies Only**: Higher layers depend on lower layers, never the reverse
- **Foundation Services**: Core infrastructure used by all modules
- **Clear Layer Boundaries**: Each layer has distinct responsibilities
- **Modular Composition**: Modules can be used independently or combined

**Layer Responsibilities**:
- **Foundation Layer**: Provides essential services (logging, environment, terminal, MCP)
- **Core Layer**: Implements primary development capabilities (analysis, execution, AI, visualization)
- **Service Layer**: Orchestrates complex workflows and integrations (build, docs, CI/CD, orchestration)
- **Application Layer**: User interfaces and system coordination (CLI, shell, API, discovery)

See **[detailed architecture documentation](docs/project/architecture.md)** for design principles and module relationships.

## Core Modules

Codomyrmex modules are organized in a layered architecture where higher layers depend on lower layers, preventing circular dependencies:

```mermaid
graph TD
    subgraph "Application Layer"
        InteractiveShell["Interactive<br/>Shell"]
        SystemDiscovery["System Discovery<br/>& Orchestration"]
        CLI["Command Line<br/>Interface"]
    end

    subgraph "Service Layer"
        AICodeEditing["AI Code<br/>Editing"]
        Documentation["Documentation<br/>Generation"]
        BuildSynthesis["Build<br/>Synthesis"]
        StaticAnalysis["Static Analysis<br/>& Quality"]
        ProjectOrchestration["Project<br/>Orchestration"]
        CICDAutomation["CI/CD<br/>Automation"]
        APIDocumentation["API<br/>Documentation"]
        Containerization["Container<br/>Management"]
        DatabaseManagement["Database<br/>Management"]
        ConfigManagement["Config<br/>Management"]
    end

    subgraph "Core Layer"
        CodeExecution["Code Execution<br/>Sandbox"]
        DataVisualization["Data Visualization<br/>& Plotting"]
        PatternMatching["Pattern<br/>Matching"]
        GitOperations["Git Operations<br/>& Version Control"]
        CodeReview["Code<br/>Review"]
        OllamaIntegration["Ollama<br/>Integration"]
        LanguageModels["Language<br/>Models"]
        SecurityAudit["Security<br/>Audit"]
        Performance["Performance<br/>Monitoring"]
        Spatial["Spatial<br/>(3D/4D)"]
        PhysicalManagement["Physical<br/>Management"]
    end

    subgraph "Foundation Layer"
        LoggingMonitoring["Logging &<br/>Monitoring"]
        EnvironmentSetup["Environment<br/>Setup"]
        ModelContextProtocol["Model Context<br/>Protocol"]
        TerminalInterface["Terminal<br/>Interface"]
    end

    %% Dependencies flow upward (dotted lines show "depends on")
    InteractiveShell -.-> SystemDiscovery
    CLI -.-> SystemDiscovery
    SystemDiscovery -.-> LoggingMonitoring
    SystemDiscovery -.-> EnvironmentSetup
    SystemDiscovery -.-> TerminalInterface

    AICodeEditing -.-> LoggingMonitoring
    AICodeEditing -.-> EnvironmentSetup
    AICodeEditing -.-> ModelContextProtocol
    AICodeEditing -.-> TerminalInterface
    AICodeEditing -.-> CodeExecution
    AICodeEditing -.-> PatternMatching

    Documentation -.-> LoggingMonitoring
    Documentation -.-> BuildSynthesis
    Documentation -.-> StaticAnalysis

    BuildSynthesis -.-> StaticAnalysis
    BuildSynthesis -.-> LoggingMonitoring
    BuildSynthesis -.-> GitOperations

    StaticAnalysis -.-> LoggingMonitoring
    StaticAnalysis -.-> PatternMatching
    StaticAnalysis -.-> CodeReview

    ProjectOrchestration -.-> LoggingMonitoring
    ProjectOrchestration -.-> BuildSynthesis
    ProjectOrchestration -.-> Documentation

    CICDAutomation -.-> BuildSynthesis
    CICDAutomation -.-> SecurityAudit
    CICDAutomation -.-> LoggingMonitoring

    APIDocumentation -.-> LoggingMonitoring
    APIDocumentation -.-> Documentation

    Containerization -.-> PhysicalManagement
    Containerization -.-> LoggingMonitoring

    DatabaseManagement -.-> LoggingMonitoring
    DatabaseManagement -.-> BuildSynthesis

    ConfigManagement -.-> EnvironmentSetup
    ConfigManagement -.-> LoggingMonitoring

    CodeExecution -.-> LoggingMonitoring
    DataVisualization -.-> LoggingMonitoring
    PatternMatching -.-> LoggingMonitoring
    PatternMatching -.-> EnvironmentSetup
    GitOperations -.-> LoggingMonitoring
    CodeReview -.-> LoggingMonitoring
    CodeReview -.-> StaticAnalysis
    OllamaIntegration -.-> LoggingMonitoring
    OllamaIntegration -.-> EnvironmentSetup
    LanguageModels -.-> LoggingMonitoring
    LanguageModels -.-> EnvironmentSetup
    SecurityAudit -.-> LoggingMonitoring
    Performance -.-> LoggingMonitoring
    Spatial -.-> LoggingMonitoring
    PhysicalManagement -.-> LoggingMonitoring
```

### Foundation Layer
Essential infrastructure used by all other modules:

| Module | Purpose | Key Features |
|--------|---------|-------------|
| [**logging_monitoring**](src/codomyrmex/logging_monitoring/) | Centralized logging system | Structured logging, multiple formats, aggregation |
| [**environment_setup**](src/codomyrmex/environment_setup/) | Environment validation | Dependency checking, API key management, setup automation |
| [**model_context_protocol**](src/codomyrmex/model_context_protocol/) | AI communication standard | Standardized LLM interfaces, tool specifications |
| [**terminal_interface**](src/codomyrmex/terminal_interface/) | Rich terminal interactions | Colored output, progress bars, interactive prompts |

### Core Functional Modules
Primary capabilities for development workflows:

| Module | Purpose | Key Features |
|--------|---------|-------------|
| [**agents**](src/codomyrmex/agents/) | Agentic framework integrations | AI code editing, task management, various providers |
| [**static_analysis**](src/codomyrmex/static_analysis/) | Code quality analysis | Linting, security scanning, complexity metrics |
| [**coding**](src/codomyrmex/coding/) | Code execution & review | Safe sandbox execution, automated code review |
| [**data_visualization**](src/codomyrmex/data_visualization/) | Charts and plots | Static/interactive plots, multiple formats |
| [**pattern_matching**](src/codomyrmex/pattern_matching/) | Code pattern analysis | Pattern recognition, dependency analysis |
| [**git_operations**](src/codomyrmex/git_operations/) | Version control automation | Git workflows, branch management, commit automation |
| [**security**](src/codomyrmex/security/) | Security scanning | Vulnerability detection, compliance checking, threat assessment |
| [**llm**](src/codomyrmex/llm/) | LLM infrastructure | Model management, local/remote providers (Ollama), benchmarking |
| [**performance**](src/codomyrmex/performance/) | Performance monitoring | Profiling, optimization, benchmarking |

### Service Modules
Higher-level services that orchestrate core modules:

| Module | Purpose | Key Features |
|--------|---------|-------------|
| [**build_synthesis**](src/codomyrmex/build_synthesis/) | Build automation | Multi-language builds, artifact generation, pipelines |
| [**documentation**](src/codomyrmex/documentation/) | Documentation generation | Website generation, API docs, tutorial creation |
| [**api**](src/codomyrmex/api/) | API infrastructure | OpenAPI/Swagger specs, standardization, documentation |
| [**ci_cd_automation**](src/codomyrmex/ci_cd_automation/) | CI/CD pipeline management | Pipeline orchestration, deployment automation |
| [**containerization**](src/codomyrmex/containerization/) | Container management | Docker lifecycle, Kubernetes orchestration |
| [**database_management**](src/codomyrmex/database_management/) | Database operations | Schema management, migrations, backups |
| [**config_management**](src/codomyrmex/config_management/) | Configuration management | Environment setup, secret management, validation |
| [**project_orchestration**](src/codomyrmex/project_orchestration/) | Workflow orchestration | Workflow management, task coordination |

### Specialized Modules
Advanced capabilities for specific domains:

| Module | Purpose | Key Features |
|--------|---------|-------------|
| [**spatial**](src/codomyrmex/spatial/) | Spatial modeling (3D/4D) | Scene creation, rendering, geometric operations, world models |
| [**physical_management**](src/codomyrmex/physical_management/) | Physical system simulation | Hardware monitoring, resource management |
| [**system_discovery**](src/codomyrmex/system_discovery/) | System exploration | Module discovery, capability detection, health monitoring |
| [**module_template**](src/codomyrmex/module_template/) | Module creation templates | Scaffold generation, template management |
| [**events**](src/codomyrmex/events/) | Event system | Message passing, pub/sub patterns, event logging |
| [**plugin_system**](src/codomyrmex/plugin_system/) | Plugin architecture | Extension loading, plugin management, interfaces |
| [**tools**](src/codomyrmex/tools/) | Utility tools | Development helpers, analysis utilities |

## Module Quick Reference

| Category | Modules |
|----------|---------|
| **Foundation** | [logging_monitoring](src/codomyrmex/logging_monitoring/) • [environment_setup](src/codomyrmex/environment_setup/) • [model_context_protocol](src/codomyrmex/model_context_protocol/) • [terminal_interface](src/codomyrmex/terminal_interface/) |
| **AI & Intelligence** | [agents](src/codomyrmex/agents/) • [llm](src/codomyrmex/llm/) |
| **Analysis & Quality** | [static_analysis](src/codomyrmex/static_analysis/) • [code](src/codomyrmex/coding/) • [pattern_matching](src/codomyrmex/pattern_matching/) • [security](src/codomyrmex/security/) |
| **Build & Deploy** | [build_synthesis](src/codomyrmex/build_synthesis/) • [git_operations](src/codomyrmex/git_operations/) • [ci_cd_automation](src/codomyrmex/ci_cd_automation/) • [containerization](src/codomyrmex/containerization/) |
| **Visualization** | [data_visualization](src/codomyrmex/data_visualization/) • [spatial](src/codomyrmex/spatial/) |
| **Infrastructure** | [database_management](src/codomyrmex/database_management/) • [config_management](src/codomyrmex/config_management/) • [physical_management](src/codomyrmex/physical_management/) |
| **Orchestration** | [documentation](src/codomyrmex/documentation/) • [api](src/codomyrmex/api/) • [project_orchestration](src/codomyrmex/project_orchestration/) • [system_discovery](src/codomyrmex/system_discovery/) |
| **Execution** | [coding](src/codomyrmex/coding/) • [performance](src/codomyrmex/performance/) |
| **Extensions** | [events](src/codomyrmex/events/) • [plugin_system](src/codomyrmex/plugin_system/) • [module_template](src/codomyrmex/module_template/) • [tools](src/codomyrmex/tools/) |

## Common Use Cases

### Development Workflows
- **Code Analysis Pipeline**: [Static analysis](src/codomyrmex/static_analysis/) → [Code review](src/codomyrmex/coding/review/) → [Security scan](src/codomyrmex/security/)
- **AI-Assisted Development**: [AI code editing](src/codomyrmex/agents/ai_code_editing/) with [pattern matching](src/codomyrmex/pattern_matching/) for code refactoring
- **Build & Deploy**: [Build synthesis](src/codomyrmex/build_synthesis/) → [CI/CD automation](src/codomyrmex/ci_cd_automation/) → [Container management](src/codomyrmex/containerization/)

### Research & Analysis
- **Data Science Workflow**: [Coding](src/codomyrmex/coding/sandbox/) → [Data visualization](src/codomyrmex/data_visualization/) → [Performance monitoring](src/codomyrmex/performance/)
- **System Exploration**: [System discovery](src/codomyrmex/system_discovery/) → [Pattern analysis](src/codomyrmex/pattern_matching/) → [Documentation generation](src/codomyrmex/documentation/)

### Production Operations
- **Infrastructure Management**: [Database operations](src/codomyrmex/database_management/) → [Configuration management](src/codomyrmex/config_management/) → [Physical monitoring](src/codomyrmex/physical_management/)
- **Quality Assurance**: [Security scanning](src/codomyrmex/security/) → [Performance benchmarking](src/codomyrmex/performance/) → [Automated testing](src/codomyrmex/tests/)

See **[executable examples](scripts/examples/)** for working demonstrations of these workflows.

## Project Structure

```
codomyrmex/
├── /src/codomyrmex/          # Core source modules
│   ├── /src/codomyrmex/coding/              # Code interaction and sandboxing
│   ├── /src/codomyrmex/static_analysis/     # Code quality analysis
│   ├── /src/codomyrmex/logging_monitoring/  # Centralized logging
│   └── ...                  # 40+ additional modules
├── /scripts/                 # Maintenance and automation utilities
│   ├── /scripts/documentation/       # Documentation maintenance scripts
│   ├── /scripts/development/         # Development utilities
│   ├── /scripts/examples/            # Example scripts and demonstrations
│   └── ...                  # 30+ module orchestrators
├── /docs/                    # Project documentation
│   ├── /docs/getting-started/     # Installation and quickstart guides
│   ├── /docs/modules/             # Module system documentation
│   ├── /docs/project/             # Architecture and contributing guides
│   └── /docs/reference/           # API reference and troubleshooting
├── /src/codomyrmex/tests/    # Test suites
│   ├── /src/codomyrmex/tests/unit/                # Unit tests
│   └── /src/codomyrmex/tests/integration/         # Integration tests
├── /config/                  # Configuration templates and examples
│   ├── /config/examples/            # Configuration examples
│   └── /config/templates/           # Configuration templates
├── /cursorrules/             # Coding standards and automation rules
│   ├── /cursorrules/modules/             # Module-specific rules
│   ├── /cursorrules/cross-module/        # Cross-module coordination rules
│   └── /cursorrules/file-specific/       # File-specific rules
├── /projects/                # Project workspace and templates
│   └── /projects/test_project/        # Example project structure
├── /src/template/            # Code generation templates
└── /output/                 # Generated output and reports
```

### Repository Organization

```mermaid
graph TD
    subgraph "Core Platform"
        CoreSrc["src/codomyrmex/<br/>30+ Modules"]
        CoreScripts["scripts/<br/>Automation & Orchestration"]
        CoreTests["src/codomyrmex/tests/<br/>Unit & Integration Tests"]
    end

    subgraph "Documentation & Config"
        Docs["docs/<br/>User & Developer Guides"]
        Config["config/<br/>Templates & Examples"]
        Rules["cursorrules/<br/>Coding Standards"]
        Projects["projects/<br/>Project Templates"]
    end

    subgraph "Examples & Output"
        Examples["examples/<br/>Usage Demonstrations"]
        Output["@output/<br/>Generated Reports"]
        ScriptsExamples["scripts/examples/<br/>Executable Demos"]
    end

    CoreSrc --> Docs
    CoreScripts --> Docs
    CoreTests --> Docs
    Config --> CoreSrc
    Rules --> CoreSrc
    Projects --> CoreScripts
    Examples --> CoreSrc
    ScriptsExamples --> CoreScripts
    CoreSrc --> Output
    CoreScripts --> Output
```

## Key Concepts

### Modular Architecture
Each module is self-contained with:
- Own dependencies (`requirements.txt`)
- Tests (`tests/`)
- API documentation (`API_SPECIFICATION.md`)
- Usage examples (`USAGE_EXAMPLES.md`)
- Security considerations (`SECURITY.md`)

See **[module system overview](docs/modules/overview.md)** for detailed module architecture and relationships.

### Model Context Protocol (MCP)
Standardized interface for AI integration:
- Tool specifications for LLM interactions
- Consistent parameter schemas
- Provider-agnostic design
- Full documentation in each module's `MCP_TOOL_SPECIFICATION.md`

See **[MCP documentation](src/codomyrmex/model_context_protocol/)** for technical specifications and implementation details.

### Layered Dependencies
Modules organized to prevent circular dependencies:
- **Foundation Layer**: Base services (logging, environment, terminal)
- **Core Layer**: Functional capabilities (analysis, execution, visualization)
- **Service Layer**: Orchestration and integration
- **Application Layer**: User interfaces (CLI, interactive shell)

## Signposting
- **Self**: [Codomyrmex Root](README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)
- **Children**:
    - [Source Code](src/README.md)
    - [Documentation](docs/README.md)
    - [Scripts](scripts/README.md)

## Documentation

- **[Getting Started Guide](docs/getting-started/quickstart.md)** - Quick introduction and setup
- **[Architecture Overview](docs/project/architecture.md)** - System design and principles
- **[Module System](docs/modules/overview.md)** - Module architecture and relationships
- **[Contributing Guide](docs/project/contributing.md)** - Development guidelines
- **[API Reference](docs/reference/api.md)** - API documentation
- **[Troubleshooting](docs/reference/troubleshooting.md)** - Common issues and solutions

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/codomyrmex --cov-report=html

# Run specific test suite
uv run pytest src/codomyrmex/tests/unit/
uv run pytest src/codomyrmex/tests/integration/
```

### Code Quality

```bash
# Format code
uv run black src/

# Lint code
uv run ruff check src/

# Type checking
uv run mypy src/
```

### Module Development

See **[Creating a Module Tutorial](docs/getting-started/tutorials/creating-a-module.md)** for detailed guidance on developing new modules.

## Contributing

We welcome contributions! Please see our **[Contributing Guide](docs/project/contributing.md)** for:
- Code standards and best practices
- Development workflow
- Pull request process
- Testing requirements
- Documentation guidelines

## Security

Security is a priority. See **[SECURITY.md](SECURITY.md)** for:
- Vulnerability reporting
- Security best practices
- Module-specific security considerations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 The Codomyrmex Contributors (@docxology)

### Data Flow Architecture

```mermaid
graph TD
    subgraph "Data Sources"
        UserInput[👤 User Input<br/>Commands, Code, Config]
        FileSystem[💾 File System<br/>Source Code, Data Files]
        APIs[🔗 External APIs<br/>GitHub, Docker Hub, PyPI]
        Databases[🗄️ Databases<br/>Local/Remote DBs]
    end

    subgraph "Processing Pipeline"
        InputParser[📥 Input Parser<br/>CLI Args, Config Files]
        ModuleOrchestrator[🎯 Module Orchestrator<br/>Workflow Coordination]
        DataTransformers[🔄 Data Transformers<br/>Analysis, Processing]
        OutputGenerators[📤 Output Generators<br/>Reports, Visualizations]
    end

    subgraph "Storage & Persistence"
        LocalStorage[💿 Local Storage<br/>JSON, CSV, Images]
        RemoteStorage[☁️ Remote Storage<br/>Cloud Services, Git]
        CacheLayer[⚡ Cache Layer<br/>In-Memory, Redis]
    end

    subgraph "Consumption"
        TerminalOutput[🖥️ Terminal Display<br/>Rich Text, Tables]
        FileOutputs[📄 File Outputs<br/>Reports, Exports]
        WebInterfaces[🌐 Web Interfaces<br/>Dashboards, APIs]
    end

    UserInput --> InputParser
    FileSystem --> InputParser
    APIs --> DataTransformers
    Databases --> DataTransformers

    InputParser --> ModuleOrchestrator
    ModuleOrchestrator --> DataTransformers
    DataTransformers --> OutputGenerators

    OutputGenerators --> LocalStorage
    OutputGenerators --> RemoteStorage
    OutputGenerators --> CacheLayer

    LocalStorage --> TerminalOutput
    RemoteStorage --> FileOutputs
    CacheLayer --> WebInterfaces

    %% Bidirectional data flow
    CacheLayer -.->|"Read/Write"| DataTransformers
    LocalStorage -.->|"Read/Write"| ModuleOrchestrator
```

### Module Interaction Workflow

```mermaid
graph TD
    subgraph "Entry Points"
        CLI[📟 CLI Command]
        InteractiveShell[🐚 Interactive Shell]
        APIEndpoint[🔌 REST API]
        ConfigFile[⚙️ Config File]
    end

    subgraph "Orchestration Layer"
        SystemDiscovery[🔍 System Discovery<br/>Module Loading]
        ProjectOrchestrator[🎯 Project Orchestrator<br/>Workflow Planning]
        TaskScheduler[📅 Task Scheduler<br/>Parallel Execution]
    end

    subgraph "Core Processing Modules"
        AICode[🤖 AI Code Editing<br/>Generation, Refactoring]
        StaticAnalysis[🔬 Static Analysis<br/>Quality Metrics]
        Code[⚙️ Code Execution<br/>& Review]
        Security[🛡️ Security<br/>Vulnerability Scanning]
    end

    subgraph "Infrastructure Modules"
        GitOps[🔀 Git Operations<br/>Version Control]
        BuildSynth[🏗️ Build Synthesis<br/>Multi-Language Builds]
        ContainerMgmt[🐳 Container Management<br/>Docker, K8s]
        DatabaseMgmt[🗄️ Database Management<br/>Migrations, Queries]
    end

    subgraph "Output & Visualization"
        DataVisualization[📊 Data Visualization<br/>Charts, Plots]
        Documentation[📚 Documentation<br/>API Docs, Guides]
        Reporting[📋 Reporting<br/>Status, Metrics]
    end

    CLI --> SystemDiscovery
    InteractiveShell --> SystemDiscovery
    APIEndpoint --> ProjectOrchestrator
    ConfigFile --> TaskScheduler

    SystemDiscovery --> ProjectOrchestrator
    ProjectOrchestrator --> TaskScheduler

    TaskScheduler --> AICode
    TaskScheduler --> StaticAnalysis
    TaskScheduler --> Code
    TaskScheduler --> Security

    AICode --> GitOps
    StaticAnalysis --> BuildSynth
    Code --> ContainerMgmt
    Security --> DatabaseMgmt

    GitOps --> DataVisualization
    BuildSynth --> Documentation
    ContainerMgmt --> Reporting
    DatabaseMgmt --> DataVisualization

    DataVisualization --> Reporting
    Documentation --> Reporting

    %% Cross-module dependencies
    AICode -.->|"Code Review"| StaticAnalysis
    StaticAnalysis -.->|"Security Scan"| Security
    BuildSynth -.->|"Container Build"| ContainerMgmt
    GitOps -.->|"Version Control"| BuildSynth
```

### Development Workflow Architecture

```mermaid
flowchart TD
    subgraph "Planning Phase"
        Requirements[📋 Requirements<br/>Analysis]
        Design[🎨 Design<br/>Architecture]
        Planning[📅 Planning<br/>Task Breakdown]
    end

    subgraph "Development Phase"
        CodeGeneration[🤖 Code Generation<br/>AI-Assisted]
        Implementation[💻 Implementation<br/>Manual Coding]
        Testing[🧪 Testing<br/>Unit & Integration]
        CodeReview[🔍 Code Review<br/>Automated & Manual]
    end

    subgraph "Quality Assurance"
        StaticAnalysis[🔬 Static Analysis<br/>Linting, Metrics]
        Security[🛡️ Security<br/>Vulnerability Checks]
        PerformanceTesting[⚡ Performance Testing<br/>Benchmarking]
        Documentation[📚 Documentation<br/>API Docs, Guides]
    end

    subgraph "Integration Phase"
        BuildProcess[🏗️ Build Process<br/>Compilation, Packaging]
        Deployment[🚀 Deployment<br/>Container, Cloud]
        Monitoring[📊 Monitoring<br/>Logs, Metrics]
        FeedbackLoop[🔄 Feedback Loop<br/>Issue Tracking]
    end

    Requirements --> Design
    Design --> Planning
    Planning --> CodeGeneration
    Planning --> Implementation

    CodeGeneration --> Testing
    Implementation --> Testing
    Testing --> CodeReview
    CodeReview --> StaticAnalysis

    StaticAnalysis --> Security
    Security --> PerformanceTesting
    PerformanceTesting --> Documentation

    Documentation --> BuildProcess
    BuildProcess --> Deployment
    Deployment --> Monitoring
    Monitoring --> FeedbackLoop

    FeedbackLoop --> Requirements

    %% Tool integration
    CodeGeneration -.->|"AI Code Editing"| Testing
    Testing -.->|"Test Runners"| CodeReview
    StaticAnalysis -.->|"Linting Tools"| Security
    BuildProcess -.->|"CI/CD"| Deployment
    Monitoring -.->|"Logging"| FeedbackLoop
```

## Dependencies Overview

```mermaid
graph TD
    subgraph "Core Dependencies"
        CorePy["Python ≥3.10<br/>Runtime Environment"]
        CoreUV["uv<br/>Package Manager"]
        CorePyTest["pytest<br/>Testing Framework"]
    end

    subgraph "AI/ML Dependencies"
        AIDocker["Docker<br/>Container Runtime"]
        AIModels["Ollama<br/>Local Models"]
        AIAPI["OpenAI/Anthropic<br/>API Keys"]
    end

    subgraph "Development Dependencies"
        DevBlack["Black<br/>Code Formatter"]
        DevRuff["Ruff<br/>Linter"]
        DevMyPy["MyPy<br/>Type Checker"]
        DevPreCommit["Pre-commit<br/>Hooks"]
    end

    subgraph "Optional Dependencies"
        OptKubernetes["Kubernetes<br/>Orchestration"]
        OptDatabases["PostgreSQL/MySQL<br/>Database Servers"]
        OptCloud["AWS/GCP/Azure<br/>Cloud Providers"]
    end

    CorePy --> CoreUV
    CoreUV --> CorePyTest
    CorePy --> DevBlack
    CorePy --> DevRuff
    CorePy --> DevMyPy
    CorePy --> DevPreCommit

    CorePy --> AIDocker
    AIDocker --> AIModels
    CorePy --> AIAPI

    CorePy --> OptKubernetes
    CorePy --> OptDatabases
    CorePy --> OptCloud
```

## Module Maturity Levels

```mermaid
pie title Module Development Status (December 2025)
    "Production Ready" : 12
    "Beta" : 8
    "Alpha" : 6
    "Planning" : 4
```

| **Production Ready** | Fully tested, documented, stable APIs | logging_monitoring, environment_setup, terminal_interface |
| **Beta** | Core functionality complete, API stabilization | agents, static_analysis, code |
| **Alpha** | Basic functionality, APIs may change | spatial, physical_management, system_discovery |
| **Planning** | Requirements gathering, initial design | Future specialized modules |

## Key Metrics

- **Lines of Code**: ~50K+ across 33 modules
- **Test Coverage**: ≥80% target (currently 75%)
- **Module Count**: 33 core modules
- **Language Support**: Python, JavaScript, Go, Rust, Java
- **AI Integration**: 5+ LLM providers supported
- **Documentation**: 200+ pages across all modules

## Links

- **Repository**: [github.com/codomyrmex/codomyrmex](https://github.com/codomyrmex/codomyrmex)
- **Issues**: [github.com/codomyrmex/codomyrmex/issues](https://github.com/codomyrmex/codomyrmex/issues)
- **Documentation**: [codomyrmex.readthedocs.io](https://codomyrmex.readthedocs.io/)
- **PyPI**: [pypi.org/project/codomyrmex/](https://pypi.org/project/codomyrmex/)
- **Docker Hub**: [hub.docker.com/r/codomyrmex/codomyrmex](https://hub.docker.com/r/codomyrmex/codomyrmex)

---

**Built with a focus on modularity, clarity, and professional development practices.**

## Navigation Links

- **Documentation**: [Reference Guides](docs/README.md)
- **All Agents**: [AGENTS.md](AGENTS.md)
- **Functional Spec**: [SPEC.md](SPEC.md)
- **Source Index**: [src/README.md](src/README.md)

## Example Usage

```python
from codomyrmex import core

def main():
    # Standard usage pattern
    app = core.Application()
    app.run()
```
