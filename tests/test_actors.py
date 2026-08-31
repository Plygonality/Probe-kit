from __future__ import annotations

from gn_as_code import GraphKind, SocketType, validate

from probe_kit.registry import REGISTRY


def test_every_actor_is_a_valid_group() -> None:
    for spec in REGISTRY:
        data = spec.graph().to_data()
        assert data.kind == GraphKind.GROUP, spec.id
        errors = validate(data)
        assert errors == [], (spec.id, [str(e) for e in errors])


def test_shared_scale_and_attach_sockets() -> None:
    for spec in REGISTRY:
        data = spec.graph().to_data()
        inputs = {item.name: item for item in data.interface_inputs}
        outputs = {item.name: item for item in data.interface_outputs}

        assert inputs["Scale"].socket == SocketType.FLOAT
        assert inputs["Scale"].default == 1
        assert inputs["Attach Location"].socket == SocketType.VECTOR
        assert inputs["Attach Rotation"].socket == SocketType.VECTOR
        assert inputs["Hull"].socket == SocketType.MATERIAL
        assert inputs["Glass"].socket == SocketType.MATERIAL

        assert outputs["Geometry"].socket == SocketType.GEOMETRY
        assert outputs["Attach"].socket == SocketType.VECTOR

        for extra in spec.extra_inputs:
            assert extra in inputs, spec.id
        for extra in spec.extra_outputs:
            assert extra in outputs, spec.id
            assert outputs[extra].socket == SocketType.VECTOR


def test_primary_attach_is_the_location_socket() -> None:
    for spec in REGISTRY:
        data = spec.graph().to_data()
        wired = [
            ln
            for ln in data.links
            if ln.to_node == "Group Output" and ln.to_socket == "Attach"
        ]
        assert len(wired) == 1, spec.id
        assert wired[0].from_node == "Group Input"
        assert wired[0].from_socket == "Attach Location"


def test_place_uses_scale_location_rotation() -> None:
    for spec in REGISTRY:
        data = spec.graph().to_data()
        into_place = {
            ln.to_socket: ln.from_socket
            for ln in data.links
            if ln.to_node == "place" and ln.from_node == "Group Input"
        }
        assert into_place["Translation"] == "Attach Location", spec.id
        assert into_place["Rotation"] == "Attach Rotation", spec.id
        scale_links = [
            ln for ln in data.links if ln.to_node == "place" and ln.to_socket == "Scale"
        ]
        assert scale_links, spec.id
        assert data.node_map()[scale_links[0].from_node].type == "ShaderNodeCombineXYZ"


def test_master_node_materials_are_wired() -> None:
    for spec in REGISTRY:
        data = spec.graph().to_data()
        nodes = data.node_map()
        hull = nodes["assign_hull"]
        assert hull.type == "GeometryNodeSetMaterial"
        hull_mat = [
            ln.from_socket
            for ln in data.links
            if ln.to_node == "assign_hull" and ln.to_socket == "Material"
        ]
        assert hull_mat == ["Hull"], spec.id
        if spec.id == "debris_chunk":
            assert "assign_glass" not in nodes
            continue
        glass_mat = [
            ln.from_socket
            for ln in data.links
            if ln.to_node == "assign_glass" and ln.to_socket == "Material"
        ]
        assert glass_mat == ["Glass"], spec.id
