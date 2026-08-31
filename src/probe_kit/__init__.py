"""Probe-kit: reusable Geometry Node actors as registered graphs.

[gn-as-code](https://github.com/Plygonality/gn-as-code) is how the trees are
authored. This package is the catalog: scale, attach sockets, Master-Node
hull/glass. Scatter is later.
"""

from probe_kit.materials import GLASS, HULL, MaterialBinding
from probe_kit.registry import REGISTRY, ActorSpec, AttachSocket, get_actor, list_actors
from probe_kit.sockets import (
    ACTOR_KIND,
    SHARED_INPUTS,
    SHARED_OUTPUTS,
    ActorSockets,
    add_actor_interface,
    place_actor,
)

__all__ = [
    "ACTOR_KIND",
    "GLASS",
    "HULL",
    "REGISTRY",
    "SHARED_INPUTS",
    "SHARED_OUTPUTS",
    "ActorSockets",
    "ActorSpec",
    "AttachSocket",
    "MaterialBinding",
    "add_actor_interface",
    "get_actor",
    "list_actors",
    "place_actor",
]

__version__ = "0.1.0"
