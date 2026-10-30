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
| `chocomk` | Musapey's Choco Marker (GDL-0014A) | Kunoichi 0.91, Apr 06 2000 |
| `moeru` | Moeru Casinyo (GDL-0013) | Kunoichi2 2.04, Nov 17 2000 |
| `vathlete` | Virtua Athletics (GDS-0019) | Kunoichi 0.96, Oct 23 2000 |
| `meltybld` | Melty Blood Act Cadenza Ver. A (GDL-0028C) | Kunoichi 0.99, Mar 19 2001 |
| `psyvar2` | Psyvariar 2 (GDL-0024) | Kunoichi2 2.07, Mar 21 2001 |
| `ss2005` | Super Shanghai 2005 Rev A (GDL-0031A) | Kunoichi2 2.07, Mar 21 2001 |
| `tetkiwam` | Tetris Kiwamemichi (GDL-0020) | Kunoichi2 2.07, Mar 21 2001 |
| `quizqgd` | Quiz Keitai Q mode (GDL-0017) | none at 60 s |
| `takoron` | Noukone Puzzle Takoron (GDL-0042) | none at 15 s |

Not yet swept, CHD available: `bdrdown`, `cfield`, `cleoftp`,
`confmiss`, `cvsgd`, `ggxx`, `ggxxac`, `ggxxrl`, `ggxxsla`, `gundmgd`,
`gundmxgd`, `ikaruga`, `jingystm`, `karous`, `keyboard`, `kurucham`,
`lupinsho`, `meltyb`, `mok`, `monkeyba`, `puyofev`, `radirgy`, `senko`,
`senkosp`, `sfz3ugd`, `shikgam2`, `slashout`, `spkrbtl`, `sprtjam`,
`starseek`, `trgheart`, `trizeal`, `undefeat`, `usagiym`, `vtennis2`.

## Dating pattern

- SDK 2.02 (disc 2000-11-22) ships `kunoi2.lib` 2.04 built 2000-11-17:
  five days before the disc. Moeru Casinyo loads exactly that build.
- SDK 2.04 (disc 2001-03-23) should ship the 2.07 generation: library
  2.07 is built 2001-03-21, two days before the disc. Super Shanghai
  2005, Tetris Kiwamemichi and Psyvariar 2 all load that build.

No compiler banner survives in RAM; the compiler itself still has to
come from the disc.
