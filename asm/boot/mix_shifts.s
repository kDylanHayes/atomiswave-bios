! mix_shifts
! File 0x318. Four shld steps. The pool counts are -1, -21, -31, and +1.
! The +1 is also the mask applied before the last shift.

        .org    0x318
        .global mix_shifts
mix_shifts:
        mov     r0, r13
        mov     r13, r11
        mov.l   .Lminus1, r12
        shld    r12, r11
        xor     r11, r0
        mov     r13, r11
        mov.l   .Lminus21, r12
        shld    r12, r11
        xor     r11, r0
        mov     r13, r11
        mov.l   .Lminus31, r12
        shld    r12, r11
        xor     r11, r0
        xor     #1, r0
        mov.l   .Lone, r12
        and     r12, r0
        shld    r12, r13
        or      r13, r0
        rts
        nop
.Lminus1:
        .long   0xffffffff
.Lminus21:
        .long   0xffffffeb
.Lminus31:
        .long   0xffffffe1
.Lone:
        .long   0x00000001
