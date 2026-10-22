#!/usr/bin/env python3
"""Byte gate for the bios0 image.

Every code range is either linked C or checked assembly. Hole and footer
bytes come from their assembly objects. Font, tables, and padding are copied
from the ROM only where no object was placed. A built object whose .text
differs from flash fails this command. The same object's ELF wrapper must
equal write_elf of those flash bytes.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sh4
from link_matched import PIN_FLAGS, REJECTED

ROOT = Path(__file__).resolve().parents[1]
ROM_PATH = Path.home() / "Documents/awbios/bios0.ic23"
SHA1 = "b4c1a26bc8906d5275eb28c701dff2b9365bcdfa"
IMAGE = ROOT / "build/bios0.ic23"


def object_for(item):
    if item.get("object"):
        return ROOT / item["object"]
    source = item.get("source")
    if source and source.endswith(".s"):
        return ROOT / "build" / (source[:-2] + ".o")
    return None


def text_of(path, lo, hi):
    if not path.is_file():
        raise SystemExit(f"missing built object {path}")
    blob = path.read_bytes()
    data = sh4.elf_text(blob)
    if len(data) != hi - lo:
        raise SystemExit(f"{path.name}: .text is {len(data)} bytes, flash span is {hi - lo}")
    return blob, data


def place(image, covered, origin, data, label):
    for offset, byte in enumerate(data):
        index = origin + offset
        if covered[index]:
            raise SystemExit(f"{label} overlaps another object at {index:#x}")
        image[index] = byte
        covered[index] = 1


def main():
    for flag in REJECTED:
        if flag in PIN_FLAGS:
            raise SystemExit(f"pin contains rejected flag {flag}")
    rom = ROM_PATH.read_bytes()
    if hashlib.sha1(rom).hexdigest() != SHA1 or len(rom) != 131072:
        raise SystemExit("ROM is not bios0")
    payload = json.loads((ROOT / "asm/map.json").read_text())
    image = bytearray(len(rom))
    covered = bytearray(len(rom))
    c_matched = []
    asm_matched = []
    relocations = 0
    for fn in payload["functions"]:
        path = object_for(fn)
        if path is None:
            raise SystemExit(f"{fn['name']} has no built object")
        blob, data = text_of(path, fn["entry"], fn["end"])
        flash = rom[fn["entry"]:fn["end"]]
        if data != flash:
            raise SystemExit(f"{fn['name']}: built object does not match flash at {fn['entry']:#x}")
        align = 4 if fn["entry"] % 4 == 0 else 2
        if blob != sh4.write_elf(flash, fn["name"], align=align):
            raise SystemExit(f"{fn['name']}: built ELF does not wrap the flash bytes")
        relocations += sh4.elf_relocation_count(blob)
        place(image, covered, fn["entry"], data, fn["name"])
        if fn.get("matched_c"):
            c_matched.append(fn)
        else:
            asm_matched.append(fn)
    for item in payload["data"]:
        path = object_for(item)
        if path is None:
            raise SystemExit(f"{item['name']} has no assembly object")
        _blob, data = text_of(path, item["entry"], item["end"])
        if data != rom[item["entry"]:item["end"]]:
            raise SystemExit(f"{item['name']}: data object does not match flash")
        place(image, covered, item["entry"], data, item["name"])
    missing = [
        fn["name"]
        for fn in payload["functions"]
        if sum(covered[fn["entry"]:fn["end"]]) != fn["end"] - fn["entry"]
    ]
    if missing or len(c_matched) + len(asm_matched) != len(payload["functions"]):
        raise SystemExit("a code range was not placed from a built object: " + ", ".join(missing))
    for index, flag in enumerate(covered):
        if not flag:
            image[index] = rom[index]
    digest = hashlib.sha1(image).hexdigest()
    IMAGE.parent.mkdir(parents=True, exist_ok=True)
    IMAGE.write_bytes(image)
    c_bytes = sum(fn["end"] - fn["entry"] for fn in c_matched)
    asm_bytes = sum(fn["end"] - fn["entry"] for fn in asm_matched)
    print(f"compiler: Hitachi SHC 5.1 Release 04, {PIN_FLAGS}")
    print("not re-flagged: -nospeed, -speed, -size, -rtnext, and -cpu=sh4 stay off")
    print(
        "matched C: "
        + ", ".join(f"{fn['name']} {fn['end'] - fn['entry']} bytes at 0x{fn['entry']:x}" for fn in c_matched)
    )
    noun = "function" if len(c_matched) == 1 else "functions"
    print(f"matched C total: {len(c_matched)} {noun}, {c_bytes} bytes")
    print(
        "byte-identical assembly: "
        + ", ".join(f"{fn['name']} {fn['end'] - fn['entry']} bytes at 0x{fn['entry']:x}" for fn in asm_matched)
    )
    print(f"byte-identical assembly total: {len(asm_matched)} functions, {asm_bytes} bytes")
    unplaced_bytes = sum(
        (fn["end"] - fn["entry"]) - sum(covered[fn["entry"]:fn["end"]])
        for fn in payload["functions"]
    )
    print(f"unplaced code: {len(missing)} functions, {unplaced_bytes} bytes")
    print(
        f"built ELF wraps the flash bytes for {len(c_matched) + len(asm_matched)} code units"
    )
    print(f"image sha1: {digest}")
    if digest != SHA1:
        raise SystemExit(f"image sha1 {digest} does not match bios0")
    print(f"relocation entries: {relocations}")


if __name__ == "__main__":
    main()
