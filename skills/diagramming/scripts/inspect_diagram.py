#!/usr/bin/env python3
"""Inspect draw.io XML or a PNG containing embedded draw.io source."""

from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import struct
import tempfile
import urllib.parse
import zlib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
TAG_PATTERN = re.compile(r"<[^>]+>")
SPACE_PATTERN = re.compile(r"\s+")


def clean_label(value: str | None) -> str:
    if not value:
        return ""
    text = value.replace("<br>", " ").replace("<br/>", " ")
    text = TAG_PATTERN.sub(" ", text)
    return SPACE_PATTERN.sub(" ", html.unescape(text)).strip()


def read_png_xml(path: Path) -> tuple[str, dict[str, Any]]:
    with path.open("rb") as stream:
        if stream.read(8) != PNG_SIGNATURE:
            raise SystemExit(f"not a valid PNG: {path}")

        width = height = 0
        embedded_xml: str | None = None
        while True:
            length_bytes = stream.read(4)
            if not length_bytes:
                break
            length = struct.unpack(">I", length_bytes)[0]
            chunk_type = stream.read(4)
            chunk_data = stream.read(length)
            stream.read(4)

            if chunk_type == b"IHDR":
                width, height = struct.unpack(">II", chunk_data[:8])
            elif chunk_type == b"zTXt" and chunk_data.startswith(
                b"mxGraphModel\x00"
            ):
                payload = chunk_data.split(b"\x00", 1)[1]
                if not payload or payload[0] != 0:
                    raise SystemExit("unsupported PNG text compression method")
                encoded = zlib.decompress(payload[1:]).decode("utf-8")
                embedded_xml = urllib.parse.unquote(encoded)
            elif chunk_type == b"tEXt" and chunk_data.startswith(
                b"mxGraphModel\x00"
            ):
                encoded = chunk_data.split(b"\x00", 1)[1].decode("utf-8")
                embedded_xml = urllib.parse.unquote(encoded)
            elif chunk_type == b"IEND":
                break

    if embedded_xml is None:
        raise SystemExit("PNG does not contain embedded draw.io source")
    return embedded_xml, {"width": width, "height": height, "embedded": True}


def decode_diagram(diagram: ET.Element) -> ET.Element:
    graph = diagram.find("mxGraphModel")
    if graph is not None:
        return graph

    payload = (diagram.text or "").strip()
    if not payload:
        raise SystemExit(f"diagram {diagram.get('name', '')!r} has no graph data")
    try:
        compressed = base64.b64decode(payload)
        encoded = zlib.decompress(compressed, -15).decode("utf-8")
        return ET.fromstring(urllib.parse.unquote(encoded))
    except (ValueError, zlib.error, ET.ParseError) as error:
        raise SystemExit(
            f"cannot decode diagram {diagram.get('name', '')!r}: {error}"
        ) from error


def shape_from_style(style: str) -> str:
    fields = {}
    for part in style.split(";"):
        if "=" in part:
            key, value = part.split("=", 1)
            fields[key] = value
        elif part:
            fields[part] = "1"

    if fields.get("container") == "1":
        return "container"
    if "shape" in fields:
        return fields["shape"]
    for name in ("swimlane", "group", "ellipse", "rhombus", "cylinder"):
        if name in fields:
            return name
    return "rectangle"


def geometry_of(cell: ET.Element) -> dict[str, float]:
    geometry = cell.find("mxGeometry")
    if geometry is None:
        return {}

    result: dict[str, float] = {}
    for field in ("x", "y", "width", "height"):
        value = geometry.get(field)
        if value is not None:
            try:
                result[field] = float(value)
            except ValueError:
                continue
    return result


def inspect_graph(graph: ET.Element) -> dict[str, Any]:
    parent_by_child = {child: parent for parent in graph.iter() for child in parent}
    nodes = []
    edges = []

    for cell in graph.iter("mxCell"):
        if cell.get("vertex") != "1" and cell.get("edge") != "1":
            continue

        wrapper = parent_by_child.get(cell)
        wrapper_is_metadata = wrapper is not None and wrapper.tag in {
            "object",
            "UserObject",
        }
        element_id = (
            wrapper.get("id") if wrapper_is_metadata else cell.get("id")
        ) or cell.get("id", "")
        raw_label = (
            wrapper.get("label") or wrapper.get("value")
            if wrapper_is_metadata
            else cell.get("value")
        )

        if cell.get("vertex") == "1":
            style = cell.get("style", "")
            nodes.append(
                {
                    "id": element_id,
                    "label": clean_label(raw_label),
                    "parent": cell.get("parent", ""),
                    "shape": shape_from_style(style),
                    "geometry": geometry_of(cell),
                }
            )
        else:
            edges.append(
                {
                    "id": element_id,
                    "label": clean_label(raw_label),
                    "source": cell.get("source", ""),
                    "target": cell.get("target", ""),
                }
            )

    return {"nodes": nodes, "edges": edges}


def inspect_xml(xml: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as error:
        raise SystemExit(f"invalid draw.io XML: {error}") from error

    if root.tag == "mxGraphModel":
        return [{"id": "", "name": "Page 1", **inspect_graph(root)}]
    if root.tag != "mxfile":
        raise SystemExit(f"unsupported draw.io XML root: {root.tag}")

    pages = []
    for index, diagram in enumerate(root.findall("diagram"), start=1):
        pages.append(
            {
                "id": diagram.get("id", ""),
                "name": diagram.get("name") or f"Page {index}",
                **inspect_graph(decode_diagram(diagram)),
            }
        )
    if not pages:
        raise SystemExit("draw.io file contains no pages")
    return pages


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect draw.io XML or embedded source in a PNG."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--extract",
        type=Path,
        help="Restore embedded PNG source to an uncompressed .drawio file",
    )
    args = parser.parse_args()
    source = args.source.expanduser().resolve()

    if not source.is_file():
        raise SystemExit(f"diagram file not found: {source}")

    png = None
    if source.suffix.lower() == ".png":
        xml, png = read_png_xml(source)
    else:
        xml = source.read_text(encoding="utf-8")

    pages = inspect_xml(xml)
    extracted_to = None
    if args.extract is not None:
        if png is None:
            raise SystemExit("--extract is only supported for PNG input")
        extracted_to = args.extract.expanduser().resolve()
        if extracted_to.suffix.lower() != ".drawio":
            raise SystemExit(f"extracted output must use .drawio: {extracted_to}")
        extracted_to.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{extracted_to.stem}.",
            suffix=".drawio",
            dir=extracted_to.parent,
        )
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            temporary.write_text(xml, encoding="utf-8")
            temporary.replace(extracted_to)
        finally:
            temporary.unlink(missing_ok=True)

    result = {
        "source": str(source),
        "format": "embedded-png" if png else "drawio-xml",
        "page_count": len(pages),
        "node_count": sum(len(page["nodes"]) for page in pages),
        "edge_count": sum(len(page["edges"]) for page in pages),
        "pages": pages,
    }
    if png:
        result["png"] = png
    if extracted_to:
        result["extracted_to"] = str(extracted_to)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
