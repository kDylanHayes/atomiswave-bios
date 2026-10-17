! FUN_09e68
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0x9e68
        .global FUN_09e68
FUN_09e68:
        mov.l r14, @-r15
        stc gbr, r3
        mov.l .L9f00, r2
        mov.l r13, @-r15
        sts.l pr, @-r15
        ldc r2, gbr
        add #-4, r15
        mov.l r3, @r15
        mov.w @(gbr,144), r0
        mov r0, r14
        exts.w r14, r3
        cmp/pz r3
        bt .L9e86
        bsr 0xa15e
        nop
.L9e86:
        exts.w r14, r0
        cmp/eq #-8, r0
        bf .L9e90
        bra .L9f70
        nop
.L9e90:
        cmp/eq #-7, r0
        bt .L9eec
        cmp/eq #-6, r0
        bt .L9ed6
        cmp/eq #-5, r0
        bt .L9f5e
        cmp/eq #-4, r0
        bt .L9eec
        cmp/eq #-3, r0
        bt .L9ed6
        cmp/eq #-2, r0
        bt .L9ece
        cmp/eq #-1, r0
        bt .L9ebc
        cmp/eq #0, r0
        bsr 0x9d52
        nop
        mov #38, r0
        or.b #1, @(r0,gbr)
        mov #10, r0
        bra .L9f46
        mov.w r0, @(gbr,70)
.L9ebc:
        mov.l @(gbr,48), r0
        mov #0, r2
        cmp/hi r2, r0
        bf .L9eca
        mov.l @(gbr,48), r0
        bra .L9f82
        mov r0, r14
.L9eca:
        bra .L9f82
        mov #127, r14
.L9ece:
        mov #24, r0
        bsr 0xa1d4
        mov.l r0, @(gbr,236)
        mov #-3, r14
.L9ed6:
        bsr 0xa3a0
        mov #0, r4
        cmp/eq #1, r0
        bt/s .L9f30
        mov r0, r4
        tst r4, r4
        bf .L9f82
        bsr 0xa1d4
        add #-1, r14
        bra .L9f82
        nop
.L9eec:
        bsr 0xa3a0
        mov #1, r4
        cmp/eq #-2, r0
        bf/s .L9f04
        mov r0, r13
        bra .L9f22
        add #-2, r14
        .word   0x0000
        .long   0x8c008000
.L9f00:
        .long   0x8c000000
.L9f04:
        tst r13, r13
        bf .L9f22
        mov.l @(gbr,76), r0
        mov.w .L9fac, r2
        cmp/eq r2, r0
        bf .L9f14
        bra .L9f22
        add #-1, r14
.L9f14:
        bsr 0x9e50
        nop
        tst r0, r0
        bt .L9f20
        bra .L9f22
        mov #0, r14
.L9f20:
        mov #1, r13
.L9f22:
        mov r13, r0
        cmp/eq #1, r0
        bf .L9f82
        bsr 0x9e34
        nop
        cmp/eq #-1, r0
        bf .L9f34
.L9f30:
        bra .L9f82
        mov #-1, r14
.L9f34:
        mov.l @(gbr,48), r0
        cmp/eq #2, r0
        bt .L9f4a
        cmp/eq #6, r0
        bt .L9f46
        cmp/eq #16, r0
        bt .L9f4e
        bra .L9f5a
        nop
.L9f46:
        bra .L9f82
        mov #-2, r14
.L9f4a:
        bra .L9f82
        add #2, r14
.L9f4e:
        bsr 0x9e50
        nop
        tst r0, r0
        bf .L9f7c
        bra .L9f82
        nop
.L9f5a:
        bra .L9f82
        mov #-1, r14
.L9f5e:
        mov.l .L9fb0, r4
        mov.l .L9fb4, r2
        jsr r2
        nop
        mov.l @(gbr,100), r0
        bsr 0xa1d4
        mov.l r0, @(gbr,248)
        bra .L9ed6
        mov #-6, r14
.L9f70:
        mov.l @(gbr,100), r0
        mov.l .L9fb8, r3
        jsr r3
        mov r0, r4
        tst r0, r0
        bf .L9f80
.L9f7c:
        bra .L9f82
        mov #0, r14
.L9f80:
        mov #126, r14
.L9f82:
        exts.w r14, r3
        mov.w @(gbr,146), r0
        exts.w r0, r0
        cmp/ge r0, r3
        bt .L9f8e
        mov #0, r14
.L9f8e:
        exts.w r14, r3
        cmp/pz r3
        bf .L9f98
        bsr 0x9db8
        nop
.L9f98:
        mov r14, r0
        mov.w r0, @(gbr,144)
        mov.l @r15, r2
        exts.w r14, r0
        ldc r2, gbr
        add #4, r15
        lds.l @+r15, pr
        mov.l @+r15, r13
        rts
        mov.l @+r15, r14
.L9fac:
        .long   0x00000080
.L9fb0:
        .long   0x8c000fc4
.L9fb4:
        .long   0x8c0005b8
.L9fb8:
        .long   0x8c0004f4
