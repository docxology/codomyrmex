# Codomyrmex Examples

Welcome to the Codomyrmex Examples! This directory contains **executable demonstrations** of Codomyrmex capabilities through orchestrator shell scripts that guide you through complete workflows.

## 🎯 What Are These Examples?

Each example is a **self-contained orchestrator script** that:
- ✅ **Sets up** the necessary environment and dependencies
- ✅ **Confirms** system readiness before proceeding  
- ✅ **Executes** a complete workflow demonstrating specific capabilities
- ✅ **Shows results** with clear output and explanations
- ✅ **Guides you** through each step with interactive prompts

## 📁 Example Categories

### **🔰 Basic Examples** (`basic/`)
*Single module demonstrations - perfect for getting started*

| Example | Description | Duration | Prerequisites |
|---------|-------------|----------|---------------|
| **[data-visualization-demo.sh](basic/data-visualization-demo.sh)** ✅ | Create charts, plots, and visualizations | ~3 min | None |
| **[static-analysis-demo.sh](basic/static-analysis-demo.sh)** ✅ | Code quality analysis and linting | ~2 min | Sample Python code |
| **code-execution-demo.sh** 🚧 | Safe code execution in sandbox | ~2 min | Docker |
| **ai-code-editing-demo.sh** 🚧 | AI-powered code generation | ~4 min | API keys |
| **pattern-matching-demo.sh** 🚧 | Code pattern analysis and recognition | ~3 min | None |

### **📋 Core Scripts**
*Main demonstration and usage scripts*

| Script | Description | Usage |
|--------|-------------|-------|
| **[example_usage.py](example_usage.py)** | Complete module demonstration | `python examples/example_usage.py` |
| **[demo_orchestrator.py](demo_orchestrator.py)** | Interactive system discovery demo | `python examples/demo_orchestrator.py` |

### **🔗 Integration Examples** (`integration/`)
*Multiple modules working together - shows the power of integration*

| Example | Description | Duration | Prerequisites |
|---------|-------------|----------|---------------|
| **[ai-enhanced-analysis.sh](integration/ai-enhanced-analysis.sh)** ✅ | AI + Static Analysis + Visualization | ~5 min | API keys |
| **[setup-fabric-demo.sh](setup-fabric-demo.sh)** ✅ | Complete Fabric AI framework integration | ~8 min | Git, Go (API keys optional) |
| **[code-quality-pipeline.sh](integration/code-quality-pipeline.sh)** ✅ | Static analysis + Data visualization pipeline | ~4 min | Sample project |
| **[ai-development-assistant.sh](integration/ai-development-assistant.sh)** ✅ | AI code generation + Sandbox testing + Refinement | ~6 min | API keys |
| **[environment-health-monitor.sh](integration/environment-health-monitor.sh)** ✅ | Environment + Git + System health assessment | ~3 min | None |
| **[development-workflow-orchestrator.sh](integration/development-workflow-orchestrator.sh)** ✅ | Complete AI-enhanced development lifecycle | ~8 min | API keys recommended |

### **🎲 Utility Scripts**
*Helper scripts for running and managing examples*

| Script | Description | Usage |
|--------|-------------|-------|
| **[run-all-basic.sh](run-all-basic.sh)** ✅ | Run all basic examples in sequence | `./run-all-basic.sh` |
| **[select-example.sh](select-example.sh)** ✅ | Interactive example selector | `./select-example.sh` |
| **[check-example-prerequisites.sh](check-example-prerequisites.sh)** ✅ | Verify environment setup for examples | `./check-example-prerequisites.sh` |
| **[git_visualization_comprehensive_demo.py](git_visualization_comprehensive_demo.py)** ✅ | Git operations + visualization demo | `python git_visualization_comprehensive_demo.py` |

### **🔮 Status Legend**
- ✅ **Available** - Ready to run, fully functional
- 🚧 **Planned** - In development, will be added soon  
- 🔄 **Updating** - Exists but being improved

*Note: Focus on the ✅ examples for reliable demonstrations. 🚧 examples are planned improvements.*

## 🎯 Featured Orchestrator Examples

**All orchestrator examples are fully functional thin orchestrators!** ✅

### **🔍 Code Quality Pipeline** - `integration/code-quality-pipeline.sh` ✅
**Comprehensive code quality analysis with visualization**
- Static analysis using multiple tools with graceful fallbacks
- File metrics collection and analysis
- Quality visualization charts and dashboards
- Comprehensive quality reporting with recommendations
- **Modules**: static_analysis + data_visualization + logging_monitoring
- **Status**: ✅ **Working** (no prerequisites)
- **Usage**: `./integration/code-quality-pipeline.sh --non-interactive`

### **🏥 Environment Health Monitor** - `integration/environment-health-monitor.sh` ✅
**Comprehensive development environment assessment**
- Python environment validation and dependency checking
- Git repository health assessment and analysis
- System performance metrics and monitoring
- Health scoring with actionable recommendations
- **Modules**: environment_setup + git_operations + logging_monitoring + system_discovery
- **Status**: ✅ **Working** (no prerequisites)
- **Usage**: `./integration/environment-health-monitor.sh`

### **🤖 AI Development Assistant** - `integration/ai-development-assistant.sh` ⚠️
**Complete AI-powered development workflow**
- Interactive task selection and AI code generation
- Secure code execution in sandbox environment
- Iterative refinement based on execution feedback
- Session tracking and comprehensive reporting
- **Modules**: ai_code_editing + code_execution_sandbox + logging_monitoring
- **Status**: ⚠️ **Requires API Keys + Docker**
- **Usage**: `./integration/ai-development-assistant.sh --non-interactive`

### **🚀 Development Workflow Orchestrator** - `integration/development-workflow-orchestrator.sh` ⚠️
**Complete AI-enhanced development lifecycle demonstration**
- Full project generation with AI assistance
- Multi-phase development process automation
- Code quality analysis and secure testing
- Development metrics dashboards and visualization
- Git integration with documentation and reporting
- **Modules**: ALL modules working together in harmony
- **Status**: ⚠️ **Requires API Keys + Docker + Git**
- **Usage**: `./integration/development-workflow-orchestrator.sh --non-interactive`

## 🚀 Quick Start

### **🎯 Recommended Workflow - Start Here!**
```bash
# 1. Check your environment and prerequisites
cd examples
./check-example-prerequisites.sh

# 2. Test all working examples automatically
./test-all-examples.sh

# 3. Run individual examples interactively
./basic/data-visualization-demo.sh            # 📊 Charts and plots
./basic/static-analysis-demo.sh               # 🔍 Code quality analysis  
./integration/environment-health-monitor.sh   # 🏥 Environment assessment
./integration/code-quality-pipeline.sh        # 🔗 Multi-module workflow
```

### **🤖 For Non-Interactive/Automated Use**
```bash
# Perfect for CI/CD pipelines and automated testing
./basic/data-visualization-demo.sh --non-interactive
./integration/code-quality-pipeline.sh --non-interactive --target=src/
```

### **📋 For AI-Enhanced Workflows** (Optional - Requires API Keys)
```bash
# 1. Set up API keys first
cp .env.example .env  # Add your OpenAI/Anthropic API keys
docker info          # Ensure Docker is running

# 2. Run AI-powered orchestrators
./integration/ai-development-assistant.sh
./integration/development-workflow-orchestrator.sh
```

## 📋 Usage Patterns

### **For New Users**
Start with **Basic Examples** to understand individual module capabilities:
```bash
cd examples/basic
./data-visualization-demo.sh  # See plots and charts
./static-analysis-demo.sh     # Understand code analysis
./code-execution-demo.sh      # Try safe code execution
```

### **For Integration Learning**
Move to **Integration Examples** to see modules working together:
```bash
cd examples
./setup-fabric-demo.sh        # Complete Fabric AI framework integration
cd integration
./code-quality-pipeline.sh    # See analysis + testing + reporting
./ai-enhanced-analysis.sh     # See AI + analysis + visualization
```

### **For Production Insights**
Explore **Complete Workflows** for real-world usage patterns:
```bash
cd examples/workflows
./new-project-setup.sh        # Learn project initialization
./code-review-automation.sh   # See automated code review
```

### **For Deep Learning**
Use **Learning Examples** for comprehensive understanding:
```bash
cd examples/learning
./module-system-tour.sh       # Understand the entire system
./building-your-first-module.sh # Learn module development
```

## ⚙️ Example Script Features

### **Consistent Structure**
Every example script follows this pattern:
```bash
# 1. Header with description and prerequisites
# 2. Environment setup and dependency checks  
# 3. Interactive confirmation prompts
# 4. Step-by-step workflow execution
# 5. Result demonstration with explanations
# 6. Optional cleanup and next steps
```

### **Safety Features**
- ✅ **Environment validation** before execution
- ✅ **Interactive confirmations** at key steps  
- ✅ **Error handling** with clear messages
- ✅ **Cleanup options** to restore original state
- ✅ **Dry-run modes** for safety testing

### **Educational Features**
- 📚 **Explanations** of what each step accomplishes
- 💡 **Tips and best practices** throughout
- 🔗 **Links** to relevant documentation
- 📊 **Progress indicators** and timing information
- 🎯 **Learning objectives** clearly stated

## 🔧 Prerequisites by Category

### **None Required**
- Basic data visualization
- Static analysis
- Pattern matching
- Module system tour

### **API Keys Required**
Create `.env` file with:
```bash
OPENAI_API_KEY="your-openai-key"
ANTHROPIC_API_KEY="your-anthropic-key"  
GOOGLE_API_KEY="your-google-key"
```

### **Docker Required**
- Code execution sandbox examples
- Containerized workflow examples

### **Sample Data/Code Required**
- Some examples generate sample data automatically
- Others work with your existing projects
- All requirements are clearly documented in each script

## 📊 Example Output

Each example produces:
- **Console output** with step-by-step progress
- **Generated files** (plots, reports, code, etc.)
- **Summary reports** of what was accomplished
- **Links to created artifacts** for further exploration

Example directory after running basic examples:
```
examples/output/
├── data-visualization/       # Generated plots and charts
├── static-analysis/         # Analysis reports
├── code-execution/          # Execution results
├── ai-generated/           # AI-generated code samples
└── integration-results/    # Combined workflow outputs
```

## 🎮 Interactive Features

### **Progress Tracking**
- Real-time progress bars
- Step completion indicators  
- Time estimates and actual duration
- Success/failure status for each operation

### **User Control**
- Pause at any step to examine results
- Skip optional steps based on your interests
- Repeat steps for better understanding
- Exit safely at any point

### **Customization Options**
```bash
# Run with custom parameters
./data-visualization-demo.sh --dataset=large --format=svg

# Run in quiet mode (minimal prompts)
./static-analysis-demo.sh --quiet

# Run with debug output
./ai-code-editing-demo.sh --debug
```

## 🔍 Troubleshooting Examples

### **Example Won't Start**
```bash
# Check Codomyrmex installation
codomyrmex check

# Verify you're in the right directory
pwd  # Should be /path/to/codomyrmex/examples

# Check script permissions
ls -la basic/data-visualization-demo.sh
chmod +x basic/data-visualization-demo.sh  # If needed
```

### **Missing Dependencies**
```bash
# Run setup check
./check-example-prerequisites.sh

# Install missing dependencies
pip install -e .  # Reinstall Codomyrmex
```

### **API Key Issues**
```bash
# Verify API keys are set
./check-api-keys.sh

# Create .env file if missing
cp .env.example .env
# Edit with your actual API keys
```

## 📚 Integration with Documentation

These examples complement the main documentation:

- **[Installation Guide](../docs/getting-started/installation.md)** → Run basic examples to verify
- **[Quick Start](../docs/getting-started/quickstart.md)** → Examples provide deeper exploration
- **[Module Overview](../docs/modules/overview.md)** → Examples show modules in action
- **[Tutorials](../docs/getting-started/tutorials/)** → Examples provide hands-on practice

## 🤝 Contributing Examples

Want to add your own example? See our [Example Contribution Guide](CONTRIBUTING.md):

### **Example Template**
```bash
# Use the example template
cp template-example.sh my-new-example.sh

# Follow the established patterns
# 1. Clear header and description
# 2. Environment checks
# 3. Interactive workflow
# 4. Results demonstration
# 5. Educational explanations
```

### **Quality Standards**
- ✅ **Self-contained** - runs with minimal setup
- ✅ **Educational** - explains what's happening
- ✅ **Safe** - includes error handling and cleanup
- ✅ **Tested** - works reliably across environments
- ✅ **Documented** - clear description and prerequisites

## 🎯 Learning Objectives

After working through these examples, you'll understand:

### **Module Capabilities** 
- What each Codomyrmex module can do
- How to configure and use individual modules
- Best practices for module-specific operations

### **Integration Patterns**
- How modules work together effectively
- Common integration patterns and workflows
- Data flow between different modules

### **Real-World Applications**
- Complete development workflows using Codomyrmex
- Production-ready automation patterns
- AI-enhanced development processes

### **Extension and Customization**
- How to build your own modules
- How to create custom workflows
- How to integrate Codomyrmex with other tools

---

**Ready to explore?** Start with a basic example and work your way up to complete workflows. Each example builds on the previous ones, creating a comprehensive learning experience!

**Happy exploring! 🐜✨**
