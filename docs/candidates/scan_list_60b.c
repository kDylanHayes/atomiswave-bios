/*
 * scan_list -- SHC 6.0B candidate, not byte-identical.
 *
 * The loop, list types, GBR stores, and fixed-address calls are
 * structurally right. 6.0B compiles this to 159 instructions against the
 * flash's 161. The remaining gap is the allocator/scheduler:
 *   - list is assigned to R13; the flash uses R12 (p/idx uses R12 here,
 *     R13 in the flash);
 *   - saved and the 0x6DDD0 bound land in R10/R9; the flash uses R9/R10;
 *   - 6.0B caches the 0x8C000598 and 0x8C000800 callbacks in callee-saved
 *     registers, while the flash reloads them from the pool each pass;
 *   - the constant-index loads use add+mov.b here, @(r0,r14) in the flash.
 * 5.1 produces the same register order as 6.0B; 6.0AD spills the frame.
 * Kept as the starting point for a later Atomiswave-era build or a
 * register-renaming canonicaliser.
 */
#include <machine.h>

#pragma gbr_base (gbr)
struct {
    char pad0[36];
    volatile unsigned char flag_36;
    char pad37[33];
    unsigned short count_70;
    char pad72[84];
    int word_156;
    char pad160[76];
    int cmd_236;
    int arg_240;
    int arg_244;
    int arg_248;
    int arg_252;
} gbr;

static int hole_9ce2(int);
static int hole_9cdc(void);
static int run_transfer(void);
static int retry_issue(int);
static void prime_count68(void);

int scan_list(char *list, int bound)
{
    unsigned int a, b;
    char *cursor = list;
    char *limit;
    unsigned char saved;
    unsigned char idx;
    char *p;

    ((int (*)(char *))0x8C0004D8)(list);
    gbr.cmd_236 = 17;
    gbr.arg_240 = bound;
    gbr.arg_244 = 1;
    gbr.arg_248 = (int)list;
    gbr.arg_252 = 0;
    if (run_transfer())
        return 0;
    if (((int (*)(char *))0x8C000590)(list))
        return 0;
    a = hole_9ce2((int)(list + 0xA2));
    gbr.arg_240 = a + 0x96;
    gbr.arg_244 = 1;
    gbr.arg_248 = (int)list;
    gbr.arg_252 = 0;
    gbr.cmd_236 = 17;
    run_transfer();
    cursor = list;
    limit = list + 0x800;
    while (*cursor != 0 && cursor < limit) {
        if ((*(unsigned char *)(cursor + 25) & 2) == 0) {
            idx = *(unsigned char *)(cursor + 32);
            p = cursor + 33 + idx;
            saved = *p;
            *p = 59;
            if (((int (*)(char *, int))0x8C000598)(cursor + 33, gbr.word_156) == 0) {
                a = hole_9ce2((int)(cursor + 14));
                b = hole_9ce2((int)(cursor + 6)) + 0x96;
                if (b < 0x6DDD0 && gbr.flag_36 != 2)
                    ((void (*)(int))0x8C000800)(1);
                gbr.arg_240 = b;
                gbr.arg_244 = (a + 0x7FF) >> 11;
                gbr.arg_248 = (gbr.flag_36 == 0) ? (int)list : 0;
                gbr.arg_252 = (gbr.flag_36 == 0) ? 0 : a;
                gbr.count_70 = 10;
                prime_count68();
                gbr.cmd_236 = (gbr.flag_36 != 0) ? 28 : 17;
                retry_issue(0);
                hole_9cdc();
                return (int)a;
            }
            *p = saved;
        }
        cursor += *(unsigned char *)cursor;
    }
    return 0;
}

static int hole_9ce2(int x) { return x; }
static int hole_9cdc(void) { return 0; }
static int run_transfer(void) { return 0; }
static int retry_issue(int x) { return x; }
static void prime_count68(void) {}
