! FUN_09e50
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0x9e50
        .global FUN_09e50
FUN_09e50:
        mov.l @(gbr,100), r0
        mov.l 0x9efc, r3
        cmp/eq r3, r0
        bf .L9e62
        mov.l @(gbr,76), r0
        cmp/eq #32, r0
        bf .L9e62
        rts
        mov #1, r0
.L9e62:
        mov #0, r0
        rts
        nop
