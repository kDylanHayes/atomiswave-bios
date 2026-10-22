! quiet_interrupts at 0xA144
! ORs 0x100000F0 into SR, stores 0 at GBR+136, and stores 0 at 0xA05F6910.
! The reload of that word is the rts delay.
! Checked assembly, not matched C.

        .org    0xa144
        .global quiet_interrupts
quiet_interrupts:
        mov.l 0xa1b4, r2
        stc sr, r3
        or r2, r3
        ldc r3, sr
        mov #0, r0
        mov.l r0, @(gbr,136)
        mov.l 0xa1c4, r4
        mov.l r0, @r4
        rts
        mov.l @r4, r0
