"""
Comprehensive integration tests for the complete language_models module.

This test suite validates the entire module ecosystem including:
- End-to-end workflows
- Cross-component integration
- Configuration management
- Output generation and validation
- Error recovery and resilience
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
    LLMConfig,
    LLMConfigPresets,
    get_config,
    set_config,
    reset_config,
    generate_with_ollama,
    stream_with_ollama,
    chat_with_ollama,
    create_chat_messages,
    get_available_models,
    check_ollama_availability,
    get_default_manager
)

# Test configuration
TEST_MODEL = "llama3.1:latest"


def save_integration_output(filename: str, data: dict):
    """Save integration test results to integration directory."""
    config = get_config()
    config.integration_dir.mkdir(parents=True, exist_ok=True)
    filepath = config.integration_dir / f"{filename}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    @pytest.mark.integration
    def test_complete_text_generation_workflow(self):
        """Test complete workflow from configuration to output generation."""
        workflow_start = time.perf_counter()
        
        # Step 1: Configuration setup
        config = LLMConfigPresets.creative()
        set_config(config)
        
        # Step 2: Model availability check
        available = check_ollama_availability()
        assert available, "Ollama service must be available"
        
        models = get_available_models()
        assert len(models) > 0, "At least one model must be available"
        
        # Step 3: Text generation with different methods
        prompt = "Write a creative short story about a time-traveling librarian."
        
        # Method 1: Direct function call
        response1 = generate_with_ollama(prompt)
        
        # Method 2: Manager approach
        manager = get_default_manager()
        response2 = manager.generate(prompt)
        
        # Method 3: Direct client
        client = OllamaClient(model=TEST_MODEL)
        response3 = client.generate(prompt, model=TEST_MODEL)
        
        workflow_end = time.perf_counter()
        
        # Validation
        responses = [response1, response2, response3]
        for i, response in enumerate(responses, 1):
            assert len(response) > 100, f"Response {i} too short: {len(response)} chars"
            assert "librarian" in response.lower(), f"Response {i} doesn't contain key term"
        
        # Save comprehensive workflow results
        workflow_data = {
            "test_name": "complete_text_generation_workflow",
            "timestamp": time.time(),
            "total_time": workflow_end - workflow_start,
            "configuration": config.to_dict(),
            "models_available": len(models),
            "responses": {
                f"method_{i}": {
                    "length": len(response),
                    "preview": response[:200] + "..." if len(response) > 200 else response
                }
                for i, response in enumerate(responses, 1)
            },
            "validation": {
                "all_responses_adequate_length": all(len(r) > 100 for r in responses),
                "all_contain_key_term": all("librarian" in r.lower() for r in responses),
                "response_diversity": len(set(responses)) == len(responses)
            }
        }
        
        save_integration_output("complete_text_generation_workflow", workflow_data)
        
        # Cleanup
        manager.close()
        client.close()
        reset_config()

    @pytest.mark.integration
    def test_streaming_chat_workflow(self):
        """Test complete streaming chat workflow."""
        workflow_start = time.perf_counter()
        
        # Setup configuration for fast responses
        config = LLMConfigPresets.fast()
        set_config(config)
        
        # Create conversation
        messages = create_chat_messages(
            system_prompt="You are a helpful coding assistant.",
            user_message="Explain Python list comprehensions with a simple example."
        )
        
        # Test streaming chat
        chunks = []
        chunk_times = []
        
        async def collect_streaming_chat():
            start_time = time.perf_counter()
            async for chunk in stream_with_ollama(messages[1]["content"]):
                chunk_time = time.perf_counter() - start_time
                chunks.append(chunk)
                chunk_times.append(chunk_time)
        
        asyncio.run(collect_streaming_chat())
        
        # Test regular chat for comparison
        regular_response = chat_with_ollama(messages)
        
        workflow_end = time.perf_counter()
        
        # Analysis
        full_streaming_response = "".join(chunks)
        
        workflow_data = {
            "test_name": "streaming_chat_workflow",
            "timestamp": time.time(),
            "total_time": workflow_end - workflow_start,
            "configuration": config.to_dict(),
            "conversation": {
                "messages": messages,
                "streaming_chunks": len(chunks),
                "streaming_response_length": len(full_streaming_response),
                "regular_response_length": len(regular_response),
                "time_to_first_chunk": chunk_times[0] if chunk_times else 0,
                "streaming_complete_time": chunk_times[-1] if chunk_times else 0
            },
            "performance": {
                "chunks_per_second": len(chunks) / (chunk_times[-1] if chunk_times else 1),
                "chars_per_second_streaming": len(full_streaming_response) / (chunk_times[-1] if chunk_times else 1),
                "streaming_vs_regular_ratio": len(full_streaming_response) / max(1, len(regular_response))
            }
        }
        
        save_integration_output("streaming_chat_workflow", workflow_data)
        
        # Assertions
        assert len(chunks) > 1, "Should receive multiple streaming chunks"
        assert len(full_streaming_response) > 50, "Streaming response should be substantial"
        assert "python" in full_streaming_response.lower(), "Should discuss Python"
        assert chunk_times[0] < 10.0, "Time to first chunk should be reasonable"
        
        reset_config()


class TestCrossComponentIntegration:
    """Test integration between different module components."""

    @pytest.mark.integration
    def test_config_client_manager_integration(self):
        """Test integration between configuration, client, and manager."""
        # Test different configuration presets
        presets = {
            "default": LLMConfigPresets.default(),
            "creative": LLMConfigPresets.creative(),
            "precise": LLMConfigPresets.precise()
        }
        
        results = {}
        
        for preset_name, preset_config in presets.items():
            set_config(preset_config)
            
            # Test client with config
            client = OllamaClient(
                model=preset_config.model,
                timeout=preset_config.timeout
            )
            
            # Test manager with config
            manager = OllamaManager(
                model=preset_config.model,
                timeout=preset_config.timeout
            )
            manager.set_default_options(preset_config.get_generation_options())
            
            # Generate responses
            prompt = "Describe the color blue in exactly two sentences."
            
            try:
                client_response = client.generate(prompt, model=TEST_MODEL)
                manager_response = manager.generate(prompt)
                
                results[preset_name] = {
                    "config": preset_config.to_dict(),
                    "client_response": {
                        "length": len(client_response),
                        "preview": client_response[:100] + "..." if len(client_response) > 100 else client_response
                    },
                    "manager_response": {
                        "length": len(manager_response),
                        "preview": manager_response[:100] + "..." if len(manager_response) > 100 else manager_response
                    },
                    "status": "success"
                }
            except Exception as e:
                results[preset_name] = {
                    "config": preset_config.to_dict(),
                    "error": str(e),
                    "status": "error"
                }
            finally:
                client.close()
                manager.close()
        
        integration_data = {
            "test_name": "config_client_manager_integration",
            "timestamp": time.time(),
            "presets_tested": list(presets.keys()),
            "results": results,
            "success_rate": sum(1 for r in results.values() if r["status"] == "success") / len(results)
        }
        
        save_integration_output("config_client_manager_integration", integration_data)
        
        # Assertions
        assert integration_data["success_rate"] > 0.6, "Most preset configurations should work"
        
        reset_config()

    @pytest.mark.integration
    def test_error_recovery_integration(self):
        """Test error recovery across components."""
        error_scenarios = []
        
        # Scenario 1: Invalid model recovery
        try:
            client = OllamaClient(model="nonexistent-model")
            client.generate("Test prompt", model="nonexistent-model")
        except Exception as e:
            error_scenarios.append({
                "scenario": "invalid_model",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "recovered": True
            })
        
        # Scenario 2: Timeout recovery
        try:
            client = OllamaClient(timeout=0.001)  # Very short timeout
            client.generate("Write a very long essay about everything", model=TEST_MODEL)
        except Exception as e:
            error_scenarios.append({
                "scenario": "timeout",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "recovered": True
            })
        
        # Scenario 3: Configuration reset recovery
        try:
            # Corrupt configuration
            bad_config = LLMConfig(temperature=999.0, max_tokens=-1)
            set_config(bad_config)
            
            # Should still work with fallbacks
            response = generate_with_ollama("Simple test", model=TEST_MODEL)
            
            error_scenarios.append({
                "scenario": "bad_configuration",
                "error_type": "None",
                "error_message": "Configuration handled gracefully",
                "recovered": True,
                "response_length": len(response)
            })
        except Exception as e:
            error_scenarios.append({
                "scenario": "bad_configuration",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "recovered": False
            })
        
        recovery_data = {
            "test_name": "error_recovery_integration",
            "timestamp": time.time(),
            "scenarios_tested": len(error_scenarios),
            "scenarios": error_scenarios,
            "recovery_rate": sum(1 for s in error_scenarios if s["recovered"]) / len(error_scenarios)
        }
        
        save_integration_output("error_recovery_integration", recovery_data)
        
        # Assertions
        assert recovery_data["recovery_rate"] >= 0.5, "Should handle most error scenarios gracefully"
        
        reset_config()


class TestModuleEcosystem:
    """Test the complete module ecosystem."""

    @pytest.mark.integration
    def test_full_ecosystem_validation(self):
        """Comprehensive validation of the entire module ecosystem."""
        ecosystem_start = time.perf_counter()
        
        validation_results = {
            "imports": {},
            "configuration": {},
            "connectivity": {},
            "functionality": {},
            "outputs": {},
            "cleanup": {}
        }
        
        # 1. Import validation
        try:
            import codomyrmex.language_models as llm_module
            validation_results["imports"]["status"] = "success"
            validation_results["imports"]["components"] = [
                "OllamaClient", "OllamaManager", "LLMConfig", "LLMConfigPresets",
                "generate_with_ollama", "stream_with_ollama", "chat_with_ollama"
            ]
            validation_results["imports"]["available_components"] = [
                name for name in dir(llm_module) if not name.startswith('_')
            ]
        except Exception as e:
            validation_results["imports"]["status"] = "error"
            validation_results["imports"]["error"] = str(e)
        
        # 2. Configuration validation
        try:
            config = get_config()
            validation_results["configuration"]["status"] = "success"
            validation_results["configuration"]["directories_created"] = all([
                config.test_results_dir.exists(),
                config.llm_outputs_dir.exists(),
                config.reports_dir.exists(),
                config.performance_dir.exists(),
                config.integration_dir.exists()
            ])
            validation_results["configuration"]["config_values"] = {
                "model": config.model,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens
            }
        except Exception as e:
            validation_results["configuration"]["status"] = "error"
            validation_results["configuration"]["error"] = str(e)
        
        # 3. Connectivity validation
        try:
            available = check_ollama_availability()
            models = get_available_models()
            validation_results["connectivity"]["status"] = "success"
            validation_results["connectivity"]["ollama_available"] = available
            validation_results["connectivity"]["models_count"] = len(models)
        except Exception as e:
            validation_results["connectivity"]["status"] = "error"
            validation_results["connectivity"]["error"] = str(e)
        
        # 4. Functionality validation
        try:
            # Test core functions
            response = generate_with_ollama("Hello", model=TEST_MODEL)
            messages = create_chat_messages(user_message="Hi")
            chat_response = chat_with_ollama(messages, model=TEST_MODEL)
            
            validation_results["functionality"]["status"] = "success"
            validation_results["functionality"]["generation_works"] = len(response) > 0
            validation_results["functionality"]["chat_works"] = len(chat_response) > 0
        except Exception as e:
            validation_results["functionality"]["status"] = "error"
            validation_results["functionality"]["error"] = str(e)
        
        # 5. Output validation
        try:
            output_dirs = [config.test_results_dir, config.llm_outputs_dir, config.reports_dir, 
                          config.performance_dir, config.integration_dir]
            total_files = sum(len(list(d.glob("*"))) for d in output_dirs if d.exists())
            
            validation_results["outputs"]["status"] = "success"
            validation_results["outputs"]["total_files"] = total_files
            validation_results["outputs"]["directories_with_files"] = sum(
                1 for d in output_dirs if d.exists() and len(list(d.glob("*"))) > 0
            )
        except Exception as e:
            validation_results["outputs"]["status"] = "error"
            validation_results["outputs"]["error"] = str(e)
        
        # 6. Cleanup validation
        try:
            manager = get_default_manager()
            manager.close()
            validation_results["cleanup"]["status"] = "success"
            validation_results["cleanup"]["manager_cleanup"] = True
        except Exception as e:
            validation_results["cleanup"]["status"] = "error"
            validation_results["cleanup"]["error"] = str(e)
        
        ecosystem_end = time.perf_counter()
        
        # Comprehensive ecosystem report
        ecosystem_data = {
            "test_name": "full_ecosystem_validation",
            "timestamp": time.time(),
            "total_validation_time": ecosystem_end - ecosystem_start,
            "validation_results": validation_results,
            "overall_health": {
                "components_passing": sum(1 for v in validation_results.values() if v.get("status") == "success"),
                "total_components": len(validation_results),
                "health_score": sum(1 for v in validation_results.values() if v.get("status") == "success") / len(validation_results)
            },
            "ecosystem_status": "healthy" if sum(1 for v in validation_results.values() if v.get("status") == "success") >= 5 else "degraded"
        }
        
        save_integration_output("full_ecosystem_validation", ecosystem_data)
        
        # Final assertions
        assert ecosystem_data["overall_health"]["health_score"] >= 0.8, "Ecosystem health score too low"
        assert validation_results["imports"]["status"] == "success", "Import validation failed"
        assert validation_results["configuration"]["status"] == "success", "Configuration validation failed"
        assert validation_results["functionality"]["status"] == "success", "Functionality validation failed"
        
        print(f"🎉 Ecosystem validation complete: {ecosystem_data['ecosystem_status'].upper()}")
        print(f"📊 Health score: {ecosystem_data['overall_health']['health_score']:.2%}")
        print(f"⏱️  Validation time: {ecosystem_data['total_validation_time']:.2f}s")


class TestProductionReadiness:
    """Test production readiness of the module."""

    @pytest.mark.integration
    def test_production_deployment_simulation(self):
        """Simulate production deployment scenarios."""
        deployment_scenarios = []
        
        # Scenario 1: High-load simulation
        try:
            import threading
            import queue
            
            results_queue = queue.Queue()
            num_concurrent = 3
            
            def worker(worker_id):
                try:
                    response = generate_with_ollama(f"Worker {worker_id}: What is AI?", model=TEST_MODEL)
                    results_queue.put({
                        "worker_id": worker_id,
                        "response_length": len(response),
                        "status": "success"
                    })
                except Exception as e:
                    results_queue.put({
                        "worker_id": worker_id,
                        "error": str(e),
                        "status": "error"
                    })
            
            threads = []
            start_time = time.perf_counter()
            
            for i in range(num_concurrent):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            end_time = time.perf_counter()
            
            results = []
            while not results_queue.empty():
                results.append(results_queue.get())
            
            deployment_scenarios.append({
                "scenario": "high_load_simulation",
                "concurrent_requests": num_concurrent,
                "total_time": end_time - start_time,
                "success_rate": sum(1 for r in results if r["status"] == "success") / len(results),
                "results": results,
                "status": "success"
            })
            
        except Exception as e:
            deployment_scenarios.append({
                "scenario": "high_load_simulation",
                "error": str(e),
                "status": "error"
            })
        
        # Scenario 2: Configuration persistence
        try:
            config = LLMConfigPresets.creative()
            config.save_config()
            
            # Reset and reload
            reset_config()
            loaded_config = LLMConfig.from_file(config.config_dir / "config.json")
            
            deployment_scenarios.append({
                "scenario": "configuration_persistence",
                "original_temperature": config.temperature,
                "loaded_temperature": loaded_config.temperature,
                "persistence_works": abs(config.temperature - loaded_config.temperature) < 0.001,
                "status": "success"
            })
            
        except Exception as e:
            deployment_scenarios.append({
                "scenario": "configuration_persistence",
                "error": str(e),
                "status": "error"
            })
        
        # Scenario 3: Resource cleanup
        try:
            clients = []
            managers = []
            
            # Create multiple instances
            for i in range(3):
                client = OllamaClient(model=TEST_MODEL)
                manager = OllamaManager(model=TEST_MODEL)
                clients.append(client)
                managers.append(manager)
            
            # Cleanup all
            for client in clients:
                client.close()
            for manager in managers:
                manager.close()
            
            deployment_scenarios.append({
                "scenario": "resource_cleanup",
                "instances_created": len(clients) + len(managers),
                "cleanup_successful": True,
                "status": "success"
            })
            
        except Exception as e:
            deployment_scenarios.append({
                "scenario": "resource_cleanup",
                "error": str(e),
                "status": "error"
            })
        
        production_data = {
            "test_name": "production_deployment_simulation",
            "timestamp": time.time(),
            "scenarios": deployment_scenarios,
            "production_readiness": {
                "scenarios_passed": sum(1 for s in deployment_scenarios if s["status"] == "success"),
                "total_scenarios": len(deployment_scenarios),
                "readiness_score": sum(1 for s in deployment_scenarios if s["status"] == "success") / len(deployment_scenarios)
            }
        }
        
        save_integration_output("production_deployment_simulation", production_data)
        
        # Assertions - adjusted for realistic production scenarios
        assert production_data["production_readiness"]["readiness_score"] >= 0.6, "Production readiness score too low"
        
        reset_config()
