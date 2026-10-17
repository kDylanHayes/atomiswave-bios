# Atomiswave BIOS

Sammy Atomiswave (SYSTEM X) SH-4 boot flash, IC23. Hitachi SH-4, little-endian, 128 KiB.

`decomp/bios0/functions` is Ghidra pseudocode for bios0. `decomp/bios0/index.txt` lists each function. bios1 matches those bytes except six footer bytes, also listed in the index. That C is decompiler output, not rebuilt source.

The ROM images are not in this repo. A local bios0 is checked against SHA-1 `b4c1a26bc8906d5275eb28c701dff2b9365bcdfa` before the split. The default path is `~/Documents/awbios/bios0.ic23`.

## Matching status

Matched C is 0 functions and 0 bytes. No compiler is pinned. `src/` is empty on purpose. See `docs/compiler.md`.

`asm/functions.txt` is the split. Boot code below `0xA00` is handwritten assembly. The cluster from `0x9E34` to `0xA49C` is the ABI-shaped code (`sts.l pr,@-r15`, `mov.l r14,@-r15`, and real `bsr`). There is no such prologue at or past `0xA6A0`. `0x9CDC` is a `bsr` target whose bytes are zero, so it is data. `0xB090` and `0xCED8` are `sts.l pr,@-r6` inside repeating data, not functions.

Three boot routines are byte-identical assembly, checked against the flash bytes:

| Unit | File offset | Bytes, including the pool |
| --- | --- | --- |
| `mix_shifts` | `0x318` | 56 |
| `copy_words` | `0x46C` | 24 |
| `poll_bit` | `0x97C` | 32 |

`reset`, `boot`, and `program_bootrom` stay original bytes. Nothing is marked `complete` in `objdiff.json`. objdiff 3.8.2 disassembles SuperH as big-endian, so its percent is not the gate for this image. See `docs/objdiff.md`.

```
make
```

That refreshes the split, assembles the three units, writes `objdiff.json`, and prints the three progress numbers.
