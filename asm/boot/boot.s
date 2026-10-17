! boot
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0x5c
        .global boot
boot:
        mov.l .L74, r1
        mov.l .L78, r0
        or r0, r1
        mov.l .L7c, r2
        or r0, r2
.L66:
        mov.l @r1, r0
        add #4, r1
        cmp/hi r1, r2
        bt .L66
        bra .L84
        nop
        .word   0x0000
.L74:
        .long   0x00000080
.L78:
        .long   0xa0000000
.L7c:
        .long   0x0000a678
        .long   0x00000000
.L84:
        mov.l 0x11c, r0
        ldc r0, sr
        mov.l 0x120, r1
        mov.l @r1, r0
        mov.l 0x124, r2
        mov.l r0, @r2
        mov.l @(4,r1), r0
        mov.l 0x128, r2
        mov.w r0, @r2
        mov.l @(8,r1), r0
        mov.l 0x12c, r2
        mov.l r0, @r2
        mov.l @(12,r1), r0
        mov.l 0x130, r2
        mov.l r0, @r2
        mov.l @(16,r1), r0
        mov.l 0x134, r2
        mov.l r0, @r2
        mov.l @(20,r1), r0
        mov.l 0x138, r2
        mov.w r0, @r2
        mov.l @(24,r1), r0
        mov.l 0x13c, r2
        mov.w r0, @r2
        mov.l @(28,r1), r0
        mov.l 0x140, r2
        mov.w r0, @r2
        mov.l @(32,r1), r0
        mov.l 0x144, r2
        mov.w r0, @r2
        mov.l @(36,r1), r0
        mov.l 0x148, r2
        and r2, r0
        mov.l 0x14c, r2
        mov.l r0, @r2
        mov #-1, r0
        mov.l @(40,r1), r2
        mov.b r0, @r2
        mov.l @(36,r1), r0
        mov.l 0x14c, r2
        mov.l r0, @r2
        mov.l 0x144, r2
        mov #8, r3
.Lda:
        mov.w @r2, r0
        cmp/hi r3, r0
        bf .Lda
        mov.l @(36,r1), r0
        mov.l 0x148, r2
        and r2, r0
        mov.l 0x14c, r2
        mov.l r0, @r2
        mov #-1, r0
        mov.l @(40,r1), r2
        mov.b r0, @r2
        mov.l @(20,r1), r0
        mov.l 0x138, r2
        mov.w r0, @r2
        mov.l @(24,r1), r0
        mov.l 0x13c, r2
        mov.w r0, @r2
        mov.l @(28,r1), r0
        mov.l 0x140, r2
