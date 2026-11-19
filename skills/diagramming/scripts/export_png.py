#!/usr/bin/env python3
"""Export a draw.io source file to a validated PNG artifact."""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

from drawio_cli import run_drawio


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def inspect_png(path: Path) -> tuple[int, int, bool]:
    with path.open("rb") as stream:
        if stream.read(8) != PNG_SIGNATURE:
            raise SystemExit(f"draw.io produced an invalid PNG: {path}")

        width = height = 0
        embeds_diagram = False

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
            elif chunk_type in {b"zTXt", b"tEXt"}:
                embeds_diagram = embeds_diagram or chunk_data.startswith(
                    b"mxGraphModel\x00"
                )
            elif chunk_type == b"IEND":
                break

    if width <= 0 or height <= 0:
        raise SystemExit(f"PNG has invalid dimensions: {path}")
    return width, height, embeds_diagram


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a .drawio file to PNG and validate the result."
    )
    parser.add_argument("source", type=Path, help="Input .drawio file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Output PNG path (default: source path with .png suffix)",
    )
    size = parser.add_mutually_exclusive_group()
    size.add_argument("--scale", type=float, help="Export scale (default: 2)")
    size.add_argument("--width", type=int, help="Fit the PNG to this width")
    parser.add_argument("--border", type=int, default=24, help="Border in pixels")
    parser.add_argument(
        "--theme", choices=("light", "dark", "auto"), default="light"
    )
    parser.add_argument("--page", type=int, help="1-based page index")
    parser.add_argument("--transparent", action="store_true")
    parser.add_argument(
        "--no-embed", action="store_true", help="Do not embed editable source XML"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source.expanduser().resolve()
    output = (args.output or source.with_suffix(".png")).expanduser().resolve()

    if not source.is_file():
        raise SystemExit(f"draw.io source file not found: {source}")
    if output.suffix.lower() != ".png":
        raise SystemExit(f"output must use the .png extension: {output}")
    if args.border < 0:
        raise SystemExit("--border must be zero or greater")
    if args.width is not None and args.width <= 0:
        raise SystemExit("--width must be greater than zero")
    if args.scale is not None and args.scale <= 0:
        raise SystemExit("--scale must be greater than zero")
    if args.page is not None and args.page <= 0:
        raise SystemExit("--page must be greater than zero")

    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.stem}.", suffix=".png", dir=output.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    temporary.unlink()

    command = [
        "--export",
        "--format",
        "png",
        "--output",
        str(temporary),
        "--border",
        str(args.border),
        "--theme",
        args.theme,
    ]
    if args.width is not None:
        command.extend(("--width", str(args.width)))
    else:
        command.extend(("--scale", str(args.scale or 2)))
    if args.page is not None:
        command.extend(("--page-index", str(args.page)))
    if args.transparent:
        command.append("--transparent")
    if not args.no_embed:
        command.append("--embed-diagram")
    command.append(str(source))

    try:
        run_drawio(command)
        if not temporary.is_file():
            raise SystemExit("draw.io exited successfully but produced no PNG")
        width, height, embeds_diagram = inspect_png(temporary)
        if not args.no_embed and not embeds_diagram:
            raise SystemExit("PNG does not contain the requested embedded diagram")
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)

    print(
        json.dumps(
            {
                "source": str(source),
                "output": str(output),
                "width": width,
                "height": height,
                "bytes": output.stat().st_size,
                "theme": args.theme,
                "embedded_diagram": embeds_diagram,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
