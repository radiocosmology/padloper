"""
_diagram.py

A whole-system view of the inventory as a Graphviz graph: every active
component, nested by subcomponent containment, with the connections in force
at a given time drawn between them.
"""
import collections
import datetime
import html
import shutil
import subprocess
import time
from typing import Optional

import _global as g
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import P

__all__ = ["system_inventory", "system_summary", "system_dot", "render_dot"]

# Fill colours assigned to component types in sorted order.
_PALETTE = ["#cfe2f3", "#d9ead3", "#fff2cc", "#f4cccc", "#d9d2e9", "#fce5cd",
            "#c9daf8", "#e6b8af", "#b6d7a8", "#ffe599", "#ea9999", "#b4a7d6",
            "#f9cb9c", "#a2c4c9", "#d5a6bd"]


def system_inventory(at_time: Optional[int] = None) -> dict:
    """Read what the system diagram needs from the database.

    :param at_time: UNIX time at which connections must be in force
        (start_time <= at_time < end_time); defaults to now. Components are
        the currently active ones.
    :type at_time: int
    :return: A dictionary with 'components' ([{'name', 'type'}]),
        'containment' ([(subcomponent, container)]), 'connections'
        ([(a, b)]) and 'at_time'.
    :rtype: dict
    """
    if at_time is None:
        at_time = int(time.time())
    components = g.t.V().has("category", "component").has("active", True) \
        .project("name", "type").by("name") \
        .by(__.coalesce(__.both("rel_component_type").has("active", True)
                        .values("name").limit(1), __.constant("?"))) \
        .toList()
    # The rel_subcomponent edge runs from the subcomponent (out) to its
    # container (in); see Component.get_subcomponents().
    containment = g.t.E().hasLabel("rel_subcomponent").has("active", True) \
        .project("sub", "container") \
        .by(__.outV().values("name")).by(__.inV().values("name")).toList()
    connections = g.t.E().hasLabel("rel_connection").has("active", True) \
        .has("start_time", P.lte(at_time)).has("end_time", P.gt(at_time)) \
        .project("a", "b") \
        .by(__.outV().values("name")).by(__.inV().values("name")).toList()
    return {
        "components": [{"name": c["name"], "type": c["type"]} for c in components],
        "containment": [(e["sub"], e["container"]) for e in containment],
        "connections": [(e["a"], e["b"]) for e in connections],
        "at_time": at_time,
    }


def _type_colours(type_of: dict) -> dict:
    """Fill colour per component type, assigned in sorted order so it is
    stable between renders."""
    types = sorted(set(type_of.values()))
    return {t: _PALETTE[i % len(_PALETTE)] for i, t in enumerate(types)}


def _drawn_connections(inventory: dict, type_of: dict) -> list:
    return [(a, b) for a, b in inventory["connections"]
            if a in type_of and b in type_of]


def system_summary(inventory: Optional[dict] = None) -> dict:
    """The legend data for the system view: each component type with its
    colour and count, plus totals. Fetches the inventory when omitted.

    :return: {'types': [{'name', 'colour', 'count'}], 'components': int,
        'connections': int, 'at_time': int}
    :rtype: dict
    """
    if inventory is None:
        inventory = system_inventory()
    type_of = {c["name"]: c["type"] for c in inventory["components"]}
    colour = _type_colours(type_of)
    counts = collections.Counter(type_of.values())
    return {
        "types": [{"name": t, "colour": colour[t], "count": counts[t]}
                  for t in sorted(counts)],
        "components": len(type_of),
        "connections": len(_drawn_connections(inventory, type_of)),
        "at_time": inventory["at_time"],
    }


def _plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def _quoted(s) -> str:
    """A DOT double-quoted string."""
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _label(s) -> str:
    """Text for use inside a DOT double-quoted label."""
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def system_dot(inventory: Optional[dict] = None, rankdir: str = "LR") -> str:
    """Return the Graphviz DOT source for the system view.

    Pure given `inventory` (the structure returned by system_inventory()), so
    it can be tested without a database; fetches the inventory when omitted.

    :param inventory: See system_inventory().
    :param rankdir: Graphviz rank direction, "LR" or "TB".
    :return: DOT source.
    :rtype: str
    """
    if inventory is None:
        inventory = system_inventory()
    type_of = {c["name"]: c["type"] for c in inventory["components"]}
    colour = _type_colours(type_of)
    parent_of = {sub: container for sub, container in inventory["containment"]
                 if sub in type_of and container in type_of}
    children = collections.defaultdict(list)
    for sub, container in parent_of.items():
        children[container].append(sub)
    stamp = datetime.datetime.fromtimestamp(
        inventory["at_time"], datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "graph padloper {",
        f'  label="Padloper system view as of {stamp}.  Boxes: components '
        '(colour = type).  Nesting: subcomponents.  Lines: connections.";',
        f'  labelloc=t; fontname="Helvetica"; fontsize=20; rankdir={rankdir}; '
        "splines=true; nodesep=0.25; ranksep=0.6;",
        '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10];',
        '  edge [color="#444444", penwidth=1.2];',
    ]
    counter = [0]
    visited = set()

    def node_line(name, indent, container=False):
        t = type_of[name]
        extra = ", peripheries=2" if container else ""
        return (f'{indent}{_quoted(name)} [label="{_label(name)}\\n{_label(t)}", '
                f'fillcolor="{colour[t]}"{extra}];')

    def emit(name, indent):
        if name in visited:
            return
        visited.add(name)
        kids = sorted(children.get(name, []))
        if kids:
            counter[0] += 1
            lines.append(f"{indent}subgraph cluster_{counter[0]} {{")
            lines.append(f'{indent}  label="{_label(name)}  ({_label(type_of[name])})"; '
                         'style="rounded"; color="#999999"; fontname="Helvetica"; fontsize=11;')
            lines.append(node_line(name, indent + "  ", container=True))
            for kid in kids:
                emit(kid, indent + "  ")
            lines.append(f"{indent}}}")
        else:
            lines.append(node_line(name, indent))

    for root in sorted(n for n in type_of if n not in parent_of):
        emit(root, "  ")
    for name in sorted(type_of):      # anything left over (containment cycles)
        emit(name, "  ")
    connections = _drawn_connections(inventory, type_of)
    for a, b in connections:
        lines.append(f"  {_quoted(a)} -- {_quoted(b)};")

    # Legend: an HTML-like table node, so it survives in downloaded files.
    counts = collections.Counter(type_of.values())
    rows = "".join(
        f'<TR><TD BGCOLOR="{colour[t]}">{html.escape(t)}</TD>'
        f'<TD ALIGN="RIGHT">{counts[t]}</TD></TR>' for t in sorted(counts))
    lines.append("  subgraph cluster_legend {")
    lines.append('    label="Legend"; style="rounded"; color="#999999"; '
                 'fontname="Helvetica"; fontsize=11;')
    lines.append('    "__legend__" [shape=none, margin=0, fillcolor="white", label=<'
                 '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">'
                 '<TR><TD COLSPAN="2"><B>Component types</B></TD></TR>'
                 f'{rows}'
                 f'<TR><TD COLSPAN="2">{_plural(len(type_of), "component")}, '
                 f'{_plural(len(connections), "connection")}</TD></TR>'
                 '<TR><TD COLSPAN="2">Double border: contains subcomponents</TD></TR>'
                 "</TABLE>>];")
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_dot(dot_source: str, fmt: str = "svg") -> bytes:
    """Render DOT source with the Graphviz `dot` program.

    :param dot_source: DOT text, e.g. from system_dot().
    :param fmt: A Graphviz output format such as "svg" or "png".
    :return: The rendered image.
    :rtype: bytes
    :raises RuntimeError: if Graphviz is not installed or rendering fails.
    """
    if shutil.which("dot") is None:
        raise RuntimeError("Graphviz is not installed on the server "
                           "(the 'dot' program was not found).")
    result = subprocess.run(["dot", f"-T{fmt}"], input=dot_source.encode(),
                            capture_output=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError("Graphviz failed: " +
                           result.stderr.decode(errors="replace").strip())
    return result.stdout
