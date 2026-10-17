#!/usr/bin/env python3
"""Record whether a SuperH C compiler is available. Do not invent one."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = (
    "sh-elf-gcc",
    "sh-elf-as",
    "sh-elf-ld",
    "sh4-elf-gcc",
    "sh4-linux-gnu-gcc",
    "sh4-linux-gnu-as",
    "shc",
    "ccsh",
)
ROM = Path.home() / "Documents/awbios/bios0.ic23"


def main():
    found = {name: shutil.which(name) for name in CANDIDATES}
    lines = [
        "# Compiler probe",
        "",
        "Hitachi SHC 5.1 Release 04 is pinned. See docs/compiler.md.",
        "This script only reports which compiler names are on PATH.",
        "It does not overwrite the pin.",
        "",
        "## What is installed",
        "",
    ]
    for name, path in found.items():
        lines.append(f"- `{name}`: {path or 'not on PATH'}")
    lines.extend([
        "",
        "Homebrew has no `sh-elf` formula. This probe does not build GCC and",
        "does not download an unpinned toolchain.",
        "",
    ])
    if ROM.is_file() and ROM.stat().st_size == 131072:
        rom = ROM.read_bytes()
        lines.append("## Probe bytes")
        lines.append("")
        lines.append(f"`0xA354`: `{rom[0xA354:0xA370].hex()}`")
        lines.append("")
        lines.append(f"`0xA370`: `{rom[0xA370:0xA3A0].hex()}`")
        lines.append("")
    text = "\n".join(lines)
    print(text)
    print("docs/compiler.md is the pin. This probe does not overwrite it.")


if __name__ == "__main__":
    main()
