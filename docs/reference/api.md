# API Reference Index

This document provides a comprehensive index of all APIs available in the Codomyrmex ecosystem, organized by module and functionality.

## 📋 Overview

Codomyrmex provides multiple API layers:

1. **Python Module APIs**: Direct Python imports and function calls
2. **CLI APIs**: Command-line interface for all functionality
3. **MCP Tool APIs**: Model Context Protocol tools for AI integration
4. **REST APIs**: HTTP endpoints for web integration (planned)

## 🏗️ Module API Index

### **Foundation Modules**

#### **[logging_monitoring](../../src/codomyrmex/logging_monitoring/API_SPECIFICATION.md)**
- **`setup_logging()`**: Initialize logging system
- **`get_logger(name)`**: Get logger instance
- **`log_performance(func)`**: Performance logging decorator
- **Status**: ✅ Stable API

#### **[environment_setup](../../src/codomyrmex/environment_setup/API_SPECIFICATION.md)**
- **`ensure_dependencies_installed()`**: Validate dependencies
- **`check_and_setup_env_vars(root_path)`**: Environment validation
- **`setup_development_environment()`**: Development setup automation
- **Status**: ✅ Stable API

#### **[model_context_protocol](../../src/codomyrmex/model_context_protocol/API_SPECIFICATION.md)**
- **`MCPToolCall`**: Tool call schema class
- **`MCPToolResult`**: Tool result schema class
- **`validate_mcp_tool()`**: Tool validation
- **Status**: ✅ Stable Schema

### **Core Functional Modules**

#### **[ai_code_editing](../../src/codomyrmex/ai_code_editing/API_SPECIFICATION.md)**
- **`generate_code_snippet(prompt, language, provider)`**: AI code generation
- **`refactor_code_snippet(code, instruction, language)`**: Code refactoring
- **`explain_code(code, language)`**: Code explanation
- **`AICodeEditor`**: Main class for AI operations
- **MCP Tools**: `generate_code_snippet`, `refactor_code_snippet`
- **Status**: 🔄 Evolving API

#### **[data_visualization](../../src/codomyrmex/data_visualization/API_SPECIFICATION.md)**
- **`create_line_plot(x_data, y_data, **options)`**: Line charts
- **`create_bar_chart(categories, values, **options)`**: Bar charts  
- **`create_scatter_plot(x_data, y_data, **options)`**: Scatter plots
- **`create_histogram(data, **options)`**: Histograms
- **`create_pie_chart(labels, sizes, **options)`**: Pie charts
- **`create_heatmap(data, **options)`**: Heatmaps
- **Status**: ✅ Stable API

#### **[code_execution_sandbox](../../src/codomyrmex/code_execution_sandbox/API_SPECIFICATION.md)**
- **`execute_code(language, code, timeout)`**: Safe code execution
- **`CodeExecutor`**: Main execution class
- **`ExecutionResult`**: Result data class
- **MCP Tools**: `execute_code`
- **Status**: 🔄 Evolving API

#### **[static_analysis](../../src/codomyrmex/static_analysis/API_SPECIFICATION.md)**
- **`run_pyrefly_analysis(paths, project_root)`**: Python analysis
- **`analyze_code_quality(file_path)`**: Quality metrics
- **`run_security_scan(file_path)`**: Security analysis
- **`StaticAnalyzer`**: Main analysis class
- **Status**: 🔄 Evolving API

#### **[pattern_matching](../../src/codomyrmex/pattern_matching/API_SPECIFICATION.md)**
- **`analyze_repository_path(path, config)`**: Repository analysis
- **`find_patterns(code, pattern_type)`**: Pattern detection
- **`PatternMatcher`**: Main pattern matching class
- **Status**: 🔄 Evolving API

### **Service Modules**

#### **[build_synthesis](../../src/codomyrmex/build_synthesis/API_SPECIFICATION.md)**
- **`trigger_build(target, config)`**: Build automation
- **`synthesize_code_component(template, params)`**: Code generation
- **`BuildOrchestrator`**: Main build class
- **MCP Tools**: `trigger_build`, `synthesize_code_component`
- **Status**: 🔄 Evolving API

#### **[git_operations](../../src/codomyrmex/git_operations/API_SPECIFICATION.md)**
- **`repository_manager`**: Repository management functions
- **`metadata_cli`**: CLI for metadata operations
- **`repo_cli`**: Repository CLI operations
- **Status**: 🔄 Evolving API

#### **[documentation](../../src/codomyrmex/documentation/API_SPECIFICATION.md)**
- **`generate_documentation_website()`**: Website generation
- **`build_static_site()`**: Static site building
- **`DocumentationGenerator`**: Main documentation class
- **Status**: 🔄 Evolving API

## 🔌 MCP Tool Reference

Model Context Protocol tools for AI integration:

### **AI Code Editing Tools**
```typescript
interface GenerateCodeSnippet {
  name: "generate_code_snippet"
  parameters: {
    prompt: string
    language: string
    provider?: "openai" | "anthropic" | "google"
    model_name?: string
  }
  returns: {
    status: "success" | "error"
    generated_code?: string
    explanation?: string
    error_message?: string
  }
}

interface RefactorCodeSnippet {
  name: "refactor_code_snippet"
  parameters: {
    code_snippet: string
    refactoring_instruction: string
    language: string
  }
  returns: {
    status: "success" | "error"
    refactored_code?: string
    explanation?: string
    error_message?: string
  }
}
```

### **Code Execution Tools**
```typescript
interface ExecuteCode {
  name: "execute_code"
  parameters: {
    language: string
    code: string
    timeout?: number
    input_data?: string
  }
  returns: {
    status: "success" | "error"
    stdout?: string
    stderr?: string
    exit_code?: number
    execution_time?: number
    error_message?: string
  }
}
```

### **Build Synthesis Tools**
```typescript
interface TriggerBuild {
  name: "trigger_build"
  parameters: {
    target: string
    config?: object
  }
  returns: {
    status: "success" | "error"
    build_result?: object
    artifacts?: string[]
    error_message?: string
  }
}

interface SynthesizeCodeComponent {
  name: "synthesize_code_component"
  parameters: {
    template: string
    parameters: object
  }
  returns: {
    status: "success" | "error"
    generated_files?: string[]
    component_info?: object
    error_message?: string
  }
}
```

## 🌐 CLI API Reference

Complete command-line interface. See [CLI Reference](cli.md) for full details.

### **Core Commands**
- **`codomyrmex check`**: System health verification
- **`codomyrmex info`**: Project information display
- **`codomyrmex setup`**: Environment configuration

### **AI Commands**
- **`codomyrmex generate`**: AI-powered code generation
- **`codomyrmex refactor`**: AI-assisted code refactoring

### **Analysis Commands**
- **`codomyrmex analyze`**: Static code analysis
- **`codomyrmex visualize`**: Data visualization creation

### **Execution Commands**
- **`codomyrmex execute`**: Safe code execution
- **`codomyrmex test`**: Test execution and validation

## 📊 Usage Patterns

### **Basic Module Usage**
```python
# Foundation setup
from codomyrmex.logging_monitoring import setup_logging, get_logger
from codomyrmex.environment_setup import ensure_dependencies_installed

# Initialize environment
setup_logging()
logger = get_logger(__name__)
ensure_dependencies_installed()

# Use core modules
from codomyrmex.data_visualization import create_line_plot
from codomyrmex.ai_code_editing import generate_code_snippet

# Create visualization
plot_result = create_line_plot(x_data, y_data, title="My Plot")

# Generate code with AI
code_result = generate_code_snippet("Create a sorting function", "python")
```

### **MCP Integration Pattern**
```python
from codomyrmex.model_context_protocol import MCPToolCall, MCPToolResult

# Create tool call
tool_call = MCPToolCall(
    tool_name="generate_code_snippet",
    parameters={
        "prompt": "Create a data processing function",
        "language": "python",
        "provider": "openai"
    }
)

# Execute tool (handled by MCP framework)
result = mcp_framework.execute_tool(tool_call)
```

### **CLI Integration Pattern**
```bash
# Scripted workflow
codomyrmex generate "data processor" --language python --output processor.py
codomyrmex analyze processor.py --type security --format json --output analysis.json
codomyrmex execute processor.py --input data.txt --output results.txt
```

## 🔍 API Discovery

### **Programmatic Discovery**
```python
from codomyrmex.system_discovery import SystemDiscovery

discovery = SystemDiscovery()
modules = discovery.discover_modules()

for module_name, module_info in modules.items():
    print(f"Module: {module_name}")
    print(f"API Functions: {len(module_info.functions)}")
    print(f"MCP Tools: {len(module_info.mcp_tools)}")
    print(f"Status: {'✅' if module_info.is_importable else '❌'}")
```

### **CLI Discovery**
```bash
# Discover available APIs
codomyrmex discover --detailed --output api-inventory.json

# List available MCP tools
codomyrmex info --modules --format json | jq '.modules[].mcp_tools'

# Show specific module API
codomyrmex docs generate --module ai_code_editing --format markdown
```

## 📚 Documentation Links

### **Module-Specific API Documentation**
| Module | API Reference | MCP Tools | Status |
|--------|---------------|-----------|--------|
| **ai_code_editing** | [API Docs](../../src/codomyrmex/ai_code_editing/API_SPECIFICATION.md) | [MCP Tools](../../src/codomyrmex/ai_code_editing/MCP_TOOL_SPECIFICATION.md) | 🔄 Evolving |
| **data_visualization** | [API Docs](../../src/codomyrmex/data_visualization/API_SPECIFICATION.md) | None | ✅ Stable |
| **code_execution_sandbox** | [API Docs](../../src/codomyrmex/code_execution_sandbox/API_SPECIFICATION.md) | [MCP Tools](../../src/codomyrmex/code_execution_sandbox/MCP_TOOL_SPECIFICATION.md) | 🔄 Evolving |
| **static_analysis** | [API Docs](../../src/codomyrmex/static_analysis/API_SPECIFICATION.md) | [MCP Tools](../../src/codomyrmex/static_analysis/MCP_TOOL_SPECIFICATION.md) | 🔄 Evolving |
| **build_synthesis** | [API Docs](../../src/codomyrmex/build_synthesis/API_SPECIFICATION.md) | [MCP Tools](../../src/codomyrmex/build_synthesis/MCP_TOOL_SPECIFICATION.md) | 🔄 Evolving |
| **pattern_matching** | [API Docs](../../src/codomyrmex/pattern_matching/API_SPECIFICATION.md) | [MCP Tools](../../src/codomyrmex/pattern_matching/MCP_TOOL_SPECIFICATION.md) | 🔄 Evolving |
| **git_operations** | [API Docs](../../src/codomyrmex/git_operations/API_SPECIFICATION.md) | [MCP Tools](../../src/codomyrmex/git_operations/MCP_TOOL_SPECIFICATION.md) | 🔄 Evolving |
| **documentation** | [API Docs](../../src/codomyrmex/documentation/API_SPECIFICATION.md) | None | 🔄 Evolving |
| **logging_monitoring** | [API Docs](../../src/codomyrmex/logging_monitoring/API_SPECIFICATION.md) | None | ✅ Stable |
| **environment_setup** | [API Docs](../../src/codomyrmex/environment_setup/API_SPECIFICATION.md) | None | ✅ Stable |
| **model_context_protocol** | [API Docs](../../src/codomyrmex/model_context_protocol/API_SPECIFICATION.md) | Schema Only | ✅ Stable |

### **Additional References**
- **[CLI Reference](cli.md)**: Complete command-line interface documentation
- **[Module Overview](../modules/overview.md)**: Module system architecture
- **[Module Relationships](../modules/relationships.md)**: Inter-module dependencies
- **[Architecture Guide](../project/architecture.md)**: System design principles

## 🚀 Getting Started with APIs

### **New Users**
1. Start with [Installation Guide](../getting-started/installation.md)
2. Try [Quick Start Examples](../getting-started/quickstart.md)
3. Explore [Module Overview](../modules/overview.md)

### **API Developers**
1. Read [Architecture Guide](../project/architecture.md)
2. Study [Module Relationships](../modules/relationships.md)
3. Follow [Module Creation Tutorial](../getting-started/tutorials/creating-a-module.md)

### **Integration Developers**
1. Review [MCP Tool Specifications](../../src/codomyrmex/*/MCP_TOOL_SPECIFICATION.md)
2. Examine [CLI Reference](cli.md)
3. Check [Usage Examples](../../src/codomyrmex/*/USAGE_EXAMPLES.md)

---

**Version**: 0.1.0  
**Last Updated**: Auto-generated from API analysis  
**API Stability**: See individual module documentation for stability guarantees
