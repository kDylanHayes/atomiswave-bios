# objdiff

`tools/bin/objdiff-cli` is objdiff 3.8.2 for macOS arm64. It is gitignored.
`objdiff.json` lists one unit per recovered function. `target_path` is an
ELF32 object whose `.text` is the flash bytes for that range. `base_path`
is the built object: checked assembly under `build/asm/`, or a linked
object for `reject_code`, `retry_issue`, and `run_transfer`. `complete`
stays false. `tools/gen_objdiff.py` writes that flag.

`tools/sh4.py` stores the linked halfwords in an ELF32 ET_REL `.text` and
leaves the relocation section empty. A GBR displacement is already filled
(`C612`, `C123`) and a `bsr` displacement is already resolved. Setting
`complete` from that byte compare would mark a relocation-free object
done. `tools/progress.py` rejects `complete` on an object with no
relocation entries.

objdiff's SuperH disassembler reads each halfword with `u16::from_be_bytes`
(`objdiff-core/src/arch/superh/mod.rs`). This BIOS is little-endian. The tool
therefore prints `.word 0x.... /* unknown instruction */` for ordinary
instructions such as `mov.l @(disp, pc), r1`. A one-byte corruption of an
object still scored 100% in 3.8.2, because every instruction was unknown on
both sides.

Flipping the first byte of `build/asm/boot/poll_bit.o` left that unit at
`matched_code` 32/32 in `objdiff-cli report`. The percent does not see the
difference.

`make progress` is the image gate. It requires every code range's built
`.text` to equal flash, every built ELF to equal the extracted ELF, and
the reconstructed image SHA-1. A newer object that no longer matches is
not assembled over. The report then prints objdiff's percent and leaves
`complete` false. Matched C is `reject_code`, `retry_issue`, and
`run_transfer`: each linked slice equals its flash range. Every other
code range is checked assembly. The other functions in `src/services.c`
are schedules only. objdiff is not the grader for this image.
