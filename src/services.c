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
 * prime_count68 slot so this function starts at 0xA1DA.
 * set_hook and ram_window_ready are linked in their own units. A later
 * function mentions the same literal so the pool lands on the flash
 * displacement. ram_call_2 and ram_call_3 share one unit. A 6-byte
 * spacer puts them on their 2-mod-4 flash addresses, and 22 empty
 * globals place 0x8C0010F0 at the flash displacement. prime_count68
 * is its own unit. Sixty-seven empty globals place its halfword at
 * displacement 0x87. quiet_interrupts is its own unit. Four constant
 * returns and twenty-three empty globals place 0x100000F0 and
 * 0xA05F6910 at the flash displacements. enter_ram is its own unit.
 * Fifteen 6-byte constant returns put it on a 2-mod-4 boundary, and
 * thirteen empty globals place its pool. step_phase is its own unit.
 * The phase unit's 4-byte stub stays, so phase_until_clear does not
 * move. Distance stubs and three add-chains pin the bsr sites and the
 * literal pool. rof2bin -v=00 fills two reserved alignment halfwords
 * with zero. Those helpers are not in the flash. An extern compiles
 * as jsr. A bsr needs a static callee in the same unit.
 * This file is the schedule source. It is not the flash image.
 *
 * hole_09cdc and issue_command are named from the bsr targets. Their
 * bodies are not in this file. An extern compiles as jsr. They have
 * to be static in the caller's unit before those calls become bsr.
 * step_phase's body is below. phase_until_clear still calls a 4-byte
 * static stub of that name.
 *
 * GBR+0 is the lo window. $G0 is 128 bytes, so the hi window starts at
 * GBR+128. Field suffixes are those displacements.
 */

#include <machine.h>

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

/* Calls the erased hole at 0x9DB8 when the phase is non-negative.
 * Returning the phase keeps the sign test on r14. */
#pragma inline (sign_keep)
static short sign_keep(short phase)
{
    if (phase >= 0)
        hole_09db8();
    return phase;
}

/* Calls ram_call_2 when the phase is negative, then returns it. */
#pragma inline (pass_s)
static short pass_s(short phase)
{
    if (phase < 0)
        ram_call_2();
    return phase;
}

/* A copy the compiler cannot fold into the pointer it already holds.
 * Used only on the reachable epilogue, so the saved GBR reloads into r2
 * while the phase -5 call stays jsr @r2. */
#pragma inline (same_ptr)
static void *same_ptr(void *p)
{
    return p;
}

#define TAIL \
    if (phase < (short)gbr_read_word(146)) \
        phase = 0; \
    phase = sign_keep(phase); \
    hi.phase_144 = phase

/* 0x9E68. One step of the signed short at GBR+144.
 * hold is unreachable. Its plain set_gbr keeps phase -5 calling through
 * r2. The reachable return uses same_ptr. if (0) keeps the reject arm
 * from sharing the default arm. The link unit slices these 340 bytes. */
int step_phase(void)
{
    void *keep;
    short phase;
    int result;
    {
        void *saved;
        saved = get_gbr();
        set_gbr((void *)0x8C000000);
        keep = saved;
    }
    phase = pass_s(hi.phase_144);
    switch (phase) {
    case -8: goto phase_m8;
    case -7: goto phase_m7;
    case -6: goto phase_m6;
    case -5: goto phase_m5;
    case -4: goto phase_m7;
    case -3: goto phase_m6;
    case -2: goto phase_m2;
    case -1: goto phase_m1;
    case 0:
    default:
        break;
    }
    hole();
    lo.flag_38 |= 1;
    lo.count_70 = 10;
    phase = -2;
    goto clamp;
phase_m1:
    if ((unsigned)*(volatile int *)&lo.word_48 > 0)
        phase = (short)*(volatile int *)&lo.word_48;
    else
        phase = 127;
    goto clamp;
phase_m2:
    hi.cmd_236 = 24;
    prime_count68();
    phase = -3;
phase_m6:
    result = issue_command(0);
    if (result == 1)
        goto rej_m1;
    if (result != 0)
        goto clamp;
    phase = (short)(phase - 1);
    prime_count68();
    goto clamp;
phase_m7:
    result = issue_command(1);
    if (result == -2) {
        phase = (short)(phase - 2);
        goto after_m7;
    }
    if (result != 0)
        goto after_m7;
    if (lo.word_76 == 0x80) {
        phase = (short)(phase - 1);
        goto after_m7;
    }
    if (ram_window_ready()) {
        phase = 0;
        goto after_m7;
    }
    result = 1;
after_m7:
    if (result != 1)
        goto clamp;
    if (reject_code() == -1)
        goto rej_m1;
    goto word_tests;
rej_m1:
    phase = -1;
    if (0)
        phase = 1;
    goto clamp;
word_tests:
    switch (lo.word_48) {
    case 2: goto add2;
    case 6: goto set_m2;
    case 16: goto win16;
    default: goto set_late;
    }
set_m2:
    phase = -2;
    goto clamp;
add2:
    phase = (short)(phase + 2);
    goto clamp;
win16:
    if (ram_window_ready())
        goto set_zero;
    goto clamp;
set_late:
    phase = -1;
    goto clamp;
hold:
    TAIL;
    set_gbr(keep);
    return phase;
phase_m5:
    (*(void (*)(int))0x8C0005B8)(0x8C000FC4);
    hi.arg_248 = lo.ptr_100;
    prime_count68();
    phase = -6;
    goto phase_m6;
phase_m8:
    if ((*(int (*)(int))0x8C0004F4)(lo.ptr_100) != 0)
        goto phase_126;
set_zero:
    phase = 0;
    goto clamp;
phase_126:
    phase = 126;
clamp:
    TAIL;
    set_gbr(same_ptr(keep));
    return phase;
}

/* 0xA1D4. Stores 600 at GBR+68. mov.w @(disp,PC) zero-extends disp,
 * so 0x87 at this address loads the halfword at 0xA2E6. That halfword
 * is 600, inside scan_list, in the gap a bra skips. */
void prime_count68(void)
{
    lo.count_68 = 600;
}

/* 0xA116. Blocks interrupts, installs VBR 0x8C000000, calls 0x8C0006AA,
 * stores 0x8C000728 at GBR+564, writes 8 at 0xA05F6910, clears the
 * block, and jumps to 0x8C000768. The link unit starts this function
 * 2-mod-4. A 0-mod-4 entry saves pr first and loads the port before
 * mov #8. */
void enter_ram(void)
{
    set_cr(get_cr() | 0x100000F0);
    set_vbr((void *)0x8C000000);
    (*(void (*)(void))0x8C0006AA)();
    gbr_write_long(564, 0x8C000728);
    *(volatile int *)0xA05F6910 = 8;
    (void)*(volatile int *)0xA05F6910;
    set_cr(get_cr() & 0xEFFFFF0F);
    (*(void (*)(void))0x8C000768)();
}

/* 0xA144. ORs 0x100000F0 into SR, stores 0 at GBR+136, stores 0 at
 * 0xA05F6910, and reads that word back into r0. service_main overwrites
 * r0 on return. The read is what fills the rts delay. gbr_write_long
 * keeps the zero in r0. Assigning hi.hook_136 loads the address first. */
int quiet_interrupts(void)
{
    set_cr(get_cr() | 0x100000F0);
    gbr_write_long(136, 0);
    *(volatile int *)0xA05F6910 = 0;
    return *(volatile int *)0xA05F6910;
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
