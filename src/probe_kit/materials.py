"""Master-Node bindings for actor material sockets.

Hull is metal. Glass is glass. The N-panel owns look-dev; these graphs only
expose the sockets. Presets named here are the free framework looks so a new
file is usable without a paid pack.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

HULL_SOCKET = "Hull"
GLASS_SOCKET = "Glass"


@dataclass(frozen=True)
class MaterialBinding:
    """One actor material socket → one Master-Node category master."""

    socket: str
    category: str
    tree: str
    preset: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "socket": self.socket,
            "master_category": self.category,
            "tree": self.tree,
            "preset": self.preset,
            "description": self.description,
        }


HULL = MaterialBinding(
    socket=HULL_SOCKET,
    category="metal",
    tree="MN Metal",
    preset="metal.brushed_aluminum",
    description="Conductor hull, radiator, legs, thrusters.",
)

GLASS = MaterialBinding(
    socket=GLASS_SOCKET,
    category="glass",
    tree="MN Glass",
    preset="glass.clear",
    description="Canopy, sensor dome, viewport.",
)

BINDINGS = (HULL, GLASS)
CATEGORY_BY_SOCKET = {b.socket: b.category for b in BINDINGS}
