/* Codegen fingerprint corpus.
 *
 * Each function isolates one codegen trait seen in the service cluster.
 * Compile with -show=object and compare the listings across SHC builds.
 * This file is not part of the build and is never linked.
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
    unsigned short count_68;
    unsigned short count_70;
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

extern int ext_call(int);
extern void ext_void(void);

/* 1. Literal pool and an if/else with a bra between the arms. */
int fp_pool_bra(int a)
{
    int r;
    if (a) {
        r = ext_call(a);
        r = r + 0x1234;
    } else {
        r = ext_call(a + 1);
        r = r + 0x5678;
    }
    return r;
}

/* 2. Sibling branches that use the same constant. */
int fp_const_twice(int a)
{
    if (a == 1) {
        lo.count_68 += 0xFFFF;
        return -1;
    }
    if (a == 2) {
        lo.count_70 += 0xFFFF;
        return -2;
    }
    return a;
}

/* 3. switch on an unsigned short, case 0. */
int fp_switch_u16(int a)
{
    switch (a) {
    case 0:
        return 1;
    case 1:
        return 2;
    default:
        return 3;
    }
}

/* 4. truth test on an unsigned short field. */
int fp_extu_if(int a)
{
    if (lo.count_68)
        return 1;
    return a;
}

/* 5. goto label with a literal used before it. */
int fp_pool_label(int a)
{
    int r;
    if (a) {
        r = ext_call(a) + 0x1111;
        goto out;
    }
    r = ext_call(a + 2);
out:
    return r;
}

/* 6. Call result assigned, then tested (two mov r0,rN). */
int fp_two_mov(int a)
{
    int res;
    res = ext_call(a);
    if (res == 0)
        return 1;
    return res;
}

/* 7. GBR plus 240, a value that does not fit add #imm. */
void *fp_gbr240(int a)
{
    return (void *)((int)get_gbr() + 240 + a);
}

/* 8. Branch, literal, then a label. */
int fp_align(int a)
{
    int r;
    if (a == 0) {
        r = ext_call(a) + 0x2222;
        return r;
    }
    r = ext_call(3);
    return r;
}

/* 9. Call followed by a store, delay slot. */
int fp_delay(int a)
{
    lo.saved_64 = ext_call(a);
    return lo.saved_64;
}

/* 10. Result live across two calls. */
int fp_prologue(int a)
{
    int r = 1;
    if (a == 0) {
        if (ext_call(0) != 0)
            r = 0;
    } else {
        if (ext_call(1) == 2)
            r = 0;
        else if (ext_call(2) == 3)
            r = -1;
    }
    return r;
}

/* 11. Same function pointer called twice. */
int fp_ptr_twice(int a)
{
    int x;
    x = ((int (*)(int, int, int, int))0x8c0010f0)(a, 0, 0, 1);
    if (x)
        x = ((int (*)(int, int, int, int))0x8c0010f0)(x, 0, 0, 2);
    return x;
}

/* 12. Same function pointer, three call sites. */
int fp_ptr_three(int a)
{
    int x;
    x = ((int (*)(int, int, int, int))0x8c0010f0)(a, 0, 0, 0);
    if (x == 2)
        return 0;
    x = ((int (*)(int, int, int, int))0x8c0010f0)(a, 0, 0, 1);
    if (x == -1)
        return -1;
    x = ((int (*)(int, int, int, int))0x8c0010f0)(a, 0, 0, 4);
    return x;
}

/* 13. Seven-way switch as a comparison chain. */
int fp_switch7(int a)
{
    switch (lo.word_48) {
    case 0:
    case 1:
    case 2:
    case 5:
    case 6:
    case 11:
    case 16:
        return 1;
    default:
        return 0;
    }
}

/* 14. unsigned short decrement with a pool constant. */
int fp_dec16(int a)
{
    if (lo.count_68) {
        lo.count_68 += 0xFFFF;
        return -1;
    }
    return a;
}

/* 15. unsigned short decrement as -1. */
int fp_dec16b(int a)
{
    if (lo.count_68) {
        lo.count_68 -= 1;
        return -1;
    }
    return a;
}

/* 16. two GBR loads in one expression. */
int fp_gbr_two(int a)
{
    return lo.word_76 + hi.cmd_236 + a;
}

/* 17. compare GBR word with a large constant. */
int fp_gbr_const(int a)
{
    if (lo.ptr_100 == 0x8c008000)
        return 1;
    return a;
}

/* 18. short return value. */
short fp_ret_short(short a)
{
    return a + 1;
}

/* 19. call then add a pool constant. */
int fp_call_add(int a)
{
    return ext_call(a) + 0x7FFF;
}

/* 20. nested if with &&. */
int fp_and(int a)
{
    if (a && lo.count_68)
        return ext_call(a);
    return 0;
}

/* 21. switch on an unsigned short field. */
int fp_sw_u16_field(int a)
{
    switch (lo.count_68) {
    case 0:
        return 1;
    default:
        return 2;
    }
}

/* 22. named unsigned short temporary. */
int fp_u16_temp(int a)
{
    unsigned short c;
    c = lo.count_68;
    if (c)
        return 1;
    return a;
}

/* 23. the service countdown, shape for shape. */
int fp_countdown(int r)
{
    if (r == 1 || r == -1) {
        if (lo.count_68) {
            lo.count_68 += 0xFFFF;
            r = -1;
        } else if (lo.count_70) {
            lo.count_70 += 0xFFFF;
            ext_void();
            r = -2;
        }
    }
    return r;
}

/* 24. the first call arm of issue_command. */
int fp_arm(int arg)
{
    int res;
    int r = 1;
    if (arg == 0) {
        res = ((int (*)(int, void *, int, int))0x8c0010f0)(hi.cmd_236, (void *)((int)get_gbr() + 240), 0, 0);
        lo.saved_64 = res;
        if (res != 0)
            r = 0;
    } else {
        r = ext_call(arg);
    }
    return r;
}

/* 25. distinct literals in the two arms. */
int fp_literal_branch(int a)
{
    if (a) {
        ext_void();
        return 0x1111;
    }
    ext_void();
    return 0x2222;
}

/* 26. nested branch with literals, closer to the service layout. */
int fp_pool_far(int a)
{
    int r;
    if (a) {
        r = ext_call(a) + 0x1234;
        if (r > 5)
            r = ext_call(r) + 0x5678;
        else
            r = 0;
    } else {
        r = 1;
    }
    return r;
}
