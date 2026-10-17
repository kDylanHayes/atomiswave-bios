#!/usr/bin/env python3
"""Split bios0 into asm, compiled, and data ranges.

Entries come from the architectural vectors, resolved bsr/jsr targets, and
real SH ABI prologues (sts.l pr,@-r15 and mov.l r14,@-r15). A forward branch
becomes a new entry only when another entry already sits between the branch
and its target, which is how the boot tails separate from the helpers they
jump over. Literal pools stay with the function that loads them.

0x9CDC is kept as a data hole: a bsr lands there and the bytes are zero.
Halfwords at 0xB090 and 0xCED8 are not prologues.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sh4

SHA1 = "b4c1a26bc8906d5275eb28c701dff2b9365bcdfa"
ARCH = (0x0, 0x5C, 0x100, 0x400, 0x600)
NAMES = {
    0x0: "reset",
    0x5C: "boot",
    0x100: "exc_general",
    0x318: "mix_shifts",
    0x350: "init_memory",
    0x400: "exc_tlb_miss",
    0x46C: "copy_words",
    0x484: "set_system_bits",
    0x538: "check_header",
    0x600: "exc_interrupt",
    0x7A4: "program_bootrom",
    0x97C: "poll_bit",
    0x99C: "blit_glyphs",
}
# Spans include the trailing literal pool. These three were the first
# handwritten units and must stay kind asm at these ends.
REQUIRED = {0x318: 0x350, 0x46C: 0x484, 0x97C: 0x99C}
MATCHED_C = "FUN_09e34"
TOP = object()
CONTROL = {
    "bra", "bsr", "bt", "bf", "bt/s", "bf/s", "jmp", "jsr", "rts", "rte", "braf", "bsrf",
}
STOP_AFTER_DELAY = {"bra", "jmp", "rts", "rte", "braf"}
ROOT = Path(__file__).resolve().parents[1]


def word(rom, off):
    if off < 0 or off + 2 > len(rom):
        return None
    return int.from_bytes(rom[off:off + 2], "little")


def is_delay_slot(rom, addr):
    ins = sh4.decode(word(rom, addr - 2)) if addr >= 2 else None
    return bool(ins and sh4.delayed(ins[0]))


def prologue_prefix(ins):
    if ins is None:
        return False
    op = ins[0]
    if op == "mov.l" and isinstance(ins[2], str) and ins[2].startswith("@-r"):
        return True
    if op == "mov.l" and isinstance(ins[1], tuple) and ins[1][0] == "pc":
        return True
    if op == "stc":
        return True
    if op == "mov" and (isinstance(ins[1], int) or ins[1] in sh4.REGS):
        return True
    if op == "tst" and ins[1] in sh4.REGS:
        return True
    return False


def walkback(rom, site):
    pc = site
    limit = max(0, site - 32)
    while pc - 2 >= limit:
        if is_delay_slot(rom, pc - 2):
            break
        ins = sh4.decode(word(rom, pc - 2))
        if not prologue_prefix(ins):
            break
        pc -= 2
    return pc


def prologue_entries(rom):
    """Frame saves (mov.l r14,@-r15) own a following sts.l pr within 48 bytes.

    Walking back from the sts alone stops on the and/or that the prologue
    interleaves with the register saves, which splits one function in half.
    """
    frames = scan_half(rom, 0x2FE6)
    saves = scan_half(rom, 0x4F22)
    claimed = set()
    entries = []
    for frame in frames:
        entries.append(walkback(rom, frame))
        for site in saves:
            if frame < site <= frame + 48 and not any(frame < other < site for other in frames):
                claimed.add(site)
    for site in saves:
        if site not in claimed:
            entries.append(walkback(rom, site))
    return sorted(set(entries))


def scan_half(rom, hw):
    return [off for off in range(0, len(rom) - 1, 2) if word(rom, off) == hw]


def put(state, reg, value):
    if not isinstance(reg, str):
        return
    if value is TOP:
        state.pop(reg, None)
    else:
        state[reg] = sh4.u32(value)


def get(state, reg):
    if not isinstance(reg, str):
        return TOP
    return state.get(reg, TOP)


def effect(state, pc, ins):
    """Data effect of one instruction. Control flow is handled by the walker."""
    st = dict(state)
    pools = []
    op = ins[0]
    if op in CONTROL or op in ("nop", "clrt", "sett", "div0u", "clrmac", "sleep", "pref"):
        return st, pools
    if op in ("cmp/eq", "cmp/hs", "cmp/ge", "cmp/hi", "cmp/gt", "cmp/pl", "cmp/pz",
              "cmp/str", "tst", "div0s", "div1"):
        return st, pools
    if op == "dt":
        src = get(state, ins[1])
        put(st, ins[1], TOP if src is TOP else src - 1)
        return st, pools
    if op == "mov" and isinstance(ins[1], int):
        put(st, ins[2], ins[1])
        return st, pools
    if op == "mov" and ins[1] in sh4.REGS:
        put(st, ins[2], get(state, ins[1]))
        return st, pools
    if op == "mov.l" and isinstance(ins[1], tuple) and ins[1][0] == "pc":
        ea = sh4.pc_rel_long(pc, ins[1][1])
        pools.append((ea, 4))
        return st, pools  # value filled by the caller that has the ROM
    if op == "mov.w" and isinstance(ins[1], tuple) and ins[1][0] == "pc":
        ea = sh4.pc_rel_word(pc, ins[1][1])
        pools.append((ea, 2))
        return st, pools
    if op == "add" and isinstance(ins[1], int):
        src = get(state, ins[2])
        put(st, ins[2], TOP if src is TOP else src + ins[1])
        return st, pools
    if op in ("add", "sub", "and", "or", "xor") and ins[1] in sh4.REGS:
        a = get(state, ins[2])
        b = get(state, ins[1])
        if a is TOP or b is TOP:
            put(st, ins[2], TOP)
        elif op == "add":
            put(st, ins[2], a + b)
        elif op == "sub":
            put(st, ins[2], a - b)
        elif op == "and":
            put(st, ins[2], a & b)
        elif op == "or":
            put(st, ins[2], a | b)
        else:
            put(st, ins[2], a ^ b)
        return st, pools
    if op in ("and", "or", "xor") and isinstance(ins[1], int):
        a = get(state, "r0")
        if a is TOP:
            put(st, "r0", TOP)
        elif op == "and":
            put(st, "r0", a & ins[1])
        elif op == "or":
            put(st, "r0", a | ins[1])
        else:
            put(st, "r0", a ^ ins[1])
        return st, pools
    if op in ("shll", "shll2", "shll8", "shll16", "shlr", "shlr2", "shlr8", "shlr16"):
        src = get(state, ins[1])
        shift = {"shll": 1, "shll2": 2, "shll8": 8, "shll16": 16,
                 "shlr": 1, "shlr2": 2, "shlr8": 8, "shlr16": 16}[op]
        if src is TOP:
            put(st, ins[1], TOP)
        elif op.startswith("shll"):
            put(st, ins[1], src << shift)
        else:
            put(st, ins[1], (src & 0xFFFFFFFF) >> shift)
        return st, pools
    if op in ("extu.b", "extu.w", "exts.b", "exts.w", "neg", "not"):
        src = get(state, ins[1])
        dest = ins[2]
        if src is TOP:
            put(st, dest, TOP)
        elif op == "extu.b":
            put(st, dest, src & 0xFF)
        elif op == "extu.w":
            put(st, dest, src & 0xFFFF)
        elif op == "exts.b":
            put(st, dest, sh4.sx(src & 0xFF, 8))
        elif op == "exts.w":
            put(st, dest, sh4.sx(src & 0xFFFF, 16))
        elif op == "neg":
            put(st, dest, -src)
        else:
            put(st, dest, ~src)
        return st, pools
    if op == "mov.l" and isinstance(ins[1], str) and ins[1].startswith("@+"):
        put(st, ins[2], TOP)
        reg = ins[1][2:]
        val = get(state, reg)
        put(st, reg, TOP if val is TOP else val + 4)
        return st, pools
    if op == "mov.w" and isinstance(ins[1], str) and ins[1].startswith("@+"):
        put(st, ins[2], TOP)
        reg = ins[1][2:]
        val = get(state, reg)
        put(st, reg, TOP if val is TOP else val + 2)
        return st, pools
    if op == "mov.l" and isinstance(ins[2], str) and ins[2].startswith("@-"):
        reg = ins[2][2:]
        val = get(state, reg)
        put(st, reg, TOP if val is TOP else val - 4)
        return st, pools
    if op in ("sts", "stc", "lds", "ldc") and len(ins) >= 3:
        put(st, ins[2], get(state, ins[1]))
        return st, pools
    if op == "sts.l" and isinstance(ins[2], str) and ins[2].startswith("@-"):
        reg = ins[2][2:]
        val = get(state, reg)
        put(st, reg, TOP if val is TOP else val - 4)
        return st, pools
    if op == "lds.l" and isinstance(ins[1], str) and ins[1].startswith("@+"):
        put(st, ins[2], TOP)
        reg = ins[1][2:]
        val = get(state, reg)
        put(st, reg, TOP if val is TOP else val + 4)
        return st, pools
    dest = ins[-1]
    if isinstance(dest, str) and dest in sh4.REGS:
        put(st, dest, TOP)
    return st, pools


def load_pool(rom, st, ins, pools):
    if not pools:
        return st
    op = ins[0]
    if op == "mov.l" and isinstance(ins[1], tuple):
        ea, size = pools[-1]
        if 0 <= ea and ea + 4 <= len(rom):
            put(st, ins[2], int.from_bytes(rom[ea:ea + 4], "little"))
    elif op == "mov.w" and isinstance(ins[1], tuple):
        ea, size = pools[-1]
        if 0 <= ea and ea + 2 <= len(rom):
            put(st, ins[2], sh4.sx(int.from_bytes(rom[ea:ea + 2], "little"), 16))
    return st


def join(old, new):
    out = {}
    for key in set(old) | set(new):
        a = old.get(key, TOP)
        b = new.get(key, TOP)
        if a is not TOP and a == b:
            out[key] = a
    changed = out != old
    return out, changed


def hole_at(rom, addr):
    if addr < 0 or addr + 8 > len(rom):
        return False
    block = rom[addr:addr + 8]
    return block == b"\x00" * 8 or block == b"\xff" * 8


def run_of(rom, addr):
    if addr < 0 or addr >= len(rom):
        return addr
    byte = rom[addr]
    if byte not in (0, 0xFF):
        return addr
    end = addr
    while end < len(rom) and rom[end] == byte:
        end += 1
    return end


class Discover:
    def __init__(self, rom):
        self.rom = rom
        self.entries = set()
        self.holes = set()
        self.refs = []

    def consider(self, target, kind, site):
        if target is TOP or not isinstance(target, int):
            self.refs.append({"kind": kind, "site": site, "target": None, "status": "indirect"})
            return
        target = sh4.u32(target)
        if target & 1:
            return
        if not (0 <= target < len(self.rom) - 1):
            self.refs.append({"kind": kind, "site": site, "target": target, "status": "external"})
            return
        if hole_at(self.rom, target):
            self.holes.add(target)
            self.refs.append({"kind": kind, "site": site, "target": target, "status": "hole"})
            return
        ins = sh4.decode(word(self.rom, target))
        # A pool word immediately before a real entry often decodes as bra/jsr.
        # Reject only when this site's own delay slot is the target.
        if ins is None or target == site + 2:
            self.refs.append({"kind": kind, "site": site, "target": target, "status": "rejected"})
            return
        self.entries.add(target)
        self.refs.append({"kind": kind, "site": site, "target": target, "status": "code"})


def crosses(src, target, entry, barriers):
    lo, hi = (src, target) if src < target else (target, src)
    return any(lo < other < hi and other != entry for other in barriers)


def peek(rom, pc, state, found, barriers):
    """Follow a few instructions into another entry, only to recover jsr targets."""
    st = dict(state)
    for _ in range(16):
        if pc < 0 or pc + 2 > len(rom):
            return
        ins = sh4.decode(word(rom, pc))
        if ins is None:
            return
        op = ins[0]
        if op in CONTROL:
            if op == "jsr" and ins[1] in sh4.REGS:
                found.consider(get(st, ins[1]), "jsr", pc)
            elif op == "bsr":
                found.consider(sh4.branch_target(pc, ins[1]), "bsr", pc)
            elif op == "jmp" and ins[1] in sh4.REGS:
                found.consider(get(st, ins[1]), "jmp", pc)
            return
        st, pools = effect(st, pc, ins)
        st = load_pool(rom, st, ins, pools)
        pc += 2


def walk(rom, entry, barriers, found):
    insns = set()
    pools = []
    state_at = {}
    work = [(entry, {})]
    steps = 0
    while work:
        pc, st = work.pop()
        steps += 1
        if steps > 20000:
            break
        if pc != entry and pc in barriers:
            peek(rom, pc, st, found, barriers)
            continue
        if pc < 0 or pc + 2 > len(rom) or pc & 1:
            continue
        hw = word(rom, pc)
        ins = sh4.decode(hw)
        if ins is None:
            continue
        prev = state_at.get(pc)
        if prev is None:
            state_at[pc] = dict(st)
        else:
            merged, changed = join(prev, st)
            if not changed:
                continue
            state_at[pc] = merged
            st = merged
        insns.add(pc)
        op = ins[0]
        if op not in CONTROL:
            st, extra = effect(st, pc, ins)
            st = load_pool(rom, st, ins, extra)
            pools.extend(extra)
            work.append((pc + 2, st))
            continue
        slot = pc + 2
        after = dict(st)
        if slot + 2 <= len(rom) and not (slot != entry and slot in barriers):
            slot_ins = sh4.decode(word(rom, slot))
            if slot_ins is not None and slot_ins[0] not in CONTROL:
                insns.add(slot)
                after, extra = effect(after, slot, slot_ins)
                after = load_pool(rom, after, slot_ins, extra)
                pools.extend(extra)
        if op == "bsr":
            found.consider(sh4.branch_target(pc, ins[1]), "bsr", pc)
            work.append((pc + 4, clobber_call(after)))
        elif op == "jsr" and ins[1] in sh4.REGS:
            found.consider(get(after, ins[1]), "jsr", pc)
            work.append((pc + 4, clobber_call(after)))
        elif op == "bra":
            target = sh4.branch_target(pc, ins[1])
            follow_branch(work, found, entry, barriers, pc, target, after, "bra")
        elif op in ("bt", "bf"):
            target = sh4.branch_target(pc, ins[1])
            work.append((pc + 2, dict(st)))
            follow_branch(work, found, entry, barriers, pc, target, st, op)
        elif op in ("bt/s", "bf/s"):
            target = sh4.branch_target(pc, ins[1])
            work.append((pc + 4, after))
            follow_branch(work, found, entry, barriers, pc, target, after, op)
        elif op == "jmp" and ins[1] in sh4.REGS:
            found.consider(get(after, ins[1]), "jmp", pc)
        elif op == "bsrf":
            work.append((pc + 4, clobber_call(after)))
        # rts, rte, braf: delay slot already kept, path ends
    return insns, pools


def clobber_call(state):
    out = dict(state)
    for reg in ("r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "pr"):
        out.pop(reg, None)
    return out


def follow_branch(work, found, entry, barriers, site, target, state, kind):
    if target == entry or (isinstance(target, int) and target not in barriers and not crosses(site, target, entry, barriers)):
        if isinstance(target, int):
            work.append((target, state))
        return
    found.consider(target, kind, site)


def signals(rom, insns):
    has_sts = has_frame = has_bsr = False
    for pc in insns:
        hw = word(rom, pc)
        if hw == 0x4F22:
            has_sts = True
        elif hw == 0x2FE6:
            has_frame = True
        ins = sh4.decode(hw)
        if ins and ins[0] == "bsr":
            has_bsr = True
    return has_sts or has_frame or has_bsr


def build(rom):
    found = Discover(rom)
    found.entries.update(ARCH)
    found.entries.update(prologue_entries(rom))
    owned = {}
    pools_of = {}
    for _ in range(12):
        before = set(found.entries)
        barriers = set(found.entries)
        owned = {}
        pools_of = {}
        for entry in sorted(barriers):
            insns, pools = walk(rom, entry, barriers, found)
            owned[entry] = insns
            pools_of[entry] = pools
        if found.entries == before:
            break
    functions = []
    order = sorted(found.entries)
    following = {entry: order[index + 1] if index + 1 < len(order) else len(rom)
                 for index, entry in enumerate(order)}
    for entry in order:
        insns = {pc for pc in owned.get(entry, ()) if entry <= pc < following[entry]}
        if not insns:
            continue
        end = max(pc + 2 for pc in insns)
        for ea, size in pools_of.get(entry, ()):
            if entry <= ea < following[entry]:
                end = max(end, ea + size)
        end = min(end, following[entry])
        functions.append({
            "entry": entry,
            "end": end,
            "name": NAMES.get(entry, f"FUN_{entry:05x}"),
            "insns": len(insns),
            "compiled_signal": signals(rom, insns),
        })
    calls = []
    seen = set()
    for ref in found.refs:
        if ref["status"] != "code" or ref["kind"] not in ("bsr", "jsr"):
            continue
        key = (ref["site"], ref["target"], ref["kind"])
        if key in seen:
            continue
        seen.add(key)
        calls.append(ref)
    kind = {}
    for fn in functions:
        kind[fn["entry"]] = "compiled" if fn["compiled_signal"] else "asm"
    changed = True
    while changed:
        changed = False
        for ref in calls:
            caller = max((fn["entry"] for fn in functions if fn["entry"] <= ref["site"] < fn["end"]), default=None)
            callee = ref["target"]
            if caller is None or callee not in kind:
                continue
            if kind[caller] == "compiled" and kind[callee] == "asm" and callee >= 0x9E00:
                kind[callee] = "compiled"
                changed = True
    for fn in functions:
        fn["kind"] = kind[fn["entry"]]
        fn["category"] = "services" if fn["kind"] == "compiled" else "boot"
        if fn["name"] == MATCHED_C:
            fn["matched_c"] = True
            fn["object"] = "build/services/FUN_09e34.o"
        else:
            folder = "boot" if fn["category"] == "boot" else "services"
            fn["source"] = f"asm/{folder}/{fn['name']}.s"
        fn.pop("compiled_signal")
    data = []
    covered_until = -1
    for hole in sorted(found.holes):
        end = run_of(rom, hole)
        if hole < covered_until:
            continue
        covered_until = end
        data.append({
            "entry": hole,
            "end": end,
            "name": f"hole_{hole:05x}",
            "kind": "data",
            "note": "bsr target in erased flash (" + ("0x00" if rom[hole] == 0 else "0xFF") + ")",
        })
    data.append({
        "entry": 0x1A000,
        "end": 0x1A00C,
        "name": "footer",
        "kind": "data",
        "note": "12-byte footer. bios1 differs at 0x1a003, 0x1a004, 0x1a006, 0x1a007, 0x1a008, 0x1a009",
    })
    for item in data:
        item["source"] = f"asm/data/{item['name']}.s"
    notes = notes_for(rom, functions, found.holes, found.refs)
    return functions, data, calls, notes


def notes_for(rom, functions, holes, refs):
    sts = scan_half(rom, 0x4F22)
    frame = scan_half(rom, 0x2FE6)
    lines = [
        "sts.l pr,@-r15 (0x4F22) at " + ", ".join(f"0x{off:05x}" for off in sts),
        "mov.l r14,@-r15 (0x2FE6) at " + ", ".join(f"0x{off:05x}" for off in frame),
        "no 0x4F22 or 0x2FE6 site is at or past 0xA6A0"
        if all(off < 0xA6A0 for off in sts + frame)
        else "WARNING: a prologue encoding was found at or past 0xA6A0",
        f"0xb090 halfword is 0x{word(rom, 0xb090):04x} (sts.l pr,@-r6 inside repeating data, not an entry)",
        f"0xced8 halfword is 0x{word(rom, 0xced8):04x} (same data pattern, not an entry)",
    ]
    if 0x9CDC in holes:
        sites = sorted({ref["site"] for ref in refs if ref.get("target") == 0x9CDC})
        where = ", ".join(f"0x{site:05x}" for site in sites) or "no recorded site"
        lines.append(f"0x9CDC is a bsr target ({where}) and a zero hole, so it is data, not a function")
    else:
        lines.append("WARNING: 0x9CDC was not recorded as a hole")
    last = max((fn["end"] for fn in functions), default=0)
    lines.append(
        f"last recovered code byte is 0x{last:05x}; nothing past 0xA6A0 was recovered as code"
        if last <= 0xA6A0
        else f"recovered code extends to 0x{last:05x}, which is past 0xA6A0"
    )
    lines.append("bytes that are not listed were not linear-swept; font, tables, and padding stay data")
    lines.append(
        "Hitachi SHC 5.1 Release 04 is pinned: -cpu=sh3 -endian=little -optimize=1. "
        "C match in this build is FUN_09e34, 28 bytes; see docs/compiler.md"
    )
    return lines


def write_text(path, functions, data, notes, digest):
    lines = [
        "# Atomiswave BIOS bios0 split",
        f"# sha1 {digest}",
        "# kind is asm, compiled, or data. compiled means an ABI prologue or a real bsr,",
        "# or a routine past 0x9E00 that is only reached from one of those.",
        "# asm is handwritten boot code. It is not matched C.",
    ]
    lines.extend(f"# {note}" for note in notes)
    lines.append("# entry end size kind category name")
    for fn in functions:
        lines.append(
            f"{fn['entry']:06x} {fn['end']:06x} {fn['end'] - fn['entry']:6d} "
            f"{fn['kind']:8} {fn['category']:8} {fn['name']}"
        )
    lines.append("# data")
    for item in data:
        lines.append(
            f"{item['entry']:06x} {item['end']:06x} {item['end'] - item['entry']:6d} "
            f"data     data     {item['name']}  {item['note']}"
        )
    path.write_text("\n".join(lines) + "\n")


def check(functions, notes):
    by_entry = {fn["entry"]: fn for fn in functions}
    problems = []
    for entry, end in REQUIRED.items():
        fn = by_entry.get(entry)
        if fn is None:
            problems.append(f"missing function at 0x{entry:x}")
        elif fn["end"] != end:
            problems.append(
                f"{fn['name']} ends at 0x{fn['end']:x}, ROM span through the pool is 0x{end:x}"
            )
        elif fn["kind"] != "asm":
            problems.append(f"{fn['name']} was classified {fn['kind']}")
    for entry in (0x0, 0x5C, 0x7A4):
        fn = by_entry.get(entry)
        if fn is None:
            problems.append(f"missing boot unit at 0x{entry:x}")
        elif not fn.get("source"):
            problems.append(f"{fn['name']} has no assembly source")
    if not any("0x9CDC is a bsr target" in note for note in notes):
        problems.append("0x9CDC hole was not recorded")
    if any("WARNING" in note for note in notes):
        problems.extend(note for note in notes if "WARNING" in note)
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", nargs="?", default=str(Path.home() / "Documents/awbios/bios0.ic23"))
    parser.add_argument("--text", default=str(ROOT / "asm/functions.txt"))
    parser.add_argument("--json", default=str(ROOT / "asm/map.json"))
    args = parser.parse_args()
    rom_path = Path(args.rom)
    rom = rom_path.read_bytes()
    digest = hashlib.sha1(rom).hexdigest()
    if digest != SHA1 or len(rom) != 131072:
        raise SystemExit(f"ROM sha1 {digest} length {len(rom)} does not match bios0")
    functions, data, calls, notes = build(rom)
    for fn in functions:
        fn["size"] = fn["end"] - fn["entry"]
    payload = {
        "image": "bios0",
        "sha1": digest,
        "compiler": "Hitachi SHC 5.1 Release 04 -cpu=sh3 -endian=little -optimize=1",
        "c_match_functions": 1,
        "notes": notes,
        "functions": functions,
        "data": data,
        "calls": calls,
    }
    text_path = Path(args.text)
    json_path = Path(args.json)
    text_path.parent.mkdir(parents=True, exist_ok=True)
    write_text(text_path, functions, data, notes, digest)
    json_path.write_text(json.dumps(payload, indent=2) + "\n")
    problems = check(functions, notes)
    asm = [fn for fn in functions if fn["kind"] == "asm"]
    compiled = [fn for fn in functions if fn["kind"] == "compiled"]
    print(f"functions {len(functions)}  asm {len(asm)}  compiled {len(compiled)}  data {len(data)}")
    print(f"asm bytes {sum(fn['size'] for fn in asm)}  compiled bytes {sum(fn['size'] for fn in compiled)}")
    print(f"wrote {text_path}")
    for note in notes:
        print(note)
    if problems:
        for problem in problems:
            print("error:", problem)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
