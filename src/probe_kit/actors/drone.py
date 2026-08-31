"""Service drone — underside dock is the origin."""

from __future__ import annotations

from gn_as_code import Graph

from probe_kit.actors.primitives import box, cone, cylinder, join, sphere
from probe_kit.sockets import add_actor_interface, new_actor_graph, place_actor

GROUP_NAME = "PK Service Drone"
CANOPY_ATTACH = (0.0, 0.06, 0.16)
_RX = 1.570796  # along +Y
_RY = 1.570796  # along +X


def build_drone() -> Graph:
    g = new_actor_graph(GROUP_NAME)
    sockets = add_actor_interface(g)

    fuselage = box(g, (0.28, 0.22, 0.07), (0.0, 0.0, 0.08), id="fuselage")
    nose = cone(
        g,
        radius_bottom=0.06,
        depth=0.10,
        location=(0.0, 0.16, 0.08),
        rotation=(_RX, 0.0, 0.0),
        id="nose",
    )
    dock = cylinder(
        g,
        radius=0.055,
        depth=0.02,
        location=(0.0, 0.0, 0.012),
        vertices=16,
        id="dock",
    )
    port = cylinder(
        g,
        radius=0.032,
        depth=0.10,
        location=(-0.17, 0.0, 0.06),
        rotation=(0.0, _RY, 0.0),
        id="thruster_port",
    )
    starboard = cylinder(
        g,
        radius=0.032,
        depth=0.10,
        location=(0.17, 0.0, 0.06),
        rotation=(0.0, _RY, 0.0),
        id="thruster_starboard",
    )
    antenna = cylinder(
        g,
        radius=0.008,
        depth=0.08,
        location=(0.0, -0.06, 0.16),
        vertices=8,
        id="antenna",
    )
    hull = join(
        g,
        fuselage,
        nose,
        dock,
        port,
        starboard,
        antenna,
        id="hull",
    )

    canopy = sphere(
        g,
        radius=0.07,
        location=(0.0, 0.06, 0.13),
        scale=(0.85, 1.05, 0.55),
        id="canopy",
    )

    place_actor(g, sockets, hull, canopy, extra_attach={"Canopy Attach": CANOPY_ATTACH})
    return g
