"""HandsManager — parse and manage openfang autonomous Hands."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Hand:
    """Represents a single openfang autonomous Hand capability."""

    name: str
    description: str = ""
    schedule: str = ""
    enabled: bool = True
    tags: list[str] = field(default_factory=list)


class HandsManager:
    """Parse openfang `hands list` output into structured Hand objects."""

    @staticmethod
    def parse_list_output(raw_output: str) -> list[Hand]:
        """Parse the text output of `openfang hands list` into Hand objects.

        openfang's output format may change across versions; this parser
        uses a best-effort line-by-line approach and returns whatever it can.
        """
        hands: list[Hand] = []
        current: dict[str, str] = {}
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                if current.get("name"):
                    hands.append(
                        Hand(
                            name=current["name"],
                            description=current.get("description", ""),
                            schedule=current.get("schedule", ""),
                            enabled=current.get("enabled", "true").lower() == "true",
                            tags=[
                                t.strip()
                                for t in current.get("tags", "").split(",")
                                if t.strip()
                            ],
                        )
                    )
                current = {}
            elif ":" in line:
                key, _, value = line.partition(":")
                current[key.strip().lower()] = value.strip()
            elif not current.get("name"):
                current["name"] = line
        # Flush last entry
        if current.get("name"):
            hands.append(
                Hand(
                    name=current["name"],
                    description=current.get("description", ""),
                    schedule=current.get("schedule", ""),
                    enabled=current.get("enabled", "true").lower() == "true",
                    tags=[
                        t.strip()
                        for t in current.get("tags", "").split(",")
                        if t.strip()
                    ],
                )
            )
        return hands
