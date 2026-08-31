from __future__ import annotations

import json
from pathlib import Path

from gn_as_code.dump import dumps

from probe_kit.cli import _canonical_json
from probe_kit.registry import REGISTRY, registry_dict

GRAPHS = Path(__file__).resolve().parents[1] / "graphs"


def test_dumped_graphs_match_builders() -> None:
    missing: list[str] = []
    drifted: list[str] = []
    for spec in REGISTRY:
        path = GRAPHS / f"{spec.id}.json"
        got = dumps(spec.graph().to_data())
        if not path.exists():
            missing.append(spec.id)
            continue
        if path.read_text(encoding="utf-8") != got:
            drifted.append(spec.id)
    registry_path = GRAPHS / "registry.json"
    registry_got = _canonical_json(registry_dict())
    if not registry_path.exists():
        missing.append("registry")
    elif registry_path.read_text(encoding="utf-8") != registry_got:
        drifted.append("registry")
    assert not missing, f"Missing dumps for {missing}. Run: python -m probe_kit dump"
    assert not drifted, f"Dumps drifted for {drifted}. Run: python -m probe_kit dump"


def test_dumped_json_is_gn_as_code() -> None:
    for spec in REGISTRY:
        payload = json.loads((GRAPHS / f"{spec.id}.json").read_text(encoding="utf-8"))
        assert payload["format"] == "gn-as-code"
        assert payload["kind"] == "GROUP"
        assert payload["name"] == spec.name
