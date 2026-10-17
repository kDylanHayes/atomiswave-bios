# objdiff

`tools/bin/objdiff-cli` is objdiff 3.8.2 for macOS arm64. It is gitignored.
`objdiff.json` lists one unit per recovered function. `target_path` is an
ELF32 object whose `.text` is the flash bytes for that range. `base_path` is
set only for the three assembly files under `asm/boot/`. `complete` is false
on every unit.

objdiff's SuperH disassembler reads each halfword with `u16::from_be_bytes`
(`objdiff-core/src/arch/superh/mod.rs`). This BIOS is little-endian. The tool
therefore prints `.word 0x.... /* unknown instruction */` for ordinary
instructions such as `mov.l @(disp, pc), r1`. A one-byte corruption of an
object still scored 100% in 3.8.2, because every instruction was unknown on
both sides.

Flipping the first byte of `build/asm/boot/poll_bit.o` left that unit at
`matched_code` 32/32 in `objdiff-cli report`. The percent does not see the
difference.

The ROM byte check in `tools/as_sh.py --check` is the gate for
`mix_shifts`, `copy_words`, and `poll_bit`. `make progress` also requires
each built ELF to be byte-identical to the extracted ELF. Those matches are
assembly. They are not matched C. `FUN_09e34` in `src/services.c` is
matched C: linked with `$G0` at 0, its 28 bytes equal the flash at
`0x9E34`. The other functions in that file match as schedules only.
`complete` stays false. objdiff is not the grader for this image.
