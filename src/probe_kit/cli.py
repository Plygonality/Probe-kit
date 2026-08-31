"""Dump registered graphs, validate, emit Plygon-mcp apply scripts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gn_as_code.apply import to_apply_script
from gn_as_code.dump import dumps
from gn_as_code.validate import validate

from probe_kit.registry import REGISTRY, get_actor, registry_dict

ROOT = Path(__file__).resolve().parents[2]
GRAPHS = ROOT / "graphs"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="probe-kit",
        description="Reusable Geometry Node actors as registered graphs.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="Print the node-group registry")

    p_dump = sub.add_parser("dump", help="Write canonical JSON for every registered group")
    p_dump.add_argument("-o", "--output", type=Path, default=GRAPHS)
    p_dump.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if graphs/ is stale instead of writing",
    )

    p_val = sub.add_parser("validate", help="Validate every registered graph")
    p_val.add_argument("id", nargs="?")

    p_apply = sub.add_parser("apply-script", help="Emit a bpy script Plygon-mcp can run")
    p_apply.add_argument("id")
    p_apply.add_argument("--object")
    p_apply.add_argument("-o", "--output", type=Path)

    args = parser.parse_args(argv)
    if args.cmd == "list":
        sys.stdout.write(json.dumps(registry_dict(), indent=2) + "\n")
        return 0
    if args.cmd == "dump":
        return _dump(args.output, check=args.check)
    if args.cmd == "validate":
        return _validate(args.id)
    if args.cmd == "apply-script":
        spec = get_actor(args.id)
        script = to_apply_script(spec.graph().to_data(), object_name=args.object)
        if args.output:
            args.output.write_text(script, encoding="utf-8")
        else:
            sys.stdout.write(script)
        return 0
    raise AssertionError(args.cmd)


def _dump(out: Path, *, check: bool) -> int:
    written: dict[str, str] = {"registry.json": _canonical_json(registry_dict())}
    for spec in REGISTRY:
        written[f"{spec.id}.json"] = dumps(spec.graph().to_data())

    if check:
        stale: list[str] = []
        for name, text in written.items():
            path = out / name
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        if stale:
            sys.stderr.write("stale graphs: " + ", ".join(stale) + "\n")
            sys.stderr.write("Re-run: python -m probe_kit dump\n")
            return 1
        sys.stdout.write("ok\n")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    for name, text in written.items():
        (out / name).write_text(text, encoding="utf-8")
        sys.stdout.write(f"wrote {out / name}\n")
    return 0


def _validate(id_or_name: str | None) -> int:
    specs = [get_actor(id_or_name)] if id_or_name else list(REGISTRY)
    failed = 0
    for spec in specs:
        errors = validate(spec.graph().to_data())
        if errors:
            failed += 1
            for err in errors:
                sys.stderr.write(f"{spec.id}: {err}\n")
        else:
            sys.stdout.write(f"{spec.id}: ok\n")
    return 2 if failed else 0


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
