# 🐜 Codomyrmex Orchestrator System

Welcome to the **epistemic forager nest**! The Codomyrmex Orchestrator provides a comprehensive, interactive system for discovering, exploring, and managing the entire Codomyrmex ecosystem.

## 🚀 Quick Start

### **1. Launch the Orchestrator**
```bash
./start_here.sh
```

### **2. Interactive Shell**
For deep exploration and foraging:
```bash
./start_here.sh
# Choose option 7: Interactive Shell
```

Or launch directly:
```bash
python3 -c "
import sys; sys.path.insert(0, 'src')
from codomyrmex.terminal_interface import InteractiveShell
InteractiveShell().run()
"
```

## 🎯 Features

### **📡 System Discovery**
- **Complete module scanning** - Discovers all modules, functions, classes, and capabilities
- **Dependency mapping** - Shows relationships between modules and external dependencies
- **Capability analysis** - Deep inspection of functions, methods, and classes
- **Import status** - Identifies which modules are working vs. need attention

### **📊 Status Reporting** 
- **Health dashboard** - Comprehensive system status overview
- **Environment checks** - Python, virtual environment, git repository status
- **Dependency validation** - Checks for all required and optional packages
- **Configuration audit** - Validates project structure and config files

### **🎮 Interactive Exploration**
- **Foraging commands** - Search and discover capabilities like an epistemic forager
- **Module deep-dives** - Detailed exploration of specific modules
- **Live demonstrations** - Run working examples from functional modules
- **Capability browsing** - Browse functions, classes, and methods interactively

### **🔧 Development Tools**
- **Automated testing** - Run test suites across all modules
- **Code quality** - Linting, formatting, type checking, security scans
- **Documentation** - Browse and generate documentation
- **Git operations** - Repository status and operations

## 📋 Main Menu Options

| Option | Feature | Description |
|--------|---------|-------------|
| **1** | 🔍 System Discovery | Scan all modules and discover capabilities |
| **2** | 📊 Status Dashboard | Comprehensive system health check |
| **3** | 🏃 Quick Demo | Run example workflows from working modules |
| **4** | 🧪 Test Suite | Run comprehensive tests across all modules |
| **5** | 📚 Documentation | Browse and generate documentation |
| **6** | 🔧 Development Tools | Linting, formatting, and code analysis |
| **7** | 🎮 Interactive Shell | **Enter epistemic forager mode!** |
| **8** | 📋 Export Inventory | Generate complete system inventory report |
| **9** | 🌐 Git Repository Status | Check git repos and dependencies |

## 🐜 Interactive Shell Commands

### **Exploration Commands**
- `explore` - Overview of all modules in the nest
- `explore <module>` - Deep dive into specific module
- `capabilities` - Show all discovered capabilities
- `capabilities <type>` - Show functions, classes, or methods
- `dive <module>` - Detailed capability inspection

### **Foraging Commands** 🔍
- `forage` - Random discovery of interesting capabilities  
- `forage <search>` - Search for capabilities by name or description
- `demo` - Run live demonstrations
- `demo <module>` - Demo specific module

### **System Commands**
- `status` - System health check and session stats
- `export` - Generate comprehensive inventory report
- `session` - Show your foraging session statistics

## 📊 What Gets Discovered

### **Module Information**
- ✅ **Import status** - Whether modules load successfully
- 📝 **Descriptions** - From README.md and docstrings
- 🔢 **Version information** - Module versions where available
- 📅 **Last modified** - When modules were last updated
- 🔗 **Dependencies** - Required packages and relationships

### **Capability Details**
- 🔧 **Functions** - Signatures, parameters, return types, complexity scores
- 📦 **Classes** - Methods, properties, inheritance, abstractions
- 🔄 **Methods** - Class methods with full signature analysis
- 📊 **Constants** - Module-level constants and configuration
- 🎯 **Exports** - Public API surfaces (`__all__` attributes)

### **Relationships**
- 🕸️ **Import dependencies** - Which modules import what
- 🔗 **Function calls** - Cross-module function usage (basic analysis)
- 👥 **Shared names** - Functions/classes with same names across modules
- 📈 **Complexity analysis** - Code complexity metrics and high-complexity identification

## 🎨 Example Output

```bash
🐜 codomyrmex> explore data_visualization

🏠 ============================================================
   EXPLORING: DATA_VISUALIZATION
============================================================
📍 Location: /Users/you/codomyrmex/src/codomyrmex/data_visualization
📝 Description: Comprehensive data visualization capabilities...
🏷️  Version: 0.1.0
📅 Last Modified: 2025-08-28 15:17:36
🔧 Status: ✅ Importable 🧪 Tested 📚 Documented

🛠️  Capabilities (13 total):

   📂 Functions (11):
      • create_line_plot
        💬 Create a line plot with the given data and styling options...
      • create_bar_chart
        💬 Create a bar chart visualization with customization options...
      • create_scatter_plot
        💬 Create a scatter plot with optional styling and annotations...

   📂 Classes (2):
      • PlotStyler
        💬 Advanced plot styling and customization utilities...

💡 Try 'demo data_visualization' to see this module in action!
💡 Try 'dive data_visualization' for detailed capability inspection!
```

## 📈 Reports and Exports

### **System Inventory** (`codomyrmex_inventory.json`)
Complete JSON report including:
- All discovered modules with full metadata
- Function signatures and complexity analysis  
- Class hierarchies and method details
- Dependency relationships
- System status and health metrics

### **Status Reports** (`codomyrmex_status_report_TIMESTAMP.json`)
Detailed system health analysis:
- Python environment validation
- Project structure assessment
- Dependency availability matrix
- Git repository status
- External tool availability

### **Capabilities Report** (`codomyrmex_capabilities_TIMESTAMP.json`)
Deep technical analysis:
- Complete AST-based function analysis
- Parameter and return type annotations
- Complexity scores and recommendations
- Cross-module relationship mapping

## 🛠️ Architecture

```
start_here.sh (Main Orchestrator)
├── system_discovery/
│   ├── discovery_engine.py      # Main discovery logic
│   ├── status_reporter.py       # Health checks and reporting
│   └── capability_scanner.py    # Deep code analysis
└── terminal_interface/
    ├── interactive_shell.py     # Epistemic forager shell
    └── terminal_utils.py        # Beautiful terminal formatting
```

## 🎯 Use Cases

### **🔬 Research & Discovery**
- **New team members** - Quickly understand the codebase structure
- **Code archaeology** - Discover forgotten capabilities and modules
- **Architecture analysis** - Understand module relationships and dependencies

### **🧪 Development & Testing**
- **Pre-commit checks** - Validate system health before commits
- **Integration testing** - Test cross-module functionality
- **Code quality** - Automated linting, formatting, and analysis

### **📊 Project Management**
- **Health monitoring** - Regular system health assessments
- **Documentation** - Generate comprehensive project documentation
- **Capability inventory** - Track available functionality across versions

### **🎓 Learning & Training**
- **Interactive exploration** - Learn by doing with the foraging interface
- **Live demonstrations** - See working examples of each module
- **Code analysis** - Understand function complexity and design patterns

## 🌟 Tips for Epistemic Foraging

1. **Start broad** - Use `explore` without arguments to get the big picture
2. **Follow your nose** - Use `forage` to discover interesting capabilities randomly
3. **Go deep** - Use `dive <module>` when you find something interesting  
4. **Try things** - Use `demo` to see modules in action
5. **Track your journey** - Use `session` to see what you've discovered
6. **Export your findings** - Use `export` to save discoveries for later

---

## Related Documentation

- [Task Orchestration Guide](../project_orchestration/task-orchestration-guide.md) - Complete task orchestration guide
- [Project Lifecycle Guide](../project_orchestration/project-lifecycle-guide.md) - Project management guide
- [Dispatch and Coordination](../project_orchestration/dispatch-coordination.md) - Dispatch patterns and coordination
- [Config-Driven Operations](../project_orchestration/config-driven-operations.md) - Configuration-driven workflows
- [Workflow Configuration Schema](../project_orchestration/workflow-configuration-schema.md) - Workflow JSON schema
- [Project Template Schema](../project_orchestration/project-template-schema.md) - Project template structure
- [Resource Configuration](../project_orchestration/resource-configuration.md) - Resource management
- [Examples Documentation](../examples/README.md) - Complete examples guide

---

**Happy foraging in the Codomyrmex nest! 🐜✨**

*Remember: You're not just browsing code - you're an epistemic forager exploring a vast, structured knowledge ecosystem. Every command helps you understand the territory better!*
