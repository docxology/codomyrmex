"""Chat and infinite conversation handlers."""

import json
import traceback
from pathlib import Path
from typing import Optional, List, Any

from codomyrmex.cli.utils import get_logger, print_success, print_error, print_header

logger = get_logger(__name__)

def handle_chat_session(
    todo_path: Optional[str] = None,
    rounds: int = 0,
    context: Optional[List[str]] = None,
    stream: bool = False,
    resume: Optional[str] = None
) -> bool:
    """Handle continuous multi-turn chat sessions."""
    try:
        from codomyrmex.agents.orchestrator import ConversationOrchestrator
        
        print_header("Starting Conversation Orchestrator...")
        if todo_path:
            print(f"🎯 Targeting scaffolding: {todo_path}")
            
        orch = ConversationOrchestrator.dev_loop(
            todo_path=todo_path if todo_path else "TO-DO.md",
            extra_files=context,
        )
        
        # Handle resume
        if resume:
            resume_path = Path(resume)
            if not resume_path.exists():
                print_error(f"Resume file not found: {resume_path}")
                return False
            print_header(f"Resuming conversation from {resume_path}")
            orch.load_export(resume_path)
        
        print(f"⚡ Executing {'Infinite' if rounds == 0 else rounds} rounds...")
        
        def on_turn_callback(turn: Any) -> None:
            """Execute On Turn Callback operations natively."""
            if stream:
                print(f"\n🤖 [{turn.speaker}] ({turn.elapsed_seconds}s):\n{turn.content}\n" + "-"*40)
        
        transcript = orch.run(rounds=rounds, on_turn=on_turn_callback)
        
        # Export state
        log = orch.get_log()
        export_path = Path("logs") / f"chat_{log.channel_id}.jsonl"
        log.export(export_path)
        print_success(f"Conversation exported to {export_path}")
        
        return True
    except KeyboardInterrupt:
        print("\nConversation stopped by user.")
        return True
    except Exception as e:
        logger.error(f"Chat session failed: {e}")
        traceback.print_exc()
        return False
