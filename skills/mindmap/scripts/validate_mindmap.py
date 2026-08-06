#!/usr/bin/env python3
"""Validate a mind map source and its embedded-source PNG artifact."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def drawio_skill_dir() -> Path:
    configured = os.environ.get("DRAWIO_SKILL_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return skill_dir().parent / "drawio"


def run_json(command: list[str], operation: str) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise SystemExit(message or f"{operation} failed")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise SystemExit(f"{operation} returned invalid JSON: {error}") from error


def inspect_hierarchy(source: Path) -> dict[str, Any]:
    inspector = skill_dir() / "scripts" / "inspect_mindmap.py"
    return run_json(
        [sys.executable, str(inspector), str(source), "--format", "json"],
        f"mind map inspection for {source}",
    )


def extract_png(png: Path, output: Path) -> dict[str, Any]:
    inspector = drawio_skill_dir() / "scripts" / "inspect_diagram.py"
    if not inspector.is_file():
        raise SystemExit(f"drawio inspector not found: {inspector}")
    return run_json(
        [sys.executable, str(inspector), str(png), "--extract", str(output)],
        f"embedded PNG extraction for {png}",
    )


def validate_pages(hierarchy: dict[str, Any], label: str) -> list[str]:
    failures = []
    pages = hierarchy.get("pages", [])
    if not pages:
        return [f"{label} contains no pages"]
    for page in pages:
        name = page.get("name") or page.get("id") or "unnamed page"
        roots = page.get("root_ids", [])
        if len(roots) != 1:
            failures.append(f"{label} page {name!r} must have one root topic, found {len(roots)}")
        for warning in page.get("warnings", []):
            failures.append(f"{label} page {name!r}: {warning}")
    return failures


def page_summary(hierarchy: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for page in hierarchy.get("pages", []):
        outline = page.get("outline", [])
        root_label = outline[0].get("label", "") if outline else ""
        result.append(
            {
                "name": page.get("name", ""),
                "root": root_label,
                "cross_edge_count": len(page.get("cross_edges", [])),
            }
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate structure, source synchronization, and embedded PNG metadata."
    )
    parser.add_argument("source", type=Path, help="Authoritative .drawio source")
    parser.add_argument("png", type=Path, nargs="?", help="PNG artifact; defaults to the source basename")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    png = (args.png or source.with_suffix(".png")).expanduser().resolve()
    if source.suffix.lower() != ".drawio":
        raise SystemExit(f"source must use the .drawio extension: {source}")
    if png.suffix.lower() != ".png":
        raise SystemExit(f"artifact must use the .png extension: {png}")
    if not source.is_file():
        raise SystemExit(f"mind map source not found: {source}")
    if not png.is_file():
        raise SystemExit(f"mind map PNG not found: {png}")

    source_hierarchy = inspect_hierarchy(source)
    png_hierarchy = inspect_hierarchy(png)
    failures = validate_pages(source_hierarchy, "source")
    failures.extend(validate_pages(png_hierarchy, "PNG"))

    if source_hierarchy.get("node_count", 0) <= 0:
        failures.append("source contains no topic nodes")
    if source_hierarchy.get("node_count") != png_hierarchy.get("node_count"):
        failures.append("source and PNG node counts differ")
    if source_hierarchy.get("edge_count") != png_hierarchy.get("edge_count"):
        failures.append("source and PNG edge counts differ")

    png_metadata = png_hierarchy.get("png") or {}
    if not png_metadata.get("embedded"):
        failures.append("PNG does not contain embedded draw.io source")

    with tempfile.TemporaryDirectory(prefix="mindmap-validate-") as temporary:
        extracted = Path(temporary) / "embedded.drawio"
        extract_png(png, extracted)
        source_matches_png = source.read_bytes() == extracted.read_bytes()
    if not source_matches_png:
        failures.append("PNG embedded source does not match the authoritative .drawio file")

    if failures:
        raise SystemExit("mind map validation failed:\n- " + "\n- ".join(failures))

    print(
        json.dumps(
            {
                "valid": True,
                "source": str(source),
                "png": str(png),
                "node_count": source_hierarchy["node_count"],
                "edge_count": source_hierarchy["edge_count"],
                "page_count": len(source_hierarchy["pages"]),
                "pages": page_summary(source_hierarchy),
                "width": png_metadata.get("width", 0),
                "height": png_metadata.get("height", 0),
                "embedded_diagram": True,
                "source_matches_png": True,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
