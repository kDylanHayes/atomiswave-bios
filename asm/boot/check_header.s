! check_header
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0x538
        .global check_header
check_header:
        mov.l .L54c, r4
        mov.l .L550, r1
        mov #4, r3
.L53e:
        mov.l @+r1, r0
        mov.l @+r4, r2
        cmp/eq r0, r2
        bt .L554
        bra .L55c
        nop
        .word   0x0000
.L54c:
        .long   0xac010000
.L550:
        .long   0x00000a00
.L554:
        dt r3
        bf .L53e
        bra 0x7a4
        nop
.L55c:
        mov.l 0x674, r11
        mov.l 0x678, r1
        mov.l 0x67c, r2
        mov.l 0x680, r3
        jsr r11
        nop
        mov.l 0x684, r1
        mov.l 0x688, r2
        mov.l 0x68c, r3
        jsr r11
        nop
        mov.l 0x690, r0
        mov.l 0x694, r1
        jsr r1
        nop
        mov.l 0x698, r1
        mov.l 0x69c, r2
        mov.l 0x6a0, r0
.L580:
        mov.l r0, @r1
        add #4, r1
        dt r2
        bf .L580
        mov.l 0x698, r1
        mov.l 0x6a4, r2
        mov.l 0x6a8, r3
.L58e:
        mov r1, r4
        mov.l 0x6ac, r5
        mov.l 0x6b0, r0
        mov.l 0x6b4, r6
        cmp/eq r6, r3
        bf .L59c
        mov.l 0x6b8, r0
.L59c:
        mov.l r0, @r4
        add r2, r4
        dt r5
        bf .L59c
        mov.l 0x6bc, r0
        add r0, r1
        mov.l 0x6c0, r0
        cmp/eq r0, r3
        bf .L5b2
        mov.l 0x6c4, r0
        sub r0, r1
.L5b2:
        dt r3
        bf .L58e
        mov.l 0x698, r1
        mov.l 0x6c8, r2
.L5ba:
        mov r1, r6
        mov.l 0x6cc, r5
.L5be:
        mov.l 0x6d0, r0
        mov.l 0x6c0, r7
        cmp/eq r5, r7
        bf .L5c8
        mov.l 0x6d4, r0
.L5c8:
        mov r6, r4
        mov.l 0x6d8, r3
.L5cc:
        mov.l r0, @r4
        add #4, r4
        dt r3
        bf .L5cc
        mov.l 0x6a4, r0
        add r0, r6
        dt r5
        bf .L5be
        mov.l 0x6dc, r0
        add r0, r1
        mov.l 0x6c0, r0
        cmp/eq r0, r2
        bf .L5ea
        mov.l 0x6e0, r0
        sub r0, r1
.L5ea:
        dt r2
        bf .L5ba
        mov.l 0x6e4, r1
        mov.l 0x6e8, r2
        mov.l 0x6ec, r0
        mov r1, r4
        mov.l 0x6f0, r3
.L5f8:
        mov.l r0, @r4
        add #4, r4
        dt r3
        bf .L5f8
