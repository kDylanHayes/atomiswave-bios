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
two bsr displacements match. That stub stays 4 bytes. The real step_phase
is a later unit and must not grow this one.

step_phase's own unit puts the backward callees at the flash distances
with 6-byte gaps and empty globals, then the 340-byte body. Three
unreferenced add-chains keep the end pool inside those 340 bytes and put
ram_call_2, prime_count68, and issue_command at the forward distances.
rof2bin -v=00 fills the two reserved alignment halfwords; the flash stores
them as zero. The chains, the gaps, and the stubs are not in the image.

set_hook and ram_window_ready each have their own unit. A mov.l literal
reaches forward only, so a later function mentions the same constant and
the compiler keeps one pool. Empty globals make that pool land on the
flash displacement. Those later functions are not in the flash.

ram_call_2 and ram_call_3 share one unit. Both are 2-mod-4 in the flash
because set_hook is 6 bytes. gap_six is that prefix. Twenty-two empty
globals put their one shared 0x8C0010F0 pool at the flash displacement.
Neither the prefix nor the pads are flash functions. The real pool bytes
stay in asm/data/service_pool.s.

prime_count68 is its own unit. mov.w @(disp,PC) zero-extends disp, so
the halfword at flash 0xA2E6 is 600. Sixty-seven empty globals put that
pool at displacement 0x87. rof2bin keeps the 6-byte function. The real
halfword stays inside scan_list.

quiet_interrupts is its own unit. Four 6-byte functions return the
constants that sit between 0x100000F0 and 0xA05F6910, and 23 empty
globals put that pool at displacement 0x1B and 0x1C. rof2bin keeps the
prefix plus the 20-byte function. The slice at 0x18 is the object.

enter_ram is its own unit. It has to start 2-mod-4, or the compiler
saves PR first and loads the port address before mov #8. Fifteen 6-byte
constant returns put it at offset 0x5A. The first of those returns
0xEFFFFF0F, and the next fourteen are the pool words that sit between
that mask and 0x100000F0. Thirteen empty globals then put the pool at
offset 0xBC. rof2bin -e=88 keeps the prefix plus the function. The
slice at 0x5A is the object. The prefix and the pads are not in the flash.

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
CALL2 = 0xA15E
CALL3 = 0xA16A
CALL_SIZE = 12
CALL_PADS = 22
PRIME_SIZE = 6
PRIME_PADS = 67
QUIET = 0xA144
QUIET_SIZE = 20
# Four `return <constant>` functions, 6 bytes each. quiet starts at 0x18.
QUIET_PREFIX = 0x18
QUIET_PADS = 23
ENTER = 0xA116
ENTER_SIZE = 46
# Fifteen 6-byte constant returns. enter_ram starts at 0x5A, which is 2-mod-4.
ENTER_PREFIX = 0x5A
ENTER_PADS = 13
STEP_SIZE = 340
# Section offset of the real body. section_off(STEP) is the 4-byte stub
# in the phase unit, not this offset.
STEP_BODY = 0x11C
STEP_END = STEP_BODY + STEP_SIZE
# add r5,r4 counts. Each add is 2 bytes and the return trailer is 4.
# The first chain crosses the mov.w reach, so the end pool stays put.
STEP_ADDS = (207, 55, 226)
ENTER_LEAD = (
    0xEFFFFF0F,
    0x0000FF80,
    0x8C000800,
    0x8C00C000,
    0x8C008000,
    0x8CE00000,
    0x8C0004F4,
    0x0000FFFB,
    0x8C000472,
    0x8C000462,
    0x8C000FD8,
    0x8C0005B8,
    0x0000B06E,
    0x8C010000,
    0x8C008100,
)


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


def calls_unit(text):
    """ram_call_2 at section offset 6 and ram_call_3 at 0x12.

    The flash entries are 2-mod-4. gap_six is 6 bytes and has no pool, so
    the first real function starts on that boundary. Both functions load
    0x8C0010F0. Twenty-two empty globals leave the code end 2-mod-4, and
    the compiler writes one pool at offset 0x78. rof2bin -e=1E keeps the
    prefix plus both functions. The pads are not in the flash.
    """
    call2 = function_at(text, "void ram_call_2(void)")
    call3 = function_at(text, "void ram_call_3(void)")
    if "0x8c0010f0)(0, 0, 0, 2)" not in call2:
        raise SystemExit("ram_call_2 lost its tail call")
    if "0x8c0010f0)(0, 0, 0, 3)" not in call3:
        raise SystemExit("ram_call_3 lost its tail call")
    code_end = ANCHOR + CALL_SIZE + CALL_SIZE + CALL_PADS * STUB
    if code_end != 0x76 or CALL2 % 4 != 2 or CALL3 % 4 != 2:
        raise SystemExit(f"ram_call pool gap drifted to {code_end:#x}")
    parts = [
        "int gap_six(int value)\n{\n    return value + 1;\n}",
        "",
        call2,
        "",
        call3,
        "",
    ]
    parts.extend(
        empty_function(f"pad_k_{index:04d}", False).rstrip("\n")
        for index in range(CALL_PADS)
    )
    parts.append("")
    source = "\n".join(parts)
    if source.count("\nvoid pad_k_") != CALL_PADS:
        raise SystemExit("ram_call pads were not emitted")
    return source


def prime_unit(text):
    """prime_count68 at offset 0. The halfword pool is at offset 0x112.

    Displacement 0x87 reaches 0x10E bytes past PC+4. The function is 6
    bytes, so 67 empty globals land the .DATA.W on that slot. rof2bin
    -e=6 drops the pads and the pool. The flash halfword stays in
    scan_list at 0xA2E6.
    """
    lo_at = text.index("#pragma gbr_base (lo)")
    lo = text[lo_at:text.index("} lo;", lo_at) + len("} lo;")]
    prime = function_at(text, "void prime_count68(void)")
    if "lo.count_68 = 600;" not in prime:
        raise SystemExit("prime_count68 lost its store")
    code_end = PRIME_SIZE + PRIME_PADS * STUB
    if code_end != 0x112 or PRIME % 4:
        raise SystemExit(f"prime_count68 pool gap drifted to {code_end:#x}")
    parts = [lo, "", prime, ""]
    parts.extend(
        empty_function(f"pad_p_{index:04d}", False).rstrip("\n")
        for index in range(PRIME_PADS)
    )
    parts.append("")
    source = "\n".join(parts)
    if source.count("\nvoid pad_p_") != PRIME_PADS:
        raise SystemExit("prime_count68 pads were not emitted")
    return source


def quiet_unit(text):
    """quiet_interrupts at section offset 0x18.

    The pool order is the order of first reference. The four prefix
    functions name 0x100000F0, 0x8C000000, 0x8C0006AA, and 0x8C000728.
    quiet_interrupts is the first use of 0xA05F6910, so that word follows
    them. Twenty-three empty globals put the pool at offset 0x88.
    Displacements from the real function are then 0x1B and 0x1C.
    rof2bin -e=2C keeps the prefix plus the function. The object is the
    slice at 0x18. The prefix and the pads are not flash functions.
    """
    quiet = function_at(text, "int quiet_interrupts(void)")
    for needle in (
        "set_cr(get_cr() | 0x100000F0);",
        "gbr_write_long(136, 0);",
        "*(volatile int *)0xA05F6910 = 0;",
        "return *(volatile int *)0xA05F6910;",
    ):
        if needle not in quiet:
            raise SystemExit(f"quiet_interrupts lost {needle}")
    code_end = QUIET_PREFIX + QUIET_SIZE + QUIET_PADS * STUB
    if code_end != 0x88 or QUIET % 4 or QUIET_PREFIX != 24:
        raise SystemExit(f"quiet_interrupts pool gap drifted to {code_end:#x}")
    parts = [
        "#include <machine.h>",
        "",
        "int pref_mask(void)\n{\n    return 0x100000F0;\n}",
        "",
        "int pref_b(void)\n{\n    return 0x8C000000;\n}",
        "",
        "int pref_c(void)\n{\n    return 0x8C0006AA;\n}",
        "",
        "int pref_d(void)\n{\n    return 0x8C000728;\n}",
        "",
        quiet,
        "",
    ]
    parts.extend(
        empty_function(f"pad_q_{index:04d}", False).rstrip("\n")
        for index in range(QUIET_PADS)
    )
    parts.append("")
    source = "\n".join(parts)
    if source.count("\nvoid pad_q_") != QUIET_PADS:
        raise SystemExit("quiet_interrupts pads were not emitted")
    return source


def enter_unit(text):
    """enter_ram at section offset 0x5A.

    A 0-mod-4 entry saves PR first and loads 0xA05F6910 before mov #8.
    Fifteen 6-byte returns make the entry 2-mod-4, and their constants
    are the pool words from 0xEFFFFF0F through 0x8C008100. Thirteen
    empty globals put that pool at offset 0xBC, so the function's own
    displacements match the flash. rof2bin -e=88 keeps the prefix plus
    the 46-byte function. The slice at 0x5A is the object.
    """
    body = function_at(text, "void enter_ram(void)")
    for needle in (
        "set_cr(get_cr() | 0x100000F0);",
        "set_vbr((void *)0x8C000000);",
        "(*(void (*)(void))0x8C0006AA)();",
        "gbr_write_long(564, 0x8C000728);",
        "*(volatile int *)0xA05F6910 = 8;",
        "(void)*(volatile int *)0xA05F6910;",
        "set_cr(get_cr() & 0xEFFFFF0F);",
        "(*(void (*)(void))0x8C000768)();",
    ):
        if needle not in body:
            raise SystemExit(f"enter_ram lost {needle}")
    if len(ENTER_LEAD) * ANCHOR != ENTER_PREFIX:
        raise SystemExit("enter_ram prefix is not 15 six-byte returns")
    code_end = ENTER_PREFIX + ENTER_SIZE + ENTER_PADS * STUB
    if code_end != 0xBC or ENTER % 4 != 2:
        raise SystemExit(f"enter_ram pool gap drifted to {code_end:#x}")
    parts = ["#include <machine.h>", ""]
    for index, value in enumerate(ENTER_LEAD):
        parts.append(f"int pref_e_{index:02d}(void)\n{{\n    return 0x{value:08X};\n}}")
        parts.append("")
    parts.append(body)
    parts.append("")
    parts.extend(
        empty_function(f"pad_e_{index:04d}", False).rstrip("\n")
        for index in range(ENTER_PADS)
    )
    parts.append("")
    source = "\n".join(parts)
    if source.count("\nint pref_e_") != len(ENTER_LEAD):
        raise SystemExit("enter_ram prefixes were not emitted")
    if source.count("\nvoid pad_e_") != ENTER_PADS:
        raise SystemExit("enter_ram pads were not emitted")
    return source


def inline_helper(text, name, signature):
    marker = f"#pragma inline ({name})"
    at = text.index(marker)
    rest = text[at:]
    body = function_at(rest, signature)
    return rest[:rest.index(body) + len(body)]


def add_chain(name, count):
    body = "    x = x + y;\n" * count
    return f"int {name}(int x, int y)\n{{\n{body}    return x;\n}}\n"


def step_unit(text):
    """step_phase at section offset 0x11C. The slice is 340 bytes.

    Backward callees sit at the flash deltas from 0x9E68. The real
    ram_window_ready is compiled just before the body so its literal
    parks at func+0x94. Forward callees sit after add-chains. The first
    chain is longer than a mov.w @(disp,PC) can reach, which keeps the
    end pool between the rts and that chain. reject_code here returns 0
    and is 4 bytes; the real 28-byte body is another unit. The phase
    unit's stub is not this function.
    """
    lo, hi = gbr_structs(text)
    body = function_at(text, "int step_phase(void)")
    for needle in (
        "set_gbr((void *)0x8C000000);",
        "phase = pass_s(hi.phase_144);",
        "case -5: goto phase_m5;",
        "if (0)",
        "phase = -6;",
        "goto phase_m6;",
        "set_gbr(keep);",
        "set_gbr(same_ptr(keep));",
        "TAIL;",
        "(unsigned)*(volatile int *)&lo.word_48",
        "(*(void (*)(int))0x8C0005B8)(0x8C000FC4);",
        "(*(int (*)(int))0x8C0004F4)(lo.ptr_100)",
    ):
        if needle not in body:
            raise SystemExit(f"step_phase lost {needle}")
    if body.count("set_gbr(keep)") != 1 or body.count("set_gbr(same_ptr(keep))") != 1:
        raise SystemExit("step_phase epilogue split drifted")
    macro_at = text.index("#define TAIL")
    macro = text[macro_at:text.index("int step_phase(void)", macro_at)].strip()
    if "gbr_read_word(146)" not in macro:
        raise SystemExit("step_phase tail lost gbr_read_word(146)")
    sign = inline_helper(text, "sign_keep", "static short sign_keep(short phase)")
    passed = inline_helper(text, "pass_s", "static short pass_s(short phase)")
    same = inline_helper(text, "same_ptr", "static void *same_ptr(void *p)")
    window = "static " + function_at(text, "int ram_window_ready(void)")
    lead = 6
    stub = 4
    pads_h, pads_r, pads_w = 23, 30, 6
    prefix = (
        lead + stub + lead + pads_h * stub + stub
        + pads_r * stub + stub + pads_w * stub + WINDOW_SIZE
    )
    call2_at = STEP_BODY + (CALL2 - STEP)
    prime_at = STEP_BODY + (PRIME - STEP)
    issue_at = STEP_BODY + (ISSUE - STEP)
    bulk_c, bulk_p, bulk_i = (2 * count + 4 for count in STEP_ADDS)
    if prefix != STEP_BODY or STEP_END != 0x270:
        raise SystemExit(f"step_phase prefix drifted to {prefix:#x}")
    if STEP_END + bulk_c != call2_at:
        raise SystemExit(f"ram_call_2 distance drifted to {STEP_END + bulk_c:#x}")
    if call2_at + stub + bulk_p != prime_at:
        raise SystemExit("prime_count68 distance drifted")
    if prime_at + stub + bulk_i != issue_at:
        raise SystemExit("issue_command distance drifted")
    if call2_at != 0x412 or prime_at != 0x488 or issue_at != 0x654:
        raise SystemExit("step_phase forward anchors drifted")
    parts = [
        "#include <machine.h>",
        "#pragma global_register(g8=R8,g9=R9,g10=R10,g11=R11,g12=R12)",
        lo,
        hi,
        "static void hole(void);",
        "static void hole_09db8(void);",
        "static void ram_call_2(void);",
        "static void prime_count68(void);",
        "static int issue_command(int arg);",
        "static int reject_code(void);",
        "static int ram_window_ready(void);",
        sign,
        passed,
        same,
        macro,
        "int gap_lead(int value)\n{\n    return value + 1;\n}",
        "static void hole(void) {}",
        "int gap_h(int value)\n{\n    return value + 1;\n}",
    ]
    parts.extend(empty_function(f"pad_h_{index:04d}", False).rstrip("\n") for index in range(pads_h))
    parts.append("static void hole_09db8(void) {}")
    parts.extend(empty_function(f"pad_r_{index:04d}", False).rstrip("\n") for index in range(pads_r))
    parts.append("static int reject_code(void)\n{\n    return 0;\n}")
    parts.extend(empty_function(f"pad_w_{index:04d}", False).rstrip("\n") for index in range(pads_w))
    parts.extend([
        window,
        body,
        add_chain("bulk_c", STEP_ADDS[0]).rstrip("\n"),
        "static void ram_call_2(void) {}",
        add_chain("bulk_p", STEP_ADDS[1]).rstrip("\n"),
        "static void prime_count68(void) {}",
        add_chain("bulk_i", STEP_ADDS[2]).rstrip("\n"),
        "static int issue_command(int arg)\n{\n    return arg;\n}",
    ])
    source = "\n".join(parts) + "\n"
    if source.count("\nvoid pad_h_") != pads_h or source.count("\nvoid pad_r_") != pads_r:
        raise SystemExit("step_phase pads were not emitted")
    if source.count("\nvoid pad_w_") != pads_w:
        raise SystemExit("step_phase window pads were not emitted")
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


def compile_matched(reject_src, probe_src, phase_src, hook_src, window_src, call_src, prime_src, quiet_src, enter_src, step_src):
    for flag in REJECTED:
        if flag in PIN_FLAGS:
            raise SystemExit(f"pin contains rejected flag {flag}")
    stage_tools()
    write_lf("f9e34.c", reject_src)
    write_lf("fprobe.c", probe_src)
    write_lf("fphase.c", phase_src)
    write_lf("fhook.c", hook_src)
    write_lf("fwin.c", window_src)
    write_lf("fcall.c", call_src)
    write_lf("fprime.c", prime_src)
    write_lf("fquiet.c", quiet_src)
    write_lf("feram.c", enter_src)
    write_lf("fstep.c", step_src)
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
        f"c:\\probe\\lib\\shc.exe c:\\probe\\fcall.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\fcall.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_call.sub\r\n"
        "c:\\probe\\lib\\rof2bin.exe -q -s=0 -e=1E c:\\probe\\fcall.abs\r\n"
        f"c:\\probe\\lib\\shc.exe c:\\probe\\fprime.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\fprime.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_prime.sub\r\n"
        "c:\\probe\\lib\\rof2bin.exe -q -s=0 -e=6 c:\\probe\\fprime.abs\r\n"
        f"c:\\probe\\lib\\shc.exe c:\\probe\\fquiet.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\fquiet.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_quiet.sub\r\n"
        "c:\\probe\\lib\\rof2bin.exe -q -s=0 -e=2C c:\\probe\\fquiet.abs\r\n"
        f"c:\\probe\\lib\\shc.exe c:\\probe\\feram.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\feram.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_enter.sub\r\n"
        "c:\\probe\\lib\\rof2bin.exe -q -s=0 -e=88 c:\\probe\\feram.abs\r\n"
        f"c:\\probe\\lib\\shc.exe c:\\probe\\fstep.c {PIN_FLAGS} "
        "-show=object -listfile=c:\\probe\\out\\fstep.lst\r\n"
        "c:\\probe\\lib\\lnk.exe -subcommand=c:\\probe\\link_step.sub\r\n"
        f"c:\\probe\\lib\\rof2bin.exe -q -v=00 -s=0 -e={STEP_END:X} c:\\probe\\fstep.abs\r\n"
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
    write_crlf(
        "link_call.sub",
        "input c:\\probe\\fcall.obj\r\n"
        "output c:\\probe\\fcall.abs\r\n"
        "entry _ram_call_2\r\n"
        "start P/0,$G0/0\r\n"
        "print c:\\probe\\fcall.map\r\n"
        "exit\r\n",
    )
    write_crlf(
        "link_prime.sub",
        "input c:\\probe\\fprime.obj\r\n"
        "output c:\\probe\\fprime.abs\r\n"
        "entry _prime_count68\r\n"
        "start P/0,$G0/0\r\n"
        "print c:\\probe\\fprime.map\r\n"
        "exit\r\n",
    )
    write_crlf(
        "link_quiet.sub",
        "input c:\\probe\\fquiet.obj\r\n"
        "output c:\\probe\\fquiet.abs\r\n"
        "entry _quiet_interrupts\r\n"
        "start P/0,$G0/0\r\n"
        "print c:\\probe\\fquiet.map\r\n"
        "exit\r\n",
    )
    write_crlf(
        "link_enter.sub",
        "input c:\\probe\\feram.obj\r\n"
        "output c:\\probe\\feram.abs\r\n"
        "entry _enter_ram\r\n"
        "start P/0,$G0/0\r\n"
        "print c:\\probe\\feram.map\r\n"
        "exit\r\n",
    )
    write_crlf(
        "link_step.sub",
        "input c:\\probe\\fstep.obj\r\n"
        "output c:\\probe\\fstep.abs\r\n"
        "entry _step_phase\r\n"
        "start P/0,$G0/0\r\n"
        "print c:\\probe\\fstep.map\r\n"
        "exit\r\n",
    )
    for name in (
        "f9e34.abs", "f9e34.bin",
        "fprobe.abs", "fprobe.bin",
        "fphase.abs", "fphase.bin",
        "fhook.abs", "fhook.bin",
        "fwin.abs", "fwin.bin",
        "fcall.abs", "fcall.bin",
        "fprime.abs", "fprime.bin",
        "fquiet.abs", "fquiet.bin",
        "feram.abs", "feram.bin",
        "fstep.abs", "fstep.bin",
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
    call_bin = STAGE / "fcall.bin"
    prime_bin = STAGE / "fprime.bin"
    quiet_bin = STAGE / "fquiet.bin"
    enter_bin = STAGE / "feram.bin"
    step_bin = STAGE / "fstep.bin"
    if not all(path.is_file() for path in (
        reject_bin, probe_bin, phase_bin, hook_bin, window_bin, call_bin, prime_bin, quiet_bin,
        enter_bin, step_bin,
    )):
        chunks = [(ran.stdout or ""), (ran.stderr or "")]
        for listing in (
            STAGE / "out" / "f9e34.lst",
            STAGE / "out" / "fprobe.lst",
            STAGE / "out" / "fphase.lst",
            STAGE / "out" / "fhook.lst",
            STAGE / "out" / "fwin.lst",
            STAGE / "out" / "fcall.lst",
            STAGE / "out" / "fprime.lst",
            STAGE / "out" / "fquiet.lst",
            STAGE / "out" / "feram.lst",
            STAGE / "out" / "fstep.lst",
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
        call_bin.read_bytes(),
        prime_bin.read_bytes(),
        quiet_bin.read_bytes(),
        enter_bin.read_bytes(),
        step_bin.read_bytes(),
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
    reject_bin, probe_bin, phase_bin, hook_bin, window_bin, call_bin, prime_bin, quiet_bin, enter_bin, step_bin = compile_matched(
        slice_reject(source),
        distance_unit(source),
        phase_unit(source),
        hook_unit(source),
        window_unit(source),
        calls_unit(source),
        prime_unit(source),
        quiet_unit(source),
        enter_unit(source),
        step_unit(source),
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
    call_end = ANCHOR + CALL_SIZE + CALL_SIZE
    if len(call_bin) != call_end:
        where2 = listed_offset(STAGE / "out" / "fcall.lst", "ram_call_2")
        where3 = listed_offset(STAGE / "out" / "fcall.lst", "ram_call_3")
        raise SystemExit(
            f"ram_call image is {len(call_bin)} bytes, slice is {call_end}; "
            f"ram_call_2 at {where2}, ram_call_3 at {where3}"
        )
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
    call2 = call_bin[ANCHOR:ANCHOR + CALL_SIZE]
    call3 = call_bin[ANCHOR + CALL_SIZE:call_end]
    require_equal("reject_code", reject, rom[REJECT_ENTRY:REJECT_ENTRY + REJECT_SIZE])
    require_equal("retry_issue", retry, rom[RETRY:RETRY + RETRY_SIZE])
    require_equal("run_transfer", run, rom[RUN:RUN + RUN_SIZE])
    require_equal("set_hook", hook_bin, rom[HOOK:HOOK + HOOK_SIZE])
    require_equal("ram_window_ready", window_bin, rom[WINDOW:WINDOW + WINDOW_SIZE])
    require_equal("ram_call_2", call2, rom[CALL2:CALL2 + CALL_SIZE])
    require_equal("ram_call_3", call3, rom[CALL3:CALL3 + CALL_SIZE])
    if len(prime_bin) != PRIME_SIZE:
        raise SystemExit(f"prime_count68 image is {len(prime_bin)} bytes")
    require_equal("prime_count68", prime_bin, rom[PRIME:PRIME + PRIME_SIZE])
    quiet_end = QUIET_PREFIX + QUIET_SIZE
    if len(quiet_bin) != quiet_end:
        where = listed_offset(STAGE / "out" / "fquiet.lst", "quiet_interrupts")
        raise SystemExit(
            f"quiet_interrupts image is {len(quiet_bin)} bytes, slice is {quiet_end}; "
            f"quiet_interrupts at {where}"
        )
    quiet = quiet_bin[QUIET_PREFIX:quiet_end]
    require_equal("quiet_interrupts", quiet, rom[QUIET:QUIET + QUIET_SIZE])
    enter_end = ENTER_PREFIX + ENTER_SIZE
    if len(enter_bin) != enter_end:
        where = listed_offset(STAGE / "out" / "feram.lst", "enter_ram")
        raise SystemExit(
            f"enter_ram image is {len(enter_bin)} bytes, slice is {enter_end}; "
            f"enter_ram at {where}"
        )
    enter = enter_bin[ENTER_PREFIX:enter_end]
    require_equal("enter_ram", enter, rom[ENTER:ENTER + ENTER_SIZE])
    if len(step_bin) != STEP_END:
        where = listed_offset(STAGE / "out" / "fstep.lst", "step_phase")
        raise SystemExit(
            f"step_phase image is {len(step_bin)} bytes, P slice is {STEP_END}; "
            f"step_phase at {where}"
        )
    step_where = listed_offset(STAGE / "out" / "fstep.lst", "step_phase")
    call_where = listed_offset(STAGE / "out" / "fstep.lst", "ram_call_2")
    prime_where = listed_offset(STAGE / "out" / "fstep.lst", "prime_count68")
    issue_where = listed_offset(STAGE / "out" / "fstep.lst", "issue_command")
    if (step_where, call_where, prime_where, issue_where) != (STEP_BODY, 0x412, 0x488, 0x654):
        raise SystemExit(
            "step_phase distances drifted: "
            f"body {step_where}, ram_call_2 {call_where}, "
            f"prime_count68 {prime_where}, issue_command {issue_where}"
        )
    step = step_bin[STEP_BODY:STEP_END]
    require_equal("step_phase", step, rom[STEP:STEP + STEP_SIZE])
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
        ("ram_call_2", call2, 2),
        ("ram_call_3", call3, 2),
        ("prime_count68", prime_bin, 4),
        ("quiet_interrupts", quiet, 4),
        ("enter_ram", enter, 2),
        ("step_phase", step, 4),
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
    print(f"matched C: ram_call_2 {CALL_SIZE} bytes at 0x{CALL2:x}")
    print(f"matched C: ram_call_3 {CALL_SIZE} bytes at 0x{CALL3:x}")
    print(f"matched C: prime_count68 {PRIME_SIZE} bytes at 0x{PRIME:x}")
    print(f"matched C: quiet_interrupts {QUIET_SIZE} bytes at 0x{QUIET:x}")
    print(f"matched C: enter_ram {ENTER_SIZE} bytes at 0x{ENTER:x}")
    print(f"matched C: step_phase {STEP_SIZE} bytes at 0x{STEP:x}")
    print(retry.hex())
    print(run.hex())
    print(phase.hex())


if __name__ == "__main__":
    main()
