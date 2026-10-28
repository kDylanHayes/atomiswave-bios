#!/usr/bin/env python3
"""Assemble the SHC 6.0B .src for issue_command, honouring its pool site.

The Hitachi assembler rejects a literal pool that sits between a
conditional branch and its target. The 6.0B compiler emits exactly that
layout. This assembler is linear: labels are the compiler's labels and
.DATA.W/.DATA.L stay where the compiler put them.

The local __$reject_code / __$prime_count68 stubs are removed from the
source before assembly and their BSR targets are supplied with --extern,
so the second pool stays at the end of issue_command. Those addresses are
the matched reject_code and prime_count68 functions in the image.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sh4


def preprocess(text):
    text = re.sub(r"@\(_lo-\(STARTOF \$G0\)\+(\d+),GBR\)", r"@(\1,gbr)", text)
    text = re.sub(
        r"@\(_hi-\(STARTOF \$G0\)\+(\d+),GBR\)",
        lambda m: f"@({int(m.group(1)) + 128},gbr)",
        text,
    )
    if "STARTOF" in text:
        raise SystemExit("unhandled STARTOF expression")
    return text


def classify(line):
    if line.startswith("."):
        parts = line.split(None, 1)
        d = parts[0].upper()
        rest = parts[1].strip() if len(parts) > 1 else ""
        if d == ".SECTION":
            return "section", rest.split(",")[0].strip()
        if d in (".DATA.W", ".DATA.L", ".DATAB.L", ".RES.W"):
            return "data", (d, rest)
        return "ignore", None
    if line.endswith(":"):
        return "label", line[:-1].strip()
    parts = line.split(None, 1)
    return "insn", (parts[0].lower(), parts[1] if len(parts) > 1 else "")


def walk(text, externs):
    """Yield (address, kind, payload) and stop at the GBR data sections."""
    addr = 0
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        kind, payload = classify(line)
        if kind == "section":
            if payload != "P":
                break
            continue
        if kind == "label":
            yield addr, kind, payload
            if payload in externs:
                break
            continue
        if kind == "data":
            d, rest = payload
            if d == ".DATAB.L":
                size = int(rest.split(",")[0], 0)
            elif d == ".RES.W":
                size = 2 * int(rest, 0)
            else:
                size = 2 if d == ".DATA.W" else 4
            yield addr, kind, payload
            addr += size
            continue
        if kind == "ignore":
            continue
        yield addr, kind, payload
        addr += 2


def parse_value(text, externs):
    text = text.strip()
    m = re.fullmatch(r"H'([0-9A-Fa-f]+)'?", text)
    if m:
        return int(m.group(1), 16)
    if text in externs:
        return externs[text]
    return int(text, 0)


def resolve(node, labels):
    if node[0] != "label":
        return node
    m = re.fullmatch(r"([A-Za-z_$][\w$]*)([+-]\d+)?", node[1])
    if not m:
        raise SystemExit(f"bad label expression {node[1]!r}")
    base, off = m.group(1), int(m.group(2) or 0)
    if base not in labels:
        raise SystemExit(f"undefined label {base}")
    return ("imm", labels[base] + off)


def assemble(text, origin, externs):
    labels = dict(externs)
    for addr, kind, payload in walk(text, externs):
        if kind == "label":
            labels[payload] = origin + addr

    out = bytearray()
    for addr, kind, payload in walk(text, externs):
        if kind == "label" or kind == "ignore":
            continue
        if kind == "data":
            d, rest = payload
            if d == ".DATAB.L":
                out.extend(b"\0" * int(rest.split(",")[0], 0))
            elif d == ".RES.W":
                out.extend(b"\0" * (2 * int(rest, 0)))
            else:
                width = 2 if d == ".DATA.W" else 4
                value = parse_value(rest, externs)
                out.extend((value & ((1 << (8 * width)) - 1)).to_bytes(width, "little"))
            continue
        op, raw_ops = payload
        ops = [resolve(n, labels) for n in sh4._split_ops(raw_ops)]
        half = sh4._encode(op, ops, origin + addr, labels)
        out.extend(half.to_bytes(2, "little"))
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--origin", default="0xA3A0")
    ap.add_argument("--symbol", default="issue_command")
    ap.add_argument("--extern", action="append", default=[],
                    help="name=address, e.g. __$reject_code=0x9E34")
    ap.add_argument("--check", help="ROM image to compare against --origin")
    args = ap.parse_args()

    externs = {}
    for item in args.extern:
        name, value = item.split("=", 1)
        externs[name] = int(value, 0)
    origin = int(args.origin, 0)

    text = preprocess(Path(args.source).read_text())
    data = assemble(text, origin, externs)
    if args.check:
        rom = Path(args.check).read_bytes()
        flash = rom[origin:origin + len(data)]
        if data != flash:
            diffs = [i for i in range(min(len(data), len(flash))) if data[i] != flash[i]]
            raise SystemExit(f"{len(diffs)} bytes differ at {origin:#x}")
        print(f"{len(data)} bytes match flash at {origin:#x}")
    align = 4 if origin % 4 == 0 else 2
    Path(args.output).write_bytes(sh4.write_elf(data, args.symbol, align=align))


if __name__ == "__main__":
    main()
