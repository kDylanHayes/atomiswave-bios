! FUN_0a144
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0xa144
        .global FUN_0a144
FUN_0a144:
        mov.l 0xa1b4, r2
        stc sr, r3
        or r2, r3
        ldc r3, sr
        mov #0, r0
        mov.l r0, @(gbr,136)
        mov.l 0xa1c4, r4
        mov.l r0, @r4
        rts
        mov.l @r4, r0
