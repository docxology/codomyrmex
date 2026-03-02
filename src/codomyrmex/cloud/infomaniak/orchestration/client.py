"""
Infomaniak Orchestration Client (Heat).

Provides stack management via OpenStack Heat templates.
"""

from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..base import InfomaniakOpenStackBase

logger = get_logger(__name__)


class InfomaniakHeatClient(InfomaniakOpenStackBase):
    """
    Client for Infomaniak orchestration (Heat) operations.

    Provides methods for managing Heat stacks and templates.
    """

    _service_name = "orchestration"

    # =========================================================================
    # Stack Operations
    # =========================================================================

    def list_stacks(self) -> list[dict[str, Any]]:
        """List all Heat stacks."""
        try:
            stacks = list(self._conn.orchestration.stacks())
            return [
                {
                    "id": s.id,
                    "name": s.name,
                    "status": s.status,
                    "status_reason": s.status_reason,
                    "creation_time": str(s.created_at) if s.created_at else None,
                }
                for s in stacks
            ]
        except Exception as e:
            logger.error(f"Failed to list stacks: {e}")
            return []

    def get_stack(self, stack_id: str) -> dict[str, Any] | None:
        """Get a specific stack by ID or name."""
        try:
            stack = self._conn.orchestration.find_stack(stack_id)
            if stack:
                return {
                    "id": stack.id,
                    "name": stack.name,
                    "status": stack.status,
                    "status_reason": stack.status_reason,
                    "description": stack.description,
                    "parameters": dict(stack.parameters) if stack.parameters else {},
                    "outputs": stack.outputs or [],
                    "creation_time": str(stack.created_at) if stack.created_at else None,
                    "updated_time": str(stack.updated_at) if stack.updated_at else None,
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get stack {stack_id}: {e}")
            return None

    def create_stack(
        self,
        name: str,
        template: str,
        parameters: dict[str, Any] | None = None,
        environment: dict[str, Any] | None = None,
        timeout_mins: int = 60,
        disable_rollback: bool = False,
        **kwargs
    ) -> dict[str, Any] | None:
        """
        Create a new Heat stack.

        Args:
            name: Stack name
            template: Heat template (YAML string or dict)
            parameters: Template parameters
            environment: Environment file contents
            timeout_mins: Stack creation timeout
            disable_rollback: Whether to disable rollback on failure
        """
        try:
            stack = self._conn.orchestration.create_stack(
                name=name,
                template=template,
                parameters=parameters or {},
                environment=environment,
                timeout_mins=timeout_mins,
                disable_rollback=disable_rollback,
                **kwargs
            )
            logger.info(f"Created stack: {stack.id}")
            return {"id": stack.id, "name": name}
        except Exception as e:
            logger.error(f"Failed to create stack {name}: {e}")
            return None

    def create_stack_from_file(
        self,
        name: str,
        template_path: str,
        parameters: dict[str, Any] | None = None,
        **kwargs
    ) -> dict[str, Any] | None:
        """Create a stack from a template file."""
        try:
            with open(template_path) as f:
                template = f.read()
            return self.create_stack(name, template, parameters, **kwargs)
        except Exception as e:
            logger.error(f"Failed to read template {template_path}: {e}")
            return None

    def update_stack(
        self,
        stack_id: str,
        template: str | None = None,
        parameters: dict[str, Any] | None = None,
        environment: dict[str, Any] | None = None,
        **kwargs
    ) -> bool:
        """Update an existing stack."""
        try:
            updates = {}
            if template:
                updates["template"] = template
            if parameters:
                updates["parameters"] = parameters
            if environment:
                updates["environment"] = environment
            updates.update(kwargs)

            self._conn.orchestration.update_stack(stack_id, **updates)
            logger.info(f"Updated stack: {stack_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update stack {stack_id}: {e}")
            return False

    def delete_stack(self, stack_id: str) -> bool:
        """Delete a stack."""
        try:
            self._conn.orchestration.delete_stack(stack_id)
            logger.info(f"Deleted stack: {stack_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete stack {stack_id}: {e}")
            return False

    def suspend_stack(self, stack_id: str) -> bool:
        """Suspend a stack."""
        try:
            self._conn.orchestration.suspend_stack(stack_id)
            logger.info(f"Suspended stack: {stack_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to suspend stack {stack_id}: {e}")
            return False

    def resume_stack(self, stack_id: str) -> bool:
        """Resume a suspended stack."""
        try:
            self._conn.orchestration.resume_stack(stack_id)
            logger.info(f"Resumed stack: {stack_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume stack {stack_id}: {e}")
            return False

    # =========================================================================
    # Stack Resources
    # =========================================================================

    def list_stack_resources(self, stack_id: str) -> list[dict[str, Any]]:
        """List resources in a stack."""
        try:
            resources = list(self._conn.orchestration.resources(stack_id))
            return [
                {
                    "name": r.name,
                    "resource_type": r.resource_type,
                    "status": r.status,
                    "status_reason": r.status_reason,
                    "physical_resource_id": r.physical_resource_id,
                }
                for r in resources
            ]
        except Exception as e:
            logger.error(f"Failed to list resources for stack {stack_id}: {e}")
            return []

    def get_stack_resource(
        self,
        stack_id: str,
        resource_name: str
    ) -> dict[str, Any] | None:
        """Get a specific resource in a stack."""
        try:
            resource = self._conn.orchestration.get_resource(stack_id, resource_name)
            if resource:
                return {
                    "name": resource.name,
                    "resource_type": resource.resource_type,
                    "status": resource.status,
                    "physical_resource_id": resource.physical_resource_id,
                    "attributes": resource.attributes,
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get resource {resource_name}: {e}")
            return None

    # =========================================================================
    # Stack Events
    # =========================================================================

    def list_stack_events(
        self,
        stack_id: str,
        resource_name: str | None = None
    ) -> list[dict[str, Any]]:
        """List events for a stack or specific resource."""
        try:
            events = list(self._conn.orchestration.events(stack_id, resource_name))
            return [
                {
                    "id": e.id,
                    "resource_name": e.resource_name,
                    "resource_status": e.resource_status,
                    "resource_status_reason": e.resource_status_reason,
                    "event_time": str(e.event_time) if e.event_time else None,
                }
                for e in events
            ]
        except Exception as e:
            logger.error(f"Failed to list events for stack {stack_id}: {e}")
            return []

    # =========================================================================
    # Template Operations
    # =========================================================================

    def validate_template(
        self,
        template: str,
        environment: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Validate a Heat template.

        Args:
            template: Heat template (YAML string)
            environment: Optional environment file contents

        Returns:
            Validation result with parameters and description
        """
        try:
            result = self._conn.orchestration.validate_template(
                template=template,
                environment=environment
            )
            return {
                "valid": True,
                "description": result.get("Description", ""),
                "parameters": result.get("Parameters", {}),
            }
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            return {"valid": False, "error": str(e)}

    def get_stack_template(self, stack_id: str) -> str | None:
        """Get the template for an existing stack."""
        try:
            template = self._conn.orchestration.get_stack_template(stack_id)
            return template
        except Exception as e:
            logger.error(f"Failed to get template for stack {stack_id}: {e}")
            return None

    # =========================================================================
    # Stack Outputs
    # =========================================================================

    def get_stack_outputs(self, stack_id: str) -> dict[str, Any]:
        """Get outputs from a stack."""
        try:
            stack = self._conn.orchestration.find_stack(stack_id)
            if stack and stack.outputs:
                return {
                    out.get("output_key"): out.get("output_value")
                    for out in stack.outputs
                }
            return {}
        except Exception as e:
            logger.error(f"Failed to get outputs for stack {stack_id}: {e}")
            return {}
