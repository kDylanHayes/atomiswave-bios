! FUN_0a3a0
! Lifted from bios0. Byte-checked assembly, not matched C.

        .org    0xa3a0
        .global FUN_0a3a0
FUN_0a3a0:
        mov.l r14, @-r15
        tst r4, r4
        sts.l pr, @-r15
        bf/s .La3d0
        mov #1, r14
        mov #0, r7
        mov.w .La3c8, r3
        stc gbr, r5
        mov r7, r6
        add r3, r5
        mov.l @(gbr,236), r0
        mov.l .La3cc, r2
        jsr r2
        mov r0, r4
        mov r0, r4
        tst r4, r4
        bt/s .La458
        mov.l r0, @(gbr,64)
        bra .La458
        mov #0, r14
.La3c8:
        .long   0x000000f0
.La3cc:
        .long   0x8c0010f0
.La3d0:
        mov #1, r7
        mov #0, r6
        stc gbr, r5
        add #48, r5
        mov.l @(gbr,64), r0
        mov.l .La494, r3
        jsr r3
        mov r0, r4
        mov r0, r4
        cmp/eq #2, r0
        bt/s .La41e
        mov.l r0, @(gbr,232)
        mov r4, r0
        cmp/eq #-1, r0
        bf .La41a
        mov #0, r0
        mov.w r0, @(gbr,68)
        mov.l @(gbr,48), r0
        cmp/eq #0, r0
        bt .La414
        cmp/eq #1, r0
        bt .La414
        cmp/eq #2, r0
        bt .La414
        cmp/eq #5, r0
        bt .La414
        cmp/eq #6, r0
        bt .La414
        cmp/eq #11, r0
        bt .La414
        cmp/eq #16, r0
        bt .La414
        bra .La430
        nop
.La414:
        mov #0, r0
        bra .La430
        mov.w r0, @(gbr,70)
.La41a:
        tst r4, r4
        bf .La422
.La41e:
        bra .La430
        mov #0, r14
.La422:
        mov r4, r0
        cmp/eq #1, r0
        bt .La42e
        mov r4, r0
        cmp/eq #3, r0
        bf .La430
.La42e:
        mov #-1, r14
.La430:
        mov r14, r0
        cmp/eq #-1, r0
        bt .La458
        mov #4, r7
        mov.l .La494, r3
        mov #0, r6
        mov r6, r5
        stc gbr, r4
        jsr r3
        add #72, r4
        mov r0, r4
        tst r4, r4
        bf .La458
        bsr 0x9e34
        nop
        cmp/eq #-1, r0
        bf .La458
        mov #0, r0
        mov.w r0, @(gbr,68)
        mov.w r0, @(gbr,70)
.La458:
        mov r14, r0
        cmp/eq #1, r0
        bt .La464
        mov r14, r0
        cmp/eq #-1, r0
        bf .La48c
.La464:
        mov.w @(gbr,68), r0
        extu.w r0, r0
        tst r0, r0
        bt .La478
        mov.w @(gbr,68), r0
        mov.l .La498, r2
        add r2, r0
        mov.w r0, @(gbr,68)
        bra .La48c
        mov #-1, r14
.La478:
        mov.w @(gbr,70), r0
        extu.w r0, r0
        tst r0, r0
        bt .La48c
        mov.w @(gbr,70), r0
        mov.l .La498, r3
        add r3, r0
        bsr 0xa1d4
        mov.w r0, @(gbr,70)
        mov #-2, r14
.La48c:
        lds.l @+r15, pr
        mov r14, r0
        rts
        mov.l @+r15, r14
.La494:
        .long   0x8c0010f0
.La498:
        .long   0x0000ffff
