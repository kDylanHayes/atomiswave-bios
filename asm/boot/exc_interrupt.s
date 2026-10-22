! exc_interrupt
! File 0x600, the interrupt vector. The bf after the first dt targets
! 0x5F2, which is inside check_header. The rest fills a run and walks
! a table of halfwords.
! Byte-checked assembly, not matched C.

        .org    0x600
        .global exc_interrupt
exc_interrupt:
        mov.l .L6a4, r0
        add r0, r1
        dt r2
        bf 0x5f2
        mov.l .L6f4, r1
        mov.l .L69c, r2
        mov.l .L6a0, r0
.L60e:
        mov.l r0, @r1
        add #4, r1
        dt r2
        bf .L60e
        mov.l .L6f8, r1
        mov.l .L6fc, r2
        mov.l .L6c4, r3
.L61c:
        mov r2, r7
        mov.l .L6c8, r4
.L620:
        mov.w @+r1, r0
        mov.l .L6b0, r8
        and r8, r0
        mov r0, r8
        shll16 r0
        or r8, r0
        mov r7, r8
        mov.l .L6bc, r5
.L630:
        mov r8, r9
        mov.l .L6c8, r6
.L634:
        mov.l r0, @r9
        add #4, r9
        dt r6
        bf .L634
        mov.l .L6a4, r10
        add r10, r8
        dt r5
        bf .L630
        mov.l .L6bc, r0
        add r0, r7
        dt r4
        bf .L620
        mov.l .L700, r0
        add r0, r2
        dt r3
        bf .L61c
.L654:
        mov.l .L704, r4
        mov.l .L6c0, r5
.L658:
        mov.l @+r4, r0
        mov.l .L708, r2
        mov.l r0, @r2
        mov.l @+r4, r0
        add #4, r2
        mov.l r0, @r2
        mov.l .L70c, r0
        mov.l .L694, r1
        jsr r1
        nop
        dt r5
        bf .L658
        bra .L654
        nop
        .long   0x0000099c
        .long   0x00000c4d
        .long   0xa5041200
        .long   0x00000008
        .long   0x00000c55
        .long   0xa504b060
        .long   0x00000022
        .long   0x000000b4
.L694:
        .long   0x0000097c
        .long   0xa5096000
.L69c:
        .long   0x00025800
.L6a0:
        .long   0x10821082
.L6a4:
        .long   0x00000500
        .long   0x00000015
        .long   0x000001e0
.L6b0:
        .long   0x0000ffff
        .long   0x00000001
        .long   0xffff0000
.L6bc:
        .long   0x00000040
.L6c0:
        .long   0x00000002
.L6c4:
        .long   0x00000004
.L6c8:
        .long   0x00000010
        .long   0x00000003
        .long   0x528a528a
        .long   0xad55ad55
        .long   0x00000140
        .long   0x0000a000
        .long   0x00000a00
        .long   0xa50c86c0
        .long   0x000000a2
        .long   0xffffffff
        .long   0x00000060
.L6f4:
        .long   0xa5192000
.L6f8:
        .long   0x00000714
.L6fc:
        .long   0xa51b5080
.L700:
        .long   0x00014000
.L704:
        .long   0x00000794
.L708:
        .long   0xa05f8050
.L70c:
        .long   0x00000258
