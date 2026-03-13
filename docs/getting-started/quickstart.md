# 🚀 Codomyrmex Quick Start Guide

Get up and running with Codomyrmex in **5 minutes or less**! This guide will show you how to install, configure, and start using Codomyrmex features immediately.

## ⚡ Lightning-Fast Setup

### **Option 1: UV-Optimized Setup (Recommended)**

```bash
# Clone and setup everything automatically with uv
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex
./start_here.sh
```

### **Option 2: Manual UV Setup**

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup virtual environment
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex
uv venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
uv sync

# 4. Verify installation
codomyrmex check
```

### **Option 3: Alternative Setup (if uv not available)**

```bash
# 1. Clone and setup virtual environment
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies (uv pip is preferred over pip)
uv pip install -e .

# 3. Verify installation
codomyrmex check
```

> **Note**: Using `uv` is strongly recommended over traditional pip. See [uv installation guide](https://github.com/astral-sh/uv) for setup instructions.

**[📦 Complete Setup Guide](setup.md)** • **[🔧 Troubleshooting](../reference/troubleshooting.md)** • **[📚 Full Documentation](../README.md)**

## 🎯 **Your First Codomyrmex Commands**

After installation, let's verify everything works and explore the system:

```bash
# 1. Check system health
codomyrmex check

# 2. View project information
codomyrmex info

# 3. Explore available modules
codomyrmex modules

# 4. Check system status
codomyrmex status
```

## 🎨 **Hands-On Examples: Create Something Amazing**

Now let's create something! Here are step-by-step examples of Codomyrmex features:

### **1. 🎨 Create Stunning Data Visualizations**

Let's create a beautiful chart that showcases Codomyrmex's visualization capabilities:

```python
from codomyrmex.data_visualization import create_line_plot, create_bar_chart
import numpy as np

print("🎨 Creating beautiful data visualizations...")

# Create sample data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)  # Sine wave
y2 = np.cos(x)  # Cosine wave

# Create a professional line plot
create_line_plot(
    x_data=x,
    y_data=y1,
    title="Beautiful Sine Wave Visualization",
    x_label="Time (seconds)",
    y_label="Amplitude",
    output_path="sine_wave.png",
    show_plot=False,  # Save to file instead of showing
    color="blue",
    linewidth=2
)
print("✅ Sine wave visualization saved!")

# Create a bar chart comparing programming languages
languages = ["Python", "JavaScript", "Java", "C++", "Go"]
popularity = [85, 72, 65, 58, 45]

create_bar_chart(
    categories=languages,
    values=popularity,
    title="Programming Language Popularity (2024)",
    x_label="Programming Language",
    y_label="Popularity Score",
    output_path="language_popularity.png",
    color_palette="viridis"
)
print("✅ Programming language comparison saved!")

print("🎉 Check your output files: sine_wave.png and language_popularity.png")
```

### **2. 🤖 AI-Powered Code Generation**

Experience the future of coding with AI assistance (requires API key):

```python
from codomyrmex.agents import generate_code_snippet

print("🤖 Generating code with AI assistance...")

# Generate a complete function with AI
result = generate_code_snippet(
    prompt="Create a secure REST API endpoint for user registration with input validation",
    language="python",
    provider="openai"  # or "anthropic", "google"
)

if result["status"] == "success":
    print("🤖 AI Generated Code:")
    print("=" * 60)
    print(result["generated_code"])
    print("=" * 60)
    print(f"⏱️ Generated in {result['execution_time']:.2f} seconds")
    print(f"🔢 Tokens used: {result.get('tokens_used', 'N/A')}")
else:
    print(f"❌ Generation failed: {result['error_message']}")

# You can also refactor existing code
from codomyrmex.agents import refactor_code_snippet

code_to_refactor = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total
"""

refactored = refactor_code_snippet(
    code=code_to_refactor,
    refactoring_type="optimize",
    language="python"
)

if refactored["status"] == "success":
    print("🔧 Refactored Code:")
    print(refactored["refactored_code"])
```

### **3. 🏃 Safe Code Execution Sandbox**

Test and run code in a secure, isolated environment:

```python
from codomyrmex.coding import execute_code

print("🏃 Testing code in secure sandbox...")

# Test a simple Python function
python_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Calculate first 10 Fibonacci numbers
for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")
"""

result = execute_code(
    language="python",
    code=python_code,
    timeout=30  # 30 second timeout
)

print("📊 Execution Results:")
print(f"✅ Success: {result['success']}")
print(f"📄 Output: {result['output']}")
print(f"⏱️ Execution time: {result['execution_time']:.3f}s")

# Test JavaScript code too!
js_code = """
function greet(name) {
    return \`Hello, \${name}! Welcome to Codomyrmex!\`;
}

console.log(greet('Developer'));
"""

js_result = execute_code(
    language="javascript",
    code=js_code
)

print(f"JavaScript Output: {js_result['output']}")
```

### **4. 🔍 Comprehensive Code Analysis**

Analyze your codebase for quality, security, and performance issues:

```python
from codomyrmex.coding.static_analysis import run_pyrefly_analysis

print("🔍 Analyzing code quality...")

# Analyze your current project
analysis_result = run_pyrefly_analysis(
    target_paths=["src/codomyrmex/"],  # Analyze the main source code
    project_root="."
)

print("📊 Analysis Summary:")
print(f"📁 Files analyzed: {analysis_result.get('files_analyzed', 0)}")
print(f"🚨 Issues found: {analysis_result.get('issue_count', 0)}")
print(f"⚡ Performance score: {analysis_result.get('performance_score', 'N/A')}")

# You can also analyze specific files
single_file_result = run_pyrefly_analysis(
    target_paths=["README.md"],  # This won't have Python issues
    project_root="."
)
print(f"📄 Single file analysis completed")
```

### **5. 🎮 Interactive Exploration**

Launch the interactive shell to explore all capabilities:

```bash
# Method 1: Use the orchestrator (recommended)
./start_here.sh
# Choose option 7: Interactive Shell

# Method 2: Direct launch
uv run python -c "
from codomyrmex.terminal_interface import InteractiveShell
shell = InteractiveShell()
shell.run()
"
```

**In the interactive shell, try:**

```bash
🐜 codomyrmex> explore                    # Overview of all modules
🐜 codomyrmex> forage visualization       # Find visualization capabilities
🐜 codomyrmex> demo data_visualization    # Run live demo
🐜 codomyrmex> dive agents       # Deep dive into AI module
🐜 codomyrmex> status                     # System health check
🐜 codomyrmex> export                     # Generate system inventory
```

---

## 📋 **Quick Reference**

### **Essential Commands**

```bash
# Check system status
codomyrmex check

# View project information
codomyrmex info

# Run all tests
uv run pytest src/codomyrmex/tests/unit/ -v

# Launch interactive exploration
./start_here.sh
```

### **Environment Variables**

For AI features, create a `.env` file in the project root:

```bash
# Create .env file with your API keys
cat > .env << EOF
OPENAI_API_KEY="your-key-here"
ANTHROPIC_API_KEY="your-key-here"
GOOGLE_API_KEY="your-key-here"
EOF
```

### **Module Quick Access**

| Module                 | Import                                                            | Main Function               |
| ---------------------- | ----------------------------------------------------------------- | --------------------------- |
| **Data Visualization** | `from codomyrmex.data_visualization import create_bar_chart`      | `create_bar_chart()`        |
| **AI Agents**          | `from codomyrmex.agents import generate_code_snippet`    | `generate_code_snippet()`   |
| **Code Execution**     | `from codomyrmex.coding import execute_code`      | `execute_code()`            |
| **Static Analysis**    | `from codomyrmex.coding.static_analysis import run_pyrefly_analysis`     | `run_pyrefly_analysis()`    |
| **Pattern Matching**   | `from codomyrmex.coding.pattern_matching import analyze_repository_path` | `analyze_repository_path()` |
| **Secure Identity**    | `from codomyrmex.identity import IdentityManager`                 | `IdentityManager()`         |

---

**📝 Documentation Status**: ✅ **Verified & Signed** | _Last reviewed: March 2026_ | _Maintained by: Codomyrmex Documentation Team_ | _Version: v1.2.2_

## 🎓 Common Workflows

### **Code Quality Pipeline**

```python
from codomyrmex.coding.static_analysis import run_pyrefly_analysis
from codomyrmex.coding import execute_code
from codomyrmex.agents import refactor_code_snippet

# 1. Analyze code quality
issues = run_pyrefly_analysis(["src/"], "/project")

# 2. Test code execution
result = execute_code("python", "print('test')")

# 3. Refactor if needed
refactored = refactor_code_snippet(
    code_snippet="def func():
    return True",
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
from codomyrmex.agents import generate_code_snippet, refactor_code_snippet
from codomyrmex.coding import execute_code

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

## 🚀 Next Steps

### **Dive Deeper**

1. **🎮 [Interactive Examples](../examples/basic-examples.md)** - Hands-on demonstrations
2. **📖 [Module Overview](../modules/overview.md)** - Understand the module system
3. **🎯 [Tutorials](tutorials/)** - Step-by-step guides for specific tasks
4. **🔗 [Module Relationships](../modules/relationships.md)** - How modules work together
5. **🏗️ [Architecture Guide](../project/architecture.md)** - System design and principles

### **Get Involved**

1. **🤝 [Contributing Guide](../project/contributing.md)** - How to contribute to Codomyrmex
2. **🧪 [Development Setup](../development/environment-setup.md)** - Set up development environment
3. **🔧 [Create a Module](tutorials/creating-a-module.md)** - Build your own Codomyrmex module

---

**🎉 Congratulations!** You've successfully set up Codomyrmex and tried the core features. You're ready to explore the modular toolkit for code analysis, generation, and workflow automation.

**Happy coding! 🐜✨**

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../README.md)
- **Home**: [Repository Root](../../README.md)
