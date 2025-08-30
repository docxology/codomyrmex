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
| **[data-visualization-demo.sh](basic/data-visualization-demo.sh)** | Create charts, plots, and visualizations | ~3 min | None |
| **[static-analysis-demo.sh](basic/static-analysis-demo.sh)** | Code quality analysis and linting | ~2 min | Sample Python code |
| **[code-execution-demo.sh](basic/code-execution-demo.sh)** | Safe code execution in sandbox | ~2 min | Docker (optional) |
| **[ai-code-editing-demo.sh](basic/ai-code-editing-demo.sh)** | AI-powered code generation | ~4 min | API keys |
| **[pattern-matching-demo.sh](basic/pattern-matching-demo.sh)** | Code pattern analysis and recognition | ~3 min | None |

### **🔗 Integration Examples** (`integration/`)
*Multiple modules working together - shows the power of integration*

| Example | Description | Duration | Prerequisites |
|---------|-------------|----------|---------------|
| **[ai-enhanced-analysis.sh](integration/ai-enhanced-analysis.sh)** | AI + Static Analysis + Visualization | ~5 min | API keys |
| **[setup-fabric-demo.sh](setup-fabric-demo.sh)** | Complete Fabric AI framework integration | ~8 min | Git, Go (API keys optional) |
| **[code-quality-pipeline.sh](integration/code-quality-pipeline.sh)** | Analysis → Testing → Reporting | ~4 min | Sample project |
| **[data-analysis-workflow.sh](integration/data-analysis-workflow.sh)** | Data processing + Visualization + AI insights | ~6 min | Sample data |
| **[documentation-generator.sh](integration/documentation-generator.sh)** | Code analysis + Documentation generation | ~5 min | Sample project |

### **🚀 Complete Workflows** (`workflows/`)
*End-to-end processes - production-ready demonstrations*

| Example | Description | Duration | Prerequisites |
|---------|-------------|----------|---------------|
| **[new-project-setup.sh](workflows/new-project-setup.sh)** | Complete new project initialization | ~8 min | None |
| **[code-review-automation.sh](workflows/code-review-automation.sh)** | Automated code review process | ~6 min | Git repository |
| **[performance-analysis.sh](workflows/performance-analysis.sh)** | Code performance analysis and optimization | ~7 min | Sample code |
| **[ai-development-cycle.sh](workflows/ai-development-cycle.sh)** | AI-enhanced development workflow | ~10 min | API keys |

### **🎓 Learning Examples** (`learning/`)
*Educational demonstrations - understand concepts step by step*

| Example | Description | Duration | Prerequisites |
|---------|-------------|----------|---------------|
| **[module-system-tour.sh](learning/module-system-tour.sh)** | Interactive tour of all modules | ~15 min | None |
| **[building-your-first-module.sh](learning/building-your-first-module.sh)** | Create a module from scratch | ~20 min | Development setup |
| **[integration-patterns.sh](learning/integration-patterns.sh)** | Learn module integration patterns | ~12 min | Basic understanding |

## 🚀 Quick Start

### **Run Your First Example**
```bash
# 1. Ensure Codomyrmex is installed
codomyrmex check

# 2. Choose and run an example
cd examples/basic
./data-visualization-demo.sh
```

### **Run All Basic Examples**
```bash
# Run the example orchestrator
cd examples
./run-all-basic.sh
```

### **Interactive Example Selection**
```bash
# Launch the example selector
cd examples  
./select-example.sh
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
