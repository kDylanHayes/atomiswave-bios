# Compiler probe

No C is compiled in this tree. A unit is not a C match until one
compiler and one flag set reproduce a real function, including the
prologue, the delay slots, and the literal pool.

The probe functions are file `0xA354` (28 bytes) and `0xA370` (48 bytes).
Both save `pr` and both contain `bsr`. They are not the handwritten boot code.

Candidates, in the order they should be tried once a binary exists:

- Hitachi/Renesas SHC from the Dreamcast era
- `sh-elf-gcc`

Nothing below was pinned. `src/` stays empty.

## What is installed

- `sh-elf-gcc`: not on PATH
- `sh-elf-as`: not on PATH
- `sh-elf-ld`: not on PATH
- `sh4-elf-gcc`: not on PATH
- `sh4-linux-gnu-gcc`: not on PATH
- `sh4-linux-gnu-as`: not on PATH
- `shc`: not on PATH
- `ccsh`: not on PATH

Homebrew has no `sh-elf` formula. This probe does not build GCC and
does not download an unpinned toolchain.

## Probe bytes

`0xA354`: `224ffc7f422fbfbc09001fb0f26403641144f88b047f264f0b004360`

`0xA370`: `224f0ae023c12dbf0900ebbf00e4036448240a8b26bf0900a8bc090008b001e4fe88f08d03641144f68b264f0b004360`
