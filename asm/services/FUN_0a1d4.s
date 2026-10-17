! FUN_0a1d4
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0xa1d4
        .global FUN_0a1d4
FUN_0a1d4:
        mov.w 0xa0e6, r0
        rts
        mov.w r0, @(gbr,68)
