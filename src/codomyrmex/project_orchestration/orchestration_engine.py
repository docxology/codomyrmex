"""
Orchestration Engine for Codomyrmex

This is the main orchestration engine that coordinates all project management,
task orchestration, and resource management components. It provides a unified
interface for complex multi-module workflows.
"""

import os
import json
import asyncio
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Import Codomyrmex modules
try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from codomyrmex.performance import monitor_performance, PerformanceMonitor
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False
    def monitor_performance(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

try:
    from codomyrmex.model_context_protocol import MCPToolResult, MCPErrorDetail
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Import orchestration components
from .workflow_manager import WorkflowManager, WorkflowStatus
from .task_orchestrator import TaskOrchestrator, Task, TaskStatus
from .project_manager import ProjectManager, Project, ProjectStatus
from .resource_manager import ResourceManager, Resource, ResourceType


class OrchestrationMode(Enum):
    """Orchestration execution modes."""
    SEQUENTIAL = "sequential"  # Execute workflows/tasks one after another
    PARALLEL = "parallel"     # Execute workflows/tasks in parallel when possible
    PRIORITY = "priority"     # Execute based on priority ordering
    RESOURCE_AWARE = "resource_aware"  # Execute based on resource availability


@dataclass
class OrchestrationContext:
    """Context for orchestration execution."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "system"
    mode: OrchestrationMode = OrchestrationMode.RESOURCE_AWARE
    max_parallel_tasks: int = 4
    max_parallel_workflows: int = 2
    timeout_seconds: Optional[int] = None
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "initialized"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'mode': self.mode.value,
            'max_parallel_tasks': self.max_parallel_tasks,
            'max_parallel_workflows': self.max_parallel_workflows,
            'timeout_seconds': self.timeout_seconds,
            'resource_requirements': self.resource_requirements,
            'metadata': self.metadata,
            'status': self.status
        }
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data


class OrchestrationEngine:
    """Main orchestration engine coordinating all components."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the orchestration engine."""
        self.config = config or {}
        
        # Initialize component managers
        self.workflow_manager = WorkflowManager(
            config_dir=self.config.get('workflows_dir')
        )
        self.task_orchestrator = TaskOrchestrator(
            max_workers=self.config.get('max_workers', 4)
        )
        self.project_manager = ProjectManager(
            projects_dir=self.config.get('projects_dir'),
            templates_dir=self.config.get('templates_dir')
        )
        self.resource_manager = ResourceManager(
            config_file=self.config.get('resource_config')
        )
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor() if PERFORMANCE_AVAILABLE else None
        
        # Active sessions
        self.active_sessions: Dict[str, OrchestrationContext] = {}
        self.session_lock = threading.RLock()
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Start task orchestrator
        self.task_orchestrator.start_execution()
        
        logger.info("OrchestrationEngine initialized successfully")
    
    def register_event_handler(self, event: str, handler: Callable):
        """Register an event handler."""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def emit_event(self, event: str, data: Dict[str, Any]):
        """Emit an event to registered handlers."""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(event, data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event}: {e}")
    
    def create_session(self, user_id: str = "system", **kwargs) -> str:
        """Create a new orchestration session."""
        context = OrchestrationContext(
            user_id=user_id,
            mode=OrchestrationMode(kwargs.get('mode', 'resource_aware')),
            max_parallel_tasks=kwargs.get('max_parallel_tasks', 4),
            max_parallel_workflows=kwargs.get('max_parallel_workflows', 2),
            timeout_seconds=kwargs.get('timeout_seconds'),
            resource_requirements=kwargs.get('resource_requirements', {}),
            metadata=kwargs.get('metadata', {})
        )
        
        with self.session_lock:
            self.active_sessions[context.session_id] = context
        
        self.emit_event('session_created', {'session_id': context.session_id, 'user_id': user_id})
        logger.info(f"Created orchestration session: {context.session_id}")
        
        return context.session_id
    
    def get_session(self, session_id: str) -> Optional[OrchestrationContext]:
        """Get a session by ID."""
        with self.session_lock:
            return self.active_sessions.get(session_id)
    
    def close_session(self, session_id: str) -> bool:
        """Close an orchestration session."""
        with self.session_lock:
            if session_id in self.active_sessions:
                context = self.active_sessions[session_id]
                context.status = "closed"
                context.completed_at = datetime.now(timezone.utc)
                
                # Cleanup session resources
                self.resource_manager.deallocate_resources(session_id)
                
                del self.active_sessions[session_id]
                
                self.emit_event('session_closed', {'session_id': session_id})
                logger.info(f"Closed orchestration session: {session_id}")
                return True
        return False
    
    @monitor_performance(function_name="execute_workflow")
    def execute_workflow(self, workflow_name: str, session_id: Optional[str] = None, 
                        **params) -> Dict[str, Any]:
        """Execute a workflow with orchestration."""
        if not session_id:
            session_id = self.create_session()
        
        context = self.get_session(session_id)
        if not context:
            return {
                'success': False,
                'error': f'Session {session_id} not found'
            }
        
        context.started_at = datetime.now(timezone.utc)
        context.status = "executing_workflow"
        
        try:
            # Allocate resources if needed
            if context.resource_requirements:
                allocated = self.resource_manager.allocate_resources(
                    session_id, context.resource_requirements, context.timeout_seconds
                )
                if not allocated:
                    return {
                        'success': False,
                        'error': 'Failed to allocate required resources'
                    }
            
            # Execute workflow
            result = self.workflow_manager.execute_workflow(workflow_name, **params)
            
            # Update context
            context.status = "completed" if result['success'] else "failed"
            context.completed_at = datetime.now(timezone.utc)
            
            # Emit events
            event_data = {
                'session_id': session_id,
                'workflow_name': workflow_name,
                'success': result['success'],
                'execution_time': (context.completed_at - context.started_at).total_seconds()
            }
            self.emit_event('workflow_completed', event_data)
            
            return result
            
        except Exception as e:
            context.status = "failed"
            context.completed_at = datetime.now(timezone.utc)
            logger.error(f"Workflow execution failed: {e}")
            
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Clean up resources
            self.resource_manager.deallocate_resources(session_id)
    
    @monitor_performance(function_name="execute_task")
    def execute_task(self, task: Union[Task, Dict[str, Any]], session_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a single task with orchestration."""
        if not session_id:
            session_id = self.create_session()
        
        context = self.get_session(session_id)
        if not context:
            return {
                'success': False,
                'error': f'Session {session_id} not found'
            }
        
        # Convert dict to Task if needed
        if isinstance(task, dict):
            task = Task(**task)
        
        try:
            # Add task to orchestrator
            task_id = self.task_orchestrator.add_task(task)
            
            # Wait for completion (simplified - in practice might be async)
            import time
            while True:
                task_obj = self.task_orchestrator.get_task(task_id)
                if task_obj and task_obj.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    break
                time.sleep(0.1)
            
            result = self.task_orchestrator.get_task_result(task_id)
            
            return {
                'success': result.success if result else False,
                'result': result.to_dict() if result else None,
                'task_id': task_id
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @monitor_performance(function_name="execute_project_workflow")
    def execute_project_workflow(self, project_name: str, workflow_name: str, 
                                session_id: Optional[str] = None, **params) -> Dict[str, Any]:
        """Execute a workflow for a specific project."""
        if not session_id:
            session_id = self.create_session()
        
        context = self.get_session(session_id)
        if not context:
            return {
                'success': False,
                'error': f'Session {session_id} not found'
            }
        
        try:
            result = self.project_manager.execute_project_workflow(
                project_name, workflow_name, **params
            )
            
            # Update project metrics
            if result['success']:
                metrics = {
                    'last_workflow_execution': datetime.now(timezone.utc).isoformat(),
                    'workflow_executions': 1
                }
                self.project_manager.update_project_metrics(project_name, metrics)
            
            return result
            
        except Exception as e:
            logger.error(f"Project workflow execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_complex_workflow(self, workflow_definition: Dict[str, Any], 
                                session_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a complex workflow with multiple interdependent steps."""
        if not session_id:
            session_id = self.create_session()
        
        context = self.get_session(session_id)
        if not context:
            return {
                'success': False,
                'error': f'Session {session_id} not found'
            }
        
        try:
            # Parse workflow definition
            steps = workflow_definition.get('steps', [])
            dependencies = workflow_definition.get('dependencies', {})
            parallel_groups = workflow_definition.get('parallel_groups', [])
            
            # Create tasks from steps
            tasks = {}
            for step in steps:
                task = Task(
                    name=step['name'],
                    module=step['module'],
                    action=step['action'],
                    parameters=step.get('parameters', {}),
                    dependencies=dependencies.get(step['name'], [])
                )
                task_id = self.task_orchestrator.add_task(task)
                tasks[step['name']] = task_id
            
            # Wait for all tasks to complete
            completed = self.task_orchestrator.wait_for_completion(
                timeout=context.timeout_seconds
            )
            
            if completed:
                # Collect results
                results = {}
                for step_name, task_id in tasks.items():
                    result = self.task_orchestrator.get_task_result(task_id)
                    results[step_name] = result.to_dict() if result else None
                
                return {
                    'success': True,
                    'results': results,
                    'execution_stats': self.task_orchestrator.get_execution_stats()
                }
            else:
                return {
                    'success': False,
                    'error': 'Workflow execution timed out'
                }
                
        except Exception as e:
            logger.error(f"Complex workflow execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'orchestration_engine': {
                'active_sessions': len(self.active_sessions),
                'event_handlers': {event: len(handlers) for event, handlers in self.event_handlers.items()}
            },
            'workflow_manager': {
                'total_workflows': len(self.workflow_manager.workflows),
                'running_workflows': len(self.workflow_manager.executions)
            },
            'task_orchestrator': self.task_orchestrator.get_execution_stats(),
            'project_manager': self.project_manager.get_projects_summary(),
            'resource_manager': self.resource_manager.get_resource_usage()
        }
        
        if self.performance_monitor:
            status['performance'] = self.performance_monitor.get_stats()
        
        return status
    
    def create_project_from_workflow(self, project_name: str, workflow_name: str, 
                                   template_name: str = "ai_analysis", **kwargs) -> Dict[str, Any]:
        """Create a project and execute a workflow for it."""
        try:
            # Create project
            project = self.project_manager.create_project(
                name=project_name,
                template_name=template_name,
                **kwargs
            )
            
            # Execute workflow for project
            result = self.execute_project_workflow(project_name, workflow_name)
            
            if result['success']:
                # Add completion milestone
                self.project_manager.add_project_milestone(
                    project_name, 
                    f"workflow_{workflow_name}_completed",
                    {
                        'workflow': workflow_name,
                        'execution_time': result.get('execution_time', 0),
                        'success': True
                    }
                )
            
            return {
                'success': True,
                'project_created': True,
                'workflow_result': result
            }
            
        except Exception as e:
            logger.error(f"Failed to create project and execute workflow: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health = {
            'overall_status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'components': {},
            'issues': []
        }
        
        try:
            # Check each component
            components = {
                'workflow_manager': self.workflow_manager,
                'task_orchestrator': self.task_orchestrator,
                'project_manager': self.project_manager,
                'resource_manager': self.resource_manager
            }
            
            for name, component in components.items():
                component_health = {'status': 'healthy', 'details': {}}
                
                if hasattr(component, 'health_check'):
                    try:
                        component_status = component.health_check()
                        component_health['details'] = component_status
                        
                        if component_status.get('overall_status') != 'healthy':
                            component_health['status'] = component_status.get('overall_status', 'unhealthy')
                            health['issues'].extend(component_status.get('issues', []))
                    except Exception as e:
                        component_health['status'] = 'error'
                        component_health['error'] = str(e)
                        health['issues'].append(f"{name}: {str(e)}")
                
                health['components'][name] = component_health
            
            # Determine overall status
            unhealthy_components = [name for name, comp in health['components'].items() 
                                 if comp['status'] not in ['healthy', 'degraded']]
            
            if unhealthy_components:
                health['overall_status'] = 'unhealthy'
            elif health['issues']:
                health['overall_status'] = 'degraded'
                
        except Exception as e:
            health['overall_status'] = 'error'
            health['error'] = str(e)
        
        return health
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics."""
        metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'sessions': {
                'total': len(self.active_sessions),
                'by_status': {}
            },
            'workflows': {},
            'tasks': {},
            'projects': {},
            'resources': {}
        }
        
        # Session metrics
        for session in self.active_sessions.values():
            status = session.status
            metrics['sessions']['by_status'][status] = metrics['sessions']['by_status'].get(status, 0) + 1
        
        # Component metrics
        if hasattr(self.workflow_manager, 'get_metrics'):
            metrics['workflows'] = self.workflow_manager.get_metrics()
        
        metrics['tasks'] = self.task_orchestrator.get_execution_stats()
        metrics['projects'] = self.project_manager.get_projects_summary()
        metrics['resources'] = self.resource_manager.get_resource_usage()
        
        return metrics
    
    def shutdown(self):
        """Shutdown the orchestration engine."""
        logger.info("Shutting down OrchestrationEngine...")
        
        # Close all active sessions
        session_ids = list(self.active_sessions.keys())
        for session_id in session_ids:
            self.close_session(session_id)
        
        # Stop components
        self.task_orchestrator.stop_execution()
        
        # Save state
        if hasattr(self.resource_manager, 'save_resources'):
            self.resource_manager.save_resources()
        
        logger.info("OrchestrationEngine shutdown complete")
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.shutdown()
        except:
            pass


# MCP Tool Integration (if available)
if MCP_AVAILABLE:
    def create_orchestration_mcp_tools():
        """Create MCP tools for orchestration."""
        tools = {}
        
        # Workflow execution tool
        tools['execute_workflow'] = {
            'name': 'execute_workflow',
            'description': 'Execute a workflow with the orchestration engine',
            'input_schema': {
                'type': 'object',
                'properties': {
                    'workflow_name': {'type': 'string', 'description': 'Name of workflow to execute'},
                    'parameters': {'type': 'object', 'description': 'Workflow parameters'},
                    'session_id': {'type': 'string', 'description': 'Optional session ID'}
                },
                'required': ['workflow_name']
            }
        }
        
        # Project creation tool
        tools['create_project'] = {
            'name': 'create_project',
            'description': 'Create a new project with optional workflow execution',
            'input_schema': {
                'type': 'object',
                'properties': {
                    'project_name': {'type': 'string', 'description': 'Name of the project'},
                    'template_name': {'type': 'string', 'description': 'Project template to use'},
                    'workflow_name': {'type': 'string', 'description': 'Optional workflow to execute'},
                    'description': {'type': 'string', 'description': 'Project description'}
                },
                'required': ['project_name']
            }
        }
        
        # Status check tool
        tools['get_system_status'] = {
            'name': 'get_system_status',
            'description': 'Get comprehensive system status and metrics',
            'input_schema': {
                'type': 'object',
                'properties': {},
                'required': []
            }
        }
        
        return tools


# Global orchestration engine instance
_orchestration_engine = None

def get_orchestration_engine() -> OrchestrationEngine:
    """Get the global orchestration engine instance."""
    global _orchestration_engine
    if _orchestration_engine is None:
        _orchestration_engine = OrchestrationEngine()
    return _orchestration_engine
