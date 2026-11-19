#!/usr/bin/env python3
"""Convert Mermaid source into editable, uncompressed draw.io XML."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.dont_write_bytecode = True

from drawio_cli import run_drawio


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Mermaid into native editable draw.io elements."
    )
    parser.add_argument("source", type=Path, help="Input .mmd or .mermaid file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Output .drawio path (default: source path with .drawio suffix)",
    )
    return parser.parse_args()


def prepare_output(path: Path, page_name: str) -> tuple[int, int, int]:
    try:
        tree = ET.parse(path)
    except ET.ParseError as error:
        raise SystemExit(f"draw.io produced invalid XML: {error}") from error

    root = tree.getroot()
    diagrams = root.findall("diagram") if root.tag == "mxfile" else []
    pages = len(diagrams) if diagrams else 1
    if len(diagrams) == 1:
        diagrams[0].set("name", page_name)
        ET.indent(tree, space="  ")
        tree.write(path, encoding="unicode")

    nodes = sum(cell.get("vertex") == "1" for cell in root.iter("mxCell"))
    edges = sum(cell.get("edge") == "1" for cell in root.iter("mxCell"))
    if nodes == 0:
        raise SystemExit("conversion produced no editable draw.io nodes")
    return pages, nodes, edges


def main() -> None:
    args = parse_args()
    source = args.source.expanduser().resolve()
    output = (args.output or source.with_suffix(".drawio")).expanduser().resolve()

    if not source.is_file():
        raise SystemExit(f"Mermaid source file not found: {source}")
    if source.suffix.lower() not in {".mmd", ".mermaid"}:
        raise SystemExit(f"input must use .mmd or .mermaid: {source}")
    if output.suffix.lower() != ".drawio":
        raise SystemExit(f"output must use the .drawio extension: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.stem}.", suffix=".drawio", dir=output.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    temporary.unlink()

    try:
        run_drawio(
            [
                "--export",
                "--format",
                "xml",
                "--uncompressed",
                "--output",
                str(temporary),
                str(source),
            ]
        )
        if not temporary.is_file():
            raise SystemExit("draw.io exited successfully but produced no source file")
        pages, nodes, edges = prepare_output(temporary, output.stem)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)

    print(
        json.dumps(
            {
                "source": str(source),
                "output": str(output),
                "pages": pages,
                "editable_nodes": nodes,
                "editable_edges": edges,
                "bytes": output.stat().st_size,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
