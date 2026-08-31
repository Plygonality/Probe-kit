from __future__ import annotations

from probe_kit.cli import main
from probe_kit.registry import REGISTRY


def test_cli_list_and_validate(capsys) -> None:
    assert main(["list"]) == 0
    listed = capsys.readouterr().out
    assert "node-group-registry" in listed
    assert "von_neumann_crawler" in listed
    assert main(["validate"]) == 0
    validated = capsys.readouterr().out
    for spec in REGISTRY:
        assert f"{spec.id}: ok" in validated


def test_cli_apply_script_mentions_group(capsys) -> None:
    assert main(["apply-script", "von_neumann_crawler"]) == 0
    script = capsys.readouterr().out
    assert "PK Von Neumann Crawler" in script
    assert "apply_graph_dict" in script
