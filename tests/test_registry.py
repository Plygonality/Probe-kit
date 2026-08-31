from __future__ import annotations

from probe_kit.registry import REGISTRY, get_actor, registry_dict
from probe_kit.sockets import SHARED_INPUTS, SHARED_OUTPUTS


def test_registry_ids_and_names_unique() -> None:
    ids = [spec.id for spec in REGISTRY]
    names = [spec.name for spec in REGISTRY]
    assert len(ids) == len(set(ids))
    assert len(names) == len(set(names))
    assert {spec.id for spec in REGISTRY} == {
        "von_neumann_crawler",
        "service_drone",
        "debris_chunk",
    }


def test_get_actor_accepts_id_or_group_name() -> None:
    by_id = get_actor("service_drone")
    by_name = get_actor("PK Service Drone")
    assert by_id is by_name
    try:
        get_actor("nope")
    except KeyError as err:
        assert "von_neumann_crawler" in str(err)
    else:
        raise AssertionError("expected KeyError")


def test_registry_dict_contract() -> None:
    payload = registry_dict()
    assert payload["format"] == "node-group-registry"
    assert payload["kind"] == "GROUP"
    assert payload["scatter"] == "later"
    assert payload["scale_socket"] == "Scale"
    assert payload["shared"]["inputs"] == list(SHARED_INPUTS)
    assert payload["shared"]["outputs"] == list(SHARED_OUTPUTS)
    sockets = {m["socket"]: m["master_category"] for m in payload["materials"]}
    assert sockets == {"Hull": "metal", "Glass": "glass"}
    assert [g["id"] for g in payload["groups"]] == [
        "von_neumann_crawler",
        "service_drone",
        "debris_chunk",
    ]
