#!/usr/bin/env python3
"""Lift split ranges to checked assembly.

Each function is a control-flow walk. The delay slot of bra, jmp, rts, rte,
and braf does not fall through. PC-relative literals are data, including
literals that sit in another function's span. Decoder mistakes for ldc/lds,
indexed mov.b/mov.w, and the GBR bit ops are corrected here. decode() itself
stays as it was so the split does not move.

The three handwritten boot files are left alone. FUN_09e34 is matched C and
is not emitted. Output is byte-checked against the ROM before it is written.
This is assembly. It is not matched C.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sh4

ROOT = Path(__file__).resolve().parents[1]
HANDWRITTEN = {"mix_shifts", "copy_words", "poll_bit"}
MATCHED_C = {"FUN_09e34"}
# bsr lands inside the erased holes, not only at their starts.
HOLE_LABELS = {
    "hole_09cdc": (0x9CE2,),
    "hole_09d52": (0x9DB8,),
}
TERMINAL = {"bra", "jmp", "rts", "rte", "braf"}
DELAYED = {"bra", "bsr", "bt/s", "bf/s", "jmp", "jsr", "rts", "rte", "braf", "bsrf"}
BRANCH = {"bt", "bf", "bt/s", "bf/s", "bra", "bsr"}


def word_at(rom, addr):
    return int.from_bytes(rom[addr:addr + 2], "little")


def fix(hw):
    """Instruction tuple. Corrects the decoder cases this image hits."""
    top = hw >> 8
    n = (hw >> 8) & 0xF
    m = (hw >> 4) & 0xF
    op = hw >> 12
    if top in (0xCF, 0xCD, 0xCE, 0xCC):
        name = {0xCF: "or.b", 0xCD: "and.b", 0xCE: "xor.b", 0xCC: "tst.b"}[top]
        return (name, hw & 0xFF, "@(r0,gbr)")
    # ldc/lds keep the source register in bits 8-11. decode() reads bits 4-7.
    if op == 0x4 and (hw & 0xFF) in (0x0E, 0x1E, 0x2E, 0x0A, 0x1A, 0x2A):
        which = {
            0x0E: ("ldc", "sr"),
            0x1E: ("ldc", "gbr"),
            0x2E: ("ldc", "vbr"),
            0x0A: ("lds", "mach"),
            0x1A: ("lds", "macl"),
            0x2A: ("lds", "pr"),
        }[hw & 0xFF]
        return (which[0], f"r{n}", which[1])
    # 0000nnnnmmmm1100 is mov.b @(r0, rm), rn. decode() always prints r0.
    if op == 0 and (hw & 0xF) == 0xC:
        return ("mov.b", f"@(r0,r{m})", f"r{n}")
    if op == 0 and (hw & 0xF) == 0xD:
        return ("mov.w", f"@(r0,r{m})", f"r{n}")
    if op == 0 and (hw & 0xF) == 0x4:
        return ("mov.b", f"r{m}", f"@(r0,r{n})")
    if op == 0 and (hw & 0xF) == 0x5:
        return ("mov.w", f"r{m}", f"@(r0,r{n})")
    return sh4.decode(hw)


def _pool(ins, pc):
    op = ins[0]
    if op == "mov.l" and isinstance(ins[1], tuple) and ins[1][0] == "pc":
        target = sh4.pc_rel_long(pc, ins[1][1])
        return target, 4
    if op == "mov.w" and isinstance(ins[1], tuple) and ins[1][0] == "pc":
        target = sh4.pc_rel_word(pc, ins[1][1])
        return target, 2
    if op == "mova" and isinstance(ins[1], tuple) and ins[1][0] == "pc":
        target = (pc & ~3) + 4 + ins[1][1] * 4
        return target, 4
    return None


def walk(rom, entry, end, blocked):
    """Return code starts, pool bytes, and addresses that need labels."""
    code = {}
    pools = set()
    labels = set()
    work = [entry]
    seen = set()
    delay_of = {}
    while work:
        pc = work.pop()
        if pc in seen or pc < entry or pc >= end or pc in blocked or pc in pools:
            continue
        seen.add(pc)
        ins = fix(word_at(rom, pc))
        if ins is None:
            raise SystemExit(f"unknown encoding {word_at(rom, pc):04x} at {pc:#x}")
        op = ins[0]
        code[pc] = ins
        pooled = _pool(ins, pc)
        if pooled:
            target, size = pooled
            labels.add(target)
            for addr in range(target, target + size):
                pools.add(addr)
        if op in BRANCH:
            labels.add(sh4.branch_target(pc, ins[1]))
        nxt = pc + 2
        if op in DELAYED:
            if entry <= nxt < end and nxt not in blocked:
                delay_of[nxt] = op
                work.append(nxt)
            if op not in TERMINAL and entry <= pc + 4 < end:
                work.append(pc + 4)
            if op in BRANCH and entry <= sh4.branch_target(pc, ins[1]) < end:
                work.append(sh4.branch_target(pc, ins[1]))
        elif op in ("bt", "bf"):
            target = sh4.branch_target(pc, ins[1])
            if entry <= target < end:
                work.append(target)
            if entry <= nxt < end:
                work.append(nxt)
        elif delay_of.get(pc) not in TERMINAL and entry <= nxt < end:
            work.append(nxt)
    for pc in list(code):
        if pc in pools or (pc + 1) in pools:
            del code[pc]
    return code, pools, labels


def classify(rom, entry, end, blocked):
    """Repeat the walk until a pool is no longer decoded as code."""
    blocked = set(blocked)
    while True:
        code, pools, labels = walk(rom, entry, end, blocked)
        fresh = {addr for addr in pools if entry <= addr < end}
        overlap = set()
        for pc in code:
            if pc in fresh or (pc + 1) in fresh:
                overlap.add(pc)
                overlap.add(pc + 1)
        if not overlap and fresh <= blocked:
            return code, labels
        blocked |= fresh
        blocked |= overlap


def ref(target, entry, end, needed):
    if entry <= target < end:
        needed.add(target)
        return f".L{target:x}"
    return f"0x{target:x}"


def render(ins, pc, entry, end, needed):
    op = ins[0]
    if op in BRANCH:
        return f"{op} {ref(sh4.branch_target(pc, ins[1]), entry, end, needed)}"
    if op in ("mov.l", "mov.w") and isinstance(ins[1], tuple) and ins[1][0] == "pc":
        if op == "mov.l":
            target = sh4.pc_rel_long(pc, ins[1][1])
        else:
            target = sh4.pc_rel_word(pc, ins[1][1])
        return f"{op} {ref(target, entry, end, needed)}, {ins[2]}"
    parts = []
    for opnd in ins[1:]:
        if isinstance(opnd, int):
            parts.append(f"#{opnd}")
        elif isinstance(opnd, tuple):
            raise SystemExit(f"unrendered operand {opnd!r} in {ins!r} at {pc:#x}")
        else:
            parts.append(str(opnd))
    if not parts:
        return op
    return op + " " + ", ".join(parts)


def emit_function(rom, fn, blocked):
    entry, end, name = fn["entry"], fn["end"], fn["name"]
    code, labels = classify(rom, entry, end, blocked)
    needed = {addr for addr in labels if entry <= addr < end}
    lines = [
        f"! {name}",
        "! Lifted from bios0. Byte-checked assembly, not matched C.",
        "",
        f"        .org    0x{entry:x}",
        f"        .global {name}",
    ]
    pc = entry
    while pc < end:
        if pc == entry:
            lines.append(f"{name}:")
        if pc in needed:
            lines.append(f".L{pc:x}:")
        if pc in code:
            lines.append(f"        {render(code[pc], pc, entry, end, needed)}")
            pc += 2
            continue
        # A label inside the next four bytes has to stay addressable.
        width = 2
        if (
            pc % 4 == 0
            and pc + 4 <= end
            and all(addr not in code for addr in range(pc, pc + 4))
            and not any(addr in needed for addr in range(pc + 1, pc + 4))
        ):
            width = 4
        if any(addr in code for addr in range(pc, pc + width)):
            raise SystemExit(f"{name}: data at {pc:#x} overlaps an instruction")
        value = int.from_bytes(rom[pc:pc + width], "little")
        if width == 4:
            lines.append(f"        .long   0x{value:08x}")
        else:
            lines.append(f"        .word   0x{value:04x}")
        pc += width
    text = "\n".join(lines) + "\n"
    origin, data, symbol = sh4.assemble(text)
    if origin != entry or symbol != name or data != rom[entry:end]:
        raise SystemExit(f"{name}: lifted assembly does not match {entry:#x}")
    return text


def emit_data(rom, item):
    entry, end, name = item["entry"], item["end"], item["name"]
    extra = set(HOLE_LABELS.get(name, ()))
    lines = [
        f"! {name}",
        "! Original flash bytes. Not a recoverable function.",
        "",
        f"        .org    0x{entry:x}",
        f"        .global {name}",
        f"{name}:",
    ]
    pc = entry
    while pc < end:
        if pc in extra:
            lines.append(f"hole_{pc:05x}:")
        if pc % 4 == 0 and pc + 4 <= end and not any(addr in extra for addr in range(pc + 1, pc + 4)):
            value = int.from_bytes(rom[pc:pc + 4], "little")
            lines.append(f"        .long   0x{value:08x}")
            pc += 4
        else:
            value = int.from_bytes(rom[pc:pc + 2], "little")
            lines.append(f"        .word   0x{value:04x}")
            pc += 2
    text = "\n".join(lines) + "\n"
    origin, data, symbol = sh4.assemble(text)
    if origin != entry or symbol != name or data != rom[entry:end]:
        raise SystemExit(f"{name}: data assembly does not match {entry:#x}")
    return text


def pool_bytes(rom, functions):
    """Literals referenced from any function. They are not code."""
    blocked = set()
    for fn in functions:
        if fn["name"] in MATCHED_C:
            continue
        _code, pools, _labels = walk(rom, fn["entry"], fn["end"], set())
        blocked |= pools
    return blocked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", default=str(Path.home() / "Documents/awbios/bios0.ic23"))
    parser.add_argument("--map", default=str(ROOT / "asm/map.json"))
    parser.add_argument("--check", action="store_true", help="round-trip only; do not write")
    args = parser.parse_args()
    rom = Path(args.rom).read_bytes()
    payload = json.loads(Path(args.map).read_text())
    blocked = pool_bytes(rom, payload["functions"])
    written = 0
    for fn in payload["functions"]:
        if fn["name"] in HANDWRITTEN or fn["name"] in MATCHED_C:
            continue
        text = emit_function(rom, fn, blocked)
        folder = "boot" if fn["category"] == "boot" else "services"
        path = ROOT / "asm" / folder / f"{fn['name']}.s"
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        written += 1
    for item in payload["data"]:
        text = emit_data(rom, item)
        path = ROOT / "asm/data" / f"{item['name']}.s"
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        written += 1
    print(f"lifted {written} ranges")


if __name__ == "__main__":
    main()
