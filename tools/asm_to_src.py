#!/usr/bin/env python3
"""Translate a checked .s listing into the SHC .src dialect.

The .s files use the same mnemonic set and operand order as the SHC
listing; this only uppercases registers, turns .word/.long into
.DATA.W/.DATA.L, and rewrites absolute bsr targets to extern symbols.
"""
import re
import sys
from pathlib import Path

BSR = re.compile(r"(?i)^bsr\s+0x([0-9a-f]+)$")


def conv_operand(text):
    text = text.strip()
    text = re.sub(r"\.L([A-Za-z0-9_]+)", lambda m: f"L_{m.group(1)}", text)
    text = re.sub(r"\br(\d+)\b", lambda m: f"R{m.group(1)}", text, flags=re.I)
    text = text.replace("@+R15", "@R15+")
    text = re.sub(r"\b(gbr|sr|pr|mach|macl|vbr)\b", lambda m: m.group(1).upper(), text, flags=re.I)
    return text


def main():
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    out = [".SECTION    P,CODE,ALIGN=4"]
    externs = {}
    addr = 0xA1F4
    for raw in src.read_text().splitlines():
        line = raw.split("!", 1)[0].strip()
        if not line:
            continue
        if line.endswith(":"):
            name = line[:-1].strip()
            if name.startswith(".L"):
                name = "L_" + name[2:]
            out.append(name + ":")
            continue
        if line.startswith("."):
            parts = line.split(None, 1)
            d = parts[0].lower()
            rest = parts[1].strip() if len(parts) > 1 else ""
            if d == ".org":
                addr = int(rest, 0)
                continue
            if d == ".global":
                continue
            if d == ".word":
                out.append(f"          .DATA.W     H'{int(rest,0):04X}'")
                addr += 2
                continue
            if d == ".long":
                out.append(f"          .DATA.L     H'{int(rest,0):08X}'")
                addr += 4
                continue
            out.append(line)
            continue
        m = BSR.match(line)
        if m:
            sym = f"X_{m.group(1).upper()}"
            externs[sym] = int(m.group(1), 16)
            out.append(f"          BSR         {sym}")
            addr += 2
            continue
        parts = line.split(None, 1)
        op = parts[0].upper()
        rest = parts[1].strip() if len(parts) > 1 else ""
        if op == "JSR" or (op.startswith("JSR") and "@" not in rest):
            rest = "@" + rest
        ops = [conv_operand(x) for x in re.split(r",(?![^(]*\))", rest)]
        out.append(f"          {op:<12}{','.join(ops)}")
        addr += 2
    out.append("          .END")
    dst.write_text("\n".join(out) + "\n")
    print("externs:", " ".join(f"--extern {k}={v:#x}" for k, v in externs.items()))


if __name__ == "__main__":
    main()
