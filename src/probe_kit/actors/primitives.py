"""Primitive placement helpers used by the actor builders."""

from __future__ import annotations

from collections.abc import Sequence

from gn_as_code import Graph
from gn_as_code.graph import InputValue, NodeHandle


def box(
    g: Graph,
    size: Sequence[float],
    location: Sequence[float],
    *,
    id: str,
) -> NodeHandle:
    mesh = g.mesh_cube(size=tuple(size), id=f"{id}_mesh")
    return g.transform(mesh, translation=tuple(location), id=id)


def cylinder(
    g: Graph,
    *,
    radius: float,
    depth: float,
    location: Sequence[float],
    rotation: Sequence[float] = (0.0, 0.0, 0.0),
    vertices: int = 12,
    id: str,
) -> NodeHandle:
    mesh = g.mesh_cylinder(
        vertices=vertices,
        radius=radius,
        depth=depth,
        id=f"{id}_mesh",
    )
    return g.transform(
        mesh,
        translation=tuple(location),
        rotation=tuple(rotation),
        id=id,
    )


def cone(
    g: Graph,
    *,
    radius_bottom: float,
    depth: float,
    location: Sequence[float],
    rotation: Sequence[float] = (0.0, 0.0, 0.0),
    radius_top: float = 0.0,
    vertices: int = 12,
    id: str,
) -> NodeHandle:
    mesh = g.mesh_cone(
        vertices=vertices,
        radius_top=radius_top,
        radius_bottom=radius_bottom,
        depth=depth,
        id=f"{id}_mesh",
    )
    return g.transform(
        mesh,
        translation=tuple(location),
        rotation=tuple(rotation),
        id=id,
    )


def sphere(
    g: Graph,
    *,
    radius: float,
    location: Sequence[float],
    scale: Sequence[float] = (1.0, 1.0, 1.0),
    segments: int = 16,
    rings: int = 8,
    id: str,
) -> NodeHandle:
    mesh = g.mesh_uv_sphere(
        segments=segments,
        rings=rings,
        radius=radius,
        id=f"{id}_mesh",
    )
    return g.transform(
        mesh,
        translation=tuple(location),
        scale=tuple(scale),
        id=id,
    )


def join(g: Graph, *parts: InputValue, id: str) -> NodeHandle:
    return g.join_geometry(*parts, id=id)
