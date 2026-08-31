# Probe-kit

Small reusable Geometry Node **actors** as registered graphs.

A crawler, a drone, a debris chunk. Each is a node group with a Scale socket, attach sockets, and Master-Node hull/glass. Git is the source of truth. The `.blend` is a cache.

Scatter is later. These groups are the instances, not the distributor.

```
Python builder  →  graphs/*.json  →  Plygon-mcp apply  →  viewport
                      ↑
              node-group-registry
```

This is a catalog you import, not another `execute_python` wrapper.

```python
from probe_kit import get_actor

crawler = get_actor("von_neumann_crawler").graph()
Path("graphs/von_neumann_crawler.json").write_text(crawler.dumps())
```

## Why this repo exists

A kit of `.blend` props is a pack. The pack goes stale the moment you need a socket that is not on the object.

A **registered group** is the opposite. Each actor is one Geometry Node tree. Scale is one float. Attach is a named socket. Hull and glass are material sockets that bind to [Master-Node](https://github.com/Plygonality/Master-Node) category masters. A later scatter graph instances these groups. It does not rebuild them.

| Role | Job |
|---|---|
| **This catalog** | Actor graphs, node-group-registry, shared Scale / Attach / Hull / Glass contract |
| **[gn-as-code](https://github.com/Plygonality/gn-as-code)** | Typed builders, canonical JSON, structural diffs |
| **[Master-Node](https://github.com/Plygonality/Master-Node)** | Hull = `MN Metal`, glass = `MN Glass`. Look-dev in the N-panel |
| **[Plygon-mcp](https://github.com/Plygonality/Plygon-mcp)** | Apply a dump and screenshot the viewport |
| **The `.blend`** | Working cache, never the source of truth |

## Actors

Z-up, Y-forward. Origin is the primary attach.

| id | Group | Primary attach | Extra attach | Hull | Glass |
|---|---|---|---|---|---|
| `von_neumann_crawler` | PK Von Neumann Crawler | `Attach` — foot plane (`contact`) | `Tool Attach` — harvest-arm tip | chassis, legs, arm | sensor dome |
| `service_drone` | PK Service Drone | `Attach` — underside dock | `Canopy Attach` — canopy apex | fuselage, thrusters, ring | canopy |
| `debris_chunk` | PK Debris Chunk | `Attach` — centroid | `Weld Attach` — +Z fragment point | whole chunk | unwired (socket kept) |

Debris keeps the Glass socket so a scatter graph can wire every actor the same way.

## Shared sockets

Every group is `kind=GROUP` (nestable). Extra per-actor sockets come after this contract.

**Inputs**

| Socket | Type | Default | Notes |
|---|---|---|---|
| Scale | FLOAT | 1.0 | Uniform, around the origin |
| Attach Location | VECTOR | (0, 0, 0) | Plants the origin |
| Attach Rotation | VECTOR | (0, 0, 0) | Euler XYZ, radians |
| Hull | MATERIAL | — | Master-Node `metal` (`MN Metal`, free look `metal.brushed_aluminum`) |
| Glass | MATERIAL | — | Master-Node `glass` (`MN Glass`, free look `glass.clear`) |

**Outputs**

| Socket | Type | Space | Notes |
|---|---|---|---|
| Geometry | GEOMETRY | world | After Scale / Attach transform |
| Attach | VECTOR | world | Equals Attach Location — the planted origin |
| *(extra)* | VECTOR | local | Offset × Scale. Scatter applies instance rotation later |

## Install

```bash
pip install -e ".[dev]"
python -m probe_kit list
python -m probe_kit dump
pytest -q
```

Python 3.10+. No Blender required to build, dump, or validate. [gn-as-code](https://github.com/Plygonality/gn-as-code) is pulled from GitHub.

```bash
python -m probe_kit validate
python -m probe_kit apply-script von_neumann_crawler --object Crawler
```

`dump` writes `graphs/`. That JSON is what git diffs. `--check` fails if it is stale.

## Apply in Blender (via Plygon-mcp)

The agent authors a graph here, then asks Plygon-mcp to run a self-contained bpy script. Blender does not need this package installed.

```python
from probe_kit import get_actor
from gn_as_code.apply import to_apply_script

script = to_apply_script(
    get_actor("service_drone").graph().to_data(),
    object_name="ServiceDrone",
)
# Plygon-mcp: execute_blender_code(script) → get_viewport_screenshot()
```

Create **MN Metal** and **MN Glass** with Master-Node, assign them to the Hull / Glass sockets. Do not author a unique shader per actor.

## Tests

```bash
pip install -e ".[dev]"
pytest -q
python -m probe_kit dump --check
```

```bash
python -m probe_kit dump   # rewrite graphs/ after an intentional builder change
```

If a dump drifted and the change was not intended, the test failed for a reason.

## Layout

```
src/probe_kit/          registry, shared sockets, actor builders
graphs/                 canonical gn-as-code JSON + registry.json
tests/                  contract, validation, golden dumps
```

## Scatter later

Do not distribute these groups yet. A future scatter graph will instance them on a host mesh, drive Scale, and plant Attach Location / Attach Rotation from face points. The registry records `"scatter": "later"` until that graph exists.
