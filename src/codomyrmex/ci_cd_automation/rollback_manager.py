"""Rollback Management Module for Codomyrmex CI/CD Automation.

This module provides comprehensive rollback capabilities for failed deployments,
including rollback strategies, execution tracking, and recovery mechanisms.
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from collections.abc import Callable

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


class RollbackStrategy(Enum):
    """Rollback strategy types."""
    IMMEDIATE = "immediate"
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    MANUAL = "manual"


@dataclass
class RollbackStep:
    """Individual step in a rollback strategy."""
    name: str
    description: str
    action: Callable
    timeout: int = 300  # 5 minutes default
    retry_count: int = 3
    dependencies: list[str] = field(default_factory=list)


@dataclass
class RollbackPlan:
    """Complete rollback plan for a deployment."""
    deployment_id: str
    strategy: RollbackStrategy
    steps: list[RollbackStep]
    created_at: datetime
    reason: str
    estimated_duration: int
    risk_level: str = "medium"


@dataclass
class RollbackExecution:
    """Execution record for a rollback operation."""
    execution_id: str
    deployment_id: str
    strategy: RollbackStrategy
    status: str
    start_time: datetime
    end_time: datetime | None = None
    current_step: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class RollbackManager:
    """Rollback management and execution system."""

    def __init__(self, workspace_dir: str | None = None):
        """Initialize rollback manager.

        Args:
            workspace_dir: Directory for storing rollback plans and history
        """
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.rollback_plans_dir = self.workspace_dir / "rollback_plans"
        self.rollback_history_dir = self.workspace_dir / "rollback_history"
        self._ensure_directories()

        # In-memory storage
        self._active_rollbacks: dict[str, RollbackExecution] = {}
        self._rollback_plans: dict[str, RollbackPlan] = {}

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.rollback_plans_dir.mkdir(parents=True, exist_ok=True)
        self.rollback_history_dir.mkdir(parents=True, exist_ok=True)

    def create_rollback_plan(
        self,
        deployment_id: str,
        strategy: RollbackStrategy,
        reason: str,
        custom_steps: list[RollbackStep] | None = None
    ) -> RollbackPlan:
        """Create a rollback plan for a failed deployment.

        Args:
            deployment_id: ID of the deployment to rollback
            strategy: Rollback strategy to use
            reason: Reason for the rollback
            custom_steps: Custom steps to include in the plan

        Returns:
            Created rollback plan
        """
        # Create steps based on strategy
        if custom_steps:
            steps = custom_steps
        else:
            steps = self._create_default_steps(strategy)

        plan = RollbackPlan(
            deployment_id=deployment_id,
            strategy=strategy,
            steps=steps,
            created_at=datetime.now(),
            reason=reason,
            estimated_duration=self._calculate_estimated_duration(steps)
        )

        # Save plan
        plan_file = self.rollback_plans_dir / f"plan_{deployment_id}_{int(time.time())}.json"
        with open(plan_file, 'w') as f:
            json.dump({
                "deployment_id": plan.deployment_id,
                "strategy": plan.strategy.value,
                "steps": [{"name": s.name, "description": s.description, "timeout": s.timeout} for s in plan.steps],
                "created_at": plan.created_at.isoformat(),
                "reason": plan.reason,
                "estimated_duration": plan.estimated_duration
            }, f, indent=2)

        self._rollback_plans[deployment_id] = plan
        logger.info(f"Created rollback plan for deployment {deployment_id} using {strategy.value} strategy")

        return plan

    def _create_default_steps(self, strategy: RollbackStrategy) -> list[RollbackStep]:
        """Create default rollback steps for a strategy."""
        if strategy == RollbackStrategy.IMMEDIATE:
            return [
                RollbackStep(
                    name="stop_services",
                    description="Stop all running services",
                    action=self._stop_services,
                    timeout=60
                ),
                RollbackStep(
                    name="restore_backup",
                    description="Restore from backup",
                    action=self._restore_backup,
                    timeout=300
                ),
                RollbackStep(
                    name="restart_services",
                    description="Restart services with restored version",
                    action=self._restart_services,
                    timeout=120
                )
            ]
        elif strategy == RollbackStrategy.ROLLING:
            return [
                RollbackStep(
                    name="identify_healthy_instances",
                    description="Identify instances that are still healthy",
                    action=self._identify_healthy_instances,
                    timeout=30
                ),
                RollbackStep(
                    name="rollback_instances",
                    description="Rollback instances one by one",
                    action=self._rollback_rolling,
                    timeout=600
                ),
                RollbackStep(
                    name="validate_rollback",
                    description="Validate that rollback completed successfully",
                    action=self._validate_rollback,
                    timeout=120
                )
            ]
        else:
            # Generic steps for other strategies
            return [
                RollbackStep(
                    name="prepare_rollback",
                    description="Prepare for rollback",
                    action=self._prepare_rollback,
                    timeout=60
                ),
                RollbackStep(
                    name="execute_rollback",
                    description="Execute rollback procedure",
                    action=self._execute_rollback,
                    timeout=300
                ),
                RollbackStep(
                    name="validate_rollback",
                    description="Validate rollback success",
                    action=self._validate_rollback,
                    timeout=120
                )
            ]

    def _calculate_estimated_duration(self, steps: list[RollbackStep]) -> int:
        """Calculate estimated duration for rollback steps."""
        return sum(step.timeout for step in steps)

    async def execute_rollback(self, deployment_id: str) -> RollbackExecution:
        """Execute a rollback plan.

        Args:
            deployment_id: ID of the deployment to rollback

        Returns:
            Rollback execution record
        """
        if deployment_id not in self._rollback_plans:
            raise CodomyrmexError(f"No rollback plan found for deployment {deployment_id}")

        plan = self._rollback_plans[deployment_id]

        # Create execution record
        execution_id = f"rollback_{deployment_id}_{int(time.time())}"
        execution = RollbackExecution(
            execution_id=execution_id,
            deployment_id=deployment_id,
            strategy=plan.strategy,
            status="running",
            start_time=datetime.now()
        )

        self._active_rollbacks[execution_id] = execution

        try:
            logger.info(f"Starting rollback execution {execution_id} for deployment {deployment_id}")

            # Execute steps
            for i, step in enumerate(plan.steps):
                execution.current_step = i

                try:
                    logger.info(f"Executing rollback step {i+1}/{len(plan.steps)}: {step.name}")

                    # Execute step with timeout
                    # In a real implementation we would actually await self._execute_step_async(step)
                    # Here we simulate it
                    await asyncio.wait_for(
                        self._execute_step_async(step),
                        timeout=step.timeout
                    )

                    execution.completed_steps += 1
                    logger.info(f"Completed rollback step: {step.name}")

                except asyncio.TimeoutError:
                    execution.failed_steps += 1
                    execution.errors.append(f"Step '{step.name}' timed out after {step.timeout}s")
                    logger.error(f"Rollback step '{step.name}' timed out")

                    # For immediate strategy, fail fast
                    if plan.strategy == RollbackStrategy.IMMEDIATE:
                        raise

                except Exception as e:
                    execution.failed_steps += 1
                    execution.errors.append(f"Step '{step.name}' failed: {str(e)}")
                    logger.error(f"Rollback step '{step.name}' failed: {e}")

                    # For immediate strategy, fail fast
                    if plan.strategy == RollbackStrategy.IMMEDIATE:
                        raise

            # Mark as completed or failed
            if execution.failed_steps == 0:
                execution.status = "completed"
                logger.info(f"Rollback execution {execution_id} completed successfully")
            else:
                execution.status = "failed"
                logger.error(f"Rollback execution {execution_id} failed with {execution.failed_steps} failed steps")

        except Exception as e:
            execution.status = "failed"
            execution.errors.append(f"Rollback execution failed: {str(e)}")
            logger.error(f"Rollback execution {execution_id} failed: {e}")
            raise
        finally:
            execution.end_time = datetime.now()

            # Save execution history
            history_file = self.rollback_history_dir / f"execution_{execution_id}.json"
            with open(history_file, 'w') as f:
                json.dump({
                    "execution_id": execution.execution_id,
                    "deployment_id": execution.deployment_id,
                    "strategy": execution.strategy.value,
                    "status": execution.status,
                    "start_time": execution.start_time.isoformat(),
                    "end_time": execution.end_time.isoformat() if execution.end_time else None,
                    "current_step": execution.current_step,
                    "completed_steps": execution.completed_steps,
                    "failed_steps": execution.failed_steps,
                    "errors": execution.errors,
                    "warnings": execution.warnings
                }, f, indent=2)

        return execution

    async def _execute_step_async(self, step: RollbackStep):
        """Execute a rollback step asynchronously."""
        # This would typically call the actual rollback functions
        # For now, simulate execution
        await asyncio.sleep(1)
        step.action()

    def _stop_services(self):
        """Stop all running services."""
        logger.info("Stopping services...")
        # Implementation would stop Docker containers, Kubernetes pods, etc.

    def _restore_backup(self):
        """Restore from backup."""
        logger.info("Restoring from backup...")
        # Implementation would restore from backup storage

    def _restart_services(self):
        """Restart services with restored version."""
        logger.info("Restarting services...")
        # Implementation would restart services

    def _identify_healthy_instances(self):
        """Identify instances that are still healthy."""
        logger.info("Identifying healthy instances...")
        # Implementation would check instance health

    def _rollback_rolling(self):
        """Execute rolling rollback."""
        logger.info("Executing rolling rollback...")
        # Implementation would rollback instances one by one

    def _validate_rollback(self):
        """Validate that rollback completed successfully."""
        logger.info("Validating rollback...")
        # Implementation would run health checks

    def _prepare_rollback(self):
        """Prepare for rollback."""
        logger.info("Preparing for rollback...")
        # Implementation would prepare rollback environment

    def _execute_rollback(self):
        """Execute rollback procedure."""
        logger.info("Executing rollback...")
        # Implementation would execute the main rollback logic

    def get_rollback_status(self, execution_id: str) -> RollbackExecution | None:
        """Get status of a rollback execution.

        Args:
            execution_id: ID of the rollback execution

        Returns:
            Rollback execution record or None if not found
        """
        return self._active_rollbacks.get(execution_id)

    def list_rollback_plans(self) -> list[RollbackPlan]:
        """List all rollback plans.

        Returns:
            List of rollback plans
        """
        return list(self._rollback_plans.values())

    def cancel_rollback(self, execution_id: str) -> bool:
        """Cancel a running rollback.

        Args:
            execution_id: ID of the rollback to cancel

        Returns:
            True if cancelled successfully
        """
        if execution_id in self._active_rollbacks:
            execution = self._active_rollbacks[execution_id]
            execution.status = "cancelled"
            execution.end_time = datetime.now()
            del self._active_rollbacks[execution_id]
            logger.info(f"Cancelled rollback execution {execution_id}")
            return True

        return False


def handle_rollback(
    deployment_id: str,
    strategy: RollbackStrategy = RollbackStrategy.IMMEDIATE,
    reason: str = "Deployment failure",
    workspace_dir: str | None = None
) -> RollbackExecution:
    """Handle rollback for a failed deployment.

    Args:
        deployment_id: ID of the deployment to rollback
        strategy: Rollback strategy to use
        reason: Reason for the rollback
        workspace_dir: Workspace directory

    Returns:
        Rollback execution record
    """
    manager = RollbackManager(workspace_dir)

    # Create rollback plan
    manager.create_rollback_plan(deployment_id, strategy, reason)

    # Execute rollback asynchronously
    # In a real implementation, this would be awaited or run in background
    try:
        # For synchronous execution, we'll run it directly
        # In production, this should be async
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        execution = loop.run_until_complete(manager.execute_rollback(deployment_id))
        loop.close()
        return execution
    except Exception as e:
        logger.error(f"Rollback execution failed: {e}")
        # Return a failed execution record
        return RollbackExecution(
            execution_id=f"failed_{deployment_id}_{int(time.time())}",
            deployment_id=deployment_id,
            strategy=strategy,
            status="failed",
            start_time=datetime.now(),
            errors=[str(e)]
        )
