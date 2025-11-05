# 🚀 Fabric Integration Quick Start

Get up and running with Fabric + Codomyrmex integration in under 5 minutes!

## ⚡ One-Command Setup

```bash
cd scripts/output/fabric-integration
python3 setup_fabric_env.py
```

**That's it!** The interactive script handles everything:
- ✅ API key configuration (with masked input)
- ✅ Model selection with smart defaults  
- ✅ Environment file creation
- ✅ Real-time testing with live API calls

## 🔑 API Key Recommendations

### Option 1: OpenRouter (Recommended)
- **Cost**: 50-80% cheaper than direct APIs
- **Access**: Multiple providers with one key
- **Sign up**: [OpenRouter.ai](https://openrouter.ai)
- **Free tier**: $5 credit to start

### Option 2: Direct Providers
- **OpenAI**: [OpenAI API](https://platform.openai.com)
- **Anthropic**: [Anthropic Console](https://console.anthropic.com)  
- **Google**: [Google AI Studio](https://aistudio.google.com)

## 🧪 Test Your Setup

```bash
# Basic functionality test
echo "Hello from Codomyrmex!" | fabric --pattern summarize

# Code analysis test
echo "def hello(): print('world')" | fabric --pattern analyze_code

# List available patterns
fabric --listpatterns | head -5
```

## 🎯 Try the Examples

```bash
# Interactive orchestrator demo
python3 fabric_orchestrator.py

# Content analysis workflow
python3 content_analysis_workflow.py  

# Code improvement workflow
python3 code_improvement_workflow.py
```

## 💡 Quick Tips

1. **Start with OpenRouter**: Best cost/performance ratio
2. **Use gpt-4o-mini**: Fast and cost-effective for most tasks
3. **Check patterns**: `fabric --listpatterns` shows all 227 options
4. **Monitor usage**: OpenRouter dashboard tracks costs
5. **Custom patterns**: Use `fabric_config_manager.py` to create your own

## 🆘 Need Help?

Run the demo guide for detailed explanations:
```bash
python3 demo_env_setup.py
```

Or check the [full README.md](README.md) for comprehensive documentation.

---

**🎊 Ready in 5 minutes? Your AI-augmented development environment awaits!**
