/*
 * scan_list -- struct addressing + linker-bound extern calls.
 *
 * The struct pointer makes 6.0B emit the flash's indexed loads:
 *     mov #25,r0 ; mov.b @(r0,r14),r2
 *     mov #32,r0 ; mov.b @(r0,r14),r5
 * The extern declarations (bound with DEFINE sym(address)) keep one
 * literal per call site instead of caching the address in R8/R9.
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

struct entry {
    unsigned char len;
    unsigned char pad1[24];
    unsigned char flags;
    unsigned char pad26[6];
    unsigned char type;
    unsigned char data[1];
};

extern int sys_4d8(char *);
extern int sys_590(char *);
extern int sys_598(unsigned char *, int);
extern void sys_800(int);

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
    unsigned char *data;
    unsigned char saved;

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
            data = &entry->data[0];
            p = data + entry->type;
            saved = *p;
            *p = 59;
            if (sys_598(data, gbr.word_156) == 0) {
                a = (unsigned int)hole_9ce2((int)((unsigned char *)entry + 14));
                b = (unsigned int)hole_9ce2((int)((unsigned char *)entry + 6)) + 0x96;
                if (b < 0x6DDD0 && gbr.flag_36 != 2)
                    sys_800(1);
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
