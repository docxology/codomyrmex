# 📚 Codomyrmex Documentation Hub

The comprehensive documentation center for the Codomyrmex platform, providing guides, API references, and educational materials for developers, contributors, and users.

## 🎯 Important Distinction

This `docs/` folder contains documentation **about** Codomyrmex as a project:
- How to use Codomyrmex
- How to contribute to Codomyrmex
- Architecture and design decisions
- Project governance and policies

**Not to be confused with** `src/codomyrmex/documentation/` which is a **module** that provides documentation generation capabilities for other projects.

## 📁 Documentation Structure

```
docs/
├── README.md                     # This file - central documentation hub
│
├── getting-started/              # 🚀 User onboarding and quick start
│   ├── AGENTS.md                     # Getting started agent coordination
│   ├── installation.md               # Complete setup for all platforms
│   ├── quickstart.md                 # 5-minute hands-on experience
│   └── tutorials/                    # Step-by-step learning paths
│       ├── AGENTS.md                 # Tutorial agent coordination
│       └── creating-a-module.md      # Build your own module tutorial
│
├── development/                  # 🔧 Developer-focused documentation
│   ├── AGENTS.md                     # Development agent coordination
│   ├── environment-setup.md          # Development environment configuration
│   ├── documentation.md              # Standards for writing and maintaining docs
│   ├── testing-strategy.md           # Testing approach and best practices
│   └── uv-usage-guide.md             # Modern Python package management
│
├── modules/                      # 📦 Module system documentation
│   ├── AGENTS.md                     # Module system agent coordination
│   ├── overview.md                   # Module architecture and design principles
│   └── relationships.md              # Inter-module dependencies and integration patterns
│
├── integration/                  # 🔗 External system integration
│   ├── AGENTS.md                     # Integration agent coordination
│   ├── external-systems.md           # Third-party integrations
│   └── fabric-ai-integration.md      # AI workflow integration
│
├── project/                      # 🏗️ Project governance and contribution
│   ├── AGENTS.md                     # Project governance agent coordination
│   ├── architecture.md               # System architecture with Mermaid diagrams
│   ├── contributing.md               # How to contribute effectively
│   ├── documentation-reorganization-summary.md
│   └── todo.md                       # Project roadmap and current priorities
│
├── reference/                    # 📖 Technical references
│   ├── AGENTS.md                     # Reference documentation agent coordination
│   ├── api-complete.md               # **ACCURATE** API with real function signatures
│   ├── api.md                        # API index with source links
│   ├── cli.md                        # Complete command-line documentation
│   ├── changelog.md                  # Project change history (redirects to root)
│   ├── migration-guide.md            # Upgrade instructions
│   ├── orchestrator.md               # Workflow orchestration guide
│   ├── performance.md                # Performance optimization guide
│   └── troubleshooting.md            # Common issues and comprehensive solutions
│
├── project_orchestration/        # 🎯 Project orchestration system
│   ├── README.md                      # Orchestration documentation overview
│   ├── task-orchestration-guide.md    # Complete task orchestration guide
│   ├── project-lifecycle-guide.md     # Project lifecycle management
│   ├── config-driven-operations.md    # Configuration-driven workflows
│   ├── workflow-configuration-schema.md  # Workflow JSON schema
│   ├── project-template-schema.md     # Project template structure
│   ├── resource-configuration.md      # Resource management
│   └── dispatch-coordination.md       # Dispatch and coordination patterns
│
├── examples/                     # 📚 Examples documentation
│   ├── README.md                      # Examples overview
│   ├── basic-examples.md              # Basic single-module examples
│   ├── integration-examples.md        # Multi-module integration examples
│   └── orchestration-examples.md      # Orchestration examples
│
└── deployment/                   # 🚀 Production deployment
    ├── AGENTS.md                     # Deployment agent coordination
    └── production.md                 # Production environment setup guide
```

## 🎯 Navigation by User Type

### **👤 New Users - Getting Started Path**
Start here if you're new to Codomyrmex:
1. **[📦 Installation Guide](getting-started/installation.md)** - Complete setup for all platforms
2. **[⚡ Quick Start](getting-started/quickstart.md)** - 5-minute hands-on experience
3. **[🎓 Module Creation Tutorial](getting-started/tutorials/creating-a-module.md)** - Learn by building
4. **[🎮 Interactive Examples](../../scripts/examples/README.md)** - Hands-on demonstrations

### **👨‍💻 Developers - Development Path**
For contributors and module developers:
1. **[🏗️ Environment Setup](development/environment-setup.md)** - Configure development environment
2. **[📝 Documentation Guidelines](development/documentation.md)** - Writing and maintaining docs
3. **[🧪 Testing Strategy](development/testing-strategy.md)** - Testing approach and best practices
4. **[📦 UV Usage Guide](development/uv-usage-guide.md)** - Modern Python package management
5. **[🤝 Contributing Guide](project/contributing.md)** - How to contribute effectively

### **🏗️ Architects - System Understanding**
For understanding the system design:
1. **[🏛️ Architecture Overview](project/architecture.md)** - System design and principles
2. **[📦 Module System](modules/overview.md)** - Understanding the modular architecture
3. **[🔗 Module Relationships](modules/relationships.md)** - How modules work together
4. **[📦 Module Template](../src/codomyrmex/module_template/README.md)** - Template for creating modules

### **🔌 Integrators - External Systems**
For connecting with other systems:
1. **[🌐 External Systems](integration/external-systems.md)** - Third-party integrations
2. **[🤖 Fabric AI Integration](integration/fabric-ai-integration.md)** - AI workflow integration
3. **[🔌 Complete API Reference](reference/api-complete.md)** - All available APIs
4. **[💻 CLI Reference](reference/cli.md)** - Command-line interface documentation

### **🎯 Orchestration Users - Workflow Management**
For task, project, and workflow orchestration:
1. **[Task Orchestration Guide](project_orchestration/task-orchestration-guide.md)** - Complete task orchestration
2. **[Project Lifecycle Guide](project_orchestration/project-lifecycle-guide.md)** - Project management
3. **[Config-Driven Operations](project_orchestration/config-driven-operations.md)** - Configuration-driven workflows
4. **[Dispatch and Coordination](project_orchestration/dispatch-coordination.md)** - Dispatch patterns
5. **[Examples Documentation](examples/README.md)** - Complete examples guide

### **🚀 DevOps - Production Deployment**
For production deployment:
1. **[🏭 Production Deployment](deployment/production.md)** - Production environment setup
2. **[⚡ Performance Guide](reference/performance.md)** - Performance optimization
3. **[🔧 Troubleshooting](reference/troubleshooting.md)** - Common issues and solutions
4. **[🔄 Migration Guide](reference/migration-guide.md)** - Version upgrade instructions

### **🎓 Learners - Educational Path**
For comprehensive learning:
1. **[🎮 Orchestrator Guide](reference/orchestrator.md)** - System exploration and discovery
2. **[📋 Project TODO](project/todo.md)** - Current development priorities
3. **[📝 Documentation Reorg](project/documentation-reorganization-summary.md)** - How documentation is organized
4. **[🔌 Module APIs](reference/api.md#module-apis)** - Individual module documentation (see API reference)
5. **[🎮 Interactive Examples](../../scripts/examples/README.md)** - Hands-on demonstrations
6. **[🏛️ System Architecture](project/architecture.md)** - Complete system design understanding

## 📊 Documentation Statistics

### **Coverage Metrics**
- **📄 Total Documents**: 17 comprehensive documentation files
- **🔗 Cross-References**: 200+ internal links for seamless navigation
- **🎯 User Entry Points**: 6 different paths for various user types
- **📚 API Documentation**: 100% coverage of implemented functions
- **🧪 Examples**: Real, working code examples in all guides

### **Documentation Quality Indicators**
- **✅ Real Implementations**: All API examples use actual function signatures
- **✅ No Mocks**: Testing philosophy ensures real data and implementations
- **✅ Cross-Linked**: Every section connects to related content
- **✅ Progressive Complexity**: Information organized from simple to advanced
- **✅ User-Centric**: Organized by user intent, not code structure

## 🎯 User Journey Navigation

### **New Users** - Getting Started Path
```
Start Here
    ↓
📖 [Main README](../README.md) → Project overview and value proposition
    ↓
🚀 [Installation Guide](./getting-started/installation.md) → Complete setup
    ↓
⚡ [Quick Start](./getting-started/quickstart.md) → 5-minute hands-on experience
    ↓
💡 [Examples](../scripts/examples/README.md) → Try interactive demonstrations
    ↓
📚 [API Reference](./reference/api.md) → Learn the interfaces
```

### **Developers** - Development Path
```
🔧 [Development Setup](./development/environment-setup.md) → Environment preparation
    ↓
🏗️ [Architecture Overview](./project/architecture.md) → System design understanding
    ↓
📦 [Module System](./modules/overview.md) → Modular architecture deep dive
    ↓
🤝 [Contributing Guide](./project/contributing.md) → How to contribute effectively
    ↓
📝 [Documentation Guidelines](./development/documentation.md) → Writing and maintaining docs
```

### **API Users** - Integration Path
```
🔌 [API Reference](./reference/api-complete.md) → Complete API documentation
    ↓
💻 [CLI Reference](./reference/cli.md) → Command-line interface guide
    ↓
🔗 [Integration Examples](./integration/) → External system integration
    ↓
🎮 [Examples](../scripts/examples/) → Working code examples
```

## 📂 Documentation Categories

### 🚀 **Getting Started**
Essential guides for new users and quick onboarding:
- **[Installation Guide](./getting-started/installation.md)** - Complete setup instructions for all platforms
- **[Quick Start](./getting-started/quickstart.md)** - 5-minute getting started with practical examples
- **[Module Creation Tutorial](./getting-started/tutorials/creating-a-module.md)** - Build your own module step-by-step

### 🔧 **Development**
Technical guides for contributors and module developers:
- **[Development Setup](./development/environment-setup.md)** - Complete development environment configuration
- **[Documentation Guidelines](./development/documentation.md)** - Standards for writing and maintaining documentation
- **[Testing Strategy](./development/testing-strategy.md)** - Testing approach and best practices
- **[UV Usage Guide](./development/uv-usage-guide.md)** - Modern Python package management

### 📦 **Module System**
Understanding the modular architecture:
- **[Module Overview](./modules/overview.md)** - Architecture and design principles
- **[Module Relationships](./modules/relationships.md)** - Dependencies and integration patterns

### 🔗 **Integration**
Connecting with external systems:
- **[External Systems](./integration/external-systems.md)** - Third-party integrations
- **[Fabric AI Integration](./integration/fabric-ai-integration.md)** - AI workflow integration

### 🏗️ **Project Governance**
Project management and contribution:
- **[Architecture Overview](./project/architecture.md)** - System architecture with Mermaid diagrams
- **[Contributing Guide](./project/contributing.md)** - How to contribute effectively
- **[Project TODO](./project/todo.md)** - Roadmap and current priorities

### 📖 **Reference Documentation**
Technical references and API documentation:
- **[Complete API Reference](./reference/api-complete.md)** - **ACCURATE** API with real function signatures
- **[API Index](./reference/api.md)** - Quick API overview with source links
- **[CLI Reference](./reference/cli.md)** - Complete command-line documentation
- **[Migration Guide](./reference/migration-guide.md)** - Upgrade instructions
- **[Troubleshooting Guide](./reference/troubleshooting.md)** - Common issues and comprehensive solutions

### 🚀 **Deployment**
Production deployment guides:
- **[Production Deployment](./deployment/production.md)** - Production environment setup guide

## 🤖 AI Agent Integration

This documentation is maintained by Codomyrmex's AI agents:

### Documentation Agent (`src/codomyrmex/documentation/`)
- **Location**: `src/codomyrmex/documentation/`
- **Purpose**: Automated documentation generation and maintenance
- **Capabilities**:
  - API documentation generation
  - README and tutorial creation
  - Code comment enhancement
  - Documentation quality assessment

### Code Editing Agent (`src/codomyrmex/ai_code_editing/`)
- **Location**: `src/codomyrmex/ai_code_editing/`
- **Purpose**: Intelligent documentation improvement
- **Capabilities**:
  - Documentation structure optimization
  - Cross-reference generation
  - Example code enhancement

## 📋 Documentation Standards

### Philosophy
- **"Show, don't tell"** - Code examples demonstrate capabilities
- **Understated descriptions** - Let functionality speak for itself
- **Comprehensive cross-linking** - Every level has navigation to related content
- **Real implementations** - No mock examples, all code works

### Structure Requirements
Every documentation level must include:
- **README.md** - Overview and navigation for that level
- **AGENTS.md** - AI agent context and capabilities at that level
- **Cross-links** - Navigation to parent, child, and related content
- **Navigation diagrams** - Visual representation of content relationships

## 🔍 Search and Discovery

### Quick Access by Need
| Need | Primary Resource | Alternative |
|------|------------------|-------------|
| **Installation Help** | [Installation Guide](./getting-started/installation.md) | [Quick Start](./getting-started/quickstart.md) |
| **API Reference** | [API Reference](./reference/api-complete.md) | [API Index](./reference/api.md) |
| **Development Setup** | [Dev Setup](./development/environment-setup.md) | [Contributing](./project/contributing.md) |
| **Troubleshooting** | [Troubleshooting](./reference/troubleshooting.md) | [Examples](../scripts/examples/) |
| **Module Development** | [Module Tutorial](./getting-started/tutorials/creating-a-module.md) | [Module Overview](./modules/overview.md) |

### Navigation Patterns
- **Parent → Child**: Each level links to sub-levels
- **Child → Parent**: Sub-levels link back to parent context
- **Sibling Navigation**: Related content at same level
- **Cross-Category**: Links between different documentation areas

## 🔗 Cross-References & Navigation

### **📚 Documentation Hierarchy**
```
📖 [Main README](../README.md) ← Project overview and user journey
    ↓
📚 [This Documentation Hub](./README.md) ← Current level overview
    ├── 🚀 [Getting Started](./getting-started/) ← User onboarding
    ├── 🔧 [Development](./development/) ← Developer guides
    ├── 📦 [Modules](./modules/) ← Module system
    ├── 🔗 [Integration](./integration/) ← External systems
    ├── 🏗️ [Project](./project/) ← Governance
    ├── 📖 [Reference](./reference/) ← Technical docs
    └── 🚀 [Deployment](./deployment/) ← Production
```

### **🌐 External Documentation**
- **[GitHub Repository](https://github.com/codomyrmex/codomyrmex)** - Source code and issue tracking
- **[PyPI Package](https://pypi.org/project/codomyrmex/)** - Package installation and metadata
- **[Documentation Website](https://codomyrmex.dev/)** - Web-based documentation (planned)

### **📂 Source Code Navigation**
- **[Source Overview](../src/README.md)** - Source code structure and navigation
- **[Package Documentation](../src/codomyrmex/README.md)** - Module status and integration patterns
- **[Individual Module APIs](reference/api.md#module-apis)** - Module-specific APIs (see API reference)

## 🤝 Contributing to Documentation

### How to Help
1. **Report Issues** - Use [GitHub Issues](https://github.com/codomyrmex/codomyrmex/issues) for documentation problems
2. **Suggest Improvements** - [GitHub Discussions](https://github.com/codomyrmex/codomyrmex/discussions) for enhancement ideas
3. **Submit PRs** - Follow [Contributing Guide](./project/contributing.md) for documentation updates
4. **Review Changes** - Help maintain quality through [Documentation Guidelines](./development/documentation.md)

### Documentation Maintenance
- **AI Agent Updates** - Automated maintenance by Codomyrmex agents
- **Community Contributions** - Human-reviewed improvements
- **Regular Reviews** - Periodic quality assessments
- **Cross-Level Consistency** - Maintained navigation patterns

---

**📝 Documentation Status**: ✅ **Verified & Current** | *Last reviewed: January 2025* | *Maintained by: Codomyrmex Documentation Team* | *Version: v0.1.0*

