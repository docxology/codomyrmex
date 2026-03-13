"""Shell Explore Mixin for InteractiveShell."""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class ShellExploreMixin:
    """Provides the explore functionality for InteractiveShell."""

    session_data: "dict[str, Any]"
    discovery: "Any"

    def do_explore(self, arg: str):
        """
        Begin exploring the Codomyrmex ecosystem.

        Usage: explore [module_name]

        Without arguments, shows overview of all modules.
        With module name, explores that specific module in detail.
        """
        # Note: foraging_messages is defined in InteractiveShell.__init__
        if hasattr(self, "foraging_messages"):
            print(random.choice(self.foraging_messages))
        print()

        self.session_data["commands_run"] += 1

        if not self.discovery:
            print("❌ System discovery not available - running in limited mode")
            return

        if arg:
            self._explore_module(arg.strip())
        else:
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

    def _explore_module(self, module_name: str):
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

        if info.capabilities:
            print(f"\n🛠️  Capabilities ({len(info.capabilities)} total):")

            by_type = {}
            for cap in info.capabilities:
                if cap.type not in by_type:
                    by_type[cap.type] = []
                by_type[cap.type].append(cap)

            for cap_type, caps in by_type.items():
                print(f"\n   📂 {cap_type.title()}s ({len(caps)}):")
                for cap in caps[:5]:
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
