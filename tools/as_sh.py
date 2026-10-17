#!/usr/bin/env python3
"""Assemble one GNU-as subset file and write an ELF32 SH-4 object.

The bytes are checked against the ROM when --check is given. A match here
is a byte-identical assembly unit. It is not a C match.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sh4


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--check", help="ROM image to compare against .org")
    args = parser.parse_args()
    text = Path(args.source).read_text()
    origin, data, symbol = sh4.assemble(text)
    if args.check:
        rom = Path(args.check).read_bytes()
        sh4.check_against_rom(origin, data, rom)
    align = 4 if origin % 4 == 0 else 2
    blob = sh4.write_elf(data, symbol, align=align)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(blob)


if __name__ == "__main__":
    main()
