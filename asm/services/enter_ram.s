! enter_ram at 0xA116
! ORs 0x100000F0 into SR, sets VBR to 0x8C000000, calls 0x8C0006AA,
! stores 0x8C000728 at GBR+564, writes 8 to 0xA05F6910, ANDs SR with
! 0xEFFFFF0F, and jumps to 0x8C000768.
! Checked assembly, not matched C.

        .org    0xa116
        .global enter_ram
enter_ram:
        stc sr, r3
        mov.l 0xa1b4, r2
        sts.l pr, @-r15
        or r2, r3
        ldc r3, sr
        mov.l 0xa1b8, r3
        ldc r3, vbr
        mov.l 0xa1bc, r1
        jsr r1
        nop
        mov.l 0xa1c0, r0
        mov.l r0, @(gbr,564)
        mov #8, r3
        mov.l 0xa1c4, r4
        mov.l r3, @r4
        mov.l @r4, r2
        stc sr, r1
        mov.l 0xa178, r3
        and r3, r1
        ldc r1, sr
        mov.l 0xa1c8, r2
        jmp r2
        lds.l @+r15, pr
