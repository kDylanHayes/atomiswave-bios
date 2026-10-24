/* Service cluster for the Atomiswave BIOS.
 *
 * Hitachi SHC 5.1 Release 04:
 *   shc -cpu=sh3 -endian=little -optimize=1
 *
 * An AI assigned these names from the bytes. The flash has no symbol
 * table. docs/services.md is the map.
 * tools/link_matched.py compiles reject_code by itself, with $G0 at 0.
 * It compiles retry_issue and run_transfer in a second unit, with static
 * stubs at the flash distances, so their bsr displacements match.
 * phase_until_clear is a third unit. A 6-byte spacer occupies the
 * prime_count68 slot so this function starts at 0xA1DA. The other
 * schedules in this file stay unlinked. An extern compiles as jsr. A
 * bsr needs a static callee in the same unit. This file is the schedule
 * source. It is not the flash image.
 *
 * hole_09cdc, step_phase, and issue_command are named from the bsr
 * targets. Their bodies are not in this file. An extern compiles as jsr.
 * They have to be static in this file before those calls become bsr.
 *
 * GBR+0 is the lo window. $G0 is 128 bytes, so the hi window starts at
 * GBR+128. Field suffixes are those displacements.
 */

#pragma gbr_base (lo)
struct {
    char b0;
    char pad1[35];
    char flag_36;
    char flag_37;
    char flag_38;
    char pad39[9];
    int word_48;
    char pad52[12];
    int saved_64;
    short count_68;
    short count_70;
    int code_72;
    int word_76;
    char pad80[20];
    int ptr_100;
    char pad104[24];
} lo;

#pragma gbr_base1 (hi)
struct {
    char pad0[8];
    int hook_136;
    char pad140[4];
    short phase_144;
    short limit_146;
    char pad148[8];
    int word_156;
    char pad160[68];
    int mode_228;
    int result_232;
    int cmd_236;
    int arg_240;
    int arg_244;
    int arg_248;
    int arg_252;
    char pad256[308];
    int ptr_564;
} hi;

extern void hole_09cdc(void);
extern int step_phase(void);
extern int issue_command(int arg);

/* 0x9E34. Plain bt, then one shared return through r4.
 * An || chain compiles as bt/s. A switch that returns the constant
 * directly compiles as rts with the constant in r0.
 * Returns -1 when GBR+72 is 6, 7, or 9, and 0 otherwise. */
int reject_code(void)
{
    int r;

    switch (lo.code_72) {
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
int ram_window_ready(void)
{
    if (lo.ptr_100 == 0x8c008000 && lo.word_76 == 32)
        return 1;
    return 0;
}

/* 0xA1D4. The flash loads the halfword at 0xA0E6, which is 0x65A3.
 * That slot sits inside service_main. 600 is not the flash immediate. */
void prime_count68(void)
{
    lo.count_68 = 0x65a3;
}

/* 0xA158. Stores 0x8C000C86 at GBR+136. */
void set_hook(void)
{
    hi.hook_136 = 0x8c000c86;
}

/* 0xA15E. Tail call. r4, r5, and r6 are 0. r7 is 2. */
void ram_call_2(void)
{
    ((void (*)(int, int, int, int))0x8c0010f0)(0, 0, 0, 2);
}

/* 0xA16A. Same tail call with r7 = 3. Twelve bytes of code; the pool follows. */
void ram_call_3(void)
{
    ((void (*)(int, int, int, int))0x8c0010f0)(0, 0, 0, 3);
}

/* 0xA1DA. Stores the argument at GBR+146, then repeats until step_phase >= 0. */
int phase_until_clear(short param_1)
{
    int iVar1;

    hi.limit_146 = param_1;
    do {
        hole_09cdc();
        iVar1 = step_phase();
    } while (iVar1 < 0);
    return iVar1;
}

/* 0xA354. Repeats until issue_command(arg) >= 0. The argument is reloaded
 * from the stack for every call. */
int retry_issue(int param_1)
{
    int iVar1;

    do {
        hole_09cdc();
        iVar1 = issue_command(param_1);
    } while (iVar1 < 0);
    return iVar1;
}

/* 0xA370. Stores 10 at GBR+70 once. A result of -2 restarts after that store. */
int run_transfer(void)
{
    int iVar1;

    lo.count_70 = 10;
restart:
    prime_count68();
    iVar1 = retry_issue(0);
    if (iVar1 == 0) {
        prime_count68();
        do {
            hole_09cdc();
            iVar1 = issue_command(1);
            if (iVar1 == -2)
                goto restart;
        } while (iVar1 < 0);
    }
    return iVar1;
}
