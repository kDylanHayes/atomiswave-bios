! set_system_bits
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0x484
        .global set_system_bits
set_system_bits:
        mov.l .L4f0, r1
        mov.l @r1, r0
        or #5, r0
        mov.l r0, @r1
        mov.l .L4f4, r1
        mov.l .L4f8, r2
.L490:
        mov.l @r1, r0
        tst r2, r0
        bf .L490
        mov.l .L4fc, r1
        mov #-9, r2
        mov.l @r1, r0
        and r2, r0
        mov.l r0, @r1
        mov.l .L500, r0
        mov.l .L504, r1
        jsr r1
        nop
        mov.l .L4fc, r1
        mov #8, r2
        mov.l @r1, r0
        or r2, r0
        mov.l r0, @r1
        mov.l .L508, r1
        mov.l .L50c, r2
        mov.l .L510, r0
.L4b8:
        mov.l r0, @r1
        add #4, r1
        dt r2
        bf .L4b8
        mov.l .L4fc, r1
        mov #-9, r2
        mov.l @r1, r0
        and r2, r0
        mov.l r0, @r1
        mov.l .L514, r1
        mov.l @r1, r0
        mov.l .L518, r1
        cmp/eq r1, r0
        bf 0x538
        mov.l .L51c, r11
        mov.l .L520, r1
        mov.l .L524, r2
        mov.l .L528, r3
        jsr r11
        nop
        mov.l .L52c, r1
        mov.l .L530, r2
        mov.l .L534, r3
        jsr r11
        nop
.L4ea:
        bra .L4ea
        nop
        .word   0x0000
.L4f0:
        .long   0xa05f8044
.L4f4:
        .long   0xa05f810c
.L4f8:
        .long   0x00002000
.L4fc:
        .long   0xa05f80e8
.L500:
        .long   0x0000012c
.L504:
        .long   0x0000097c
.L508:
        .long   0xa5000000
.L50c:
        .long   0x00025800
.L510:
        .long   0x528a528a
.L514:
        .long   0x0cfffffc
.L518:
        .long   0x000000ff
.L51c:
        .long   0x0000099c
.L520:
        .long   0x00000c34
.L524:
        .long   0xa5041200
.L528:
        .long   0x00000008
.L52c:
        .long   0x00000c3c
.L530:
        .long   0xa504b168
.L534:
        .long   0x00000011
