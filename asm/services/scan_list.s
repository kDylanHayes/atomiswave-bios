! scan_list at 0xA1F4
! Walks the byte list in r4 up to the bound in r5. Fills GBR+236..GBR+252
! and calls run_transfer and retry_issue. Record offsets are in the loads.
! Checked assembly, not matched C.

        .org    0xa1f4
        .global scan_list
scan_list:
        mov.l r14, @-r15
        mov.l r13, @-r15
        mov.l r12, @-r15
        mov r4, r12
        mov.l .La2f0, r3
        mov.l r11, @-r15
        mov.l r10, @-r15
        mov.l r9, @-r15
        mov.l r8, @-r15
        sts.l pr, @-r15
        add #-4, r15
        mov.l r5, @r15
        ! Call 0x8C0004D8 with the list pointer. Then store 17, the
        ! bound, 1, the list pointer, and 0 at GBR+236 through GBR+252
        ! and call run_transfer.
        jsr r3
        mov r12, r4
        mov r12, r14
        mov r12, r13
        mov #17, r0
        mov.l r0, @(gbr,236)
        mov.l @r15, r0
        mov.l r0, @(gbr,240)
        mov #1, r0
        mov.l r0, @(gbr,244)
        mov r13, r0
        mov.l r0, @(gbr,248)
        mov #0, r0
        bsr 0xa370
        mov.l r0, @(gbr,252)
        tst r0, r0
        bt .La232
        bra .La33e
        nop
.La232:
        ! run_transfer returned 0. Call 0x8C000590 with the list pointer.
        ! A nonzero result returns 0.
        mov.l .La2f4, r2
        jsr r2
        mov r14, r4
        tst r0, r0
        bt .La240
        bra .La33e
        nop
.La240:
        ! Call hole 0x9CE2 with the list plus 0xA2, add 0x96, and store
        ! that with command 17. run_transfer again. The walk bound
        ! becomes the list plus 0x800.
        mov.w .La2e8, r4
        bsr 0x9ce2
        add r14, r4
        mov.w .La2ea, r2
        add r2, r0
        mov.l r0, @(gbr,240)
        mov #1, r0
        mov.l r0, @(gbr,244)
        mov r13, r0
        mov.l r0, @(gbr,248)
        mov #0, r0
        mov.l r0, @(gbr,252)
        mov #17, r0
        bsr 0xa370
        mov.l r0, @(gbr,236)
        mov r13, r14
        mov.l .La2f8, r10
        mov #2, r8
        mov.w .La2ea, r11
        mov.w .La2ec, r2
        add r2, r13
        bra .La332
        mov.l r13, @r15
.La26e:
        ! Skip this entry when bit 1 of the byte at cursor+25 is set.
        ! Otherwise read the byte at cursor+32, index cursor+33 by it,
        ! save that byte, and store 59 over it. Call 0x8C000598 with
        ! r5 = GBR+156. A nonzero result restores the saved byte.
        mov #25, r0
        mov.b @(r0,r14), r2
        extu.b r2, r2
        tst r8, r2
        bf .La32c
        mov #32, r0
        mov r14, r4
        mov.b @(r0,r14), r5
        mov #59, r3
        add #33, r4
        extu.b r5, r13
        add r4, r13
        mov.b @r13, r9
        mov.b r3, @r13
        mov.l @(gbr,156), r0
        mov.l .La2fc, r2
        jsr r2
        mov r0, r5
        tst r0, r0
        bf .La32a
        ! Call hole 0x9CE2 at cursor+14 and again at cursor+6. Add 0x96
        ! to the second result. If that sum is below 0x6DDD0 and GBR+36
        ! is not 2, call 0x8C000800 with r4 = 1.
        mov r14, r4
        bsr 0x9ce2
        add #14, r4
        mov r0, r13
        mov r14, r4
        bsr 0x9ce2
        add #6, r4
        mov r0, r14
        add r11, r14
        cmp/hs r10, r14
        bt .La2ba
        mov.b @(gbr,36), r0
        extu.b r0, r0
        cmp/eq #2, r0
        bt .La2ba
        mov.l .La300, r2
        jsr r2
        mov #1, r4
.La2ba:
        ! GBR+240 is the second 0x9CE2 result plus 0x96. GBR+244 is
        ! the first result plus 0x7FF, shifted right 11. GBR+36 == 0
        ! stores the original list pointer at GBR+248 and 0 at GBR+252.
        ! Otherwise GBR+248 is 0 and GBR+252 is the first result.
        mov r14, r0
        mov.l r0, @(gbr,240)
        mov.w .La2ee, r0
        add r13, r0
        shlr8 r0
        shlr2 r0
        shlr r0
        mov.l r0, @(gbr,244)
        mov.b @(gbr,36), r0
        extu.b r0, r0
        tst r0, r0
        bt .La2d6
        bra .La2d8
        mov #0, r0
.La2d6:
        mov r12, r0
.La2d8:
        mov.l r0, @(gbr,248)
        mov.b @(gbr,36), r0
        extu.b r0, r0
        tst r0, r0
        bt .La304
        bra .La306
        mov r13, r0
        .word   0x0258 ! 0xA2E6. prime_count68 loads 600 from here
.La2e8:
        .word   0x00a2 ! added to the list before hole 0x9CE2
.La2ea:
        .word   0x0096 ! added to a 0x9CE2 result
.La2ec:
        .word   0x0800 ! added to the cursor before the walk
.La2ee:
        .word   0x07ff ! added before the shift into GBR+244
.La2f0:
        .long   0x8c0004d8 ! called with the list pointer
.La2f4:
        .long   0x8c000590 ! called with the list pointer
.La2f8:
        .long   0x0006ddd0 ! compared with the second 0x9CE2 result plus 0x96
.La2fc:
        .long   0x8c000598 ! called with r5 = GBR+156
.La300:
        .long   0x8c000800 ! called with r4 = 1
.La304:
        mov #0, r0
.La306:
        mov.l r0, @(gbr,252)
        ! Store 10 at GBR+70 and call prime_count68. Command 28 when
        ! GBR+36 is not 0, otherwise 17. retry_issue(0), hole 0x9CDC,
        ! and return the first 0x9CE2 result.
        mov #10, r0
        bsr 0xa1d4
        mov.w r0, @(gbr,70)
        mov.b @(gbr,36), r0
        extu.b r0, r0
        tst r0, r0
        bt .La31a
        bra .La31c
        mov #28, r0
.La31a:
        mov #17, r0
.La31c:
        mov.l r0, @(gbr,236)
        bsr 0xa354
        mov #0, r4
        bsr 0x9cdc
        nop
        bra .La340
        mov r13, r0
.La32a:
        mov.b r9, @r13
.La32c:
        ! Advance the cursor by the byte at the cursor. The byte at the
        ! new cursor being 0, or the cursor reaching the bound, returns 0.
        mov.b @r14, r3
        extu.b r3, r3
        add r3, r14
.La332:
        mov.b @r14, r2
        tst r2, r2
        bt .La33e
        mov.l @r15, r3
        cmp/hs r3, r14
        bf .La26e
.La33e:
        mov #0, r0
.La340:
        add #4, r15
        lds.l @+r15, pr
        mov.l @+r15, r8
        mov.l @+r15, r9
        mov.l @+r15, r10
        mov.l @+r15, r11
        mov.l @+r15, r12
        mov.l @+r15, r13
        rts
        mov.l @+r15, r14
