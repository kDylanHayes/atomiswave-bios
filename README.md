# Atomiswave BIOS

Byte-matching reconstruction of the Sammy Atomiswave (SYSTEM X) SH-4
boot flash, IC23. The image is 128 KiB, little-endian.

The flash has no symbol table and no original source was available. The
first bytes are the reset instruction. Function and field names in this
repo were assigned from control flow, the pinned compiler's output, and
the few surviving strings (`SYSTEM_X_APP`, the 2001 SI ELECTRONICS
copyright, the error text, `BOOTROM WRITE OK`). They are not Sammy's
identifiers. Every claim is held to the rebuilt image's SHA-1.

## Status

| | |
|---|---|
| ROM | `bios0.ic23`, 131072 bytes |
| SHA-1 | `b4c1a26bc8906d5275eb28c701dff2b9365bcdfa` |
| Matched C | **14 functions, 1200 bytes** |
| Byte-identical assembly | **14 functions, 2758 bytes** |
| Unplaced code | **0 functions, 0 bytes** |
| Gate | `make progress` rebuilds and compares the image |

`make progress` splits the ROM, assembles every unit, links the C units,
places the bytes, and fails unless the rebuilt image hashes to the
SHA-1 above.

## Layout

| Path | Contents |
|---|---|
| `src/services.c` | twelve compiler-matched C units |
| `docs/candidates/*.src` | canonicalised listings: `issue_command` 252 B, `scan_list` 352 B |
| `asm/services/` | `service_main` — the one service unit still in assembly |
| `asm/boot/` | reset, boot, exceptions, memory and bootrom code |
| `asm/data/` | literal pool, holes and footer |
| `include/awbios.h` | GBR layout and hardware constants |
| `decomp/bios0/` | Ghidra pseudocode and function index |
| `tools/` | splitter, assembler, linker, probes, progress gate |
| `docs/` | compiler evidence, service semantics, status, tooling |

## Build

```bash
make            # split, assemble, link, place, verify SHA-1
make progress   # same gate (default)
```

A clean clone cannot build by itself. It needs, outside this repo:

- `~/Documents/awbios/bios0.ic23` — the ROM image
- `~/Documents/awbios/shc` — the extracted Hitachi SHC 5.1 Release 04 tools
- `~/Documents/awbios/boxedwine` — the Boxedwine prefix that runs them

The ROM and the compiler are not committed.

## Matched C (14 units, 1200 bytes)

| Address | Bytes | Name | Built with |
|---:|---:|---|---|
| `0x9E34` | 28 | `reject_code` | SHC 5.1 R04 |
| `0x9E50` | 24 | `ram_window_ready` | SHC 5.1 R04 |
| `0x9E68` | 340 | `step_phase` | SHC 5.1 R04 |
| `0xA116` | 46 | `enter_ram` | SHC 5.1 R04 |
| `0xA144` | 20 | `quiet_interrupts` | SHC 5.1 R04 |
| `0xA158` | 6 | `set_hook` | SHC 5.1 R04 |
| `0xA15E` | 12 | `ram_call_2` | SHC 5.1 R04 |
| `0xA16A` | 12 | `ram_call_3` | SHC 5.1 R04 |
| `0xA1D4` | 6 | `prime_count68` | SHC 5.1 R04 |
| `0xA1DA` | 26 | `phase_until_clear` | SHC 5.1 R04 |
| `0xA1F4` | 352 | `scan_list` | 6.0B listing, canonicalised |
| `0xA354` | 28 | `retry_issue` | SHC 5.1 R04 |
| `0xA370` | 48 | `run_transfer` | SHC 5.1 R04 |
| `0xA3A0` | 252 | `issue_command` | 6.0B listing, canonicalised |

The twelve SHC 5.1 units compile with
`-cpu=sh3 -endian=little -optimize=1`. `issue_command` and `scan_list`
are SHC 6.0B listings whose literal-pool and schedule differences were
canonicalised before assembly; their C sources are in
`docs/candidates/`.

## Byte-identical assembly (14 units, 2758 bytes)

| Address | Bytes | Name |
|---:|---:|---|
| `0x0` | 92 | `reset` |
| `0x5C` | 164 | `boot` |
| `0x100` | 536 | `exc_general` |
| `0x318` | 56 | `mix_shifts` |
| `0x350` | 176 | `init_memory` |
| `0x400` | 108 | `exc_tlb_miss` |
| `0x46C` | 24 | `copy_words` |
| `0x484` | 180 | `set_system_bits` |
| `0x538` | 200 | `check_header` |
| `0x600` | 272 | `exc_interrupt` |
| `0x7A4` | 472 | `program_bootrom` |
| `0x97C` | 32 | `poll_bit` |
| `0x99C` | 100 | `blit_glyphs` |
| `0x9FBC` | 346 | `service_main` |

`service_main` stays assembly for its state machine and the inline
branch at `0xA0E6`. Its `SR` prologue **is** C-expressible:
`set_cr((get_cr() & 0xEFFFFF0F) | 0xF0)` compiles to the flash's
`STC SR,R0` / `AND` / `OR #240` / `LDC R0,SR`. See
`docs/open-ranges.md`.

## Documentation

| Document | Contents |
|---|---|
| [`docs/status.md`](docs/status.md) | current gate, what is genuine C, blocker |
| [`docs/compiler.md`](docs/compiler.md) | compiler pin, per-unit notes, rejected flags |
| [`docs/open-ranges.md`](docs/open-ranges.md) | research log: 6.0B recipe, allocator studies, SDK search |
| [`docs/services.md`](docs/services.md) | service-cluster semantics and GBR fields |
| [`docs/boot.md`](docs/boot.md) | boot path, memory init, bootrom handoff |
| [`docs/tooling.md`](docs/tooling.md) | Ghidra and REA versions, decompiler export |
| [`docs/kunoichi-games.md`](docs/kunoichi-games.md) | trackable NAOMI GD titles and their Kunoichi library versions |
| [`docs/atomiswave-games.md`](docs/atomiswave-games.md) | Atomiswave titles and their SystemX/Shinobi library generations |

## Notes

- `decomp/bios0/` is Ghidra pseudocode, not rebuilt source. Its byte
  counts are decompiler bodies and omit literal pools; `asm/functions.txt`
  is the byte split used by the gate.
- The Ghidra export has no file for `service_main` (`0x9FBC`) or
  `ram_call_3` (`0xA16A`).
- `bios1.ic23` differs from `bios0` in six footer bytes; the service code
  is identical.
- The SHA-1 check is the contract. Names and comments are interpretation.
