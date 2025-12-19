# Codomyrmex

**Version**: 0.1.0 | **License**: MIT | **Python**: ≥3.10

A modular, extensible coding workspace designed for AI development workflows. Codomyrmex integrates tools for building, documenting, analyzing, executing, and visualizing code across multiple languages.

## Overview

Codomyrmex provides a suite of development tools organized as independent, composable modules. Each module offers specific functionality while maintaining clear interfaces and minimal coupling, enabling flexible composition and easy extensibility.

**Key Design Principles**:
- **Modularity First**: Self-contained modules with clear boundaries
- **AI Integration**: Built-in support for Large Language Models via Model Context Protocol (MCP)
- **Polyglot Support**: Language-agnostic interfaces with pluggable implementations
- **Professional Quality**: Testing, documentation, and security practices

## System Architecture

```mermaid
graph TB
    subgraph "User Interfaces"
        CLI["CLI<br/>(codomyrmex)"]
        Shell["Interactive<br/>Shell"]
        API["API Endpoints<br/>(FastAPI)"]
    end

    subgraph "Core Services Layer"
        Discovery["System<br/>Discovery"]
        Status["Status<br/>Reporting"]
        Terminal["Interactive<br/>Terminal"]
    end

    subgraph "Module Layer - AI & Intelligence"
        AICode["AI Code<br/>Editing"]
        MCP["Model Context<br/>Protocol"]
        Ollama["Ollama<br/>Integration"]
        LangModels["Language<br/>Models"]
    end

    subgraph "Module Layer - Analysis & Quality"
        StaticAnalysis["Static<br/>Analysis"]
        PatternMatch["Pattern<br/>Matching"]
        CodeExec["Code Execution<br/>Sandbox"]
        CodeReview["Code<br/>Review"]
        SecurityAudit["Security<br/>Audit"]
    end

    subgraph "Module Layer - Build & Deploy"
        Build["Build<br/>Synthesis"]
        Git["Git<br/>Operations"]
        Docs["Documentation<br/>Generation"]
        CICDAuto["CI/CD<br/>Automation"]
        Container["Container<br/>Management"]
    end

    subgraph "Module Layer - Visualization & Data"
        DataViz["Data<br/>Visualization"]
        Modeling3D["3D<br/>Modeling"]
    end

    subgraph "Module Layer - Infrastructure"
        Database["Database<br/>Management"]
        ConfigMgmt["Config<br/>Management"]
        PhysMgmt["Physical<br/>Management"]
    end

    subgraph "Foundation Layer"
        Logging["Logging &<br/>Monitoring"]
        Environment["Environment<br/>Setup"]
        TerminalInterface["Terminal<br/>Interface"]
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
    AICode --> CodeExec
    AICode --> MCP
    AICode --> Ollama
    AICode --> LangModels
    StaticAnalysis --> Build
    StaticAnalysis --> PatternMatch
    StaticAnalysis --> CodeReview
    StaticAnalysis --> SecurityAudit
    PatternMatch --> AICode
    PatternMatch --> CodeReview
    Build --> Git
    Build --> Docs
    Build --> CICDAuto
    Build --> Container
    Docs --> StaticAnalysis
    CICDAuto --> Build
    CICDAuto --> SecurityAudit
    Container --> PhysMgmt
    DataViz --> Modeling3D
    Database --> Build
    ConfigMgmt --> Environment

    %% Foundation connections (all modules depend on foundation)
    AICode -.-> Logging
    StaticAnalysis -.-> Logging
    CodeExec -.-> Logging
    CodeReview -.-> Logging
    SecurityAudit -.-> Logging
    Build -.-> Logging
    Git -.-> Logging
    Docs -.-> Logging
    CICDAuto -.-> Logging
    Container -.-> Logging
    DataViz -.-> Logging
    Modeling3D -.-> Logging
    Database -.-> Logging
    ConfigMgmt -.-> Logging
    PhysMgmt -.-> Logging
    Discovery -.-> Logging
    Status -.-> Logging
    Terminal -.-> Logging

    AICode -.-> Environment
    StaticAnalysis -.-> Environment
    CodeExec -.-> Environment
    CodeReview -.-> Environment
    SecurityAudit -.-> Environment
    Build -.-> Environment
    Git -.-> Environment
    Docs -.-> Environment
    CICDAuto -.-> Environment
    Container -.-> Environment
    DataViz -.-> Environment
    Modeling3D -.-> Environment
    Database -.-> Environment
    ConfigMgmt -.-> Environment
    PhysMgmt -.-> Environment
    Discovery -.-> Environment
    Status -.-> Environment
    Terminal -.-> Environment

    AICode -.-> TerminalInterface
    MCP -.-> TerminalInterface
    Ollama -.-> TerminalInterface
    LangModels -.-> TerminalInterface
    Discovery -.-> TerminalInterface
    Status -.-> TerminalInterface
    Terminal -.-> TerminalInterface
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

See **[detailed architecture documentation](docs/project/architecture.md)** for comprehensive design principles and module relationships.

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
        Modeling3D["3D<br/>Modeling"]
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
    Modeling3D -.-> LoggingMonitoring
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
| [**ai_code_editing**](src/codomyrmex/ai_code_editing/) | AI-powered code assistance | Code generation, refactoring, multi-LLM support |
| [**static_analysis**](src/codomyrmex/static_analysis/) | Code quality analysis | Linting, security scanning, complexity metrics |
| [**code_execution_sandbox**](src/codomyrmex/code_execution_sandbox/) | Safe code execution | Multi-language support, resource limits, isolation |
| [**data_visualization**](src/codomyrmex/data_visualization/) | Charts and plots | Static/interactive plots, multiple formats |
| [**pattern_matching**](src/codomyrmex/pattern_matching/) | Code pattern analysis | Pattern recognition, dependency analysis |
| [**git_operations**](src/codomyrmex/git_operations/) | Version control automation | Git workflows, branch management, commit automation |
| [**code_review**](src/codomyrmex/code_review/) | Automated code review | AI-powered review, quality analysis, suggestions |
| [**ollama_integration**](src/codomyrmex/ollama_integration/) | Local LLM integration | Local model management, execution, benchmarking |
| [**security_audit**](src/codomyrmex/security_audit/) | Security scanning | Vulnerability detection, compliance checking |
| [**language_models**](src/codomyrmex/language_models/) | LLM infrastructure | Model management, API integration, benchmarking |
| [**performance**](src/codomyrmex/performance/) | Performance monitoring | Profiling, optimization, benchmarking |

### Service Modules
Higher-level services that orchestrate core modules:

| Module | Purpose | Key Features |
|--------|---------|-------------|
| [**build_synthesis**](src/codomyrmex/build_synthesis/) | Build automation | Multi-language builds, artifact generation, pipelines |
| [**documentation**](src/codomyrmex/documentation/) | Documentation generation | Website generation, API docs, tutorial creation |
| [**api_documentation**](src/codomyrmex/api_documentation/) | API documentation | OpenAPI/Swagger specs, structured documentation |
| [**ci_cd_automation**](src/codomyrmex/ci_cd_automation/) | CI/CD pipeline management | Pipeline orchestration, deployment automation |
| [**containerization**](src/codomyrmex/containerization/) | Container management | Docker lifecycle, Kubernetes orchestration |
| [**database_management**](src/codomyrmex/database_management/) | Database operations | Schema management, migrations, backups |
| [**config_management**](src/codomyrmex/config_management/) | Configuration management | Environment setup, secret management, validation |
| [**project_orchestration**](src/codomyrmex/project_orchestration/) | Workflow orchestration | Workflow management, task coordination |

### Specialized Modules
Advanced capabilities for specific domains:

| Module | Purpose | Key Features |
|--------|---------|-------------|
| [**modeling_3d**](src/codomyrmex/modeling_3d/) | 3D modeling and visualization | Scene creation, rendering, geometric operations |
| [**physical_management**](src/codomyrmex/physical_management/) | Physical system simulation | Hardware monitoring, resource management |
| [**system_discovery**](src/codomyrmex/system_discovery/) | System exploration | Module discovery, capability detection, health monitoring |

## Module Quick Reference

| Category | Modules |
|----------|---------|
| **Foundation** | [logging_monitoring](src/codomyrmex/logging_monitoring/) • [environment_setup](src/codomyrmex/environment_setup/) • [model_context_protocol](src/codomyrmex/model_context_protocol/) • [terminal_interface](src/codomyrmex/terminal_interface/) |
| **AI & Intelligence** | [ai_code_editing](src/codomyrmex/ai_code_editing/) • [ollama_integration](src/codomyrmex/ollama_integration/) • [language_models](src/codomyrmex/language_models/) |
| **Analysis & Quality** | [static_analysis](src/codomyrmex/static_analysis/) • [code_review](src/codomyrmex/code_review/) • [pattern_matching](src/codomyrmex/pattern_matching/) • [security_audit](src/codomyrmex/security_audit/) |
| **Build & Deploy** | [build_synthesis](src/codomyrmex/build_synthesis/) • [git_operations](src/codomyrmex/git_operations/) • [ci_cd_automation](src/codomyrmex/ci_cd_automation/) • [containerization](src/codomyrmex/containerization/) |
| **Visualization** | [data_visualization](src/codomyrmex/data_visualization/) • [modeling_3d](src/codomyrmex/modeling_3d/) |
| **Infrastructure** | [database_management](src/codomyrmex/database_management/) • [config_management](src/codomyrmex/config_management/) • [physical_management](src/codomyrmex/physical_management/) |
| **Orchestration** | [documentation](src/codomyrmex/documentation/) • [api_documentation](src/codomyrmex/api_documentation/) • [project_orchestration](src/codomyrmex/project_orchestration/) • [system_discovery](src/codomyrmex/system_discovery/) |
| **Execution** | [code_execution_sandbox](src/codomyrmex/code_execution_sandbox/) • [performance](src/codomyrmex/performance/) |

## Common Use Cases

### Development Workflows
- **Code Analysis Pipeline**: [Static analysis](src/codomyrmex/static_analysis/) → [Code review](src/codomyrmex/code_review/) → [Security audit](src/codomyrmex/security_audit/)
- **AI-Assisted Development**: [AI code editing](src/codomyrmex/ai_code_editing/) with [pattern matching](src/codomyrmex/pattern_matching/) for intelligent refactoring
- **Build & Deploy**: [Build synthesis](src/codomyrmex/build_synthesis/) → [CI/CD automation](src/codomyrmex/ci_cd_automation/) → [Container management](src/codomyrmex/containerization/)

### Research & Analysis
- **Data Science Workflow**: [Code execution](src/codomyrmex/code_execution_sandbox/) → [Data visualization](src/codomyrmex/data_visualization/) → [Performance monitoring](src/codomyrmex/performance/)
- **System Exploration**: [System discovery](src/codomyrmex/system_discovery/) → [Pattern analysis](src/codomyrmex/pattern_matching/) → [Documentation generation](src/codomyrmex/documentation/)

### Production Operations
- **Infrastructure Management**: [Database operations](src/codomyrmex/database_management/) → [Configuration management](src/codomyrmex/config_management/) → [Physical monitoring](src/codomyrmex/physical_management/)
- **Quality Assurance**: [Security scanning](src/codomyrmex/security_audit/) → [Performance benchmarking](src/codomyrmex/performance/) → [Automated testing](testing/)

See **[executable examples](scripts/examples/)** for complete working demonstrations of these workflows.

## Project Structure

```
codomyrmex/
├── src/codomyrmex/          # Core source modules
│   ├── ai_code_editing/     # AI-powered code assistance
│   ├── static_analysis/     # Code quality analysis
│   ├── logging_monitoring/  # Centralized logging
│   └── ...                  # 30+ additional modules
├── scripts/                 # Maintenance and automation utilities
│   ├── documentation/       # Documentation maintenance scripts
│   ├── development/         # Development utilities
│   ├── examples/            # Example scripts and demonstrations
│   └── ...                  # 30+ module orchestrators
├── docs/                    # Project documentation
│   ├── getting-started/     # Installation and quickstart guides
│   ├── modules/             # Module system documentation
│   ├── project/             # Architecture and contributing guides
│   └── reference/           # API reference and troubleshooting
├── testing/                 # Test suites
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── config/                  # Configuration templates and examples
│   ├── examples/            # Configuration examples
│   └── templates/           # Configuration templates
├── cursorrules/             # Coding standards and automation rules
│   ├── modules/             # Module-specific rules
│   ├── cross-module/        # Cross-module coordination rules
│   └── file-specific/       # File-specific rules
├── projects/                # Project workspace and templates
│   └── test_project/        # Example project structure
├── examples/                # Example scripts and demonstrations
├── src/template/            # Code generation templates
└── @output/                 # Generated output and reports
```

### Repository Organization

```mermaid
graph TD
    subgraph "Core Platform"
        CoreSrc["src/codomyrmex/<br/>30+ Modules"]
        CoreScripts["scripts/<br/>Automation & Orchestration"]
        CoreTests["testing/<br/>Unit & Integration Tests"]
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
uv run pytest testing/unit/
uv run pytest testing/integration/
```

### Code Quality

```bash
# Format code
uv run black src/ testing/

# Lint code
uv run ruff check src/ testing/

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

## Links

- **Repository**: [github.com/codomyrmex/codomyrmex](https://github.com/codomyrmex/codomyrmex)
- **Issues**: [github.com/codomyrmex/codomyrmex/issues](https://github.com/codomyrmex/codomyrmex/issues)
- **Documentation**: [codomyrmex.readthedocs.io](https://codomyrmex.readthedocs.io/)

---

**Built with a focus on modularity, clarity, and professional development practices.**
