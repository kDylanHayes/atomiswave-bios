# Kunoichi games

Trackable NAOMI GD-ROM titles and the Kunoichi library each one loads.
The point is to date the SDK generations without decrypting the disc
image: run the game under MAME, dump SH-4 RAM, and read the library
banner.

## Method

1. MAME 0.289, ROM zip from the MAME merged set and the CHD from
   [Naomigdrompack](https://archive.org/details/Naomigdrompack).
2. Run headless with `-autoplay`-free Lua:
   `mame <set> -rompath roms -autoboot_script dump.lua -video none -sound none`.
3. `dump.lua` waits 900 frames, dumps `0x0C000000`-`0x0C7FFFFF`
   (8 MB of SH-4 RAM), and exits.
4. `strings -a -n 5 ram.bin | grep -i kunoichi`.

## Sources

| Source | Contents |
|---|---|
| [Naomigdrompack](https://archive.org/details/Naomigdrompack) | 44 GD sets with CHDs |
| [MAME 0.289 ROMs (merged)](https://archive.org/details/mame-roms-merged_) | game ROM zips, BIOS and device sets |
| [REDUMP NAOMI](https://archive.org/details/REDUMP_Arcade_-_Sega_-_Naomi) | 34 GDI titles, direct tracks |
| [VincentNL's Kunoichi list](https://github.com/VincentNLOBJ/Naomi-Kunoichi-Games) | games known to use Kunoichi libraries |

## Sweep status

| MAME set | Title | Banner |
|---|---|---|
| `chocomk` | Musapey's Choco Marker | 0.91, Apr 06 2000 |
| `cleoftp` | Cleopatra Fortune Plus | 2.04, Nov 17 2000 |
| `moeru` | Moeru Casinyo | 2.04, Nov 17 2000 |
| `vathlete` | Virtua Athletics | 0.96, Oct 23 2000 |
| `sfz3ugd` | Street Fighter Zero 3 Upper | 0.96, Oct 23 2000 |
| `ikaruga` | Ikaruga | 2.06, Feb 20 2001 |
| `keyboard` | La Keyboard | 2.06, Feb 20 2001 |
| `jingystm` | Jingi Storm | 0.99, Mar 19 2001 |
| `meltybld` | Melty Blood Act Cadenza Ver. A | 0.99, Mar 19 2001 |
| `bdrdown` | Border Down | 2.07, Mar 21 2001 |
| `cfield` | Chaos Field | 2.07, Mar 21 2001 |
| `karous` | Karous | 2.07, Mar 21 2001 |
| `kurucham` | Kurukuru Chameleon | 2.07, Mar 21 2001 |
| `meltyb` | Melty Blood Act Cadenza Version B2 | 2.07, Mar 21 2001 |
| `psyvar2` | Psyvariar 2 | 2.07, Mar 21 2001 |
| `radirgy` | Radirgy | 2.07, Mar 21 2001 |
| `senko` | Senko no Ronde | 2.07, Mar 21 2001 |
| `senkosp` | Senko no Ronde Special | 2.07, Mar 21 2001 |
| `shikgam2` | Shikigami no Shiro II | 2.07, Mar 21 2001 |
| `ss2005` | Super Shanghai 2005 | 2.07, Mar 21 2001 |
| `tetkiwam` | Tetris Kiwamemichi | 2.07, Mar 21 2001 |
| `trgheart` | Trigger Heart Exelica | 2.07, Mar 21 2001 |
| `trizeal` | Trizeal | 2.07, Mar 21 2001 |
| `undefeat` | Under Defeat | 2.07, Mar 21 2001 |
| `usagiym` | Usagi - Yamashiro Mahjong Hen | 2.07, Mar 21 2001 |
| `confmiss` | Confidential Mission | none |
| `cvsgd` | Capcom Vs. SNK Pro | none |
| `ggxx` / `ggxxac` / `ggxxrl` / `ggxxsla` | Guilty Gear XX family | none (carries `NLOBJPUT 0.99`) |
| `gundmgd` / `gundmxgd` | Gundam Federation vs Zeon | none |
| `mok` | The Maze of the Kings | none |
| `monkeyba` | Monkey Ball | none |
| `slashout` | Slashout | none |
| `spkrbtl` | Spikers Battle | none |
| `sprtjam` | Sports Jam | none |
| `starseek` | Doki Doki Idol Star Seeker | none |
| `vtennis2` | Virtua Tennis 2 | none |
| `quizqgd` | Quiz Keitai Q mode | none at 60 s |
| `takoron` | Noukone Puzzle Takoron | none at 15 s |
| `lupinsho` / `lupinshoo` | Lupin The Third - The Shooting | 0.99, Mar 19 2001 |
| `puyofev` / `puyofevj` | Puyo Pop Fever | 2.07, Mar 21 2001 |

Sixteen titles load **2.07 built 2001-03-21**. That is the dominant
2001-2008 library.

## Dating pattern

- SDK 2.02 (disc 2000-11-22) ships `kunoi2.lib` 2.04 built 2000-11-17:
  five days before the disc. Moeru Casinyo and Cleopatra Fortune Plus
  load exactly that build.
- SDK 2.04 (disc 2001-03-23) should ship the 2.07 generation: library
  2.07 is built 2001-03-21, two days before the disc. Sixteen titles
  load that build.
- The 2.06 build (2001-02-20) sits between: Ikaruga and La Keyboard.
- The 0.96/0.99 build line (Oct 2000-Mar 2001) is separate from the
  2.0x line and is used by Virtua Athletics, SFZ3 Upper, Jingi Storm
  and Melty Blood Act Cadenza.

No compiler banner survives in RAM; the compiler itself still has to
come from the disc.

## Compiler fingerprint attempts (negative)

The RAM dumps date the *library*, not the compiler. Three attempts:

1. **4 KB block matching** across dumps: Psyvariar 2 (2.07) vs Super
   Shanghai (2.07) shares 9 blocks; Moeru (2.04) vs Psyvariar shares 9.
   Only BIOS/data blocks match; library code is relocated and cannot be
   aligned this way.
2. **Whole-window matching** blew memory at 8 MB per dump; restricting
   to the banner region still finds nothing stable.
3. **Library symbols**: the Hitachi librarian (`LBR.EXE` 2.0A, 5.1
   tools) lists `kunoi2.lib` as 108 modules / 1197 symbols, and
   `EXTRACT` + `OUTPUT` produces a one-module library. The embedded ROF
   object starts at offset 768 (`80 21 00 80 ...`); slicing it and
   running `elfcnv.exe` (5.1 R11) converts it to ELF with SYSROF
   sections (`PSG` code, `CSG` constants, `BSG` bss). But linking into
   the game relocates the code, so raw matching of a module's `PSG`
   bytes against RAM is unreliable (pdtmr_: 9/310 windows in Moeru).

Even with perfect symbol recovery, the library is compiled code without
source; identifying *which* compiler produced it still requires the
compiler binaries or a build manifest. Those are only on the SDK disc.

## Cartridge titles (all 94 sets)

The 0.239 NAOMI DAT lists 94 cart sets. All were run through the same
RAM-dump method. Nineteen load a Kunoichi banner:

| Library | Build | Titles |
|---|---|---|
| 0.06zrTEST2 | Sep 30 1999 | Toukon Retsuden 4 |
| 0.62TEST4 | Sep 29 1999 | Puyo Puyo Da!, Samba de Amigo |
| 0.71 | Dec 08 1999 | Tokyo Bus, Virtual On Oratorio Tangram, WWF Royal Rumble, Death Crimson OX |
| 0.96 | Oct 23 2000 | Gun Survivor 2, Samba de Amigo ver. 2000, Wave Runner GP |
| 0.99 | Mar 19 2001 | Shootout Pool |
| 2.07 | Mar 21 2001 | Asian Dynamite, Akatsuki Blitzkampf Ausf. Achse, Melty Blood Actress Again, Radirgy Noa, Mushiking 2004/2005/2006 First/2006 Second |

The other 75 carts show no Kunoichi banner. Missing parent/BIOS sets
were supplied from the MAME 0.289 merged set, so all 94 carts ran.

The 0.06zrTEST2 hit pushes the line back to **September 1999**; the
2008-2009 carts (`mbaa`, `radirgyn`) still use 2.07.

## System SP (SPIDER)

MAME's `segasp` driver works with the BIOS built from the retrobios
`segasp/` files. The same RAM-dump method applies. System SP kept the
Kunoichi2 line alive after the NAOMI 2.07 build, with platform-specific
`sp` builds:

| Library | Build | MAME sets | Titles |
|---|---|---|---|
| Kunoichi2 2.07sp | Jun 21 2004 | `dinoking` | Dinosaur King (USA) |
| Kunoichi2 2.07sp | Oct 08 2004 | `lovebery`, `aminosan`, `mirworld` | Love And Berry 1st-2nd, Aminosan, Mirage World |
| Kunoichi2 2.08sp | Jun 14 2006 | `bingogal`, `bingogals`, `brickppl`, `galilfac`, `magicpop`, `manpuku`, `ochaken`, `puyomedal`, `tetgiant`, `unomedal`, `westdrmg` | Bingo Galaxy (main/satellite), Brick People, Galileo Factory, Magical Poppins, Manpuku Suizokukan, Ocha-Ken Hot Medal, Puyo Puyo! The Medal Edition, Tetris Giant, UNO the Medal, Western Dream Gold |
| Kunoichi2 2.09sp | Feb 26 2008 | `kingyo`, `shateki` | Yataimura Kingyosukui, Yataimura Shateki |
| none | 2004/2005 | `dinokior`, `dinoki25` | Dinosaur King Operation: Dinosaur Rescue, Dinosaur King D-Team VS. the Alpha Fortress |

`dinokior` and `dinoki25` load `SPIDERHAT` (`Ver.0.010`, 2004;
`Ver.0.020`, 2005) but no Kunoichi banner. `isshoni` (Isshoni Wanwan
Waiwai Puppy 2008) hung under MAME and produced no dump; `dinoki4` is
a placeholder zip.

The `sp` line runs **2.07sp (2004) -> 2.08sp (2006) -> 2.09sp (2008)**,
four years past the last NAOMI build.

## NAOMI 2

NAOMI 2 is a separate library family. Its ROMs carry two banners:
`NAOMI LIBRARY Ver 0.8 AM R&D` and `NAOMI2 LIBRARY Ver 0.0x SOFT1 R&D`,
plus an `nlam/Version` build string. They are readable directly from
the cart ROM zips:

| MAME set | Title | NAOMI LIBRARY 0.8 | NAOMI2 LIBRARY | nlam |
|---|---|---|---|---|
| `wldrider` | Wild Riders | Feb 21 2000 | 0.01, May 24 2000 | 2.220550, Aug 22 2000 |
| `vstrik3c` | Virtua Striker 3 (World, Rev B) | Aug 24 2000 | 0.02, Aug 14 2000 | 2.220550, Aug 22 2000 |
| `kingrt66` | The King of Route 66 (Rev A) | Jun 11 2001 | 0.02, Jun 11 2001 | 2.230620, May 15 2001 |
| `vf4cart` | Virtua Fighter 4 (World) | Jun 15 2001 | 0.02, Jun 15 2001 | 2.230720, Jun 08 2001 |
| `soulsurf` | Soul Surfer (Rev A) | Nov 21 2001 | 0.02, Oct 30 2000 | 2.220780, Sep 12 2001 |
| `clubk2k3` | Club Kart: European Session (2003, Rev A) | Dec 17 2001 | 0.03, Apr 11 2001 | 2.220830, Feb 28 2003 |
| `vf4evoct` | Virtua Fighter 4: Evolution (World) | May 18 2002 | 0.03, May 18 2002 | 2.220830, Dec 14 2001 |

The GD-based NAOMI 2 titles (`initd`, `beachspi`, `vf4tuned`,
`initdv2*`, `initdv3*`) wrap the game in a `NAOMIGD.BIN` container whose
234 MB `VB.BIN` payload is packed; no plaintext library banner survives
in the CHD or in a 32 MB RAM dump. Their library versions are not yet
recovered.

## Platform matrix

| Platform | Library family | Earliest | Latest |
|---|---|---|---|
| NAOMI (cart/GD) | Kunoichi / Kunoichi2 | 0.06zrTEST2, Sep 1999 | 2.07, Mar 2001 |
| Atomiswave | SystemX / Shinobi | SystemX 1.01, 2001 | Shinobi 2.01, 2003 |
| System SP | Kunoichi2 `sp` | 2.07sp, Jun 2004 | 2.09sp, Feb 2008 |
| NAOMI 2 | NAOMI2 LIBRARY | 0.01, May 2000 | 0.03, May 2002 |

## What is still uncovered

- GD-based NAOMI 2 payloads (`initd`, `beachspi`, `vf4tuned`, `initdv2*`, `initdv3*`).
- `isshoni` and `dinoki4` on System SP.
- Atomiswave prototypes (below).

## Atomiswave prototypes

- **Sushi Bar**: only a NAOMI conversion exists
  ([`sushibar`](https://archive.org/details/sushibar)); no original
  Atomiswave dump is public.
- **Chicago 1929**: no public ROM dump.

