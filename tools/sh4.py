#!/usr/bin/env python3
"""SH-4 helpers for the Atomiswave BIOS split.

The decoder covers the integer instructions this image actually uses.
The assembler accepts a small GNU as subset and emits the same halfwords.
write_elf wraps those bytes in an ELF32 ET_REL object (EM_SH, EF_SH4)
with no relocations. That is the shape objdiff can grade. It is not a
substitute for sh-elf-as, and it is not evidence that a C compiler matches.
"""

from __future__ import annotations

import struct
from pathlib import Path

EM_SH = 42
EF_SH4 = 0x9
ET_REL = 1
SHT_NULL = 0
SHT_PROGBITS = 1
SHT_SYMTAB = 2
SHT_STRTAB = 3
SHF_ALLOC = 0x2
SHF_EXECINSTR = 0x4
STB_LOCAL = 0
STB_GLOBAL = 1
STT_FUNC = 2
STT_SECTION = 3

REGS = {f"r{i}": i for i in range(16)}


def sx(value, bits):
    sign = 1 << (bits - 1)
    return (value & (sign - 1)) - (value & sign)


def u32(value):
    return value & 0xFFFFFFFF


def decode(hw):
    op = hw >> 12
    n = (hw >> 8) & 0xF
    m = (hw >> 4) & 0xF
    imm8 = hw & 0xFF
    disp4 = hw & 0xF
    rn, rm = f"r{n}", f"r{m}"
    if hw == 0x0008:
        return ("clrt",)
    if hw == 0x0009:
        return ("nop",)
    if hw == 0x000B:
        return ("rts",)
    if hw == 0x0018:
        return ("sett",)
    if hw == 0x0019:
        return ("div0u",)
    if hw == 0x001B:
        return ("sleep",)
    if hw == 0x0028:
        return ("clrmac",)
    if hw == 0x0029:
        return ("movt", "r0")
    if hw == 0x002B:
        return ("rte",)
    if op == 0x0 and (hw & 0xF) == 0x2 and ((hw >> 4) & 0xF) == 0x0:
        return ("stc", "sr", rn)
    if op == 0x0 and (hw & 0xF) == 0x2 and ((hw >> 4) & 0xF) == 0x1:
        return ("stc", "gbr", rn)
    if op == 0x0 and (hw & 0xF) == 0x2 and ((hw >> 4) & 0xF) == 0x2:
        return ("stc", "vbr", rn)
    if op == 0x0 and (hw & 0xF) == 0xA and ((hw >> 4) & 0xF) == 0x0:
        return ("sts", "mach", rn)
    if op == 0x0 and (hw & 0xF) == 0xA and ((hw >> 4) & 0xF) == 0x1:
        return ("sts", "macl", rn)
    if op == 0x0 and (hw & 0xF) == 0xA and ((hw >> 4) & 0xF) == 0x2:
        return ("sts", "pr", rn)
    if op == 0x0 and (hw & 0xF) == 0x3:
        low = (hw >> 4) & 0xF
        kind = {0: "bsrf", 2: "braf"}.get(low)
        if kind:
            return (kind, rn)
    if op == 0x0 and (hw & 0xF) == 0x4:
        return ("mov.b", "r0", f"@(r0,{rn})")
    if op == 0x0 and (hw & 0xF) == 0x5:
        return ("mov.w", "r0", f"@(r0,{rn})")
    if op == 0x0 and (hw & 0xF) == 0x6:
        return ("mov.l", rm, f"@(r0,{rn})")
    if op == 0x0 and (hw & 0xF) == 0x7:
        return ("mul.l", rm, rn)
    if op == 0x0 and (hw & 0xF) == 0xC:
        return ("mov.b", f"@(r0,{rm})", "r0")
    if op == 0x0 and (hw & 0xF) == 0xD:
        return ("mov.w", f"@(r0,{rm})", "r0")
    if op == 0x0 and (hw & 0xF) == 0xE:
        return ("mov.l", f"@(r0,{rm})", rn)
    if op == 0x0 and (hw & 0xF) == 0xF:
        low = (hw >> 4) & 0xF
        opname = {0: "mac.l", 3: "ocbi", 4: "ocbp", 5: "ocbwb", 6: "pref", 9: "mova"}.get(low)
        if opname == "mac.l":
            return ("mac.l", f"@+{rm}", f"@+{rn}")
        if opname and opname != "mova":
            return (opname, f"@{rn}")
    if op == 0x1:
        return ("mov.l", rm, f"@({disp4 * 4},{rn})")
    if op == 0x2 and (hw & 0xF) == 0x0:
        return ("mov.b", rm, f"@{rn}")
    if op == 0x2 and (hw & 0xF) == 0x1:
        return ("mov.w", rm, f"@{rn}")
    if op == 0x2 and (hw & 0xF) == 0x2:
        return ("mov.l", rm, f"@{rn}")
    if op == 0x2 and (hw & 0xF) == 0x4:
        return ("mov.b", rm, f"@-{rn}")
    if op == 0x2 and (hw & 0xF) == 0x5:
        return ("mov.w", rm, f"@-{rn}")
    if op == 0x2 and (hw & 0xF) == 0x6:
        return ("mov.l", rm, f"@-{rn}")
    if op == 0x2 and (hw & 0xF) == 0x7:
        return ("div0s", rm, rn)
    if op == 0x2 and (hw & 0xF) == 0x8:
        return ("tst", rm, rn)
    if op == 0x2 and (hw & 0xF) == 0x9:
        return ("and", rm, rn)
    if op == 0x2 and (hw & 0xF) == 0xA:
        return ("xor", rm, rn)
    if op == 0x2 and (hw & 0xF) == 0xB:
        return ("or", rm, rn)
    if op == 0x2 and (hw & 0xF) == 0xC:
        return ("cmp/str", rm, rn)
    if op == 0x2 and (hw & 0xF) == 0xD:
        return ("xtrct", rm, rn)
    if op == 0x2 and (hw & 0xF) == 0xE:
        return ("mulu.w", rm, rn)
    if op == 0x2 and (hw & 0xF) == 0xF:
        return ("muls.w", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0x0:
        return ("cmp/eq", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0x2:
        return ("cmp/hs", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0x3:
        return ("cmp/ge", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0x4:
        return ("div1", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0x5:
        return ("dmulu.l", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0x6:
        return ("cmp/hi", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0x7:
        return ("cmp/gt", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0x8:
        return ("sub", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0xA:
        return ("subc", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0xB:
        return ("subv", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0xC:
        return ("add", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0xE:
        return ("addc", rm, rn)
    if op == 0x3 and (hw & 0xF) == 0xF:
        return ("addv", rm, rn)
    if op == 0x4 and (hw & 0xFF) == 0x00:
        return ("shll", rn)
    if op == 0x4 and (hw & 0xFF) == 0x01:
        return ("shlr", rn)
    if op == 0x4 and (hw & 0xFF) == 0x04:
        return ("rotl", rn)
    if op == 0x4 and (hw & 0xFF) == 0x05:
        return ("rotr", rn)
    if op == 0x4 and (hw & 0xFF) == 0x08:
        return ("shll2", rn)
    if op == 0x4 and (hw & 0xFF) == 0x09:
        return ("shlr2", rn)
    if op == 0x4 and (hw & 0xF) == 0xC:
        return ("shad", rm, rn)
    if op == 0x4 and (hw & 0xF) == 0xD:
        return ("shld", rm, rn)
    if op == 0x4 and (hw & 0xFF) == 0x0B:
        return ("jsr", rn)
    if op == 0x4 and (hw & 0xFF) == 0x10:
        return ("dt", rn)
    if op == 0x4 and (hw & 0xFF) == 0x11:
        return ("cmp/pz", rn)
    if op == 0x4 and (hw & 0xFF) == 0x15:
        return ("cmp/pl", rn)
    if op == 0x4 and (hw & 0xFF) == 0x18:
        return ("shll8", rn)
    if op == 0x4 and (hw & 0xFF) == 0x19:
        return ("shlr8", rn)
    if op == 0x4 and (hw & 0xFF) == 0x1B:
        return ("tas.b", f"@{rn}")
    if op == 0x4 and (hw & 0xFF) == 0x20:
        return ("shal", rn)
    if op == 0x4 and (hw & 0xFF) == 0x21:
        return ("shar", rn)
    if op == 0x4 and (hw & 0xFF) == 0x22:
        return ("sts.l", "pr", f"@-{rn}")
    if op == 0x4 and (hw & 0xFF) == 0x24:
        return ("rotcl", rn)
    if op == 0x4 and (hw & 0xFF) == 0x25:
        return ("rotcr", rn)
    if op == 0x4 and (hw & 0xFF) == 0x26:
        return ("lds.l", f"@+{rn}", "pr")
    if op == 0x4 and (hw & 0xFF) == 0x28:
        return ("shll16", rn)
    if op == 0x4 and (hw & 0xFF) == 0x29:
        return ("shlr16", rn)
    if op == 0x4 and (hw & 0xFF) == 0x2B:
        return ("jmp", rn)
    if op == 0x4 and (hw & 0xFF) == 0x0E:
        return ("ldc", rm, "sr")
    if op == 0x4 and (hw & 0xFF) == 0x1E:
        return ("ldc", rm, "gbr")
    if op == 0x4 and (hw & 0xFF) == 0x2E:
        return ("ldc", rm, "vbr")
    if op == 0x4 and (hw & 0xFF) == 0x0A:
        return ("lds", rm, "mach")
    if op == 0x4 and (hw & 0xFF) == 0x1A:
        return ("lds", rm, "macl")
    if op == 0x4 and (hw & 0xFF) == 0x2A:
        return ("lds", rm, "pr")
    if op == 0x4 and (hw & 0xFF) == 0x03:
        return ("stc.l", "sr", f"@-{rn}")
    if op == 0x4 and (hw & 0xFF) == 0x07:
        return ("ldc.l", f"@+{rn}", "sr")
    if op == 0x4 and (hw & 0xFF) == 0x13:
        return ("stc.l", "gbr", f"@-{rn}")
    if op == 0x4 and (hw & 0xFF) == 0x17:
        return ("ldc.l", f"@+{rn}", "gbr")
    if op == 0x4 and (hw & 0xFF) == 0x23:
        return ("stc.l", "vbr", f"@-{rn}")
    if op == 0x4 and (hw & 0xFF) == 0x27:
        return ("ldc.l", f"@+{rn}", "vbr")
    if op == 0x4 and (hw & 0xFF) == 0x02:
        return ("sts.l", "mach", f"@-{rn}")
    if op == 0x4 and (hw & 0xFF) == 0x06:
        return ("lds.l", f"@+{rn}", "mach")
    if op == 0x4 and (hw & 0xFF) == 0x12:
        return ("sts.l", "macl", f"@-{rn}")
    if op == 0x4 and (hw & 0xFF) == 0x16:
        return ("lds.l", f"@+{rn}", "macl")
    if op == 0x5:
        return ("mov.l", f"@({disp4 * 4},{rm})", rn)
    if op == 0x6 and (hw & 0xF) == 0x0:
        return ("mov.b", f"@{rm}", rn)
    if op == 0x6 and (hw & 0xF) == 0x1:
        return ("mov.w", f"@{rm}", rn)
    if op == 0x6 and (hw & 0xF) == 0x2:
        return ("mov.l", f"@{rm}", rn)
    if op == 0x6 and (hw & 0xF) == 0x3:
        return ("mov", rm, rn)
    if op == 0x6 and (hw & 0xF) == 0x4:
        return ("mov.b", f"@+{rm}", rn)
    if op == 0x6 and (hw & 0xF) == 0x5:
        return ("mov.w", f"@+{rm}", rn)
    if op == 0x6 and (hw & 0xF) == 0x6:
        return ("mov.l", f"@+{rm}", rn)
    if op == 0x6 and (hw & 0xF) == 0x7:
        return ("not", rm, rn)
    if op == 0x6 and (hw & 0xF) == 0x8:
        return ("swap.b", rm, rn)
    if op == 0x6 and (hw & 0xF) == 0x9:
        return ("swap.w", rm, rn)
    if op == 0x6 and (hw & 0xF) == 0xA:
        return ("negc", rm, rn)
    if op == 0x6 and (hw & 0xF) == 0xB:
        return ("neg", rm, rn)
    if op == 0x6 and (hw & 0xF) == 0xC:
        return ("extu.b", rm, rn)
    if op == 0x6 and (hw & 0xF) == 0xD:
        return ("extu.w", rm, rn)
    if op == 0x6 and (hw & 0xF) == 0xE:
        return ("exts.b", rm, rn)
    if op == 0x6 and (hw & 0xF) == 0xF:
        return ("exts.w", rm, rn)
    if op == 0x7:
        return ("add", sx(imm8, 8), rn)
    if op == 0x8 and (hw >> 8) == 0x80:
        return ("mov.b", "r0", f"@({(hw & 0xF)},r{(hw >> 4) & 0xF})")
    if op == 0x8 and (hw >> 8) == 0x81:
        return ("mov.w", "r0", f"@({(hw & 0xF) * 2},r{(hw >> 4) & 0xF})")
    if op == 0x8 and (hw >> 8) == 0x84:
        return ("mov.b", f"@({(hw & 0xF)},r{(hw >> 4) & 0xF})", "r0")
    if op == 0x8 and (hw >> 8) == 0x85:
        return ("mov.w", f"@({(hw & 0xF) * 2},r{(hw >> 4) & 0xF})", "r0")
    if op == 0x8 and (hw >> 8) == 0x88:
        return ("cmp/eq", sx(imm8, 8), "r0")
    if op == 0x8 and (hw >> 8) == 0x89:
        return ("bt", sx(imm8, 8))
    if op == 0x8 and (hw >> 8) == 0x8B:
        return ("bf", sx(imm8, 8))
    if op == 0x8 and (hw >> 8) == 0x8D:
        return ("bt/s", sx(imm8, 8))
    if op == 0x8 and (hw >> 8) == 0x8F:
        return ("bf/s", sx(imm8, 8))
    if op == 0x9:
        return ("mov.w", ("pc", sx(imm8, 8)), rn)
    if op == 0xA:
        return ("bra", sx(hw & 0xFFF, 12))
    if op == 0xB:
        return ("bsr", sx(hw & 0xFFF, 12))
    if op == 0xC and (hw >> 8) == 0xC0:
        return ("mov.b", "r0", f"@(gbr,{imm8})")
    if op == 0xC and (hw >> 8) == 0xC1:
        return ("mov.w", "r0", f"@(gbr,{imm8 * 2})")
    if op == 0xC and (hw >> 8) == 0xC2:
        return ("mov.l", "r0", f"@(gbr,{imm8 * 4})")
    if op == 0xC and (hw >> 8) == 0xC3:
        return ("trapa", imm8)
    if op == 0xC and (hw >> 8) == 0xC4:
        return ("mov.b", f"@(gbr,{imm8})", "r0")
    if op == 0xC and (hw >> 8) == 0xC5:
        return ("mov.w", f"@(gbr,{imm8 * 2})", "r0")
    if op == 0xC and (hw >> 8) == 0xC6:
        return ("mov.l", f"@(gbr,{imm8 * 4})", "r0")
    if op == 0xC and (hw >> 8) == 0xC7:
        return ("mova", ("pc", imm8), "r0")
    if op == 0xC and (hw >> 8) == 0xC8:
        return ("tst", imm8, "r0")
    if op == 0xC and (hw >> 8) == 0xC9:
        return ("and", imm8, "r0")
    if op == 0xC and (hw >> 8) == 0xCA:
        return ("xor", imm8, "r0")
    if op == 0xC and (hw >> 8) == 0xCB:
        return ("or", imm8, "r0")
    if op == 0xD:
        return ("mov.l", ("pc", imm8), rn)
    if op == 0xE:
        return ("mov", sx(imm8, 8), rn)
    return None


def word(buf, off):
    return int.from_bytes(buf[off:off + 2], "little")


def dword(buf, off):
    return int.from_bytes(buf[off:off + 4], "little")


def delayed(op):
    return op in {
        "bra", "bsr", "bt/s", "bf/s", "jmp", "jsr", "rts", "rte", "braf", "bsrf",
    }


def branch_target(pc, disp):
    return u32(pc + 4 + disp * 2)


def pc_rel_long(pc, disp):
    return u32((pc & ~3) + 4 + disp * 4)


def pc_rel_word(pc, disp):
    return u32(pc + 4 + disp * 2)


def _parse_num(text):
    return int(text, 0)


def _parse_operand(text):
    raw = text.strip()
    low = raw.lower()
    if low.startswith("#"):
        return ("imm", _parse_num(low[1:]))
    if low.startswith("@-r"):
        return ("pre", REGS[low[2:]])
    if low.startswith("@r") and low.endswith("+"):
        return ("post", REGS[low[1:-1]])
    if low.startswith("@r"):
        return ("at", REGS[low[1:]])
    if low in REGS:
        return ("reg", REGS[low])
    if low.startswith("0x") or low[:1].isdigit() or low.startswith("-"):
        return ("imm", _parse_num(low))
    return ("label", raw)


def _split_ops(text):
    if not text.strip():
        return []
    return [_parse_operand(part) for part in text.split(",")]


def _disp8(value, signed):
    if value % 2:
        raise ValueError(f"branch displacement {value} is not even")
    disp = value // 2
    if signed:
        if not -128 <= disp <= 127:
            raise ValueError(f"bf/bt displacement {disp} does not fit in 8 bits")
        return disp & 0xFF
    if not 0 <= disp <= 255:
        raise ValueError(f"pc-relative displacement {disp} does not fit")
    return disp


def _encode(op, args, pc, labels):
    def lab(node):
        if node[0] != "label":
            raise ValueError(f"{op} expected a label, got {node}")
        if node[1] not in labels:
            raise ValueError(f"undefined label {node[1]}")
        return labels[node[1]]

    def reg(node):
        if node[0] != "reg":
            raise ValueError(f"{op} expected a register, got {node}")
        return node[1]

    if op == "nop":
        return 0x0009
    if op == "rts":
        return 0x000B
    if op == "clrt":
        return 0x0008
    if op == "sett":
        return 0x0018
    if op == "dt":
        return 0x4010 | (reg(args[0]) << 8)
    if op == "mov" and args[0][0] == "imm":
        imm = args[0][1]
        if not -128 <= imm <= 255:
            raise ValueError(f"mov immediate {imm} does not fit")
        return 0xE000 | (reg(args[1]) << 8) | (imm & 0xFF)
    if op == "mov" and args[0][0] == "reg":
        return 0x6003 | (reg(args[1]) << 8) | (reg(args[0]) << 4)
    if op == "mov.l" and args[0][0] == "label":
        disp_bytes = lab(args[0]) - ((pc & ~3) + 4)
        if disp_bytes % 4:
            raise ValueError(f"mov.l pool at {lab(args[0]):#x} is not 4-byte aligned from {pc:#x}")
        disp = disp_bytes // 4
        if not 0 <= disp <= 255:
            raise ValueError(f"mov.l displacement {disp} does not fit")
        return 0xD000 | (reg(args[1]) << 8) | disp
    if op == "mov.l" and args[0][0] == "at":
        return 0x6002 | (reg(args[1]) << 8) | (args[0][1] << 4)
    if op == "mov.l" and args[0][0] == "post":
        return 0x6006 | (reg(args[1]) << 8) | (args[0][1] << 4)
    if op == "mov.l" and args[0][0] == "reg" and args[1][0] == "at":
        return 0x2002 | (args[1][1] << 8) | (reg(args[0]) << 4)
    if op == "mov.l" and args[0][0] == "reg" and args[1][0] == "pre":
        return 0x2006 | (args[1][1] << 8) | (reg(args[0]) << 4)
    if op == "add" and args[0][0] == "imm":
        imm = args[0][1]
        if not -128 <= imm <= 255:
            raise ValueError(f"add immediate {imm} does not fit")
        return 0x7000 | (reg(args[1]) << 8) | (imm & 0xFF)
    if op == "add" and args[0][0] == "reg":
        return 0x300C | (reg(args[1]) << 8) | (reg(args[0]) << 4)
    if op == "tst":
        return 0x2008 | (reg(args[1]) << 8) | (reg(args[0]) << 4)
    if op == "xor" and args[0][0] == "imm":
        if reg(args[1]) != 0:
            raise ValueError("xor #imm only writes r0")
        return 0xCA00 | (args[0][1] & 0xFF)
    if op == "xor":
        return 0x200A | (reg(args[1]) << 8) | (reg(args[0]) << 4)
    if op == "and" and args[0][0] == "imm":
        if reg(args[1]) != 0:
            raise ValueError("and #imm only writes r0")
        return 0xC900 | (args[0][1] & 0xFF)
    if op == "and":
        return 0x2009 | (reg(args[1]) << 8) | (reg(args[0]) << 4)
    if op == "or" and args[0][0] == "imm":
        if reg(args[1]) != 0:
            raise ValueError("or #imm only writes r0")
        return 0xCB00 | (args[0][1] & 0xFF)
    if op == "or":
        return 0x200B | (reg(args[1]) << 8) | (reg(args[0]) << 4)
    if op == "shld":
        return 0x400D | (reg(args[1]) << 8) | (reg(args[0]) << 4)
    if op in ("bf", "bt"):
        disp = lab(args[0]) - (pc + 4)
        opcode = 0x8B00 if op == "bf" else 0x8900
        return opcode | _disp8(disp, signed=True)
    raise ValueError(f"assembler does not implement {op}")


def assemble(text, origin=None):
    """Assemble a GNU-as subset. Returns (load_address, bytes)."""
    labels = {}
    global_name = None
    items = []
    lc = 0 if origin is None else origin
    started = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if "!" in line:
            line = line[:line.index("!")]
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        if line.endswith(":"):
            name = line[:-1].strip()
            labels[name] = lc
            if global_name is None:
                global_name = name
            continue
        if line.startswith("."):
            parts = line.split(None, 1)
            directive = parts[0].lower()
            rest = parts[1] if len(parts) > 1 else ""
            if directive in (".text", ".section"):
                continue
            if directive in (".global", ".globl"):
                global_name = rest.split(",")[0].strip()
                continue
            if directive == ".org":
                if started:
                    raise ValueError(".org must appear before any bytes")
                lc = _parse_num(rest.strip())
                continue
            if directive == ".align":
                align = 1 << _parse_num(rest.strip())
                padded = (lc + align - 1) & ~(align - 1)
                if padded != lc:
                    items.append((lc, "bytes", b"\x00" * (padded - lc)))
                    lc = padded
                    started = True
                continue
            if directive in (".long", ".word"):
                width = 4 if directive == ".long" else 2
                for piece in rest.split(","):
                    value = _parse_num(piece.strip()) & ((1 << (width * 8)) - 1)
                    items.append((lc, "bytes", value.to_bytes(width, "little")))
                    lc += width
                    started = True
                continue
            raise ValueError(f"line {lineno}: unknown directive {directive}")
        if ":" in line:
            name, line = line.split(":", 1)
            labels[name.strip()] = lc
            line = line.strip()
            if not line:
                continue
        parts = line.split(None, 1)
        mnemonic = parts[0].lower()
        operands = _split_ops(parts[1] if len(parts) > 1 else "")
        items.append((lc, "insn", mnemonic, operands))
        lc += 2
        started = True
    if not items:
        raise ValueError("empty assembly")
    origin = items[0][0]
    out = bytearray()
    cursor = origin
    for item in items:
        addr = item[0]
        if addr < cursor:
            raise ValueError(f"address went backwards at {addr:#x}")
        if addr > cursor:
            out.extend(b"\x00" * (addr - cursor))
            cursor = addr
        if item[1] == "bytes":
            out.extend(item[2])
            cursor += len(item[2])
        else:
            _, _, mnemonic, operands = item
            half = _encode(mnemonic, operands, addr, labels)
            out.extend(half.to_bytes(2, "little"))
            cursor += 2
    if global_name is None:
        raise ValueError("assembly has no global symbol")
    return origin, bytes(out), global_name


def _sym(name_off, value, size, info, shndx):
    return struct.pack("<IIIBBH", name_off, value, size, info, 0, shndx)


def write_elf(text, symbol, align=2):
    """ELF32 little-endian relocatable, one .text function, no relocations."""
    if align not in (2, 4):
        raise ValueError(f"unexpected alignment {align}")
    shstr = b"\0.text\0.shstrtab\0.strtab\0.symtab\0"
    strtab = b"\0" + symbol.encode("ascii") + b"\0"
    # Symbol 0 is null. Symbol 1 is the .text section. Symbol 2 is the function.
    symbols = b"".join([
        _sym(0, 0, 0, 0, 0),
        _sym(0, 0, 0, STT_SECTION, 1),
        _sym(1, 0, len(text), (STB_GLOBAL << 4) | STT_FUNC, 1),
    ])
    names = {
        ".text": 1,
        ".shstrtab": 7,
        ".strtab": 17,
        ".symtab": 25,
    }
    # 1 + len(".text") = 6, plus NUL = 7. Check:
    # \0 . t e x t \0 . s h s t r t a b \0 . s t r t a b \0 . s y m t a b \0
    assert shstr[names[".text"]:].split(b"\0", 1)[0] == b".text"
    assert shstr[names[".shstrtab"]:].split(b"\0", 1)[0] == b".shstrtab"
    assert shstr[names[".strtab"]:].split(b"\0", 1)[0] == b".strtab"
    assert shstr[names[".symtab"]:].split(b"\0", 1)[0] == b".symtab"

    def align_up(value, boundary):
        return (value + boundary - 1) & ~(boundary - 1)

    chunks = []
    off = 52
    text_off = off
    off += len(text)
    off = align_up(off, 4)
    shstr_off = off
    off += len(shstr)
    off = align_up(off, 4)
    str_off = off
    off += len(strtab)
    off = align_up(off, 4)
    sym_off = off
    off += len(symbols)
    shoff = align_up(off, 4)

    def sheader(name, typ, flags, addr, offset, size, link, info, addralign, entsize):
        return struct.pack("<IIIIIIIIII", name, typ, flags, addr, offset, size, link, info, addralign, entsize)

    headers = b"".join([
        sheader(0, SHT_NULL, 0, 0, 0, 0, 0, 0, 0, 0),
        sheader(names[".text"], SHT_PROGBITS, SHF_ALLOC | SHF_EXECINSTR, 0, text_off, len(text), 0, 0, align, 0),
        sheader(names[".shstrtab"], SHT_STRTAB, 0, 0, shstr_off, len(shstr), 0, 0, 1, 0),
        sheader(names[".strtab"], SHT_STRTAB, 0, 0, str_off, len(strtab), 0, 0, 1, 0),
        sheader(names[".symtab"], SHT_SYMTAB, 0, 0, sym_off, len(symbols), 3, 2, 4, 16),
    ])
    ehdr = struct.pack(
        "<16sHHIIIIIHHHHHH",
        bytes([0x7F, 0x45, 0x4C, 0x46, 1, 1, 1, 0]) + b"\0" * 8,
        ET_REL,
        EM_SH,
        1,
        0,
        0,
        shoff,
        EF_SH4,
        52,
        0,
        0,
        40,
        5,
        2,
    )
    blob = bytearray(shoff + len(headers))
    blob[:52] = ehdr
    blob[text_off:text_off + len(text)] = text
    blob[shstr_off:shstr_off + len(shstr)] = shstr
    blob[str_off:str_off + len(strtab)] = strtab
    blob[sym_off:sym_off + len(symbols)] = symbols
    blob[shoff:shoff + len(headers)] = headers
    return bytes(blob)


def check_against_rom(origin, data, rom):
    got = rom[origin:origin + len(data)]
    if got != data:
        for index, (left, right) in enumerate(zip(got, data)):
            if left != right:
                raise SystemExit(
                    f"bytes differ at {origin + index:#x}: rom {left:02x} asm {right:02x}"
                )
        raise SystemExit(
            f"length differs at {origin:#x}: rom {len(got)} asm {len(data)}"
        )
