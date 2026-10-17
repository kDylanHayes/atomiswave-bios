#!/usr/bin/env python3
"""Write expected ELF objects and objdiff.json from asm/map.json.

complete stays false. objdiff 3.8.2 disassembles SuperH as big-endian, so a
100% report on these little-endian objects is not a match. See docs/objdiff.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sh4

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=str(Path.home() / "Documents/awbios/bios0.ic23"))
    parser.add_argument("--map", default=str(ROOT / "asm/map.json"))
    args = parser.parse_args()
    rom = Path(args.rom).read_bytes()
    payload = json.loads(Path(args.map).read_text())
    if payload["sha1"] != hashlib.sha1(rom).hexdigest():
        raise SystemExit("map sha1 does not match the ROM")
    units = []
    for fn in payload["functions"]:
        data = rom[fn["entry"]:fn["end"]]
        align = 4 if fn["entry"] % 4 == 0 else 2
        blob = sh4.write_elf(data, fn["name"], align=align)
        target = ROOT / "expected" / fn["category"] / f"{fn['name']}.o"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        unit = {
            "name": f"{fn['category']}/{fn['name']}",
            "target_path": str(target.relative_to(ROOT)),
            "metadata": {
                "complete": False,
                "progress_categories": [fn["category"]],
            },
        }
        if fn.get("source"):
            unit["base_path"] = f"build/{fn['source'].replace('.s', '.o')}"
            unit["metadata"]["source_path"] = fn["source"]
        units.append(unit)
    config = {
        "$schema": "https://raw.githubusercontent.com/encounter/objdiff/main/config.schema.json",
        "min_version": "3.0.0",
        "custom_make": "make",
        "build_target": False,
        "build_base": True,
        "watch_patterns": ["*.s", "*.c", "*.h", "*.py"],
        "progress_categories": [
            {"id": "boot", "name": "Boot assembly"},
            {"id": "services", "name": "ABI-shaped services"},
        ],
        "units": units,
    }
    (ROOT / "objdiff.json").write_text(json.dumps(config, indent=2) + "\n")
    print(f"units {len(units)}  with source {sum(1 for u in units if 'base_path' in u)}")


if __name__ == "__main__":
    main()
