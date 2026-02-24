
import json
from typing import Any
from collections.abc import Iterator

from codomyrmex.agents.core.base import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.git_operations.api.github import (
    create_issue,
    list_issues,
)
from codomyrmex.git_operations.core.git import (
    add_remote,
    clean_repository,
    list_remotes,
)
from codomyrmex.git_operations.core.repository import RepositoryManager
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class GitAgent(BaseAgent):
    """
    Agent specialized for Git and GitHub operations.

    Capabilities:
    - Repository Management (Sync, Clean, Prune)
    - Remote Management
    - Issue Management
    """

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        repository_manager: RepositoryManager | None = None,
    ):
        """Execute   Init   operations natively."""
        super().__init__(
            name="GitAgent",
            capabilities=[AgentCapabilities.CODE_EXECUTION], # Technically executing git commands
            config=config,
        )
        self.repo_manager = repository_manager or RepositoryManager()

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """
        Execute a git-related request.

        The prompt is expected to be a JSON string or a structured command string
        defining the action and parameters.

        Format: "action: param1=value1, param2=value2"
        OR JSON: {"action": "sync", "repository": "owner/repo"}
        """
        try:
            # simple parsing strategy for now
            # In a real agent, an LLM would parse natural language into this structure
            if request.prompt.startswith("{"):
                data = json.loads(request.prompt)
                action = data.get("action")
                params = data
            else:
                # Basic string parsing "action: key=value"
                if ":" not in request.prompt:
                    return AgentResponse(content="Invalid format. Use 'action: key=value' or JSON.", error="InvalidFormat")

                action, param_str = request.prompt.split(":", 1)
                action = action.strip()
                params = {}
                if param_str.strip():
                    for part in param_str.split(","):
                        if "=" in part:
                            k, v = part.split("=", 1)
                            params[k.strip()] = v.strip()

            result = self._handle_action(action, params)
            return AgentResponse(content=str(result))

        except Exception as e:
            logger.exception(f"GitAgent execution error: {e}")
            return AgentResponse(content="", error=str(e))

    def _handle_action(self, action: str, params: dict) -> Any:
        """Dispatch action to specific handlers."""
        repo_name = params.get("repository")

        if action == "sync":
            if not repo_name:
                raise ValueError("Repository name required for sync")
            return self.repo_manager.sync_repository(repo_name)

        elif action == "prune":
             if not repo_name:
                raise ValueError("Repository name required for prune")
             return self.repo_manager.prune_repository(repo_name)

        elif action == "clean":
            if not repo_name:
                raise ValueError("Repository name required for clean")
            repo = self.repo_manager.get_repository(repo_name)
            if not repo:
                 raise ValueError(f"Repository {repo_name} not found")
            local_path = str(self.repo_manager.get_local_path(repo))
            return clean_repository(force=params.get("force") == "true", directories=True, repository_path=local_path)

        elif action == "status":
            if not repo_name:
                raise ValueError("Repository name required for status")
            return self.repo_manager.get_repository_status(repo_name)

        elif action == "list_remotes":
            if not repo_name:
                raise ValueError("Repository name required for list_remotes")
            repo = self.repo_manager.get_repository(repo_name)
            if not repo:
                 raise ValueError(f"Repository {repo_name} not found")
            local_path = str(self.repo_manager.get_local_path(repo))
            return list_remotes(local_path)

        elif action == "add_remote":
            if not repo_name:
                raise ValueError("Repository name required for add_remote")
            name = params.get("name")
            url = params.get("url")
            if not name or not url:
                raise ValueError("Name and URL required for add_remote")

            repo = self.repo_manager.get_repository(repo_name)
            if not repo:
                 raise ValueError(f"Repository {repo_name} not found")
            local_path = str(self.repo_manager.get_local_path(repo))
            return add_remote(name, url, local_path)

        # GitHub Issue Actions
        elif action == "create_issue":
            return create_issue(
                owner=params.get("owner"),
                repo_name=params.get("repo_name"), # Using repo_name to match API arg
                title=params.get("title"),
                body=params.get("body", ""),
                labels=params.get("labels", "").split(",") if params.get("labels") else None
            )

        elif action == "list_issues":
             return list_issues(
                owner=params.get("owner"),
                repo_name=params.get("repo_name"),
                state=params.get("state", "open")
            )

        else:
            raise ValueError(f"Unknown action: {action}")

    def stream(self, request: AgentRequest) -> Iterator[str]:
        """Streaming not supported for this agent currently."""
        yield self.execute(request).content
