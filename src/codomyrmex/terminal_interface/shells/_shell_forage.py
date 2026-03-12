"""Shell Forage Mixin for InteractiveShell."""

import random
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class ShellForageMixin:
    """Provides the forage and search functionality for InteractiveShell."""

    session_data: "dict[str, Any]"
    discovery: "Any"

    def do_forage(self, arg: str):
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
            self._forage_search(arg.strip(), all_caps)
        else:
            self._forage_random(all_caps)

        self.session_data["commands_run"] += 1

    def _forage_search(self, search_term: str, all_caps: list):
        """Search for specific capabilities."""
        search_lower = search_term.lower()
        matches = [
            cap
            for cap in all_caps
            if search_lower in cap.name.lower()
            or search_lower in cap.docstring.lower()
            or search_lower in cap.signature.lower()
        ]

        if not matches:
            print(f"🤷 No capabilities found matching '{search_term}'")
            print(
                "💡 Try a broader search term or use 'forage' for random discoveries"
            )
            return

        print(f"🎯 Found {len(matches)} capabilities matching '{search_term}':\n")

        for cap in matches[:10]:
            module_name = Path(cap.module_path).name
            print(f"🔍 {module_name}.{cap.name} ({cap.type})")
            print(f"   📝 {cap.signature}")
            if cap.docstring != "No docstring":
                doc_preview = cap.docstring.split("\n")[0][:60]
                print(f"   💬 {doc_preview}...")
            print()

        if len(matches) > 10:
            print(f"... and {len(matches) - 10} more matches!")

    def _forage_random(self, all_caps: list):
        """Show random capability discoveries."""
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
