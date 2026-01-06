# Language Models Module - Usage Examples

This document provides comprehensive examples for using the language_models module.

## Basic Text Generation

```python
from codomyrmex.language_models import generate_with_ollama

# Simple generation
response = generate_with_ollama("Explain quantum computing")
print(response)

# Generation with options
response = generate_with_ollama(
    "Write a Python function",
    options={"temperature": 0.3, "num_predict": 200}
)
print(response)
```

## Chat Interface

```python
from codomyrmex.language_models import chat_with_ollama, create_chat_messages

# Create conversation with system prompt
messages = create_chat_messages(
    system_prompt="You are a helpful Python coding assistant.",
    user_message="How do I optimize this Python code: for i in range(1000000): pass"
)

response = chat_with_ollama(messages)
print(response)
```

## Advanced Client Usage

```python
from codomyrmex.language_models import OllamaClient

# Create client with custom settings
client = OllamaClient(
    base_url="http://localhost:11434",
    model="codellama",
    timeout=60,
    max_retries=5
)

# List available models
models = client.list_models()
print(f"Available models: {[m['name'] for m in models]}")

# Check if model exists
if client.check_model_exists("llama3.1"):
    response = client.generate("Hello, how are you?")
    print(response)

# Get model info
model_info = client.get_model_info("llama3.1")
print(f"Model size: {model_info.get('size', 0)} bytes")

client.close()
```

## Manager Class

```python
from codomyrmex.language_models import OllamaManager

# Create manager with default options
manager = OllamaManager(
    model="llama3.1",
    base_url="http://localhost:11434"
)

# Set default options for all generations
manager.set_default_options(
    temperature=0.7,
    top_p=0.9,
    num_predict=500
)

# Generate with defaults
response = manager.generate("Write a short story")
print(response)

# Override options for specific generation
response = manager.generate(
    "Write a haiku",
    options={"temperature": 0.3, "num_predict": 50}
)
print(response)

manager.close()
```

## Streaming Examples

```python
import asyncio
from codomyrmex.language_models import stream_with_ollama, stream_chat_with_ollama

async def streaming_example():
    print("=== Streaming Text Generation ===")

    # Stream simple text
    async for chunk in stream_with_ollama("Tell me a bedtime story"):
        print(chunk, end="", flush=True)
    print("
")

    print("=== Streaming Chat ===")

    # Stream chat response
    messages = [
        {"role": "system", "content": "You are a creative writer."},
        {"role": "user", "content": "Write a mystery story"}
    ]

    async for chunk in stream_chat_with_ollama(messages):
        print(chunk, end="", flush=True)
    print()

# Run the example
asyncio.run(streaming_example())
```

## Error Handling

```python
from codomyrmex.language_models import (
    OllamaClient,
    check_ollama_availability,
    OllamaConnectionError,
    OllamaTimeoutError,
    OllamaModelError
)

# Check availability first
if check_ollama_availability():
    print("Ollama server is available")

    client = OllamaClient(timeout=30)

    try:
        # Try to generate with a model that might not exist
        response = client.generate("Test prompt", model="nonexistent-model")
    except OllamaModelError as e:
        print(f"Model error: {e}")
    except OllamaConnectionError as e:
        print(f"Connection error: {e}")
    except OllamaTimeoutError as e:
        print(f"Timeout error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        client.close()
else:
    print("Ollama server is not available")
```

## Utility Functions

```python
from codomyrmex.language_models import (
    get_available_models,
    create_chat_messages
)

# Get list of available models
models = get_available_models()
print(f"Available models: {models}")

# Create chat messages in various ways
messages1 = create_chat_messages(
    system_prompt="You are a helpful assistant"
)

messages2 = create_chat_messages(
    user_message="How does machine learning work?"
)

messages3 = create_chat_messages(
    system_prompt="You are a coding expert",
    user_message="Explain recursion in Python",
    conversation_history=[
        {"role": "user", "content": "What is programming?"},
        {"role": "assistant", "content": "Programming is writing code..."}
    ]
)

print(f"Messages 1: {messages1}")
print(f"Messages 2: {messages2}")
print(f"Messages 3: {messages3}")
```

## Async Patterns

```python
import asyncio
from codomyrmex.language_models import OllamaManager

async def async_example():
    manager = OllamaManager(timeout=30)

    # Async generation
    response = await manager.generate("Explain async programming")
    print(f"Async response: {response}")

    # Async chat
    messages = [{"role": "user", "content": "What is asyncio?"}]
    response = await manager.chat(messages)
    print(f"Chat response: {response}")

    manager.close()

# Run async example
asyncio.run(async_example())
```

## Batch Processing

```python
from codomyrmex.language_models import generate_with_ollama
import asyncio

async def batch_process():
    prompts = [
        "Explain Python decorators",
        "What is machine learning?",
        "How does blockchain work?",
        "Describe quantum computing"
    ]

    tasks = []
    for prompt in prompts:
        # Create tasks for concurrent processing
        task = asyncio.create_task(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda p=prompt: generate_with_ollama(p, options={"temperature": 0.5})
            )
        )
        tasks.append(task)

    # Wait for all tasks to complete
    responses = await asyncio.gather(*tasks)

    for i, (prompt, response) in enumerate(zip(prompts, responses)):
        print(f"Q{i+1}: {prompt}")
        print(f"A{i+1}: {response[:100]}...")  # First 100 chars
        print()

asyncio.run(batch_process())
```

## Custom Configuration

```python
from codomyrmex.language_models import OllamaClient

# Custom client with specific settings
client = OllamaClient(
    base_url="http://localhost:11434",
    model="llama3.1",
    timeout=120,  # Longer timeout for complex tasks
    max_retries=5,  # More retries for reliability
    backoff_factor=0.5,  # Slower backoff
    verify_ssl=True  # Verify SSL certificates
)

# Use client for various operations
try:
    # Generation with custom options
    response = client.generate(
        "Write a detailed technical explanation",
        options={
            "temperature": 0.1,  # Low creativity
            "top_p": 0.9,
            "num_predict": 1000,
            "repeat_penalty": 1.2
        }
    )

    print(response)

finally:
    client.close()
```

## Integration with Other Modules

```python
from codomyrmex.language_models import generate_with_ollama
from codomyrmex.data_visualization import plot_text_analysis

# Use LLM for content analysis
text = "This is a sample text for analysis..."
analysis_prompt = f"Analyze this text and extract key themes: {text}"

analysis = generate_with_ollama(
    analysis_prompt,
    options={"temperature": 0.3}
)

print(f"Analysis: {analysis}")

# Could integrate with visualization
# plot_text_analysis(analysis)
```

## Performance Monitoring

```python
import time
from codomyrmex.language_models import OllamaManager

def performance_test():
    manager = OllamaManager(timeout=60)

    prompts = [
        "Short response",
        "Medium length response with some detail",
        "Long detailed response with comprehensive information"
    ]

    for i, prompt in enumerate(prompts):
        start_time = time.time()

        response = manager.generate(prompt)

        end_time = time.time()
        duration = end_time - start_time

        print(f"Test {i+1}:")
        print(f"  Prompt: {prompt}")
        print(f"  Duration: {duration".2f"}s")
        print(f"  Response length: {len(response)} chars")
        print(f"  Rate: {len(response)/duration".1f"} chars/sec")
        print()

    manager.close()

performance_test()
```

These examples demonstrate the full range of capabilities available in the language_models module, from simple text generation to complex async operations with comprehensive error handling.
