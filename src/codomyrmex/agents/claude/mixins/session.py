"""SessionMixin functionality."""


from codomyrmex.agents.core import (
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.session import AgentSession
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class SessionMixin:
    """SessionMixin class."""

    def execute_with_session(
        self,
        request: AgentRequest,
        session: AgentSession | None = None,
        session_id: str | None = None,
    ) -> AgentResponse:
        """Execute request with session context for multi-turn conversations.

        Args:
            request: Agent request
            session: Existing session to use
            session_id: Session ID to retrieve from manager

        Returns:
            Agent response
        """
        # Get or create session
        if session is None and session_id and self.session_manager:
            session = self.session_manager.get_session(session_id)
        if session is None and self.session_manager:
            session = self.session_manager.create_session("claude")

        if session:
            # Add conversation history to context
            history = session.get_context()
            if "messages" not in (request.context or {}):
                if request.context is None:
                    request.context = {}
                request.context["messages"] = history

            # Add user message to session
            session.add_user_message(request.prompt)

        # Execute request
        response = self.execute(request)

        if session and response.is_success():
            # Add assistant response to session
            session.add_assistant_message(
                response.content,
                metadata={
                    "tokens_used": response.tokens_used,
                    "execution_time": response.execution_time,
                },
            )

        return response

    def create_session(self, session_id: str | None = None) -> AgentSession:
        """Create a new conversation session.

        Args:
            session_id: Optional specific session ID

        Returns:
            New AgentSession
        """
        if self.session_manager:
            return self.session_manager.create_session("claude", session_id)
        return AgentSession(agent_name="claude")

