/* Service cluster for the Atomiswave BIOS.
 *
 * Hitachi SHC 5.1 Release 04:
 *   shc -cpu=sh3 -endian=little -optimize=1
 *
 * The schedules below match the flash. Only FUN_09e34 is linked into
 * the image: $G0 at 0 fills its one GBR relocation, and the other 13
 * halfwords have no relocation. A bsr displacement matches only when
 * every static callee in this file has its real size. This file is the
 * schedule source. It is not the flash image.
 *
 * hole_09cdc, FUN_09e68, and FUN_0a3a0 are named from the bsr targets.
 * Their bodies are not in this file. An extern compiles as jsr.
 * They have to be static in this file before those calls become bsr.
 */

#pragma gbr_base (lo)
struct {
    char b0;
    char pad1[35];
    char b36;
    char b37;
    char b38;
    char pad39[9];
    int l48;
    char pad52[12];
    int l64;
    short w68;
    short w70;
    int l72;
    int l76;
    char pad80[20];
    int l100;
    char pad104[24];
} lo;

#pragma gbr_base1 (hi)
struct {
    char pad0[8];
    int l136;
    char pad140[4];
    short w144;
    short w146;
    char pad148[8];
    int l156;
    char pad160[68];
    int l228;
    int l232;
    int l236;
    int l240;
    int l244;
    int l248;
    int l252;
    char pad256[308];
    int l564;
} hi;

extern void hole_09cdc(void);
extern int FUN_09e68(void);
extern int FUN_0a3a0(int param_1);

/* 0x9E34. Plain bt, then one shared return through r4.
 * An || chain compiles as bt/s. A switch that returns the constant
 * directly compiles as rts with the constant in r0. */
int FUN_09e34(void)
{
    int r;

    switch (lo.l72) {
    case 6:
    case 7:
    case 9:
        r = -1;
        break;
    default:
        r = 0;
        break;
    }
    return r;
}

/* 0x9E50. True when GBR+100 is 0x8C008000 and GBR+76 is 32. */
int FUN_09e50(void)
{
    if (lo.l100 == 0x8c008000 && lo.l76 == 32)
        return 1;
    return 0;
}

/* 0xA1D4. The constant 600 does not fit in mov #imm, so it comes from a pool. */
void FUN_0a1d4(void)
{
    lo.w68 = 600;
}

/* 0xA158. */
void FUN_0a158(void)
{
    hi.l136 = 0x8c000c86;
}

/* 0xA15E. Tail call. r4, r5, and r6 are 0. r7 is 2. */
void FUN_0a15e(void)
{
    ((void (*)(int, int, int, int))0x8c0010f0)(0, 0, 0, 2);
}

/* 0xA16A. Same tail call with r7 = 3. Twelve bytes of code; the pool follows. */
void FUN_0a16a(void)
{
    ((void (*)(int, int, int, int))0x8c0010f0)(0, 0, 0, 3);
}

/* 0xA1DA. */
int FUN_0a1da(short param_1)
{
    int iVar1;

    hi.w146 = param_1;
    do {
        hole_09cdc();
        iVar1 = FUN_09e68();
    } while (iVar1 < 0);
    return iVar1;
}

/* 0xA354. */
int FUN_0a354(int param_1)
{
    int iVar1;

    do {
        hole_09cdc();
        iVar1 = FUN_0a3a0(param_1);
    } while (iVar1 < 0);
    return iVar1;
}

/* 0xA370. The store of 10 runs once. A result of -2 restarts after that store. */
int FUN_0a370(void)
{
    int iVar1;

    lo.w70 = 10;
restart:
    FUN_0a1d4();
    iVar1 = FUN_0a354(0);
    if (iVar1 == 0) {
        FUN_0a1d4();
        do {
            hole_09cdc();
            iVar1 = FUN_0a3a0(1);
            if (iVar1 == -2)
                goto restart;
        } while (iVar1 < 0);
    }
    return iVar1;
}
