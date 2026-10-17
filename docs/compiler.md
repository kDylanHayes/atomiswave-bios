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
the grader. The grader is the linked halfwords against the flash. Nothing
is marked `complete`.

The compiler is not in this repo. Matched C is `FUN_09e34`, 28 bytes.
`src/services.c` also holds schedules for eight more functions. Linking
that whole file does not yet reproduce the flash, because several
callees are still missing and a `bsr` displacement depends on their sizes.

## What matched

Compared with `-show=object`, then with the linker for GBR offsets.
Internal branches are included. `bsr` immediates are not, until every
static callee has its real size.

| Flash | Bytes | Source | Result |
| --- | --- | --- | --- |
| `0x9E34` | 28 | `FUN_09e34` | linked bytes match the flash |
| `0x9E50` | 24 | `FUN_09e50` | schedule matches, including both returns |
| `0xA158` | 6 | `FUN_0a158` | `rts` with the store in the delay slot |
| `0xA15E` | 12 | `FUN_0a15e` | tail `jmp` to `0x8C0010F0` with args `(0,0,0,2)` |
| `0xA16A` | 12 | `FUN_0a16a` | same tail call with `(0,0,0,3)`. The following bytes are a literal pool, not this function |
| `0xA1D4` | 6 | `FUN_0a1d4` | stores 600 through GBR+68 in the `rts` delay slot |
| `0xA1DA` | 26 | `FUN_0a1da` | same loop schedule as `0xA354`, plus the short store |
| `0xA354` | 28 | `FUN_0a354` | exact halfwords once the callees sit at the flash distances |
| `0xA370` | 48 | `FUN_0a370` | exact schedule, including `8B0A`, `8DF0`, and `8BF6` |

`0xA354` was also checked as raw halfwords
`4F22 7FFC 2F42 BCBF 0009 B01F 64F2 6403 4411 8BF8 7F04 4F26 000B 6043`
when the first callee was `0x678` bytes before it and the second was
`0x4C` bytes after it. Those distances are the real ones: `0x9CDC` and
`0xA3A0`.

GBR variables use `#pragma gbr_base (lo)` and `#pragma gbr_base1 (hi)`.
The parenthesis form is required, and the pragma comes before the
definition. `$G0` is 128 bytes. `$G1` follows it, so a field at `hi+8`
is GBR+136. Linked checks: `C612` (GBR+72), `C619` (GBR+100), `C122`
(GBR+68), `C123` (GBR+70), `C149` (GBR+146), `C222` (GBR+136).

`_builtin_set_cr(get_cr() | 0x100000F0)` is the SR update at `0xA144`
and `0xA116`. `_builtin_set_imask(15)` is the `and`/`or #240` sequence,
and it does not clear the BL bit. The cluster's mask `0xEFFFFF0F` clears
BL as well. `_builtin_set_gbr` and `_builtin_set_vbr` accept a constant
address. `0x8C000000` is the base installed by `FUN_09e68` and the VBR
installed by `FUN_0a116`. `(int)_builtin_get_gbr() + 240` is `stc gbr`
plus a register add. `&hi.l240` is not: 112 does not fit in `add #imm`,
so the compiler emits a relocated absolute.

`FUN_09e34` is a `switch` on GBR+72. Cases 6, 7, and 9 assign `-1` to a
local; the default assigns `0`; one `return` follows. The linked body,
with `$G0` at 0, is the 28 flash bytes at `0x9E34`. An `||` chain or a
`goto` chain compiles as `bt/s` and is not this function. A `switch`
that `return`s the constant directly compiles as `rts` with that
constant in `r0`, and the flash returns through `r4`.

## What does not match yet

`FUN_09e68`, `FUN_09fbc`, `FUN_0a116`, `FUN_0a144`, `FUN_0a1f4`, and
`FUN_0a3a0` are not reproduced.

`FUN_0a3a0` uses the same `switch` shape for the 0/1/2/5/6/11/16 test.
A standalone `switch` emits plain `bt` and the flash displacements
`890D`, `890B`, `8909`, `8907`, `8905`, `8903`, `8901`. One shared
callee is cached in `r12`. Three different externs are not, but they
cannot share the flash pool `0x8C0010F0`. Constant 0 is cached in
`r13` under `-optimize=1`, `-nospeed`, `-speed`, and `-size`.

`#pragma global_register(g8=R8,g9=R9,g10=R10,g11=R11,g12=R12,g13=R13)`
reserves those registers and `FUN_09e34` still matches. Zeros become
`mov #0`, and the prologue no longer saves `r13`. What remains is
order: the flash pushes `r14` and then tests the argument; SHC tests
first. The flash epilogue is `lds.l pr`, then `mov r14,r0`; SHC writes
the `mov` first. `-nospeed` and `-size` do not swap either pair.
`FUN_09fbc` and `FUN_0a1f4` use `r8`–`r14`, so that pragma cannot cover
a translation unit that contains them. Folding the third call into
`&&` removes the stack spill and emits `tst r0,r0`. The flash is
`mov r0,r4` / `tst r4,r4`. Naming that return brings the spill back.

The decrement in flash is `extu.w r0,r0`, `tst r0,r0`, a reload, then
pool `0x0000FFFF` added into `r0`. A named unsigned temporary of a
volatile unsigned short keeps the pool, the reload, and `add` into
`r0`, but the extend is `extu.w r0,r4`. A signed store of `+ 65535`
folds to `add #-1`. An unsigned store keeps the pool. A cast used only
in the zero test is deleted, because a sign-extended short is zero in
the same cases. `-rtnext` does emit `extu.w r0,r0`, in the `rts` delay
of a function whose return type is `unsigned short`. `FUN_09e34` is
unchanged by that flag. Inlining the same return does not keep the
extend in `r0`; the caller still gets `extu.w r0,r4`.

`FUN_0a144` compiled alone has the flash `set_cr` order, zero in `r0`,
address in `r4`, and the reload in the `rts` delay. The address load
is still before `mov #0` and the GBR store. In a multi-function file
the `set_cr` pair swaps. `FUN_0a116` matches the tail `jmp` / `lds.l pr`,
the dead word reload, and `and 0xEFFFFF0F`. `sts.l pr` is first, and
the GBR+564 store is after `mov #8`. Neither schedule is promoted.

Calls to `0x9CDC`, `0x9CE2`, `0x9D52`, and `0x9DB8` are real `bsr`
instructions into bytes that are zero or erased `0xFF`. They are not
recoverable function bodies. The callers still have to land on those
addresses, which means those symbols have to occupy those offsets in
the same translation unit. An empty C function is `rts; nop`, which is
not what the flash stores there.

The boot block below `0xA00` stays assembly. Three routines are already
byte-identical: `poll_bit`, `copy_words`, and `mix_shifts`.

## Flags that were rejected

- `-cpu=sh4`: FPSCR traffic around every call. Absent from the cluster.
- `-cpu=sh4 -double=float`: warning 1302, option ignored.
- `-optimize=0`: delay slots stay `nop`. The flash fills some of them.
- `-nospeed`, `-speed`, and `-size` on top of `-optimize=1`: `FUN_09e34`
  still matches, and none of them removes the `r13` zero cache or the
  `extu.w r0,r4` decrement. The pin stays `-optimize=1` alone.
- `-rtnext`: `extu.w r0,r0` appears only in the delay slot of an
  `unsigned short` return. It does not fix the inlined decrement.
- `#pragma regsave`: saves `r8`–`r14` plus `mach` and `macl`. The
  argument test then sits after the `r14` push, which is the flash
  order, and the extra saves are not the flash.
- A one-function file with extern callees: `jsr` through a literal pool,
  not the flash `bsr`.
