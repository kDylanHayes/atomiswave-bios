#!/usr/bin/env python3
"""Print matched C, byte-identical assembly, and unmatched code separately."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sh4

ROOT = Path(__file__).resolve().parents[1]
ROM = Path.home() / "Documents/awbios/bios0.ic23"
CLI = ROOT / "tools/bin/objdiff-cli"


def rom_check(rom):
    matched = []
    for name in ("poll_bit", "copy_words", "mix_shifts"):
        origin, data, _symbol = sh4.assemble((ROOT / "asm/boot" / f"{name}.s").read_text())
        sh4.check_against_rom(origin, data, rom)
        matched.append((name, origin, len(data)))
    return matched


def main():
    rom = ROM.read_bytes()
    payload = json.loads((ROOT / "asm/map.json").read_text())
    matched = rom_check(rom)
    matched_bytes = sum(size for _name, _origin, size in matched)
    code = payload["functions"]
    code_bytes = sum(fn["size"] for fn in code)
    asm_bytes = sum(fn["size"] for fn in code if fn["kind"] == "asm")
    compiled_bytes = sum(fn["size"] for fn in code if fn["kind"] == "compiled")
    # Linked with SHC outside this tree ($G0 at 0). make progress does not re-run it.
    c_matched = [("FUN_09e34", 0x9E34, 28)]
    c_bytes = sum(size for _name, _origin, size in c_matched)
    print("compiler: Hitachi SHC 5.1 Release 04, -cpu=sh3 -endian=little -optimize=1")
    print(
        "matched C: "
        + ", ".join(f"{name} {size} bytes at 0x{origin:x}" for name, origin, size in c_matched)
    )
    c_noun = "function" if len(c_matched) == 1 else "functions"
    print(f"matched C total: {len(c_matched)} {c_noun}, {c_bytes} bytes")
    print("matched C was linked with SHC; make progress does not re-run the compiler")
    print(
        "byte-identical assembly: "
        + ", ".join(f"{name} {size} bytes at 0x{origin:x}" for name, origin, size in matched)
    )
    print(f"byte-identical assembly total: {len(matched)} functions, {matched_bytes} bytes")
    print(
        f"unmatched code: {len(code) - len(matched) - len(c_matched)} functions, "
        f"{code_bytes - matched_bytes - c_bytes} bytes"
    )
    print(f"split: asm {asm_bytes} bytes, compiled {compiled_bytes} bytes, data listed separately")
    print("objdiff complete: false on every unit")
    for name in ("poll_bit", "copy_words", "mix_shifts"):
        built = (ROOT / "build/asm/boot" / f"{name}.o").read_bytes()
        expected = (ROOT / "expected/boot" / f"{name}.o").read_bytes()
        if built != expected:
            raise SystemExit(f"{name}: built object is not the extracted object")
    print("built ELF matches extracted ELF for the three assembly units")
    if not CLI.is_file():
        print("objdiff-cli is not installed at tools/bin/objdiff-cli")
        return
    report = subprocess.run(
        [str(CLI), "report", "generate", "-p", str(ROOT), "-f", "json"],
        check=False,
        capture_output=True,
        text=True,
    )
    if report.returncode != 0:
        print("objdiff report failed")
        print(report.stderr.strip())
        return
    print("objdiff report ran. The percent is not used. See docs/objdiff.md.")


if __name__ == "__main__":
    main()
