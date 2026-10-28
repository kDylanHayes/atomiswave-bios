# Open ranges

Three code ranges are still checked assembly. Everything else is either
matched C or byte-identical boot assembly.

| Flash | Bytes | Name | Assembly |
| --- | --- | --- | --- |
| `0x9FBC` | 346 | `service_main` | `asm/services/service_main.s` |
| `0xA1F4` | 352 | `scan_list` | `asm/services/scan_list.s` |
| `0xA3A0` | 252 | `issue_command` | `asm/services/issue_command.s` |

`issue_command` has had the most compiler work, so it is the worked
example below. The other two use the same ABI-shaped code and are
expected to hit the same scheduler difference, but they have not been
taken to the same instruction-level diff.

## Probing one function

`tools/probe_function.py` compiles one C file with the pin, links one
object with section P at 0, runs `rof2bin`, and prints the linked bytes
next to the flash slice. It does not touch `build/` and claims no unit.

```
python3 tools/probe_function.py docs/candidates/issue_command.c issue_command A3A0 FC
python3 tools/probe_function.py --selftest
```

`--selftest` compiles `reject_code` at `0x9E34` and checks its 28 bytes.
That unit needs no distance fillers, so it also checks the tool itself.

`--define SYM=HEX` adds a linker `DEFINE` line:

```
python3 tools/probe_function.py cand.c issue_command A3A0 FC --define _ram_fn=8C0010F0
```

`DEFINE` is an H SERIES LINKAGE EDITOR subcommand
(`DEFINE <import symbol>(<address>)`, hexadecimal, no `0x`). It resolves
an extern to an absolute address. An extern call is `mov.l` + `jsr @rN`
with one literal per call site, so the address is not cached in a
callee-saved register. The `start P/0,$G0/0` line prints `** 202` on
every link; that message is normal and the absolute file is still
written.

## issue_command

`docs/candidates/issue_command.c` is the closest schedule found. It
matches the flash for **109 of 118 instructions**: prologue, both call
arms, the 0/1/2/5/6/11/16 `bt` chain, the `r7 = 4` call, the
`bsr reject_code` test, the shared tail, and the
`lds.l pr` / `mov r14,r0` / `rts` / `mov.l @r15+,r14` epilogue.

Three things keep it from the flash.

### 1. The literal pool is not flushed after the first `bra`

The flash puts `0x00F0` and `0x8C0010F0` at `0xA3C8`/`0xA3CC`, between
the `bra 0xA458` at `0xA3C4` and the `0xA3D0` arm. That pool also pads
the arm label to 16 bytes. SHC 5.1R04 keeps those literals at the end of
the function, so `0xA3D0` arrives 8 bytes early and every forward
displacement is short. With `-align16` the compiler pads the gap with
`nop` instead of the pool.

### 2. The third call loads its target one slot early

Flash:

```
mov #4,r7
mov.l 0xA494,r3
mov #0,r6
```

Probe:

```
mov.l 0xA000,r3
mov #4,r7
mov #0,r6
```

One instruction swap, same registers. Extern + `DEFINE` gives the same
order.

### 3. The countdown reloads `0xFFFF` per branch and extends

Flash at `0xA464`:

```
mov.w @(68,gbr),r0
extu.w r0,r0
tst r0,r0
bt 0xA478
mov.w @(68,gbr),r0
mov.l 0xA498,r2
add r2,r0
mov.w r0,@(68,gbr)
bra 0xA48C
mov #-1,r14
mov.w @(70,gbr),r0
extu.w r0,r0
tst r0,r0
bt 0xA48C
mov.w @(70,gbr),r0
mov.l 0xA498,r3
add r3,r0
bsr 0xA1D4
```

The probe:

```
mov.l 0xA000,r4          <- one hoisted copy for both branches
mov.w @(68,gbr),r0
tst r0,r0                <- no extu.w
...
add r4,r0
...
mov.w @(70,gbr),r0
tst r0,r0
...
add r4,r0
```

Both flash loads read the same pool slot (`0xA498 = 0xFFFF`), so this is
constant re-materialisation, not two different literals. SHC 5.1R04 at
`-optimize=1` always hoists a repeated constant into one register and
drops the redundant `extu.w`.

Source shapes tried against this block, all with the same result:
`!= 0`, `> 0`, `(unsigned)`, `(unsigned short)`, an `int`/`short`
temporary, `goto` vs `else if`, `do { } while (0)`, `#pragma inline`
helpers taking `unsigned short`, signed vs unsigned fields, `volatile`
fields, and `+= 0xFFFF` vs `= x + 0xFFFF` vs `65535` vs `0xFFFFu`.
`-cpu=sh2` gives the same schedule as `sh3`; `-size`, `-speed`,
`-noloop`, `-align16`, `-goptimize`, `-case=table`, `-lang=cpp`, and
`-inline` do not change the hoist; `-align16` only adds `nop` padding.

The `extu.w` does have a source: a `switch` on an `unsigned short`
converts the value with `EXTU.W`. A switch with `case 0` and a
`default` body gives

```
MOV.L  L,R5            ; one hoisted 0xFFFF, still shared
MOV.W  @(68,GBR),R0
EXTU.W R0,R0
CMP/EQ #0,R0
BT     next
```

so the extend matches and the compare does not (`CMP/EQ #0` instead of
`TST`), and the constant is still shared. `if` on the same field gives
`TST` and no extend. No shape produced both the extend and the `TST`.

`-optimize=0` does reload the constant per branch, but it also spills
locals to the stack and leaves `nop` in the delay slots. The flash has
the `-optimize=0` constant handling with filled delay slots and register
locals, which is a combination the pin does not emit. Together with the
`TST`-after-`EXTU.W` form, that points at a different SHC release rather
than a different source text for this block.

## Toolchain versions tested

The Sega Katana discs and the Naomi SDK archive hold several Hitachi
compiler releases. Each was run on
`docs/candidates/issue_command.c`:

| Compiler | Result |
| --- | --- |
| SHC 5.0 Release32 | identical bytes to the pin |
| SHC 5.1 Release01 | identical |
| SHC 5.1 Release04 | the pin |
| SHC 5.1 Release08 | identical |
| SHC 5.1 Release11 (Katana R10) | identical |
| SHC 5.1 Release13 (post-R11 Sega drop) | identical |
| SHC 6.0A (HEW 6.0A) | identical |
| SHC 6.0 AD Release04 | incomplete package, no code generator |
| SHC 7.1.04 (HEW 7.1) | different family: stack spills, see below |
| SHC 9.00.01 (HEW 9.0.1) | different family: stack spills |

So the release alone is not the difference up to 6.0A.

The Renesas HEW packages (SHC 7.1.04 and 9.00.01) reject
`#pragma gbr_base` under the default `-gbr=auto`; they need `-gbr=user`.
With that flag they compile, but the result is a different code shape:
`mov.l r14,@-r15`, `sts.l pr,@-r15`, `add #-4,r15`, the function pointer
spilled to the stack, and `240` built as `mov #-16` + `extu.b`. That is
not the flash. SHC 8.0.05 is packed in an InstallShield X self-extractor
that unshield, i6comp, and ISx cannot read.

SHC 5.1R11 with `-goptimize` but a plain `LNK` link is closer still:
the first call arm and the following blocks take the flash order
(`mov r7,r6`, `add r3,r5`, `mov.l @(236,gbr),r0`, `mov.l` of the callee,
`jsr`). The literals stay in one pool after the last branch instead of
the flash's two pools at `0xA3C8` and `0xA494`, the third call still
loads its literal one slot early, and the countdown still hoists
`0xFFFF` and emits `CMP/EQ`-free `TST` without `EXTU.W`.

`-align16` aligns the arm label to `0xA3D0` (the flash's `bf/s`
displacement `0x13`) but pads every other post-branch label with `nop`,
which the flash does not have.

The Naomi and Katana R10 discs also ship `OPTSH.EXE`, the SH series
inter-module optimizer, and `OPTLNKSH.EXE`, which runs it before the
link. `-goptimize` emits the data it consumes. On `-goptimize` plus
`OPTLNKSH`:

- the first call arm follows the flash order (`mov r7,r6`,
  `add r3,r5`, `mov.l @(236,gbr),r0`, `mov.l` of the callee, `jsr`);
- the optimizer reallocates the result from `r14` to `r4`, so the flash
  `mov.l r14,@-r15` prologue disappears and the epilogue stops matching;
- the countdown keeps one hoisted `0xFFFF` and still emits `CMP/EQ #0`.

The twelve matched functions were linked without the optimizer, so a
build that used `-goptimize` everywhere would not have produced the
flash `r14` schedule. The optimizer is therefore not the missing stage
for this function.

The flash countdown needs a compiler that materialises `0xFFFF` in each
branch and emits `EXTU.W R0,R0` before `TST`. None of Releases 01, 04,
08, or 11 does that at `-optimize=1`, with or without `-goptimize`.

## Compiler recovered: SHC 6.0B

The missing build is the standard **SH SERIES C/C++ Compiler Ver. 6.0B**.
It was recovered from Hitachi's 2002 updater, archived by the Wayback
Machine:

```
http://www.hitachisemiconductor.com/sic/jsp/japan/eng/pdf/mpumcu/tool/cross/updater/v6bpatch.exe
https://web.archive.org/web/20020213204547id_/http://www.hitachisemiconductor.com:80/sic/jsp/japan/eng/pdf/mpumcu/tool/cross/updater/v6bpatch.exe
```

The exe is a `DIFFMAKE` self-applying patch, not a CAB. Its overlay holds
two complete patch sets: the lowercase names update 6.0 -> 6.0A, the
uppercase names update 6.0A -> 6.0B. Each `Diff` record is

```
"Diff" u32 version u32 old_crc u32 new_crc
u32 old_size u32 new_size u16 year u16 month_day
u8 hour u8 minute u8 second
name\0 dir\0 subdir\0
records...
```

with records `u16 n`: `0x8000` = unchanged, high bit set = copy
`n & 0x7fff` bytes from old + `u32` offset, otherwise copy the next `n`
literal bytes. Applying the 6.0A set to the 6.0A files and checking the
6.0B CRCs reconstructs the whole 6.0B toolchain (103 files, including
`SHC.EXE`, `SHCGEN.EXE`, `SHCASM.EXE`, `SHCFRT.EXE`).

6.0B is the compiler that matches the cluster's prologue and first call
arm. Its `.src` for `issue_command` matches the flash for the first 71
instructions, including the double `mov r0,r4`, the split literal pools,
and the `0x00F0` pool immediately after the first `bra`.

Two exact-byte blockers remain:

1. **Inline pool after a conditional branch.** The compiler emits
   `.DATA.W 0x00F0` / `.DATA.L 0x8C0010F0` at offset `0x28`, after the
   `bra` at `0x24` and before its target at `0x30` — the flash layout.
   `asmsh` accepts the `.DATA` but relocates the pool to the section end.
   Forcing it inline with `.RES.W 1` / `.DATA.W 0` and adjusting the
   references produces `ILLEGAL DATA AREA ADDRESS` at the `.DATA.L` and
   at the `MOV.L` that references it. The same failure occurs with
   asmsh 4.0, 5.0A, 5.0B, 5.1 and 7.00.01, and with `.POOL`/`.NOPOOL`.
   A minimal `.DATA` block after an unconditional branch assembles
   inline; adding any earlier conditional branch (`BF`, `BF/S`, `BT`)
   makes the inline pool illegal. The compiler's machinecode path also
   moves the pool. This is an assembler limitation, not a C-source
   difference.
2. **Countdown schedule.** 6.0B with a named temporary emits
   `EXTU.W R0,R5` + `TST R5,R5` and hoists one `0xFFFF` load; the flash
   extends in place (`EXTU.W R0,R0`), reloads the counter, and loads
   `0xFFFF` inside each branch. 6.0AD R4 sinks the constant per branch
   but saves `pr` before `tst r4,r4` and differs throughout the first
   arm, so it is not the build.

The 6.0B tree is staged at `probe60b` in the BoxedWine drive; the
6.0C section below is retained as history, since 6.0B and 6.0C share
the same codegen on this function.

Both blockers were subsequently resolved for `issue_command` by the
canonicaliser plus `tools/as_shc_src.py`; see "issue_command closed"
below. They still apply to `service_main` and `scan_list`.

## Compiler identified: SHC 6.0C

The standard **SH SERIES C/C++ Compiler Ver. 6.0C.001** was the closest
standard build before 6.0B was recovered. It is present in
`~/Downloads/renesas-xfer` as `REN_shv60c0u_UCM_20051110_1.exe` (the
6.0C update over 6.0A); the Katana discs only carry 5.1 and the Adria
6.0AD line.

Install layout: the update's `E_Toolchains/Sh/6_0_a/BIN` replaces the
6.0A compiler, and the 6.0A package supplies `include` and `LIB`.
Build:

```
SHC.EXE file.c -cpu=sh3 -endian=little -optimize=1 -code=asmcode
asmsh.exe file.src -cpu=sh3 -endian=little -object=file.obj
optlnk.exe file.obj -form=absolute -entry=_issue_command -start=P/0 -output=file.abs
```

On `issue_command` the compiler now reproduces, in its `.src`:

- the flash prologue `mov.l r14` / `tst r4,r4` / `sts.l pr` / `bf/s`
  (5.1 order, which 6.0AD could not produce);
- the whole first arm in flash order, including the double `mov r0,r4`;
- a literal pool immediately after the first `bra` containing
  `.DATA.W 0x00F0` and `.DATA.L 0x8C0010F0` — the flash's `0xA3C8`
  pool — and a second pool with `0x8C0010F0` and `0xFFFF`.

The two remaining gaps are at the assembler/optimizer level:

1. `asmsh` (4.0, 5.0A and 5.0B all tested) relocates the referenced
   `.DATA` pool to a later pool site (object offset `0x7C` instead of
   the compiler's `0x2A`) and merges the end pool; the flash keeps the
   first pool at `0xA3C8`. A tiny `.DATA` after a `bra` does stay
   inline, so the assembler is choosing a different pool site for the
   function, not ignoring `.DATA` outright.
2. The countdown still hoists `0xFFFF` into a register and omits
   `EXTU.W`; the flash reloads it per branch with `EXTU.W R0,R0` /
   `TST R0,R0`. 6.0AD R4 produced that pair but with the wrong prologue.

`optlnk -optimize=register|branch|speed` does not change either, and
`-goptimize` plus `optlnk` keeps the hoisted countdown (`tst`, no
`extu.w`). Countdown source forms tried on 6.0C: `if (c)`, casts to
`unsigned short`/`unsigned`, a named `unsigned short` temporary, and
`switch (c)`. Only `if (c > 0)` emits `EXTU.W R0,R0`, and it uses
`CMP/PL`, not `TST`. Two call sites through different function-pointer
types still share one literal, so the flash's duplicated `0x8C0010F0`
is not a prototype effect.

## Fingerprint corpus

`docs/candidates/corpus.c` holds 26 small functions, each isolating one codegen trait seen in the
service cluster: pool placement around a `bra`, a repeated constant in
sibling branches, a `switch` on an `unsigned short`, a named `unsigned
short` temporary, the countdown shape, the first call arm, two calls to
one cast pointer, `GBR+240`, and so on.

Each was compiled with every staged build at `-cpu=sh3 -endian=little
-optimize=1`, plus Release13 with `-align16` and with `-goptimize`, and
the listings were normalised and hashed per function.

Result:

- All eight compilations (5.0R32, 5.1R01/R04/R08/R11/R13, 6.0A, and
  R13 `-goptimize`) produce the **same code for every function**. The
  only divergence is R13 `-align16`, which adds label padding.
- The flash's two distinctive traits never appear in any of them:
  a literal pool flushed immediately after an unconditional branch, and
  `EXTU.W R0,R0` followed by `TST`.
- The traits that do appear (double `mov r0,r4`, the `r14`-first
  prologue) show up only in the first-call-arm function.

A `switch` on an `unsigned short` gives `EXTU.W R0,R0` with
`CMP/EQ #0`; an `if` gives `TST` without the extend. The countdown
function always hoists one copy of `0xFFFF`. So the pool split and the
extend/compare pair are outside this compiler family's codegen envelope,
not a release or source-shape difference.

## Compiler identified: SHC 6.0AD

The Kunoichi SDK 2.02 (NAOMI port of Dreamcast SDK 2.02J, November
2000) ships **SH SERIES C/C++ Compiler Ver. 6.0 AD (Release04)** in
`utl/dev/hitachi_ad/`. It is the successor to SHC 5.1 and is run through
the Adria backend:

```
set SHC_LIB=<dir>\hitachi_ad
set SHC_INC=<dir>\hitachi_ad\include
set ADRIA_CMD_CONFIGFILE_C=<dir>\hitachi_ad\we2_c_shcross.cfg.ver3
shc.exe file.c -cpu=sh3 -endian=little -optimize=1 -size -code=asmcode
```

Two things matter for this cluster:

- This build crashes in `adr_objout.c`/`adr_asmout.c` on
  `#pragma gbr_base1` (`$G1`). A single `#pragma gbr_base (gbr)` struct
  covering both windows compiles, because every access is still
  `@(disp,gbr)` with the same displacement. `docs/candidates/issue_command_ad.c`
  is the 6.0AD variant.
- On `-size` it emits the two traits that SHC 5.1 never produced:

```
MOV.W  @(68,GBR),R0
EXTU.W R0,R2
TST    R2,R2      ; the flash has EXTU.W R0,R0 / TST R0,R0
...
MOV.L  L+8,R3     ; 0xFFFF loaded again in each branch
```

So the countdown's per-branch `0xFFFF` and the `EXTU`/`TST` pair are
6.0AD codegen, not 5.1. The remaining differences are the register
chosen for the extended value (`R2` vs `R0`), the prologue order
(this build saves `pr` before testing `r4`; the flash tests first), and
the single end pool instead of the flash's two pools.

The build in Kunoichi 2.02 is an **evaluation** release (the Adria
release note says so) and still has the `$G1` crash. Its prologue is
`mov.l r14` / `sts.l pr` / `tst r4,r4` for every tested flag
(`-size`, `-speed`, `-optimize=0/1`, `-noloop`, `-macsave=0`,
`-noalign16`, `-case=ifthen`); the flash tests `r4` before saving
`pr`. It also allocates the countdown's extend to `R2` and copies back
to `R0`, while the flash extends in place.

6.0AD R4 also does not reproduce `reject_code` (a 5.1-matched unit):
it returns through `R2` with a `mov r0,r2` per comparison, where the
flash returns through `R4` like 5.1. So the BIOS either mixes 5.1 and
6.0AD objects (Sega shipped mixed-toolchain objects in this SDK) or
the three ranges come from the **standard SHC/C++ 6.0** line. The
Adria release note names that product directly: for ELF/DWARF and the
full compiler use "SHC/C++ Ver.6.0 R03", and refers to the
"SHC/C++ V6.0 R04b" list. That standard 6.0 build is the one to test
next; it is not in the Katana or Kunoichi discs. The iteration harness is
`adloop.py` (compile with 6.0AD, diff against the flash) and
`cmpsrc.py` (diff the `.src` listing); the candidate is
`docs/candidates/issue_command_ad.c`.

## issue_command closed with SHC 6.0B

The 6.0B source compiles the flash instruction stream once the third
call is placed inside the `else` arm and the countdown uses a named
temporary. Two post-compile steps close the remaining bytes:

1. **Pool split.** 6.0B emits one merged pool at `0x7A`. The flash has
   a pool at `0x28` (word `0x00F0`, pad, `0x8C0010F0`) and one at
   `0xF4` (`0x8C0010F0`, `0xFFFF`). The canonicaliser moves the block
   to `0x28` and duplicates the shared `0x8C0010F0`.
2. **Countdown canonicalisation.** 6.0B hoists one `0xFFFF` and tests
   through `R5`; the flash loads `0xFFFF` in each branch and extends in
   place. The canonicaliser rewrites only that block.

`tools/as_shc_src.py` assembles the canonicalised `.src` linearly,
honouring the pool site; every Hitachi `asmsh` rejects it because the
pool lies between a conditional branch and its target. The source is
`docs/candidates/issue_command_60b.c`, the canonicalised listing is
`docs/candidates/issue_command_60b.src`, and the result is 252/252
bytes. Recompiling the C source with 6.0B reproduces the pre-canonical
listing; the checked-in `.src` is that listing after the two steps
above. `make progress` reports 13 C functions / 848 bytes with the same
SHA-1. `service_main` and `scan_list` still stay assembly.

## What would close the remaining two

- The same 6.0B pipeline applied to a reconstructed `service_main` and
  `scan_list` C source. The best `scan_list` candidate is
  `docs/candidates/scan_list_60b.c`. A struct-pointer source shape makes
  6.0B emit the flash's indexed loads (`mov #25,r0 ; mov.b
  @(r0,r14),...`), and 113 of the flash's 161 instructions align. The
  remaining gap is the callee-saved allocation: `list` goes to `R13`
  (flash `R12`), `p`/`entry` to `R12` (flash `R13`), `saved`/`0x6DDD0`
  to `R10`/`R9` (flash `R9`/`R10`), and the
  `0x8C000598`/`0x8C000800` callbacks are cached instead of reloaded
  from the pool. 5.0, 5.1, 6.0A/B/C and 6.0AD all fail this allocation
  in the same way (6.0AD spills the frame). Closing it with a
  canonicaliser means rewriting the loop's register assignment and call
  schedule, not a small peephole. `service_main` was not reconstructed;
  its 346-byte state machine needs the same source-level work.
- An assembler that keeps a referenced `.DATA` pool inline when the
  pool lies between a conditional branch and its target; this is the
  toolchain limitation now worked around by `tools/as_shc_src.py`.

The image SHA-1 stays `b4c1a26bc8906d5275eb28c701dff2b9365bcdfa`.

## Search round 2: the SystemX SDK and a corrected 6.0AD test

The 2001 BIOS is SI Electronics "System X" Version 01.00. The SDK that
built it was never public, so this round chased the artefacts and the
people around it:

- **Katana SDK R11b (2001-02-27)** ships `Utl/Dev/Hitachi/shc.exe`
  version **5.1 (Release11)**, PE date 2000-02-08. The public Katana
  line ends there and never carries a 6.0 compiler
  (`sega-dreamcast-katana-sdk-r11b-inventory`).
- **Naomi SDK 001002** (2000-10-02) carries only the 5.0/5.1 tool
  packages (`pcv5r*.zip`, `sgiv5r*.tgz`). **Kunoichi SDK 2.02** is the
  only public Sega SDK with 6.0AD, and it is R04.
- The **Atomiswave dev kit HDD** (NeoTurfMasta, 2017) was promised for
  release but no image is on archive.org under `GDIMG`, SystemX,
  Atomiswave, or the owner's name. The 2020 Dreamcast-Talk "katana
  files" thread is a Take the Bullet prototype HDD, not an SDK.
- The Adria package identifies itself as product `P-HAP4ADRIA`, config
  `V00-02` (`we2_c_shcross.cfg.ver3`). Neither string is indexed
  anywhere public.

**6.0AD needs `ADRIA_CMD_CONFIGFILE_C`.** Without it `badria_SHCROSS`
prints "Object not created" for every input, including a two-line test
file, and reports no error. With
`ADRIA_CMD_CONFIGFILE_C=C:\...\we2_c_shcross.cfg.ver3` it compiles.
Earlier 6.0AD probes that failed silently should be re-read with that in
mind; the results below are from a working setup.

Re-tested with a working R04:

- `scan_list`: frame 32, saves only `R13`/`R14`, keeps the bound in
  `R14`, and spills `list` to the stack. The flash saves `R8`-`R14` and
  keeps `list` in `R12` with derived pointers in `R13`/`R14`.
- `issue_command`: saves `PR` before `TST R4,R4`, branches with `BT/S`
  (flash `BF/S`), and emits a different pool. On the canonical 6.0B
  source it dies with `Internal Error: adr_asmout.c:619` after emitting
  a partial listing.

So 6.0AD R04 is not the build. The only compiler that still reproduces
`issue_command` 252/252 bytes, and the flash's seven-register frame for
`scan_list`, is **6.0B**. The working hypothesis is now that the BIOS
was built with 6.0B or a build with identical codegen, and that the two
remaining gaps are source shape: `list` must be allocated to `R12`
before the derived pointers, and the `0x8C000598`/`0x8C000800` calls
must stay in the pool rather than being cached in registers.

## Allocation experiments: extern calls and the hoist fingerprint

`docs/candidates/scan_list_ext.c` declares the four `0x8C00xxxx`
targets as externals and binds them with the linker
(`DEFINE sym(address)`). That is the source shape the flash implies:

- 6.0B stops caching `0x8C000800` in a callee-saved register and emits
  `MOV.L pool,R3 ; JSR @R3` at the call site, exactly like the flash's
  `mov.l .La300,r2 ; jsr r2`.
- The literal-cast form instead hoists the address into `R8`/`R9` and
  forces `saved` into `R10`.

With extern calls the 6.0B frame is 40 bytes and the loop preheader is:

```
MOV #10,R8      ; gbr.count_70 = 10, hoisted
MOV #59,R9      ; *p = 59, hoisted
MOV #2,R10      ; flags & 2, hoisted
MOV #0x96,R11
```

The flash instead keeps `R8=2`, `R9=saved byte`, `R10=0x6DDD0`,
`R11=0x96`, and re-materialises `10` and `59` with `mov #imm` inside
the loop. `saved` therefore lives in `R9` and the frame stays 36 bytes.

That hoist set is a compiler-build fingerprint, not a source shape:

| build | frame | loop constants hoisted |
|---|---:|---|
| 6.0A | 40 | 10, 59, 2 |
| 6.0B | 40 | 10, 59, 2 |
| 6.0C | 40 | 10, 59, 2 |
| 6.0AD R04 | 32 | none; whole frame spilled, `list` in `R14` |
| flash | 36 | 2, 0x96, 0x6DDD0 |

Marking `gbr` or `p` volatile changes nothing. Every 6.0A/B/C build
over-hoists; R04 under-hoists and spills. The BIOS build sits between
them, which is consistent with the official post-evaluation Adria
release (R05, planned for October 2000) rather than R04 or 6.0B.

## Undumped disc lead: Kunoichi SDK 2.04 (2001-03-23)

The Kunoichi line is the only Sega SDK that ships the Adria
(`utl/dev/hitachi_ad`) compiler. Version 2.02 (2000-11-22) carries
**6.0AD R04**, the evaluation build. A later disc exists and is
**undumped**:

```
Kunoichi SDK 2.04   March 23, 2001   (C) SEGA CORPORATION, 2001
```

The date is printed on the CD label (Mercari item `m14380387223`,
photos `m14380387223_1.jpg` / `_2.jpg`; also eBay 188320099138,
287290577333, 227388792444 and a second Mercari listing for 2.02,
`m23996491991`). Asking price is ¥98,000. The disc is an InstallShield
package with the same layout as 2.02, including `kn2ver.txt`,
`kunoichi2.txt`, `version2.txt`, `release.txt`, `upgrade.txt`,
`set_nm2.bat` and the `utl` tree.

Why this is the target: it is the only public 2001 Sega SDK disc, it is
dated seven months after Adria R04 and in the same year as the
Atomiswave BIOS, and every other Sega SDK of that date is ruled out —
Katana R11b (2001-02-28) still ships **SHC 5.1 R11**. If the 6.0AD R05
official release shipped anywhere, it is almost certainly here.

On acquisition, check in this order:

1. `utl/dev/hitachi_ad/shc.exe` banner (`SH SERIES C/C++ Compiler
   Ver. ...`) and its PE date.
2. `kn2ver.txt`, `version2.txt`, `release.txt`, `upgrade.txt` for the
   bundled tool versions.
3. Compile `docs/candidates/scan_list_ext.c` and compare the loop
   preheader: the target build keeps `10`/`59` as immediates, keeps
   `R8=2`, `R9=saved`, `R10=0x6DDD0`, `R11=0x96`, and returns a
   36-byte frame with `list` in `R12`.

No other 2001+ NAOMI/System SP SDK disc is public or listed: searches
for `Kunoichi 2.05/2.06`, `NAOMI SDK` updates after 001002, and
System SP SDK material return nothing. The Atomiswave SystemX SDK and
its HDD remain unobtained.

Market scan for the 2.04 disc (2026-10-28): the only copies on sale
are Mercari `m14380387223` at ¥98,000 (about $650) and two eBay
listings at $1,069 and $1,080. The same Mercari seller also lists
Kunoichi 2.02 at ¥98,000 (`m23996491991`). No current Yahoo Auctions
listing; a 2.02 sold there for ¥11,611 in April 2025, so cheaper copies
do surface. No 2.05/2.06 exists publicly. The practical routes are a
proxy purchase of the Mercari disc (ZenMarket/FromJapan), a saved
search for a cheaper Yahoo listing, or a crowdfunded buy-and-dump via
the Arcade-Projects NAOMI SDK thread where 001002 and 2.02 were
previously acquired and released.

## scan_list: source shaping exhausted

`docs/candidates/scan_list_60b_extern.c` combines the three shapes that
each fixed one gap:

- struct pointer -> the flash's indexed loads
  (`mov #25,r0 ; mov.b @(r0,r14)`)
- extern calls bound by the linker -> one literal per call site
  (`_sys_800` loaded inside the loop, not cached)
- an explicit `data = &entry->data[0]` local -> the flash's argument
  order (`mov r14,r4 ; add #33,r4 ; ... ; extu.b ; add r4,r13`)

That build has the flash's **36-byte frame**, saves `R8`-`R14`, emits
`tst r8,r2`, `cmp/hs`, and the same `_sys_598` call sequence. After
permuting `R8`-`R14` to the best alignment, 93 of 161 instructions are
identical.

The rest is the allocator, not the source. Six structural variants were
compiled (pointer initialised at declaration, entry initialised at
declaration, both, `p` split from `list`, post-call copies,
declaration-order permutations). Every one gives the parameter `R13`
and the derived entry pointer `R12`; the flash gives the parameter
`R12` and the derived pointer `R13`. The compiler also hoists one or
two of `10`, `59`, `2`, `0x96` into callee-saved registers, while the
flash hoists only `2`, `0x96`, `0x6DDD0`. That trade moves with
register pressure but never lands on the flash's set.

`service_main` is worse: it contains hand-scheduled SR manipulation and
a branch into the middle of an instruction pair at `0xA0E6`
(`.word 0x65A3` / `.long 0x7510A001`). No C compiler emits that.

With the Adria line unobtained, both remaining units are at the
compiler boundary. Growing the C gate further requires a canonicalised
listing (the `issue_command` route), not more source work.
