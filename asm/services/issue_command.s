! issue_command at 0xA3A0
! r4 == 0 calls 0x8C0010F0(GBR+236, GBR+240, 0, 0).
! Any other r4 calls 0x8C0010F0(GBR+64, GBR+48, 0, 1), then maybe r7 = 4.
! Counts GBR+68 and GBR+70 down by adding 0xFFFF. See docs/services.md.
! Checked assembly, not matched C.

        .org    0xa3a0
        .global issue_command
issue_command:
        mov.l r14, @-r15
        tst r4, r4
        sts.l pr, @-r15
        bf/s .La3d0
        mov #1, r14
        ! r4 == 0. Call 0x8C0010F0(GBR+236, GBR+240, 0, 0) and store the
        ! result at GBR+64. A 0 result leaves r14 at 1. Any other result
        ! sets r14 to 0, which skips the countdown.
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
        .long   0x000000f0 ! added to GBR, so r5 is GBR+240
.La3cc:
        .long   0x8c0010f0
.La3d0:
        ! r4 != 0. Call 0x8C0010F0(GBR+64, GBR+48, 0, 1). The result is
        ! stored at GBR+232. 2 sets r14 to 0. -1 clears GBR+68, and clears
        ! GBR+70 when GBR+48 is 0, 1, 2, 5, 6, 11, or 16. 1 or 3 sets r14
        ! to -1. A result of 0 also sets r14 to 0.
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
        ! r14 == -1 skips the r7 = 4 call. Otherwise call
        ! 0x8C0010F0(GBR+72, 0, 0, 4). If that returns 0 and reject_code
        ! returns -1, clear GBR+68 and GBR+70.
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
        ! Countdown only when r14 is 1 or -1. A nonzero GBR+68 takes
        ! 0xFFFF and the return becomes -1. If that counter is 0 and
        ! GBR+70 is not, GBR+70 takes 0xFFFF, prime_count68 runs, and
        ! the return becomes -2.
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
        .long   0x0000ffff ! added to the short counters
