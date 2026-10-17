! init_memory
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0x350
        .global init_memory
init_memory:
        mov.l .L3a0, r1
        mov.l .L3a4, r0
        mov.l r0, @r1
        mov.l .L3a8, r1
        mov.l .L3ac, r0
        mov.l r0, @r1
        mov.l .L3b0, r1
        mov.l .L3b4, r0
        mov.l r0, @r1
        mov.l .L3b8, r1
        mov.l .L3bc, r0
        mov.l r0, @r1
        add #4, r1
        mov.l r0, @r1
        mov.l .L3c0, r1
        mov.l .L3c4, r0
        mov.l r0, @r1
        add #4, r1
        mov.l .L3c8, r0
        mov.l r0, @r1
        add #4, r1
        mov #1, r0
        mov.l r0, @r1
        add #8, r1
        mov.l r0, @r1
        add #4, r1
        mov.l r0, @r1
.L386:
        nop
        nop
        mov.l @r1, r0
        tst #1, r0
        bf .L386
        mov.l .L3cc, r1
        mov.l @r1, r0
        and #3, r0
        tst r0, r0
        bf .L3d0
        bra 0x538
        nop
        .word   0x0000
.L3a0:
        .long   0xa05f74b8
.L3a4:
        .long   0x8843007f
.L3a8:
        .long   0xa05f7490
.L3ac:
        .long   0x00000a32
.L3b0:
        .long   0xa05f74a0
.L3b4:
        .long   0x0000600a
.L3b8:
        .long   0xa05f7000
.L3bc:
        .long   0x00000000
.L3c0:
        .long   0xa05f7404
.L3c4:
        .long   0x0c010000
.L3c8:
        .long   0x00000100
.L3cc:
        .long   0xa0600280
.L3d0:
        mov.l 0x428, r1
        mov #0, r0
        mov.l r0, @r1
        add #80, r0
        shll2 r0
        shll2 r0
        add #4, r1
        mov.l r0, @r1
        mov.l 0x42c, r1
        mov.l @r1, r0
        mov #-9, r2
        and r2, r0
        or #8, r0
        mov.l r0, @r1
        mov.l 0x430, r1
        mov.l 0x434, r2
        mov #-1, r0
.L3f2:
        mov.l r0, @r1
        add #4, r1
        dt r2
        bf .L3f2
        mov.l 0x438, r1
        mov.l 0x43c, r2
        mov.l 0x440, r3
