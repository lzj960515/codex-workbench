#!/usr/bin/env python3
"""Inspect the hierarchy of a draw.io mind map or embedded-source PNG."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def drawio_skill_dir() -> Path:
    configured = os.environ.get("DRAWIO_SKILL_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "drawio"


def inspect_diagram(source: Path) -> dict[str, Any]:
    inspector = drawio_skill_dir() / "scripts" / "inspect_diagram.py"
    if not inspector.is_file():
        raise SystemExit(f"drawio inspector not found: {inspector}")
    completed = subprocess.run(
        [sys.executable, str(inspector), str(source)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise SystemExit(message or "drawio inspector failed")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise SystemExit(f"drawio inspector returned invalid JSON: {error}") from error


def build_page_outline(page: dict[str, Any]) -> dict[str, Any]:
    nodes = {node["id"]: node for node in page.get("nodes", [])}
    children: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    parent: dict[str, str] = {}
    cross_edges = []

    for edge in page.get("edges", []):
        source = edge.get("source")
        target = edge.get("target")
        if source not in nodes or target not in nodes:
            cross_edges.append({**edge, "reason": "endpoint is not a topic node"})
        elif target in parent:
            cross_edges.append({**edge, "reason": "target already has a tree parent"})
        else:
            parent[target] = source
            children[source].append(target)

    root_ids = [node_id for node_id in nodes if node_id not in parent]
    if "topic-root" in root_ids:
        root_ids.remove("topic-root")
        root_ids.insert(0, "topic-root")

    visited: set[str] = set()
    active: set[str] = set()
    warnings: list[str] = []

    def visit(node_id: str) -> dict[str, Any]:
        if node_id in active:
            warnings.append(f"cycle detected at {node_id}")
            return {"id": node_id, "label": nodes[node_id].get("label", ""), "cycle": True, "children": []}
        if node_id in visited:
            return {"id": node_id, "label": nodes[node_id].get("label", ""), "reference": True, "children": []}
        active.add(node_id)
        visited.add(node_id)
        result = {
            "id": node_id,
            "label": nodes[node_id].get("label", ""),
            "children": [visit(child_id) for child_id in children[node_id]],
        }
        active.remove(node_id)
        return result

    outline = [visit(root_id) for root_id in root_ids]
    unreachable = [node_id for node_id in nodes if node_id not in visited]
    if unreachable:
        warnings.append("unreachable or cyclic topics: " + ", ".join(unreachable))

    return {
        "id": page.get("id", ""),
        "name": page.get("name", ""),
        "root_ids": root_ids,
        "outline": outline,
        "cross_edges": cross_edges,
        "warnings": warnings,
    }


def markdown_topic(topic: dict[str, Any], depth: int) -> list[str]:
    label = topic.get("label") or topic.get("id") or "Untitled"
    suffix = " (cycle)" if topic.get("cycle") else ""
    if depth == 0:
        lines = [f"# {label}{suffix}"]
    else:
        lines = [f"{'  ' * (depth - 1)}- {label}{suffix}"]
    for child in topic.get("children", []):
        lines.extend(markdown_topic(child, depth + 1))
    return lines


def to_markdown(result: dict[str, Any]) -> str:
    blocks = []
    for page in result["pages"]:
        if len(result["pages"]) > 1:
            blocks.append(f"<!-- Page: {page['name']} -->")
        for root in page["outline"]:
            blocks.extend(markdown_topic(root, 0))
        if page["cross_edges"]:
            blocks.append("\n## Cross links")
            for edge in page["cross_edges"]:
                label = f" ({edge['label']})" if edge.get("label") else ""
                blocks.append(f"- {edge.get('source', '?')} -> {edge.get('target', '?')}{label}")
        if page["warnings"]:
            blocks.append("\n## Warnings")
            blocks.extend(f"- {warning}" for warning in page["warnings"])
        blocks.append("")
    return "\n".join(blocks).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect a draw.io mind map hierarchy from source or embedded PNG."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"mind map file not found: {source}")

    diagram = inspect_diagram(source)
    result = {
        "source": diagram.get("source", str(source)),
        "format": diagram.get("format", ""),
        "node_count": diagram.get("node_count", 0),
        "edge_count": diagram.get("edge_count", 0),
        "png": diagram.get("png"),
        "pages": [build_page_outline(page) for page in diagram.get("pages", [])],
    }
    if args.format == "markdown":
        print(to_markdown(result), end="")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
