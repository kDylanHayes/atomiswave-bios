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
| `lupinsho` | Lupin The Third - The Shooting | untested (CHD fetch 500) |
| `puyofev` | Puyo Pop Fever | untested (CHD name mismatch) |

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

