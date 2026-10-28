! service_main at 0x9FBC
! Outer driver for the service cluster. Calls step_phase, issue_command,
! enter_ram, scan_list, and the RAM addresses in service_pool.
! Checked assembly, not matched C.

        .org    0x9fbc
        .global service_main
service_main:
        mov.l r14, @-r15
        stc sr, r0
        mov.l 0xa178, r3
        mov.l r13, @-r15
        mov.l r12, @-r15
        and r3, r0
        mov.l r11, @-r15
        or #240, r0
        mov.l r10, @-r15
        mov.l r9, @-r15
        mov.l r8, @-r15
        sts.l pr, @-r15
        ldc r0, sr
        ! AND with 0xEFFFFF0F, then OR 0xF0, was the SR update above.
        ! call ram_call_3, then store 0xFF80 at GBR+146. r12 is 0x8C000800.
        ! r14 is 0x8C00C000.
        bsr 0xa16a
        nop
        mov.l 0xa17c, r0
        mov.w r0, @(gbr,146)
        mov.l 0xa180, r12
        mov.l 0xa184, r14
        mov.l @(gbr,228), r0
        ! GBR+228 == 1 stores 1 at GBR+37, sets bit 0 of GBR+38, and
        ! joins the loop at .La074 with r13 still 0.
        cmp/eq #1, r0
        bf/s .L9ff4
        mov #0, r13
        mov #1, r0
        mov.b r0, @(gbr,37)
        mov #38, r0
        bra .La074
        or.b #1, @(r0,gbr)
.L9ff4:
        ! GBR+228 == 3 jumps to the loop head. Any other value stores 0
        ! at GBR+37, calls 0x8C00C000 with 0 and then 1, sets r13 to 2,
        ! and stores 0x8C008000 at GBR+100.
        mov.l @(gbr,228), r0
        cmp/eq #3, r0
        bt .La0a8
        mov #0, r0
        mov.b r0, @(gbr,37)
        jsr r14
        mov r0, r4
        jsr r14
        mov #1, r4
        mov #2, r13
        mov.l 0xa188, r0
        bra .La0a8
        mov.l r0, @(gbr,100)
.La00e:
        ! enter_ram, hole 0x9CDC, then call the address in r9 with r11
        ! set to -1. phase_until_clear(-4) follows.
        bsr 0xa116
        nop
        bsr 0x9cdc
        nop
        jsr r9
        mov #-1, r11
        bsr 0xa1da
        mov #-4, r4
        mov.l @(gbr,76), r0
        ! GBR+76 == 32 stores 0 at GBR+136 and calls 0x8CE00000 with
        ! r4 = 1. A nonzero result calls 0x8C0004F4 with GBR+100. A 0
        ! result from that call stores 2 at GBR+36, calls set_hook, and
        ! leaves through .La0ae. r11 is 0 on that path, and r10 keeps
        ! the 0x8CE00000 result.
        cmp/eq #32, r0
        bf .La04c
        mov #0, r0
        mov.l r0, @(gbr,136)
        mov.l 0xa18c, r10
        jsr r10
        mov #1, r4
        mov r0, r10
        tst r10, r10
        bt .La04c
        mov.l 0xa190, r8
        mov #0, r11
        mov.l @(gbr,100), r0
        jsr r8
        mov r0, r4
        tst r0, r0
        bf .La04c
        mov #2, r0
        bsr 0xa158
        mov.b r0, @(gbr,36)
        bra .La0ae
        nop
.La04c:
        ! Otherwise set_hook, step_phase, store 0xFFFB at GBR+144, and
        ! phase_until_clear(-128). A 0 result leaves through .La0ae.
        bsr 0xa158
        nop
        mov.l 0xa17c, r0
        bsr 0x9e68
        mov.w r0, @(gbr,146)
        mov.l 0xa194, r0
        mov.w r0, @(gbr,144)
        bsr 0xa1da
        mov #-128, r4
        bsr 0xa158
        mov r0, r8
        tst r8, r8
        bt .La0ae
.La066:
        ! quiet_interrupts, then the same SR update as the entry.
        bsr 0xa144
        nop
        stc sr, r0
        mov.l 0xa178, r3
        and r3, r0
        or #240, r0
        ldc r0, sr
.La074:
        ! Store 0x8C008000 at GBR+100. If r13 >= 0, call 0x8C00C000
        ! with r13 and then with 3. Then call it with 4, call 0x8C000472,
        ! and call 0x8C000800 with 4 when GBR+76 is 32 or GBR+48 is 16,
        ! then with 3. The loop returns through .La0a8.
        mov.l 0xa188, r0
        cmp/pz r13
        bf/s .La084
        mov.l r0, @(gbr,100)
        jsr r14
        mov r13, r4
        jsr r14
        mov #3, r4
.La084:
        mov.l 0xa17c, r0
        mov #0, r13
        mov.w r0, @(gbr,146)
        jsr r14
        mov #4, r4
        mov.l 0xa198, r9
        jsr r9
        nop
        mov.l @(gbr,76), r0
        cmp/eq #32, r0
        bt .La0a0
        mov.l @(gbr,48), r0
        cmp/eq #16, r0
        bf .La0a4
.La0a0:
        jsr r12
        mov #4, r4
.La0a4:
        jsr r12
        mov #3, r4
.La0a8:
        ! r9 becomes 0x8C000462. Loop back to enter_ram.
        mov.l 0xa19c, r9
        bra .La00e
        nop
.La0ae:
        ! A clear GBR+38 goes back to quiet_interrupts. Otherwise call
        ! 0x8C00C000 when r13 >= 0, call r9, then call 0x8C0005B8 with
        ! r4 = 0x8C000FD8. r11 == 0 stores r10 + 7 at GBR+240.
        mov.b @(gbr,38), r0
        extu.b r0, r0
        tst r0, r0
        bt .La066
        cmp/pz r13
        bf .La0c2
        jsr r14
        mov r13, r4
        jsr r14
        mov #3, r4
.La0c2:
        jsr r9
        nop
        mov.l 0xa1a0, r4
        mov.l 0xa1a4, r2
        jsr r2
        nop
        tst r11, r11
        bf .La0d8
        mov r10, r0
        add #7, r0
        mov.l r0, @(gbr,240)
.La0d8:
        bsr 0xa370
        nop
        mov r0, r4
        tst r4, r4
        bf .La0f8
        tst r11, r11
        ! r11 != 0 skips the next three halfwords. r11 == 0 executes
        ! them: mov r10, r5 / bra to the r4 load / add #16, r5.
        ! The first halfword is 0x65A3 at file 0xA0E6.
        bf .La0ec
        .word   0x65a3
        .long   0x7510a001
.La0ec:
        ! scan_list(0x8C010000, 0xB06E), unless the bra above skipped
        ! the r5 load and r5 is r10 + 16. A 0 result calls 0x8C000800
        ! with r4 = 1. The return stores 0xFF80 at GBR+146 and
        ! 0x8C008100 at GBR+100.
        mov.l 0xa1a8, r5
        mov.l 0xa1ac, r4
        bsr 0xa1f4
        nop
        tst r0, r0
        bf .La0fc
.La0f8:
        jsr r12
        mov #1, r4
.La0fc:
        mov.l 0xa17c, r0
        mov.w r0, @(gbr,146)
        mov.l 0xa1b0, r0
        mov.l r0, @(gbr,100)
        lds.l @+r15, pr
        mov.l @+r15, r8
        mov.l @+r15, r9
        mov.l @+r15, r10
        mov.l @+r15, r11
        mov.l @+r15, r12
        mov.l @+r15, r13
        rts
        mov.l @+r15, r14
