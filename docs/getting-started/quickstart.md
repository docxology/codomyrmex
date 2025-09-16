# 🚀 Codomyrmex Quick Start Guide

Get up and running with Codomyrmex in **5 minutes or less**!

## ⚡ Lightning-Fast Setup

### **Option 1: UV-Optimized Setup (Recommended)**
```bash
# Clone and setup everything automatically with uv
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex
./install_with_uv.sh
```

### **Option 2: Manual UV Setup**
```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup virtual environment
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex
uv venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
uv pip install -e .

# 4. Verify installation
codomyrmex check
```

### **Option 3: Traditional pip Setup (Alternative)**
```bash
# 1. Clone and setup virtual environment
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -e .

# 3. Verify installation
codomyrmex check
```

## 🎯 Try It Now!

### **1. Generate Your First Plot**
```python
from codomyrmex.data_visualization import create_line_plot
import numpy as np

# Create sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Generate plot
create_line_plot(
    x_data=x,
    y_data=y,
    title="My First Codomyrmex Plot",
    x_label="Time",
    y_label="Amplitude",
    output_path="hello_plot.png",
    show_plot=True
)
print("✅ Plot saved as hello_plot.png!")
```

### **2. AI-Powered Code Generation**
```python
from codomyrmex.ai_code_editing import generate_code_snippet

# Generate code with AI (requires API key)
result = generate_code_snippet(
    prompt="Create a function to calculate factorial",
    language="python"
)

if result["status"] == "success":
    print("🤖 AI Generated Code:")
    print(result["generated_code"])
```

### **3. Test Code in Sandbox**
```python
from codomyrmex.code_execution_sandbox import execute_code

# Execute code safely
result = execute_code(
    language="python",
    code="print('Hello from Codomyrmex!')"
)

print(f"Output: {result['stdout']}")
print(f"Exit Code: {result['exit_code']}")
```

### **4. Analyze Your Code**
```python
from codomyrmex.static_analysis import run_pyrefly_analysis

# Analyze Python files
issues = run_pyrefly_analysis(
    target_paths=["my_project/"],
    project_root="/path/to/project"
)

print(f"Found {issues['issue_count']} issues")
```

## 📋 Quick Reference

### **Essential Commands**
```bash
# Check system status
codomyrmex check

# View project information
codomyrmex info

# Run all tests
pytest testing/unit/ -v

# Launch interactive exploration
./start_here.sh
```

### **Environment Variables**
For AI features, create a `.env` file in the project root:
```bash
# Create .env file with your API keys
cat > .env << EOF
OPENAI_API_KEY="sk-your-openai-key"
ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"  
GOOGLE_API_KEY="AIzaSy-your-google-key"
EOF
```

### **Module Quick Access**
| Module | Import | Main Function |
|--------|--------|---------------|
| **Data Visualization** | `from codomyrmex.data_visualization import create_bar_chart` | `create_bar_chart()` |
| **AI Code Editing** | `from codomyrmex.ai_code_editing import generate_code_snippet` | `generate_code_snippet()` |
| **Code Execution** | `from codomyrmex.code_execution_sandbox import execute_code` | `execute_code()` |
| **Static Analysis** | `from codomyrmex.static_analysis import run_pyrefly_analysis` | `run_pyrefly_analysis()` |
| **Pattern Matching** | `from codomyrmex.pattern_matching import analyze_repository_path` | `analyze_repository_path()` |

## 🎓 Common Workflows

### **Code Quality Pipeline**
```python
from codomyrmex.static_analysis import run_pyrefly_analysis
from codomyrmex.code_execution_sandbox import execute_code
from codomyrmex.ai_code_editing import refactor_code_snippet

# 1. Analyze code quality
issues = run_pyrefly_analysis(["src/"], "/project")

# 2. Test code execution
result = execute_code("python", "print('test')")

# 3. Refactor if needed
refactored = refactor_code_snippet(
    code_snippet="def func():\n    return True",
    refactoring_instruction="Add type hints",
    language="python"
)
```

### **Data Analysis Workflow**
```python
from codomyrmex.data_visualization import create_histogram, create_scatter_plot
import pandas as pd

# Load and analyze data
data = pd.read_csv('data.csv')

# Create visualizations
create_histogram(
    data=data['values'],
    title="Data Distribution",
    output_path="histogram.png"
)

create_scatter_plot(
    x_data=data['x'],
    y_data=data['y'],
    title="Data Correlation",
    output_path="scatter.png"
)
```

### **AI-Enhanced Development**
```python
from codomyrmex.ai_code_editing import generate_code_snippet, refactor_code_snippet
from codomyrmex.code_execution_sandbox import execute_code

# Generate new feature
feature_code = generate_code_snippet(
    "Create a REST API endpoint for user management",
    "python"
)

# Test the generated code
test_result = execute_code("python", feature_code["generated_code"])

# Refactor for production
production_code = refactor_code_snippet(
    code_snippet=feature_code["generated_code"],
    refactoring_instruction="Add error handling and logging",
    language="python"
)
```

## 🎮 Interactive Exploration

### **Launch the Interactive Shell**
```bash
# Method 1: Use the orchestrator (recommended)
./start_here.sh
# Choose option 7: Interactive Shell

# Method 2: Direct launch
python -c "
import sys; sys.path.insert(0, 'src')
from codomyrmex.terminal_interface import InteractiveShell
InteractiveShell().run()
"
```

### **Shell Commands to Try**
```bash
🐜 codomyrmex> explore                    # Overview of all modules
🐜 codomyrmex> forage visualization       # Find visualization capabilities  
🐜 codomyrmex> demo data_visualization    # Run live demo
🐜 codomyrmex> dive ai_code_editing       # Deep dive into AI module
🐜 codomyrmex> status                     # System health check
🐜 codomyrmex> export                     # Generate system inventory
```

## 🔍 Troubleshooting

### **Common Issues**

#### **❌ Module not found**
```bash
# Ensure proper installation
pip install -e .
# Verify you're in project root and venv is active
```

#### **❌ Docker issues** 
```bash
# Ensure Docker is running
docker run hello-world
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
```

#### **❌ API key errors**
```bash
# Add keys to .env file in project root
echo 'OPENAI_API_KEY="your-key"' >> .env
```

#### **❌ Plot not displaying**
```bash
# Set show_plot=True or check matplotlib backend
python -c "import matplotlib; print(matplotlib.get_backend())"
```

### **Get Help**
- 📚 **Full Installation Guide**: [Installation](installation.md)
- 🔍 **Detailed Troubleshooting**: [Troubleshooting](../reference/troubleshooting.md)
- 💬 **Community Support**: [GitHub Discussions](https://github.com/codomyrmex/codomyrmex/discussions)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/codomyrmex/codomyrmex/issues)

## 🚀 Next Steps

### **🎮 Try Interactive Examples**
```bash
# Launch the example selector for guided exploration
cd examples
./select-example.sh

# Or run all basic examples in sequence
./run-all-basic.sh

# Or try specific examples
cd basic && ./data-visualization-demo.sh
cd ../integration && ./ai-enhanced-analysis.sh
```

### **Dive Deeper**
1. **🎮 [Interactive Examples](../../examples/README.md)** - Hands-on demonstrations
2. **📖 [Module Overview](../modules/overview.md)** - Understand the module system
3. **🎯 [Tutorials](tutorials/)** - Step-by-step guides for specific tasks
4. **🔗 [Module Relationships](../modules/relationships.md)** - How modules work together
5. **🏗️ [Architecture Guide](../project/architecture.md)** - System design and principles

### **Get Involved**
1. **🤝 [Contributing Guide](../project/contributing.md)** - How to contribute to Codomyrmex
2. **🧪 [Development Setup](../development/environment-setup.md)** - Set up development environment  
3. **🔧 [Create a Module](tutorials/creating-a-module.md)** - Build your own Codomyrmex module

### **Explore Use Cases**
1. **🤖 AI-Enhanced Development** - Use AI to accelerate coding workflows
2. **📊 Data Analysis Pipelines** - Create visualizations and process data
3. **🔍 Code Quality Automation** - Set up automated quality checking
4. **🏗️ Build Orchestration** - Automate build and deployment processes

---

**🎉 Congratulations!** You've successfully set up Codomyrmex and tried the core features. You're ready to explore the powerful modular toolkit for code analysis, generation, and workflow automation.

**Happy coding! 🐜✨**
