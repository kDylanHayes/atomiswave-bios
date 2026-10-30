# Tooling

The build gate needs only Python 3, the Hitachi SHC toolchain, Boxedwine
and a local `bios0.ic23` (see the README). Everything below is for
inspection work and is not required by `make`.

## Compiler

| Use | Toolchain |
|---|---|
| `make progress`, `src/services.c` | Hitachi SHC 5.1 Release 04 (`-cpu=sh3 -endian=little -optimize=1`) |
| `issue_command_60b.src`, `scan_list_60b.src` | SHC 6.0B listing, canonicalised |

The 6.0B build lives outside the repo under the Boxedwine prefix; the
`.src` files are committed so the gate does not depend on it.

## Ghidra

| Version | Path | Notes |
|---|---|---|
| 12.1.4 | `~/Documents/ghidra_12.1.4_PUBLIC` | used by REA |
| 12.2 | `~/Documents/ghidra_12.2_PUBLIC` | installed, macOS natives built locally |

Ghidra 12.2 no longer ships prebuilt macOS native binaries (the public
release covers Windows x86-64/ARM64 and Linux x86-64 only). Build them
once per install:

```bash
cd ~/Documents/ghidra_12.2_PUBLIC/support/gradle
./gradlew buildNatives
```

That produces `Ghidra/Features/Decompiler/build/os/mac_arm_64/decompile`
and the GNU demanglers. Requires a JDK and Xcode Command Line Tools.

## REA

- `rea-agents` 6.5.0, skill v42, registered for OpenCode in
  `~/.config/opencode/opencode.json`
- registration environment: `GHIDRA_INSTALL_DIR`, `JAVA_HOME`
- doctor: `npx -y rea-agents@6.5.0 doctor --client opencode --json`
- setup: `npx -y rea-agents@6.5.0 setup --client opencode --yes`

REA 6.5.0, 6.7.0 and 6.8.0 all accept **Ghidra 12.1.x only** and reject
12.2 (`accepted releases are 12.1.x (verified build 12.1.4)`), so the
registration stays pinned to 12.1.4. 12.2 is usable manually through
`ghidraRun`. Switch when a REA release adds 12.2 support:

```bash
GHIDRA_INSTALL_DIR=~/Documents/ghidra_12.2_PUBLIC \
  npx -y rea-agents@<version> setup --client opencode --yes
```

## Decompiler export

`decomp/bios0/functions` is Ghidra pseudocode for bios0 and
`decomp/bios0/index.txt` lists the exported bodies. Those byte counts
are Ghidra bodies and omit literal pools; `asm/functions.txt` is the
byte split used by the gate. The export has no file for `service_main`
(`0x9FBC`) or `ram_call_3` (`0xA16A`).
