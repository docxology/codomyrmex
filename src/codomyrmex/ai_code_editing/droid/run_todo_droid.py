"""
🤖 Codomyrmex Droid TODO Processor

Run droid TODO items with configurable execution count and intelligent processing.

This enhanced version provides:
- Interactive prompt for number of TODOs to process
- Sequential processing with progress indication
- Codomyrmex-specific enhanced prompts with project context and rules
- Comprehensive error handling and metrics tracking
- Support for both interactive and command-line usage

Usage:
    # Interactive mode (prompts for count)
    python -m src.codomyrmex.ai_code_editing.droid.run_todo_droid

    # Non-interactive mode (specify count)
    python -m src.codomyrmex.ai_code_editing.droid.run_todo_droid --count 2

    # Programmatic usage
    from codomyrmex.ai_code_editing.droid.run_todo_droid import run_todos
from codomyrmex.exceptions import CodomyrmexError
    processed = list(run_todos(controller, manager, 3))
"""
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


from __future__ import annotations

import argparse
import importlib
import sys
from typing import Callable, Iterable

# Handle both module and direct execution imports
try:
    # When run as module
    from .controller import (
        DroidController,
        DroidConfig,
        create_default_controller,
        load_config_from_file,
    )
    from .todo import TodoItem, TodoManager
except ImportError:
    # When run directly as script
    from controller import (
        DroidController,
        DroidConfig,
        create_default_controller,
        load_config_from_file,
    )
    from todo import TodoItem, TodoManager

# Enhanced prompt with Codomyrmex-specific context and rules
CODOMYRMEX_ENHANCED_PROMPT = (
    "You are operating within the Codomyrmex project - a revolutionary modular coding workspace "
    "that integrates AI capabilities with traditional development tools. Follow these core principles:\n\n"
    "🎯 **Project Context**:\n"
    "- Codomyrmex combines AI-powered code generation, static analysis, data visualization, and build orchestration\n"
    "- 15+ specialized modules work together in a unified, extensible platform\n"
    "- Built for scalability, security, and production readiness\n\n"
    "📋 **Core Principles** (from general.cursorrules):\n"
    "1. Understand Context: Consider broader project goals and module roles\n"
    "2. Modularity & Cohesion: Respect modular architecture, minimize cross-module impact\n"
    "3. Clarity & Readability: Write clear, concise, well-documented code\n"
    "4. Consistency: Follow existing coding styles and architectural patterns\n"
    "5. Functionality First: Ensure robust, purposeful code\n"
    "6. Testability: Code should be inherently testable with comprehensive tests\n"
    "7. Security: Maintain security-conscious mindset\n"
    "8. Efficiency: Balance efficiency with clarity and maintainability\n"
    "9. Documentation: Keep all documentation accurate and up-to-date\n"
    "10. User-Focus: Consider end-users (developers, AI agents, platform users)\n\n"
    "🔧 **Task-Specific Instructions**:\n"
    "- Ensure documentation is updated, logging is present, and all referenced methods exist\n"
    "- Confirm real implementations and comprehensive tests are in place\n"
    "- Follow PEP 8 for Python code and established conventions for other languages\n"
    "- Implement comprehensive error handling with informative messages\n"
    "- Use the logging_monitoring module for appropriate logging\n"
    "- Update relevant CHANGELOG.md files for significant modifications\n"
    "- Maintain security best practices throughout\n"
    "- Consider the impact of changes on other modules\n"
    "- Prioritize clarity and maintainability over premature optimization\n\n"
    "✅ **Completion Criteria**:\n"
    "- All functionality works as intended\n"
    "- Code follows project conventions and best practices\n"
    "- Documentation is accurate and complete\n"
    "- Tests pass and provide adequate coverage\n"
    "- Changes respect modular architecture\n"
    "- Security considerations are addressed\n"
    "- Performance impact is considered\n"
    "- User experience is maintained or improved"
)


def resolve_handler(handler_path: str) -> Callable:
    if ":" not in handler_path:
        raise ValueError(
            f"Handler path must include module and attribute: {handler_path}"
        )
    module_name, attribute = handler_path.split(":", 1)

    try:
        if module_name.startswith("."):
            # Handle relative imports
            current_package = "codomyrmex.ai_code_editing.droid"
            if module_name.startswith(".."):
                # Go up one level
                current_package = "codomyrmex.ai_code_editing"
            module = importlib.import_module(module_name, current_package)
        else:
            # Handle absolute imports
            module = importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Failed to import handler module '{module_name}': {e}")

    handler = getattr(module, attribute, None)
    if handler is None or not callable(handler):
        raise AttributeError(f"Handler {handler_path} is not callable")
    return handler


def get_todo_count_interactive() -> int:
    """Interactively prompt user for number of TODOs to process."""
    import os

    todo_file = os.path.join(os.path.dirname(__file__), "todo_list.txt")
    todo_items, _ = TodoManager(todo_file).load()
    available_count = len(todo_items)

    if available_count == 0:
        print("🤖 No TODO items available to process.")
        return 0

    print(f"\n📋 Found {available_count} TODO item(s) available:")
    for i, item in enumerate(todo_items, 1):
        print(f"  {i}. {item.operation_id}: {item.description}")

    while True:
        try:
            choice = (
                input(
                    f"\n🔢 How many TODOs would you like to process? (1-{available_count}, or 'all'): "
                )
                .strip()
                .lower()
            )

            if choice == "all":
                return available_count

            count = int(choice)
            if 1 <= count <= available_count:
                return count
            else:
                print(f"❌ Please enter a number between 1 and {available_count}")

        except ValueError:
            print("❌ Please enter a valid number or 'all'")
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user.")
            sys.exit(0)


def run_todos(
    controller: DroidController, manager: TodoManager, count: int
) -> Iterable[TodoItem]:
    """Process TODO items sequentially with enhanced Codomyrmex-specific prompts and real-time statistics."""
    todo_items, completed_items = manager.load()
    if not todo_items:
        return []

    to_process = todo_items[:count]
    remaining = todo_items[count:]
    processed: list[TodoItem] = []

    # Enhanced startup display
    print(
        f"\n🚀 Processing {len(to_process)} TODO item(s) with Codomyrmex intelligence..."
    )
    print("=" * 70)

    # Initialize timing and statistics
    start_time = time.time()
    task_times: list[float] = []
    task_status: list[str] = []

    # Progress bar setup
    bar_width = 50

    for i, item in enumerate(to_process, 1):
        task_start_time = time.time()

        # Enhanced task header
        print(f"\n⚙️  Task {i}/{len(to_process)}: {item.operation_id}")
        print(f"   📝 {item.description}")
        print(f"   🎯 Handler: {item.handler_path}")

        # Progress indicator
        progress = (i - 1) / len(to_process)
        filled = int(bar_width * progress)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"   📊 Progress: [{bar}] {progress*100:.1f}%")

        try:
            handler = resolve_handler(item.handler_path)

            # Execute with enhanced monitoring
            result = controller.execute_task(
                item.operation_id,
                handler,
                prompt=CODOMYRMEX_ENHANCED_PROMPT,
                description=item.description,
            )

            # Calculate task timing
            task_duration = time.time() - task_start_time
            task_times.append(task_duration)
            task_status.append("✅")

            # Success display with timing
            avg_time = sum(task_times) / len(task_times)
            remaining_tasks = len(to_process) - i
            eta = avg_time * remaining_tasks if remaining_tasks > 0 else 0

            print(f"   ✅ Completed in {task_duration:.3f}s ({item.operation_id})")
            print(
                f"   📈 Stats: Avg: {avg_time:.3f}s | ETA: {eta:.1f}s ({remaining_tasks} tasks)"
            )

            processed.append(item)

        except Exception as e:
            task_duration = time.time() - task_start_time
            task_times.append(task_duration)
            task_status.append("❌")

            print(
                f"   ❌ Failed in {task_duration:.3f}s ({item.operation_id}): {str(e)}"
            )
            print(f"   💡 Error: {type(e).__name__}")

        # Real-time statistics display
        if i < len(to_process):  # Don't show final stats yet
            current_time = time.time() - start_time
            success_count = len([s for s in task_status if s == "✅"])
            success_rate = (
                (success_count / len(task_status)) * 100 if task_status else 0
            )

            print("\n📊 Session Progress:")
            print(f"   ⏱️  Elapsed: {current_time:.1f}s")
            print(f"   📋 Completed: {len(processed)}/{i}")
            print(f"   📊 Success Rate: {success_rate:.1f}%")

    # Final summary with comprehensive statistics
    total_time = time.time() - start_time

    if processed:
        success_count = len([s for s in task_status if s == "✅"])
        failure_count = len([s for s in task_status if s == "❌"])

        print("\n🎉 Execution Summary:")
        print("=" * 70)
        print(
            f"   ✅ Successfully processed: {success_count}/{len(to_process)} TODO(s)"
        )
        print(f"   ❌ Failed: {failure_count}/{len(to_process)} TODO(s)")
        print(f"   ⏱️  Total execution time: {total_time:.2f}s")
        print(f"   📊 Tasks per minute: {len(processed) / (total_time / 60):.1f}")

        if task_times:
            avg_task_time = sum(task_times) / len(task_times)
            min_task_time = min(task_times)
            max_task_time = max(task_times)

            print("\n📈 Task Performance:")
            print(f"   ⏱️  Average task time: {avg_task_time:.3f}s")
            print(f"   ⚡ Fastest task: {min_task_time:.3f}s")
            print(f"   🐌 Slowest task: {max_task_time:.3f}s")

        # Update TODO list
        manager.rotate(processed, remaining, completed_items)

        # Final controller metrics
        metrics = controller.metrics
        print("\n🎮 Controller Metrics:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")

    else:
        print("\n❌ No TODOs were successfully processed.")
        print(f"   ⏱️  Total execution time: {total_time:.2f}s")

    return processed


def build_controller(config_path: str | None) -> DroidController:
    if config_path:
        config = load_config_from_file(config_path)
        controller = DroidController(config)
        controller.start()
        return controller
    return create_default_controller()


def main() -> None:
    """Main entry point with interactive prompt and enhanced processing."""
    parser = argparse.ArgumentParser(
        description="🤖 Codomyrmex Droid TODO Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_todo_droid.py                    # Interactive mode
  python run_todo_droid.py --count 3         # Process 3 TODOs
  python run_todo_droid.py --count -1        # Process all TODOs
  python run_todo_droid.py --non-interactive # Process 1 TODO non-interactively
  python run_todo_droid.py --list            # List all TODOs without processing
        """,
    )

    parser.add_argument(
        "--todo-file",
        default="todo_list.txt",
        help="Path to todo list file (default: todo_list.txt)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of items to process (use -1 for all, skip interactive prompt)",
    )
    parser.add_argument("--config", default=None, help="Optional path to config file")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode (process 1 TODO)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List all TODOs without processing"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without actually doing it",
    )

    args = parser.parse_args()

    # Set the working directory to the droid folder for relative paths
    import os
    import sys

    droid_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(droid_dir)))
    )
    os.chdir(droid_dir)

    # Add project root to Python path for module imports
    if project_root not in sys.path:
        pass
#         sys.path.insert(0, project_root)  # Removed sys.path manipulation

    print("🤖 Codomyrmex Droid TODO Processor")
    print("=====================================")

    # Load TODOs first to check what's available
    manager = TodoManager(args.todo_file)
    todo_items, completed_items = manager.load()

    # Handle --list option
    if args.list:
        print("📋 TODO List:")
        print("============")
        if not todo_items:
            print("No TODO items found.")
        else:
            for i, item in enumerate(todo_items, 1):
                print(f"{i}. [{item.operation_id}] {item.description}")
                print(f"   Handler: {item.handler_path}")

        if completed_items:
            print(f"\n✅ Completed ({len(completed_items)} items):")
            for item in completed_items:
                print(f"   [{item.operation_id}] {item.description}")

        return

    # Determine the count to process
    if args.count is not None:
        if args.count == -1:
            count = len(todo_items)  # Process all
        elif args.count < -1:
            print(
                f"❌ Invalid count: {args.count}. Use positive numbers or -1 for all."
            )
            return
        else:
            count = args.count
    elif args.non_interactive or args.dry_run:
        count = 1  # Default to 1 in non-interactive or dry-run mode
    else:
        count = get_todo_count_interactive()

    if count == 0 or not todo_items:
        print("👋 No TODOs to process. Exiting.")
        return

    # Handle --dry-run option
    if args.dry_run:
        print(f"🔍 Dry run: Would process {count} TODO(s)")
        print("Items to process:")
        for i, item in enumerate(todo_items[:count], 1):
            print(f"  {i}. [{item.operation_id}] {item.description}")
        return

    controller = build_controller(args.config)

    try:
        processed = list(run_todos(controller, manager, count))

        if not processed:
            print("❌ No TODO items were processed.")
        else:
            print("\n📊 Summary:")
            print(f"   ✅ Successfully processed: {len(processed)} TODO(s)")
            print(f"   📈 Controller metrics: {controller.metrics}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during TODO processing: {e}")
    finally:
        # Always show final metrics
        try:
            if controller:
                print(f"\n📊 Final Controller Metrics: {controller.metrics}")
        except:
            pass
        print("👋 Droid session completed.")


# Example of programmatic usage
def demo_programmatic_usage():
    """Demonstrate how to use the droid system programmatically."""
    # Use the already imported modules to avoid import issues
    import os

    print("🤖 Demo: Programmatic Droid Usage")
    print("=" * 40)

    # Setup
    controller = create_default_controller()
    todo_file = os.path.join(os.path.dirname(__file__), "todo_list.txt")
    manager = TodoManager(todo_file)

    # Process 1 TODO
    print("Processing 1 TODO programmatically...")
    processed = list(run_todos(controller, manager, 1))

    print(f"✅ Processed {len(processed)} TODO(s)")
    for item in processed:
        print(f"   - {item.operation_id}: {item.description}")

    return processed


if __name__ == "__main__":  # pragma: no cover
    main()
