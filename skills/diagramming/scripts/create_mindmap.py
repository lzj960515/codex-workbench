#!/usr/bin/env python3
"""Create an editable sketch mind map as uncompressed draw.io XML."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PAPER = "#FFFDF5"
INK = "#243142"
PALETTE = {
    "blue": ("#DCEBFF", "#376A9E"),
    "yellow": ("#FFF2CC", "#9A6B14"),
    "green": ("#DFF3E4", "#3F7D54"),
    "red": ("#F9DFDF", "#A84B49"),
    "violet": ("#E9E1F7", "#76569A"),
    "orange": ("#FDE7C3", "#A8642A"),
}
PALETTE_ORDER = tuple(PALETTE)
LAYOUTS = {"both", "right", "left"}
SIDES = {"right", "left"}
MAX_NODES = 200
MAX_DEPTH = 8
LEAF_GAP = 34.0
SUBTREE_GAP = 52.0
FIRST_LEVEL_GAP = 150.0
LEVEL_STEP = 270.0
PAGE_MARGIN = 90.0


@dataclass
class Topic:
    text: str
    path: tuple[int, ...]
    level: int
    color_name: str | None = None
    requested_side: str | None = None
    children: list["Topic"] = field(default_factory=list)
    side: str = "right"
    fill: str = PALETTE["yellow"][0]
    stroke: str = PALETTE["yellow"][1]
    width: float = 160.0
    height: float = 54.0
    span: float = 54.0
    x: float = 0.0
    y: float = 0.0

    @property
    def topic_id(self) -> str:
        if not self.path:
            return "topic-root"
        return "topic-" + "-".join(str(part) for part in self.path)


def fail(message: str) -> None:
    raise SystemExit(message)


def display_units(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1 for char in text)


def topic_size(text: str, level: int) -> tuple[float, float]:
    units = display_units(text)
    if level == 0:
        width = max(190, min(310, 92 + units * 11))
        chars_per_line = 20
        base_height = 84
        line_height = 25
    elif level == 1:
        width = max(155, min(250, 66 + units * 9))
        chars_per_line = 24
        base_height = 62
        line_height = 21
    elif level == 2:
        width = max(140, min(225, 58 + units * 8))
        chars_per_line = 26
        base_height = 54
        line_height = 19
    else:
        width = max(125, min(210, 52 + units * 7.5))
        chars_per_line = 28
        base_height = 48
        line_height = 18
    lines = max(1, math.ceil(units / chars_per_line))
    return float(width), float(base_height + (lines - 1) * line_height)


def parse_topic(raw: Any, path: tuple[int, ...], level: int) -> Topic:
    if not isinstance(raw, dict):
        fail(f"branches{list(path)} must be an object")
    text = raw.get("text")
    if not isinstance(text, str) or not text.strip():
        fail(f"branches{list(path)}.text must be a non-empty string")
    if level > MAX_DEPTH:
        fail(f"mind map depth exceeds {MAX_DEPTH} at {text!r}; split it into a detail map")

    color_name = raw.get("color")
    if color_name is not None and color_name not in PALETTE:
        fail(f"branches{list(path)}.color must be one of: {', '.join(PALETTE)}")
    if color_name is not None and level != 1:
        fail(f"branches{list(path)}.color is only supported on first-level branches")

    requested_side = raw.get("side")
    if requested_side is not None:
        if level != 1:
            fail(f"branches{list(path)}.side is only supported on first-level branches")
        if requested_side not in SIDES:
            fail(f"branches{list(path)}.side must be left or right")

    children_raw = raw.get("children", [])
    if not isinstance(children_raw, list):
        fail(f"branches{list(path)}.children must be an array")
    topic = Topic(text=text.strip(), path=path, level=level, color_name=color_name, requested_side=requested_side)
    topic.children = [
        parse_topic(child, path + (index,), level + 1)
        for index, child in enumerate(children_raw, start=1)
    ]
    return topic


def load_outline(path: Path) -> tuple[Topic, str]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"outline file not found: {path}")
    except json.JSONDecodeError as error:
        fail(f"invalid outline JSON at line {error.lineno}, column {error.colno}: {error.msg}")

    if not isinstance(raw, dict):
        fail("outline root must be an object")
    title = raw.get("title")
    if not isinstance(title, str) or not title.strip():
        fail("title must be a non-empty string")
    layout = raw.get("layout", "both")
    if layout not in LAYOUTS:
        fail("layout must be both, right, or left")
    branches = raw.get("branches")
    if not isinstance(branches, list) or not branches:
        fail("branches must be a non-empty array")

    root = Topic(text=title.strip(), path=(), level=0)
    root.children = [
        parse_topic(branch, (index,), 1)
        for index, branch in enumerate(branches, start=1)
    ]
    node_count = sum(1 for _ in walk_topics(root))
    if node_count > MAX_NODES:
        fail(f"mind map has {node_count} nodes; split it into maps of at most {MAX_NODES} nodes")
    return root, layout


def walk_topics(topic: Topic):
    yield topic
    for child in topic.children:
        yield from walk_topics(child)


def measure(topic: Topic) -> float:
    topic.width, topic.height = topic_size(topic.text, topic.level)
    if topic.children:
        child_spans = [measure(child) for child in topic.children]
        topic.span = max(topic.height, sum(child_spans) + LEAF_GAP * (len(child_spans) - 1))
    else:
        topic.span = topic.height
    return topic.span


def assign_branch_styles(root: Topic, layout: str) -> None:
    side_load = {"left": 0.0, "right": 0.0}
    for index, branch in enumerate(root.children):
        color_name = branch.color_name or PALETTE_ORDER[index % len(PALETTE_ORDER)]
        branch.fill, branch.stroke = PALETTE[color_name]

        if layout in SIDES:
            side = layout
        elif branch.requested_side:
            side = branch.requested_side
        else:
            side = "right" if side_load["right"] <= side_load["left"] else "left"
        branch.side = side
        side_load[side] += branch.span + SUBTREE_GAP
        propagate_style(branch, side, branch.fill, branch.stroke)


def propagate_style(topic: Topic, side: str, fill: str, stroke: str) -> None:
    topic.side = side
    topic.fill = fill
    topic.stroke = stroke
    for child in topic.children:
        propagate_style(child, side, fill, stroke)


def level_center_x(root: Topic, topic: Topic) -> float:
    distance = root.width / 2 + FIRST_LEVEL_GAP + topic.width / 2
    distance += (topic.level - 1) * LEVEL_STEP
    return distance if topic.side == "right" else -distance


def place_subtree(root: Topic, topic: Topic, top: float) -> None:
    topic.x = level_center_x(root, topic)
    if not topic.children:
        topic.y = top + topic.span / 2
        return

    children_height = sum(child.span for child in topic.children)
    children_height += LEAF_GAP * (len(topic.children) - 1)
    child_top = top + (topic.span - children_height) / 2
    for child in topic.children:
        place_subtree(root, child, child_top)
        child_top += child.span + LEAF_GAP
    topic.y = (topic.children[0].y + topic.children[-1].y) / 2


def place_topics(root: Topic) -> None:
    root.x = 0.0
    root.y = 0.0
    for side in ("left", "right"):
        branches = [branch for branch in root.children if branch.side == side]
        if not branches:
            continue
        total = sum(branch.span for branch in branches)
        total += SUBTREE_GAP * (len(branches) - 1)
        top = -total / 2
        for branch in branches:
            place_subtree(root, branch, top)
            top += branch.span + SUBTREE_GAP


def shift_to_page(root: Topic) -> tuple[int, int]:
    topics = list(walk_topics(root))
    min_x = min(topic.x - topic.width / 2 for topic in topics)
    max_x = max(topic.x + topic.width / 2 for topic in topics)
    min_y = min(topic.y - topic.height / 2 for topic in topics)
    max_y = max(topic.y + topic.height / 2 for topic in topics)
    dx = PAGE_MARGIN - min_x
    dy = PAGE_MARGIN - min_y
    for topic in topics:
        topic.x += dx
        topic.y += dy
    width = max(1200, int(math.ceil((max_x - min_x + 2 * PAGE_MARGIN) / 100) * 100))
    height = max(800, int(math.ceil((max_y - min_y + 2 * PAGE_MARGIN) / 100) * 100))
    return width, height


def node_style(topic: Topic) -> str:
    common = (
        "whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
        "container=1;recursiveResize=0;treeFolding=1;collapsible=1;"
        "sketch=1;curveFitting=1;jiggle=2;hachureGap=8;fillWeight=1.5;"
        f"fontFamily=Chalkboard SE,Comic Sans MS;fontColor={INK};spacing=10;"
    )
    if topic.level == 0:
        return common + (
            "ellipse;aspect=fixed;fillColor=#FFF2CC;"
            f"strokeColor={INK};strokeWidth=3;fontSize=26;fontStyle=1;"
        )
    if topic.level == 1:
        return common + (
            f"rounded=1;arcSize=24;fillColor={topic.fill};strokeColor={topic.stroke};"
            "strokeWidth=2.5;fontSize=19;fontStyle=1;"
        )
    if topic.level == 2:
        return common + (
            f"rounded=1;arcSize=20;fillColor={topic.fill};fillOpacity=62;"
            f"strokeColor={topic.stroke};strokeWidth=2;fontSize=17;"
        )
    return common + (
        f"rounded=1;arcSize=16;fillColor={PAPER};strokeColor={topic.stroke};"
        "strokeWidth=1.8;fontSize=16;"
    )


def edge_style(parent: Topic, child: Topic) -> str:
    width = 3.4 if child.level == 1 else 2.6 if child.level == 2 else 2.0
    if child.side == "right":
        terminals = "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
    else:
        terminals = "exitX=0;exitY=0.5;entryX=1;entryY=0.5;"
    return (
        "edgeStyle=entityRelationEdgeStyle;curved=1;rounded=1;html=1;"
        "sketch=1;curveFitting=1;jiggle=2;startArrow=none;endArrow=none;"
        f"strokeColor={child.stroke};strokeWidth={width};{terminals}"
    )


def add_topic(graph_root: ET.Element, topic: Topic) -> None:
    attributes = {
        "id": topic.topic_id,
        "label": topic.text,
        "mindmapRole": "root" if topic.level == 0 else "topic",
        "mindmapLevel": str(topic.level),
        "mindmapSide": "center" if topic.level == 0 else topic.side,
    }
    if topic.path:
        attributes["mindmapParent"] = (
            "topic-root" if len(topic.path) == 1 else "topic-" + "-".join(str(part) for part in topic.path[:-1])
        )
    wrapper = ET.SubElement(graph_root, "object", attributes)
    cell = ET.SubElement(
        wrapper,
        "mxCell",
        {"style": node_style(topic), "vertex": "1", "parent": "1"},
    )
    ET.SubElement(
        cell,
        "mxGeometry",
        {
            "x": f"{topic.x - topic.width / 2:.1f}",
            "y": f"{topic.y - topic.height / 2:.1f}",
            "width": f"{topic.width:.1f}",
            "height": f"{topic.height:.1f}",
            "as": "geometry",
        },
    )


def add_edges(graph_root: ET.Element, topic: Topic) -> None:
    for child in topic.children:
        edge = ET.SubElement(
            graph_root,
            "mxCell",
            {
                "id": f"edge-{topic.topic_id}-{child.topic_id}",
                "style": edge_style(topic, child),
                "edge": "1",
                "parent": "1",
                "source": topic.topic_id,
                "target": child.topic_id,
            },
        )
        ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
        add_edges(graph_root, child)


def build_xml(root: Topic, page_width: int, page_height: int, page_name: str) -> str:
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "Agent",
            "agent": "mindmap-skill",
            "version": "31.1.5",
            "type": "device",
            "compressed": "false",
        },
    )
    diagram = ET.SubElement(mxfile, "diagram", {"id": "mindmap", "name": page_name})
    graph = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": str(page_width),
            "dy": str(page_height),
            "grid": "0",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": str(page_width),
            "pageHeight": str(page_height),
            "background": PAPER,
            "math": "0",
            "shadow": "0",
        },
    )
    graph_root = ET.SubElement(graph, "root")
    ET.SubElement(graph_root, "mxCell", {"id": "0"})
    ET.SubElement(graph_root, "mxCell", {"id": "1", "parent": "0"})
    for topic in walk_topics(root):
        add_topic(graph_root, topic)
    add_edges(graph_root, root)
    ET.indent(mxfile, space="  ")
    return ET.tostring(mxfile, encoding="unicode", xml_declaration=False) + "\n"


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.stem}.", suffix=".drawio", dir=path.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an editable sketch mind map as draw.io XML."
    )
    parser.add_argument("outline", type=Path, help="Input JSON outline")
    parser.add_argument("output", type=Path, help="Output .drawio file")
    parser.add_argument("--layout", choices=sorted(LAYOUTS), help="Override JSON layout")
    parser.add_argument("--page-name", default="Mindmap", help="draw.io page name")
    args = parser.parse_args()

    outline = args.outline.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.suffix.lower() != ".drawio":
        fail(f"output must use the .drawio extension: {output}")
    if not args.page_name.strip():
        fail("page name must not be empty")

    root, configured_layout = load_outline(outline)
    layout = args.layout or configured_layout
    measure(root)
    assign_branch_styles(root, layout)
    place_topics(root)
    page_width, page_height = shift_to_page(root)
    xml = build_xml(root, page_width, page_height, args.page_name.strip())
    write_atomic(output, xml)

    topics = list(walk_topics(root))
    print(
        json.dumps(
            {
                "source": str(outline),
                "output": str(output),
                "layout": layout,
                "node_count": len(topics),
                "edge_count": len(topics) - 1,
                "page_width": page_width,
                "page_height": page_height,
                "sides": {
                    side: sum(1 for topic in root.children if topic.side == side)
                    for side in ("left", "right")
                },
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
