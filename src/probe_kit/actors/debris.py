"""Debris chunk — fractured hull fragment, origin at the centroid."""

from __future__ import annotations

from gn_as_code import Graph

from probe_kit.sockets import add_actor_interface, new_actor_graph, place_actor

GROUP_NAME = "PK Debris Chunk"
WELD_ATTACH = (0.0, 0.0, 0.18)


def build_debris() -> Graph:
    g = new_actor_graph(GROUP_NAME)
    sockets = add_actor_interface(g)
    seed = g.input_int("Seed", 0, description="Offsets the fracture noise")

    rock = g.mesh_ico_sphere(radius=0.16, subdivisions=1, id="rock")
    seed_f = g.math("MULTIPLY", seed, 0.37, id="seed_f")
    noise_vec = g.combine_xyz(seed_f.value, 0.0, 0.0, id="noise_vec")
    noise = g.noise_texture(scale=3.4, detail=3.0, roughness=0.55, vector=noise_vec, id="fracture")
    amp = g.math("MULTIPLY", noise.fac, 0.08, id="chip_amp")
    offset = g.vector_math("SCALE", g.normal().normal, scale=amp.value, id="chip")
    chipped = g.set_position(rock.mesh, offset=offset.vector, id="displace")

    cut_a = g.mesh_cube(size=(0.18, 0.06, 0.22), id="cut_a_mesh")
    cut_a = g.transform(cut_a, translation=(0.12, 0.08, 0.04), rotation=(0.4, 0.2, 0.6), id="cut_a")
    cut_b = g.mesh_cube(size=(0.10, 0.20, 0.08), id="cut_b_mesh")
    cut_b = g.transform(cut_b, translation=(-0.10, -0.06, 0.10), rotation=(0.2, -0.5, 0.1), id="cut_b")
    carved = g.mesh_boolean(chipped, (cut_a, cut_b), operation="DIFFERENCE", id="carve")

    # Glass stays on the shared interface so scatter can wire every actor the same way.
    place_actor(g, sockets, carved, extra_attach={"Weld Attach": WELD_ATTACH})
    return g
