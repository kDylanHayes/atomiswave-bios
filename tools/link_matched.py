#!/usr/bin/env python3
"""Link the matched service functions with the pinned Hitachi SHC.

reject_code is its own unit. $G0 at 0 fills the GBR+72 relocation.

retry_issue and run_transfer share one unit. A bsr displacement is fixed
at compile time, so the static callees have to sit at the flash distances.
hole_09cdc, prime_count68, and issue_command are 4-byte stubs in that unit.
317 and 95 unreferenced global empty functions fill the gaps. The real
bodies of those callees stay assembly. rof2bin pulls section P out of the
absolute file. -e is an exclusive end address. The slices are compared
with bios0 before any object is written.

The H SERIES linker prints ** 202 on `start P/0,$G0/0` and still writes
the absolute file. That line stays. The pin flags stay.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sh4

ROOT = Path(__file__).resolve().parents[1]
# Local drop, not the git repo. bios0.ic23 is the flash. The Hitachi tools
# are extracted from the Katana R9 cab in the same folder.
LOCAL = Path.home() / "Documents" / "awbios"
SHC_LIB = LOCAL / "shc" / "UtlDevHitachi"
SHC_INC = LOCAL / "shc" / "Include"
RUNNER = LOCAL / "boxedwine"
ROOT_FS = RUNNER / "shc-root"
# Boxedwine's host mount refuses DeleteFile, and SHC error 3304 stops the
# compile when a temp file cannot be removed. The prefix C: drive can.
STAGE = ROOT_FS / "home/username/.wine/drive_c/probe"
BW = RUNNER / "Boxedwine-open.app" / "Contents" / "MacOS" / "Boxedwine"
WINE_ZIP = RUNNER / "TinyCore15Wine11.0.zip"
PIN_FLAGS = "-cpu=sh3 -endian=little -optimize=1"
REJECTED = ("-nospeed", "-speed", "-size", "-rtnext", "-cpu=sh4", "-optimize=0")

# Flash addresses. Section P of the distance unit starts at hole_09cdc.
HOLE = 0x9CDC
PRIME = 0xA1D4
RETRY = 0xA354
RUN = 0xA370
ISSUE = 0xA3A0
STUB = 4
RETRY_SIZE = 28
RUN_SIZE = 48
REJECT_ENTRY = 0x9E34
REJECT_SIZE = 28


def section_off(addr):
    return addr - HOLE


def function_at(text, signature):
    fn_at = text.index(signature)
    brace = text.index("{", fn_at)
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[fn_at:index + 1]
    raise SystemExit(f"{signature} has no closing brace")


def slice_reject(text):
    start = text.index("#pragma gbr_base (lo)")
    struct = text[start:text.index("} lo;", start) + len("} lo;")]
    return struct + "\n\n" + function_at(text, "int reject_code(void)") + "\n"


def empty_function(name, static):
    prefix = "static " if static else ""
    return f"{prefix}void {name}(void)\n{{\n}}\n\n"


def distance_unit(text):
    """One translation unit whose bsr sites match 0xA354 and 0xA370.

    Layout, with hole_09cdc at section offset 0:
      4-byte hole, 317 global pads, 4-byte prime, 95 global pads,
      static retry_issue (28 bytes), run_transfer (48 bytes),
      4-byte issue_command.
    Unreferenced globals are kept in source order. Unreferenced statics
    are deleted, so retry_issue stays static and run_transfer calls it.
    """
    start = text.index("#pragma gbr_base (lo)")
    struct = text[start:text.index("} lo;", start) + len("} lo;")]
    pads_a = (section_off(PRIME) - STUB) // STUB
    gap_b = section_off(RETRY) - section_off(PRIME) - STUB
    pads_b = gap_b // STUB
    if pads_a != 317 or pads_b != 95 or gap_b % STUB:
        raise SystemExit(
            f"distance pads drifted: {pads_a} then {pads_b}"
        )
    if section_off(RUN) - section_off(RETRY) != RETRY_SIZE:
        raise SystemExit("retry_issue no longer ends where run_transfer starts")
    if section_off(ISSUE) - section_off(RUN) != RUN_SIZE:
        raise SystemExit("run_transfer no longer ends where issue_command starts")
    retry = function_at(text, "int retry_issue(int param_1)")
    if not retry.startswith("static "):
        retry = "static " + retry
    run = function_at(text, "int run_transfer(void)")
    for needle in ("hole_09cdc();", "issue_command(param_1)"):
        if needle not in retry:
            raise SystemExit(f"retry_issue lost {needle}")
    for needle in ("lo.count_70 = 10;", "goto restart;", "retry_issue(0)"):
        if needle not in run:
            raise SystemExit(f"run_transfer lost {needle}")
    parts = [
        struct,
        "",
        "static void hole_09cdc(void);",
        "static void prime_count68(void);",
        "static int retry_issue(int param_1);",
        "static int issue_command(int arg);",
        "",
        empty_function("hole_09cdc", True).rstrip("\n"),
        "",
    ]
    parts.extend(empty_function(f"pad_a_{index:04d}", False).rstrip("\n") for index in range(pads_a))
    parts.append("")
    parts.append(empty_function("prime_count68", True).rstrip("\n"))
    parts.append("")
    parts.extend(empty_function(f"pad_b_{index:04d}", False).rstrip("\n") for index in range(pads_b))
    parts.append("")
    parts.append(retry)
    parts.append("")
    parts.append(run)
    parts.append("")
    parts.append("static int issue_command(int arg)\n{\n    return arg;\n}\n")
    source = "\n".join(parts)
    if source.count("\nvoid pad_a_") != 317 or source.count("\nvoid pad_b_") != 95:
        raise SystemExit("pad functions were not emitted")
    return source


def stage_tools():
    lib_src = SHC_LIB
    inc_src = SHC_INC
    if not (lib_src / "shc.exe").is_file() or not (lib_src / "lnk.exe").is_file():
        raise SystemExit(f"SHC is not at {lib_src}")
    if not (lib_src / "rof2bin.exe").is_file():
        raise SystemExit(f"rof2bin is not at {lib_src}")
    if not (inc_src / "machine.h").is_file():
        raise SystemExit(f"SHC headers are not at {inc_src}")
    for name in ("lib", "inc", "tmp", "out"):
        (STAGE / name).mkdir(parents=True, exist_ok=True)
    for src_dir, dest_dir in ((lib_src, STAGE / "lib"), (inc_src, STAGE / "inc")):
        for src in src_dir.iterdir():
            if not src.is_file():
                continue
            dest = dest_dir / src.name
            if (
                not dest.is_file()
                or dest.stat().st_size != src.stat().st_size
                or dest.stat().st_mtime < src.stat().st_mtime
            ):
                shutil.copy2(src, dest)


def write_lf(name, text):
    (STAGE / name).write_bytes(text.replace("\r\n", "\n").encode())


def write_crlf(name, text):
    normalized = text.replace("\r\n", "\n").replace("\n", "\r\n")
    (STAGE / name).write_bytes(normalized.encode())


def compile_both(reject_src, probe_src):
    for flag in REJECTED:
        if flag in PIN_FLAGS:
            raise SystemExit(f"pin contains rejected flag {flag}")
    stage_tools()
    write_lf("f9e34.c", reject_src)
    write_lf("fprobe.c", probe_src)
    p_end = section_off(ISSUE) + STUB
    bat = (
        f"c:\\probe\\lib\\shc.exe c:\\probe\\f9e34.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\f9e34.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_9e34.sub\r\n"
        "c:\\probe\\lib\\rof2bin.exe -q -s=0 -e=1C c:\\probe\\f9e34.abs\r\n"
        f"c:\\probe\\lib\\shc.exe c:\\probe\\fprobe.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\fprobe.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_probe.sub\r\n"
        f"c:\\probe\\lib\\rof2bin.exe -q -s=0 -e={p_end:X} c:\\probe\\fprobe.abs\r\n"
    )
    for flag in REJECTED:
        if flag in bat:
            raise SystemExit(f"link command contains rejected flag {flag}")
    write_crlf("run_matched.bat", bat)
    write_crlf(
        "link_9e34.sub",
        "input c:\\probe\\f9e34.obj\r\n"
        "output c:\\probe\\f9e34.abs\r\n"
        "entry _reject_code\r\n"
        "start P/0,$G0/0\r\n"
        "print c:\\probe\\f9e34.map\r\n"
        "exit\r\n",
    )
    write_crlf(
        "link_probe.sub",
        "input c:\\probe\\fprobe.obj\r\n"
        "output c:\\probe\\fprobe.abs\r\n"
        "entry _run_transfer\r\n"
        "start P/0,$G0/0\r\n"
        "print c:\\probe\\fprobe.map\r\n"
        "exit\r\n",
    )
    for name in ("f9e34.abs", "f9e34.bin", "fprobe.abs", "fprobe.bin"):
        path = STAGE / name
        if path.exists():
            path.unlink()
    if not BW.is_file():
        raise SystemExit(f"Boxedwine is not at {BW}")
    if not WINE_ZIP.is_file():
        raise SystemExit(f"Wine file system is not at {WINE_ZIP}")
    cmd = [
        str(BW),
        "-root", str(ROOT_FS),
        "-zip", str(WINE_ZIP),
        "-nosound", "-novideo", "-ttyPrepend", "-dxvk", "0",
        "-resolution", "320x200",
        "-env", r"SHC_TMP=C:\probe\tmp",
        "-env", r"SHC_INC=C:\probe\inc",
        "-env", r"SHC_LIB=C:\probe\lib",
        "-env", r"HLNK_TMP=C:\probe\tmp",
        "-env", r"TEMP=C:\probe\tmp",
        "-env", r"TMP=C:\probe\tmp",
        "-w", "/home/username/.wine/drive_c/probe",
        "/bin/wine", "cmd", "/c", r"c:\probe\run_matched.bat",
    ]
    ran = subprocess.run(cmd, check=False, capture_output=True, text=True)
    reject_bin = STAGE / "f9e34.bin"
    probe_bin = STAGE / "fprobe.bin"
    if not reject_bin.is_file() or not probe_bin.is_file():
        chunks = [(ran.stdout or ""), (ran.stderr or "")]
        for listing in (STAGE / "out" / "f9e34.lst", STAGE / "out" / "fprobe.lst"):
            if listing.is_file():
                lines = [
                    line for line in listing.read_text(errors="replace").splitlines()
                    if "(E)" in line or "(F)" in line or "ERROR" in line
                ]
                chunks.append("\n".join(lines[-20:]))
        raise SystemExit("linker wrote no binary image\n" + "\n".join(chunks)[-2500:])
    return reject_bin.read_bytes(), probe_bin.read_bytes()


def require_equal(name, got, flash):
    if got != flash:
        raise SystemExit(
            f"{name} linked bytes differ from flash: {got.hex()}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=str(Path.home() / "Documents/awbios/bios0.ic23"))
    args = parser.parse_args()
    rom = Path(args.rom).read_bytes()
    source = (ROOT / "src/services.c").read_text()
    reject_bin, probe_bin = compile_both(slice_reject(source), distance_unit(source))
    if len(reject_bin) != REJECT_SIZE:
        raise SystemExit(f"reject_code image is {len(reject_bin)} bytes")
    p_end = section_off(ISSUE) + STUB
    if len(probe_bin) != p_end:
        raise SystemExit(f"distance image is {len(probe_bin)} bytes, P is {p_end}")
    reject = reject_bin
    retry = probe_bin[section_off(RETRY):section_off(RETRY) + RETRY_SIZE]
    run = probe_bin[section_off(RUN):section_off(RUN) + RUN_SIZE]
    require_equal("reject_code", reject, rom[REJECT_ENTRY:REJECT_ENTRY + REJECT_SIZE])
    require_equal("retry_issue", retry, rom[RETRY:RETRY + RETRY_SIZE])
    require_equal("run_transfer", run, rom[RUN:RUN + RUN_SIZE])
    stub = probe_bin[section_off(ISSUE):section_off(ISSUE) + STUB]
    if stub != bytes.fromhex("0b004360"):
        raise SystemExit(f"issue_command stub drifted: {stub.hex()}")
    outputs = (
        ("reject_code", reject),
        ("retry_issue", retry),
        ("run_transfer", run),
    )
    for name, blob in outputs:
        path = ROOT / "build" / "services" / f"{name}.o"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(sh4.write_elf(blob, name, align=4))
    print(f"compiler: Hitachi SHC 5.1 Release 04, {PIN_FLAGS}")
    print("not re-flagged: -nospeed, -speed, -size, -rtnext, and -cpu=sh4 stay off")
    print(f"matched C: reject_code {REJECT_SIZE} bytes at 0x{REJECT_ENTRY:x}")
    print(f"matched C: retry_issue {RETRY_SIZE} bytes at 0x{RETRY:x}")
    print(f"matched C: run_transfer {RUN_SIZE} bytes at 0x{RUN:x}")
    print(retry.hex())
    print(run.hex())


if __name__ == "__main__":
    main()
