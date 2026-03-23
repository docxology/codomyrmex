import logging
import re
import time
from typing import Any

logger = logging.getLogger(__name__)


class ClaudeTaskPlanningMixin:
    """Mixin for Claude task master planning and decomposition logic."""

    def decompose_task(
        self,
        task: str,
        max_subtasks: int = 10,
        context: str | None = None,
        include_dependencies: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Decompose a complex task into subtasks.

        Args:
            task: Complex task to decompose
            max_subtasks: Maximum number of subtasks
            context: Additional context
            include_dependencies: Whether to include dependency analysis
            **kwargs: Additional arguments

        Returns:
            Dictionary containing subtasks and metadata
        """
        start_time = time.time()

        try:
            system_prompt = (
                "You are a task decomposition expert. Break down complex tasks "
                "into clear, actionable subtasks. Each subtask should be specific, "
                "measurable, and achievable independently where possible."
            )

            if include_dependencies:
                system_prompt += (
                    "\n\nFor each subtask, also identify any dependencies on other subtasks. "
                    "Format dependencies as: [Depends on: subtask numbers]"
                )

            system_prompt += "\n\nFormat your response as a numbered list of subtasks."

            user_message = (
                f"Decompose this task into at most {max_subtasks} subtasks:\n\n{task}"
            )
            if context:
                user_message += f"\n\nContext: {context}"

            response, retries = self._execute_with_retry(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                max_tokens=2048,
                temperature=0.2,
                **kwargs,
            )

            execution_time = time.time() - start_time
            result_text = response.content[0].text if response.content else ""
            input_tokens = (
                response.usage.input_tokens
                if hasattr(response, "usage") and response.usage
                else 0
            )
            output_tokens = (
                response.usage.output_tokens
                if hasattr(response, "usage") and response.usage
                else 0
            )
            tokens_used = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Track totals
            self._total_tokens += tokens_used
            self._total_cost += cost

            subtasks = self._parse_subtasks(result_text, include_dependencies)

            logger.info(
                "Decomposed task into %s subtasks in %.2fs ($%.6f)",
                len(subtasks),
                execution_time,
                cost,
            )

            return {
                "original_task": task,
                "subtasks": subtasks,
                "raw_response": result_text,
                "model": self.model,
                "tokens_used": tokens_used,
                "cost_usd": cost,
                "execution_time": execution_time,
                "status": "success",
                "retries": retries,
            }

        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Error decomposing task: %s", e, exc_info=True)
            raise RuntimeError(f"Task decomposition failed: {e}") from None

    def analyze_task(
        self, task: str, context: str | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Analyze a task for complexity, requirements, and approach.

        Args:
            task: Task to analyze
            context: Additional context
            **kwargs: Additional arguments

        Returns:
            Dictionary containing task analysis
        """
        start_time = time.time()

        try:
            system_prompt = (
                "You are a project planning expert. Analyze the given task and provide:\n"
                "1. Complexity assessment (low/medium/high)\n"
                "2. Estimated effort (hours/days)\n"
                "3. Required skills or resources\n"
                "4. Potential risks or challenges\n"
                "5. Recommended approach\n"
                "6. Success criteria"
            )

            user_message = f"Analyze this task:\n\n{task}"
            if context:
                user_message += f"\n\nContext: {context}"

            response, retries = self._execute_with_retry(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                max_tokens=2048,
                temperature=0.2,
                **kwargs,
            )

            execution_time = time.time() - start_time
            analysis = response.content[0].text if response.content else ""
            input_tokens = (
                response.usage.input_tokens
                if hasattr(response, "usage") and response.usage
                else 0
            )
            output_tokens = (
                response.usage.output_tokens
                if hasattr(response, "usage") and response.usage
                else 0
            )
            tokens_used = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Track totals
            self._total_tokens += tokens_used
            self._total_cost += cost

            # Parse structured analysis
            parsed = self._parse_analysis(analysis)

            logger.info(
                "Analyzed task in %.2fs (%s tokens, $%.6f)",
                execution_time,
                tokens_used,
                cost,
            )

            return {
                "task": task,
                "analysis": analysis,
                "parsed": parsed,
                "model": self.model,
                "tokens_used": tokens_used,
                "cost_usd": cost,
                "execution_time": execution_time,
                "status": "success",
                "retries": retries,
            }

        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Error analyzing task: %s", e, exc_info=True)
            raise RuntimeError(f"Task analysis failed: {e}") from None

    def plan_workflow(
        self,
        goal: str,
        constraints: list[str] | None = None,
        context: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a workflow plan to achieve a goal.

        Args:
            goal: The goal to achieve
            constraints: list of constraints
            context: Additional context
            **kwargs: Additional arguments

        Returns:
            Dictionary containing workflow plan
        """
        start_time = time.time()

        try:
            system_prompt = (
                "You are a workflow planning expert. Create a detailed workflow "
                "plan with clear phases, steps, dependencies, and milestones. "
                "Structure the plan with:\n"
                "1. Overview\n"
                "2. Prerequisites\n"
                "3. Phases with steps\n"
                "4. Milestones and checkpoints\n"
                "5. Risk mitigation strategies"
            )

            user_message = f"Create a workflow plan to achieve:\n\n{goal}"
            if constraints:
                user_message += "\n\nConstraints:\n" + "\n".join(
                    f"- {c}" for c in constraints
                )
            if context:
                user_message += f"\n\nContext: {context}"

            response, retries = self._execute_with_retry(
                messages=[{"role": "user", "content": user_message}],
                system=system_prompt,
                max_tokens=4096,
                temperature=0.3,
                **kwargs,
            )

            execution_time = time.time() - start_time
            plan = response.content[0].text if response.content else ""
            input_tokens = (
                response.usage.input_tokens
                if hasattr(response, "usage") and response.usage
                else 0
            )
            output_tokens = (
                response.usage.output_tokens
                if hasattr(response, "usage") and response.usage
                else 0
            )
            tokens_used = input_tokens + output_tokens
            cost = self._calculate_cost(input_tokens, output_tokens)

            # Track totals
            self._total_tokens += tokens_used
            self._total_cost += cost

            logger.info(
                "Created workflow plan in %.2fs (%s tokens, $%.6f)",
                execution_time,
                tokens_used,
                cost,
            )

            return {
                "goal": goal,
                "constraints": constraints or [],
                "plan": plan,
                "model": self.model,
                "tokens_used": tokens_used,
                "cost_usd": cost,
                "execution_time": execution_time,
                "status": "success",
                "retries": retries,
            }

        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Error planning workflow: %s", e, exc_info=True)
            raise RuntimeError(f"Workflow planning failed: {e}") from None

    def _parse_subtasks(
        self, response: str, include_dependencies: bool = False
    ) -> list[dict[str, Any]]:
        """Parse subtasks from Claude's response."""
        subtasks = []
        lines = response.strip().split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            # Match numbered items: 1. Task, 1) Task, - Task, * Task
            match = re.match(r"^(?:(\d+)[\.\)]\s*|[-*]\s*)(.+)$", line)
            if match:
                number = match.group(1)
                task_text = match.group(2).strip()
                if task_text:
                    subtask: dict[str, Any] = {
                        "id": int(number) if number else i + 1,
                        "description": task_text,
                        "status": "pending",
                    }

                    if include_dependencies:
                        dep_match = re.search(
                            r"\[Depends on:\s*([^\]]+)\]", task_text, re.IGNORECASE
                        )
                        if dep_match:
                            deps = [d.strip() for d in dep_match.group(1).split(",")]
                            subtask["dependencies"] = deps
                            subtask["description"] = re.sub(
                                r"\s*\[Depends on:[^\]]+\]", "", task_text
                            ).strip()

                    subtasks.append(subtask)

        return subtasks

    def _parse_analysis(self, analysis: str) -> dict[str, Any]:
        """Parse structured analysis output."""
        parsed: dict[str, Any] = {
            "complexity": None,
            "effort": None,
            "skills": [],
            "risks": [],
            "approach": None,
        }

        lines = analysis.lower()

        # Extract complexity
        if "high" in lines and "complexity" in lines:
            parsed["complexity"] = "high"
        elif "medium" in lines and "complexity" in lines:
            parsed["complexity"] = "medium"
        elif "low" in lines and "complexity" in lines:
            parsed["complexity"] = "low"

        return parsed
