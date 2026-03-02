#!/usr/bin/env python3
"""Interactive Shell for Codomyrmex

Provides an engaging, interactive terminal interface for exploring the
Codomyrmex ecosystem - like being an epistemic forager in a vast,
structured nest.
"""

import cmd
import logging
import os
import random
import shlex
import subprocess
from pathlib import Path

# NOTE: Core-layer imports (coding, data_visualization) are loaded lazily
# inside the methods that need them to respect the Foundation → Core layer
# boundary.  Only Foundation-layer imports appear at the top level.
# system_discovery (Application layer) is NOT imported — _ensure_discovery()
# uses pkgutil instead.
from codomyrmex.logging_monitoring import get_logger

try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

class InteractiveShell(cmd.Cmd):
    """
    Interactive shell for exploring the Codomyrmex ecosystem.

    This shell provides a fun, accessible way to discover modules,
    run demos, check status, and interact with the system like
    an epistemic forager exploring a vast nest.
    """

    intro = """
🐜 Welcome to the Codomyrmex Interactive Shell! 🐜

You are now an epistemic forager in the vast Codomyrmex nest.
Explore modules, discover capabilities, and forage for knowledge!

Type 'help' or '?' to list commands.
Type 'help <command>' for detailed information about a command.
Type 'explore' to begin your foraging adventure!
    """

    prompt = "🐜 codomyrmex> "

    def __init__(self):
        """Initialize the interactive shell."""
        super().__init__()

        # SystemDiscovery (Application layer) is NOT imported here — this module
        # is Foundation layer.  _ensure_discovery() uses pkgutil for module names.
        self.discovery = None
        self._module_names: list[str] = []

        # Track session data
        self.session_data = {
            "commands_run": 0,
            "modules_explored": set(),
            "discoveries_made": [],
            "demos_run": 0,
        }

        # Fun foraging messages
        self.foraging_messages = [
            "🔍 Sniffing around for interesting modules...",
            "🐜 Following the scent trail of code...",
            "🍯 Found some sweet capabilities!",
            "🏃 Scurrying through the codebase...",
            "🌿 Exploring new territories in the nest...",
            "🔬 Examining specimens under the microscope...",
            "🎯 Zeroing in on valuable resources...",
            "🚀 Launching discovery expedition...",
        ]

        print(self.intro)

    def _ensure_discovery(self) -> None:
        """Build the module name list using pkgutil (Foundation-layer safe).

        Populates ``self._module_names`` without importing any Core/Application
        layer modules, preserving the Foundation → Core layer boundary.
        ``self.discovery`` remains ``None``; commands that need rich discovery
        data report limited-mode status as designed.
        """
        if not self._module_names:
            try:
                import pkgutil

                import codomyrmex
                self._module_names = [
                    name
                    for _, name, _ in pkgutil.iter_modules(codomyrmex.__path__)
                ]
            except Exception as exc:
                logger.warning("pkgutil module scan failed: %s", exc)
                self._module_names = []

    def precmd(self, line: str) -> str:
        """Ensure discovery engine is initialised before any command runs."""
        self._ensure_discovery()
        return line

    def emptyline(self):
        """Handle empty lines gracefully without repeating the last command."""
        return False

    def default(self, line):
        """Handle unknown commands with helpful suggestions."""
        print(f"🤔 Unknown command: '{line}'")
        print(
            "💡 Try 'help' to see available commands, or 'explore' to start foraging!"
        )

    def do_explore(self, arg):
        """
        Begin exploring the Codomyrmex ecosystem.

        Usage: explore [module_name]

        Without arguments, shows overview of all modules.
        With module name, explores that specific module in detail.
        """
        print(random.choice(self.foraging_messages))
        print()

        self.session_data["commands_run"] += 1

        if not self.discovery:
            print("❌ System discovery not available - running in limited mode")
            return

        if arg:
            # Explore specific module
            self._explore_module(arg.strip())
        else:
            # General exploration
            self._explore_overview()

    def _explore_overview(self):
        """Show overview of all available modules."""
        print("🗺️  " + "=" * 60)
        print("   CODOMYRMEX ECOSYSTEM MAP")
        print("=" * 60)

        if not self.discovery.modules:
            print("📡 Scanning nest for modules...")
            self.discovery._discover_modules()

        if not self.discovery.modules:
            print("😕 No modules discovered. The nest seems empty...")
            return

        print(f"🏠 Discovered {len(self.discovery.modules)} chambers in the nest:\n")

        for i, (name, info) in enumerate(self.discovery.modules.items(), 1):
            status = "✅" if info.is_importable else "🔧"
            capability_count = len(info.capabilities)

            print(f"{i:2d}. {status} {name}")
            print(f"    📝 {info.description[:60]}...")
            print(f"    🔧 {capability_count} capabilities")

            if info.has_tests:
                print("    🧪 Has tests")
            if info.has_docs:
                print("    📚 Has documentation")
            print()

        print("💡 Use 'explore <module_name>' to investigate a specific chamber!")
        print("💡 Use 'capabilities' to see all available tools!")
        print("💡 Use 'demo' to run live demonstrations!")

    def _explore_module(self, module_name):
        """Explore a specific module in detail."""
        if module_name not in self.discovery.modules:
            print(f"🔍 Module '{module_name}' not found in the nest.")
            print("🗺️  Use 'explore' to see available modules.")
            return

        info = self.discovery.modules[module_name]
        self.session_data["modules_explored"].add(module_name)

        print("🏠 " + "=" * 60)
        print(f"   EXPLORING: {module_name.upper()}")
        print("=" * 60)

        print(f"📍 Location: {info.path}")
        print(f"📝 Description: {info.description}")
        print(f"🏷️  Version: {info.version}")
        print(f"📅 Last Modified: {info.last_modified}")
        print(
            f"🔗 Dependencies: {', '.join(info.dependencies) if info.dependencies else 'None'}"
        )

        # Status indicators
        status_line = "🔧 Status: "
        if info.is_importable:
            status_line += "✅ Importable "
        else:
            status_line += "❌ Import Issues "

        if info.has_tests:
            status_line += "🧪 Tested "
        if info.has_docs:
            status_line += "📚 Documented "

        print(status_line)

        # Capabilities
        if info.capabilities:
            print(f"\n🛠️  Capabilities ({len(info.capabilities)} total):")

            # Group by type
            by_type = {}
            for cap in info.capabilities:
                if cap.type not in by_type:
                    by_type[cap.type] = []
                by_type[cap.type].append(cap)

            for cap_type, caps in by_type.items():
                print(f"\n   📂 {cap_type.title()}s ({len(caps)}):")
                for cap in caps[:5]:  # Show first 5
                    print(f"      • {cap.name}")
                    if cap.docstring and cap.docstring != "No docstring":
                        doc_preview = cap.docstring.split("\n")[0][:50]
                        print(f"        💬 {doc_preview}...")

                if len(caps) > 5:
                    print(f"      ... and {len(caps) - 5} more")
        else:
            print("\n🤷 No capabilities discovered (module may need import fixes)")

        print(f"\n💡 Try 'demo {module_name}' to see this module in action!")
        print(f"💡 Try 'dive {module_name}' for detailed capability inspection!")

    def do_capabilities(self, arg):
        """
        Show all discovered capabilities across modules.

        Usage: capabilities [type]

        Without arguments, shows summary by type.
        With type (function, class, method), shows detailed list.
        """
        print("🛠️  " + "=" * 60)
        print("   CAPABILITY INVENTORY")
        print("=" * 60)

        if not self.discovery or not self.discovery.modules:
            print("📡 First scanning for modules...")
            self.discovery._discover_modules()

        all_caps = []
        for info in self.discovery.modules.values():
            all_caps.extend(info.capabilities)

        if not all_caps:
            print("😕 No capabilities discovered yet. Run 'explore' first!")
            return

        if arg:
            # Show specific type
            cap_type = arg.strip().lower()
            filtered_caps = [cap for cap in all_caps if cap.type.lower() == cap_type]

            if not filtered_caps:
                print(f"🔍 No capabilities of type '{cap_type}' found.")
                return

            print(f"🔧 {cap_type.title()} Capabilities ({len(filtered_caps)} total):\n")

            for cap in filtered_caps:
                module_name = Path(cap.module_path).name
                print(f"   📦 {module_name}.{cap.name}")
                print(f"      📝 {cap.signature}")
                if cap.docstring and cap.docstring != "No docstring":
                    doc_preview = cap.docstring.split("\n")[0][:60]
                    print(f"      💬 {doc_preview}...")
                print()

        else:
            # Show summary by type
            by_type = {}
            for cap in all_caps:
                if cap.type not in by_type:
                    by_type[cap.type] = []
                by_type[cap.type].append(cap)

            print("📊 Capability Summary:\n")
            for cap_type, caps in sorted(by_type.items()):
                print(f"   {cap_type:<12}: {len(caps):3d} items")

            print(f"\n🎯 Total Capabilities: {len(all_caps)}")
            print("\n💡 Use 'capabilities <type>' to see details for a specific type")
            print("💡 Example: 'capabilities function' or 'capabilities class'")

        self.session_data["commands_run"] += 1

    def do_demo(self, arg):
        """
        Run demonstration workflows.

        Usage: demo [module_name]

        Without arguments, runs demos for all working modules.
        With module name, runs demo for specific module if available.
        """
        print("🚀 " + "=" * 60)
        print("   DEMONSTRATION MODE")
        print("=" * 60)

        print(
            random.choice(
                [
                    "🎭 Setting up the stage for our performance...",
                    "🎪 Ladies and gentlemen, the show is about to begin!",
                    "🧪 Preparing laboratory demonstrations...",
                    "🎬 Lights, camera, action!",
                ]
            )
        )
        print()

        self.session_data["commands_run"] += 1

        if not self.discovery:
            print("❌ Discovery system not available")
            return

        if arg:
            self._demo_specific_module(arg.strip())
        else:
            self._demo_all_modules()

        self.session_data["demos_run"] += 1

    def _demo_specific_module(self, module_name):
        """Run demo for a specific module."""
        if module_name not in self.discovery.modules:
            print(f"🔍 Module '{module_name}' not found.")
            return

        info = self.discovery.modules[module_name]
        if not info.is_importable:
            print(f"❌ Module '{module_name}' has import issues - cannot demo")
            return

        print(f"🎯 Running demo for {module_name}...")

        try:
            if module_name == "data_visualization":
                self._demo_data_visualization()
            elif module_name == "logging_monitoring":
                self._demo_logging()
            elif module_name == "code":
                self._demo_code_execution()
            else:
                print(f"🤷 No specific demo available for {module_name}")
                print("💡 Try the general demo instead: 'demo'")

        except Exception as e:
            print(f"❌ Demo failed: {e}")

    def _demo_all_modules(self):
        """Run demos for all working modules."""
        if not self.discovery:
            return

        self.discovery.run_demo_workflows()

    def _demo_data_visualization(self):
        """Demo the data visualization module."""
        try:
            # Lazy-load Core-layer dependencies inside the method
            import numpy as np

            from codomyrmex.data_visualization import create_bar_chart, create_line_plot

            print("   📊 Creating sample line plot...")
            x = np.linspace(0, 6.28, 100)
            y = np.sin(x) * np.exp(-x / 10)

            create_line_plot(
                x_data=x,
                y_data=y,
                title="Interactive Demo: Damped Sine Wave",
                x_label="Time",
                y_label="Amplitude",
                output_path="interactive_demo_line.png",
                show_plot=False,
            )

            print("   📊 Creating sample bar chart...")
            categories = ["Foraging", "Building", "Exploring", "Coding", "Testing"]
            values = np.random.randint(10, 100, size=len(categories))

            create_bar_chart(
                categories=categories,
                values=values,
                title="Interactive Demo: Ant Activity Levels",
                x_label="Activity",
                y_label="Level",
                output_path="interactive_demo_bar.png",
                show_plot=False,
            )

            print(
                "   ✅ Plots saved: interactive_demo_line.png, interactive_demo_bar.png"
            )

        except Exception as e:
            print(f"   ❌ Data visualization demo failed: {e}")

    def _demo_logging(self):
        """Demo the logging system."""
        try:

            demo_logger = get_logger("interactive_demo")

            demo_logger.info("🐜 Starting interactive logging demo...")
            demo_logger.debug("🔍 This is a debug message")
            demo_logger.warning("⚠️  This is a warning message")
            demo_logger.error(
                "❌ This is an error message (don't worry, it's just a demo!)"
            )
            demo_logger.info("✅ Interactive logging demo completed successfully!")

        except Exception as e:
            print(f"   ❌ Logging demo failed: {e}")

    def _demo_code_execution(self):
        """Demo the code execution sandbox."""
        try:
            # Lazy-load Core-layer dependency inside the method
            from codomyrmex.coding import execute_code

            print("   🏃 Executing sample Python code in sandbox...")

            code = """
print("Hello from the Codomyrmex sandbox! 🐜")
print(f"The answer to everything: {6 * 7}")
print(f"Pi to 3 decimal places: {math.pi:.3f}")
for i in range(5):
    print(f"Foraging step {i+1}... 🔍")
print("Sandbox execution complete! ✅")
"""

            result = execute_code(language="python", code=code)

            if result.get("exit_code") == 0:
                print("   📤 Sandbox output:")
                for line in result.get("stdout", "").split("\n"):
                    if line.strip():
                        print(f"      {line}")
            else:
                print(
                    f"   ❌ Execution failed with exit code: {result.get('exit_code')}"
                )

        except Exception as e:
            print(f"   ❌ Code execution demo failed: {e}")

    def do_status(self, arg):
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

        # Session stats
        print("\n🎮 Your Session Stats:")
        print(f"   Commands run: {self.session_data['commands_run']}")
        print(f"   Modules explored: {len(self.session_data['modules_explored'])}")
        print(f"   Demos run: {self.session_data['demos_run']}")

        if self.session_data["modules_explored"]:
            print(
                f"   Explored modules: {', '.join(self.session_data['modules_explored'])}"
            )

        self.session_data["commands_run"] += 1

    def do_dive(self, arg):
        """
        Deep dive into a specific module's capabilities.

        Usage: dive <module_name>

        Shows detailed information about all capabilities in the module.
        """
        if not arg:
            print("🤿 Usage: dive <module_name>")
            print("💡 Use 'explore' to see available modules")
            return

        module_name = arg.strip()

        if not self.discovery or module_name not in self.discovery.modules:
            print(f"🔍 Module '{module_name}' not found.")
            return

        info = self.discovery.modules[module_name]

        print("🤿 " + "=" * 60)
        print(f"   DEEP DIVE: {module_name.upper()}")
        print("=" * 60)

        if not info.capabilities:
            print("🤷 No capabilities discovered for deep diving.")
            return

        print(f"🔬 Examining {len(info.capabilities)} capabilities in detail:\n")

        for i, cap in enumerate(info.capabilities, 1):
            print(f"{i:3d}. 🔧 {cap.type.upper()}: {cap.name}")
            print(f"      📍 Location: {Path(cap.file_path).name}:{cap.line_number}")
            print(f"      📝 Signature: {cap.signature}")

            if cap.docstring and cap.docstring != "No docstring":
                # Show first few lines of docstring
                doc_lines = cap.docstring.split("\n")[:3]
                for line in doc_lines:
                    if line.strip():
                        print(f"      💬 {line.strip()}")

            if cap.dependencies:
                print(f"      🔗 Dependencies: {', '.join(cap.dependencies)}")

            print()  # Space between capabilities

        self.session_data["modules_explored"].add(module_name)
        self.session_data["commands_run"] += 1

    def do_forage(self, arg):
        """
        Go foraging for interesting discoveries in the nest.

        Usage: forage [search_term]

        Without arguments, finds random interesting capabilities.
        With search term, looks for capabilities matching the term.
        """
        print(
            "🔍 "
            + random.choice(
                [
                    "Time to forage for knowledge! 🐜",
                    "Let's see what treasures we can find... 💎",
                    "Searching for interesting specimens... 🔬",
                    "Following scent trails to new discoveries... 👃",
                ]
            )
        )
        print()

        if not self.discovery or not self.discovery.modules:
            print("📡 First scanning for modules...")
            self.discovery._discover_modules()

        all_caps = []
        for info in self.discovery.modules.values():
            all_caps.extend(info.capabilities)

        if not all_caps:
            print("😕 The foraging grounds seem empty. No capabilities discovered.")
            return

        if arg:
            # Search for specific term
            search_term = arg.strip().lower()
            matches = []

            for cap in all_caps:
                if (
                    search_term in cap.name.lower()
                    or search_term in cap.docstring.lower()
                    or search_term in cap.signature.lower()
                ):
                    matches.append(cap)

            if not matches:
                print(f"🤷 No capabilities found matching '{search_term}'")
                print(
                    "💡 Try a broader search term or use 'forage' for random discoveries"
                )
                return

            print(f"🎯 Found {len(matches)} capabilities matching '{search_term}':\n")

            for cap in matches[:10]:  # Limit to first 10
                module_name = Path(cap.module_path).name
                print(f"🔍 {module_name}.{cap.name} ({cap.type})")
                print(f"   📝 {cap.signature}")
                if cap.docstring != "No docstring":
                    doc_preview = cap.docstring.split("\n")[0][:60]
                    print(f"   💬 {doc_preview}...")
                print()

            if len(matches) > 10:
                print(f"... and {len(matches) - 10} more matches!")

        else:
            # Random discoveries
            random_caps = random.sample(all_caps, min(5, len(all_caps)))

            print("🎲 Random Discoveries from the Nest:\n")

            for cap in random_caps:
                module_name = Path(cap.module_path).name
                print(f"💎 {module_name}.{cap.name} ({cap.type})")
                print(f"   📝 {cap.signature}")
                if cap.docstring != "No docstring":
                    doc_preview = cap.docstring.split("\n")[0][:60]
                    print(f"   💬 {doc_preview}...")
                print()

        self.session_data["commands_run"] += 1

    def do_export(self, arg):
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

    def do_session(self, arg):
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

        # Fun foraging achievement
        if self.session_data["commands_run"] > 10:
            print("\n🏆 Achievement Unlocked: Expert Forager!")
            print("   You've been busy exploring the nest! 🐜")
        elif self.session_data["modules_explored"]:
            print("\n🏆 Achievement Unlocked: Nest Explorer!")
            print("   You've started mapping the territory! 🗺️")

    def do_quit(self, arg):
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

    def do_exit(self, arg):
        """
        Exit the interactive shell.

        Usage: exit
        """
        return self.do_quit(arg)

    def do_EOF(self, arg):
        """Handle Ctrl+D gracefully."""
        print()  # New line after ^D
        return self.do_quit(arg)

    def do_shell(self, arg):
        """
        Execute shell commands.

        Usage: shell <command>
        """
        if not arg.strip():
            print("❌ Please provide a command to execute.")
            return

        try:
            # Use list form for safer execution; fall back to shell=True
            # only for commands containing shell operators (pipes, redirects)
            shell_operators = ('|', '>', '<', '&&', '||', ';', '`', '$')
            if any(op in arg for op in shell_operators):
                # SECURITY: shell=True is intentional here — this is an
                # interactive shell command entered by the local user.
                result = subprocess.run(arg, shell=True, capture_output=True, text=True, timeout=300)
            else:
                result = subprocess.run(shlex.split(arg), capture_output=True, text=True, timeout=300)
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

    def do_stats(self, arg):
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

    def do_clear(self, arg):
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

        # Reset session data
        self.session_data = {
            'commands_run': 0,
            'modules_explored': set(),
            'discoveries_made': set(),
            'demos_run': set()
        }
        self.command_history = []

    def do_history(self, arg):
        """
        Show command history.

        Usage: history
        """
        # Note: cmd module doesn't store history by default
        # This is a simplified implementation
        print("📜 Command History:")
        print("  (History tracking not implemented in this version)")
        print(
            "  Commands executed this session: {}".format(
                self.session_data["commands_run"]
            )
        )

    def complete_explore(self, text, line, begidx, endidx):
        """
        Tab completion for explore command.
        """
        if not self.discovery:
            return []

        # Get available modules for completion
        try:
            modules = self.discovery.discover_modules()
            module_names = [
                module.get("name", "") for module in modules if "name" in module
            ]
            if text:
                return [name for name in module_names if name.startswith(text)]
            else:
                return module_names
        except Exception as e:
            logger.error(f"Error in tab completion: {e}")
            return []

    def run(self):
        """Run the interactive shell."""
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print("\n\n🐜 Interrupted! Thanks for exploring the Codomyrmex nest!")
        except Exception as e:
            logger.error(f"Error in interactive shell: {e}")
            print(f"\n❌ An error occurred: {e}")
            print("🐜 Thanks for exploring the Codomyrmex nest!")

if __name__ == "__main__":
    # Allow running this module directly for testing
    shell = InteractiveShell()
    shell.run()
