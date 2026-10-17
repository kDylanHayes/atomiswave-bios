# objdiff

`tools/bin/objdiff-cli` is objdiff 3.8.2 for macOS arm64. It is gitignored.
`objdiff.json` lists one unit per recovered function. `target_path` is an
ELF32 object whose `.text` is the flash bytes for that range. `base_path`
is the built object: checked assembly under `build/asm/`, or the linked
`FUN_09e34` object. `complete` is true only when that `.text` equals the
flash range. `tools/gen_objdiff.py` rewrites the flag from the objects on
disk.

objdiff's SuperH disassembler reads each halfword with `u16::from_be_bytes`
(`objdiff-core/src/arch/superh/mod.rs`). This BIOS is little-endian. The tool
therefore prints `.word 0x.... /* unknown instruction */` for ordinary
instructions such as `mov.l @(disp, pc), r1`. A one-byte corruption of an
object still scored 100% in 3.8.2, because every instruction was unknown on
both sides.

Flipping the first byte of `build/asm/boot/poll_bit.o` left that unit at
`matched_code` 32/32 in `objdiff-cli report`. The percent does not see the
difference.

`make progress` is the gate. It requires every code range's built `.text`
to equal flash, every built ELF to equal the extracted ELF, unmatched code
of 0 bytes, and the reconstructed image SHA-1. A newer object that no
longer matches is not assembled over. `FUN_09e34` is the only matched C:
linked with `$G0` at 0, its 28 bytes equal the flash at `0x9E34`. Every
other code range is checked assembly. The other functions in
`src/services.c` are schedules only. objdiff is not the grader for this
image.
