! FUN_0a1da
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0xa1da
        .global FUN_0a1da
FUN_0a1da:
        mov r4, r0
        sts.l pr, @-r15
        mov.w r0, @(gbr,146)
.La1e0:
        bsr 0x9cdc
        nop
        bsr 0x9e68
        nop
        mov r0, r4
        cmp/pz r4
        bf .La1e0
        lds.l @+r15, pr
        rts
        mov r4, r0
