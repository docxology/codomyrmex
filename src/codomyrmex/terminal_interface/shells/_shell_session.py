"""Shell Session Mixin for InteractiveShell."""

import os
import shlex
import subprocess
from typing import TYPE_CHECKING

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from typing import Any

logger = get_logger(__name__)


class ShellSessionMixin:
    """Provides session, status, shell, history, clear, stats, export, and quit."""

    session_data: "dict[str, Any]"
    discovery: "Any"

    def do_status(self, arg: str):
        """
        Show system status and health check.

        Usage: status
        """
        print("🏥 " + "=" * 60)
        print("   SYSTEM HEALTH CHECK")
        print("=" * 60)

        if self.discovery:
            self.discovery.show_status_dashboard()
        else:
            print("❌ System discovery not available")

        print("\n🎮 Your Session Stats:")
        print(f"   Commands run: {self.session_data['commands_run']}")
        print(f"   Modules explored: {len(self.session_data['modules_explored'])}")
        print(f"   Demos run: {self.session_data['demos_run']}")

        if self.session_data["modules_explored"]:
            print(
                f"   Explored modules: {', '.join(self.session_data['modules_explored'])}"
            )

        self.session_data["commands_run"] += 1

    def do_export(self, arg: str):
        """
        Export system inventory to file.

        Usage: export

        Creates a JSON report of the entire system.
        """
        print("📋 Exporting complete system inventory...")

        if self.discovery:
            self.discovery.export_full_inventory()
        else:
            print("❌ Discovery system not available")

        self.session_data["commands_run"] += 1

    def do_session(self, arg: str):
        """
        Show session statistics and discoveries.

        Usage: session
        """
        print("🎮 " + "=" * 60)
        print("   YOUR FORAGING SESSION")
        print("=" * 60)

        print("📊 Session Statistics:")
        print(f"   Commands executed: {self.session_data['commands_run']}")
        print(f"   Modules explored: {len(self.session_data['modules_explored'])}")
        print(f"   Demonstrations run: {self.session_data['demos_run']}")

        if self.session_data["modules_explored"]:
            print("\n🏠 Chambers Explored:")
            for module in sorted(self.session_data["modules_explored"]):
                print(f"   • {module}")

        if self.session_data["discoveries_made"]:
            print("\n💎 Discoveries Made:")
            for discovery in self.session_data["discoveries_made"]:
                print(f"   • {discovery}")

        if self.session_data["commands_run"] > 10:
            print("\n🏆 Achievement Unlocked: Expert Forager!")
            print("   You've been busy exploring the nest! 🐜")
        elif self.session_data["modules_explored"]:
            print("\n🏆 Achievement Unlocked: Nest Explorer!")
            print("   You've started mapping the territory! 🗺️")

    def do_quit(self, arg: str):
        """
        Exit the interactive shell.

        Usage: quit
        """
        print("\n🐜 Thank you for foraging in the Codomyrmex nest!")

        if self.session_data["commands_run"] > 0:
            print("📊 Session summary:")
            print(f"   • {self.session_data['commands_run']} commands executed")
            print(f"   • {len(self.session_data['modules_explored'])} modules explored")
            print(f"   • {self.session_data['demos_run']} demos run")

        print("🌟 Keep exploring, and happy coding!")
        print()
        return True

    def do_exit(self, arg: str):
        """
        Exit the interactive shell.

        Usage: exit
        """
        return self.do_quit(arg)

    def do_EOF(self, arg: str):
        """Handle Ctrl+D gracefully."""
        print()
        return self.do_quit(arg)

    def do_shell(self, arg: str):
        """
        Execute shell commands.

        Usage: shell <command>
        """
        if not arg.strip():
            print("❌ Please provide a command to execute.")
            return

        try:
            shell_operators = ("|", ">", "<", "&&", "||", ";", "`", "$")
            if any(op in arg for op in shell_operators):
                # SECURITY: shell=True is intentional here — this is an
                # interactive shell command entered by the local user.
                result = subprocess.run(
                    arg, shell=True, capture_output=True, text=True, timeout=300
                )
            else:
                result = subprocess.run(
                    shlex.split(arg), capture_output=True, text=True, timeout=300
                )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.returncode != 0:
                print(f"Command exited with code: {result.returncode}")
        except subprocess.TimeoutExpired:
            print("❌ Command timed out after 300 seconds.")
        except Exception as e:
            print(f"❌ Error executing command: {e}")

    def do_stats(self, arg: str):
        """
        Show session statistics.

        Usage: stats
        """
        stats = {
            "Commands Run": self.session_data["commands_run"],
            "Modules Explored": len(self.session_data["modules_explored"]),
            "Discoveries Made": len(self.session_data["discoveries_made"]),
            "Demos Run": self.session_data["demos_run"],
        }

        print("📊 Session Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    def do_clear(self, arg: str):
        """
        Clear the terminal screen and reset session data.

        Usage: clear
        """
        try:
            subprocess.run(
                ["clear"] if os.name == "posix" else ["cmd", "/c", "cls"],
                check=False,
                timeout=5,
            )
        except Exception as e:
            print(f"❌ Could not clear screen: {e}")

        self.session_data = {
            "commands_run": 0,
            "modules_explored": set(),
            "discoveries_made": [],
            "demos_run": 0,
        }

    def do_history(self, arg: str):
        """
        Show command history.

        Usage: history
        """
        print("📜 Command History:")
        print("  (History tracking not implemented in this version)")
        print(
            "  Commands executed this session: {}".format(
                self.session_data["commands_run"]
            )
        )
