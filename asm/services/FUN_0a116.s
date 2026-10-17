! FUN_0a116
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0xa116
        .global FUN_0a116
FUN_0a116:
        stc sr, r3
        mov.l 0xa1b4, r2
        sts.l pr, @-r15
        or r2, r3
        ldc r3, sr
        mov.l 0xa1b8, r3
        ldc r3, vbr
        mov.l 0xa1bc, r1
        jsr r1
        nop
        mov.l 0xa1c0, r0
        mov.l r0, @(gbr,564)
        mov #8, r3
        mov.l 0xa1c4, r4
        mov.l r3, @r4
        mov.l @r4, r2
        stc sr, r1
        mov.l 0xa178, r3
        and r3, r1
        ldc r1, sr
        mov.l 0xa1c8, r2
        jmp r2
        lds.l @+r15, pr
