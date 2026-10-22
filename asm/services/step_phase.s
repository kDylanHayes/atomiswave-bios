! step_phase at 0x9E68
! One step of the signed short at GBR+144. Installs GBR = 0x8C000000
! and restores the caller's GBR. The phase cases are in docs/services.md.
! Checked assembly, not matched C.

        .org    0x9e68
        .global step_phase
step_phase:
        mov.l r14, @-r15
        stc gbr, r3
        mov.l .L9f00, r2
        mov.l r13, @-r15
        sts.l pr, @-r15
        ldc r2, gbr
        add #-4, r15
        mov.l r3, @r15
        mov.w @(gbr,144), r0
        mov r0, r14
        exts.w r14, r3
        cmp/pz r3
        ! A negative phase calls ram_call_2 before the dispatch.
        bt .L9e86
        bsr 0xa15e
        nop
.L9e86:
        ! Dispatch on that same signed phase.
        exts.w r14, r0
        cmp/eq #-8, r0
        bf .L9e90
        bra .L9f70
        nop
.L9e90:
        cmp/eq #-7, r0
        bt .L9eec
        cmp/eq #-6, r0
        bt .L9ed6
        cmp/eq #-5, r0
        bt .L9f5e
        cmp/eq #-4, r0
        bt .L9eec
        cmp/eq #-3, r0
        bt .L9ed6
        cmp/eq #-2, r0
        bt .L9ece
        cmp/eq #-1, r0
        bt .L9ebc
        cmp/eq #0, r0
        ! Any other phase, including 0. Call hole 0x9D52, set bit 0 of
        ! GBR+38, store 10 at GBR+70, and set the phase to -2.
        bsr 0x9d52
        nop
        mov #38, r0
        or.b #1, @(r0,gbr)
        mov #10, r0
        bra .L9f46
        mov.w r0, @(gbr,70)
.L9ebc:
        ! Phase -1. If GBR+48 is greater than 0, the phase becomes that
        ! word. Otherwise it becomes 127.
        mov.l @(gbr,48), r0
        mov #0, r2
        cmp/hi r2, r0
        bf .L9eca
        mov.l @(gbr,48), r0
        bra .L9f82
        mov r0, r14
.L9eca:
        bra .L9f82
        mov #127, r14
.L9ece:
        ! Phase -2. Store 24 at GBR+236, call prime_count68, set the
        ! phase to -3, and fall into the -3 path.
        mov #24, r0
        bsr 0xa1d4
        mov.l r0, @(gbr,236)
        mov #-3, r14
.L9ed6:
        ! Phases -6 and -3. issue_command(0). A result of 1 sets the
        ! phase to -1. A result of 0 calls prime_count68 and subtracts 1.
        bsr 0xa3a0
        mov #0, r4
        cmp/eq #1, r0
        bt/s .L9f30
        mov r0, r4
        tst r4, r4
        bf .L9f82
        bsr 0xa1d4
        add #-1, r14
        bra .L9f82
        nop
.L9eec:
        ! Phases -7 and -4. issue_command(1). A result of -2 subtracts 2.
        bsr 0xa3a0
        mov #1, r4
        cmp/eq #-2, r0
        bf/s .L9f04
        mov r0, r13
        bra .L9f22
        add #-2, r14
        .word   0x0000
        .long   0x8c008000 ! ram_window_ready compares GBR+100 with this
.L9f00:
        .long   0x8c000000 ! GBR installed for this call
.L9f04:
        tst r13, r13
        bf .L9f22
        mov.l @(gbr,76), r0
        mov.w .L9fac, r2
        cmp/eq r2, r0
        bf .L9f14
        bra .L9f22
        add #-1, r14
.L9f14:
        ! issue_command returned 0. ram_window_ready returning 1 sets
        ! the phase to 0.
        bsr 0x9e50
        nop
        tst r0, r0
        bt .L9f20
        bra .L9f22
        mov #0, r14
.L9f20:
        mov #1, r13
.L9f22:
        mov r13, r0
        cmp/eq #1, r0
        bf .L9f82
        ! The result was 1. reject_code returning -1 sets the phase to -1.
        bsr 0x9e34
        nop
        cmp/eq #-1, r0
        bf .L9f34
.L9f30:
        bra .L9f82
        mov #-1, r14
.L9f34:
        ! reject_code was not -1. GBR+48 == 2 adds 2. 6 sets the phase
        ! to -2. 16 calls ram_window_ready. Any other value sets -1.
        mov.l @(gbr,48), r0
        cmp/eq #2, r0
        bt .L9f4a
        cmp/eq #6, r0
        bt .L9f46
        cmp/eq #16, r0
        bt .L9f4e
        bra .L9f5a
        nop
.L9f46:
        bra .L9f82
        mov #-2, r14
.L9f4a:
        bra .L9f82
        add #2, r14
.L9f4e:
        bsr 0x9e50
        nop
        tst r0, r0
        bf .L9f7c
        bra .L9f82
        nop
.L9f5a:
        bra .L9f82
        mov #-1, r14
.L9f5e:
        ! Phase -5. Call 0x8C0005B8 with r4 = 0x8C000FC4, copy GBR+100
        ! to GBR+248, call prime_count68, set the phase to -6, and fall
        ! into the -6 path.
        mov.l .L9fb0, r4
        mov.l .L9fb4, r2
        jsr r2
        nop
        mov.l @(gbr,100), r0
        bsr 0xa1d4
        mov.l r0, @(gbr,248)
        bra .L9ed6
        mov #-6, r14
.L9f70:
        ! Phase -8. Call 0x8C0004F4 with GBR+100 in r4. A 0 result sets
        ! the phase to 0. Any other result sets it to 126.
        mov.l @(gbr,100), r0
        mov.l .L9fb8, r3
        jsr r3
        mov r0, r4
        tst r0, r0
        bf .L9f80
.L9f7c:
        bra .L9f82
        mov #0, r14
.L9f80:
        mov #126, r14
.L9f82:
        ! A phase below the signed limit at GBR+146 becomes 0. A phase
        ! that is then >= 0 calls hole 0x9DB8. Store it at GBR+144 and
        ! restore the caller's GBR.
        exts.w r14, r3
        mov.w @(gbr,146), r0
        exts.w r0, r0
        cmp/ge r0, r3
        bt .L9f8e
        mov #0, r14
.L9f8e:
        exts.w r14, r3
        cmp/pz r3
        bf .L9f98
        bsr 0x9db8
        nop
.L9f98:
        mov r14, r0
        mov.w r0, @(gbr,144)
        mov.l @r15, r2
        exts.w r14, r0
        ldc r2, gbr
        add #4, r15
        lds.l @+r15, pr
        mov.l @+r15, r13
        rts
        mov.l @+r15, r14
.L9fac:
        .long   0x00000080 ! compared with GBR+76
.L9fb0:
        .long   0x8c000fc4 ! r4 for the phase -5 call
.L9fb4:
        .long   0x8c0005b8 ! phase -5 callee
.L9fb8:
        .long   0x8c0004f4 ! phase -8 callee
