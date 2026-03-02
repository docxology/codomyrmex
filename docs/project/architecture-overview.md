# Architecture Overview

System architecture, layer diagrams, and data flow for Codomyrmex. For module listings, see [Module Reference](../modules/module-reference.md).

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
        Ollama["Ollama (Local LLM)"]
    end

    subgraph analysisQuality ["Module Layer - Analysis & Quality"]
        StaticAnalysis["Static Analysis"]
        PatternMatch["Pattern Matching"]
        Coding["Coding & Review"]
        Security["Security"]
        Perf["Performance Monitoring"]
    end

    subgraph buildDeploy ["Module Layer - Build & Deploy"]
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
        Cloud["Cloud Integration"]
        Networking["Networking"]
    end

    subgraph extensions ["Module Layer - Extensions"]
        ModTemplate["Module Template"]
        ToolUse["Tool Use"]
        Meme["Meme (Info Dynamics)"]
        SysDiscovery["System Discovery"]
        Cerebrum["Cerebrum (Reasoning)"]
        FPF["FPF (Functional)"]
        IDE["IDE Integration"]
        Networks["Networks"]
        Simulation["Simulation"]
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
    Discovery --> CICDAuto
    Status --> DataViz
    Terminal --> Shell

    %% Module interconnections
    AICode --> Coding
    AICode --> MCP
    AICode --> Ollama
    AICode --> LLM
    StaticAnalysis --> CICDAuto
    StaticAnalysis --> PatternMatch
    StaticAnalysis --> Coding
    StaticAnalysis --> Security
    PatternMatch --> AICode
    PatternMatch --> Coding
    Perf --> Coding
    Perf --> CICDAuto
    CICDAuto --> Git
    CICDAuto --> Docs
    CICDAuto --> Container
    Docs --> StaticAnalysis
    APIDocs --> APIStd
    CICDAuto --> Security
    Container --> PhysMgmt
    Container --> Events
    DataViz --> Spatial
    Database --> CICDAuto
    Database --> Events
    ConfigMgmt --> Environment
    Events --> PluginSys
    PluginSys --> ModTemplate
    SysDiscovery --> ModTemplate
    SysDiscovery --> ToolUse
    Meme --> ToolUse
    Meme --> Events

    %% Foundation connections (all modules depend on foundation)
    AICode -.-> Logging
    StaticAnalysis -.-> Logging
    Coding -.-> Logging
    Security -.-> Logging
    Perf -.-> Logging
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
    ToolUse -.-> Logging
    SysDiscovery -.-> Logging
    Discovery -.-> Logging
    Status -.-> Logging
    Terminal -.-> Logging

    AICode -.-> Environment
    StaticAnalysis -.-> Environment
    Coding -.-> Environment
    Security -.-> Environment
    Perf -.-> Environment
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
    ToolUse -.-> Environment
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
        Documentation["documentation"]
        API["api"]
        CICD["ci_cd_automation"]
        Container["containerization"]
        ConfigMgmt["config_management"]
        Database["database_management"]
        Logistics["logistics"]
        PhysMgmt["physical_management"]
    end

    subgraph specialized ["Specialized Layer"]
        SysDiscovery["system_discovery"]
        ModuleTemplate["module_template"]
        Spatial["spatial"]
        Meme["meme"]
        Events["events"]
        PluginSys["plugin_system"]
        ToolUse["tool_use"]
        Networks["networks"]
        Simulation["simulation"]
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
    Logging --> Documentation
    Logging --> API
    Logging --> CICD
    Logging --> Container
    Logging --> ConfigMgmt
    Logging --> Database
    Logging --> Logistics
    Logging --> PhysMgmt

    Env --> CICD
    Env --> Container
    Env --> ConfigMgmt
    Env --> Database
    Env --> PhysMgmt

    Agents --> CICD
    Agents --> Documentation
    Agents --> Logistics

    StaticAnalysis --> CICD

    Coding --> CICD

    DataViz --> Documentation
    DataViz --> API

    GitOps --> CICD
    GitOps --> Logistics

    Security --> CICD
    Security --> Container

    Performance --> CICD
    Performance --> Container

    Documentation --> Logistics
    CICD --> Logistics
    Container --> Logistics
    ConfigMgmt --> Logistics
    Database --> Logistics

    %% Specialized layer dependencies
    Logging --> SysDiscovery
    Logging --> ModuleTemplate
    Logging --> Spatial
    Logging --> Events
    Logging --> PluginSys
    Logging --> ToolUse
    Logging --> Networks
    Logging --> Simulation

    Env --> SysDiscovery
    Env --> ModuleTemplate
    Env --> Events
    Env --> PluginSys

    SysDiscovery --> ModuleTemplate
    SysDiscovery --> ToolUse
    DataViz --> Spatial
    Events --> PluginSys
    PluginSys --> ModuleTemplate
    Meme --> Events
    Meme --> ToolUse
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
    subgraph sourceCode ["Source Code"]
        AppCode["Application Code"]
        Dependencies["Dependencies"]
        ConfigFiles["Configuration"]
    end

    subgraph buildStages ["Build Stages"]
        Builder["Builder Stage: Install dependencies, Compile code, Run tests, Create artifacts"]
        Runtime["Runtime Stage: Copy artifacts, Configure runtime, Set permissions, Define entrypoint"]
    end

    subgraph output ["Output"]
        OptimizedImage["Optimized Image: Minimal layers, Security hardened, Cached efficiently"]
    end

    AppCode --> Builder
    Dependencies --> Builder
    ConfigFiles --> Builder
    ConfigFiles --> Runtime

    Builder --> Runtime
    Runtime --> OptimizedImage

    Builder -.->|"Remove build tools, Clean cache"| OptimizedImage
    Runtime -.->|"Add runtime deps, Configure app"| OptimizedImage
```

## Architecture: Layered Design Principles

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

See **[detailed architecture documentation](architecture.md)** for design principles and module relationships.

## Data Flow & Interaction Diagrams

### Data Flow Architecture

```mermaid
graph TD
    subgraph dataSources ["Data Sources"]
        UserInput["User Input: Commands, Code, Config"]
        FileSystem["File System: Source Code, Data Files"]
        APIs["External APIs: GitHub, Docker Hub, PyPI"]
        Databases["Databases: Local/Remote DBs"]
    end

    subgraph processingPipeline ["Processing Pipeline"]
        InputParser["Input Parser: CLI Args, Config Files"]
        ModuleOrchestrator["Module Orchestrator: Workflow Coordination"]
        DataTransformers["Data Transformers: Analysis, Processing"]
        OutputGenerators["Output Generators: Reports, Visualizations"]
    end

    subgraph storagePersistence ["Storage & Persistence"]
        LocalStorage["Local Storage: JSON, CSV, Images"]
        RemoteStorage["Remote Storage: Cloud Services, Git"]
        CacheLayer["Cache Layer: In-Memory, Redis"]
    end

    subgraph consumption ["Consumption"]
        TerminalOutput["Terminal Display: Rich Text, Tables"]
        FileOutputs["File Outputs: Reports, Exports"]
        WebInterfaces["Web Interfaces: Dashboards, APIs"]
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
    subgraph entryPoints ["Entry Points"]
        CLI["CLI Command"]
        InteractiveShell["Interactive Shell"]
        APIEndpoint["REST API"]
        ConfigFile["Config File"]
    end

    subgraph orchestrationLayer ["Orchestration Layer"]
        SystemDiscovery["System Discovery: Module Loading"]
        Orchestrator["Orchestrator: Workflow Planning"]
        TaskScheduler["Task Scheduler: Parallel Execution"]
    end

    subgraph coreProcessing ["Core Processing Modules"]
        AICode["AI Code Editing: Generation, Refactoring"]
        StaticAnalysis["Static Analysis: Quality Metrics"]
        Code["Code Execution & Review"]
        Security["Security: Vulnerability Scanning"]
    end

    subgraph infrastructureModules ["Infrastructure Modules"]
        GitOps["Git Operations: Version Control"]
        CICDAuto["CI/CD Automation: Builds & Deployment"]
        ContainerMgmt["Container Management: Docker, K8s"]
        DatabaseMgmt["Database Management: Migrations, Queries"]
    end

    subgraph outputVisualization ["Output & Visualization"]
        DataVisualization["Data Visualization: Charts, Plots"]
        Documentation["Documentation: API Docs, Guides"]
        Reporting["Reporting: Status, Metrics"]
    end

    CLI --> SystemDiscovery
    InteractiveShell --> SystemDiscovery
    APIEndpoint --> Orchestrator
    ConfigFile --> TaskScheduler

    SystemDiscovery --> Orchestrator
    Orchestrator --> TaskScheduler

    TaskScheduler --> AICode
    TaskScheduler --> StaticAnalysis
    TaskScheduler --> Code
    TaskScheduler --> Security

    AICode --> GitOps
    StaticAnalysis --> CICDAuto
    Code --> ContainerMgmt
    Security --> DatabaseMgmt

    GitOps --> DataVisualization
    CICDAuto --> Documentation
    ContainerMgmt --> Reporting
    DatabaseMgmt --> DataVisualization

    DataVisualization --> Reporting
    Documentation --> Reporting

    %% Cross-module dependencies
    AICode -.->|"Code Review"| StaticAnalysis
    StaticAnalysis -.->|"Security Scan"| Security
    CICDAuto -.->|"Container Build"| ContainerMgmt
    GitOps -.->|"Version Control"| CICDAuto
```

### Development Workflow Architecture

```mermaid
flowchart TD
    subgraph planningPhase ["Planning Phase"]
        Requirements["Requirements Analysis"]
        Design["Design Architecture"]
        Planning["Planning Task Breakdown"]
    end

    subgraph developmentPhase ["Development Phase"]
        CodeGeneration["Code Generation AI-Assisted"]
        Implementation["Implementation Manual Coding"]
        Testing["Testing Unit & Integration"]
        CodeReview["Code Review Automated & Manual"]
    end

    subgraph qualityAssurance ["Quality Assurance"]
        StaticAnalysis["Static Analysis Linting, Metrics"]
        Security["Security Vulnerability Checks"]
        PerformanceTesting["Performance Testing Benchmarking"]
        Documentation["Documentation API Docs, Guides"]
    end

    subgraph integrationPhase ["Integration Phase"]
        BuildProcess["Build Process Compilation, Packaging"]
        Deployment["Deployment Container, Cloud"]
        Monitoring["Monitoring Logs, Metrics"]
        FeedbackLoop["Feedback Loop Issue Tracking"]
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

## Key Concepts

### Modular Architecture

Each module is self-contained with:

- Own dependencies (managed in `pyproject.toml`)
- Tests (`tests/`)
- API documentation (`API_SPECIFICATION.md`)
- MCP tool definitions (`MCP_TOOL_SPECIFICATION.md`)
- Agent integration (`AGENTS.md`)
- Technical specification (`SPEC.md`)
- PAI integration (`PAI.md`)

See **[module system overview](../modules/overview.md)** for detailed module architecture and relationships.

### Model Context Protocol (MCP)

Standardized interface for AI integration:

- Tool specifications for LLM interactions
- Consistent parameter schemas
- Provider-agnostic design
- Full documentation in each module's `MCP_TOOL_SPECIFICATION.md`

See **[MCP documentation](../../src/codomyrmex/model_context_protocol/)** for technical specifications and implementation details.

### Layered Dependencies

Modules organized to prevent circular dependencies:

- **Foundation Layer**: Base services (logging, environment, terminal)
- **Core Layer**: Functional capabilities (analysis, execution, visualization)
- **Service Layer**: Orchestration and integration
- **Application Layer**: User interfaces (CLI, interactive shell)

## Navigation Links

- **Setup Guide**: [full-setup.md](../getting-started/full-setup.md)
- **Module Reference**: [module-reference.md](../modules/module-reference.md)
