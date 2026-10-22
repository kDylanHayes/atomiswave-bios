# Compiler

Hitachi SH SERIES C/C++ Compiler Ver. 5.1 (Release 04), from the Sega
Katana SDK R9 Hitachi tools. The flag set is:

```
shc -cpu=sh3 -endian=little -optimize=1
```

`-cpu=sh4` on this release writes an FPSCR clear and restore around every
call. The service cluster has no FPSCR operations, so `sh3` is the pin.
`-cpu=sh2` emitted the same integer schedule on the first probe. `sh3` is
the flag that stays. `sh-elf-gcc` is not the compiler: it pushes a
different register order and keeps 8-byte stack alignment.

Release 04 writes SYSROF, not ELF. The linker is H SERIES LINKAGE EDITOR
Ver. 6.0A. A GBR displacement is a relocation. The compiler listing shows
disp 0; the linker fills it. A `bsr` to a static function in the same
file is resolved while compiling. An extern is `mov.l` plus `jsr`.

objdiff 3.8.2 disassembles SuperH as big-endian, so its percent is not
the grader. The image gate is the linked or assembled halfwords against
the flash. `complete` stays false. The byte check does not set it.

The compiler is not in this repo. The local copy is
`~/Documents/awbios/shc`, extracted from the Katana R9 cab next to
`bios0.ic23`. `shc.exe` identifies itself as SH SERIES C/C++ Compiler
Ver. 5.1 (Release 04). Matched C is `reject_code` (28 bytes at
`0x9E34`), `retry_issue` (28 bytes at `0xA354`), and `run_transfer`
(48 bytes at `0xA370`). `reject_code` is linked on its own with `$G0` at 0.
`retry_issue` and `run_transfer` are linked together. `src/services.c` also
holds schedules for `ram_window_ready`, `set_hook`, `ram_call_2`,
`ram_call_3`, `prime_count68`, and `phase_until_clear`. Linking that whole
file does not reproduce the flash. The pin still caches a repeated 0 in a
callee-saved register, hoists the GBR install above the first push, and
keeps a promoted value across a call. Those ranges are checked assembly in
`asm/services/`. `-nospeed`, `-speed`, `-size`, `-rtnext`, and `-cpu=sh4`
stay off.

## What matched

Compared with `-show=object`, then with the linker for GBR offsets.
Internal branches are included. A `bsr` immediate matches when the static
callee's entry is at the flash distance. The callee's own body can be a
stub of that size.

| Flash | Bytes | Source | Result |
| --- | --- | --- | --- |
| `0x9E34` | 28 | `reject_code` | linked bytes match the flash |
| `0x9E50` | 24 | `ram_window_ready` | schedule matches, including both returns |
| `0xA158` | 6 | `set_hook` | `rts` with the store in the delay slot |
| `0xA15E` | 12 | `ram_call_2` | tail `jmp` to `0x8C0010F0` with args `(0,0,0,2)` |
| `0xA16A` | 12 | `ram_call_3` | same tail call with `(0,0,0,3)`. The following bytes are a literal pool, not this function |
| `0xA1D4` | 6 | `prime_count68` | loads halfword `0x65A3` from `0xA0E6` into GBR+68 in the `rts` delay slot. 600 is the halfword at `0xA2E6` and is not this load |
| `0xA1DA` | 26 | `phase_until_clear` | same loop schedule as `0xA354`, plus the short store |
| `0xA354` | 28 | `retry_issue` | linked bytes match the flash |
| `0xA370` | 48 | `run_transfer` | linked bytes match the flash |

`0xA354` was also checked as raw halfwords
`4F22 7FFC 2F42 BCBF 0009 B01F 64F2 6403 4411 8BF8 7F04 4F26 000B 6043`
when the first callee was `0x678` bytes before it and the second was
`0x4C` bytes after it. Those distances are the real ones: `0x9CDC` and
`0xA3A0`.

The build reproduces those distances in one translation unit. Section P
starts with a 4-byte static `hole_09cdc`. Then 317 unreferenced global
empty functions, a 4-byte static `prime_count68`, and 95 more empty
globals. `retry_issue` follows, then `run_transfer`, then a 4-byte static
`issue_command` that returns its argument. Empty globals stay in source
order. `retry_issue` is static and is called from the global
`run_transfer`, so the call is `bsr`. The linker places `$G0` at 0, which
fills the GBR+70 store as `C123`. `rof2bin` extracts P from `0` through
`0x6C8`. The slices at `0x678` and `0x694` are the flash bytes. The stubs
hold entry points. `prime_count68` in the image is still the 6-byte pool
load, and `issue_command` is still the 252-byte body. `phase_until_clear`
is 26 bytes at `0xA1DA` (2-mod-4). A 4-byte pad cannot place it on that
address without shifting `retry_issue`, so it stays a schedule.

GBR variables use `#pragma gbr_base (lo)` and `#pragma gbr_base1 (hi)`.
The parenthesis form is required, and the pragma comes before the
definition. `$G0` is 128 bytes. `$G1` follows it, so a field at `hi+8`
is GBR+136. Linked checks: `C612` (GBR+72), `C619` (GBR+100), `C122`
(GBR+68), `C123` (GBR+70), `C149` (GBR+146), `C222` (GBR+136).

`_builtin_set_cr(get_cr() | 0x100000F0)` is the SR update at `0xA144`
and `0xA116`. `_builtin_set_imask(15)` is the `and`/`or #240` sequence,
and it does not clear the BL bit. The cluster's mask `0xEFFFFF0F` clears
BL as well. `_builtin_set_gbr` and `_builtin_set_vbr` accept a constant
address. `0x8C000000` is the base installed by `step_phase` and the VBR
installed by `enter_ram`. `(int)_builtin_get_gbr() + 240` is `stc gbr`
plus a register add. `&hi.arg_240` is not: 112 does not fit in `add #imm`,
so the compiler emits a relocated absolute.

`reject_code` is a `switch` on GBR+72. Cases 6, 7, and 9 assign `-1` to a
local; the default assigns `0`; one `return` follows. The linked body,
with `$G0` at 0, is the 28 flash bytes at `0x9E34`. An `||` chain or a
`goto` chain compiles as `bt/s` and is not this function. A `switch`
that `return`s the constant directly compiles as `rts` with that
constant in `r0`, and the flash returns through `r4`.

## Why the other service bodies are assembly

`step_phase`, `service_main`, `enter_ram`, `quiet_interrupts`, `scan_list`, and
`issue_command` do not match under the pin. Their flash bytes are the
assembly in `asm/services/`. The notes below are why that C was not
promoted.

`issue_command` uses the same `switch` shape for the 0/1/2/5/6/11/16 test.
A standalone `switch` emits plain `bt` and the flash displacements
`890D`, `890B`, `8909`, `8907`, `8905`, `8903`, `8901`. One shared
callee is cached in `r12`. Three different externs are not, but they
cannot share the flash pool `0x8C0010F0`. Constant 0 is cached in
`r13` under `-optimize=1`, `-nospeed`, `-speed`, and `-size`.

`#pragma global_register(g8=R8,g9=R9,g10=R10,g11=R11,g12=R12,g13=R13)`
reserves those registers and `reject_code` still matches. Zeros become
`mov #0`, and the prologue no longer saves `r13`. Under
`#pragma global_register` the test still comes before the `r14` push.
The shape below does not need that pragma. The flash epilogue is
`lds.l pr`, then `mov r14,r0`; SHC writes the `mov` first.
`-nospeed` and `-size` do not swap that pair.
`service_main` and `scan_list` use `r8`–`r14`, so that pragma cannot cover
a translation unit that contains them. Folding the third call into
`&&` removes the stack spill and emits `tst r0,r0`. The flash is
`mov r0,r4` / `tst r4,r4`. Naming that return brings the spill back.

The prologue is reproducible without `#pragma regsave`. Assign 1 to
the result before the test, call two different functions from the
arms, and change the result after those calls:

```
mov.l r14,@-r15
tst r4,r4
sts.l pr,@-r15
bf/s
mov #1,r14
```

Those are the first five halfwords at `0xA3A0`. The same assignment
written inside both arms tests `r4` before the push and keeps the 1 in
a caller-saved register. A result that stays 1 is rematerialized in
the `rts` delay and never saves `r14`. The epilogue of this shape is
still `mov r14,r0` before `lds.l pr`. The flash pops `pr` first.

The full body does not keep those five halfwords. The result starts at
1, the arms call different externs, and those returns change the
result. A nested `if (ret == 0) { if (reject_code() == -1) ... }` changes
it again. SHC still caches 0 in `r13` and does not save `r12`. The
test is before the `r14` push, and the `bf/s` delay is `mov #0,r13`.

That nested test is the flash third call: `mov r0,r4` / `tst r4,r4` /
plain `bf` / `bsr` / `nop`, and it does not spill. With `r13` saved,
this body pops `pr` before `mov r14,r0`, then pops `r13`, and the
`rts` delay pops `r14`. The flash has that `lds` order and no `r13`
pop. The 0/1/2/5/6/11/16 `bt` displacements still match. A zero store
is `mov r13,r0` or `mov r13,r14`.

`step_phase` was checked against bios0, not the Ghidra file. That file
misses the `0x8C000000` GBR install, the `or.b #1,@(r0,gbr)` at
GBR+38, and the call through the `0x9D52` hole. With the service calls
compiled as `bsr`, and with every `s = 0` and `s = -1` sharing one
tail, the case bodies follow the flash: `(unsigned)lo.l48 > 0` is
`cmp/hi` against a zero register, `lo.b38 |= 1` is `mov #38,r0` /
`or.b #1,@(r0,gbr)`, `lo.l76 == 0x80` is a pool word, and the
`issue_command(0)` result is `cmp/eq #1` / `bf/s` / `mov r0,r4` /
`tst r4,r4`. Only `r14` and `r13` are saved. Repeating the stores
instead of sharing the tails caches 0 in `r13` and -1 in `r11`, and
the address of an extern called more than once occupies another
callee-saved register.

On that shared-tail candidate, `stc gbr,r3` is still hoisted in front
of the `r14` push. The same install in a small function pushes `r14`
first, then `stc gbr,r3`, then the `0x8C000000` literal, then `r13`,
then `pr`. That is the flash order. The promoted state is kept in
`r13` across the opening call. The flash uses `r3` for `cmp/pz` and
recomputes `exts.w r14,r0` after the call. Giving the promotion its
own `int` spills that `int` across the call instead of recomputing
from `r14`. `-nospeed` and `-size` do not change either choice. The
clamp is `exts.w` of `r14`, `mov.w` of GBR+146, `cmp/ge`, with no
`exts.w r0,r0`. A named short limit copies the loaded word and extends
the copy. The return reuses the `cmp/pz` value. The flash extends
`r14` again between the old-GBR reload and `ldc`.

The decrement in flash is `extu.w r0,r0`, `tst r0,r0`, a reload, then
pool `0x0000FFFF` added into `r0`. A named unsigned temporary of a
volatile unsigned short keeps the pool, the reload, and `add` into
`r0`, but the extend is `extu.w r0,r4`. A signed store of `+ 65535`
folds to `add #-1`. An unsigned store keeps the pool. A cast used only
in the zero test is deleted, because a sign-extended short is zero in
the same cases. `-rtnext` does emit `extu.w r0,r0`, in the `rts` delay
of a function whose return type is `unsigned short`. `reject_code` is
unchanged by that flag. Inlining the same return does not keep the
extend in `r0`; the caller still gets `extu.w r0,r4`.

`quiet_interrupts` compiled alone has the flash `set_cr` order, zero in `r0`,
address in `r4`, and the reload in the `rts` delay. The address load
is still before `mov #0` and the GBR store. In a multi-function file
the `set_cr` pair swaps. `enter_ram` matches the tail `jmp` / `lds.l pr`,
the dead word reload, and `and 0xEFFFFF0F`. `sts.l pr` is first, and
the GBR+564 store is after `mov #8`. Neither schedule is promoted.

Calls to `0x9CDC`, `0x9CE2`, `0x9D52`, and `0x9DB8` are real `bsr`
instructions into bytes that are zero or erased `0xFF`. They are not
recoverable function bodies. The callers still have to land on those
addresses, which means those symbols have to occupy those offsets in
the same translation unit. An empty C function is `rts; nop`, which is
not what the flash stores there.

The boot block below `0xA00` is byte-identical assembly. `poll_bit`,
`copy_words`, and `mix_shifts` were written by hand. The other boot
ranges were lifted from the flash.

## Flags that were rejected

- `-cpu=sh4`: FPSCR traffic around every call. Absent from the cluster.
- `-cpu=sh4 -double=float`: warning 1302, option ignored.
- `-optimize=0`: delay slots stay `nop`. The flash fills some of them.
- `-nospeed`, `-speed`, and `-size` on top of `-optimize=1`: `reject_code`
  still matches, and none of them removes the `r13` zero cache or the
  `extu.w r0,r4` decrement. They also leave the `step_phase` promotion
  in a callee-saved register and do not emit the redundant
  `exts.w r0,r0` after `mov.w @(disp,gbr),r0`. The pin stays
  `-optimize=1` alone.
- `-rtnext`: `extu.w r0,r0` appears only in the delay slot of an
  `unsigned short` return. It does not fix the inlined decrement.
- `#pragma regsave`: saves `r8`–`r14` plus `mach` and `macl`. The
  argument test then sits after the `r14` push, which is the flash
  order, and the extra saves are not the flash.
- A one-function file with extern callees: `jsr` through a literal pool,
  not the flash `bsr`.
