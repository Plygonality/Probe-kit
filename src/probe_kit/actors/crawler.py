"""Von Neumann crawler — walks a hull, origin on the foot plane."""

from __future__ import annotations

from gn_as_code import Graph

from probe_kit.actors.primitives import box, cone, cylinder, join, sphere
from probe_kit.sockets import add_actor_interface, new_actor_graph, place_actor

GROUP_NAME = "PK Von Neumann Crawler"
TOOL_ATTACH = (0.0, 0.36, 0.13)
_RX = 1.570796  # 90° around X: cylinder/cone along +Y


def build_crawler() -> Graph:
    g = new_actor_graph(GROUP_NAME)
    sockets = add_actor_interface(g)

    chassis = box(g, (0.40, 0.32, 0.09), (0.0, 0.0, 0.13), id="chassis")
    sensor_house = box(g, (0.12, 0.10, 0.06), (0.0, 0.14, 0.18), id="sensor_house")
    radiator = box(g, (0.28, 0.02, 0.08), (0.0, -0.18, 0.14), id="radiator")
    arm = cylinder(
        g,
        radius=0.018,
        depth=0.16,
        location=(0.0, 0.24, 0.13),
        rotation=(_RX, 0.0, 0.0),
        id="arm",
    )
    gripper = cone(
        g,
        radius_bottom=0.03,
        depth=0.06,
        location=(0.0, 0.34, 0.13),
        rotation=(_RX, 0.0, 0.0),
        id="gripper",
    )
    legs = _legs(g)
    hull = join(
        g,
        chassis,
        sensor_house,
        radiator,
        arm,
        gripper,
        legs,
        id="hull",
    )

    dome = sphere(g, radius=0.055, location=(0.0, 0.14, 0.22), id="dome")

    place_actor(g, sockets, hull, dome, extra_attach={"Tool Attach": TOOL_ATTACH})
    return g


def _legs(g: Graph):
    ring = g.node(
        "GeometryNodeMeshCircle",
        id="leg_ring",
        inputs={"Vertices": 6, "Radius": 0.17},
    )
    lifted = g.transform(ring, translation=(0.0, 0.0, 0.07), id="leg_ring_lift")
    points = g.node(
        "GeometryNodeMeshToPoints",
        id="leg_points",
        inputs={"Mesh": lifted},
    )
    strut = g.mesh_cylinder(vertices=10, radius=0.018, depth=0.12, id="leg_strut")
    pad = g.mesh_cylinder(vertices=10, radius=0.04, depth=0.02, id="foot_pad")
    foot = g.transform(pad, translation=(0.0, 0.0, -0.07), id="foot")
    unit = join(g, strut, foot, id="leg_unit")
    instances = g.instance_on_points(points, unit, id="leg_instances")
    return g.realize_instances(instances, id="legs")
