# Atomiswave BIOS

Sammy Atomiswave (SYSTEM X) SH-4 boot flash, IC23. Hitachi SH-4, little-endian, 128 KiB.

`decomp/bios0/functions` is Ghidra pseudocode for bios0. `decomp/bios0/index.txt` lists each exported function. Those byte counts are the Ghidra bodies and omit literal pools. `FUN_09fbc` and `FUN_0a16a` were not exported. `asm/functions.txt` is the byte split. bios1 matches those bytes except six footer bytes, also listed in the index. That C is decompiler output, not rebuilt source.

The ROM images are not in this repo. A local bios0 is checked against SHA-1 `b4c1a26bc8906d5275eb28c701dff2b9365bcdfa` before the split. The default path is `~/Documents/awbios/bios0.ic23`.

## Matching status

Matched C is `FUN_09e34`, 28 bytes at `0x9E34`. The compiler is pinned: Hitachi SHC 5.1 Release 04, `-cpu=sh3 -endian=little -optimize=1`. The build links that function with `$G0` at 0 and checks the linked bytes. `src/services.c` also holds schedules that are not linked into the image. See `docs/compiler.md`.

Every other code range is checked assembly. `make` places those bytes, plus the linked `FUN_09e34` bytes, and copies the ROM only for addresses no object covers (font, tables, padding). Holes at `0x9CDC` and `0x9D52`, and the 12-byte footer, keep their original bytes. The reconstructed image SHA-1 is the bios0 digest above. Unmatched code is 0 bytes.

`asm/functions.txt` is the split. The cluster from `0x9E34` to `0xA49C` is the ABI-shaped code (`sts.l pr,@-r15`, `mov.l r14,@-r15`, and real `bsr`). There is no such prologue at or past `0xA6A0`. `0x9CDC` is a `bsr` target whose bytes are zero, so it is data. `0xB090` and `0xCED8` are `sts.l pr,@-r6` inside repeating data, not functions.

objdiff 3.8.2 disassembles SuperH as big-endian, so its percent is not the gate for this image. `complete` is set from the byte check. See `docs/objdiff.md`.

```
make
```

That refreshes the split, assembles every unit, links `FUN_09e34`, writes `objdiff.json`, and fails unless the image matches.

A clean clone cannot finish that. `make` needs the local bios0 image, the gitignored `tools/bin/objdiff-cli`, and the Boxedwine prefix that `tools/link_matched.py` uses to run the pinned SHC. The compiler and objdiff are not in this repo.
