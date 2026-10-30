# Atomiswave games

Per-game SDK library generation, read from SH-4 RAM after boot. This
mirrors the NAOMI/Kunoichi sweep in
[`kunoichi-games.md`](kunoichi-games.md).

## Method

MAME 0.289 with `awbios.zip` and the game ROM zip; `dump.lua` waits 900
frames, dumps `0x0C000000`-`0x0C7FFFFF`, and the dump is searched for
`SystemX Library Version`, `Shinobi Library`, and the SI Electronics
copyright line.

## Library generations

| MAME set | Title | Library | SI copyright |
|---|---|---|---|
| `dolphin` | Dolphin Blue | SystemX 1.01 | 2001 |
| `demofist` | Demolish Fist | SystemX 1.01 | 2001 |
| `ggx15` | Guilty Gear X Ver 1.5 | SystemX 1.01 | 2001 |
| `kov7sprt` | Knights of Valour 7 Spirits | SystemX 1.01 | 2001 |
| `rumblef2` | Rumble Fish 2 | SystemX 1.01 | 2001 |
| `fotns` | Fist of the North Star | SystemX 1.11 | 2001,2002,2003 |
| `ggisuka` | Guilty Gear Isuka | SystemX 1.11 | 2001,2002,2003 |
| `mslug6` | Metal Slug 6 | Shinobi 2.01 | 2001,2002,2003 |
| `kofnw` | KOF Neowave | Shinobi 2.01 | 2001,2002,2003 |
| `samsptk` | Samurai Spirits Tenkaichi Kenkakuden | Shinobi 2.01 | 2001,2002,2003 |
| `ngbc` | NeoGeo Battle Coliseum | Shinobi 2.01 | 2001,2002,2003 |
| `kofxi` | KOF XI | Shinobi 2.01 | 2001,2002,2003 |
| `rumblef` | Rumble Fish | SystemX 1.11 | 2001,2002,2003 |

Three generations are visible:

- **SystemX 1.01** (2001) — the launch-era library, matching the BIOS
  copyright string.
- **SystemX 1.11** (2001-2003) — mid-life.
- **Shinobi 2.01** (2001-2003) — late-life, mostly SNK/Playmore titles.

## Open threads for a wiki

- BIOS revisions: `bios0` vs `bios1` (six footer bytes), region/build
  dates, header fields.
- Service menu and error codes (`ERROR 00`, `ERROR 01`, backup clear).
- Cartridge header (`SYSTEM_X_APP`, board/vendor/serial fields).
- SDK timeline: SystemX 1.01 → 1.11 → Shinobi 2.01; Katana 5.1/6.0 line.
- Atomiswave dev kit (SystemX) history and the unreleased SDK.
- NAOMI GD boot chain and DIMM firmware.
