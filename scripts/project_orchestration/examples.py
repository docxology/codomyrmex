#!/usr/bin/env python3
"""
Comprehensive Orchestration Examples for Codomyrmex

This file demonstrates the full capabilities of the Codomyrmex orchestration system,
including workflow creation, project management, task orchestration, and resource management.

Configuration Files:
- Workflow configurations are loaded from config/workflows/production/*.json
- Example workflows are available in config/workflows/examples/
- Project templates are in src/codomyrmex/project_orchestration/templates/

Documentation:
- Complete examples guide: docs/examples/orchestration-examples.md
- Task orchestration: docs/project_orchestration/task-orchestration-guide.md
- Project lifecycle: docs/project_orchestration/project-lifecycle-guide.md
- Config-driven operations: docs/project_orchestration/config-driven-operations.md

Usage:
    python scripts/project_orchestration/examples.py
    # Or import and run specific examples:
    from scripts.project_orchestration.examples import example_1_basic_workflow_creation
    example_1_basic_workflow_creation()
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Import Codomyrmex orchestration components
from codomyrmex.logistics.orchestration.project import (
    get_orchestration_engine,
    get_workflow_manager,
    get_task_orchestrator,
    get_project_manager,
    get_resource_manager,
    WorkflowStep,
    Task,
    TaskPriority,
    TaskResource,
    ResourceType
)


def example_1_basic_workflow_creation():
    """Example 1: Create and execute a basic workflow."""
    print("=" * 60)
    print("Example 1: Basic Workflow Creation and Execution")
    print("=" * 60)
    
    # Get workflow manager
    wf_manager = get_workflow_manager()
    
    # Create a simple AI analysis workflow
    steps = [
        WorkflowStep(
            name="environment_check",
            module="environment_setup",
            action="check_environment",
            parameters={}
        ),
        WorkflowStep(
            name="code_analysis",
            module="static_analysis",
            action="analyze_code_quality",
            parameters={"path": "."},
            dependencies=["environment_check"]
        ),
        WorkflowStep(
            name="ai_insights",
            module="ai_code_editing",
            action="generate_code_insights",
            parameters={"analysis_data": "{{code_analysis.output}}"},
            dependencies=["code_analysis"]
        ),
        WorkflowStep(
            name="create_report",
            module="data_visualization",
            action="create_analysis_chart",
            parameters={"data": "{{ai_insights.output}}"},
            dependencies=["ai_insights"]
        )
    ]
    
    # Create the workflow
    success = wf_manager.create_workflow("ai_analysis_workflow", steps)
    print(f"✅ Created workflow: {success}")
    
    # List workflows
    workflows = wf_manager.list_workflows()
    print(f"Available workflows: {list(workflows.keys())}")
    
    return success


def example_2_project_management():
    """Example 2: Project creation and management."""
    print("\n" + "=" * 60)
    print("Example 2: Project Management")
    print("=" * 60)
    
    # Get project manager
    project_manager = get_project_manager()
    
    # List available templates
    templates = project_manager.list_templates()
    print(f"Available templates: {templates}")
    
    # Create a new project
    try:
        project = project_manager.create_project(
            name="example_ai_project",
            template_name="ai_analysis",
            description="Example AI analysis project",
            author="Codomyrmex User"
        )
        
        print(f"✅ Created project: {project.name}")
        print(f"   Type: {project.type.value}")
        print(f"   Path: {project.path}")
        print(f"   Workflows: {project.workflows}")
        print(f"   Required modules: {project.required_modules}")
        
        # Get project status
        status = project_manager.get_project_status(project.name)
        print(f"Project status: {json.dumps(status, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return False


def example_3_task_orchestration():
    """Example 3: Task orchestration with dependencies and resources."""
    print("\n" + "=" * 60)
    print("Example 3: Task Orchestration")
    print("=" * 60)
    
    # Get task orchestrator
    task_orchestrator = get_task_orchestrator()
    
    # Create tasks with dependencies
    task1 = Task(
        name="setup_environment",
        module="environment_setup",
        action="check_environment",
        parameters={},
        priority=TaskPriority.HIGH,
        resources=[
            TaskResource(type=ResourceType.CPU, identifier="system_cpu", mode="read")
        ]
    )
    
    task2 = Task(
        name="analyze_code",
        module="static_analysis",
        action="analyze_code_quality",
        parameters={"path": "."},
        dependencies=[task1.id],
        priority=TaskPriority.NORMAL,
        resources=[
            TaskResource(type=ResourceType.CPU, identifier="system_cpu", mode="read"),
            TaskResource(type=ResourceType.MEMORY, identifier="system_memory", mode="read")
        ]
    )
    
    task3 = Task(
        name="generate_insights",
        module="ai_code_editing",
        action="generate_code_insights",
        parameters={"analysis_data": "placeholder"},
        dependencies=[task2.id],
        priority=TaskPriority.NORMAL,
        resources=[
            TaskResource(type=ResourceType.EXTERNAL_API, identifier="openai_api", mode="read")
        ]
    )
    
    # Add tasks to orchestrator
    task1_id = task_orchestrator.add_task(task1)
    task2_id = task_orchestrator.add_task(task2)
    task3_id = task_orchestrator.add_task(task3)
    
    print(f"✅ Added tasks: {task1_id}, {task2_id}, {task3_id}")
    
    # Start execution
    task_orchestrator.start_execution()
    print("✅ Started task execution")
    
    # Wait for completion
    completed = task_orchestrator.wait_for_completion(timeout=30.0)
    print(f"✅ Tasks completed: {completed}")
    
    # Get execution stats
    stats = task_orchestrator.get_execution_stats()
    print(f"Execution stats: {json.dumps(stats, indent=2)}")
    
    return completed


def example_4_resource_management():
    """Example 4: Resource management and allocation."""
    print("\n" + "=" * 60)
    print("Example 4: Resource Management")
    print("=" * 60)
    
    # Get resource manager
    resource_manager = get_resource_manager()
    
    # List available resources
    resources = resource_manager.list_resources()
    print(f"Available resources: {len(resources)}")
    for resource in resources:
        print(f"  - {resource.name} ({resource.type.value}): {resource.status.value}")
    
    # Get resource usage
    usage = resource_manager.get_resource_usage()
    print(f"Resource usage summary: {json.dumps(usage, indent=2)}")
    
    # Test resource allocation
    user_id = "example_user"
    requirements = {
        "cpu": {"cores": 2},
        "memory": {"gb": 4},
        "external_api": {"requests_per_minute": 10}
    }
    
    allocated = resource_manager.allocate_resources(user_id, requirements)
    if allocated:
        print(f"✅ Allocated resources: {allocated}")
        
        # Get user allocations
        user_allocations = resource_manager.get_user_allocations(user_id)
        print(f"User allocations: {json.dumps(user_allocations, indent=2)}")
        
        # Deallocate resources
        deallocated = resource_manager.deallocate_resources(user_id)
        print(f"✅ Deallocated resources: {deallocated}")
    else:
        print("❌ Failed to allocate resources")
    
    return allocated is not None


def example_5_complex_workflow():
    """Example 5: Complex workflow with orchestration engine."""
    print("\n" + "=" * 60)
    print("Example 5: Complex Workflow with Orchestration Engine")
    print("=" * 60)
    
    # Get orchestration engine
    engine = get_orchestration_engine()
    
    # Create a session
    session_id = engine.create_session(
        user_id="example_user",
        mode="resource_aware",
        max_parallel_tasks=2,
        resource_requirements={
            "cpu": {"cores": 1},
            "memory": {"gb": 2}
        }
    )
    print(f"✅ Created session: {session_id}")
    
    # Define a complex workflow
    workflow_definition = {
        "steps": [
            {
                "name": "setup",
                "module": "environment_setup",
                "action": "check_environment",
                "parameters": {}
            },
            {
                "name": "analyze",
                "module": "static_analysis",
                "action": "analyze_code_quality",
                "parameters": {"path": "."}
            },
            {
                "name": "visualize",
                "module": "data_visualization",
                "action": "create_analysis_chart",
                "parameters": {"data": "placeholder"}
            }
        ],
        "dependencies": {
            "analyze": ["setup"],
            "visualize": ["analyze"]
        }
    }
    
    # Execute complex workflow
    result = engine.execute_complex_workflow(workflow_definition, session_id)
    print(f"✅ Complex workflow result: {result['success']}")
    
    if result['success']:
        print(f"   Results: {len(result['results'])} steps completed")
        print(f"   Execution stats: {result['execution_stats']}")
    
    # Get system status
    status = engine.get_system_status()
    print(f"System status: {json.dumps(status, indent=2)}")
    
    # Close session
    closed = engine.close_session(session_id)
    print(f"✅ Closed session: {closed}")
    
    return result['success']


def example_6_performance_monitoring():
    """Example 6: Performance monitoring integration."""
    print("\n" + "=" * 60)
    print("Example 6: Performance Monitoring")
    print("=" * 60)
    
    try:
        from codomyrmex.performance import PerformanceMonitor
        
        # Create performance monitor
        monitor = PerformanceMonitor()
        print("✅ Performance monitor created")
        
        # Get workflow manager with performance monitoring
        wf_manager = get_workflow_manager()
        
        # Create a simple workflow for performance testing
        steps = [
            WorkflowStep(
                name="perf_test",
                module="environment_setup",
                action="check_environment",
                parameters={}
            )
        ]
        
        wf_manager.create_workflow("perf_test_workflow", steps)
        
        # Execute workflow (this will be monitored)
        result = wf_manager.execute_workflow("perf_test_workflow")
        print(f"✅ Workflow executed: {result.status}")
        
        # Get performance summary
        perf_summary = wf_manager.get_performance_summary()
        print(f"Performance summary: {json.dumps(perf_summary, indent=2)}")
        
        return True
        
    except ImportError:
        print("❌ Performance monitoring not available")
        return False
    except Exception as e:
        print(f"❌ Performance monitoring error: {e}")
        return False


def example_7_health_check():
    """Example 7: System health check."""
    print("\n" + "=" * 60)
    print("Example 7: System Health Check")
    print("=" * 60)
    
    # Get orchestration engine
    engine = get_orchestration_engine()
    
    # Perform health check
    health = engine.health_check()
    print(f"Overall health status: {health['overall_status']}")
    
    # Check component health
    components = health.get('components', {})
    for component_name, component_health in components.items():
        status = component_health.get('status', 'unknown')
        print(f"  {component_name}: {status}")
    
    # Check for issues
    issues = health.get('issues', [])
    if issues:
        print(f"Issues found ({len(issues)}):")
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ No issues found")
    
    return health['overall_status'] in ['healthy', 'degraded']


def main():
    """Run all orchestration examples."""
    print("🐜 Codomyrmex Orchestration Examples")
    print("=" * 60)
    
    examples = [
        ("Basic Workflow Creation", example_1_basic_workflow_creation),
        ("Project Management", example_2_project_management),
        ("Task Orchestration", example_3_task_orchestration),
        ("Resource Management", example_4_resource_management),
        ("Complex Workflow", example_5_complex_workflow),
        ("Performance Monitoring", example_6_performance_monitoring),
        ("Health Check", example_7_health_check)
    ]
    
    results = {}
    
    for name, example_func in examples:
        try:
            print(f"\nRunning {name}...")
            result = example_func()
            results[name] = result
            print(f"✅ {name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("EXECUTION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
    
    print(f"\nOverall: {passed}/{total} examples passed")
    
    if passed == total:
        print("🎉 All examples completed successfully!")
    else:
        print("⚠️  Some examples failed. Check the output above for details.")


if __name__ == "__main__":
    main()
