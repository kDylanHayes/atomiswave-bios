! exc_general
! File 0x100, the general-exception vector. The entry uses r0, r1, and
! r2 from the interrupted code. It polls RFCR (0xFF800028) until the
! halfword is above 8, then branches over a BSC literal pool to 0x204.
! Later it calls mix_shifts and branches to init_memory.
! Byte-checked assembly, not matched C.

        .org    0x100
        .global exc_general
exc_general:
        mov.w r0, @r2
        mov.l @(32,r1), r0
        mov.l .L144, r2
        mov.w r0, @r2
        mov.l @(36,r1), r0
        mov.l .L14c, r2
        mov.l r0, @r2
        mov.l .L144, r2
        mov #8, r3
.L112:
        mov.w @r2, r0
        cmp/hi r3, r0
        bf .L112
        bra .L204
        nop
        .long   0x700000f0
        .long   0x00000150
        .long   0xff800000
        .long   0xff800004
        .long   0xff800008
        .long   0xff80000c
        .long   0xff800010
        .long   0xff80001c
        .long   0xff800024
        .long   0xff800020
.L144:
        .long   0xff800028
        .long   0xfffffffb
.L14c:
        .long   0xff800014
        .long   0xa3020008
        .long   0x00000001
        .long   0x01110111
        .long   0x618066d8
        .long   0x07777777
        .long   0x0000a594
        .long   0x0000a55e
        .long   0x0000a521
        .long   0x000003ec
        .long   0xc00a0e24
        .long   0xff940190
        .long   0x00090009
        .long   0x001b0009
        .long   0x0009affd
        .long   0x00000000
        .long   0x00090009
        .long   0x0009002b
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x00000000
        .long   0x0000a678
.L204:
        mov.l .L238, r1
        mov.l .L23c, r2
        mov.l @r1, r3
        add #4, r1
.L20c:
        mov.l @r2, r0
        mov.l @r1, r4
        add #4, r1
        add #4, r2
        mov.l r0, @r4
        dt r3
        bf .L20c
        mov.l .L240, r1
        mov.l .L244, r3
        mov.w @r1, r0
        shlr8 r0
        and #3, r0
        tst r0, r0
        bt .L264
        and #1, r0
        tst r0, r0
        bt .L250
        mov.l .L248, r2
        mov.l .L24c, r0
        mov.l r0, @r3
        bra .L26a
        nop
.L238:
        .long   0x00000a10
.L23c:
        .long   0x00000a80
.L240:
        .long   0xff800030
.L244:
        .long   0xa0702c00
.L248:
        .long   0x00000b90
.L24c:
        .long   0x00000301
.L250:
        mov.l .L25c, r2
        mov.l .L260, r0
        mov.l r0, @r3
        bra .L26a
        nop
        .word   0x0000
.L25c:
        .long   0x00000b90
.L260:
        .long   0x00000201
.L264:
        mov.l .L2a4, r2
        mov #1, r0
        mov.l r0, @r3
.L26a:
        mov.l .L2a8, r1
        mov.l @r1, r3
        add #4, r1
.L270:
        mov.l @r2, r0
        mov.l @r1, r4
        add #4, r1
        add #4, r2
        mov.l r0, @r4
        dt r3
        bf .L270
        mov.l .L2ac, r1
        mov.l .L2b0, r2
        mov #12, r3
.L284:
        mov.w @+r1, r0
        mov.w r0, @r2
        add #2, r2
        dt r3
        bf .L284
        mov.l .L2b4, r1
        mov.l .L2b8, r0
        mov.l r0, @r1
        mov.l .L2bc, r1
        mov.l @r1, r0
        and #3, r0
        tst r0, r0
        bf .L2c0
        bra 0x350
        nop
        .word   0x0000
.L2a4:
        .long   0x00000b40
.L2a8:
        .long   0x00000aec
.L2ac:
        .long   0x0000017c
.L2b0:
        .long   0xac000000
.L2b4:
        .long   0xa05f8040
.L2b8:
        .long   0x00000000
.L2bc:
        .long   0xa0600280
.L2c0:
        mov.l .L2ec, r0
        mov.l .L2f0, r1
        mov.l .L2f4, r2
.L2c6:
        mov.l .L2f8, r11
        jsr r11
        nop
        mov.l r0, @r1
        add #4, r1
        dt r2
        bf .L2c6
        mov.l .L2ec, r0
        mov.l .L2f0, r1
        mov.l .L2f4, r2
.L2da:
        mov.l .L2f8, r11
        jsr r11
        nop
        mov.l @r1, r3
        cmp/eq r3, r0
        bt .L2fc
        bra .L306
        nop
        .word   0x0000
.L2ec:
        .long   0x80000000
.L2f0:
        .long   0xac000000
.L2f4:
        .long   0x00400000
.L2f8:
        .long   0x00000318
.L2fc:
        add #4, r1
        dt r2
        bf .L2da
        bra 0x350
        nop
.L306:
        mov.l .L310, r0
        mov.l .L314, r1
        mov.l r0, @r1
        bra 0x350
        nop
.L310:
        .long   0x000000ff
.L314:
        .long   0x0cfffffc
