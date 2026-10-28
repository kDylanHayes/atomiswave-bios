/*
 * scan_list -- SHC 6.0B candidate, not byte-identical.
 *
 * This is the closest source shape found. Using a struct pointer makes
 * 6.0B emit the flash's indexed loads:
 *
 *     mov #25,r0 ; mov.b @(r0,r14),r2
 *     mov #32,r0 ; mov.b @(r0,r14),r5
 *
 * It still differs in the callee-saved allocation and the loop schedule:
 * list goes to R13 (flash R12), p/entry to R12 (flash R13), saved and
 * the 0x6DDD0 bound to R10/R9 (flash R9/R10), and the 0x8C000598 /
 * 0x8C000800 callbacks are cached instead of reloaded from the pool.
 * 113 of the flash's 161 instructions align; the rest need a register
 * allocator that 5.0, 5.1, 6.0A/B/C and 6.0AD do not provide.
 * Kept as the best starting point for a later Atomiswave-era build.
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

struct entry {
    unsigned char len;
    unsigned char pad1[24];
    unsigned char flags;
    unsigned char pad26[6];
    unsigned char type;
    unsigned char data[1];
};

static int hole_9ce2(int);
static int hole_9cdc(void);
static int run_transfer(void);
static int retry_issue(int);
static void prime_count68(void);

int scan_list(char *arg_list, int bound)
{
    unsigned int a, b;
    unsigned char *list = (unsigned char *)arg_list;
    struct entry *entry;
    unsigned char *limit;
    unsigned char *p;
    unsigned char saved;
    unsigned char idx;

    ((int (*)(unsigned char *))0x8C0004D8)(list);
    gbr.cmd_236 = 17;
    gbr.arg_240 = bound;
    gbr.arg_244 = 1;
    gbr.arg_248 = (int)list;
    gbr.arg_252 = 0;
    if (run_transfer())
        return 0;
    if (((int (*)(unsigned char *))0x8C000590)(list))
        return 0;
    a = (unsigned int)hole_9ce2((int)(list + 0xA2));
    gbr.arg_240 = (int)(a + 0x96);
    gbr.arg_244 = 1;
    gbr.arg_248 = (int)list;
    gbr.arg_252 = 0;
    gbr.cmd_236 = 17;
    run_transfer();
    entry = (struct entry *)list;
    limit = list + 0x800;
    while (entry->len != 0 && (unsigned char *)entry < limit) {
        if ((entry->flags & 2) == 0) {
            idx = entry->type;
            p = &entry->data[idx];
            saved = *p;
            *p = 59;
            if (((int (*)(unsigned char *, int))0x8C000598)(&entry->data[0], gbr.word_156) == 0) {
                a = (unsigned int)hole_9ce2((int)((unsigned char *)entry + 14));
                b = (unsigned int)hole_9ce2((int)((unsigned char *)entry + 6)) + 0x96;
                if (b < 0x6DDD0 && gbr.flag_36 != 2)
                    ((void (*)(int))0x8C000800)(1);
                gbr.arg_240 = (int)b;
                gbr.arg_244 = (int)((a + 0x7FF) >> 11);
                gbr.arg_248 = (gbr.flag_36 == 0) ? (int)list : 0;
                gbr.arg_252 = (gbr.flag_36 == 0) ? 0 : (int)a;
                gbr.count_70 = 10;
                prime_count68();
                gbr.cmd_236 = (gbr.flag_36 != 0) ? 28 : 17;
                retry_issue(0);
                hole_9cdc();
                return (int)a;
            }
            *p = saved;
        }
        entry = (struct entry *)((unsigned char *)entry + entry->len);
    }
    return 0;
}

static int hole_9ce2(int x) { return x; }
static int hole_9cdc(void) { return 0; }
static int run_transfer(void) { return 0; }
static int retry_issue(int x) { return x; }
static void prime_count68(void) {}
