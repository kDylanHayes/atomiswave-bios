#!/usr/bin/env python3
"""Compile one C function with the pinned SHC and compare with the flash.

usage:
    probe_function.py SOURCE.c ENTRY FLASH_ADDR SIZE [--define SYM=HEX]...

SOURCE.c is compiled with the pin, linked as one object with section P at
0, run through rof2bin, and the first SIZE bytes are compared with the
flash slice at FLASH_ADDR (file offset = address). Nothing in build/ is
touched and no unit is claimed.

--define SYM=HEX adds a DEFINE subcommand line. The H SERIES linker can
force an import symbol to an address, so an extern call through a fixed
RAM address keeps one literal per call site instead of caching the
address in a callee-saved register.

Exit status is 0 when the bytes match and 1 when they differ.

    probe_function.py --selftest

compiles the reject_code unit at 0x9E34 and checks its 28 bytes. That
unit needs no distance fillers, so it is the tool's own check.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import link_matched as lm

ROM = Path.home() / "Documents" / "awbios" / "bios0.ic23"
TAG = "probe_one"

REJECT = """\
#include <machine.h>

#pragma gbr_base (lo)
struct {
    char b0;
    char pad1[35];
    char flag_36;
    char flag_37;
    char flag_38;
    char pad39[9];
    int word_48;
    char pad52[12];
    int saved_64;
    short count_68;
    short count_70;
    int code_72;
    int word_76;
    char pad80[20];
    int ptr_100;
    char pad104[24];
} lo;

int reject_code(void)
{
    int r;

    switch (lo.code_72) {
    case 6:
    case 7:
    case 9:
        r = -1;
        break;
    default:
        r = 0;
        break;
    }
    return r;
}
"""


def run(source: str, entry: str, addr: int, size: int, defines: list[str]):
    if not ROM.is_file():
        raise SystemExit(f"flash is not at {ROM}")
    lm.stage_tools()
    stage = lm.STAGE
    (stage / f"{TAG}.c").write_bytes(source.replace("\r\n", "\n").encode())
    lines = [
        f"c:\\probe\\lib\\shc.exe c:\\probe\\{TAG}.c {lm.PIN_FLAGS} "
        f"-show=object -listfile=c:\\probe\\out\\{TAG}.lst",
        f"c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_{TAG}.sub",
        f"c:\\probe\\lib\\rof2bin.exe -q -s=0 -e={size:X} c:\\probe\\{TAG}.abs",
    ]
    (stage / f"run_{TAG}.bat").write_bytes(("\r\n".join(lines) + "\r\n").encode())
    sub = [
        f"input c:\\probe\\{TAG}.obj",
        f"output c:\\probe\\{TAG}.abs",
        *defines,
        f"entry _{entry}",
        "start P/0,$G0/0",
        f"print c:\\probe\\{TAG}.map",
        "exit",
    ]
    (stage / f"link_{TAG}.sub").write_bytes(("\r\n".join(sub) + "\r\n").encode())
    for name in (f"{TAG}.abs", f"{TAG}.bin"):
        path = stage / name
        if path.exists():
            path.unlink()
    cmd = [
        str(lm.BW), "-root", str(lm.ROOT_FS), "-zip", str(lm.WINE_ZIP),
        "-nosound", "-novideo", "-ttyPrepend", "-dxvk", "0",
        "-resolution", "320x200",
        "-env", r"SHC_TMP=C:\probe\tmp", "-env", r"SHC_INC=C:\probe\inc",
        "-env", r"SHC_LIB=C:\probe\lib", "-env", r"HLNK_TMP=C:\probe\tmp",
        "-env", r"TEMP=C:\probe\tmp", "-env", r"TMP=C:\probe\tmp",
        "-w", "/home/username/.wine/drive_c/probe",
        "/bin/wine", "cmd", "/c", f"c:\\probe\\run_{TAG}.bat",
    ]
    ran = subprocess.run(cmd, check=False, capture_output=True, text=True)
    out = stage / f"{TAG}.bin"
    if not out.is_file():
        listing = stage / "out" / f"{TAG}.lst"
        tail = ""
        if listing.is_file():
            tail = "\n".join(
                line for line in listing.read_text(errors="replace").splitlines()
                if "(E)" in line or "(F)" in line
            )
        raise SystemExit(
            "no binary produced"
            + (f"\n{tail}" if tail else "")
            + f"\n{(ran.stdout or '')[-1500:]}"
        )
    got = out.read_bytes()
    flash = ROM.read_bytes()[addr:addr + size]
    return got, flash


def report(got: bytes, flash: bytes, addr: int, size: int) -> bool:
    n = min(len(got), len(flash))
    diff = [i for i in range(n) if got[i] != flash[i]]
    print(f"got   {got.hex()}")
    print(f"flash {flash.hex()}")
    print(f"size {len(got)} diffs {len(diff)} of {n}")
    if diff:
        first = diff[0]
        print(f"first +0x{first:X} at 0x{addr + first:X}: "
              f"got {got[first]:02X}, flash {flash[first]:02X}")
        return False
    print(f"match: {size} bytes at 0x{addr:X}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", nargs="?")
    parser.add_argument("entry", nargs="?")
    parser.add_argument("addr", nargs="?")
    parser.add_argument("size", nargs="?")
    parser.add_argument("--define", action="append", default=[],
                        metavar="SYM=HEX", help="DEFINE an import symbol")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        got, flash = run(REJECT, "reject_code", 0x9E34, 28, [])
        return 0 if report(got, flash, 0x9E34, 28) else 1

    if not (args.source and args.entry and args.addr and args.size):
        parser.error("SOURCE.c, ENTRY, FLASH_ADDR, and SIZE are required")
    source = Path(args.source).read_text()
    addr = int(args.addr, 16)
    size = int(args.size, 16)
    defines = []
    for item in args.define:
        if "=" not in item:
            parser.error(f"--define wants SYM=HEX, got {item}")
        sym, value = item.split("=", 1)
        defines.append(f"DEFINE {sym}({value})")
    got, flash = run(source, args.entry, addr, size, defines)
    return 0 if report(got, flash, addr, size) else 1


if __name__ == "__main__":
    raise SystemExit(main())
