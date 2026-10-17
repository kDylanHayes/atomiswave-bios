! FUN_0a354
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0xa354
        .global FUN_0a354
FUN_0a354:
        sts.l pr, @-r15
        add #-4, r15
        mov.l r4, @r15
.La35a:
        bsr 0x9cdc
        nop
        bsr 0xa3a0
        mov.l @r15, r4
        mov r0, r4
        cmp/pz r4
        bf .La35a
        add #4, r15
        lds.l @+r15, pr
        rts
        mov r4, r0
