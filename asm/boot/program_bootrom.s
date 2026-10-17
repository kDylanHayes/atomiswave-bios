! program_bootrom
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0x7a4
        .global program_bootrom
program_bootrom:
        mov.l .L7bc, r1
        mov.l .L7c0, r2
        mov #16, r3
.L7aa:
        mov.l @+r1, r0
        mov.l @+r2, r4
        cmp/eq r0, r4
        bf .L7c4
        dt r3
        bf .L7aa
        bra .L8c0
        nop
        .word   0x0000
.L7bc:
        .long   0xa0018000
.L7c0:
        .long   0xac010010
.L7c4:
        mov.l .L7ec, r11
        mov.l .L7f0, r1
        mov.l .L7f4, r2
        mov.l .L7f8, r3
        jsr r11
        nop
        mov.l .L7fc, r1
        mov.l .L800, r2
        mov.l .L804, r3
        jsr r11
        nop
        mov.l .L808, r0
        mov.l .L80c, r1
        mov.l .L810, r2
.L7e0:
        mov.l r0, @r1
        add #4, r1
        dt r2
        bf .L7e0
        bra .L814
        nop
.L7ec:
        .long   0x0000099c
.L7f0:
        .long   0x00000c77
.L7f4:
        .long   0xa5041200
.L7f8:
        .long   0x00000006
.L7fc:
        .long   0x00000c7d
.L800:
        .long   0xa504b0c0
.L804:
        .long   0x0000001b
.L808:
        .long   0x00000000
.L80c:
        .long   0xa0200000
.L810:
        .long   0x00008000
.L814:
        mov.l .L840, r0
        mov.l @+r0, r2
        mov.l @+r0, r3
        mov.l @+r0, r4
        mov.l @+r0, r5
        mov.l @+r0, r6
        mov.l @+r0, r7
.L822:
        mov.l @+r0, r1
        mov.b r3, @r2
        mov.b r2, @r3
        mov.b r4, @r2
        mov.b r3, @r2
        mov.b r2, @r3
        mov.b r6, @r1
.L830:
        mov.b @r1, r8
        cmp/eq r8, r5
        bf .L830
        dt r7
        bf .L822
        bra .L868
        nop
        .word   0x0000
.L840:
        .long   0x00000844
        .long   0xa0000555
        .long   0xa00002aa
        .long   0x00000080
        .long   0xffffffff
        .long   0x00000030
        .long   0x00000003
        .long   0xa0010000
        .long   0xa0018000
        .long   0xa001c000
.L868:
        mov.l .L8a4, r2
        mov.l .L8a8, r3
        mov.l .L8ac, r4
        mov.l .L8b0, r5
        mov #-86, r6
        mov #85, r7
        mov #-96, r8
        mov #16, r9
.L878:
        mov.l @+r2, r0
        mov #4, r10
.L87c:
        mov.b r6, @r4
        mov.b r7, @r5
        mov.b r8, @r4
        mov.b r0, @r3
        mov.l .L8b4, r1
.L886:
        nop
        dt r1
        bf .L886
        add #1, r3
        shlr8 r0
        dt r10
        bf .L87c
        dt r9
        bf .L878
        mov.l .L8b8, r0
        mov.l .L8bc, r1
        jsr r1
        nop
        bra .L8c0
        nop
.L8a4:
        .long   0xac010010
.L8a8:
        .long   0xa0018000
.L8ac:
        .long   0xa0000555
.L8b0:
        .long   0xa00002aa
.L8b4:
        .long   0x00001fff
.L8b8:
        .long   0x000000b4
.L8bc:
        .long   0x0000097c
.L8c0:
        mov.l .L918, r4
        mov.l .L91c, r0
        add r0, r4
        mov.l @r4, r2
        shlr r2
        mov.l .L918, r4
        mov.l .L920, r0
        add r0, r4
        mov.l @r4, r3
        mov.l .L918, r4
        mov.l .L924, r0
        add r0, r4
        mov.l @r4, r5
        mov.l .L918, r4
        mov.l .L928, r0
        add r0, r4
        mov.l @r4, r6
        mov.l .L92c, r1
        mov.l r2, @r1
        add #4, r1
        shlr16 r2
        mov.l r2, @r1
        mov.l .L930, r1
        mov.l r3, @r1
        add #4, r1
        mov.l r5, @r1
        add #4, r1
        mov #1, r0
        mov.l r0, @r1
        add #8, r1
        mov.l r0, @r1
        add #4, r1
        mov.l r0, @r1
.L902:
        nop
        nop
        mov.l @r1, r0
        tst #1, r0
        bf .L902
        add #-4, r1
        mov #0, r0
        mov.l r0, @r1
        bra .L948
        nop
        .word   0x0000
.L918:
        .long   0xac010000
.L91c:
        .long   0x00000060
.L920:
        .long   0x00000064
.L924:
        .long   0x00000068
.L928:
        .long   0x0000006c
.L92c:
        .long   0xa05f7000
.L930:
        .long   0xa05f7404
        .long   0xd003d102
        .long   0xaffe2102
        .long   0x00000009
        .long   0xa05f8040
        .long   0x00ffff00
.L948:
        mov.l .L96c, r2
        mov.l .L970, r1
        mov.l r1, @r2
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        mov.l .L974, r0
        ldc r0, sr
        mov.l .L978, r0
        or r6, r0
        jmp r0
        nop
        .word   0x0000
.L96c:
        .long   0xff00001c
.L970:
        .long   0x00000808
.L974:
        .long   0x700000f0
.L978:
        .long   0xa0000000
