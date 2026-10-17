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
        "No C is compiled in this tree. A unit is not a C match until one",
        "compiler and one flag set reproduce a real function, including the",
        "prologue, the delay slots, and the literal pool.",
        "",
        "The probe functions are file `0xA354` (28 bytes) and `0xA370` (48 bytes).",
        "Both save `pr` and both contain `bsr`. They are not the handwritten boot code.",
        "",
        "Candidates, in the order they should be tried once a binary exists:",
        "",
        "- Hitachi/Renesas SHC from the Dreamcast era",
        "- `sh-elf-gcc`",
        "",
        "Nothing below was pinned. `src/` stays empty.",
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
    out = ROOT / "docs/compiler.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(text)
    if any(found.values()):
        raise SystemExit("a compiler appeared; stop and pin it against 0xA354 before writing C")


if __name__ == "__main__":
    main()
