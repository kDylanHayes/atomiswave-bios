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
    volatile int saved_64;
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
    volatile int cmd_236;
    int arg_240;
    int arg_244;
    int arg_248;
    int arg_252;
    char pad256[308];
    int ptr_564;
} hi;

#pragma global_register (k8=R8, k9=R9, k10=R10, k11=R11, k12=R12, k13=R13)
int k8;
int k9;
int k10;
int k11;
int k12;
int k13;

static int reject_code(void);
static void prime_count68(void);

int issue_command(int arg)
{
    int res;
    int r = 1;

    if (arg == 0) {
        res = ((int (*)(int, void *, int, int))0x8c0010f0)(hi.cmd_236, (void *)((int)get_gbr() + 240), 0, 0);
        lo.saved_64 = res;
        if (res != 0)
            r = 0;
    } else {
        res = ((int (*)(int, void *, int, int))0x8c0010f0)(lo.saved_64, (void *)((int)get_gbr() + 48), 0, 1);
        hi.result_232 = res;
        if (res == 2) {
            r = 0;
        } else if (res == -1) {
            lo.count_68 = 0;
            switch (lo.word_48) {
            case 0:
            case 1:
            case 2:
            case 5:
            case 6:
            case 11:
            case 16:
                lo.count_70 = 0;
                break;
            }
        } else {
            if (res == 0)
                r = 0;
            else if (res == 1 || res == 3)
                r = -1;
        }
        if (r != -1) {
            res = ((int (*)(int, void *, int, int))0x8c0010f0)((int)get_gbr() + 72, 0, 0, 4);
            if (res == 0) {
                if (reject_code() == -1) {
                    lo.count_68 = 0;
                    lo.count_70 = 0;
                }
            }
        }
    }
    if (r == 1 || r == -1) {
        unsigned int t;
        t = lo.count_68;
        if (t != 0) {
            lo.count_68 += 0xFFFF;
            r = -1;
        } else {
            t = lo.count_70;
            if (t != 0) {
                lo.count_70 += 0xFFFF;
                prime_count68();
                r = -2;
            }
        }
    }
    return r;
}

static int reject_code(void)
{
    return 0;
}

static void prime_count68(void)
{
}
