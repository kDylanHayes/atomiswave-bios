#!/usr/bin/env python3
"""Link the matched service functions with the pinned Hitachi SHC.

reject_code is its own unit. $G0 at 0 fills the GBR+72 relocation.

retry_issue and run_transfer share one unit. A bsr displacement is fixed
at compile time, so the static callees have to sit at the flash distances.
hole_09cdc, prime_count68, and issue_command are 4-byte stubs in that unit.
317 and 95 unreferenced global empty functions fill the gaps. The real
bodies of those callees stay assembly.

phase_until_clear is a third unit. It starts at 0xA1DA, which is 2-mod-4,
because prime_count68 is 6 bytes and ends there. A run of only 4-byte
functions cannot land on that address. gap_six is a global `return value + 1`
(6 bytes, no literal pool) in the slot prime_count68 occupies. It is not
the flash body. hole_09cdc and step_phase are 4-byte static stubs so the
two bsr displacements match.

set_hook and ram_window_ready each have their own unit. A mov.l literal
reaches forward only, so a later function mentions the same constant and
the compiler keeps one pool. Empty globals make that pool land on the
flash displacement. Those later functions are not in the flash.

rof2bin pulls section P out of the absolute file. -e is an exclusive end
address. The slices are compared with bios0 before any object is written.

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
STEP = 0x9E68
PHASE = 0xA1DA
PHASE_SIZE = 26
# prime_count68 is 6 bytes at 0xA1D4 and phase_until_clear begins on the
# next halfword. The spacer has to be that size and must not grow a pool.
ANCHOR = 6
WINDOW = 0x9E50
WINDOW_SIZE = 24
HOOK = 0xA158
HOOK_SIZE = 6


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


def gbr_structs(text):
    lo_at = text.index("#pragma gbr_base (lo)")
    lo = text[lo_at:text.index("} lo;", lo_at) + len("} lo;")]
    hi_at = text.index("#pragma gbr_base1 (hi)")
    hi = text[hi_at:text.index("} hi;", hi_at) + len("} hi;")]
    return lo, hi


def phase_unit(text):
    """One translation unit whose bsr sites match 0xA1DA.

    Layout, with hole_09cdc at section offset 0:
      4-byte hole, 98 global pads, 4-byte step_phase, 218 global pads,
      6-byte gap_six, phase_until_clear (26 bytes).
    A trailing reference keeps the 128-byte lo window in the link so hi
    stays the next GBR section. GBR+146 is hi+18.
    """
    lo, hi = gbr_structs(text)
    pads_step = (section_off(STEP) - STUB) // STUB
    anchor_at = section_off(PHASE) - ANCHOR
    gap = anchor_at - (section_off(STEP) + STUB)
    pads_gap = gap // STUB
    if pads_step != 98 or pads_gap != 218 or gap % STUB or PHASE % 4 != 2:
        raise SystemExit(
            f"phase pads drifted: {pads_step} then {pads_gap}, gap {gap}"
        )
    phase = function_at(text, "int phase_until_clear(short param_1)")
    if phase.startswith("static "):
        raise SystemExit("phase_until_clear has to stay global")
    for needle in ("hi.limit_146 = param_1;", "hole_09cdc();", "step_phase()"):
        if needle not in phase:
            raise SystemExit(f"phase_until_clear lost {needle}")
    parts = [
        lo,
        "",
        hi,
        "",
        "static void hole_09cdc(void);",
        "static int step_phase(void);",
        "",
        empty_function("hole_09cdc", True).rstrip("\n"),
        "",
    ]
    parts.extend(
        empty_function(f"pad_c_{index:04d}", False).rstrip("\n")
        for index in range(pads_step)
    )
    parts.append("")
    parts.append("static int step_phase(void)\n{\n    return 0;\n}")
    parts.append("")
    parts.extend(
        empty_function(f"pad_d_{index:04d}", False).rstrip("\n")
        for index in range(pads_gap)
    )
    parts.append("")
    parts.append("int gap_six(int value)\n{\n    return value + 1;\n}")
    parts.append("")
    parts.append(phase)
    parts.append("")
    # After phase, so it does not move the matched slice. Referencing lo
    # keeps $G0 at 128 bytes. $G1 then begins at GBR+128.
    parts.append("int keep_lo(void)\n{\n    return lo.code_72;\n}")
    parts.append("")
    source = "\n".join(parts)
    if source.count("\nvoid pad_c_") != 98 or source.count("\nvoid pad_d_") != 218:
        raise SystemExit("phase pad functions were not emitted")
    return source


def hook_unit(text):
    """set_hook at offset 0. Its literal 0x8C000C86 is at offset 0x74.

    SHC merges the two stores into one pool after hook_tail. One 4-byte
    function reads lo so $G0 stays 128 bytes and the store links as GBR+136.
    """
    lo, hi = gbr_structs(text)
    hook = function_at(text, "void set_hook(void)")
    if "hi.hook_136 = 0x8c000c86;" not in hook:
        raise SystemExit("set_hook lost its store")
    span = HOOK_SIZE + 26 * STUB + HOOK_SIZE
    if span != 0x74:
        raise SystemExit(f"set_hook pool distance drifted to {span:#x}")
    parts = [
        lo,
        "",
        hi,
        "",
        hook,
        "",
        "int pad_h_0000(void)\n{\n    return lo.code_72;\n}",
        "",
    ]
    parts.extend(
        empty_function(f"pad_h_{index:04d}", False).rstrip("\n")
        for index in range(1, 26)
    )
    parts.append("")
    parts.append("void hook_tail(void)\n{\n    hi.hook_136 = 0x8c000c86;\n}")
    parts.append("")
    source = "\n".join(parts)
    if source.count("\nvoid pad_h_") != 25 or source.count("\nint pad_h_") != 1:
        raise SystemExit("set_hook pads were not emitted")
    return source


def window_unit(text):
    """ram_window_ready at offset 0. Its literal is at offset 0xAC.

    35 empty globals and a 6-byte tail leave the pool two bytes past a
    4-byte boundary, so the compiler inserts the halfword pad the flash
    distance needs. The tail is not a flash function.
    """
    lo, hi = gbr_structs(text)
    window = function_at(text, "int ram_window_ready(void)")
    for needle in ("lo.ptr_100 == 0x8c008000", "lo.word_76 == 32"):
        if needle not in window:
            raise SystemExit(f"ram_window_ready lost {needle}")
    code_end = WINDOW_SIZE + 35 * STUB + HOOK_SIZE
    if code_end != 0xAA:
        raise SystemExit(f"ram_window_ready pool gap drifted to {code_end:#x}")
    parts = [lo, "", hi, "", window, ""]
    parts.extend(
        empty_function(f"pad_w_{index:04d}", False).rstrip("\n")
        for index in range(35)
    )
    parts.append("")
    parts.append("int win_tail(void)\n{\n    return 0x8c008000;\n}")
    parts.append("")
    source = "\n".join(parts)
    if source.count("\nvoid pad_w_") != 35:
        raise SystemExit("ram_window_ready pads were not emitted")
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


def listed_offset(listing, function_name):
    """Object-listing address of a function, or None if the name is absent."""
    if not listing.is_file():
        return None
    needle = f"function: {function_name}"
    for line in listing.read_text(errors="replace").splitlines():
        if needle not in line:
            continue
        for part in line.split():
            if len(part) == 8 and all(c in "0123456789ABCDEFabcdef" for c in part):
                return int(part, 16)
    return None


def compile_matched(reject_src, probe_src, phase_src, hook_src, window_src):
    for flag in REJECTED:
        if flag in PIN_FLAGS:
            raise SystemExit(f"pin contains rejected flag {flag}")
    stage_tools()
    write_lf("f9e34.c", reject_src)
    write_lf("fprobe.c", probe_src)
    write_lf("fphase.c", phase_src)
    write_lf("fhook.c", hook_src)
    write_lf("fwin.c", window_src)
    p_end = section_off(ISSUE) + STUB
    phase_end = section_off(PHASE) + PHASE_SIZE
    bat = (
        f"c:\\probe\\lib\\shc.exe c:\\probe\\f9e34.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\f9e34.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_9e34.sub\r\n"
        "c:\\probe\\lib\\rof2bin.exe -q -s=0 -e=1C c:\\probe\\f9e34.abs\r\n"
        f"c:\\probe\\lib\\shc.exe c:\\probe\\fprobe.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\fprobe.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_probe.sub\r\n"
        f"c:\\probe\\lib\\rof2bin.exe -q -s=0 -e={p_end:X} c:\\probe\\fprobe.abs\r\n"
        f"c:\\probe\\lib\\shc.exe c:\\probe\\fphase.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\fphase.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_phase.sub\r\n"
        f"c:\\probe\\lib\\rof2bin.exe -q -s=0 -e={phase_end:X} c:\\probe\\fphase.abs\r\n"
        f"c:\\probe\\lib\\shc.exe c:\\probe\\fhook.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\fhook.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_hook.sub\r\n"
        "c:\\probe\\lib\\rof2bin.exe -q -s=0 -e=6 c:\\probe\\fhook.abs\r\n"
        f"c:\\probe\\lib\\shc.exe c:\\probe\\fwin.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\fwin.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_win.sub\r\n"
        "c:\\probe\\lib\\rof2bin.exe -q -s=0 -e=18 c:\\probe\\fwin.abs\r\n"
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
    write_crlf(
        "link_phase.sub",
        "input c:\\probe\\fphase.obj\r\n"
        "output c:\\probe\\fphase.abs\r\n"
        "entry _phase_until_clear\r\n"
        "start P/0,$G0/0\r\n"
        "print c:\\probe\\fphase.map\r\n"
        "exit\r\n",
    )
    write_crlf(
        "link_hook.sub",
        "input c:\\probe\\fhook.obj\r\n"
        "output c:\\probe\\fhook.abs\r\n"
        "entry _set_hook\r\n"
        "start P/0,$G0/0\r\n"
        "print c:\\probe\\fhook.map\r\n"
        "exit\r\n",
    )
    write_crlf(
        "link_win.sub",
        "input c:\\probe\\fwin.obj\r\n"
        "output c:\\probe\\fwin.abs\r\n"
        "entry _ram_window_ready\r\n"
        "start P/0,$G0/0\r\n"
        "print c:\\probe\\fwin.map\r\n"
        "exit\r\n",
    )
    for name in (
        "f9e34.abs", "f9e34.bin",
        "fprobe.abs", "fprobe.bin",
        "fphase.abs", "fphase.bin",
        "fhook.abs", "fhook.bin",
        "fwin.abs", "fwin.bin",
    ):
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
    phase_bin = STAGE / "fphase.bin"
    hook_bin = STAGE / "fhook.bin"
    window_bin = STAGE / "fwin.bin"
    if not all(path.is_file() for path in (
        reject_bin, probe_bin, phase_bin, hook_bin, window_bin
    )):
        chunks = [(ran.stdout or ""), (ran.stderr or "")]
        for listing in (
            STAGE / "out" / "f9e34.lst",
            STAGE / "out" / "fprobe.lst",
            STAGE / "out" / "fphase.lst",
            STAGE / "out" / "fhook.lst",
            STAGE / "out" / "fwin.lst",
        ):
            if listing.is_file():
                lines = [
                    line for line in listing.read_text(errors="replace").splitlines()
                    if "(E)" in line or "(F)" in line or "ERROR" in line
                ]
                chunks.append("\n".join(lines[-20:]))
        raise SystemExit("linker wrote no binary image\n" + "\n".join(chunks)[-2500:])
    return (
        reject_bin.read_bytes(),
        probe_bin.read_bytes(),
        phase_bin.read_bytes(),
        hook_bin.read_bytes(),
        window_bin.read_bytes(),
    )


def require_equal(name, got, flash):
    if got != flash:
        raise SystemExit(
            f"{name} linked bytes differ from flash\n"
            f"got   {got.hex()}\n"
            f"flash {flash.hex()}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=str(Path.home() / "Documents/awbios/bios0.ic23"))
    args = parser.parse_args()
    rom = Path(args.rom).read_bytes()
    source = (ROOT / "src/services.c").read_text()
    reject_bin, probe_bin, phase_bin, hook_bin, window_bin = compile_matched(
        slice_reject(source),
        distance_unit(source),
        phase_unit(source),
        hook_unit(source),
        window_unit(source),
    )
    if len(reject_bin) != REJECT_SIZE:
        raise SystemExit(f"reject_code image is {len(reject_bin)} bytes")
    p_end = section_off(ISSUE) + STUB
    if len(probe_bin) != p_end:
        raise SystemExit(f"distance image is {len(probe_bin)} bytes, P is {p_end}")
    phase_end = section_off(PHASE) + PHASE_SIZE
    if len(hook_bin) != HOOK_SIZE:
        raise SystemExit(f"set_hook image is {len(hook_bin)} bytes")
    if len(window_bin) != WINDOW_SIZE:
        raise SystemExit(f"ram_window_ready image is {len(window_bin)} bytes")
    if len(phase_bin) != phase_end:
        where = listed_offset(STAGE / "out" / "fphase.lst", "phase_until_clear")
        anchor = listed_offset(STAGE / "out" / "fphase.lst", "gap_six")
        raise SystemExit(
            f"phase image is {len(phase_bin)} bytes, P slice is {phase_end}; "
            f"gap_six at {anchor}, phase_until_clear at {where}"
        )
    reject = reject_bin
    retry = probe_bin[section_off(RETRY):section_off(RETRY) + RETRY_SIZE]
    run = probe_bin[section_off(RUN):section_off(RUN) + RUN_SIZE]
    phase = phase_bin[section_off(PHASE):section_off(PHASE) + PHASE_SIZE]
    require_equal("reject_code", reject, rom[REJECT_ENTRY:REJECT_ENTRY + REJECT_SIZE])
    require_equal("retry_issue", retry, rom[RETRY:RETRY + RETRY_SIZE])
    require_equal("run_transfer", run, rom[RUN:RUN + RUN_SIZE])
    require_equal("set_hook", hook_bin, rom[HOOK:HOOK + HOOK_SIZE])
    require_equal("ram_window_ready", window_bin, rom[WINDOW:WINDOW + WINDOW_SIZE])
    flash_phase = rom[PHASE:PHASE + PHASE_SIZE]
    if phase != flash_phase:
        where = listed_offset(STAGE / "out" / "fphase.lst", "phase_until_clear")
        anchor = listed_offset(STAGE / "out" / "fphase.lst", "gap_six")
        raise SystemExit(
            "phase_until_clear linked bytes differ from flash\n"
            f"got   {phase.hex()}\n"
            f"flash {flash_phase.hex()}\n"
            f"gap_six at {anchor}, phase_until_clear at {where}, "
            f"expected {section_off(PHASE)}"
        )
    stub = probe_bin[section_off(ISSUE):section_off(ISSUE) + STUB]
    if stub != bytes.fromhex("0b004360"):
        raise SystemExit(f"issue_command stub drifted: {stub.hex()}")
    outputs = (
        ("reject_code", reject, 4),
        ("retry_issue", retry, 4),
        ("run_transfer", run, 4),
        ("phase_until_clear", phase, 2),
        ("set_hook", hook_bin, 4),
        ("ram_window_ready", window_bin, 4),
    )
    for name, blob, align in outputs:
        path = ROOT / "build" / "services" / f"{name}.o"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(sh4.write_elf(blob, name, align=align))
    print(f"compiler: Hitachi SHC 5.1 Release 04, {PIN_FLAGS}")
    print("not re-flagged: -nospeed, -speed, -size, -rtnext, and -cpu=sh4 stay off")
    print(f"matched C: reject_code {REJECT_SIZE} bytes at 0x{REJECT_ENTRY:x}")
    print(f"matched C: retry_issue {RETRY_SIZE} bytes at 0x{RETRY:x}")
    print(f"matched C: run_transfer {RUN_SIZE} bytes at 0x{RUN:x}")
    print(f"matched C: phase_until_clear {PHASE_SIZE} bytes at 0x{PHASE:x}")
    print(f"matched C: set_hook {HOOK_SIZE} bytes at 0x{HOOK:x}")
    print(f"matched C: ram_window_ready {WINDOW_SIZE} bytes at 0x{WINDOW:x}")
    print(retry.hex())
    print(run.hex())
    print(phase.hex())


if __name__ == "__main__":
    main()
