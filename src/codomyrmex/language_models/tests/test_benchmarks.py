"""
Benchmarking and performance tests for Ollama LLM integration.

Implements best practices for LLM testing including:
- Performance benchmarking (latency, token generation speed)
- Automated evaluation pipelines
- Synthetic and real-world test data
- Continuous monitoring capabilities
"""

import time
import json
import pytest
import asyncio
from typing import Dict, List, Any
from pathlib import Path

from codomyrmex.language_models import (
    OllamaClient,
    OllamaManager,
    generate_with_ollama,
    get_config
)

# Configuration
config = get_config()
TEST_MODEL = "llama3.1:latest"


def save_benchmark_output(filename: str, data: dict):
    """Save benchmark results to performance directory."""
    config.performance_dir.mkdir(parents=True, exist_ok=True)
    filepath = config.performance_dir / f"{filename}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class TestPerformanceBenchmarks:
    """Performance benchmarking tests following LLM testing best practices."""

    @pytest.fixture
    def client(self):
        """Create Ollama client for benchmarking."""
        return OllamaClient(model=TEST_MODEL)

    @pytest.mark.integration
    def test_latency_benchmark(self, client):
        """Benchmark response latency for various prompt sizes."""
        prompts = [
            ("short", "Hello"),
            ("medium", "Write a short paragraph about artificial intelligence."),
            ("long", "Write a detailed essay about the history and future of artificial intelligence, covering key milestones, current applications, and potential societal impacts.")
        ]
        
        results = {}
        
        for prompt_type, prompt in prompts:
            latencies = []
            
            # Run multiple iterations for statistical significance
            for _ in range(3):
                start_time = time.perf_counter()
                response = client.generate(prompt, model=TEST_MODEL)
                end_time = time.perf_counter()
                
                latency = end_time - start_time
                latencies.append(latency)
            
            results[prompt_type] = {
                "prompt_length": len(prompt),
                "response_length": len(response),
                "latencies": latencies,
                "avg_latency": sum(latencies) / len(latencies),
                "min_latency": min(latencies),
                "max_latency": max(latencies)
            }
        
        # Save benchmark results
        benchmark_data = {
            "test_name": "latency_benchmark",
            "timestamp": time.time(),
            "model": TEST_MODEL,
            "results": results,
            "summary": {
                "total_tests": len(prompts) * 3,
                "avg_latency_overall": sum(r["avg_latency"] for r in results.values()) / len(results)
            }
        }
        
        save_benchmark_output("latency_benchmark", benchmark_data)
        
        # Assertions for performance thresholds
        for prompt_type, result in results.items():
            assert result["avg_latency"] < 30.0, f"Latency too high for {prompt_type} prompt: {result['avg_latency']}s"

    @pytest.mark.integration
    def test_token_generation_speed(self, client):
        """Benchmark token generation speed."""
        prompt = "Count from 1 to 20, explaining each number briefly."
        
        start_time = time.perf_counter()
        response = client.generate(prompt, model=TEST_MODEL, options={"num_predict": 200})
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        response_length = len(response)
        # Rough token estimation (4 chars per token average)
        estimated_tokens = response_length / 4
        tokens_per_second = estimated_tokens / total_time
        
        benchmark_data = {
            "test_name": "token_generation_speed",
            "timestamp": time.time(),
            "model": TEST_MODEL,
            "prompt": prompt,
            "response_length": response_length,
            "estimated_tokens": estimated_tokens,
            "total_time": total_time,
            "tokens_per_second": tokens_per_second,
            "chars_per_second": response_length / total_time
        }
        
        save_benchmark_output("token_generation_speed", benchmark_data)
        
        # Assert minimum performance threshold
        assert tokens_per_second > 1.0, f"Token generation too slow: {tokens_per_second} tokens/sec"

    @pytest.mark.integration
    def test_streaming_performance(self, client):
        """Benchmark streaming response performance."""
        prompt = "Write a story about a robot learning to paint."
        
        chunks = []
        chunk_times = []
        start_time = time.perf_counter()
        
        for chunk in client.generate(prompt, model=TEST_MODEL, stream=True):
            chunk_time = time.perf_counter()
            chunks.append(chunk)
            chunk_times.append(chunk_time - start_time)
        
        total_time = time.perf_counter() - start_time
        full_response = "".join(chunks)
        
        benchmark_data = {
            "test_name": "streaming_performance",
            "timestamp": time.time(),
            "model": TEST_MODEL,
            "prompt": prompt,
            "total_chunks": len(chunks),
            "total_time": total_time,
            "response_length": len(full_response),
            "avg_chunk_size": len(full_response) / len(chunks) if chunks else 0,
            "time_to_first_chunk": chunk_times[0] if chunk_times else 0,
            "chunk_intervals": [chunk_times[i] - chunk_times[i-1] for i in range(1, len(chunk_times))]
        }
        
        save_benchmark_output("streaming_performance", benchmark_data)
        
        # Assert streaming performance
        assert len(chunks) > 1, "Should receive multiple chunks"
        assert benchmark_data["time_to_first_chunk"] < 10.0, "Time to first chunk too high"


class TestAutomatedEvaluation:
    """Automated evaluation pipeline tests."""

    @pytest.mark.integration
    def test_response_quality_evaluation(self):
        """Evaluate response quality across different prompt types."""
        test_cases = [
            {
                "category": "factual",
                "prompt": "What is the capital of France?",
                "expected_keywords": ["paris", "france", "capital"]
            },
            {
                "category": "creative",
                "prompt": "Write a haiku about coding.",
                "expected_patterns": ["line_count_3", "syllable_structure"]
            },
            {
                "category": "analytical",
                "prompt": "Compare the advantages and disadvantages of Python vs JavaScript.",
                "expected_keywords": ["python", "javascript", "advantage", "disadvantage"]
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            response = generate_with_ollama(test_case["prompt"], model=TEST_MODEL)
            
            # Basic quality metrics
            quality_score = 0
            response_lower = response.lower()
            
            # Check for expected keywords
            if "expected_keywords" in test_case:
                keyword_matches = sum(1 for keyword in test_case["expected_keywords"] 
                                    if keyword in response_lower)
                quality_score += (keyword_matches / len(test_case["expected_keywords"])) * 100
            
            # Check response length (should be substantial)
            if len(response) > 50:
                quality_score += 20
            
            # Check for coherence (no repeated phrases)
            words = response.split()
            unique_words = set(words)
            coherence_score = len(unique_words) / len(words) if words else 0
            quality_score += coherence_score * 30
            
            results[test_case["category"]] = {
                "prompt": test_case["prompt"],
                "response": response,
                "response_length": len(response),
                "quality_score": min(quality_score, 100),  # Cap at 100
                "coherence_score": coherence_score
            }
        
        evaluation_data = {
            "test_name": "response_quality_evaluation",
            "timestamp": time.time(),
            "model": TEST_MODEL,
            "results": results,
            "overall_quality": sum(r["quality_score"] for r in results.values()) / len(results)
        }
        
        save_benchmark_output("response_quality_evaluation", evaluation_data)
        
        # Assert minimum quality thresholds
        for category, result in results.items():
            assert result["quality_score"] > 30, f"Quality too low for {category}: {result['quality_score']}"

    @pytest.mark.integration
    def test_consistency_evaluation(self):
        """Test response consistency for the same prompt."""
        prompt = "Explain the concept of machine learning in simple terms."
        responses = []
        
        # Generate multiple responses
        for i in range(3):
            response = generate_with_ollama(prompt, model=TEST_MODEL, options={"temperature": 0.1})
            responses.append(response)
        
        # Analyze consistency
        avg_length = sum(len(r) for r in responses) / len(responses)
        length_variance = sum((len(r) - avg_length) ** 2 for r in responses) / len(responses)
        
        # Check for common keywords across responses
        all_words = set()
        common_words = set(responses[0].lower().split())
        
        for response in responses:
            words = set(response.lower().split())
            all_words.update(words)
            common_words.intersection_update(words)
        
        consistency_score = len(common_words) / len(all_words) if all_words else 0
        
        consistency_data = {
            "test_name": "consistency_evaluation",
            "timestamp": time.time(),
            "model": TEST_MODEL,
            "prompt": prompt,
            "responses": responses,
            "avg_length": avg_length,
            "length_variance": length_variance,
            "consistency_score": consistency_score,
            "common_words_count": len(common_words),
            "total_unique_words": len(all_words)
        }
        
        save_benchmark_output("consistency_evaluation", consistency_data)
        
        # Assert consistency thresholds
        assert consistency_score > 0.1, f"Responses too inconsistent: {consistency_score}"
        assert length_variance < (avg_length * 0.5) ** 2, "Response lengths too variable"


class TestSyntheticDataEvaluation:
    """Tests using synthetic data for controlled experiments."""

    @pytest.mark.integration
    def test_edge_case_handling(self):
        """Test model behavior with edge cases and unusual inputs."""
        edge_cases = [
            ("empty_context", ""),
            ("very_long_prompt", "A" * 1000 + " What is this?"),
            ("special_characters", "What is the meaning of @#$%^&*()? Explain symbols."),
            ("multilingual", "Bonjour! ¿Cómo estás? Wie geht's? What languages do you recognize?"),
            ("numerical", "Calculate: 123 + 456 * 789 / 10 - 50 = ?")
        ]
        
        results = {}
        
        for case_name, prompt in edge_cases:
            try:
                start_time = time.perf_counter()
                response = generate_with_ollama(prompt, model=TEST_MODEL)
                response_time = time.perf_counter() - start_time
                
                results[case_name] = {
                    "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    "prompt_length": len(prompt),
                    "response": response[:200] + "..." if len(response) > 200 else response,
                    "response_length": len(response),
                    "response_time": response_time,
                    "status": "success"
                }
            except Exception as e:
                results[case_name] = {
                    "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    "prompt_length": len(prompt),
                    "error": str(e),
                    "status": "error"
                }
        
        edge_case_data = {
            "test_name": "edge_case_handling",
            "timestamp": time.time(),
            "model": TEST_MODEL,
            "results": results,
            "success_rate": sum(1 for r in results.values() if r["status"] == "success") / len(results)
        }
        
        save_benchmark_output("edge_case_handling", edge_case_data)
        
        # Assert robustness
        assert edge_case_data["success_rate"] > 0.6, f"Too many edge case failures: {edge_case_data['success_rate']}"


class TestContinuousMonitoring:
    """Tests for continuous monitoring capabilities."""

    @pytest.mark.integration
    def test_model_health_check(self):
        """Comprehensive health check for model availability and performance."""
        client = OllamaClient(model=TEST_MODEL)
        
        health_metrics = {
            "connection_test": False,
            "model_availability": False,
            "basic_generation": False,
            "streaming_test": False,
            "error_handling": False
        }
        
        # Connection test
        try:
            health_metrics["connection_test"] = client._check_connection()
        except Exception:
            pass
        
        # Model availability
        try:
            models = client.list_models()
            health_metrics["model_availability"] = any(
                model.get("name") == TEST_MODEL for model in models
            )
        except Exception:
            pass
        
        # Basic generation test
        try:
            response = client.generate("Hello", model=TEST_MODEL)
            health_metrics["basic_generation"] = len(response) > 0
        except Exception:
            pass
        
        # Streaming test
        try:
            chunks = list(client.generate("Count to 3", model=TEST_MODEL, stream=True))
            health_metrics["streaming_test"] = len(chunks) > 0
        except Exception:
            pass
        
        # Error handling test
        try:
            client.generate("Test", model="nonexistent-model")
        except Exception:
            health_metrics["error_handling"] = True
        
        health_score = sum(health_metrics.values()) / len(health_metrics)
        
        health_data = {
            "test_name": "model_health_check",
            "timestamp": time.time(),
            "model": TEST_MODEL,
            "health_metrics": health_metrics,
            "health_score": health_score,
            "status": "healthy" if health_score > 0.8 else "degraded" if health_score > 0.5 else "unhealthy"
        }
        
        save_benchmark_output("model_health_check", health_data)
        
        # Assert minimum health requirements
        assert health_metrics["connection_test"], "Connection test failed"
        assert health_metrics["model_availability"], "Model not available"
        assert health_score > 0.6, f"Overall health too low: {health_score}"
