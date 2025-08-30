# ⚠️ MOVED: Quick Start Guide

**This file has been moved to improve documentation organization.**

**👉 New Location: [docs/getting-started/quickstart.md](docs/getting-started/quickstart.md)**

This file will be removed in a future version. Please update any bookmarks or references.

---

# 🚀 Codomyrmex Quick Start Guide

**Note**: This content has moved to [docs/getting-started/quickstart.md](docs/getting-started/quickstart.md)

Get up and running with Codomyrmex in **3 minutes** or less!

## ⚡ Lightning-Fast Setup

### **Option 1: Automated Setup (Recommended)**
```bash
# Clone and setup everything automatically
git clone https://github.com/codomyrmex/codomyrmex.git
cd codomyrmex
bash src/codomyrmex/environment_setup/scripts/setup_dev_env.sh
```

### **Option 2: Manual Setup**
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

# Generate documentation
cd src/codomyrmex/documentation && npm run build
```

### **Environment Variables**
```bash
# For AI features, add to .env file:
OPENAI_API_KEY="your-openai-key"
ANTHROPIC_API_KEY="your-anthropic-key"
GOOGLE_API_KEY="your-google-key"
```

### **Module Quick Access**
| Module | Import | Main Function |
|--------|--------|---------------|
| **Data Visualization** | `from codomyrmex.data_visualization import create_bar_chart` | `create_bar_chart()` |
| **AI Code Editing** | `from codomyrmex.ai_code_editing import generate_code_snippet` | `generate_code_snippet()` |
| **Code Execution** | `from codomyrmex.code_execution_sandbox import execute_code` | `execute_code()` |
| **Static Analysis** | `from codomyrmex.static_analysis import run_pyrefly_analysis` | `run_pyrefly_analysis()` |
| **Pattern Matching** | `from codomyrmex.pattern_matching import analyze_repository_path` | `analyze_repository_path()` |

## 🎓 Next Steps

### **Learn More**
- **[📖 Full Documentation](src/codomyrmex/documentation/README.md)** - Complete guides and tutorials
- **[🔧 Module Relationships](MODULE_RELATIONSHIPS.md)** - How modules work together
- **[🧪 Testing Strategy](src/codomyrmex/documentation/docs/project/TESTING_STRATEGY.md)** - Quality assurance

### **Common Workflows**

#### **Code Quality Pipeline**
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

#### **Data Analysis Workflow**
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

#### **AI-Enhanced Development**
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

## 🔍 Troubleshooting

### **Common Issues**
- **❌ Module not found**: Run `pip install -e .` from project root
- **❌ Docker issues**: Ensure Docker is running for code execution
- **❌ API key errors**: Add keys to `.env` file (see Environment Variables section)
- **❌ Plot not displaying**: Set `show_plot=True` or check matplotlib backend

### **Get Help**
- **[🔍 Full Troubleshooting Guide](TROUBLESHOOTING.md)** - Solutions for common problems
- **📧 Issues**: [GitHub Issues](https://github.com/codomyrmex/codomyrmex/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/codomyrmex/codomyrmex/discussions)

---

**🎉 You're ready to start building with Codomyrmex!** Check out the [full documentation](src/codomyrmex/documentation/README.md) for advanced features and detailed tutorials.
