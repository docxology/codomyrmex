"""Shell Capabilities Mixin for InteractiveShell."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class ShellCapabilitiesMixin:
    """Provides the capabilities and dive functionality for InteractiveShell."""

    session_data: "dict[str, Any]"
    discovery: "Any"

    def do_capabilities(self, arg: str):
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

    def do_dive(self, arg: str):
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
                doc_lines = cap.docstring.split("\n")[:3]
                for line in doc_lines:
                    if line.strip():
                        print(f"      💬 {line.strip()}")

            if cap.dependencies:
                print(f"      🔗 Dependencies: {', '.join(cap.dependencies)}")

            print()

        self.session_data["modules_explored"].add(module_name)
        self.session_data["commands_run"] += 1
