# Status

Snapshot of the Atomiswave BIOS decompilation. The flash image is
`bios0.ic23`, 131072 bytes, SHA-1
`b4c1a26bc8906d5275eb28c701dff2b9365bcdfa`.

## Gate (`make progress`)

- matched C: **14 functions, 1200 bytes**
- byte-identical assembly: **14 functions, 2758 bytes**
- unplaced code: **0 functions, 0 bytes**
- relocation entries: 0
- the rebuilt image hashes to the same SHA-1

Matched C: `reject_code` 28, `ram_window_ready` 24, `step_phase` 340,
`enter_ram` 46, `quiet_interrupts` 20, `set_hook` 6, `ram_call_2` 12,
`ram_call_3` 12, `prime_count68` 6, `phase_until_clear` 26,
`scan_list` 352, `retry_issue` 28, `run_transfer` 48, `issue_command`
252.

Assembly: `reset` 92, `boot` 164, `exc_general` 536, `mix_shifts` 56,
`init_memory` 176, `exc_tlb_miss` 108, `copy_words` 24,
`set_system_bits` 180, `check_header` 200, `exc_interrupt` 272,
`program_bootrom` 472, `poll_bit` 32, `blit_glyphs` 100,
`service_main` 346.

## What is genuine C and what is not

- The twelve units built from `src/services.c` compile with the pinned
  SHC 5.1 Release 04 (`-cpu=sh3 -endian=little -optimize=1`).
- `issue_command` is built from `docs/candidates/issue_command_60b.src`,
  a 6.0B listing with two canonicalised blocks (pool split, countdown).
- `scan_list` is built from `docs/candidates/scan_list_60b.src`, a
  mechanical translation of the checked `asm/services/scan_list.s` into
  the SHC dialect. It is byte-exact but **not** a compiler match; the
  best C reconstruction is `docs/candidates/scan_list_60b_extern.c`
  (36-byte frame, correct call sites, 93/161 instructions identical).

## Blocker: the original compiler is unavailable

The BIOS was built with a Hitachi SHC 6.0-line compiler that is not in
any public SDK:

- 6.0B reproduces `issue_command` 252/252 only after canonicalisation,
  and compiles the best `scan_list` C to 93/161 with the parameter in
  `R13` (flash `R12`) and loop constants hoisted differently.
- 6.0AD Release04 (Kunoichi 2.02) is the only public Adria build; it
  fails `issue_command` structurally (`pr` before `tst`, `BT` instead of
  `BF/S`, different pool) and spills the whole `scan_list` frame.
- 5.0, 5.1, 6.0A and 6.0C fail in the same way as 6.0B.
- `service_main` rewrites `SR`, but that part is expressible:
  `set_cr((get_cr() & 0xEFFFFF0F) | 0xF0)` compiles to the flash's
  `STC SR,R0` / `AND` / `OR #240` / `LDC R0,SR`. It stays assembly for
  its state machine and the inline branch at `0xA0E6`.

The missing artefact is an **official Adria 6.0AD build after R04**
(R05 was planned for October 2000) or the exact 2001 build used for the
BIOS.

## Best remaining lead

**Kunoichi SDK 2.04, CD label dated 2001-03-23**, an undumped Sega
NAOMI SDK disc:

- Mercari `m14380387223`, ¥98,000
- eBay `188320099138` / `287290577333` / `227388792444`, $1,069-1,080
- 2.02 (2000-11-22) ships 6.0AD **R04**; Katana R11b (2001-02-28) still
  ships 5.1 R11, so the Kunoichi line is the only public 2001 candidate.

Before paying, ask the seller for a photo of
`doc\hitachi_tool\shc_60ad\shc_v6ad.txt` (first screen) and of the
`utl\dev\hitachi_ad` folder with dates. R04 again means skip; R05/R06 or
`shc.exe` later than 2000-08-21 means buy.

No other 2001+ NAOMI/System SP SDK disc is public or listed, and the
Atomiswave SystemX SDK/HDD remains unobtained.


## See also

- [`compiler.md`](compiler.md) — pin, per-unit notes, rejected flags
- [`open-ranges.md`](open-ranges.md) — research log and blocker evidence
- [`tooling.md`](tooling.md) — Ghidra and REA setup
- [`../README.md`](../README.md) — status table and build
