# Boot path

Checked assembly from file `0` through `blit_glyphs`. None of it is matched C. `mix_shifts`, `copy_words`, and `poll_bit` are handwritten. The other files were lifted from the flash. An AI added the names and comments after that. The flash has no symbol table. The service cluster starts at `0x9E34` and is mapped in `docs/services.md`.

Bytes that `asm/functions.txt` does not list were not linear-swept. Font, tables, and padding stay as they are in the ROM. The split has no code range from `0x710` to `0x7A4`.

| File | End | Name | What the bytes do |
| --- | --- | --- | --- |
| `0x0` | `0x5C` | `reset` | Stores `0x618066D8` at WCR2 (`0xFF80000C`) and `0x0000090D` at CCR (`0xFF00001C`). Stores `0xA677` at `0xA05F74E4`. Jumps to physical `0x5C`. |
| `0x5C` | `0x100` | `boot` | Reads every dword from `0xA0000080` while the pointer stays below `0xA000A678`. That end address is a limit. Loads SR from file `0x11C` (`0x700000F0`), copies the BSC table that follows it, and polls RFCR (`0xFF800028`) until the halfword is above 8. |
| `0x100` | `0x318` | `exc_general` | General-exception vector. Uses `r0`, `r1`, and `r2` from the interrupted code. Polls RFCR, branches over a BSC literal pool to `0x204`, calls `mix_shifts`, and branches to `init_memory`. |
| `0x318` | `0x350` | `mix_shifts` | Four `shld` steps. The pool counts are -1, -21, -31, and +1. The +1 is also the mask applied before the last shift. |
| `0x350` | `0x400` | `init_memory` | Stores constants at `0xA05F74B8`, `0xA05F7490`, `0xA05F74A0`, `0xA05F7000`, and `0xA05F7404`, then waits while bit 0 of the last word stays set. If the low two bits at `0xA0600280` are clear, branches to `check_header`. The other path uses the pool at file `0x428` through `0x440`. |
| `0x400` | `0x46C` | `exc_tlb_miss` | TLB-miss vector. Three `jsr @r1`. `r1` is incoming. Then branches to `set_system_bits`. The longs at `0x428` are `init_memory`'s pool, not this vector's arguments. |
| `0x46C` | `0x484` | `copy_words` | `r4` is the destination base, increased by `r2` once per outer trip. `r5` is the inner word count. `r6` is the outer count. `r3` is the source. |
| `0x484` | `0x538` | `set_system_bits` | ORs 5 into `0xA05F8044` and waits until Holly bit `0x2000` at `0xA05F810C` is clear. Clears bit 3 of `0xA05F80E8`, calls `poll_bit` with `r0 = 0x12C`, then sets bit 3 and fills `0x25800` dwords at `0xA5000000` with `0x528A528A`. Clears bit 3 again. If the word at `0x0CFFFFFC` is not `0xFF`, branches to `check_header`. Otherwise calls `blit_glyphs` twice and loops. |
| `0x538` | `0x600` | `check_header` | Compares four dwords at `0xAC010000` with the four dwords at file `0xA00`. A match branches to `program_bootrom`. |
| `0x600` | `0x710` | `exc_interrupt` | Interrupt vector. The `bf` after the first `dt` targets `0x5F2`, inside `check_header`. The rest fills a run and walks a table of halfwords. |
| `0x7A4` | `0x97C` | `program_bootrom` | Compares 16 dwords at `0xA0018000` with `0xAC010010`. A match goes to the handoff at file `0x8C0`. A mismatch calls `blit_glyphs` twice, clears `0x8000` dwords at `0xA0200000`, and byte-programs through `0xA0000555` and `0xA00002AA` with `0xAA`, `0x55`, and `0xA0`. Then `poll_bit` with `r0 = 0xB4`. The handoff jumps to `0xA0000000` ored with the dword at `0xAC01006C`. |
| `0x97C` | `0x99C` | `poll_bit` | `r0` is the countdown. Spins while Holly bit `0x2000` stays clear, then while it stays set, then decrements. The `bf` at the `dt` is the loop MAME replaces with a nop. |
| `0x99C` | `0xA00` | `blit_glyphs` | 16 by 16 glyph blit. A source byte is masked with `0xFF`, then `0x20` is subtracted, the result is multiplied by `0x20`, and the font base at file `0xC98` is added. A set glyph bit stores `0xFFFF`. A clear bit stores `0x528A`. The row stride is `0x500`. |

## `init_memory` pool

These longs are inside `exc_tlb_miss`, because that is the next file. `init_memory` loads them by file offset.

| File | Value | Use |
| --- | --- | --- |
| `0x428` | `0xA05F8050` | The word here is stored as 0. The next word is stored as `0x500`. |
| `0x42C` | `0xA05F8048` | The word at this address is ANDed with -9 and ORed with 8, which forces bit 3 on. |
| `0x430` | `0xA5000000` | Destination of the `0xFFFFFFFF` fill. |
| `0x434` | `0x00025800` | Number of dwords in that fill. |
| `0x438` | `0x0000046C` | Loaded into `r1`. This is the file offset of `copy_words`. The load is the end of the range. |
| `0x43C` | `0x00000500` | Loaded into `r2`. |
| `0x440` | `0x00001498` | Loaded into `r3`. |

## Handoff

The `jmp` at file `0x966` is `0xA0000000` ored with the dword at `0xAC01006C`. `program_bootrom` loads `0xAC010000` and adds `0x6C`. The Ghidra export comment names `0x01AC006C`. That address is not in this pool. `include/awbios.h` uses `0xAC01006C`.

## Footer

File `0x1A000` is twelve original bytes. bios1 differs at `0x1A003`, `0x1A004`, `0x1A006`, `0x1A007`, `0x1A008`, and `0x1A009`. No instruction in this split loads that address.
