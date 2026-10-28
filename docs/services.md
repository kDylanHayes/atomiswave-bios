# Service cluster

The ABI-shaped code is flash `0x9E34` through `0xA49C`. `reject_code`, `ram_window_ready`, `step_phase`, `enter_ram`, `quiet_interrupts`, `set_hook`, `ram_call_2`, `ram_call_3`, `prime_count68`, `phase_until_clear`, `retry_issue`, and `run_transfer` are matched C. Every other range here is checked assembly. Boot code below `0xA00` keeps the names already in `asm/boot/`.

`step_phase` installs GBR = `0x8C000000` and restores the caller's GBR before it returns. Other routines use whatever GBR the caller left. Offsets below are displacements from that base. `$G0` is 128 bytes, so the second window starts at GBR+128.

Calls to `0x8C0010F0` are a fixed RAM address. `r7` selects the call. The body at that address is not in this flash image.

`bsr` targets `0x9CDC`, `0x9CE2`, `0x9D52`, and `0x9DB8` land in erased flash (`0x00` or `0xFF`). They are not recoverable functions. The image keeps those bytes.

## Names

An AI assigned every name in this table. The flash does not contain them. `service_main` and `scan_list` describe the control flow. They are not a recovered cartridge format.

| Flash | Name | What the bytes do |
| --- | --- | --- |
| `0x9E34` | `reject_code` | Returns -1 when the word at GBR+72 is 6, 7, or 9. Otherwise 0. Matched C. |
| `0x9E50` | `ram_window_ready` | Returns 1 when GBR+100 is `0x8C008000` and GBR+76 is 32. Matched C. |
| `0x9E68` | `step_phase` | One step of the signed short at GBR+144. Matched C. |
| `0x9FBC` | `service_main` | Outer driver. Calls the others and several RAM addresses. |
| `0xA116` | `enter_ram` | Blocks interrupts, sets VBR to `0x8C000000`, calls `0x8C0006AA`, stores `0x8C000728` at GBR+564, writes 8 at `0xA05F6910`, clears the block, and jumps to `0x8C000768`. Matched C. |
| `0xA144` | `quiet_interrupts` | Blocks interrupts, stores 0 at GBR+136, stores 0 at `0xA05F6910`, and reads that word back. Matched C. |
| `0xA158` | `set_hook` | Stores `0x8C000C86` at GBR+136. Matched C. |
| `0xA15E` | `ram_call_2` | Tail call `0x8C0010F0(0, 0, 0, 2)`. Matched C. Twelve bytes. |
| `0xA16A` | `ram_call_3` | Tail call `0x8C0010F0(0, 0, 0, 3)`. Matched C. Twelve bytes. The next 94 bytes are `service_pool`, not this function. |
| `0xA1D4` | `prime_count68` | Stores 600 at GBR+68. Matched C. The halfword is at `0xA2E6`, inside `scan_list`. |
| `0xA1DA` | `phase_until_clear` | Stores `r4` at GBR+146, then calls the `0x9CDC` hole and `step_phase` until the result is `>= 0`. Matched C. |
| `0xA1F4` | `scan_list` | Walks a byte list passed in `r4`, with a bound in `r5`. |
| `0xA354` | `retry_issue` | Calls the `0x9CDC` hole and `issue_command(r4)` until the result is `>= 0`. Matched C. |
| `0xA370` | `run_transfer` | Stores 10 at GBR+70, then runs `issue_command(0)` and, on 0, `issue_command(1)`. Matched C. |
| `0xA3A0` | `issue_command` | Calls `0x8C0010F0` and counts GBR+68 and GBR+70 down. |

`service_main` and `scan_list` are still one function each.

## GBR fields the cluster actually touches

| Offset | Field | Use |
| --- | --- | --- |
| +36 | `flag_36` | Byte. `service_main` writes 0 or 2. `scan_list` compares it with 0 and 2. |
| +37 | `flag_37` | Byte. Set to 1 when GBR+228 is 1, otherwise 0. |
| +38 | `flag_38` | `step_phase` sets bit 0 with `or.b #1`. `service_main` tests the byte. |
| +48 | `word_48` | Compared with 0, 1, 2, 5, 6, 11, and 16. Also passed by pointer. |
| +64 | `saved_64` | Return value of the `r7 = 0` RAM call. Passed as `r4` when `r7 = 1`. |
| +68 | `count_68` | Short counter. `prime_count68` reloads it. `issue_command` adds `0xFFFF`. |
| +70 | `count_70` | Short counter. `run_transfer` stores 10. `issue_command` adds `0xFFFF`. |
| +72 | `code_72` | Word tested by `reject_code`. Passed by pointer with `r7 = 4`. |
| +76 | `word_76` | Compared with 32 and with `0x80`. |
| +100 | `ptr_100` | Pointer. Compared with `0x8C008000` and passed to RAM calls. |
| +136 | `hook_136` | `set_hook` stores `0x8C000C86`. `quiet_interrupts` stores 0. |
| +144 | `phase_144` | Signed phase for `step_phase`. |
| +146 | `limit_146` | Signed limit. If the new phase is `<` this value, the phase becomes 0. |
| +156 | `word_156` | Passed as `r5` to `0x8C000598` from `scan_list`. |
| +228 | `mode_228` | Compared with 1 and 3 by `service_main`. |
| +232 | `result_232` | Return value of the `r7 = 1` RAM call. |
| +236 | `cmd_236` | Passed as `r4` to the `r7 = 0` RAM call. The stores are 17, 24, and 28. |
| +240 | `arg_240` | Passed as `r5` to the `r7 = 0` RAM call (`GBR+0xF0`). |
| +244 | `arg_244` | Stored as 1, or as a shifted sum, before that call. |
| +248 | `arg_248` | Pointer stored next to the command word. |
| +252 | `arg_252` | Often 0. `scan_list` also stores a list offset here. |
| +564 | `ptr_564` | `enter_ram` stores `0x8C000728`. |

## `0x8C0010F0`

| `r7` | Arguments in the flash | Caller |
| --- | --- | --- |
| 0 | `(GBR+236, GBR+240, 0, 0)` | `issue_command` when `r4` is 0 |
| 1 | `(GBR+64, GBR+48, 0, 1)` | `issue_command` when `r4` is not 0 |
| 2 | `(0, 0, 0, 2)` | `ram_call_2` |
| 3 | `(0, 0, 0, 3)` | `ram_call_3` |
| 4 | `(GBR+72, 0, 0, 4)` | `issue_command` after a result other than -1 |

`issue_command` then counts. If its result is 1 or -1 and GBR+68 is not 0, it adds `0xFFFF` to GBR+68 and returns -1. If GBR+68 is 0 and GBR+70 is not 0, it adds `0xFFFF` to GBR+70, calls `prime_count68`, and returns -2.

## `step_phase`

The short at GBR+144 is sign-extended. If it is negative, the function first calls `ram_call_2`. It then branches on that same short:

| Phase | Effect before the clamp |
| --- | --- |
| -8 | Calls `0x8C0004F4` with GBR+100 in `r4`. A 0 result sets the phase to 0. Any other result sets it to 126. |
| -7 or -4 | `issue_command(1)`. -2 subtracts 2 from the phase. 0 runs `ram_window_ready` and `reject_code`. |
| -6 or -3 | `issue_command(0)`. A result of 1 sets the phase to -1. 0 reloads GBR+68 and subtracts 1 from the phase. |
| -5 | Calls `0x8C0005B8` with `r4 = 0x8C000FC4`, copies GBR+100 to GBR+248, calls `prime_count68`, sets the phase to -6, and falls into the -6 path. |
| -2 | Stores 24 at GBR+236, calls `prime_count68`, sets the phase to -3, and falls into the -3 path. |
| -1 | If GBR+48 is greater than 0, the phase becomes that word. Otherwise it becomes 127. |
| any other value, including 0 | Calls the erased hole at `0x9D52`, sets bit 0 of GBR+38, stores 10 at GBR+70, and sets the phase to -2. |

The clamp compares the new phase with GBR+146. A phase below that limit becomes 0. If the phase is then `>= 0`, the function calls the erased hole at `0x9DB8`. It stores the phase back to GBR+144 and returns it.

`0x8C0004F4` and `0x8C0005B8` are the addresses in the instruction stream. They are also the file offsets of instructions inside `set_system_bits` and `check_header`. This file does not show a copy of the flash to `0x8C000000`.

## What is still not matched C

`step_phase` is matched C. Its unit compiles the real `ram_window_ready` immediately before the body, so the literal `0x8C008000` parks at `0x9EFC`. Six-byte gaps and empty globals put the backward callees at the flash distances. Three unreferenced add-chains keep the end pool inside the 340 bytes and put `ram_call_2`, `prime_count68`, and `issue_command` at the forward distances. `rof2bin -v=00 -e=270` fills the two reserved alignment halfwords with zero and keeps the prefix plus the body. The object is the slice at `0x11C`. Those helpers are not in the flash. The phase unit's `step_phase` remains a 4-byte stub.

`service_main` and `scan_list` were compiled with the pinned flags and do
not equal the flash. The scheduler caches a repeated 0 in a
callee-saved register, hoists the GBR install above the first push, and
keeps a promoted value across a call. The pin was not changed. Those two
ranges stay checked assembly. `issue_command` is now matched: SHC 6.0B, a
corrected source structure (the third call is inside the `else` arm), and
a canonicalised `.src` that splits the compiler's merged pool at the first
`bra` and re-schedules the countdown. See `docs/open-ranges.md`.

`retry_issue` and `run_transfer` are matched C. The link unit gives their static callees the flash distances: an empty `hole_09cdc`, 317 empty globals, an empty `prime_count68`, 95 empty globals, then the two functions, then `issue_command` as `return arg`. Those stubs are 4 bytes. They hold the call sites in place. The real `issue_command` is the 6.0B unit at `0xA3A0`. The real `prime_count68` is matched in its own unit.

`phase_until_clear` is matched C in its own unit. The unit's `step_phase` is a 4-byte stub, and a 6-byte `gap_six` fills the `prime_count68` slot so the function starts at `0xA1DA`. Those are distances, not the real bodies.

`set_hook` and `ram_window_ready` are matched C. Each unit places a second mention of the same literal after a run of empty functions, so the forward `mov.l` displacement matches the flash. Those second functions are not in the image.

`ram_call_2` and `ram_call_3` are matched C. They share one unit. `gap_six` (`return value + 1`, 6 bytes, no pool) occupies the `set_hook` slot so both functions start 2-mod-4, and 22 empty globals place `0x8C0010F0` at offset `0x78`. That is flash `0xA1D0` when the unit is imagined to start at `0xA158`. `gap_six` and the pads are not flash functions. The image bytes from `0xA176` through `0xA1D4` stay in `asm/data/service_pool.s`.

`quiet_interrupts` is matched C. `gbr_write_long(136, 0)` puts the zero in `r0` and leaves the address load after that store. Returning the volatile word puts the reload in the `rts` delay. The link unit names `0x100000F0`, `0x8C000000`, `0x8C0006AA`, and `0x8C000728` first, so `0xA05F6910` is the fifth pool word. Twenty-three empty globals put that pool at offset `0x88`. The function itself starts at offset `0x18`. `rof2bin -e=2C` keeps the prefix plus the 20 bytes, and the object is the slice at `0x18`. Those prefix functions and the pads are not in the flash. The real pool bytes stay in `service_pool`.

`enter_ram` is matched C. The body is the SR block, `set_vbr`, the call through `0x8C0006AA`, `gbr_write_long(564, 0x8C000728)`, the store of 8 and the dead reload at `0xA05F6910`, the SR clear, and the tail jump through `0x8C000768`. Compiled at a 0-mod-4 entry, this compiler saves `pr` first and loads the port address before `mov #8`. Fifteen 6-byte functions return the pool words from `0xEFFFFF0F` through `0x8C008100`, so the real function starts at offset `0x5A`. That is 2-mod-4, and the schedule then matches the flash: `stc sr`, the mask load, `sts.l pr`, and the GBR+564 store before `mov #8`. Thirteen empty globals put the pool at offset `0xBC`. `rof2bin -e=88` keeps the prefix plus the 46 bytes, and the object is the slice at `0x5A`. The prefix and the pads are not in the flash. The real pool bytes stay in `service_pool`.

`prime_count68` is matched C. `mov.w @(disp,PC)` zero-extends the 8-bit displacement. At `0xA1D4` the displacement is `0x87`, so the load address is `0xA1D8 + 0x10E = 0xA2E6`. That halfword is `0x0258`, which is 600. It sits in `scan_list`, between a `bra` and its target, so those bytes are not executed. The link unit's 67 empty globals exist to put the compiler's copy of that halfword at the same displacement. `rof2bin -e=6` keeps the function. The flash halfword stays in `scan_list`.

`service_main` loads its literals from `service_pool`, file `0xA178` through `0xA1D0`. The halfword at `0xA0E6` sits in `service_main`, between a `bf` and its target. When `r11` is 0 those bytes execute: `mov r10, r5`, then `bra` over the following load of `r5`, with `add #16, r5` in the delay slot. `r5` is then `r10 + 16`. When `r11` is not 0, the `bf` skips them and `r5` is the pool constant `0xB06E`. `r4` is `0x8C010000` on both paths. A sign-extended reading of `prime_count68`'s displacement lands on this `0x65A3`. The CPU does not. The displacement is zero-extended.
