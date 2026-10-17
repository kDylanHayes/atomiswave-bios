! FUN_0a370
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0xa370
        .global FUN_0a370
FUN_0a370:
        sts.l pr, @-r15
        mov #10, r0
        mov.w r0, @(gbr,70)
.La376:
        bsr 0xa1d4
        nop
        bsr 0xa354
        mov #0, r4
        mov r0, r4
        tst r4, r4
        bf .La39a
        bsr 0xa1d4
        nop
.La388:
        bsr 0x9cdc
        nop
        bsr 0xa3a0
        mov #1, r4
        cmp/eq #-2, r0
        bt/s .La376
        mov r0, r4
        cmp/pz r4
        bf .La388
.La39a:
        lds.l @+r15, pr
        rts
        mov r4, r0
