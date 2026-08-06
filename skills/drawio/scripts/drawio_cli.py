#!/usr/bin/env python3
"""Shared helpers for invoking the installed draw.io Desktop CLI."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Sequence


MACOS_DRAWIO = Path("/Applications/draw.io.app/Contents/MacOS/draw.io")


def find_drawio() -> str:
    command = shutil.which("drawio")
    if command:
        return command
    if MACOS_DRAWIO.is_file():
        return str(MACOS_DRAWIO)
    raise SystemExit(
        "drawio command not found. On macOS, install it with: "
        "brew install --cask drawio"
    )


def run_drawio(arguments: Sequence[str]) -> None:
    command = [find_drawio(), "--disable-update", *arguments]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        return

    detail = result.stderr.strip() or result.stdout.strip() or "no diagnostic output"
    raise SystemExit(f"draw.io failed with exit code {result.returncode}: {detail}")
