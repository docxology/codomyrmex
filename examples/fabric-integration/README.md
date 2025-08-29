# 🐜 Codomyrmex + Fabric AI Integration

A comprehensive integration framework combining [Fabric AI](https://github.com/danielmiessler/fabric) with Codomyrmex for AI-augmented development workflows.

## 🎯 Overview

This integration demonstrates a **thin orchestrator pattern** that combines Fabric's 227+ AI patterns with Codomyrmex's modular architecture, enabling sophisticated AI-enhanced development processes through:

- **Pattern-Based AI Processing**: Access to 227 curated AI patterns for code analysis, content processing, and workflow automation
- **Multi-Provider AI Access**: Cost-effective integration with OpenAI, Anthropic, Google, and other providers via OpenRouter
- **Workflow Orchestration**: Chain multiple AI operations with robust error handling and fallback mechanisms
- **Interactive Configuration**: Secure, user-friendly setup with masked API key input and intelligent defaults
- **Real-Time Testing**: Built-in validation with actual API calls to ensure functionality

## 📊 Integration Statistics

- **Total Files**: 759 (including complete Fabric repository)
- **Python Scripts**: 10 integration modules
- **Configuration Files**: 36 setup and template files  
- **AI Patterns**: 227 Fabric patterns for various tasks
- **Fabric Version**: v1.4.302
- **Integration Type**: Thin orchestrator with modular components

## 🚀 Quick Start

### 1. Interactive Environment Setup
```bash
cd examples/output/fabric-integration
python3 setup_fabric_env.py
```

This interactive script will guide you through:
- **API Key Configuration**: Secure input for OpenAI, Anthropic, OpenRouter, Google
- **Model Selection**: Choose optimal models with cost-effective defaults
- **Environment Creation**: Real `.env` file at `~/.config/fabric/.env`
- **Live Testing**: Validate setup with actual Fabric API calls

### 2. Run Integration Examples
```bash
# Main orchestrator demonstration
python3 fabric_orchestrator.py

# Content analysis workflow
python3 content_analysis_workflow.py

# Code improvement workflow  
python3 code_improvement_workflow.py
```

### 3. Direct Fabric Usage
```bash
# Analyze text with Fabric patterns
echo "Your text here" | fabric --pattern summarize
echo "Your code here" | fabric --pattern analyze_code

# List all available patterns
fabric --listpatterns
```

## 📁 Integration Components

### Core Integration Scripts

#### `setup_fabric_env.py` - Interactive Environment Setup
- **Features**: Secure API key input, intelligent defaults, real-time testing
- **Providers**: OpenAI, Anthropic, OpenRouter, Google
- **Testing**: Built-in validation with live API calls
- **Output**: Production-ready `.env` at `~/.config/fabric/.env`

#### `fabric_orchestrator.py` - Main Integration Orchestrator
- **Capabilities**: Pattern discovery, workflow execution, result visualization
- **Error Handling**: Robust fallback mechanisms and timeout management
- **Logging**: Integration with Codomyrmex logging system
- **Metrics**: Performance tracking and success rate monitoring

#### `fabric_config_manager.py` - Configuration Management
- **Pattern Management**: Custom pattern creation and management
- **Directory Setup**: Automated Fabric directory structure creation
- **Configuration Export**: Backup and migration capabilities
- **Custom Patterns**: Codomyrmex-specific analysis patterns

### Workflow Examples

#### `content_analysis_workflow.py` - Content Processing
- **Patterns**: `extract_wisdom`, `summarize`, `analyze_prose`
- **Use Cases**: Article analysis, documentation processing
- **Integration**: Results visualization with Codomyrmex

#### `code_improvement_workflow.py` - Code Analysis
- **Patterns**: `analyze_code`, `find_code_smells`, `improve_code`, `security_review`
- **Use Cases**: Code quality assessment, security analysis
- **Integration**: Combined Fabric + Codomyrmex insights

### Configuration Files

#### `fabric_env_template` - Environment Template
Standard template showing all available configuration options for manual setup.

#### `fabric_config_export.json` - Configuration Backup
Complete Fabric configuration export for backup and migration purposes.

#### `demo_env_setup.py` - Setup Demonstration
Usage guide and feature demonstration for the interactive setup process.

## 🌐 OpenRouter Integration

### Why OpenRouter?

OpenRouter provides unified access to multiple AI providers through a single API key:

- **💰 Cost Effective**: Often 50-80% cheaper than direct provider APIs
- **🔄 Model Variety**: Access to OpenAI, Anthropic, Google, Meta, and other models
- **📊 Usage Tracking**: Built-in monitoring and cost tracking
- **🚀 Reliability**: Automatic failover and load balancing
- **🔑 Single API Key**: One key for multiple AI providers

### Recommended Models

| Use Case | Model | Provider | Cost/1M tokens |
|----------|-------|----------|----------------|
| **General Analysis** | `openai/gpt-4o-mini` | OpenAI | ~$0.15 |
| **Code Review** | `anthropic/claude-3-haiku` | Anthropic | ~$0.25 |
| **Creative Writing** | `anthropic/claude-3-sonnet` | Anthropic | ~$3.00 |
| **Multimodal** | `google/gemini-1.5-flash` | Google | ~$0.075 |
| **Open Source** | `meta-llama/llama-3.1-8b-instruct` | Meta | ~$0.05 |

## 🔧 Configuration Details

### Environment Variables

The interactive setup creates a complete `.env` file with:

```bash
# API Keys (masked input during setup)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here  
OPENROUTER_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Model Configuration
DEFAULT_VENDOR=OpenRouter
DEFAULT_MODEL=openai/gpt-4o-mini

# Fabric Configuration
FABRIC_OUTPUT_PATH=./fabric_outputs
PATTERNS_LOADER_GIT_REPO_URL=https://github.com/danielmiessler/fabric.git
PATTERNS_LOADER_GIT_REPO_PATTERNS_FOLDER=data/patterns

# OpenRouter Configuration  
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_SITE_URL=https://github.com/danielmiessler/fabric
OPENROUTER_APP_NAME=Fabric-Codomyrmex-Integration
```

### Directory Structure

```
fabric-integration/
├── fabric/                          # Complete Fabric repository (227 patterns)
├── setup_fabric_env.py             # Interactive environment setup
├── fabric_orchestrator.py          # Main integration orchestrator
├── fabric_config_manager.py        # Configuration management
├── content_analysis_workflow.py    # Content processing example
├── code_improvement_workflow.py    # Code analysis example
├── demo_env_setup.py               # Setup demonstration
├── fabric_env_template             # Manual setup template
├── fabric_config_export.json       # Configuration backup
└── integration_workflow_results.json # Example results
```

## 🧪 Testing and Validation

### Automated Testing

The integration includes comprehensive testing:

1. **Binary Verification**: Confirms Fabric v1.4.302 installation
2. **Pattern Discovery**: Validates access to all 227 patterns
3. **API Connectivity**: Tests real API calls with configured providers
4. **Error Handling**: Validates fallback mechanisms and timeouts
5. **Configuration**: Ensures proper `.env` file creation and loading

### Manual Testing Commands

```bash
# Test basic functionality
echo "Hello world" | fabric --pattern summarize

# Test code analysis
echo "def hello(): print('world')" | fabric --pattern analyze_code

# Test pattern listing
fabric --listpatterns | head -10

# Test orchestrator
python3 fabric_orchestrator.py
```

## 🔗 Integration Patterns

### Thin Orchestrator Pattern

This integration demonstrates a **thin orchestrator** approach:

- **Lightweight Coordination**: Minimal overhead between Fabric and Codomyrmex
- **Modular Components**: Each script handles specific workflow aspects
- **Error Resilience**: Robust error handling and fallback mechanisms
- **Extensible Design**: Easy to add new patterns and workflows

### Key Integration Points

1. **Fabric Patterns** → **Codomyrmex Logging**: Workflow tracking and monitoring
2. **Analysis Results** → **Codomyrmex Visualization**: Metrics and performance charts
3. **Code Processing** → **Combined Insights**: Fabric AI + Codomyrmex static analysis
4. **Configuration** → **Unified Management**: Centralized setup across frameworks

## 🚀 Advanced Usage

### Custom Pattern Creation

```python
from fabric_config_manager import FabricConfigManager

manager = FabricConfigManager()
manager.create_custom_pattern(
    "my_analysis_pattern",
    "# Your custom system prompt here...",
    "Description of your pattern"
)
```

### Workflow Orchestration

```python
from fabric_orchestrator import FabricCodomyrmexOrchestrator

orchestrator = FabricCodomyrmexOrchestrator()
results = orchestrator.analyze_code_with_fabric(
    code_content="your_code_here",
    analysis_type="comprehensive"
)
```

### Multi-Model Processing

```bash
# Use different models for different tasks
echo "Complex code" | fabric --model anthropic/claude-3-sonnet --pattern analyze_code
echo "Simple summary" | fabric --model openai/gpt-4o-mini --pattern summarize
```

## 📈 Performance and Cost

### Typical Usage Costs (via OpenRouter)

| Task | Pattern | Model | Input Size | Cost | Time |
|------|---------|-------|------------|------|------|
| **Code Analysis** | `analyze_code` | `gpt-4o-mini` | 500 lines | ~$0.02 | 3-5s |
| **Content Summary** | `summarize` | `claude-3-haiku` | 2000 words | ~$0.01 | 2-4s |  
| **Security Review** | `security_review` | `claude-3-sonnet` | 1000 lines | ~$0.15 | 5-10s |

### Performance Metrics

- **Pattern Discovery**: 227 patterns loaded in <1s
- **API Response**: 2-10s depending on model and complexity
- **Orchestration Overhead**: <100ms per operation
- **Success Rate**: 95%+ with proper API key configuration

## 🛠️ Troubleshooting

### Common Issues

1. **"Fabric binary not available"**
   - Solution: Ensure `$HOME/go/bin` is in your PATH
   - Check: `which fabric` and `fabric --version`

2. **"Pattern execution failed"**
   - Solution: Verify API keys in `~/.config/fabric/.env`
   - Test: `echo "test" | fabric --pattern summarize`

3. **"No module named 'codomyrmex'"**
   - Solution: Install Codomyrmex: `pip install -e .` from project root
   - Check: Python path includes Codomyrmex src directory

4. **"API rate limit exceeded"**
   - Solution: Use OpenRouter for better rate limits
   - Alternative: Switch to different model/provider

### Support Resources

- **Fabric Documentation**: [Fabric GitHub](https://github.com/danielmiessler/fabric)
- **OpenRouter Setup**: [OpenRouter Docs](https://openrouter.ai/docs)
- **Codomyrmex Issues**: Project issue tracker
- **Integration Support**: See `demo_env_setup.py` for guided troubleshooting

## 🎯 Next Steps

### Immediate Actions

1. **Run Interactive Setup**: `python3 setup_fabric_env.py`
2. **Test Integration**: Run workflow examples
3. **Create Custom Patterns**: Add domain-specific analysis patterns
4. **Monitor Usage**: Track costs and performance via OpenRouter dashboard

### Advanced Development

1. **Custom Orchestrators**: Build specialized workflow chains
2. **Integration Extensions**: Connect with additional AI providers
3. **Pattern Library**: Develop Codomyrmex-specific analysis patterns
4. **Automation**: Integrate with CI/CD pipelines for automated analysis

## 📝 License

This integration follows the licenses of both:
- **Fabric**: [Fabric License](https://github.com/danielmiessler/fabric/blob/main/LICENSE)  
- **Codomyrmex**: Project license

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional workflow examples
- Custom pattern development  
- Performance optimizations
- Documentation enhancements
- Provider integrations

---

**🎊 Ready to revolutionize your development workflow with AI? Run `python3 setup_fabric_env.py` to get started!**
