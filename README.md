# Atomiswave BIOS

Sammy Atomiswave (SYSTEM X) SH-4 boot flash, IC23. Hitachi SH-4, little-endian, 128 KiB.

This repository was written by an AI. The flash has no symbol table, and no original source was available. The first bytes are the reset instruction. The only human-readable strings are `SYSTEM_X_APP`, the 2001 SI ELECTRONICS copyright, the on-screen error text, and `BOOTROM WRITE OK`. Function names, field names, comments, the matched C, and these docs were assigned from the control flow and from the pinned compiler's output. They are not Sammy's identifiers. The SHA-1 check is what the bytes are held to.

`decomp/bios0/functions` is Ghidra pseudocode for bios0. `decomp/bios0/index.txt` lists each exported function. Those byte counts are the Ghidra bodies and omit literal pools. The Ghidra export has no file for `service_main` (`0x9FBC`) or `ram_call_3` (`0xA16A`). `asm/functions.txt` is the byte split. Names for the service cluster are in `docs/services.md`. The boot ranges below `0xA00` are mapped in `docs/boot.md`. bios1 matches those bytes except six footer bytes, also listed in the index. That C is decompiler output, not rebuilt source.

The ROM images are not in this repo. A local bios0 is checked against SHA-1 `b4c1a26bc8906d5275eb28c701dff2b9365bcdfa` before the split. The default path is `~/Documents/awbios/bios0.ic23`.

## Matching status

Matched C is `reject_code` (28 bytes at `0x9E34`), `ram_window_ready` (24 bytes at `0x9E50`), `set_hook` (6 bytes at `0xA158`), `phase_until_clear` (26 bytes at `0xA1DA`), `retry_issue` (28 bytes at `0xA354`), and `run_transfer` (48 bytes at `0xA370`). The compiler is pinned: Hitachi SHC 5.1 Release 04, `-cpu=sh3 -endian=little -optimize=1`. The build links those functions and checks the linked bytes. `retry_issue` and `run_transfer` share a unit whose static callees sit at the flash distances. `phase_until_clear` is linked in its own unit, because it starts two bytes off a 4-byte boundary. `set_hook` and `ram_window_ready` are linked in their own units so their literal pools sit at the flash displacements. `src/services.c` also holds schedules that are not linked into the image. Field names and the phase machine are in `docs/services.md`. The compiler pin is in `docs/compiler.md`.

Every other code range is checked assembly. `make` places those bytes, plus the linked C bytes, and copies the ROM only for addresses no object covers (font, tables, padding). Holes at `0x9CDC` and `0x9D52`, and the 12-byte footer, keep their original bytes. The reconstructed image SHA-1 is the bios0 digest above. Unplaced code is 0 bytes.

`asm/functions.txt` is the split. The cluster from `0x9E34` to `0xA49C` is the ABI-shaped code (`sts.l pr,@-r15`, `mov.l r14,@-r15`, and real `bsr`). There is no such prologue at or past `0xA6A0`. `0x9CDC` is a `bsr` target whose bytes are zero, so it is data. `0xB090` and `0xCED8` are `sts.l pr,@-r6` inside repeating data, not functions.

```
make
```

That refreshes the split, assembles every unit, links the six matched functions, and fails unless the image matches.

A clean clone cannot finish that. `make` needs the local bios0 image at `~/Documents/awbios/bios0.ic23`, the Hitachi tools extracted to `~/Documents/awbios/shc`, and the Boxedwine prefix under `~/Documents/awbios/boxedwine`. The compiler and the ROM are not in this repo.
