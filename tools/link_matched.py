#!/usr/bin/env python3
"""Link FUN_09e34 with the pinned Hitachi SHC and keep those bytes.

The translation unit is the lo struct and FUN_09e34 from src/services.c.
Flags are -cpu=sh3 -endian=little -optimize=1. The H SERIES linker places
$G0 at 0, which fills the GBR+72 relocation. The 28 linked bytes are what
the image uses. A mismatch with bios0 fails the build.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sh4

ROOT = Path(__file__).resolve().parents[1]
PROBE = Path("/tmp/shc-probe")
BW = Path("/tmp/boxedwine/Boxedwine-open.app/Contents/MacOS/Boxedwine")
PIN_FLAGS = "-cpu=sh3 -endian=little -optimize=1"
REJECTED = ("-nospeed", "-speed", "-size", "-rtnext", "-cpu=sh4", "-optimize=0")
ENTRY = 0x9E34
SIZE = 28
SYMBOL = "FUN_09e34"


def slice_source(text):
    start = text.index("#pragma gbr_base (lo)")
    struct = text[start:text.index("} lo;", start) + len("} lo;")]
    fn_at = text.index("int FUN_09e34(void)")
    brace = text.index("{", fn_at)
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return struct + "\n\n" + text[fn_at:index + 1] + "\n"
    raise SystemExit("FUN_09e34 has no closing brace")


def extract_section(blob, size):
    symbol = b"_FUN_09e34"
    start = blob.find(symbol)
    if start < 0:
        raise SystemExit("linked absolute is missing _FUN_09e34")
    marker = size.to_bytes(4, "big")
    rel = blob.find(marker, start, start + 80)
    if rel < 0:
        raise SystemExit("linked section is not 28 bytes")
    data = blob[rel + 4:rel + 4 + size]
    if len(data) != size:
        raise SystemExit("linked section was truncated")
    return data


def compile_and_link(source_text):
    for flag in REJECTED:
        if flag in PIN_FLAGS:
            raise SystemExit(f"pin contains rejected flag {flag}")
    PROBE.joinpath("tmp").mkdir(exist_ok=True)
    PROBE.joinpath("out").mkdir(exist_ok=True)
    (PROBE / "f9e34.c").write_bytes(source_text.replace("\r\n", "\n").encode())
    bat = (
        f"e:\\lib\\shc.exe e:\\f9e34.c {PIN_FLAGS} -show=object -listfile=e:\\out\\f9e34.lst\r\n"
        "e:\\lib\\lnk.exe -subcommand=e:\\link_9e34.sub\r\n"
    )
    for flag in REJECTED:
        if flag in bat:
            raise SystemExit(f"link command contains rejected flag {flag}")
    (PROBE / "run_9e34.bat").write_bytes(bat.encode())
    sub = (
        "input e:\\f9e34.obj\r\n"
        "output e:\\f9e34.abs\r\n"
        "entry _FUN_09e34\r\n"
        "start P/0,$G0/0\r\n"
        "print e:\\f9e34.map\r\n"
        "exit\r\n"
    )
    (PROBE / "link_9e34.sub").write_bytes(sub.encode())
    abs_path = PROBE / "f9e34.abs"
    if abs_path.exists():
        abs_path.unlink()
    if not BW.is_file():
        raise SystemExit(f"Boxedwine is not at {BW}")
    cmd = [
        str(BW),
        "-root", "/tmp/boxedwine/shc-root",
        "-zip", "/tmp/boxedwine/TinyCore15Wine11.0.zip",
        "-nosound", "-ttyPrepend", "-dxvk", "0", "-resolution", "320x200",
        "-mount_drive", str(PROBE), "e",
        "-env", r"SHC_TMP=E:\tmp",
        "-env", r"SHC_INC=E:\inc",
        "-env", r"SHC_LIB=E:\lib",
        "-env", r"HLNK_TMP=E:\tmp",
        "-env", r"TEMP=E:\tmp",
        "-env", r"TMP=E:\tmp",
        "-w", "/mnt/drive_e",
        "/bin/wine", "cmd", "/c", r"e:\run_9e34.bat",
    ]
    ran = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if not abs_path.is_file():
        tail = (ran.stdout + ran.stderr)[-2000:]
        raise SystemExit(f"linker wrote no absolute file\n{tail}")
    return abs_path.read_bytes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=str(Path.home() / "Documents/awbios/bios0.ic23"))
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    rom = Path(args.rom).read_bytes()
    source = slice_source((ROOT / "src/services.c").read_text())
    if "FUN_09e34" not in source or "lo.l72" not in source:
        raise SystemExit("services.c no longer contains FUN_09e34")
    linked = extract_section(compile_and_link(source), SIZE)
    flash = rom[ENTRY:ENTRY + SIZE]
    if linked != flash:
        raise SystemExit(
            "FUN_09e34 linked bytes differ from flash: "
            + linked.hex()
        )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(sh4.write_elf(linked, SYMBOL, align=4))
    print(f"compiler: Hitachi SHC 5.1 Release 04, {PIN_FLAGS}")
    print("not re-flagged: -nospeed, -speed, -size, -rtnext, and -cpu=sh4 stay off")
    print(f"matched C: {SYMBOL} {SIZE} bytes at 0x{ENTRY:x}")
    print(linked.hex())


if __name__ == "__main__":
    main()
