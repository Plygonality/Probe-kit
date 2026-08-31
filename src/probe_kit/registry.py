"""Node-group registry for Probe-kit actors.

Python is how you author. ``graphs/registry.json`` is what git diffs.
Scatter is deferred: these groups are the instances, not the distributor.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from gn_as_code import Graph

from probe_kit.actors.crawler import GROUP_NAME as CRAWLER_NAME
from probe_kit.actors.crawler import TOOL_ATTACH, build_crawler
from probe_kit.actors.debris import GROUP_NAME as DEBRIS_NAME
from probe_kit.actors.debris import WELD_ATTACH, build_debris
from probe_kit.actors.drone import CANOPY_ATTACH, build_drone
from probe_kit.actors.drone import GROUP_NAME as DRONE_NAME
from probe_kit.materials import BINDINGS, MaterialBinding
from probe_kit.sockets import (
    ACTOR_KIND,
    ATTACH_SOCKET,
    BLENDER,
    SCALE_SOCKET,
    SHARED_INPUTS,
    SHARED_OUTPUTS,
)

FORMAT = "node-group-registry"
FORMAT_VERSION = 1
INTERFACE_VERSION = 1
SCATTER = "later"


@dataclass(frozen=True)
class AttachSocket:
    name: str
    role: str
    space: str
    description: str
    local: tuple[float, float, float] | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "role": self.role,
            "space": self.space,
            "description": self.description,
        }
        if self.local is not None:
            data["local"] = list(self.local)
        return data


@dataclass(frozen=True)
class ActorSpec:
    id: str
    name: str
    label: str
    description: str
    build: Callable[[], Graph]
    attach: tuple[AttachSocket, ...]
    materials: tuple[MaterialBinding, ...] = BINDINGS
    extra_inputs: tuple[str, ...] = ()
    extra_outputs: tuple[str, ...] = ()
    scatter: str = SCATTER

    def graph(self) -> Graph:
        return self.build()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "kind": ACTOR_KIND.value,
            "blender": BLENDER,
            "scatter": self.scatter,
            "scale_socket": SCALE_SOCKET,
            "attach": [item.to_dict() for item in self.attach],
            "materials": [item.to_dict() for item in self.materials],
            "interface": {
                "inputs": list(SHARED_INPUTS) + list(self.extra_inputs),
                "outputs": list(SHARED_OUTPUTS) + list(self.extra_outputs),
            },
        }


CRAWLER = ActorSpec(
    id="von_neumann_crawler",
    name=CRAWLER_NAME,
    label="Von Neumann crawler",
    description=(
        "Self-replicator that walks a hull. Origin is the foot plane. "
        "Sensor dome is glass; chassis, legs, and harvest arm are hull metal."
    ),
    build=build_crawler,
    attach=(
        AttachSocket(
            ATTACH_SOCKET,
            role="contact",
            space="world",
            description="Foot plane. Plant on a surface; scatter later instances here.",
            local=(0.0, 0.0, 0.0),
        ),
        AttachSocket(
            "Tool Attach",
            role="tool",
            space="local",
            description="Harvest-arm tip. Local offset, already scaled.",
            local=TOOL_ATTACH,
        ),
    ),
    extra_outputs=("Tool Attach",),
)

DRONE = ActorSpec(
    id="service_drone",
    name=DRONE_NAME,
    label="Service drone",
    description=(
        "Short-range tender. Origin is the underside dock. "
        "Canopy is glass; fuselage and thrusters are hull metal."
    ),
    build=build_drone,
    attach=(
        AttachSocket(
            ATTACH_SOCKET,
            role="dock",
            space="world",
            description="Underside docking ring. Hang from a bay or plant on a pad.",
            local=(0.0, 0.0, 0.0),
        ),
        AttachSocket(
            "Canopy Attach",
            role="canopy",
            space="local",
            description="Glass canopy apex. Local offset, already scaled.",
            local=CANOPY_ATTACH,
        ),
    ),
    extra_outputs=("Canopy Attach",),
)

DEBRIS = ActorSpec(
    id="debris_chunk",
    name=DEBRIS_NAME,
    label="Debris chunk",
    description=(
        "Fractured hull fragment. Origin is the centroid. "
        "Hull metal only; the Glass socket is kept for the shared contract."
    ),
    build=build_debris,
    attach=(
        AttachSocket(
            ATTACH_SOCKET,
            role="centroid",
            space="world",
            description="Chunk centroid. Scatter later instances here.",
            local=(0.0, 0.0, 0.0),
        ),
        AttachSocket(
            "Weld Attach",
            role="weld",
            space="local",
            description="A point on the fragment toward +Z. Local offset, already scaled.",
            local=WELD_ATTACH,
        ),
    ),
    extra_inputs=("Seed",),
    extra_outputs=("Weld Attach",),
)

REGISTRY: tuple[ActorSpec, ...] = (CRAWLER, DRONE, DEBRIS)
REGISTRY_BY_ID: dict[str, ActorSpec] = {spec.id: spec for spec in REGISTRY}
REGISTRY_BY_NAME: dict[str, ActorSpec] = {spec.name: spec for spec in REGISTRY}


def list_actors() -> Sequence[ActorSpec]:
    return REGISTRY


def get_actor(id_or_name: str) -> ActorSpec:
    if id_or_name in REGISTRY_BY_ID:
        return REGISTRY_BY_ID[id_or_name]
    if id_or_name in REGISTRY_BY_NAME:
        return REGISTRY_BY_NAME[id_or_name]
    known = ", ".join(spec.id for spec in REGISTRY)
    raise KeyError(f"Unknown actor {id_or_name!r}. Registered: {known}")


def registry_dict() -> dict[str, Any]:
    return {
        "format": FORMAT,
        "version": FORMAT_VERSION,
        "interface_version": INTERFACE_VERSION,
        "kind": ACTOR_KIND.value,
        "scatter": SCATTER,
        "scale_socket": SCALE_SOCKET,
        "shared": {
            "inputs": list(SHARED_INPUTS),
            "outputs": list(SHARED_OUTPUTS),
        },
        "materials": [item.to_dict() for item in BINDINGS],
        "groups": [spec.to_dict() for spec in REGISTRY],
    }
