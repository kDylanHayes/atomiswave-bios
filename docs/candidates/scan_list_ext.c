/*
 * scan_list -- extern-call source shape.
 *
 * The four 0x8C00xxxx calls are declared extern and bound with the
 * linker (DEFINE sym(address)), which is how SDK code would have called
 * them. The compiler then keeps one literal per call site instead of
 * caching the address in a callee-saved register, which is what the
 * flash does.
 */
#include <machine.h>

#pragma gbr_base (gbr)
struct {
    char pad0[36];
    unsigned char flag_36;
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

extern int sys_4d8(char *);
extern int sys_590(char *);
extern int sys_598(char *, int);
extern void sys_800(int);

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

    sys_4d8(list);
    gbr.cmd_236 = 17;
    gbr.arg_240 = bound;
    gbr.arg_244 = 1;
    gbr.arg_248 = (int)list;
    gbr.arg_252 = 0;
    if (run_transfer())
        return 0;
    if (sys_590(list))
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
            if (sys_598(cursor + 33, gbr.word_156) == 0) {
                a = hole_9ce2((int)(cursor + 14));
                b = hole_9ce2((int)(cursor + 6)) + 0x96;
                if (b < 0x6DDD0 && gbr.flag_36 != 2)
                    sys_800(1);
                gbr.arg_240 = b;
                gbr.arg_244 = (a + 0x7FF) >> 11;
                gbr.arg_248 = (gbr.flag_36 == 0) ? (int)list : 0;
                gbr.arg_252 = (gbr.flag_36 == 0) ? 0 : a;
                gbr.count_70 = 10;
                prime_count68();
                gbr.cmd_236 = (gbr.flag_36 != 0) ? 28 : 17;
                retry_issue(0);
                hole_9cdc();
                return a;
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
