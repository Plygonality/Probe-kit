"""Shared actor interface: Scale, Attach, Hull, Glass.

Every registered group is ``kind=GROUP`` so a later scatter graph can nest it.
The origin is the primary attach (feet / dock / centroid). Uniform Scale and
Attach Location / Attach Rotation plant the actor. Hull and Glass are material
sockets for [Master-Node](https://github.com/Plygonality/Master-Node) category
masters — metal and glass — not ad-hoc shaders.
"""

from __future__ import annotations

from dataclasses import dataclass

from gn_as_code import Graph, GraphKind, SocketType
from gn_as_code.graph import InputValue, SocketRef

ACTOR_KIND = GraphKind.GROUP
BLENDER = "4.2"

SCALE_SOCKET = "Scale"
ATTACH_LOCATION = "Attach Location"
ATTACH_ROTATION = "Attach Rotation"
HULL_SOCKET = "Hull"
GLASS_SOCKET = "Glass"
GEOMETRY_SOCKET = "Geometry"
ATTACH_SOCKET = "Attach"

SHARED_INPUTS = (
    SCALE_SOCKET,
    ATTACH_LOCATION,
    ATTACH_ROTATION,
    HULL_SOCKET,
    GLASS_SOCKET,
)
SHARED_OUTPUTS = (GEOMETRY_SOCKET, ATTACH_SOCKET)


@dataclass(frozen=True)
class ActorSockets:
    """Group-input refs every actor graph wires the same way."""

    scale: SocketRef
    location: SocketRef
    rotation: SocketRef
    hull: SocketRef
    glass: SocketRef


def new_actor_graph(name: str) -> Graph:
    return Graph(name, kind=ACTOR_KIND, blender=BLENDER)


def add_actor_interface(g: Graph) -> ActorSockets:
    """Declare the scatter-ready sockets. Extra per-actor sockets come after."""
    scale = g.input_float(
        SCALE_SOCKET,
        1.0,
        min=0.01,
        max=50.0,
        description="Uniform actor scale around the primary attach origin",
    )
    location = g.input_vector(
        ATTACH_LOCATION,
        (0.0, 0.0, 0.0),
        description="World position of the primary attach (feet, dock, centroid)",
    )
    rotation = g.input(
        ATTACH_ROTATION,
        SocketType.VECTOR,
        (0.0, 0.0, 0.0),
        description="Euler XYZ in radians. Z-up, Y-forward.",
    )
    hull = g.input(
        HULL_SOCKET,
        SocketType.MATERIAL,
        description="Master-Node metal (MN Metal). Bind a category master, not a unique shader.",
    )
    glass = g.input(
        GLASS_SOCKET,
        SocketType.MATERIAL,
        description="Master-Node glass (MN Glass). Canopy / dome / viewport.",
    )
    return ActorSockets(
        scale=scale,
        location=location,
        rotation=rotation,
        hull=hull,
        glass=glass,
    )


def uniform_scale(g: Graph, scale: SocketRef, *, id: str = "scale_vec") -> SocketRef:
    return g.combine_xyz(scale, scale, scale, id=id).vector


def place_actor(
    g: Graph,
    sockets: ActorSockets,
    hull: InputValue,
    glass: InputValue | None = None,
    *,
    extra_attach: dict[str, tuple[float, float, float]] | None = None,
) -> SocketRef:
    """Assign Master-Node materials, plant the actor, emit Geometry + Attach.

    Extra attach sockets are local-space offsets already multiplied by Scale.
    A later scatter graph applies instance rotation on top of those.
    """
    hull_assigned = g.set_material(hull, sockets.hull, id="assign_hull")
    if glass is None:
        body: InputValue = hull_assigned
    else:
        glass_assigned = g.set_material(glass, sockets.glass, id="assign_glass")
        body = g.join_geometry(hull_assigned, glass_assigned, id="body")

    placed = g.transform(
        body,
        translation=sockets.location,
        rotation=sockets.rotation,
        scale=uniform_scale(g, sockets.scale),
        id="place",
    )
    g.output_geometry(placed)
    g.output(sockets.location, name=ATTACH_SOCKET, socket=SocketType.VECTOR)

    for name, local in (extra_attach or {}).items():
        slug = _slug(name)
        offset = g.combine_xyz(local[0], local[1], local[2], id=f"{slug}_local")
        scaled = g.vector_math(
            "SCALE",
            offset.vector,
            scale=sockets.scale,
            id=f"{slug}_scaled",
        )
        g.output(scaled.vector, name=name, socket=SocketType.VECTOR)

    return placed.geometry


def _slug(name: str) -> str:
    return name.lower().replace(" ", "_")
