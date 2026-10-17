! FUN_0a158
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0xa158
        .global FUN_0a158
FUN_0a158:
        mov.l 0xa1cc, r0
        rts
        mov.l r0, @(gbr,136)
